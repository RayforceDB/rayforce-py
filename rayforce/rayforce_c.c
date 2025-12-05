#define PY_SSIZE_T_CLEAN
#include <string.h>
#include <Python.h>
#include "rayforce.h"
#include "error.h"
#include "eval.h"
#include "binary.h"
#include "cmp.h"
#include "compose.h"
#include "cond.h"
#include "dynlib.h"
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
#include "query.h"
#include "runtime.h"
#include "serde.h"
#include "string.h"
#include "chrono.h"
#include "date.h"
#include "time.h"
#include "timestamp.h"
#include "unary.h"
#include "update.h"
#include "util.h"
#include "vary.h"
#include "os.h"
#include "proc.h"
#include "env.h"
#include <unistd.h>

static void *g_runtime = NULL;  // where runtime is stored

#ifndef memcpy
    extern void *memcpy(void *dest, const void *src, size_t n);
#endif

static PyTypeObject RayObjectType;

typedef struct
{
    PyObject_HEAD obj_p obj;
} RayObject;

static void RayObject_dealloc(RayObject *self)
{
    if (self->obj != NULL)
        drop_obj(self->obj);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

// CONSTRUCTORS
// ---------------------------------------------------------------------------
static PyObject *raypy_init_i16(PyObject *self, PyObject *args)
{
    (void)self;
    short value;
    if (!PyArg_ParseTuple(args, "h", &value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    if (result != NULL)
        result->obj = i16(value);

    return (PyObject *)result;
}
static PyObject *raypy_init_i32(PyObject *self, PyObject *args)
{
    (void)self;
    int value;

    if (!PyArg_ParseTuple(args, "i", &value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    if (result != NULL)
        result->obj = i32(value);

    return (PyObject *)result;
}
static PyObject *raypy_init_i64(PyObject *self, PyObject *args)
{
    (void)self;
    long long value;

    if (!PyArg_ParseTuple(args, "L", &value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = i64(value);

    return (PyObject *)result;
}
static PyObject *raypy_init_f64(PyObject *self, PyObject *args)
{
    (void)self;
    double value;

    if (!PyArg_ParseTuple(args, "d", &value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = f64(value);

    return (PyObject *)result;
}
static PyObject *raypy_init_c8(PyObject *self, PyObject *args)
{
    (void)self;
    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
        return NULL;

    if (len != 1)
    {
        PyErr_SetString(PyExc_ValueError, "Character must be a single character");
        return NULL;
    }

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = c8(value[0]);

    return (PyObject *)result;
}
static PyObject *raypy_init_string(PyObject *self, PyObject *args)
{
    (void)self;
    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = string_from_str(value, len);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create string");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_init_symbol(PyObject *self, PyObject *args)
{
    (void)self;
    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = symbol(value, len);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create symbol");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_init_b8(PyObject *self, PyObject *args)
{
    (void)self;
    int bool_value;

    if (!PyArg_ParseTuple(args, "p", &bool_value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = b8(bool_value ? 1 : 0);

    return (PyObject *)result;
}
static PyObject *raypy_init_u8(PyObject *self, PyObject *args)
{
    (void)self;
    unsigned char byte_value;

    if (!PyArg_ParseTuple(args, "b", &byte_value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = u8(byte_value);

    return (PyObject *)result;
}
static PyObject *raypy_init_date(PyObject *self, PyObject *args)
{
    (void)self;
    int days_value;

    if (!PyArg_ParseTuple(args, "i", &days_value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = adate(days_value);

    return (PyObject *)result;
}
static PyObject *raypy_init_time(PyObject *self, PyObject *args)
{
    (void)self;
    int ms_value;

    if (!PyArg_ParseTuple(args, "i", &ms_value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = atime(ms_value);

    return (PyObject *)result;
}
static PyObject *raypy_init_timestamp(PyObject *self, PyObject *args)
{
    (void)self;
    long long ms_value;

    if (!PyArg_ParseTuple(args, "L", &ms_value))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = timestamp(ms_value);

    return (PyObject *)result;
}
static PyObject *raypy_init_guid(PyObject *self, PyObject *args)
{
    (void)self;
    const char *guid_str;
    Py_ssize_t str_len;

    if (!PyArg_ParseTuple(args, "s#", &guid_str, &str_len))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = vector(TYPE_I64, 2);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create GUID");
            return NULL;
        }
        result->obj->type = -TYPE_GUID;

        if (guid_from_str(guid_str, str_len, *AS_GUID(result->obj)) != 0)
        {
            drop_obj(result->obj);
            Py_DECREF(result);
            PyErr_SetString(PyExc_ValueError, "Invalid GUID format");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_init_list(PyObject *self, PyObject *args)
{
    (void)self;
    Py_ssize_t initial_size = 0;

    if (!PyArg_ParseTuple(args, "|n", &initial_size))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = vector(TYPE_LIST, (u64_t)initial_size);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create list");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_init_table(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *keys_obj;
    RayObject *vals_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType, &vals_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = ray_table(keys_obj->obj, vals_obj->obj);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create table");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_init_dict(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *keys_obj;
    RayObject *vals_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType, &vals_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = ray_dict(keys_obj->obj, vals_obj->obj);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create dictionary");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_init_vector(PyObject *self, PyObject *args)
{
    (void)self;
    int type_code;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "in", &type_code, &length))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = vector(type_code, (u64_t)length);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create vector");
            return NULL;
        }
    }

    return (PyObject *)result;
}

// END CONSTRUCTORS
// ---------------------------------------------------------------------------

// READERS
// ---------------------------------------------------------------------------
static PyObject *raypy_read_i16(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_I16)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an i16");
        return NULL;
    }

    return PyLong_FromLong(ray_obj->obj->i16);
}
static PyObject *raypy_read_i32(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_I32)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an i32");
        return NULL;
    }

    return PyLong_FromLong(ray_obj->obj->i32);
}
static PyObject *raypy_read_i64(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_I64)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an i64");
        return NULL;
    }

    return PyLong_FromLongLong(ray_obj->obj->i64);
}
static PyObject *raypy_read_f64(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an f64");
        return NULL;
    }

    return PyFloat_FromDouble(ray_obj->obj->f64);
}
static PyObject *raypy_read_c8(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a c8");
        return NULL;
    }

    return PyUnicode_FromStringAndSize(&ray_obj->obj->c8, 1);
}
static PyObject *raypy_read_string(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a string");
        return NULL;
    }

    return PyUnicode_FromStringAndSize(AS_C8(ray_obj->obj), ray_obj->obj->len);
}
static PyObject *raypy_read_symbol(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_SYMBOL)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a symbol");
        return NULL;
    }

    const char *str = str_from_symbol(ray_obj->obj->i64);
    if (str == NULL)
        Py_RETURN_NONE;

    return PyUnicode_FromString(str);
}
static PyObject *raypy_read_b8(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_B8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a B8 type");
        return NULL;
    }

    return PyBool_FromLong(ray_obj->obj->b8);
}
static PyObject *raypy_read_u8(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_U8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a U8 type");
        return NULL;
    }

    return PyLong_FromLong((long)ray_obj->obj->u8);
}
static PyObject *raypy_read_date(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_DATE)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DATE type");
        return NULL;
    }

    return PyLong_FromLong(ray_obj->obj->i32);
}
static PyObject *raypy_read_time(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_TIME)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TIME type");
        return NULL;
    }

    return PyLong_FromLong(ray_obj->obj->i32);
}
static PyObject *raypy_read_timestamp(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_TIMESTAMP)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TIMESTAMP type");
        return NULL;
    }

    return PyLong_FromLongLong(ray_obj->obj->i64);
}
static PyObject *raypy_read_guid(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_GUID)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a GUID type");
        return NULL;
    }

    return PyBytes_FromStringAndSize((const char *)AS_U8(ray_obj->obj), 16);
}
// END READERS
// ---------------------------------------------------------------------------

