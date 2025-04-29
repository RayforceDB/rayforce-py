CC = clang

ifeq ($(OS),)
OS := $(shell uname -s | tr "[:upper:]" "[:lower:]")
endif

ARCH = $(shell uname -m)
PYTHON_VERSION := $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_INCLUDE := $(shell python3 -c "from sysconfig import get_paths; print(get_paths()['include'])")
PYTHON_LIB := $(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('LIBPL'))")

EXEC_DIR = $(shell pwd)

# Directory where temporary files for build are stored
TEMP_DIR = $(EXEC_DIR)/tmp
LIBRARY_DIR = $(EXEC_DIR)/raypy

ORIGINAL_RAYFORCE_DIR = $(TEMP_DIR)/rayforce-c

ifeq ($(OS),darwin)
BUILT_RAYFORCE_C_LIB = librayforce.dylib
endif

ifeq ($(OS),linux)
BUILT_RAYFORCE_C_LIB = rayforce.so
endif


.PHONY: pull_and_build_rayforce_wrapper clean rebuild lint test


pull_and_build_rayforce_wrapper:
	@rm -rf $(ORIGINAL_RAYFORCE_DIR) && \
	echo "⬇️  Cloning rayforce repo from github..."; \
	git clone git@github.com:singaraiona/rayforce.git $(ORIGINAL_RAYFORCE_DIR) && \
	echo "👷  Building rayforce shared lib..." && \
	cd $(ORIGINAL_RAYFORCE_DIR) && make shared && cd $(EXEC_DIR) && \
	cp $(ORIGINAL_RAYFORCE_DIR)/$(BUILT_RAYFORCE_C_LIB) $(LIBRARY_DIR)/$(BUILT_RAYFORCE_C_LIB) && \
	swig -python -I$(ORIGINAL_RAYFORCE_DIR)/core $(LIBRARY_DIR)/rayforce.i && \
	echo "🟡 Rayforce library ready"


clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf \
		$(LIBRARY_DIR)/_rayforce.so  \
		$(LIBRARY_DIR)/rayforce_wrap.c  \
		$(LIBRARY_DIR)/$(BUILT_RAYFORCE_C_LIB)  \
		$(LIBRARY_DIR)/rayforce.py  \
		$(TEMP_DIR)  \
		build/  \
		temp/  \
		dist/  \
		raypy.egg-info/  \


rebuild: clean pull_and_build_rayforce_wrapper
	@echo "⚙️  Compiling Python extension..."; \
	$(CC) -x c -shared -fPIC -std=c99 -arch $(ARCH) \
		-I$(PYTHON_INCLUDE) -I$(ORIGINAL_RAYFORCE_DIR)/core \
		$(LIBRARY_DIR)/rayforce_wrap.c -o $(LIBRARY_DIR)/_rayforce.so \
		-L$(LIBRARY_DIR) -lrayforce -L$(PYTHON_LIB) \
		-lpython$(PYTHON_VERSION) -ldl -framework CoreFoundation \
		-Wno-implicit-function-declaration && \
		echo "✅ Extension compiled" || echo "❌ Error during build"; \
	rm -rf $(TEMP_DIR)


importability_test:
	@cd $(LIBRARY_DIR) && \
	python3 -c "import rayforce; \
		rayforce.ray_init(); \
		assert rayforce.ray_add(rayforce.i64(2), rayforce.i64(3)).i64 == 5, 'Invalid calculation result';" && \
	echo "✅ Test passed" || echo "❌ Test failed"; \


rebuild_wheel: rebuild importability_test
	@echo "⚙️  Building python wheel..."; \
	( \
		cd $(EXEC_DIR) && \
		python3 setup.py sdist bdist_wheel > /dev/null 2>&1 \
	) && echo "✅ Python wheel successfully built - tar.gz is in dist/ directory." \
	|| echo "❌ Error during wheel build"


lint:
	ruff format ./raypy ./tests
	ruff check ./raypy ./tests

test:
	pytest tests/
