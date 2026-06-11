UNAME_S := $(shell uname -s)

RAYFORCE_GITHUB ?= https://github.com/RayforceDB/rayforce.git
RAYFORCE_LOCAL_PATH ?=
EXEC_DIR = $(shell pwd)
LIBNAME = _rayforce.so
PYTHON_VERSION = $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_INCLUDE = $(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('INCLUDEPY'))")


ifeq ($(UNAME_S),Darwin)
  RELEASE_LDFLAGS_PY = $(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('LDFLAGS') or '')")
  SHARED_COMPILE_FLAGS = -undefined dynamic_lookup
else ifeq ($(UNAME_S),Linux)
  RELEASE_LDFLAGS_PY =
  SHARED_COMPILE_FLAGS =
else
  $(error Unsupported platform: $(UNAME_S))
endif

pull_rayforce_from_github:
	@rm -rf $(EXEC_DIR)/tmp/rayforce-c
	@if [ -n "$(RAYFORCE_LOCAL_PATH)" ]; then \
		echo "📂 Copying rayforce from $(RAYFORCE_LOCAL_PATH)..."; \
		mkdir -p $(EXEC_DIR)/tmp && \
		rsync -a \
			--exclude='.git' --exclude='tmp' --exclude='build*' \
			--exclude='*.o' --exclude='*.so' --exclude='*.a' --exclude='*.dylib' \
			"$(RAYFORCE_LOCAL_PATH)/" "$(EXEC_DIR)/tmp/rayforce-c/"; \
	else \
		echo "⬇️  Cloning rayforce repo from $(RAYFORCE_GITHUB)..."; \
		git clone $(RAYFORCE_GITHUB) $(EXEC_DIR)/tmp/rayforce-c; \
	fi

patch_rayforce_makefile:
	@echo "🔧 Patching Makefile for Python support..."
	@mkdir -p $(EXEC_DIR)/tmp/rayforce-c/pyext
	@printf '\n\n# ---- Python extension target (added by rayforce-py) ----\n' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@printf 'PY_SRC = $$(wildcard pyext/*.c)\n' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@printf 'PY_OBJ = $$(PY_SRC:.c=.o)\n' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@printf 'python: CFLAGS = $$(RELEASE_CFLAGS) -DPY_SSIZE_T_CLEAN -I$(PYTHON_INCLUDE) -Ipyext -Wno-macro-redefined -Wno-unused-variable -Wno-unused-function\n' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@printf 'python: LDFLAGS = $$(RELEASE_LDFLAGS) $(RELEASE_LDFLAGS_PY)\n' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@printf 'python: $$(LIB_OBJ) $$(PY_OBJ)\n' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@printf '\t$$(CC) -shared -o $(LIBNAME) $$(CFLAGS) $$(LIB_OBJ) $$(PY_OBJ) $$(LIBS) $$(LDFLAGS) $(SHARED_COMPILE_FLAGS)\n' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile

clean:
	@echo "🧹 Cleaning cache and generated files..."
	@cd $(EXEC_DIR) && rm -rf \
		rayforce/_rayforce_c.so  \
		rayforce/_rayforce.c*.so  \
		rayforce/librayforce.* \
		rayforce/bin \
		build/ \
		*.egg-info \
		dist/ && \
		find . -type d -name "__pycache__" -exec rm -rf {} +
	@cd $(EXEC_DIR) && rm -rf \
		tmp/

rayforce_binaries:
	@mkdir -p tmp/rayforce-c/pyext
	@cp rayforce/capi/*.c tmp/rayforce-c/pyext/
	@cp rayforce/capi/*.h tmp/rayforce-c/pyext/
	@cd tmp/rayforce-c && $(MAKE) python
	@cd tmp/rayforce-c && $(MAKE) release
	@cp tmp/rayforce-c/$(LIBNAME) rayforce/_rayforce_c.so
	@mkdir -p rayforce/bin
	@cp tmp/rayforce-c/rayforce rayforce/bin/rayforce
	@chmod +x rayforce/bin/rayforce

app: pull_rayforce_from_github patch_rayforce_makefile rayforce_binaries

test:
	python3 -u -m pytest -x -vv tests/

test-cov:
	python3 -u -m pytest -m "" -x -vv --durations=20 --cov=rayforce --cov-report=term-missing --cov-report=html tests/

lint:
	python3 -m ruff format tests/ rayforce/ benchmark/
	python3 -m ruff check rayforce/ benchmark/ --fix
	python3 -m ruff check tests/ --fix --select I
	python3 -m mypy rayforce/
	clang-format -i rayforce/capi/*

ipython:
	ipython -i -c "from rayforce import *"

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
	python3 -u -m pytest -x -vv tests/

# }}
