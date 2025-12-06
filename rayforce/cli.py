import os
import sys
import subprocess
from pathlib import Path


def find_rayforce_executable():
    package_dir = Path(__file__).parent
    bundled_executable = package_dir / "bin" / "rayforce"

    if bundled_executable.exists() and os.access(bundled_executable, os.X_OK):
        return str(bundled_executable)

    project_root = package_dir.parent
    dev_executable = project_root / "tmp" / "rayforce-c" / "rayforce"

    if dev_executable.exists() and os.access(dev_executable, os.X_OK):
        return str(dev_executable)

    raise FileNotFoundError(
        "Rayforce executable not found. Try to reinstall the library"
    )


def main():
    try:
        executable = find_rayforce_executable()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("Launching Rayforce REPL...")
    subprocess.call([executable] + sys.argv[1:])


if __name__ == "__main__":
    main()