// TYPE INTROSPECTION
// ---------------------------------------------------------------------------
static PyObject *raypy_get_obj_type(PyObject *self, PyObject *args)
{
    (void)args;
    RayObject *ray_obj = (RayObject *)self;

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    return PyLong_FromLong(ray_obj->obj->type);
}
static PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    long value;

    if (!PyArg_ParseTuple(args, "O!l", &RayObjectType, &ray_obj, &value))
        return NULL;

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    ray_obj->obj->attrs = (char)value;
    return PyLong_FromLong(ray_obj->obj->attrs);
}
// END TYPE INTROSPECTION
// ---------------------------------------------------------------------------

// TABLE OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_table_keys(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    obj_p keys_list = AS_LIST(ray_obj->obj)[0];
    if (keys_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Table has no keys list");
        return NULL;
    }

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = clone_obj(keys_list);

    return (PyObject *)result;
}
static PyObject *raypy_table_values(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    obj_p values_list = AS_LIST(ray_obj->obj)[1];
    if (values_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Table has no values list");
        return NULL;
    }

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = clone_obj(values_list);

    return (PyObject *)result;
}
// END TABLE OPERATIONS
// ---------------------------------------------------------------------------

// DICT OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_dict_keys(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    obj_p keys = ray_key(ray_obj->obj);
    if (keys == NULL)
        Py_RETURN_NONE;

    result->obj = clone_obj(keys);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_dict_values(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    obj_p keys = ray_value(ray_obj->obj);
    if (keys == NULL)
        Py_RETURN_NONE;

    result->obj = clone_obj(keys);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_dict_get(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    RayObject *key_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj, &RayObjectType, &key_obj))
        return NULL;

    obj_p result = at_obj(ray_obj->obj, key_obj->obj);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_KeyError, "Key not found in dictionary");
        return NULL;
    }

    RayObject *ray_result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (ray_result != NULL)
    {
        ray_result->obj = clone_obj(result);
        if (ray_result->obj == NULL)
        {
            Py_DECREF(ray_result);
            PyErr_SetString(PyExc_MemoryError, "Failed to clone dictionary value");
            return NULL;
        }
    }

    return (PyObject *)ray_result;
}
// END DICT OPERATIONS
// ---------------------------------------------------------------------------

