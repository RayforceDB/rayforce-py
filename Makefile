# get platform and arch
UNAME_S := $(shell uname -s)
ARCH = $(shell uname -m)

PYTHON_VERSION := $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_INCLUDE := $(shell python3 -c "from sysconfig import get_paths; print(get_paths()['include'])")
PYTHON_LIB := $(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('LIBPL'))")

RAYFORCE_GITHUB = git@github.com:singaraiona/rayforce.git
EXEC_DIR = $(shell pwd)

ifeq ($(UNAME_S),Darwin)
  CC = clang
  BUILT_RAYFORCE_C_LIB = librayforce.dylib
  TARGET_LIB = $(BUILT_RAYFORCE_C_LIB)
  COMPILE_FLAGS = -arch $(ARCH) -framework CoreFoundation
  LDCONFIG_CMD = 
  INSTALL_CMD = install_name_tool -id "@loader_path/$(BUILT_RAYFORCE_C_LIB)" $(EXEC_DIR)/raypy/$(BUILT_RAYFORCE_C_LIB)
  PLATFORM_NAME = macOS
else ifeq ($(UNAME_S),Linux)
  CC = gcc
  BUILT_RAYFORCE_C_LIB = rayforce.so
  TARGET_LIB = librayforce.so
  COMPILE_FLAGS = 
  LDCONFIG_CMD = ldconfig
  INSTALL_CMD = true  # does essentially nothing
  PLATFORM_NAME = Linux
else
  $(error Unsupported platform: $(UNAME_S))
endif

.PHONY: pull_from_gh build_shared_lib compile_lib wheel build rebuild clean lint test install_system_lib

pull_from_gh:
	@rm -rf $(EXEC_DIR)/tmp/rayforce-c && \
	echo "⬇️  Cloning rayforce repo from GitHub..."; \
	git clone $(RAYFORCE_GITHUB) $(EXEC_DIR)/tmp/rayforce-c \

build_shared_lib:
	@echo "👷  Building rayforce shared lib for $(PLATFORM_NAME)..." && \
	cd $(EXEC_DIR)/tmp/rayforce-c && make shared && cd $(EXEC_DIR) && \
	cp $(EXEC_DIR)/tmp/rayforce-c/$(BUILT_RAYFORCE_C_LIB) $(EXEC_DIR)/raypy/$(TARGET_LIB) && \
	swig -python -I$(EXEC_DIR)/tmp/rayforce-c/core $(EXEC_DIR)/raypy/rayforce.i && \
	$(INSTALL_CMD) && \
	echo "🟡 Rayforce library ready"

install_system_lib:
	@echo "📦 Installing shared library system-wide..."
ifeq ($(UNAME_S),Linux)
	@cp $(EXEC_DIR)/raypy/$(TARGET_LIB) /usr/local/lib/ && \
	$(LDCONFIG_CMD) && \
	echo "✅ Library installed system-wide"
else
	@echo "⚠️  System-wide installation not implemented for $(PLATFORM_NAME)"
endif

clean:
	@echo "🧹 Cleaning generated files..."
	@cd $(EXEC_DIR) && rm -rf \
		raypy/_rayforce.so  \
		raypy/rayforce_wrap.c  \
		raypy/librayforce.dylib  \
		raypy/librayforce.so  \
		raypy/rayforce.py  \
		raypy/rayforce.so  \
		tmp/  \
		build/  \
		temp/  \
		dist/  \
		raypy.egg-info/

compile_lib: 
	@echo "⚙️  Compiling Python extension for $(PLATFORM_NAME)..."; \
	$(CC) -x c -shared -fPIC -std=c99 $(COMPILE_FLAGS) \
		-I$(PYTHON_INCLUDE) -I$(EXEC_DIR)/tmp/rayforce-c/core \
		$(EXEC_DIR)/raypy/rayforce_wrap.c -o $(EXEC_DIR)/raypy/_rayforce.so \
		-L$(EXEC_DIR)/raypy -lrayforce -L$(PYTHON_LIB) \
		-lpython$(PYTHON_VERSION) -ldl \
		-Wno-implicit-function-declaration && \
		echo "✅ Extension compiled" || echo "❌ Error during build";

wheel:
	@echo "⚙️  Building python wheel..."; \
	( \
		cd $(EXEC_DIR) && \
		python3 setup.py sdist bdist_wheel > /dev/null 2>&1 \
	) && echo "✅ Python wheel successfully built - tar.gz is in dist/ directory." \
	|| echo "❌ Error during wheel build"

build: clean pull_from_gh build_shared_lib compile_lib wheel

# Full build
# For linux, LDConfig has to be updated with new shared library
install: build
ifeq ($(UNAME_S),Linux)
	@$(MAKE) install_system_lib
endif
	@echo "✅ Installation completed for $(PLATFORM_NAME)"

lint:
	ruff format ./raypy ./tests
	ruff check ./raypy ./tests

test:
	pytest tests/

test_build_for_x86_64:
	docker run -v ~/.ssh:/root/.ssh:ro -v .:/raypy --platform linux/amd64 -it ubuntu bash -c \
	"apt update && DEBIAN_FRONTEND=noninteractive apt install -y make gcc clang swig git pip python3-dev && \
	pip install setuptools --break-system-packages && cd /raypy && make install && \
	python3 -c 'import raypy; assert raypy.add(123, 123) == 246; print(\"✅ Import successful!\")'"

help:
	@echo "Raypy Makefile"
	@echo ""
	@echo "Detected platform: $(PLATFORM_NAME)"
	@echo ""
	@echo "Available targets:"
	@echo "  build       - Build without cleaning"
	@echo "  install     - Build and install
	@echo "  clean       - Remove all generated files"
	@echo "  test        - Run tests"
	@echo "  lint        - Run code linters"
	@echo "  help        - Show this help message"
