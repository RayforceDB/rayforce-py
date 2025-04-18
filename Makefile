CC = clang

PYTHON_VERSION := $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_INCLUDE := /usr/local/opt/python@$(PYTHON_VERSION)/Frameworks/Python.framework/Versions/$(PYTHON_VERSION)/include/python$(PYTHON_VERSION)
PYTHON_LIB := /usr/local/opt/python@$(PYTHON_VERSION)/Frameworks/Python.framework/Versions/$(PYTHON_VERSION)/lib/python$(PYTHON_VERSION)/config-$(PYTHON_VERSION)-darwin

.PHONY: all clean test

all: _rayforce.so

rayforce_wrap.c: rayforce.i
	swig -python -I../rayforce/core rayforce.i

_rayforce.so: rayforce_wrap.c
	$(CC) -x c -shared -fPIC -std=c99 -arch x86_64 \
		-I$(PYTHON_INCLUDE) -I../rayforce/core \
		rayforce_wrap.c -o _rayforce.so \
		-L. -lrayforce -L$(PYTHON_LIB) \
		-lpython$(PYTHON_VERSION) -ldl -framework CoreFoundation \
		-Wno-implicit-function-declaration

test: _rayforce.so
	python3 -c "import rayforce; print('Successfully imported rayforce')"

clean:
	rm -f rayforce_wrap.c rayforce.py _rayforce.so 