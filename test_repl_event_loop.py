print("[DEBUG] test_repl_event_loop.py script is running!")

import asyncio
import code
import sys
from raypy import RayforceEventLoopPolicy

# Create and set the event loop policy
policy = RayforceEventLoopPolicy()
asyncio.set_event_loop_policy(policy)

# Start the Rayforce event loop
policy.start()

# Create a namespace for the REPL
namespace = {
    'policy': policy,
    'event_loop': policy._rayforce_loop,
    'asyncio': asyncio,
    '__builtins__': __builtins__
}

class CustomInterpreter(code.InteractiveInterpreter):
    def __init__(self, locals=None):
        super().__init__(locals)
        self.buffer = []
        self.rayforce_mode = False  # Start in Python mode
        print(f"[DEBUG] Interpreter initialized. rayforce_mode={self.rayforce_mode}")
        
    def runsource(self, source, filename="<input>", symbol="single"):
        """Handle both Python code and Rayforce commands."""
        source = source.strip()
        
        # Handle mode switching commands
        if source == "%rayforce":
            self.rayforce_mode = True
            print("Switched to Rayforce mode")
            return False
        elif source == "%python":
            self.rayforce_mode = False
            print("Switched to Python mode")
            return False
        elif source == "%mode":
            print(f"Current mode: {'Rayforce' if self.rayforce_mode else 'Python'}")
            return False
        elif source == "%exit":
            print("Exiting Rayforce...")
            policy._rayforce_loop._cmd_queue.put("exit")
            return False
            
        # Handle the command based on current mode
        if self.rayforce_mode:
            try:
                # Try to evaluate as Rayforce command
                result = policy._rayforce_loop.eval(source)
                if result is not None:
                    print(result)
                return False
            except Exception as e:
                print(f"Rayforce error: {e}")
                return False
        else:
            # Handle as Python code
            return super().runsource(source, filename, symbol)

def custom_input(prompt):
    """Custom input function that handles both Python and Rayforce input."""
    try:
        return input(prompt)
    except EOFError:
        return None

# Create interpreter
interpreter = CustomInterpreter(locals=namespace)
print(f"[DEBUG] REPL starting in {'Rayforce' if interpreter.rayforce_mode else 'Python'} mode.")

# Print banner
print("\nRayforce event loop started. You are now in a Python REPL.")
print("Objects available: policy, event_loop, asyncio")
print("Commands:")
print("  %rayforce - Switch to Rayforce mode")
print("  %python   - Switch to Python mode")
print("  %mode     - Show current mode")
print("  %exit     - Exit Rayforce")
print("Type exit() or Ctrl-D to quit.\n")

# Main REPL loop
while True:
    try:
        # Check if Rayforce is still running
        if not policy._rayforce_loop._running:
            print("\nRayforce has terminated. Exiting...")
            break
            
        mode = "RF" if interpreter.rayforce_mode else "Py"
        line = custom_input(f"{mode}>>> ")
        if line is None:
            break
        interpreter.runsource(line)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        continue
    except Exception as e:
        print(f"Error: {e}")

# Stop the Rayforce event loop when the REPL exits
policy.stop() 