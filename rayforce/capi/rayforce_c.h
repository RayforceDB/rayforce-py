#ifndef RAYFORCE_C_H
#define RAYFORCE_C_H

#define PY_SSIZE_T_CLEAN
#include "binary.h"
#include "chrono.h"
#include "cmp.h"
#include "compose.h"
#include "cond.h"
#include "date.h"
#include "dynlib.h"
#include "env.h"
#include "error.h"
#include "eval.h"
#include "format.h"
#include "guid.h"
#include "io.h"
#include "items.h"
#include "iter.h"
#include "join.h"
#include "logic.h"
#include "math.h"
#include "misc.h"
#include "ops.h"
#include "order.h"
#include "os.h"
#include "proc.h"
#include "query.h"
#include "rayforce.h"
#include "runtime.h"
#include "serde.h"
#include "string.h"
#include "time.h"
#include "timestamp.h"
#include "unary.h"
#include "update.h"
#include "util.h"
#include "vary.h"
#include <Python.h>
#include <string.h>
#include <unistd.h>

#ifndef memcpy
extern void *memcpy(void *dest, const void *src, size_t n);
#endif

// Forward declarations
extern PyTypeObject RayObjectType;

typedef struct {
  PyObject_HEAD obj_p obj;
} RayObject;

// Runtime
extern void *g_runtime;

// Conversion functions (Python -> Rayforce)
obj_p raypy_init_i16_from_py(PyObject *item);
obj_p raypy_init_i32_from_py(PyObject *item);
obj_p raypy_init_i64_from_py(PyObject *item);
obj_p raypy_init_f64_from_py(PyObject *item);
obj_p raypy_init_c8_from_py(PyObject *item);
obj_p raypy_init_b8_from_py(PyObject *item);
obj_p raypy_init_u8_from_py(PyObject *item);
obj_p raypy_init_symbol_from_py(PyObject *item);
obj_p raypy_init_guid_from_py(PyObject *item);
obj_p raypy_init_date_from_py(PyObject *item);
obj_p raypy_init_time_from_py(PyObject *item);
obj_p raypy_init_timestamp_from_py(PyObject *item);
obj_p raypy_init_dict_from_py(PyObject *item);
obj_p raypy_init_list_from_py(PyObject *item);

// Constructors
PyObject *raypy_init_i16(PyObject *self, PyObject *args);
PyObject *raypy_init_i32(PyObject *self, PyObject *args);
PyObject *raypy_init_i64(PyObject *self, PyObject *args);
PyObject *raypy_init_f64(PyObject *self, PyObject *args);
PyObject *raypy_init_c8(PyObject *self, PyObject *args);
PyObject *raypy_init_string(PyObject *self, PyObject *args);
PyObject *raypy_init_symbol(PyObject *self, PyObject *args);
PyObject *raypy_init_b8(PyObject *self, PyObject *args);
PyObject *raypy_init_u8(PyObject *self, PyObject *args);
PyObject *raypy_init_date(PyObject *self, PyObject *args);
PyObject *raypy_init_time(PyObject *self, PyObject *args);
PyObject *raypy_init_timestamp(PyObject *self, PyObject *args);
PyObject *raypy_init_guid(PyObject *self, PyObject *args);
PyObject *raypy_init_list(PyObject *self, PyObject *args);
PyObject *raypy_init_table(PyObject *self, PyObject *args);
PyObject *raypy_init_dict(PyObject *self, PyObject *args);
PyObject *raypy_init_vector(PyObject *self, PyObject *args);

// Readers
PyObject *raypy_read_i16(PyObject *self, PyObject *args);
PyObject *raypy_read_i32(PyObject *self, PyObject *args);
PyObject *raypy_read_i64(PyObject *self, PyObject *args);
PyObject *raypy_read_f64(PyObject *self, PyObject *args);
PyObject *raypy_read_c8(PyObject *self, PyObject *args);
PyObject *raypy_read_string(PyObject *self, PyObject *args);
PyObject *raypy_read_symbol(PyObject *self, PyObject *args);
PyObject *raypy_read_b8(PyObject *self, PyObject *args);
PyObject *raypy_read_u8(PyObject *self, PyObject *args);
PyObject *raypy_read_date(PyObject *self, PyObject *args);
PyObject *raypy_read_time(PyObject *self, PyObject *args);
PyObject *raypy_read_timestamp(PyObject *self, PyObject *args);
PyObject *raypy_read_guid(PyObject *self, PyObject *args);

// Type introspection
PyObject *raypy_get_obj_type(PyObject *self, PyObject *args);

// Table operations
PyObject *raypy_table_keys(PyObject *self, PyObject *args);
PyObject *raypy_table_values(PyObject *self, PyObject *args);
PyObject *raypy_repr_table(PyObject *self, PyObject *args);

// Dictionary operations
PyObject *raypy_dict_keys(PyObject *self, PyObject *args);
PyObject *raypy_dict_values(PyObject *self, PyObject *args);
PyObject *raypy_dict_get(PyObject *self, PyObject *args);

// Vector operations
PyObject *raypy_at_idx(PyObject *self, PyObject *args);
PyObject *raypy_insert_obj(PyObject *self, PyObject *args);
PyObject *raypy_push_obj(PyObject *self, PyObject *args);
PyObject *raypy_set_obj(PyObject *self, PyObject *args);
PyObject *raypy_fill_vector(PyObject *self, PyObject *args);
PyObject *raypy_fill_list(PyObject *self, PyObject *args);

// Misc operations
PyObject *raypy_get_obj_length(PyObject *self, PyObject *args);
PyObject *raypy_eval_str(PyObject *self, PyObject *args);
PyObject *raypy_get_error_obj(PyObject *self, PyObject *args);
PyObject *raypy_binary_set(PyObject *self, PyObject *args);
PyObject *raypy_env_get_internal_function_by_name(PyObject *self,
                                                  PyObject *args);
PyObject *raypy_env_get_internal_name_by_function(PyObject *self,
                                                  PyObject *args);
PyObject *raypy_eval_obj(PyObject *self, PyObject *args);
PyObject *raypy_loadfn(PyObject *self, PyObject *args);
PyObject *raypy_quote(PyObject *self, PyObject *args);
PyObject *raypy_rc(PyObject *self, PyObject *args);
PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args);

// Database operations
PyObject *raypy_select(PyObject *self, PyObject *args);
PyObject *raypy_update(PyObject *self, PyObject *args);
PyObject *raypy_insert(PyObject *self, PyObject *args);
PyObject *raypy_upsert(PyObject *self, PyObject *args);

// IO operations
PyObject *raypy_hopen(PyObject *self, PyObject *args);
PyObject *raypy_hclose(PyObject *self, PyObject *args);
PyObject *raypy_write(PyObject *self, PyObject *args);

#endif // RAYFORCE_C_H
