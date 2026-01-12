#!/bin/bash
set -e -x

EXEC_DIR=$(pwd)
RAYFORCE_GITHUB="${RAYFORCE_GITHUB:-https://github.com/RayforceDB/rayforce.git}"

PYTHON_BIN="${PYTHON_BIN:-python}"
PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | awk '{print $2}')

echo "Cleaning previous build artifacts..."
rm -rf "${EXEC_DIR}/tmp/rayforce-c"
rm -rf "${EXEC_DIR}/rayforce/rayforce"
rm -rf "${EXEC_DIR}/rayforce/bin"
rm -rf "${EXEC_DIR}/rayforce/_rayforce_c.so" "${EXEC_DIR}/rayforce/_rayforce_c.pyd"
rm -rf "${EXEC_DIR}/rayforce/plugins/libraykx".*
rm -rf "${EXEC_DIR}/build"
find "${EXEC_DIR}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "${EXEC_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "Cloning rayforce repo from GitHub..."
git clone "${RAYFORCE_GITHUB}" "${EXEC_DIR}/tmp/rayforce-c"
cp -r "${EXEC_DIR}/tmp/rayforce-c/core" "${EXEC_DIR}/rayforce/rayforce"

UNAME_S=$(uname -s 2>/dev/null || echo Windows_NT)

PYTHON_INCLUDE=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY') or '')")
PYTHON_LIBDIR=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR') or '')")
PYTHON_BASE=$($PYTHON_BIN -c "import sys; print(sys.base_prefix)")
PYTHON_LIBDIR_FALLBACK="${PYTHON_BASE}/libs"
PYTHON_LIBDIR_USE="${PYTHON_LIBDIR:-$PYTHON_LIBDIR_FALLBACK}"

# python311-style name for linking (mingw import lib)
PYTHON_LDNAME=$($PYTHON_BIN -c "import sys; print(f'python{sys.version_info.major}{sys.version_info.minor}')")

if [[ "$UNAME_S" == "Darwin" ]]; then
    LIB_EXT="dylib"
    MODULE_EXT="so"
    EXE_EXT=""
    PYTHON_LDFLAGS=$($PYTHON_BIN -c "import sysconfig; print(sysconfig.get_config_var('LDFLAGS') or '')")
    SHARED_FLAGS="-undefined dynamic_lookup"
    PY_LINK_FLAGS=""
elif [[ "$UNAME_S" == "Linux" ]]; then
    LIB_EXT="so"
    MODULE_EXT="so"
    EXE_EXT=""
    PYTHON_LDFLAGS=""
    SHARED_FLAGS=""
    PY_LINK_FLAGS=""
elif [[ "$UNAME_S" == MINGW* || "$UNAME_S" == MSYS* || "$UNAME_S" == CYGWIN* ]]; then
    LIB_EXT="dll"
    MODULE_EXT="pyd"
    EXE_EXT=".exe"
    PYTHON_LDFLAGS=""
    SHARED_FLAGS="-Wl,--enable-auto-import"
    PY_LINK_FLAGS="-L\"${PYTHON_LIBDIR_USE}\" -l${PYTHON_LDNAME}"
else
    echo "Unsupported platform: $UNAME_S"
    exit 1
fi

echo "Patching Makefile for Python support..."
cat >> "${EXEC_DIR}/tmp/rayforce-c/Makefile" << EOF

PY_OBJECTS = core/rayforce_c.o core/raypy_init_from_py.o core/raypy_init_from_buffer.o core/raypy_read_from_rf.o core/raypy_queries.o core/raypy_io.o core/raypy_binary.o core/raypy_dynlib.o core/raypy_eval.o core/raypy_iter.o core/raypy_serde.o
PY_APP_OBJECTS = app/term.o
python: CFLAGS = \$(RELEASE_CFLAGS) -DPY_SSIZE_T_CLEAN -I"${PYTHON_INCLUDE}" -Wno-macro-redefined
python: LDFLAGS = \$(RELEASE_LDFLAGS) ${PYTHON_LDFLAGS}
python: \$(CORE_OBJECTS) \$(PY_OBJECTS) \$(PY_APP_OBJECTS)
	\$(CC) -shared -o _rayforce.${MODULE_EXT} \$(CFLAGS) \$(CORE_OBJECTS) \$(PY_OBJECTS) \$(PY_APP_OBJECTS) \$(LIBS) \$(LDFLAGS) ${SHARED_FLAGS} ${PY_LINK_FLAGS}
EOF

echo "Building Rayforce..."
cp "${EXEC_DIR}/rayforce/capi/rayforce_c.c" "${EXEC_DIR}/tmp/rayforce-c/core/rayforce_c.c"
cp "${EXEC_DIR}/rayforce/capi/rayforce_c.h" "${EXEC_DIR}/tmp/rayforce-c/core/rayforce_c.h"
cp "${EXEC_DIR}/rayforce/capi/raypy_init_from_py.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_init_from_py.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_init_from_buffer.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_init_from_buffer.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_read_from_rf.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_read_from_rf.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_queries.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_queries.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_io.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_io.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_binary.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_binary.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_dynlib.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_dynlib.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_eval.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_eval.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_iter.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_iter.c"
cp "${EXEC_DIR}/rayforce/capi/raypy_serde.c" "${EXEC_DIR}/tmp/rayforce-c/core/raypy_serde.c"

cd "${EXEC_DIR}/tmp/rayforce-c"
make python
cp "${EXEC_DIR}/tmp/rayforce-c/_rayforce.${MODULE_EXT}" "${EXEC_DIR}/rayforce/_rayforce_c.${MODULE_EXT}"

echo "Building Raykx..."
cd "${EXEC_DIR}/tmp/rayforce-c/ext/raykx"
make release
cp "${EXEC_DIR}/tmp/rayforce-c/ext/raykx/libraykx.${LIB_EXT}" "${EXEC_DIR}/rayforce/plugins/libraykx.${LIB_EXT}"

echo "Building Rayforce executable..."
cd "${EXEC_DIR}/tmp/rayforce-c"
make release
mkdir -p "${EXEC_DIR}/rayforce/bin"
cp "${EXEC_DIR}/tmp/rayforce-c/rayforce${EXE_EXT}" "${EXEC_DIR}/rayforce/bin/rayforce${EXE_EXT}"
chmod +x "${EXEC_DIR}/rayforce/bin/rayforce${EXE_EXT}"

echo "Build preparation complete!"
