"""
Rayforce event loop integration with Python's asyncio.
"""

import asyncio
import threading
import ctypes
from ctypes import *
from typing import Optional, Callable, Any, Dict
import logging
from enum import IntEnum
import sys
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants from poll.h
MAX_EVENTS = 1024
BUF_SIZE = 2048
TX_QUEUE_SIZE = 16
SELECTOR_ID_OFFSET = 3

# Type definitions
class SelectorType(IntEnum):
    STDIN = 0
    STDOUT = 1
    STDERR = 2
    SOCKET = 3
    FILE = 4

class PollEvents(IntEnum):
    READ = 1
    WRITE = 2
    ERROR = 4
    HUP = 8
    RDHUP = 16
    EDGE = 32

class RayforceEventLoop:
    def __init__(self):
        self._rayforce = ctypes.CDLL("raypy/_rayforce.so", mode=ctypes.RTLD_GLOBAL)
        self._setup_function_signatures()
        self._running = False
        self._callbacks: Dict[int, Callable] = {}
        self._lock = threading.Lock()
        self._thread = None
        self._cmd_queue = queue.Queue()
        self._result_queue = queue.Queue()
        self._poll = None
        
    def _setup_function_signatures(self):
        """Set up C function signatures for the Rayforce library."""
        # Runtime management
        self._rayforce.runtime_create.argtypes = [c_int, POINTER(c_char_p)]
        self._rayforce.runtime_create.restype = None
        self._rayforce.runtime_run.argtypes = []
        self._rayforce.runtime_run.restype = c_int32
        self._rayforce.runtime_destroy.argtypes = []
        self._rayforce.runtime_destroy.restype = None
        
        # Poll creation and management
        self._rayforce.poll_create.argtypes = []
        self._rayforce.poll_create.restype = c_void_p
        self._rayforce.poll_run.argtypes = [c_void_p]
        self._rayforce.poll_run.restype = c_int64
        self._rayforce.poll_destroy.argtypes = [c_void_p]
        
        # Selector registration
        self._rayforce.poll_register.argtypes = [c_void_p, c_void_p]
        self._rayforce.poll_register.restype = c_int64
        self._rayforce.poll_deregister.argtypes = [c_void_p, c_int64]
        self._rayforce.poll_deregister.restype = c_int64
        
        # Buffer management
        self._rayforce.poll_buf_create.argtypes = [c_int64]
        self._rayforce.poll_buf_create.restype = c_void_p
        self._rayforce.poll_buf_destroy.argtypes = [c_void_p]
        
        # Buffer operations
        self._rayforce.poll_rx_buf_request.argtypes = [c_void_p, c_void_p, c_int64]
        self._rayforce.poll_rx_buf_request.restype = c_int64
        self._rayforce.poll_rx_buf_extend.argtypes = [c_void_p, c_void_p, c_int64]
        self._rayforce.poll_rx_buf_extend.restype = c_int64
        self._rayforce.poll_rx_buf_release.argtypes = [c_void_p, c_void_p]
        self._rayforce.poll_rx_buf_release.restype = c_int64
        self._rayforce.poll_rx_buf_reset.argtypes = [c_void_p, c_void_p]
        self._rayforce.poll_rx_buf_reset.restype = c_int64
        self._rayforce.poll_send_buf.argtypes = [c_void_p, c_void_p, c_void_p]
        self._rayforce.poll_send_buf.restype = c_int64
        
        # Other operations
        self._rayforce.poll_block_on.argtypes = [c_void_p, c_void_p]
        self._rayforce.poll_block_on.restype = c_void_p
        self._rayforce.poll_exit.argtypes = [c_void_p, c_int64]
        self._rayforce.poll_set_usr_fd.argtypes = [c_int64]
        
        # Command evaluation
        self._rayforce.ray_eval_str.argtypes = [c_void_p, c_void_p]
        self._rayforce.ray_eval_str.restype = c_int64
        
    def start(self):
        """Start the Rayforce event loop in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_poll_loop, daemon=True)
        self._thread.start()
        logger.info("Rayforce event loop started (background thread)")
        
    def stop(self):
        """Stop the Rayforce event loop and clean up resources."""
        if not self._running:
            return
        self._cmd_queue.put({"cmd": "exit"})
        self._thread.join(timeout=2.0)
        self._running = False
        logger.info("Rayforce event loop stopped")
        
    def _run_poll_loop(self):
        """Main event loop that processes Rayforce events."""
        # All Rayforce initialization must happen here!
        argv = [b"raypy", b"-r", b"0", None]
        logger.info(f"Initializing Rayforce runtime with argv: {argv}")
        self._rayforce.runtime_create(3, (c_char_p * 4)(*argv))
        try:
            while self._running:
                # Handle commands from the queue
                try:
                    cmd = self._cmd_queue.get(timeout=0.05)
                    if cmd["cmd"] == "exit":
                        self._running = False
                        break
                    elif cmd["cmd"] == "eval":
                        source = cmd["source"]
                        buf = self._rayforce.poll_buf_create(len(source.encode()) + 1)
                        if not buf:
                            self._result_queue.put(RuntimeError("Failed to create buffer"))
                            continue
                        try:
                            ctypes.memmove(buf, source.encode(), len(source.encode()))
                            result = self._rayforce.ray_eval_str(buf, None)
                            if result == -1:
                                self._result_queue.put(RuntimeError("Failed to evaluate command"))
                            else:
                                self._result_queue.put(result)
                        finally:
                            self._rayforce.poll_buf_destroy(buf)
                        continue
                except queue.Empty:
                    pass
                # Run the runtime
                result = self._rayforce.runtime_run()
                if result != 0:
                    logger.info(f"Runtime exited with code {result}")
                    self._running = False
                    break
        except Exception as e:
            logger.error(f"Error in poll loop: {e}")
        finally:
            self._rayforce.runtime_destroy()
        
    def register_selector(self, fd: int, selector_type: SelectorType, 
                         events: PollEvents, callback: Callable) -> int:
        """Register a new selector with the event loop."""
        with self._lock:
            # Create registry structure
            registry = (c_int64 * 12)()  # Adjust size based on your registry structure
            registry[0] = fd
            registry[1] = selector_type
            registry[2] = events
            
            # Register the selector
            selector_id = self._rayforce.poll_register(self._poll, registry)
            if selector_id > 0:
                self._callbacks[selector_id] = callback
                logger.info(f"Registered selector {selector_id} for fd {fd}")
            else:
                logger.error(f"Failed to register selector for fd {fd}")
                
            return selector_id
            
    def deregister_selector(self, selector_id: int):
        """Deregister a selector from the event loop."""
        with self._lock:
            if selector_id in self._callbacks:
                self._rayforce.poll_deregister(self._poll, selector_id)
                del self._callbacks[selector_id]
                logger.info(f"Deregistered selector {selector_id}")
                
    def create_buffer(self, size: int) -> c_void_p:
        """Create a new buffer for reading/writing data."""
        return self._rayforce.poll_buf_create(size)
        
    def destroy_buffer(self, buf: c_void_p):
        """Destroy a buffer."""
        self._rayforce.poll_buf_destroy(buf)
        
    def request_read_buffer(self, selector_id: int, size: int) -> int:
        """Request a buffer for reading data."""
        selector = self._rayforce.poll_get_selector(self._poll, selector_id)
        if selector:
            return self._rayforce.poll_rx_buf_request(self._poll, selector, size)
        return -1
        
    def send_buffer(self, selector_id: int, buf: c_void_p) -> int:
        """Send data from a buffer."""
        selector = self._rayforce.poll_get_selector(self._poll, selector_id)
        if selector:
            return self._rayforce.poll_send_buf(self._poll, selector, buf)
        return -1
        
    def block_on(self, selector_id: int) -> Any:
        """Block until a selector is ready."""
        selector = self._rayforce.poll_get_selector(self._poll, selector_id)
        if selector:
            return self._rayforce.poll_block_on(self._poll, selector)
        return None

    def eval(self, source: str) -> Any:
        """Evaluate a Rayforce command."""
        if not self._running:
            raise RuntimeError("Rayforce event loop is not running")
        self._cmd_queue.put({"cmd": "eval", "source": source})
        result = self._result_queue.get()
        if isinstance(result, Exception):
            raise result
        return result

class RayforceEventLoopPolicy(asyncio.AbstractEventLoopPolicy):
    """Event loop policy that integrates Rayforce with asyncio."""
    
    def __init__(self):
        self._rayforce_loop = RayforceEventLoop()
        self._default_policy = asyncio.get_event_loop_policy()
        
    def get_event_loop(self):
        return self._default_policy.get_event_loop()
        
    def set_event_loop(self, loop):
        self._default_policy.set_event_loop(loop)
        
    def new_event_loop(self):
        return self._default_policy.new_event_loop()
        
    def get_child_watcher(self):
        return self._default_policy.get_child_watcher()
        
    def start(self):
        """Start the Rayforce event loop."""
        self._rayforce_loop.start()
        
    def stop(self):
        """Stop the Rayforce event loop."""
        self._rayforce_loop.stop()

# Example usage
async def main():
    # Create and set the event loop policy
    policy = RayforceEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    
    # Start the Rayforce event loop
    policy.start()
    
    try:
        # Example: Register a socket
        def socket_callback(data):
            print(f"Received data: {data}")
            
        # Register a socket (example)
        socket_fd = 4  # Example socket file descriptor
        selector_id = policy._rayforce_loop.register_selector(
            socket_fd,
            SelectorType.SOCKET,
            PollEvents.READ | PollEvents.WRITE,
            socket_callback
        )
        
        # Your async code here
        await asyncio.sleep(1)
        
        # Clean up
        policy._rayforce_loop.deregister_selector(selector_id)
        
    finally:
        # Stop the Rayforce event loop
        policy.stop()

if __name__ == "__main__":
    asyncio.run(main()) 