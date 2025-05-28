import sys
import signal

from raypy import _rayforce as r


class RaypyREPL:
    _running = False
    _signal_handlers = {}

    def start(self):
        """
        Start the REPL loop
        """

        if self._running:
            print("Warning: REPL already running.")
            return

        r.repl_init()
        self._running = True

        # Set up signal handlers
        def handle_sigint(*args, **kwargs) -> None:
            raise KeyboardInterrupt()

        def handle_sigterm(*args, **kwargs) -> None:
            self.stop()
            sys.exit(0)

        self._signal_handlers = {
            signal.SIGINT: signal.signal(signal.SIGINT, handle_sigint),
            signal.SIGTERM: signal.signal(signal.SIGTERM, handle_sigterm),
        }

        try:
            r.runtime_run()
        except KeyboardInterrupt:
            print(" Exiting the REPL...")
        except EOFError:
            pass
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.stop()

    def stop(self):
        """
        Stop the REPL loop
        """
        if not self._running:
            print("Warning: REPL not running to be stopped.")
            return

        self._running = False

        for signum, handler in self._signal_handlers.items():
            signal.signal(signum, handler)
        self._signal_handlers.clear()

        r.repl_cleanup()


def start_repl() -> None:
    """
    Initiate Raypy REPL, which consists of 2 modes:
    1. Python mode - executing python code
    2. Rayforce mode - executing rayforce queries with rayfall language
    """
    RaypyREPL().start()
