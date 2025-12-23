#include "rayforce_c.h"

void *g_runtime = NULL; // where runtime is stored

PyTypeObject RayObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_rayforce_c.RayObject",
    .tp_basicsize = sizeof(RayObject),
    .tp_itemsize = 0,
    .tp_dealloc = NULL, // Will be set below
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "RayObject objects",
    .tp_methods = NULL, // Will be set below
    .tp_new = PyType_GenericNew,
};

static void RayObject_dealloc(RayObject *self) {
  if (self->obj != NULL && self->obj != NULL_OBJ)
    drop_obj(self->obj);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyMethodDef RayObject_methods[] = {
    {"get_obj_type", raypy_get_obj_type, METH_VARARGS, "Get object type"},
    {NULL, NULL, 0, NULL}};

PyMODINIT_FUNC PyInit__rayforce_c(void);

static struct PyModuleDef rayforce_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_rayforce_c",
    .m_doc = "Python C API bus to Rayforce",
    .m_size = -1,
    .m_methods = NULL, // Will be set in PyInit__rayforce_c
};

static PyMethodDef module_methods[] = {
    // Constructors
    {"init_i16", raypy_init_i16, METH_VARARGS, "Create a new i16 object"},
    {"init_i32", raypy_init_i32, METH_VARARGS, "Create a new i32 object"},
    {"init_i64", raypy_init_i64, METH_VARARGS, "Create a new i64 object"},
    {"init_f64", raypy_init_f64, METH_VARARGS, "Create a new f64 object"},
    {"init_c8", raypy_init_c8, METH_VARARGS,
     "Create a new c8 (character) object"},
    {"init_string", raypy_init_string, METH_VARARGS,
     "Create a new string object"},
    {"init_symbol", raypy_init_symbol, METH_VARARGS,
     "Create a new symbol object"},
    {"init_b8", raypy_init_b8, METH_VARARGS,
     "Create a new b8 (boolean) object"},
    {"init_u8", raypy_init_u8, METH_VARARGS, "Create a new u8 (byte) object"},
    {"init_date", raypy_init_date, METH_VARARGS, "Create a new date object"},
    {"init_time", raypy_init_time, METH_VARARGS, "Create a new time object"},
    {"init_timestamp", raypy_init_timestamp, METH_VARARGS,
     "Create a new timestamp object"},
    {"init_guid", raypy_init_guid, METH_VARARGS, "Create a new GUID object"},
    {"init_list", raypy_init_list, METH_VARARGS, "Create a new list object"},
    {"init_table", raypy_init_table, METH_VARARGS, "Create a new table object"},
    {"init_dict", raypy_init_dict, METH_VARARGS,
     "Create a new dictionary object"},
    {"init_vector", raypy_init_vector, METH_VARARGS,
     "Create a new vector object"},

    // Readers
    {"read_i16", raypy_read_i16, METH_VARARGS, "Read i16 value from object"},
    {"read_i32", raypy_read_i32, METH_VARARGS, "Read i32 value from object"},
    {"read_i64", raypy_read_i64, METH_VARARGS, "Read i64 value from object"},
    {"read_f64", raypy_read_f64, METH_VARARGS, "Read f64 value from object"},
    {"read_c8", raypy_read_c8, METH_VARARGS, "Read c8 value from object"},
    {"read_string", raypy_read_string, METH_VARARGS,
     "Read string value from object"},
    {"read_symbol", raypy_read_symbol, METH_VARARGS,
     "Read symbol value from object"},
    {"read_b8", raypy_read_b8, METH_VARARGS, "Read b8 value from object"},
    {"read_u8", raypy_read_u8, METH_VARARGS, "Read u8 value from object"},
    {"read_date", raypy_read_date, METH_VARARGS, "Read date value from object"},
    {"read_time", raypy_read_time, METH_VARARGS, "Read time value from object"},
    {"read_timestamp", raypy_read_timestamp, METH_VARARGS,
     "Read timestamp value from object"},
    {"read_guid", raypy_read_guid, METH_VARARGS, "Read GUID value from object"},

    // Table operations
    {"table_keys", raypy_table_keys, METH_VARARGS, "Get table keys"},
    {"table_values", raypy_table_values, METH_VARARGS, "Get table values"},
    {"repr_table", raypy_repr_table, METH_VARARGS, "Format table"},

    // Dictionary operations
    {"dict_keys", raypy_dict_keys, METH_VARARGS, "Get dictionary keys"},
    {"dict_values", raypy_dict_values, METH_VARARGS, "Get dictionary values"},
    {"dict_get", raypy_dict_get, METH_VARARGS, "Get value from dictionary"},

    // Vector operations
    {"at_idx", raypy_at_idx, METH_VARARGS, "Get element at index"},
    {"insert_obj", raypy_insert_obj, METH_VARARGS, "Insert object at index"},
    {"push_obj", raypy_push_obj, METH_VARARGS,
     "Push object to the end of iterable"},
    {"set_obj", raypy_set_obj, METH_VARARGS, "Set object at index"},
    {"fill_vector", raypy_fill_vector, METH_VARARGS,
     "Fill vector from Python list (bulk operation)"},
    {"fill_list", raypy_fill_list, METH_VARARGS,
     "Fill list from Python list (bulk operation)"},

    // Misc operations
    {"get_obj_length", raypy_get_obj_length, METH_VARARGS, "Get object length"},
    {"eval_str", raypy_eval_str, METH_VARARGS, "Evaluate string expression"},
    {"get_error_message", raypy_get_error_message, METH_VARARGS,
     "Get error message"},
    {"binary_set", raypy_binary_set, METH_VARARGS,
     "Set value to symbol or file"},
    {"env_get_internal_function_by_name",
     raypy_env_get_internal_function_by_name, METH_VARARGS,
     "Get internal function by name"},
    {"env_get_internal_name_by_function",
     raypy_env_get_internal_name_by_function, METH_VARARGS,
     "Get internal function name"},
    {"eval_obj", raypy_eval_obj, METH_VARARGS, "Evaluate object"},
    {"loadfn_from_file", raypy_loadfn, METH_VARARGS,
     "Load function from shared library"},
    {"quote", raypy_quote, METH_VARARGS, "Quote (clone) object"},
    {"rc_obj", raypy_rc, METH_VARARGS, "Get reference count of object"},
    {"set_obj_attrs", raypy_set_obj_attrs, METH_VARARGS,
     "Set object attributes"},

    // Database operations
    {"select", raypy_select, METH_VARARGS, "Perform SELECT query"},
    {"update", raypy_update, METH_VARARGS, "Perform UPDATE query"},
    {"insert", raypy_insert, METH_VARARGS, "Perform INSERT query"},
    {"upsert", raypy_upsert, METH_VARARGS, "Perform UPSERT query"},

    // IO operations
    {"hopen", raypy_hopen, METH_VARARGS, "Open file or socket handle"},
    {"hclose", raypy_hclose, METH_VARARGS, "Close file or socket handle"},
    {"write", raypy_write, METH_VARARGS, "Write data to file or socket"},

    {NULL, NULL, 0, NULL}};

