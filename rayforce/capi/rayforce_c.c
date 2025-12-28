#include "rayforce_c.h"

void *g_runtime = NULL;

// Initialize runtime (FFI function)
PyObject *raypy_init_runtime(PyObject *self, PyObject *args) {
  (void)self; // Suppress unused parameter warning
  (void)args; // Suppress unused parameter warning

  if (g_runtime != NULL) {
    // Runtime already initialized
    Py_RETURN_NONE;
  }

  // Убеждаемся, что GIL захвачен перед инициализацией runtime
  // Это важно, так как runtime может использовать Python API
  char *argv[] = {"raypy", "-r", "0", NULL};
  g_runtime = runtime_create(3, argv);
  if (g_runtime == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to initialize Rayforce");
    return NULL;
  }

  Py_RETURN_NONE;
}

// Internal function to drop object in runtime thread
PyObject *raypy_drop_obj_internal(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj != NULL && ray_obj->obj != NULL_OBJ && g_runtime != NULL) {
    // Проверяем _shutting_down перед вызовом drop_obj
    int should_drop = 1;
    if (Py_IsInitialized()) {
      PyObject *ffi_module = PyImport_ImportModule("rayforce.ffi");
      if (ffi_module != NULL) {
        PyObject *shutting_down = PyObject_GetAttrString(ffi_module, "_shutting_down");
        if (shutting_down != NULL && PyObject_IsTrue(shutting_down)) {
          should_drop = 0; // Не удаляем при завершении программы
        }
        if (shutting_down != NULL) {
          Py_DECREF(shutting_down);
        }
        Py_DECREF(ffi_module);
      }
    }
    
    if (should_drop) {
      obj_p obj_to_drop = ray_obj->obj;
      ray_obj->obj = NULL_OBJ;
      drop_obj(obj_to_drop);
    } else {
      // Просто помечаем как удаленный, но не вызываем drop_obj
      ray_obj->obj = NULL_OBJ;
    }
  }
  
  Py_DECREF((PyObject *)ray_obj);
  Py_RETURN_NONE;
}


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

// Флаг для отслеживания, инициализирован ли модуль
static int module_initialized = 0;

