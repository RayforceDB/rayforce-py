
# Build Python module
PY_OBJECTS = core/rayforce_c.o core/raypy_init_from_py.o core/raypy_init_from_buffer.o core/raypy_read_from_rf.o core/raypy_queries.o core/raypy_io.o core/raypy_binary.o core/raypy_dynlib.o core/raypy_eval.o core/raypy_iter.o core/raypy_serde.o
PY_APP_OBJECTS = app/term.o
python: CFLAGS = $(RELEASE_CFLAGS) -I$(PYTHON_INCLUDE) -Wno-macro-redefined
python: LDFLAGS = $(PYTHON_LDFLAGS)
python: $(CORE_OBJECTS) $(PY_OBJECTS) $(PY_APP_OBJECTS)
	$(CC) -shared -o $(PYTHON_LIBNAME) $(CFLAGS) $(CORE_OBJECTS) $(PY_OBJECTS) $(PY_APP_OBJECTS) $(LIBS) $(LDFLAGS) $(PYTHON_SHARED_FLAGS)
