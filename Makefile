UNAME_S := $(shell uname -s)

RAYFORCE_GITHUB = git@github.com:singaraiona/rayforce.git
EXEC_DIR = $(shell pwd)


ifeq ($(UNAME_S),Darwin)
  COMPILED_LIB_NAME = librayforce.dylib
  TARGET_LIB_NAME = $(COMPILED_LIB_NAME)
  PY_MODULE_NAME = _rayforce.so
  LIBNAME = $(PY_MODULE_NAME)
  RAYKX_LIB_NAME = libraykx.dylib
  RELEASE_LDFLAGS = $(shell python3.13-config --ldflags)
  SHARED_COMPILE_FLAGS = -lpython3.13
else ifeq ($(UNAME_S),Linux)
  COMPILED_LIB_NAME = rayforce.so
  TARGET_LIB_NAME = librayforce.so
  RAYKX_LIB_NAME = libraykx.so
  PY_MODULE_NAME = rayforce.so
  LIBNAME = $$(LIBNAME)
  RELEASE_LDFLAGS = $$(RELEASE_LDFLAGS)
  SHARED_COMPILE_FLAGS = 
else
  $(error Unsupported platform: $(UNAME_S))
endif

pull_from_gh:
	@rm -rf $(EXEC_DIR)/tmp/rayforce-c && \
	echo "⬇️  Cloning rayforce repo from GitHub..."; \
	git clone $(RAYFORCE_GITHUB) $(EXEC_DIR)/tmp/rayforce-c && \
	cp -r $(EXEC_DIR)/tmp/rayforce-c/core $(EXEC_DIR)/raypy/rayforce

patch_makefile:
	@echo "🔧 Patching Makefile for Python support..."
	@echo '\n# Build Python module' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'PY_OBJECTS = core/raypy.o' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: CFLAGS = $$(RELEASE_CFLAGS) $$(shell python3.13-config --includes)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: LDFLAGS = $(RELEASE_LDFLAGS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo 'python: $$(CORE_OBJECTS) $$(PY_OBJECTS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile
	@echo '\t$$(CC) -shared -o $(LIBNAME) $$(CFLAGS) $$(CORE_OBJECTS) $$(PY_OBJECTS) $$(LIBS) $$(LDFLAGS) $(SHARED_COMPILE_FLAGS)' >> $(EXEC_DIR)/tmp/rayforce-c/Makefile

clean-ext:
	@cd $(EXEC_DIR) && rm -rf \
		raypy/_rayforce.so  \
		raypy/_rayforce.c*.so  \
		raypy/librayforce.* \
		raypy/plugins/libraykx.* \
		build/ \
		dist/ && \
		find . -type d -name "__pycache__" -exec rm -rf {} +

clean: clean-ext
	@echo "🧹 Cleaning cache and generated files..."
	@cd $(EXEC_DIR) && rm -rf \
		raypy/rayforce/ \
		tmp/ \

ext: 
	@cp raypy/raypy.c tmp/rayforce-c/core/raypy.c
	@cd tmp/rayforce-c && $(MAKE) python
	@cd tmp/rayforce-c/ext/raykx && $(MAKE) release
	@cp tmp/rayforce-c/$(PY_MODULE_NAME) raypy/_rayforce.so
	@cp tmp/rayforce-c/ext/raykx/$(RAYKX_LIB_NAME) raypy/plugins/$(RAYKX_LIB_NAME)

all: pull_from_gh patch_makefile ext

test:
	pytest -x -vv tests/

lint:
	ruff format tests/ raypy/
	ruff check raypy/ --fix
	mypy raypy/

wheel:
	@echo "📦 Building wheel package..." 
	@rm -rf build/ dist/ *.egg-info/ 
	@python3 setup.py bdist_wheel 

install-wheel: wheel
	@echo "🔧 Installing wheel locally..."
	@pip3 install --force-reinstall dist/*.whl