static void RayObject_dealloc(RayObject *self) {
  if (self->obj != NULL && self->obj != NULL_OBJ) {
    obj_p obj_to_drop = self->obj;
    self->obj = NULL_OBJ;
    
    // Если Python не инициализирован или модуль еще не инициализирован,
    // удаляем объект напрямую только если runtime существует
    // Но не удаляем при завершении программы
    if (!Py_IsInitialized() || !module_initialized) {
      // При раннем завершении не вызываем drop_obj - runtime может быть уже уничтожен
      Py_TYPE(self)->tp_free((PyObject *)self);
      return;
    }
    
    // Пытаемся отправить объект в очередь на удаление в runtime потоке
    PyGILState_STATE gstate = PyGILState_Ensure();
    int scheduled = 0;
    
    PyObject *ffi_module = PyImport_ImportModule("rayforce.ffi");
    if (ffi_module != NULL) {
      // Проверяем флаг _shutting_down
      PyObject *shutting_down = PyObject_GetAttrString(ffi_module, "_shutting_down");
      if (shutting_down != NULL && PyObject_IsTrue(shutting_down)) {
        // При завершении программы не удаляем объект - runtime может быть уже уничтожен
        Py_DECREF(shutting_down);
        Py_DECREF(ffi_module);
        PyErr_Clear();
        PyGILState_Release(gstate);
        Py_TYPE(self)->tp_free((PyObject *)self);
        return;
      }
      if (shutting_down != NULL) {
        Py_DECREF(shutting_down);
      }
      
      // Пытаемся вызвать schedule_drop
      PyObject *ffi_class = PyObject_GetAttrString(ffi_module, "FFI");
      if (ffi_class != NULL) {
        PyObject *schedule_drop_func = PyObject_GetAttrString(ffi_class, "schedule_drop");
        if (schedule_drop_func != NULL && PyCallable_Check(schedule_drop_func)) {
          RayObject *obj_copy = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
          if (obj_copy != NULL) {
            obj_copy->obj = obj_to_drop;
            Py_INCREF((PyObject *)obj_copy);
            PyObject *args = PyTuple_New(1);
            if (args != NULL) {
              PyTuple_SET_ITEM(args, 0, (PyObject *)obj_copy);
              PyObject *result = PyObject_CallObject(schedule_drop_func, args);
              if (result != NULL) {
                Py_DECREF(result);
                scheduled = 1;
                Py_DECREF(args);
              } else {
                // Если schedule_drop вернул NULL, удаляем объект напрямую
                PyObject *obj_from_tuple = PyTuple_GET_ITEM(args, 0);
                Py_INCREF(obj_from_tuple);
                Py_DECREF(args);
                RayObject *obj_to_drop_direct = (RayObject *)obj_from_tuple;
                if (obj_to_drop_direct->obj != NULL && obj_to_drop_direct->obj != NULL_OBJ) {
                  // Проверяем _shutting_down перед прямым вызовом drop_obj
                  int should_drop = 1;
                  PyObject *ffi_module_check = PyImport_ImportModule("rayforce.ffi");
                  if (ffi_module_check != NULL) {
                    PyObject *shutting_down_check = PyObject_GetAttrString(ffi_module_check, "_shutting_down");
                    if (shutting_down_check != NULL && PyObject_IsTrue(shutting_down_check)) {
                      should_drop = 0; // Не удаляем при завершении программы
                    }
                    if (shutting_down_check != NULL) {
                      Py_DECREF(shutting_down_check);
                    }
                    Py_DECREF(ffi_module_check);
                  }
                  
                  if (should_drop && g_runtime != NULL) {
                    obj_p obj_to_drop_now = obj_to_drop_direct->obj;
                    obj_to_drop_direct->obj = NULL_OBJ;
                    drop_obj(obj_to_drop_now);
                  } else {
                    // Просто помечаем как удаленный
                    obj_to_drop_direct->obj = NULL_OBJ;
                  }
                }
                Py_DECREF(obj_from_tuple);
              }
            } else {
              Py_DECREF(obj_copy);
            }
          }
          Py_DECREF(schedule_drop_func);
        }
        Py_DECREF(ffi_class);
      }
      Py_DECREF(ffi_module);
    }
    
    PyErr_Clear();
    PyGILState_Release(gstate);
    
    // Если не удалось запланировать удаление, не вызываем drop_obj напрямую
    // так как это может произойти при завершении программы, когда runtime уже уничтожен
    // Объекты будут удалены при уничтожении runtime
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}

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
    {"get_error_obj", raypy_get_error_obj, METH_VARARGS, "Get error object"},
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
    {"get_obj_type", raypy_get_obj_type, METH_VARARGS, "Get object type"},

    // Database operations
    {"select", raypy_select, METH_VARARGS, "Perform SELECT query"},
    {"update", raypy_update, METH_VARARGS, "Perform UPDATE query"},
    {"insert", raypy_insert, METH_VARARGS, "Perform INSERT query"},
    {"upsert", raypy_upsert, METH_VARARGS, "Perform UPSERT query"},

    // IO operations
    {"hopen", raypy_hopen, METH_VARARGS, "Open file or socket handle"},
    {"hclose", raypy_hclose, METH_VARARGS, "Close file or socket handle"},
    {"write", raypy_write, METH_VARARGS, "Write data to file or socket"},

    {"init_runtime", raypy_init_runtime, METH_VARARGS,
     "Initialize Rayforce runtime"},
    {"get_obj_type", raypy_get_obj_type, METH_VARARGS,
     "Get object type code"},

    {NULL, NULL, 0, NULL}};

static RayObject *g_null_obj = NULL;

PyMODINIT_FUNC PyInit__rayforce_c(void) {
  PyObject *m;

  // Initialize RayObjectType
  RayObjectType.tp_dealloc = (destructor)RayObject_dealloc;

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

  // Устанавливаем флаг инициализации модуля в конце, после успешной инициализации
  // Это позволяет RayObject_dealloc безопасно использовать Python API
  module_initialized = 1;

  return m;
}
