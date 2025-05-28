"""
Rayforce event loop integration with Python's asyncio.
"""

import asyncio
import threading
import ctypes
from ctypes import *
from typing import Callable, Dict
import logging
from enum import IntEnum
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
        """Main event loop that processes Rayforce events."""
        # All Rayforce initialization must happen here!
        argv = [b"raypy", b"-r", b"0", None]
        logger.info(f"Initializing Rayforce runtime with argv: {argv}")
        self._rayforce.runtime_create(3, (c_char_p * 4)(*argv))
        self._rayforce.runtime_run()

    def register_selector(
        self,
        fd: int,
        selector_type: SelectorType,
        events: PollEvents,
        callback: Callable,
    ) -> int:
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
            socket_callback,
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
