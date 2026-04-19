#include "rayforce_c.h"
#include <pthread.h>
#include <stdlib.h>

void *g_runtime = NULL;

// Objects dropped from non-main threads (asyncio) are queued here and processed
// later
static pthread_mutex_t g_dealloc_mutex = PTHREAD_MUTEX_INITIALIZER;
static unsigned long g_main_thread_id = 0; // main thread ID

static obj_p *g_dealloc_queue = NULL;
static size_t g_dealloc_queue_size = 0;
static size_t g_dealloc_queue_capacity = 0;

static void queue_for_dealloc(obj_p obj) {
  pthread_mutex_lock(&g_dealloc_mutex);
  if (g_dealloc_queue_size >= g_dealloc_queue_capacity) {
    size_t new_capacity =
        g_dealloc_queue_capacity == 0 ? 16 : g_dealloc_queue_capacity * 2;
    obj_p *new_queue = realloc(g_dealloc_queue, new_capacity * sizeof(obj_p));
    if (new_queue == NULL) {
      pthread_mutex_unlock(&g_dealloc_mutex);
      return;
    }
    g_dealloc_queue = new_queue;
    g_dealloc_queue_capacity = new_capacity;
  }
  g_dealloc_queue[g_dealloc_queue_size++] = obj;
  pthread_mutex_unlock(&g_dealloc_mutex);
}

static void process_deferred_dealloc(void) {
  pthread_mutex_lock(&g_dealloc_mutex);
  for (size_t i = 0; i < g_dealloc_queue_size; i++) {
    ray_release(g_dealloc_queue[i]);
  }
  g_dealloc_queue_size = 0;
  pthread_mutex_unlock(&g_dealloc_mutex);
}

int check_main_thread(void) {
  if (g_main_thread_id == 0) {
    PyErr_SetString(PyExc_RuntimeError, "runtime: not initialized");
    return 0;
  }

  if ((unsigned long)PyThread_get_thread_ident() != g_main_thread_id) {
    PyErr_SetString(PyExc_RuntimeError,
                    "runtime: cannot be called from threads other than the "
                    "initialization thread");
    return 0;
  }

  process_deferred_dealloc();
  return 1;
}

// GENERIC UTILS
PyObject *raypy_init_runtime(PyObject *self, PyObject *args) {
  (void)self;
  (void)args;

  if (g_runtime != NULL) {
    PyErr_SetString(PyExc_RuntimeError, "runtime: already initialized");
    return NULL;
  }

  char *argv[] = {"py", "-i", "0", NULL};
  /* ray_runtime_create internally calls ray_heap_init, ray_sym_init,
   * and ray_lang_init (which calls ray_env_init). */
  ray_runtime_t *rt = ray_runtime_create(3, argv);
  if (rt == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "runtime: failed to initialize Rayforce");
    return NULL;
  }
  g_runtime = (void *)rt;

  g_main_thread_id = (unsigned long)PyThread_get_thread_ident();
  Py_RETURN_NONE;
}

PyObject *raypy_wrap_ray_object(obj_p ray_obj) {
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "runtime: object cannot be null");
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;
  return (PyObject *)result;
}
// --

static void RayObject_dealloc(RayObject *self) {
  if (self->obj != NULL && self->obj != RAY_NULL_OBJ) {
    // if gc deallocates objects from background threads, we need to ensure
    // that ray_release always called from the main thread.
    if (g_main_thread_id != 0 &&
        (unsigned long)PyThread_get_thread_ident() == g_main_thread_id) {
      ray_release(self->obj);
    } else {
      queue_for_dealloc(self->obj);
    }
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}

PyTypeObject RayObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_rayforce_c.RayObject",
    .tp_basicsize = sizeof(RayObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)RayObject_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "RayObject objects",
    .tp_methods = NULL,
    .tp_new = PyType_GenericNew,
};

PyMODINIT_FUNC PyInit__rayforce_c(void);

