# Detect OS (Windows uses OS env var, Unix uses uname)
ifeq ($(OS),Windows_NT)
  UNAME_S := Windows
else
  UNAME_S := $(shell uname -s)
endif

RAYFORCE_GITHUB = https://github.com/RayforceDB/rayforce.git
EXEC_DIR = $(shell pwd)

ifeq ($(UNAME_S),Darwin)
  LIBNAME = _rayforce.so
  RAYKX_LIB_NAME = libraykx.dylib
  RELEASE_LDFLAGS = $(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('LDFLAGS') or '')")
  PYTHON_VERSION = $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  SHARED_COMPILE_FLAGS = -lpython$(PYTHON_VERSION)
  RAYFORCE_BIN = rayforce
  RM = rm -rf
  CP = cp
  MKDIR = mkdir -p
  CHMOD = chmod +x
else ifeq ($(UNAME_S),Linux)
  LIBNAME = _rayforce.so
  RAYKX_LIB_NAME = libraykx.so
  RELEASE_LDFLAGS = $$(RELEASE_LDFLAGS)
  SHARED_COMPILE_FLAGS =
  RAYFORCE_BIN = rayforce
  RM = rm -rf
  CP = cp
  MKDIR = mkdir -p
  CHMOD = chmod +x
else ifeq ($(UNAME_S),Windows)
  LIBNAME = _rayforce.pyd
  RAYKX_LIB_NAME = raykx.dll
  PYTHON_INCLUDE = $(shell python -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY'))")
  PYTHON_LIBS = $(shell python -c "import sysconfig; import os; print(os.path.join(sysconfig.get_config_var('BINDIR'), 'libs'))")
  PYTHON_VERSION = $(shell python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
  RELEASE_LDFLAGS = -fuse-ld=lld -L"$(PYTHON_LIBS)" -lpython$(PYTHON_VERSION)
  SHARED_COMPILE_FLAGS = -D_CRT_SECURE_NO_WARNINGS
  RAYFORCE_BIN = rayforce.exe
  RM = del /F /Q
  CP = copy
  MKDIR = mkdir
  CHMOD = echo
  # Use forward slashes for paths in recipes
  EXEC_DIR := $(subst \,/,$(CURDIR))
else
  $(error Unsupported platform: $(UNAME_S))
endif

pull_rayforce_from_github:
ifeq ($(UNAME_S),Windows)
	@if exist tmp\rayforce-c rmdir /S /Q tmp\rayforce-c
	@echo Cloning rayforce repo from GitHub...
	@git clone $(RAYFORCE_GITHUB) tmp/rayforce-c
	@xcopy /E /I /Y tmp\rayforce-c\core rayforce\rayforce\
else
	@rm -rf $(EXEC_DIR)/tmp/rayforce-c && \
	echo "⬇️  Cloning rayforce repo from GitHub..."; \
	git clone $(RAYFORCE_GITHUB) $(EXEC_DIR)/tmp/rayforce-c && \
	cp -r $(EXEC_DIR)/tmp/rayforce-c/core $(EXEC_DIR)/rayforce/rayforce
endif

patch_rayforce_makefile:
ifeq ($(UNAME_S),Windows)
	@echo Patching Makefile for Python support...
	@echo. >> tmp\rayforce-c\Makefile
	@echo # Build Python module >> tmp\rayforce-c\Makefile
	@echo PY_OBJECTS = core/rayforce_c.o core/raypy_init_from_py.o core/raypy_init_from_buffer.o core/raypy_read_from_rf.o core/raypy_queries.o core/raypy_io.o core/raypy_binary.o core/raypy_dynlib.o core/raypy_eval.o core/raypy_iter.o core/raypy_serde.o >> tmp\rayforce-c\Makefile
	@echo PY_APP_OBJECTS = app/term.o >> tmp\rayforce-c\Makefile
	@echo python: CFLAGS = $$(RELEASE_CFLAGS) -I"$(PYTHON_INCLUDE)" -Wno-macro-redefined >> tmp\rayforce-c\Makefile
	@echo python: LDFLAGS = $(RELEASE_LDFLAGS) >> tmp\rayforce-c\Makefile
	@echo python: $$(CORE_OBJECTS) $$(PY_OBJECTS) $$(PY_APP_OBJECTS) >> tmp\rayforce-c\Makefile
	@echo 	$$(CC) -shared -o $(LIBNAME) $$(CFLAGS) $$(CORE_OBJECTS) $$(PY_OBJECTS) $$(PY_APP_OBJECTS) $$(LIBS) $$(LDFLAGS) $(SHARED_COMPILE_FLAGS) >> tmp\rayforce-c\Makefile
else
	@echo "🔧 Patching Makefile for Python support..."
	@echo '\n# Build Python module' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'PY_OBJECTS = core/rayforce_c.o core/raypy_init_from_py.o core/raypy_init_from_buffer.o core/raypy_read_from_rf.o core/raypy_queries.o core/raypy_io.o core/raypy_binary.o core/raypy_dynlib.o core/raypy_eval.o core/raypy_iter.o core/raypy_serde.o' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'PY_APP_OBJECTS = app/term.o' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: CFLAGS = $$(RELEASE_CFLAGS) -I$$(shell python3 -c "import sysconfig; print(sysconfig.get_config_var(\"INCLUDEPY\"))") -Wno-macro-redefined' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: LDFLAGS = $(RELEASE_LDFLAGS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: $$(CORE_OBJECTS) $$(PY_OBJECTS) $$(PY_APP_OBJECTS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo '\t$$(CC) -shared -o $(LIBNAME) $$(CFLAGS) $$(CORE_OBJECTS) $$(PY_OBJECTS) $$(PY_APP_OBJECTS) $$(LIBS) $$(LDFLAGS) $(SHARED_COMPILE_FLAGS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
endif

clean:
ifeq ($(UNAME_S),Windows)
	@echo Cleaning cache and generated files...
	@if exist rayforce\_rayforce_c.pyd del /F /Q rayforce\_rayforce_c.pyd
	@if exist rayforce\rayforce.dll del /F /Q rayforce\rayforce.dll
	@if exist rayforce\plugins\raykx.dll del /F /Q rayforce\plugins\raykx.dll
	@if exist rayforce\bin rmdir /S /Q rayforce\bin
	@if exist build rmdir /S /Q build
	@if exist dist rmdir /S /Q dist
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /S /Q "%%d"
	@for /d %%d in (*.egg-info) do @if exist "%%d" rmdir /S /Q "%%d"
	@if exist rayforce\rayforce rmdir /S /Q rayforce\rayforce
	@if exist tmp rmdir /S /Q tmp
else
	@echo "🧹 Cleaning cache and generated files..."
	@cd $(EXEC_DIR) && rm -rf \
		rayforce/_rayforce_c.so  \
		rayforce/_rayforce.c*.so  \
		rayforce/librayforce.* \
		rayforce/plugins/libraykx.* \
		rayforce/bin \
		build/ \
		*.egg-info \
		dist/ && \
		find . -type d -name "__pycache__" -exec rm -rf {} +
	@cd $(EXEC_DIR) && rm -rf \
		rayforce/rayforce/ \
		tmp/
endif

rayforce_binaries:
ifeq ($(UNAME_S),Windows)
	@copy rayforce\capi\rayforce_c.c tmp\rayforce-c\core\
	@copy rayforce\capi\rayforce_c.h tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_init_from_py.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_init_from_buffer.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_read_from_rf.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_queries.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_io.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_binary.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_dynlib.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_eval.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_iter.c tmp\rayforce-c\core\
	@copy rayforce\capi\raypy_serde.c tmp\rayforce-c\core\
	cd tmp\rayforce-c && $(MAKE) python
	cd tmp\rayforce-c && $(MAKE) release
	cd tmp\rayforce-c\ext\raykx && $(MAKE) release
	@copy tmp\rayforce-c\$(LIBNAME) rayforce\_rayforce_c.pyd
	@copy tmp\rayforce-c\ext\raykx\$(RAYKX_LIB_NAME) rayforce\plugins\
	@if not exist rayforce\bin mkdir rayforce\bin
	@copy tmp\rayforce-c\$(RAYFORCE_BIN) rayforce\bin\
else
	@cp rayforce/capi/rayforce_c.c tmp/rayforce-c/core/rayforce_c.c
	@cp rayforce/capi/rayforce_c.h tmp/rayforce-c/core/rayforce_c.h
	@cp rayforce/capi/raypy_init_from_py.c tmp/rayforce-c/core/raypy_init_from_py.c
	@cp rayforce/capi/raypy_init_from_buffer.c tmp/rayforce-c/core/raypy_init_from_buffer.c
	@cp rayforce/capi/raypy_read_from_rf.c tmp/rayforce-c/core/raypy_read_from_rf.c
	@cp rayforce/capi/raypy_queries.c tmp/rayforce-c/core/raypy_queries.c
	@cp rayforce/capi/raypy_io.c tmp/rayforce-c/core/raypy_io.c
	@cp rayforce/capi/raypy_binary.c tmp/rayforce-c/core/raypy_binary.c
	@cp rayforce/capi/raypy_dynlib.c tmp/rayforce-c/core/raypy_dynlib.c
	@cp rayforce/capi/raypy_eval.c tmp/rayforce-c/core/raypy_eval.c
	@cp rayforce/capi/raypy_iter.c tmp/rayforce-c/core/raypy_iter.c
	@cp rayforce/capi/raypy_serde.c tmp/rayforce-c/core/raypy_serde.c
	@cd tmp/rayforce-c && $(MAKE) python
	@cd tmp/rayforce-c && $(MAKE) release
	@cd tmp/rayforce-c/ext/raykx && $(MAKE) release
	@cp tmp/rayforce-c/$(LIBNAME) rayforce/_rayforce_c.so
	@cp tmp/rayforce-c/ext/raykx/$(RAYKX_LIB_NAME) rayforce/plugins/$(RAYKX_LIB_NAME)
	@mkdir -p rayforce/bin
	@cp tmp/rayforce-c/$(RAYFORCE_BIN) rayforce/bin/$(RAYFORCE_BIN)
	@chmod +x rayforce/bin/$(RAYFORCE_BIN)
endif

app: pull_rayforce_from_github patch_rayforce_makefile rayforce_binaries

# Use python3 on Unix, python on Windows
ifeq ($(UNAME_S),Windows)
  PYTHON = python
else
  PYTHON = python3
endif

test:
	$(PYTHON) -m pytest -x -vv tests/

test-cov:
	$(PYTHON) -m pytest -x -vv --cov=rayforce --cov-report=term-missing --cov-report=html tests/
	$(PYTHON) -m pytest -x -vv --cov=rayforce --cov-report=term-missing tests/

lint:
	$(PYTHON) -m ruff format tests/ rayforce/
	$(PYTHON) -m ruff check rayforce/ --fix
	$(PYTHON) -m ruff check tests/ --fix --select I
	$(PYTHON) -m mypy rayforce/
	clang-format -i rayforce/capi/*

ipython:
	ipython -i -c "from rayforce import *"

websocket:


benchmarkdb:
	$(PYTHON) benchmark/run.py $(ARGS)

# CI {{
wheels:
	cibuildwheel --platform linux --archs x86_64
	cibuildwheel --platform macos --archs arm64

wheels-windows:
	cibuildwheel --platform windows --archs AMD64

citest:
	$(PYTHON) -m ruff format tests/ rayforce/ --check
	$(PYTHON) -m ruff check rayforce/
	$(PYTHON) -m ruff check tests/ --select I
	$(PYTHON) -m mypy rayforce/
	$(PYTHON) -m pytest -x -vv tests/

test-linux-versions:
	@chmod +x scripts/test_linux_versions.sh
	@./scripts/test_linux_versions.sh

test-macos-versions:
	@chmod +x scripts/test_macos_versions.sh
	@./scripts/test_macos_versions.sh

test-windows-versions:
	@powershell -ExecutionPolicy Bypass -File scripts/test_windows_versions.ps1

test-versions: test-linux-versions test-macos-versions
# }}
