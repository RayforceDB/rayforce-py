#!/usr/bin/env python3

import sys
import signal
from typing import Optional, Callable
import ctypes
import os

# Load the shared library globally before importing as a Python extension
ctypes.CDLL(os.path.join(os.path.dirname(__file__), "_rayforce.so"), mode=getattr(ctypes, 'RTLD_GLOBAL', 256))

# Set RTLD_GLOBAL before importing the extension
if hasattr(sys, 'setdlopenflags'):
    _orig_flags = sys.getdlopenflags()
    RTLD_GLOBAL = getattr(ctypes, 'RTLD_GLOBAL', getattr(os, 'RTLD_GLOBAL', 256))
    RTLD_NOW = getattr(ctypes, 'RTLD_NOW', getattr(os, 'RTLD_NOW', 2))
    sys.setdlopenflags(RTLD_GLOBAL | RTLD_NOW)

from . import _rayforce as r

# Restore original dlopen flags
if hasattr(sys, 'setdlopenflags'):
    sys.setdlopenflags(_orig_flags)

class RayforceREPL:
    def __init__(self, prompt: str = "raypy> "):
        """Initialize the Rayforce REPL.
        
        Args:
            prompt: The prompt string to display before each input line
        """
        self.prompt = prompt
        self._running = False
        self._signal_handlers = {}
        
    def start(self):
        """Start the REPL loop."""
        if self._running:
            return
            
        # Initialize the REPL
        r.repl_init(self.prompt)
        self._running = True
        
        # Set up signal handlers
        self._setup_signal_handlers()
        
        try:
            while self._running:
                try:
                    r.repl_step()
                except KeyboardInterrupt:
                    print("\nUse Ctrl+D or type 'exit' to quit")
                except EOFError:
                    break
                except Exception as e:
                    print(f"Error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the REPL loop."""
        if not self._running:
            return
            
        self._running = False
        self._restore_signal_handlers()
        r.repl_cleanup()
        
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def handle_sigint(signum, frame):
            raise KeyboardInterrupt()
            
        def handle_sigterm(signum, frame):
            self.stop()
            sys.exit(0)
            
        self._signal_handlers = {
            signal.SIGINT: signal.signal(signal.SIGINT, handle_sigint),
            signal.SIGTERM: signal.signal(signal.SIGTERM, handle_sigterm)
        }
        
    def _restore_signal_handlers(self):
        """Restore original signal handlers."""
        for signum, handler in self._signal_handlers.items():
            signal.signal(signum, handler)
        self._signal_handlers.clear()

def start_repl(prompt: str = "raypy> "):
    """Start the Rayforce REPL with the given prompt.
    
    Args:
        prompt: The prompt string to display before each input line
    """
    repl = RayforceREPL(prompt)
    repl.start()

if __name__ == "__main__":
    start_repl() 