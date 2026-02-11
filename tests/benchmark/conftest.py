"""Benchmark test configuration.

Run benchmarks with: pytest tests/benchmark/ -m benchmark
"""

import pytest

# All tests in this directory are benchmarks
pytestmark = pytest.mark.benchmark