static PyMethodDef rayforce_methods[] = {
    {"init_i16", raypy_init_i16, METH_VARARGS, "Create a new i16 object"},
    {"init_i32", raypy_init_i32, METH_VARARGS, "Create a new i32 object"},
    {"init_i64", raypy_init_i64, METH_VARARGS, "Create a new i64 object"},
    {"init_f64", raypy_init_f64, METH_VARARGS, "Create a new f64 object"},
    {"init_c8", raypy_init_c8, METH_VARARGS,
     "Create a new c8 (character) object — now a length-1 RAY_STR in v2"},
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
    {"init_vector_from_arrow_array", raypy_init_vector_from_arrow_array,
     METH_VARARGS,
     "Create a new vector object from PyArrow Array (zero-copy Arrow buffer "
     "access)"},
    {"init_vector_from_raw_buffer", raypy_init_vector_from_raw_buffer,
     METH_VARARGS, "Create a new vector from raw buffer via bulk memcpy"},
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
    {"table_keys", raypy_table_keys, METH_VARARGS, "Get table keys"},
    {"table_values", raypy_table_values, METH_VARARGS, "Get table values"},
    {"repr_table", raypy_repr_table, METH_VARARGS, "Format table"},
    {"dict_keys", raypy_dict_keys, METH_VARARGS, "Get dictionary keys"},
    {"dict_values", raypy_dict_values, METH_VARARGS, "Get dictionary values"},
    {"dict_get", raypy_dict_get, METH_VARARGS, "Get value from dictionary"},
    {"at_idx", raypy_at_idx, METH_VARARGS, "Get element at index"},
    {"insert_obj", raypy_insert_obj, METH_VARARGS, "Insert object at index"},
    {"push_obj", raypy_push_obj, METH_VARARGS,
     "Push object to the end of iterable"},
    {"set_obj", raypy_set_obj, METH_VARARGS, "Set object at index"},
    {"get_obj_length", raypy_get_obj_length, METH_VARARGS, "Get object length"},
    {"eval_str", raypy_eval_str, METH_VARARGS, "Evaluate string expression"},
    {"get_error_obj", raypy_get_error_obj, METH_VARARGS, "Get error object"},
    {"binary_set", raypy_binary_set, METH_VARARGS,
     "Set value to symbol or file"},
    {"env_get_internal_fn_by_name", raypy_env_get_internal_fn_by_name,
     METH_VARARGS, "Get internal function by name"},
    {"env_get_internal_name_by_fn", raypy_env_get_internal_name_by_fn,
     METH_VARARGS, "Get internal function name"},
    {"eval_obj", raypy_eval_obj, METH_VARARGS, "Evaluate object"},
    {"quote", raypy_quote, METH_VARARGS, "Quote (clone) object"},
    {"rc_obj", raypy_rc, METH_VARARGS, "Get reference count of object"},
    {"set_obj_attrs", raypy_set_obj_attrs, METH_VARARGS,
     "Set object attributes"},
    {"get_obj_type", raypy_get_obj_type, METH_VARARGS, "Get object type"},
    {"update", raypy_update, METH_VARARGS, "Perform UPDATE query"},
    {"insert", raypy_insert, METH_VARARGS, "Perform INSERT query"},
    {"upsert", raypy_upsert, METH_VARARGS, "Perform UPSERT query"},
    {"init_runtime", raypy_init_runtime, METH_VARARGS,
     "Initialize Rayforce runtime"},
    {"ser_obj", raypy_ser_obj, METH_VARARGS,
     "Serialize RayObject to binary format"},
    {"de_obj", raypy_de_obj, METH_VARARGS,
     "Deserialize binary format to RayObject"},
    {"read_u8_vector", raypy_read_u8_vector, METH_VARARGS,
     "Read U8 vector as bytes"},
    {"read_vector_raw", raypy_read_vector_raw, METH_VARARGS,
     "Read numeric vector as raw bytes buffer"},

    {NULL, NULL, 0, NULL}};

static struct PyModuleDef rayforce_module = {
    PyModuleDef_HEAD_INIT, .m_name = "_rayforce_c",
    .m_doc = "Python C API bus to Rayforce", .m_size = -1,
    .m_methods = rayforce_methods};

static RayObject *g_null_obj = NULL;

PyMODINIT_FUNC PyInit__rayforce_c(void) {
  PyObject *m;

  if (PyType_Ready(&RayObjectType) < 0)
    return NULL;

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

  /* Type codes — synced to rayforce2 include/rayforce.h */
  PyModule_AddIntConstant(m, "TYPE_LIST", RAY_LIST);
  PyModule_AddIntConstant(m, "TYPE_B8", RAY_BOOL);
  PyModule_AddIntConstant(m, "TYPE_U8", RAY_U8);
  PyModule_AddIntConstant(m, "TYPE_I16", RAY_I16);
  PyModule_AddIntConstant(m, "TYPE_I32", RAY_I32);
  PyModule_AddIntConstant(m, "TYPE_I64", RAY_I64);
  PyModule_AddIntConstant(m, "TYPE_F32", RAY_F32);
  PyModule_AddIntConstant(m, "TYPE_F64", RAY_F64);
  PyModule_AddIntConstant(m, "TYPE_DATE", RAY_DATE);
  PyModule_AddIntConstant(m, "TYPE_TIME", RAY_TIME);
  PyModule_AddIntConstant(m, "TYPE_TIMESTAMP", RAY_TIMESTAMP);
  PyModule_AddIntConstant(m, "TYPE_GUID", RAY_GUID);
  PyModule_AddIntConstant(m, "TYPE_SYMBOL", RAY_SYM);
  PyModule_AddIntConstant(m, "TYPE_STR", RAY_STR);
  /* Back-compat alias — TYPE_C8 code paths now hit RAY_STR under the hood */
  PyModule_AddIntConstant(m, "TYPE_C8", RAY_STR);
  PyModule_AddIntConstant(m, "TYPE_TABLE", RAY_TABLE);
  PyModule_AddIntConstant(m, "TYPE_DICT", RAY_DICT);
  PyModule_AddIntConstant(m, "TYPE_LAMBDA", RAY_LAMBDA);
  PyModule_AddIntConstant(m, "TYPE_UNARY", RAY_UNARY);
  PyModule_AddIntConstant(m, "TYPE_BINARY", RAY_BINARY);
  PyModule_AddIntConstant(m, "TYPE_VARY", RAY_VARY);
  PyModule_AddIntConstant(m, "TYPE_NULL", RAY_NULL);
  PyModule_AddIntConstant(m, "TYPE_ERR", RAY_ERROR);

  g_null_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (g_null_obj == NULL) {
    Py_DECREF(m);
    return NULL;
  }

  g_null_obj->obj = RAY_NULL_OBJ;
  Py_INCREF(g_null_obj);

  if (PyModule_AddObject(m, "NULL_OBJ", (PyObject *)g_null_obj) < 0) {
    Py_DECREF(g_null_obj);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
