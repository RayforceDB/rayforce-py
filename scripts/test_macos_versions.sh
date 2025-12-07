#!/bin/bash
set -e

PYTHON_VERSIONS=("3.11" "3.12" "3.13" "3.14")

echo "🧪 Testing macOS builds for Python versions: ${PYTHON_VERSIONS[*]}"
echo ""

if ! command -v pyenv &> /dev/null; then
    echo "Error: pyenv is not installed or not in PATH"
    exit 1
fi

eval "$(pyenv init -)"

for PYTHON_VERSION in "${PYTHON_VERSIONS[@]}"; do
    echo "Testing Python ${PYTHON_VERSION}"

    pyenv shell ${PYTHON_VERSION}

    ACTUAL_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    if [ "${ACTUAL_VERSION}" != "${PYTHON_VERSION}" ]; then
        echo "Error: Expected Python ${PYTHON_VERSION}, but got ${ACTUAL_VERSION}"
        exit 1
    fi

    make clean > /dev/null 2>&1 || true

    pip install -q ruff mypy pandas polars pytest

    if ! make app; then
        echo "❌ Python ${PYTHON_VERSION}: make app FAILED"
        exit 1
    fi

    if ! make citest; then
        echo "❌ Python ${PYTHON_VERSION}: make citest FAILED"
        exit 1
    fi

    echo "✅ Python ${PYTHON_VERSION}: SUCCESS"
    echo ""
done

echo "✅ All Python versions passed!"
