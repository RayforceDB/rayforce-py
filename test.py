#!/usr/bin/env python3

import sys
import os

from raypy import _rayforce as r
from raypy.types import scalar, container

if __name__ == "__main__":
    print("Hello, World!")
    a = scalar.i64(1)
    print(a)
    r.runtime_run()