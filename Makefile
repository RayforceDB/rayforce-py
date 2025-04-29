CC = clang

ARCH = $(shell uname -m)
PYTHON_VERSION := $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_INCLUDE := $(shell python3 -c "from sysconfig import get_paths; print(get_paths()['include'])")
PYTHON_LIB := $(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('LIBPL'))")

EXEC_DIR = $(shell pwd)

# Directory where temporary files for build are stored
TEMP_DIR = $(EXEC_DIR)/tmp
LIBRARY_DIR = $(EXEC_DIR)/raypy

# MacOS-specific file
BUILT_RAYFORCE_C_LIB = librayforce.dylib

.PHONY: pull_from_gh build_shared_lib compile_lib wheel build rebuild clean lint test

pull_from_gh:
	@rm -rf $(EXEC_DIR)/tmp/rayforce-c && \
	echo "⬇️  Cloning rayforce repo from github..."; \
	git clone git@github.com:singaraiona/rayforce.git $(EXEC_DIR)/tmp/rayforce-c \

build_shared_lib:
	@echo "👷  Building rayforce shared lib..." && \
	cd $(EXEC_DIR)/tmp/rayforce-c && make shared && cd $(EXEC_DIR) && \
	cp $(EXEC_DIR)/tmp/rayforce-c/$(BUILT_RAYFORCE_C_LIB) $(EXEC_DIR)/raypy/$(BUILT_RAYFORCE_C_LIB) && \
	swig -python -I$(EXEC_DIR)/tmp/rayforce-c/core $(EXEC_DIR)/raypy/rayforce.i && \
	echo "🟡 Rayforce library ready"

clean:
	@echo "🧹 Cleaning generated files..."
	@cd $(EXEC_DIR) && rm -rf \
		raypy/_rayforce.so  \
		raypy/rayforce_wrap.c  \
		raypy/librayforce.dylib  \
		raypy/rayforce.py  \
		raypy/rayforce.so  \
		raypy/librayforce.so  \
		$(EXEC_DIR)/tmp  \
		build/  \
		temp/  \
		dist/  \
		raypy.egg-info/

compile_lib: 
	@echo "⚙️  Compiling Python extension..."; \
	$(CC) -x c -shared -fPIC -std=c99 -arch $(ARCH) \
		-I$(PYTHON_INCLUDE) -I$(EXEC_DIR)/tmp/rayforce-c/core \
		$(EXEC_DIR)/raypy/rayforce_wrap.c -o $(EXEC_DIR)/raypy/_rayforce.so \
		-L$(EXEC_DIR)/raypy -lrayforce -L$(PYTHON_LIB) \
		-lpython$(PYTHON_VERSION) -ldl -framework CoreFoundation \
		-Wno-implicit-function-declaration && \
		echo "✅ Extension compiled" || echo "❌ Error during build";

wheel:
	@echo "⚙️  Building python wheel..."; \
	( \
		cd $(EXEC_DIR) && \
		python3 setup.py sdist bdist_wheel > /dev/null 2>&1 \
	) && echo "✅ Python wheel successfully built - tar.gz is in dist/ directory." \
	|| echo "❌ Error during wheel build"

# Builds without cleaning the pulled repository
build: build_shared_lib compile_lib wheel

# Pulls the latest repo and rebuilds all from scratch
rebuild: clean pull_from_gh build_shared_lib compile_lib wheel

lint:
	ruff format ./raypy ./tests
	ruff check ./raypy ./tests

test:
	pytest tests/
