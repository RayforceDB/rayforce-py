# Introduction to raypy

Raypy is an interfacing library to RayforceDB which allows you to manipulate and execute with the Rayfall statements using Python language.

The interaction with the Rayforce is happening via C API bus, which allows us to seamlessly operate with rayforce runtime with little-to-no practical overhead.

## Installation

1. Clone the latest raypy library to your local machine
```bash
git clone git@github.com:singaraiona/raypy.git
```
2. Drop into the lib and ensure make is installed
```bash
cd raypy
apt-get install make  # Linux
brew install make  # MacOS
```
3. Execute make all command to build the library locally
```bash
make all
```
This will:
    - clean the previous builds (also accessible with `make clean`)
    - pull the latest rayforceDB repo and compile the binary from the latest master. __Subject to change once rayforce gets stable releases and versioning.__
    - build the rayforce plugins required for the library (such as raykx, which is KDB IPC).
    - move binaries arond so the library is able to find them.