// VECTOR OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_at_idx(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    Py_ssize_t index;

    if (!PyArg_ParseTuple(args, "O!n", &RayObjectType, &ray_obj, &index))
        return NULL;

    obj_p item = at_idx(ray_obj->obj, (i64_t)index);
    if (item == NULL)
        Py_RETURN_NONE;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    result->obj = clone_obj(item);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_insert_obj(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    Py_ssize_t index;
    RayObject *item;

    if (!PyArg_ParseTuple(args, "O!nO!", &RayObjectType, &ray_obj, &index, &RayObjectType, &item))
        return NULL;

    obj_p clone = clone_obj(item->obj);
    if (clone == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    ins_obj(&ray_obj->obj, (i64_t)index, clone);
    Py_RETURN_NONE;
}
static PyObject *raypy_push_obj(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    RayObject *item;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj, &RayObjectType, &item))
        return NULL;

    obj_p clone = clone_obj(item->obj);
    if (clone == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    push_obj(&ray_obj->obj, clone);
    Py_RETURN_NONE;
}
static PyObject *raypy_set_obj(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    RayObject *idx_obj;
    RayObject *val_obj;

    if (!PyArg_ParseTuple(args, "O!O!O!", &RayObjectType, &ray_obj, &RayObjectType, &idx_obj, &RayObjectType, &val_obj))
        return NULL;

    obj_p clone = clone_obj(val_obj->obj);
    obj_p old_obj = ray_obj->obj;
    obj_p result_obj = set_obj(&ray_obj->obj, idx_obj->obj, clone);
    
    if (result_obj == NULL || result_obj->type == TYPE_ERR)
    {
        drop_obj(clone);
        PyErr_SetString(PyExc_RuntimeError, "Failed to set object");
        return NULL;
    }

    if (result_obj != old_obj)
    {
        drop_obj(old_obj);
        ray_obj->obj = result_obj;
    }

    Py_INCREF((PyObject *)ray_obj);
    return (PyObject *)ray_obj;
}
// END VECTOR OPERATIONS
// ---------------------------------------------------------------------------

