#!/bin/bash
set -e

EXEC_DIR=$(pwd)
PYTHON_VERSIONS=("3.11" "3.12" "3.13" "3.14")

echo "🧪 Testing Linux wheels for Python versions: ${PYTHON_VERSIONS[*]}"
echo ""

for PYTHON_VERSION in "${PYTHON_VERSIONS[@]}"; do
    echo "Testing Python ${PYTHON_VERSION}"

    docker run --platform linux/amd64 -it --rm \
        -v "${EXEC_DIR}:/app" \
        -w /app \
        python:${PYTHON_VERSION} \
        bash -c "
            set -e
            echo 'Pulling dependencies...'
            apt-get update -qq
            apt-get install -y -qq clang make git > /dev/null 2>&1
            pip install -q ruff mypy pandas polars pytest

            make app
            make citest

            echo '✅ Python ${PYTHON_VERSION} tests passed!'
        "
    
    if [ $? -eq 0 ]; then
        echo "✅ Python ${PYTHON_VERSION}: SUCCESS"
    else
        echo "❌ Python ${PYTHON_VERSION}: FAILED"
        exit 1
    fi
    echo ""
done

echo "✅ All Python versions passed!"
