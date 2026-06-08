#!/bin/bash
set -e -x

EXEC_DIR=$(pwd)
RAYFORCE_GITHUB="${RAYFORCE_GITHUB:-https://github.com/RayforceDB/rayforce.git}"
RAYFORCE_LOCAL_PATH="${RAYFORCE_LOCAL_PATH:-}"

PYTHON_BIN="${PYTHON_BIN:-python}"
PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | awk '{print $2}')

echo "Cleaning previous build artifacts..."
rm -rf "${EXEC_DIR}/tmp/rayforce-c"
rm -rf "${EXEC_DIR}/rayforce/bin"
rm -rf "${EXEC_DIR}/rayforce/_rayforce_c.so"
rm -rf "${EXEC_DIR}/build"
find "${EXEC_DIR}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "${EXEC_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

if [[ -n "${RAYFORCE_LOCAL_PATH}" ]]; then
    echo "Copying rayforce2 from ${RAYFORCE_LOCAL_PATH}..."
    mkdir -p "${EXEC_DIR}/tmp"
    # Exclude pre-built artifacts so the Linux build doesn't pick up host
    # Mach-O / arm64 .o files left by a local `make` in RAYFORCE_LOCAL_PATH.
    rsync -a \
        --exclude='.git' --exclude='tmp' --exclude='build*' \
        --exclude='*.o' --exclude='*.so' --exclude='*.a' --exclude='*.dylib' \
        "${RAYFORCE_LOCAL_PATH}/" "${EXEC_DIR}/tmp/rayforce-c/"
else
    echo "Cloning rayforce2 repo from GitHub..."
    git clone "${RAYFORCE_GITHUB}" "${EXEC_DIR}/tmp/rayforce-c"
fi

UNAME_S=$(uname -s)

echo "Patching Makefile to use portable CPU target instead of -march=native..."
if [[ "$UNAME_S" != "Darwin" ]]; then
    # Replace -march=native with -march=x86-64-v3 (AVX2 baseline) for portable Linux builds
    sed -i 's/-march=native/-march=x86-64-v3/g' "${EXEC_DIR}/tmp/rayforce-c/Makefile"
fi
PYTHON_INCLUDE=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY'))")
PYTHON_PYVER=$($PYTHON_BIN -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

if [[ "$UNAME_S" == "Darwin" ]]; then
    PYTHON_LDFLAGS=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('LDFLAGS') or '')")
    SHARED_FLAGS="-undefined dynamic_lookup"
else
    PYTHON_LDFLAGS=""
    SHARED_FLAGS=""
fi

echo "Copying pyext sources..."
mkdir -p "${EXEC_DIR}/tmp/rayforce-c/pyext"
cp "${EXEC_DIR}"/rayforce/capi/*.c "${EXEC_DIR}/tmp/rayforce-c/pyext/"
cp "${EXEC_DIR}"/rayforce/capi/*.h "${EXEC_DIR}/tmp/rayforce-c/pyext/"

echo "Patching v2 Makefile for Python extension target..."
# PY_SRC = wildcard so any new pyext/*.c is picked up automatically and stays
# in sync with the local Makefile (which uses an explicit list).
cat >> "${EXEC_DIR}/tmp/rayforce-c/Makefile" << EOF


# ---- Python extension target (added by rayforce-py prepare_build.sh) ----
PY_SRC = \$(wildcard pyext/*.c)
PY_OBJ = \$(PY_SRC:.c=.o)
python: CFLAGS = \$(RELEASE_CFLAGS) -DPY_SSIZE_T_CLEAN -I${PYTHON_INCLUDE} -Ipyext -Wno-macro-redefined -Wno-unused-variable -Wno-unused-function
python: LDFLAGS = \$(RELEASE_LDFLAGS) ${PYTHON_LDFLAGS}
python: \$(LIB_OBJ) \$(PY_OBJ)
	\$(CC) -shared -o _rayforce.so \$(CFLAGS) \$(LIB_OBJ) \$(PY_OBJ) \$(LIBS) \$(LDFLAGS) ${SHARED_FLAGS}
EOF

cd "${EXEC_DIR}/tmp/rayforce-c"
make python
cp "${EXEC_DIR}/tmp/rayforce-c/_rayforce.so" "${EXEC_DIR}/rayforce/_rayforce_c.so"

echo "Building Rayforce executable..."
cd "${EXEC_DIR}/tmp/rayforce-c"
make release
mkdir -p "${EXEC_DIR}/rayforce/bin"
cp "${EXEC_DIR}/tmp/rayforce-c/rayforce" "${EXEC_DIR}/rayforce/bin/rayforce"
chmod +x "${EXEC_DIR}/rayforce/bin/rayforce"

echo "Build preparation complete!"