// MISC
// ---------------------------------------------------------------------------
static PyObject *raypy_get_obj_length(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    return PyLong_FromUnsignedLongLong(ray_obj->obj->len);
}
static PyObject *raypy_repr_table(PyObject *self, PyObject *args)
{
	(void)self;
	RayObject *ray_obj;
	int full = 1;

	if (!PyArg_ParseTuple(args, "O!|p", &RayObjectType, &ray_obj, &full))
		return NULL;

	obj_p item = obj_fmt(ray_obj->obj, (b8_t)full);
	if (item == NULL)
	{
		PyErr_SetString(PyExc_RuntimeError, "Failed to format object");
		return NULL;
	}

	PyObject *result = PyUnicode_FromStringAndSize(AS_C8(item), item->len);
	drop_obj(item);
	return result;
}
static PyObject *raypy_eval_str(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    result->obj = ray_eval_str(ray_obj->obj, NULL_OBJ);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate expression");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_get_error_message(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    ray_error_p err = AS_ERROR(ray_obj->obj);

    if (err != NULL && err->msg != NULL && err->msg->type == TYPE_C8)
    {
        const char *error_text = AS_C8(err->msg);
        u64_t length = err->msg->len;

        PyObject *error_message = PyUnicode_DecodeLatin1(error_text, length, "replace");

        if (err->locs != NULL && err->locs->type == TYPE_LIST && err->locs->len > 0)
        {
            PyObject *with_code = PyUnicode_FromFormat(
                "%s (error code: %lld)",
                PyUnicode_AsUTF8(error_message),
                (long long)err->code
            );
            Py_DECREF(error_message);
            return with_code;
        }

        return error_message;
    }

    if (err != NULL)
        return PyUnicode_FromFormat("Error code: %lld", (long long)err->code);
    else
        return PyUnicode_FromString("Unknown error");
}
static PyObject *raypy_binary_set(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *symbol_or_path;
    RayObject *value;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &symbol_or_path, &RayObjectType, &value))
        return NULL;

    if (symbol_or_path->obj == NULL || value->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Neither symbol/path nor value can be NULL");
        return NULL;
    }

    if (symbol_or_path->obj->type != -TYPE_SYMBOL && symbol_or_path->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "First argument must be a symbol or string");
        return NULL;
    }

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = binary_set(symbol_or_path->obj, value->obj);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to execute set operation");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_env_get_internal_function_by_name(PyObject *self, PyObject *args)
{
    (void)self;
    const char *name;
    Py_ssize_t name_len;

    if (!PyArg_ParseTuple(args, "s#", &name, &name_len))
        return NULL;

    obj_p func_obj = env_get_internal_function(name);

    if (func_obj == NULL_OBJ || func_obj == NULL)
        Py_RETURN_NONE;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
        result->obj = func_obj;

    return (PyObject *)result;
}
static PyObject *raypy_env_get_internal_name_by_function(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    str_p name = env_get_internal_name(ray_obj->obj);
    if (name == NULL)
        Py_RETURN_NONE;

    return PyUnicode_FromString(name);
}
static PyObject *raypy_eval_obj(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    result->obj = eval_obj(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate object");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_quote(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj)) 
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    result->obj = ray_quote(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to quote object");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_rc(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
        return NULL;

    return PyLong_FromUnsignedLong(rc_obj(ray_obj->obj));
}
static PyObject *raypy_loadfn(PyObject *self, PyObject *args)
{
    (void)self;
    const char *path;
    const char *func_name;
    int nargs;
    Py_ssize_t path_len, func_len;

    if (!PyArg_ParseTuple(args, "s#s#i", &path, &path_len, &func_name, &func_len, &nargs))
        return NULL;

    RayObject *path_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    path_obj->obj = vector(TYPE_C8, path_len);

    memcpy(AS_C8(path_obj->obj), path, path_len);

    RayObject *func_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    func_obj->obj = vector(TYPE_C8, func_len);

    memcpy(AS_C8(func_obj->obj), func_name, func_len);

    RayObject *nargs_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    nargs_obj->obj = i64((long long)nargs);

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    obj_p args_array[3];
    args_array[0] = path_obj->obj;
    args_array[1] = func_obj->obj;
    args_array[2] = nargs_obj->obj;

    result->obj = ray_loadfn(args_array, 3);

    // Clean up temporary objects
    Py_DECREF(path_obj);
    Py_DECREF(func_obj);
    Py_DECREF(nargs_obj);

    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to load function from shared library");
        return NULL;
    }

    return (PyObject *)result;
}
// END MISC
// ---------------------------------------------------------------------------

// DATABASE OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_select(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *query_dict;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &query_dict))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    result->obj = EVAL_WITH_CTX(ray_select(query_dict->obj), NULL_OBJ);

    return (PyObject *)result;
}
static PyObject *raypy_update(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *update_dict;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &update_dict)) 
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    result->obj = EVAL_WITH_CTX(ray_update(update_dict->obj), NULL_OBJ);

    return (PyObject *)result;
}