static RayObject *g_null_obj = NULL;

PyMODINIT_FUNC PyInit__rayforce_c(void) {
  PyObject *m;

  // Initialize RayObjectType
  RayObjectType.tp_dealloc = (destructor)RayObject_dealloc;
  RayObjectType.tp_methods = RayObject_methods;

  if (PyType_Ready(&RayObjectType) < 0)
    return NULL;

  rayforce_module.m_methods = module_methods;
  m = PyModule_Create(&rayforce_module);
  if (m == NULL)
    return NULL;

  Py_INCREF(&RayObjectType);

  // Make RayObjectType accessible from .RayObject
  if (PyModule_AddObject(m, "RayObject", (PyObject *)&RayObjectType) < 0) {
    Py_DECREF(&RayObjectType);
    Py_DECREF(m);
    return NULL;
  }

  PyModule_AddIntConstant(m, "TYPE_LIST", TYPE_LIST);
  PyModule_AddIntConstant(m, "TYPE_B8", TYPE_B8);
  PyModule_AddIntConstant(m, "TYPE_U8", TYPE_U8);
  PyModule_AddIntConstant(m, "TYPE_I16", TYPE_I16);
  PyModule_AddIntConstant(m, "TYPE_I32", TYPE_I32);
  PyModule_AddIntConstant(m, "TYPE_I64", TYPE_I64);
  PyModule_AddIntConstant(m, "TYPE_SYMBOL", TYPE_SYMBOL);
  PyModule_AddIntConstant(m, "TYPE_DATE", TYPE_DATE);
  PyModule_AddIntConstant(m, "TYPE_TIME", TYPE_TIME);
  PyModule_AddIntConstant(m, "TYPE_TIMESTAMP", TYPE_TIMESTAMP);
  PyModule_AddIntConstant(m, "TYPE_F64", TYPE_F64);
  PyModule_AddIntConstant(m, "TYPE_GUID", TYPE_GUID);
  PyModule_AddIntConstant(m, "TYPE_C8", TYPE_C8);
  PyModule_AddIntConstant(m, "TYPE_ENUM", TYPE_ENUM);
  PyModule_AddIntConstant(m, "TYPE_MAPFILTER", TYPE_MAPFILTER);
  PyModule_AddIntConstant(m, "TYPE_MAPGROUP", TYPE_MAPGROUP);
  PyModule_AddIntConstant(m, "TYPE_MAPFD", TYPE_MAPFD);
  PyModule_AddIntConstant(m, "TYPE_MAPCOMMON", TYPE_MAPCOMMON);
  PyModule_AddIntConstant(m, "TYPE_MAPLIST", TYPE_MAPLIST);
  PyModule_AddIntConstant(m, "TYPE_PARTEDLIST", TYPE_PARTEDLIST);
  PyModule_AddIntConstant(m, "TYPE_TABLE", TYPE_TABLE);
  PyModule_AddIntConstant(m, "TYPE_DICT", TYPE_DICT);
  PyModule_AddIntConstant(m, "TYPE_LAMBDA", TYPE_LAMBDA);
  PyModule_AddIntConstant(m, "TYPE_UNARY", TYPE_UNARY);
  PyModule_AddIntConstant(m, "TYPE_BINARY", TYPE_BINARY);
  PyModule_AddIntConstant(m, "TYPE_VARY", TYPE_VARY);
  PyModule_AddIntConstant(m, "TYPE_TOKEN", TYPE_TOKEN);
  PyModule_AddIntConstant(m, "TYPE_NULL", TYPE_NULL);
  PyModule_AddIntConstant(m, "TYPE_ERR", TYPE_ERR);

  g_null_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (g_null_obj == NULL) {
    Py_DECREF(m);
    return NULL;
  }

  g_null_obj->obj = NULL_OBJ;
  Py_INCREF(g_null_obj);

  if (PyModule_AddObject(m, "NULL_OBJ", (PyObject *)g_null_obj) < 0) {
    Py_DECREF(g_null_obj);
    Py_DECREF(m);
    return NULL;
  }

  char *argv[] = {"raypy", "-r", "0", NULL};
  g_runtime = runtime_create(3, argv);
  if (g_runtime == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to initialize Rayforce");
    return NULL;
  }

  return m;
}
