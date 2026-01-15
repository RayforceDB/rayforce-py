UNAME_S := $(shell uname -s)

RAYFORCE_GITHUB = https://github.com/RayforceDB/rayforce.git
EXEC_DIR = $(shell pwd)
LIBNAME = _rayforce.so


ifeq ($(UNAME_S),Darwin)
  RAYKX_LIB_NAME = libraykx.dylib
  RELEASE_LDFLAGS = $(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('LDFLAGS') or '')")
  PYTHON_VERSION = $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  SHARED_COMPILE_FLAGS = -lpython$(PYTHON_VERSION)
else ifeq ($(UNAME_S),Linux)
  RAYKX_LIB_NAME = libraykx.so
  RELEASE_LDFLAGS = $$(RELEASE_LDFLAGS)
  SHARED_COMPILE_FLAGS =
else
  $(error Unsupported platform: $(UNAME_S))
endif

pull_rayforce_from_github:
	@rm -rf $(EXEC_DIR)/tmp/rayforce-c && \
	echo "⬇️  Cloning rayforce repo from GitHub..."; \
	git clone $(RAYFORCE_GITHUB) $(EXEC_DIR)/tmp/rayforce-c && \
	cp -r $(EXEC_DIR)/tmp/rayforce-c/core $(EXEC_DIR)/rayforce/rayforce

patch_rayforce_makefile:
	@echo "🔧 Patching Makefile for Python support..."
	@echo '\n# Build Python module' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'PY_OBJECTS = core/rayforce_c.o core/raypy_init_from_py.o core/raypy_init_from_buffer.o core/raypy_read_from_rf.o core/raypy_queries.o core/raypy_io.o core/raypy_binary.o core/raypy_dynlib.o core/raypy_eval.o core/raypy_iter.o core/raypy_serde.o' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'PY_APP_OBJECTS = app/term.o' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: CFLAGS = $$(RELEASE_CFLAGS) -I$$(shell python3 -c "import sysconfig; print(sysconfig.get_config_var(\"INCLUDEPY\"))") -Wno-macro-redefined' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: LDFLAGS = $(RELEASE_LDFLAGS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: $$(CORE_OBJECTS) $$(PY_OBJECTS) $$(PY_APP_OBJECTS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo '\t$$(CC) -shared -o $(LIBNAME) $$(CFLAGS) $$(CORE_OBJECTS) $$(PY_OBJECTS) $$(PY_APP_OBJECTS) $$(LIBS) $$(LDFLAGS) $(SHARED_COMPILE_FLAGS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile

clean:
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
		tmp/ \

rayforce_binaries:
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
	@cp tmp/rayforce-c/rayforce rayforce/bin/rayforce
	@chmod +x rayforce/bin/rayforce

app: pull_rayforce_from_github patch_rayforce_makefile rayforce_binaries

test:
	python3 -m pytest -x -vv tests/

test-cov:
	python3 -m pytest -x -vv --cov=rayforce --cov-report=term-missing --cov-report=html tests/
	python3 -m pytest -x -vv --cov=rayforce --cov-report=term-missing tests/

lint:
	python3 -m ruff format tests/ rayforce/ benchmark/
	python3 -m ruff check rayforce/ benchmark/ --fix
	python3 -m ruff check tests/ --fix --select I
	python3 -m mypy rayforce/
	clang-format -i rayforce/capi/*

ipython:
	ipython -i -c "from rayforce import *"

websocket:


benchmarkdb:
	python3 benchmark/run.py $(ARGS)

# CI {{
wheels:
	cibuildwheel --platform linux --archs x86_64
	cibuildwheel --platform macos --archs arm64

citest:
	python3 -m ruff format tests/ rayforce/ --check
	python3 -m ruff check rayforce/
	python3 -m ruff check tests/ --select I
	python3 -m mypy rayforce/
	python3 -m pytest -x -vv tests/

test-linux-versions:
	@chmod +x scripts/test_linux_versions.sh
	@./scripts/test_linux_versions.sh

test-macos-versions:
	@chmod +x scripts/test_macos_versions.sh
	@./scripts/test_macos_versions.sh

test-versions: test-linux-versions test-macos-versions
# }}