static PyObject *raypy_insert(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *table_obj;
    RayObject *data_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &table_obj, &RayObjectType, &data_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    obj_p ray_args[2] = {table_obj->obj, data_obj->obj};
    result->obj = EVAL_WITH_CTX(ray_insert(ray_args, 2), NULL_OBJ);

    return (PyObject *)result;
}

static PyObject *raypy_upsert(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *table_obj;
    RayObject *keys_obj;
    RayObject *data_obj;

    if (!PyArg_ParseTuple(args, "O!O!O!", &RayObjectType, &table_obj, &RayObjectType, &keys_obj, &RayObjectType, &data_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    obj_p ray_args[3] = {table_obj->obj, keys_obj->obj, data_obj->obj};
    result->obj = EVAL_WITH_CTX(ray_upsert(ray_args, 3), NULL_OBJ);

    return (PyObject *)result;
}
// END DATABASE OPERATIONS
// ---------------------------------------------------------------------------

// IO OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_hopen(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *path_obj;
    RayObject *timeout_obj = NULL;

    if (!PyArg_ParseTuple(args, "O!|O!", &RayObjectType, &path_obj, &RayObjectType, &timeout_obj))
        return NULL;

    obj_p ray_args[2];
    i64_t arg_count = 1;    
    ray_args[0] = path_obj->obj;
    
    if (timeout_obj != NULL)
    {
        ray_args[1] = timeout_obj->obj;
        arg_count = 2;
    }

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    result->obj = ray_hopen(ray_args, arg_count);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to open handle");
        return NULL;
    }

    return (PyObject *)result;
}

static PyObject *raypy_hclose(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *handle_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &handle_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    result->obj = ray_hclose(handle_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to close handle");
        return NULL;
    }

    return (PyObject *)result;
}

static PyObject *raypy_write(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *handle_obj;
    RayObject *data_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &handle_obj, &RayObjectType, &data_obj))
        return NULL;

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    result->obj = ray_write(handle_obj->obj, data_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to write data");
        return NULL;
    }

    return (PyObject *)result;
}
// END IO OPERATIONS
// ---------------------------------------------------------------------------

