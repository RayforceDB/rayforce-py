# raypy

Python library for RayforceDB - a high-performance, column-oriented analytical database.

## Overview

raypy provides Python bindings for RayforceDB, allowing you to interact with RayforceDB's powerful data processing capabilities from Python. These bindings are generated using SWIG and provide a direct interface to the RayforceDB C library.

## Building from Source

The build process follows these steps:

1. Clone the RayforceDB C repository
2. Build the shared library
3. Generate Python bindings with SWIG
4. Compile the Python extension module
5. Create a wheel package

### Prerequisites

- Python 3.6+
- C compiler (clang is used by default)
- SWIG 4.0+
- Git
- Make

### Build Commands

The project uses a Makefile with several targets:

```bash
# Clean previous build artifacts
make clean

# Rebuild the extension module (clean + pull code + build)
make rebuild

# Run an importability test to verify the build
make importability_test

# Build a Python wheel package (includes rebuild and test)
make rebuild_wheel
```

The final wheel package will be available in the `dist/` directory.

## Usage

Basic example of using raypy:

```python
import rayforce

# Initialize the RayforceDB engine
rayforce.ray_init()

# Create and add two integers
a = rayforce.i64(2)
b = rayforce.i64(3)
result = rayforce.ray_add(a, b)

# Print the result
print(result.i64)  # Outputs: 5

# Clean up
rayforce.ray_clean()
```

## Project Structure

- `raypy/` - Main package directory
  - `__init__.py` - Package initialization
  - `rayforce.py` - Generated SWIG Python interface
  - `_rayforce.so` - Compiled extension module
  - `rayforce.i` - SWIG interface file
  - `librayforce.dylib` - RayforceDB shared library


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