static PyMethodDef RayObject_methods[] = {
    {"get_obj_type", raypy_get_obj_type, METH_VARARGS, "Get object type"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject RayObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_rayforce_c.RayObject",
    .tp_basicsize = sizeof(RayObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)RayObject_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "RayObject objects",
    .tp_methods = RayObject_methods,
    .tp_new = PyType_GenericNew,
};

static PyMethodDef module_methods[] = {
    // Constructors
    {"init_i16", raypy_init_i16, METH_VARARGS, "Create a new i16 object"},
    {"init_i32", raypy_init_i32, METH_VARARGS, "Create a new i32 object"},
    {"init_i64", raypy_init_i64, METH_VARARGS, "Create a new i64 object"},
    {"init_f64", raypy_init_f64, METH_VARARGS, "Create a new f64 object"},
    {"init_c8", raypy_init_c8, METH_VARARGS, "Create a new c8 (character) object"},
    {"init_string", raypy_init_string, METH_VARARGS, "Create a new string object"},
    {"init_symbol", raypy_init_symbol, METH_VARARGS, "Create a new symbol object"},
    {"init_b8", raypy_init_b8, METH_VARARGS, "Create a new b8 (boolean) object"},
    {"init_u8", raypy_init_u8, METH_VARARGS, "Create a new u8 (byte) object"},
    {"init_date", raypy_init_date, METH_VARARGS, "Create a new date object"},
    {"init_time", raypy_init_time, METH_VARARGS, "Create a new time object"},
    {"init_timestamp", raypy_init_timestamp, METH_VARARGS, "Create a new timestamp object"},
    {"init_guid", raypy_init_guid, METH_VARARGS, "Create a new GUID object"},
    {"init_list", raypy_init_list, METH_VARARGS, "Create a new list object"},
    {"init_table", raypy_init_table, METH_VARARGS, "Create a new table object"},
    {"init_dict", raypy_init_dict, METH_VARARGS, "Create a new dictionary object"},
    {"init_vector", raypy_init_vector, METH_VARARGS, "Create a new vector object"},

    // Readers
    {"read_i16", raypy_read_i16, METH_VARARGS, "Read i16 value from object"},
    {"read_i32", raypy_read_i32, METH_VARARGS, "Read i32 value from object"},
    {"read_i64", raypy_read_i64, METH_VARARGS, "Read i64 value from object"},
    {"read_f64", raypy_read_f64, METH_VARARGS, "Read f64 value from object"},
    {"read_c8", raypy_read_c8, METH_VARARGS, "Read c8 value from object"},
    {"read_string", raypy_read_string, METH_VARARGS, "Read string value from object"},
    {"read_symbol", raypy_read_symbol, METH_VARARGS, "Read symbol value from object"},
    {"read_b8", raypy_read_b8, METH_VARARGS, "Read b8 value from object"},
    {"read_u8", raypy_read_u8, METH_VARARGS, "Read u8 value from object"},
    {"read_date", raypy_read_date, METH_VARARGS, "Read date value from object"},
    {"read_time", raypy_read_time, METH_VARARGS, "Read time value from object"},
    {"read_timestamp", raypy_read_timestamp, METH_VARARGS, "Read timestamp value from object"},
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
    {"push_obj", raypy_push_obj, METH_VARARGS, "Push object to the end of iterable"},
    {"set_obj", raypy_set_obj, METH_VARARGS, "Set object at index"},

    // Misc operations
    {"get_obj_length", raypy_get_obj_length, METH_VARARGS, "Get object length"},
    {"eval_str", raypy_eval_str, METH_VARARGS, "Evaluate string expression"},
    {"get_error_message", raypy_get_error_message, METH_VARARGS, "Get error message"},
    {"binary_set", raypy_binary_set, METH_VARARGS, "Set value to symbol or file"},
    {"env_get_internal_function_by_name", raypy_env_get_internal_function_by_name, METH_VARARGS, "Get internal function by name"},
    {"env_get_internal_name_by_function", raypy_env_get_internal_name_by_function, METH_VARARGS, "Get internal function name"},
    {"eval_obj", raypy_eval_obj, METH_VARARGS, "Evaluate object"},
    {"eval_obj", raypy_eval_obj, METH_VARARGS, "Evaluate a RayObject"},
    {"loadfn_from_file", raypy_loadfn, METH_VARARGS, "Load function from shared library"},
    {"quote", raypy_quote, METH_VARARGS, "Quote (clone) object"},
    {"rc_obj", raypy_rc, METH_VARARGS, "Get reference count of object"},
    {"set_obj_attrs", raypy_set_obj_attrs, METH_VARARGS, "Set object attributes"},

    // Database operations
    {"select", raypy_select, METH_VARARGS, "Perform SELECT query"},
    {"update", raypy_update, METH_VARARGS, "Perform UPDATE query"},
    {"insert", raypy_insert, METH_VARARGS, "Perform INSERT query"},
    {"upsert", raypy_upsert, METH_VARARGS, "Perform UPSERT query"},

    // IO operations
    {"hopen", raypy_hopen, METH_VARARGS, "Open file or socket handle"},
    {"hclose", raypy_hclose, METH_VARARGS, "Close file or socket handle"},
    {"write", raypy_write, METH_VARARGS, "Write data to file or socket"},
    
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef rayforce_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_rayforce_c",
    .m_doc = "Python C API bus to Rayforce",
    .m_size = -1,
    .m_methods = module_methods,
};

PyMODINIT_FUNC PyInit__rayforce_c(void)
{
    PyObject *m;

    if (PyType_Ready(&RayObjectType) < 0)
        return NULL;

    m = PyModule_Create(&rayforce_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&RayObjectType);

    // Make RayObjectType accessible from .RayObject
    if (PyModule_AddObject(m, "RayObject", (PyObject *)&RayObjectType) < 0)
    {
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

    char *argv[] = {"raypy", "-r", "0", NULL};
    g_runtime = runtime_create(3, argv);
    if (g_runtime == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize Rayforce");
        return NULL;
    }

    return m;
}
