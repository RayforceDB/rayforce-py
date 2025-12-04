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
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    if (result != NULL)
    {
        result->obj = i16(value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_i32(PyObject *self, PyObject *args)
{
    (void)self;
    int value;
    if (!PyArg_ParseTuple(args, "i", &value))
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = i32(value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_i64(PyObject *self, PyObject *args)
{
    (void)self;
    long long value;
    if (!PyArg_ParseTuple(args, "L", &value))
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = i64(value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_f64(PyObject *self, PyObject *args)
{
    (void)self;
    double value;
    if (!PyArg_ParseTuple(args, "d", &value))
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = f64(value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_c8(PyObject *self, PyObject *args)
{
    (void)self;
    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
    {
        return NULL;
    }

    // Validate char is single element
    if (len != 1)
    {
        PyErr_SetString(PyExc_ValueError, "Character must be a single character");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = c8(value[0]);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_string(PyObject *self, PyObject *args)
{
    (void)self;
    // String is generally used for eval_str function.
    // Raypy has no use of them at the moment.

    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        // Create string object using rayforce function
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
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        // Symbol is a standalone type, hence no vectors are required
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
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = b8(bool_value ? 1 : 0);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_u8(PyObject *self, PyObject *args)
{
    (void)self;
    unsigned char byte_value;

    if (!PyArg_ParseTuple(args, "b", &byte_value))
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = u8(byte_value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_date(PyObject *self, PyObject *args)
{
    (void)self;
    // Date is a number of days since EPOCH
    int days_value;

    if (!PyArg_ParseTuple(args, "i", &days_value))
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = adate(days_value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_time(PyObject *self, PyObject *args)
{
    (void)self;
    // Time is a number of milliseconds within 1 day (86399999 ms max)
    int ms_value;

    if (!PyArg_ParseTuple(args, "i", &ms_value))
    {
        return NULL;
    }

    // Check if the value is within the valid range
    if (ms_value < 0 || ms_value > 86399999)
    {
        PyErr_SetString(PyExc_ValueError, "Time value must be in range 0-86399999 milliseconds");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = atime(ms_value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_timestamp(PyObject *self, PyObject *args)
{
    (void)self;
    // Timestamp is a number of milliseconds since EPOCH
    long long ms_value;

    if (!PyArg_ParseTuple(args, "L", &ms_value))
    {
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = timestamp(ms_value);
    }
    return (PyObject *)result;
}
static PyObject *raypy_init_guid(PyObject *self, PyObject *args)
{
    (void)self;
    const char *guid_str;
    Py_ssize_t str_len;

    if (!PyArg_ParseTuple(args, "s#", &guid_str, &str_len))
    {
        return NULL;
    }

    // Check if the string length is 36 characters (standard GUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
    if (str_len != 36)
    {
        PyErr_SetString(PyExc_ValueError, "GUID string must be exactly 36 characters (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        // Create a GUID object (single GUID atom) - same pattern as rayforce guid() function
        result->obj = vector(TYPE_I64, 2);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create GUID");
            return NULL;
        }
        result->obj->type = -TYPE_GUID;

        // Convert string to GUID using rayforce function
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
    {
        return NULL;
    }

    if (initial_size < 0)
    {
        PyErr_SetString(PyExc_ValueError, "List size cannot be negative");
        return NULL;
    }

    // Allocate memory for py object
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
    // Table is a type where keys are vector of symbols, and values are a list
    // of any values

    RayObject *keys_obj;
    RayObject *vals_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType, &vals_obj))
    {
        return NULL;
    }

    if (keys_obj->obj == NULL || keys_obj->obj->type != TYPE_SYMBOL)
    {
        PyErr_SetString(PyExc_TypeError, "Keys must be a vector of symbols");
        return NULL;
    }

    if (vals_obj->obj == NULL || vals_obj->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Values must be a list");
        return NULL;
    }

    if (keys_obj->obj->len != vals_obj->obj->len)
    {
        PyErr_SetString(PyExc_ValueError, "Keys and values lists must have the same length");
        return NULL;
    }

    // Allocate memory for py object
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
    // Dict is a type where keys and values are iterables of same length
    RayObject *keys_obj;
    RayObject *vals_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType, &vals_obj))
    {
        return NULL;
    }

    if (keys_obj->obj->len != vals_obj->obj->len)
    {
        PyErr_SetString(PyExc_ValueError, "Keys and values lists must have the same length");
        return NULL;
    }

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
    // Vector has certain type and length. If multiple types are present in vector,
    // Vector becomes List (type 0)
    int type_code;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "in", &type_code, &length))
    {
        return NULL;
    }

    if (length < 0)
    {
        PyErr_SetString(PyExc_ValueError, "Vector length cannot be negative");
        return NULL;
    }

    // Allocate memory for py object
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
static PyObject *raypy_init_lambda(PyObject *self, PyObject *args)
{
    (void)self;
    // Lambda has 3 components: args (list of argument names), body (expression), nfo (metadata)
    RayObject *args_obj;
    RayObject *body_obj;
    RayObject *nfo_obj = NULL;

    if (!PyArg_ParseTuple(args, "O!O!|O!", &RayObjectType, &args_obj, &RayObjectType, &body_obj, &RayObjectType, &nfo_obj))
    {
        return NULL;
    }

    // Validate args parameter (should be a list or vector of symbols)
    if (args_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Arguments object cannot be NULL");
        return NULL;
    }

    // Validate body parameter (should be an expression object)
    if (body_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Body object cannot be NULL");
        return NULL;
    }

    // Set default nfo if not provided
    obj_p nfo_ptr = (nfo_obj && nfo_obj->obj) ? nfo_obj->obj : NULL_OBJ;

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        // Clone args and body because lambda will own the objects
        obj_p clone_args = clone_obj(args_obj->obj);
        obj_p clone_body = clone_obj(body_obj->obj);

        result->obj = lambda(clone_args, clone_body, nfo_ptr);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create lambda");
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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_SYMBOL)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a symbol");
        return NULL;
    }

    // Get the symbol ID
    i64_t symbol_id = ray_obj->obj->i64;

    // Get the string representation
    const char *str = str_from_symbol(symbol_id);
    if (str == NULL)
    {
        Py_RETURN_NONE;
    }

    return PyUnicode_FromString(str);
}
static PyObject *raypy_read_b8(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_B8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a B8 type");
        return NULL;
    }

    if (ray_obj->obj->b8)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
static PyObject *raypy_read_u8(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
    {
        return NULL;
    }

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
static PyObject *raypy_get_obj_attrs(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    return PyLong_FromLong(ray_obj->obj->attrs);
}

static PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    long value;

    if (!PyArg_ParseTuple(args, "O!l", &RayObjectType, &ray_obj, &value))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    ray_obj->obj->attrs = (char)value;

    return PyLong_FromLong(ray_obj->obj->attrs);
}

static PyObject *raypy_is_vector(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (ray_obj->obj->type > 0 &&
        ray_obj->obj->type != TYPE_DICT &&
        ray_obj->obj->type != TYPE_TABLE &&
        ray_obj->obj->type != TYPE_LAMBDA &&
        ray_obj->obj->type != TYPE_UNARY &&
        ray_obj->obj->type != TYPE_BINARY &&
        ray_obj->obj->type != TYPE_VARY &&
        ray_obj->obj->type != TYPE_TOKEN)
    {
        if (ray_obj->obj->len >= 0)
        {
            Py_RETURN_TRUE;
        }
    }

    Py_RETURN_FALSE;
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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_TABLE)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TABLE type");
        return NULL;
    }

    obj_p keys_list = AS_LIST(ray_obj->obj)[0];
    if (keys_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Table has no keys list");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = clone_obj(keys_list);
    }
    return (PyObject *)result;
}
static PyObject *raypy_table_values(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_TABLE)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TABLE type");
        return NULL;
    }

    obj_p values_list = AS_LIST(ray_obj->obj)[1];
    if (values_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Table has no values list");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = clone_obj(values_list);
    }
    return (PyObject *)result;
}
// END TABLE OPERATIONS
// ---------------------------------------------------------------------------

// DICT OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_dict_length(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    obj_p keys_list = AS_LIST(ray_obj->obj)[0];
    if (keys_list == NULL)
    {
        return PyLong_FromLong(0);
    }

    return PyLong_FromUnsignedLongLong(keys_list->len);
}
static PyObject *raypy_dict_keys(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    // PyObject *py_list = PyList_New(keys_list->len);
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    obj_p keys = ray_key(ray_obj->obj);
    if (keys == NULL)
    {
        Py_RETURN_NONE;
    }

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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    // PyObject *py_list = PyList_New(keys_list->len);
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);

    obj_p keys = ray_value(ray_obj->obj);
    if (keys == NULL)
    {
        Py_RETURN_NONE;
    }

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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    if (key_obj->obj->type != -TYPE_SYMBOL && key_obj->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Key must be a symbol or string");
        return NULL;
    }

    obj_p result = at_obj(ray_obj->obj, key_obj->obj);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_KeyError, "Key not found in dictionary");
        return NULL;
    }

    // Allocate memory for new py object
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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (index < 0 || index >= (Py_ssize_t)ray_obj->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "Vector index out of range");
        return NULL;
    }

    obj_p item = at_idx(ray_obj->obj, (i64_t)index);
    if (item == NULL)
    {
        Py_RETURN_NONE;
    }

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (index < 0 || index > (Py_ssize_t)ray_obj->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "Insert index out of range");
        return NULL;
    }

    obj_p clone = clone_obj(item->obj);
    if (clone == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    ins_obj(&ray_obj->obj, (i64_t)index, clone);
    Py_RETURN_NONE;
}
static PyObject *raypy_remove_idx(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "O!n", &RayObjectType, &ray_obj, &index))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (index < 0 || index > (Py_ssize_t)ray_obj->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "Insert index out of range");
        return NULL;
    }

    // Remove the item at the index
    if (remove_idx(&ray_obj->obj, (i64_t)index) == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to remove item from list");
        return NULL;
    }

    Py_RETURN_NONE;
}
static PyObject *raypy_push_obj(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    RayObject *item;
    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj, &RayObjectType, &item))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    // We need to clone the item since push_obj will own the object
    obj_p clone = clone_obj(item->obj);
    if (clone == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    push_obj(&ray_obj->obj, clone);
    Py_RETURN_NONE;
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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (ray_obj->obj->type > 0 ||
        ray_obj->obj->type == TYPE_LIST ||
        ray_obj->obj->type == TYPE_DICT ||
        ray_obj->obj->type == TYPE_TABLE)
    {
        return PyLong_FromUnsignedLongLong(ray_obj->obj->len);
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "Object does not have a length attribute");
        return NULL;
    }
}
static PyObject *raypy_repr_table(PyObject *self, PyObject *args)
{
	(void)self;
	RayObject *ray_obj;
	int full = 1;

	if (!PyArg_ParseTuple(args, "O!|p", &RayObjectType, &ray_obj, &full))
	{
		return NULL;
	}

	if (ray_obj->obj == NULL)
	{
		PyErr_SetString(PyExc_ValueError, "Object cannot be NULL");
		return NULL;
	}

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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot evaluate NULL object");
        return NULL;
    }

    if (ray_obj->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object must be a string (TYPE_C8) for evaluation");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

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
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (ray_obj->obj->type != TYPE_ERR)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an error type");
        return NULL;
    }

    ray_error_p err = AS_ERROR(ray_obj->obj);

    if (err != NULL && err->msg != NULL && err->msg->type == TYPE_C8)
    {
        const char *error_text = AS_C8(err->msg);
        u64_t length = err->msg->len;

        PyObject *error_message = PyUnicode_DecodeLatin1(error_text, length, "replace");

        if (err->locs != NULL && err->locs->type == TYPE_LIST && err->locs->len > 0)
        {
            PyObject *with_code = PyUnicode_FromFormat("%s (error code: %lld)",
                                                       PyUnicode_AsUTF8(error_message),
                                                       (long long)err->code);
            Py_DECREF(error_message);
            return with_code;
        }

        return error_message;
    }

    if (err != NULL)
    {
        return PyUnicode_FromFormat("Error code: %lld", (long long)err->code);
    }
    else
    {
        return PyUnicode_FromString("Unknown error");
    }
}
static PyObject *raypy_binary_set(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *symbol_or_path;
    RayObject *value;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &symbol_or_path, &RayObjectType, &value))
    {
        return NULL;
    }

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

    // Allocate memory for result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = binary_set(symbol_or_path->obj, value->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to execute set operation");
        return NULL;
    }

    if (result->obj->type == TYPE_ERR)
    {
        return (PyObject *)result;
    }
    return (PyObject *)result;
}
static PyObject *raypy_env_get_internal_function_by_name(PyObject *self, PyObject *args)
{
    (void)self;
    const char *name;
    Py_ssize_t name_len;

    if (!PyArg_ParseTuple(args, "s#", &name, &name_len))
    {
        return NULL;
    }

    if (name_len == 0)
    {
        PyErr_SetString(PyExc_ValueError, "Function name cannot be empty");
        return NULL;
    }

    obj_p func_obj = env_get_internal_function(name);

    if (func_obj == NULL_OBJ || func_obj == NULL)
    {
        Py_RETURN_NONE;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        drop_obj(func_obj);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = func_obj;
    return (PyObject *)result;
}
static PyObject *raypy_env_get_internal_name_by_function(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "RayObject cannot be NULL");
        return NULL;
    }

    str_p name = env_get_internal_name(ray_obj->obj);

    if (name == NULL)
    {
        Py_RETURN_NONE;
    }
    return PyUnicode_FromString(name);
}
static PyObject *raypy_eval_obj(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "RayObject cannot be NULL");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

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

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj)) { return NULL; }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "RayObject cannot be NULL");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

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

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj)) { return NULL; }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "RayObject cannot be NULL");
        return NULL;
    }

    u32_t rc = rc_obj(ray_obj->obj);
    return PyLong_FromUnsignedLong(rc);
}
static PyObject *raypy_loadfn(PyObject *self, PyObject *args)
{
    (void)self;
    const char *path;
    const char *func_name;
    int nargs;
    Py_ssize_t path_len, func_len;

    if (!PyArg_ParseTuple(args, "s#s#i", &path, &path_len, &func_name, &func_len, &nargs))
    {
        return NULL;
    }

    if (path_len == 0)
    {
        PyErr_SetString(PyExc_ValueError, "Library path cannot be empty");
        return NULL;
    }

    if (func_len == 0)
    {
        PyErr_SetString(PyExc_ValueError, "Function name cannot be empty");
        return NULL;
    }

    if (nargs < 0)
    {
        PyErr_SetString(PyExc_ValueError, "Number of arguments cannot be negative");
        return NULL;
    }

    // Create RayObject string for path
    RayObject *path_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (path_obj == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate path object");
        return NULL;
    }
    path_obj->obj = vector(TYPE_C8, path_len);
    if (path_obj->obj == NULL)
    {
        Py_DECREF(path_obj);
        PyErr_SetString(PyExc_MemoryError, "Failed to create path string");
        return NULL;
    }
    memcpy(AS_C8(path_obj->obj), path, path_len);

    // Create RayObject string for function name
    RayObject *func_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (func_obj == NULL)
    {
        Py_DECREF(path_obj);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate function name object");
        return NULL;
    }
    func_obj->obj = vector(TYPE_C8, func_len);
    if (func_obj->obj == NULL)
    {
        Py_DECREF(path_obj);
        Py_DECREF(func_obj);
        PyErr_SetString(PyExc_MemoryError, "Failed to create function name string");
        return NULL;
    }
    memcpy(AS_C8(func_obj->obj), func_name, func_len);

    // Create RayObject i64 for number of arguments
    RayObject *nargs_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (nargs_obj == NULL)
    {
        Py_DECREF(path_obj);
        Py_DECREF(func_obj);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate nargs object");
        return NULL;
    }
    nargs_obj->obj = i64((long long)nargs);

    // Allocate memory for result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        Py_DECREF(path_obj);
        Py_DECREF(func_obj);
        Py_DECREF(nargs_obj);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Prepare arguments array for ray_loadfn
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

// MATH OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_math_add(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj1;
    RayObject *ray_obj2;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj1, &RayObjectType, &ray_obj2))
    {
        return NULL;
    }

    if (ray_obj1->obj == NULL || ray_obj2->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot add NULL objects");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_add(ray_obj1->obj, ray_obj2->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform addition operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_sub(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj1;
    RayObject *ray_obj2;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj1, &RayObjectType, &ray_obj2))
    {
        return NULL;
    }

    if (ray_obj1->obj == NULL || ray_obj2->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot subtract NULL objects");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_sub(ray_obj1->obj, ray_obj2->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform subtraction operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_mul(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj1;
    RayObject *ray_obj2;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj1, &RayObjectType, &ray_obj2))
    {
        return NULL;
    }

    if (ray_obj1->obj == NULL || ray_obj2->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot multiply NULL objects");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_mul(ray_obj1->obj, ray_obj2->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform multiplication operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_div(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj1;
    RayObject *ray_obj2;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj1, &RayObjectType, &ray_obj2))
    {
        return NULL;
    }

    if (ray_obj1->obj == NULL || ray_obj2->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot divide NULL objects");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_div(ray_obj1->obj, ray_obj2->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform division operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_fdiv(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj1;
    RayObject *ray_obj2;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj1, &RayObjectType, &ray_obj2))
    {
        return NULL;
    }

    if (ray_obj1->obj == NULL || ray_obj2->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot divide NULL objects");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_fdiv(ray_obj1->obj, ray_obj2->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform floating-point division operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_mod(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj1;
    RayObject *ray_obj2;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj1, &RayObjectType, &ray_obj2))
    {
        return NULL;
    }

    if (ray_obj1->obj == NULL || ray_obj2->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot perform modulo operation on NULL objects");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_mod(ray_obj1->obj, ray_obj2->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform modulo operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_sum(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot sum NULL object");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_sum(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform sum operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_avg(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute average of NULL object");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Handle empty vector case
    if ((ray_obj->obj->type == TYPE_I64 || ray_obj->obj->type == TYPE_F64) && ray_obj->obj->len == 0)
    {
        result->obj = f64(0.0);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create zero result");
            return NULL;
        }
        return (PyObject *)result;
    }

    result->obj = ray_avg(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform average operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_med(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute median of NULL object");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    if ((ray_obj->obj->type == TYPE_I64 || ray_obj->obj->type == TYPE_F64) && ray_obj->obj->len == 0)
    {
        result->obj = f64(0.0);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create zero result");
            return NULL;
        }
        return (PyObject *)result;
    }

    // F64 vectors are not supported by the core's ray_med function
    if (ray_obj->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for median operation");
        return NULL;
    }

    result->obj = ray_med(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform median operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_dev(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute standard deviation of NULL object");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    if ((ray_obj->obj->type == TYPE_I64 || ray_obj->obj->type == TYPE_F64) && ray_obj->obj->len == 0)
    {
        result->obj = f64(0.0);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create zero result");
            return NULL;
        }
        return (PyObject *)result;
    }

    // F64 vectors are not supported by the core's ray_dev function
    if (ray_obj->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for standard deviation operation");
        return NULL;
    }

    result->obj = ray_dev(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform standard deviation operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_min(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute minimum of NULL object");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    if ((ray_obj->obj->type == TYPE_I64 || ray_obj->obj->type == TYPE_F64) && ray_obj->obj->len == 0)
    {
        result->obj = f64(0.0);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create zero result");
            return NULL;
        }
        return (PyObject *)result;
    }

    // F64 vectors are not supported by the core's ray_min function
    if (ray_obj->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for minimum operation");
        return NULL;
    }

    result->obj = ray_min(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform minimum operation");
        return NULL;
    }

    return (PyObject *)result;
}
static PyObject *raypy_math_max(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *ray_obj;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    {
        return NULL;
    }

    if (ray_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute maximum of NULL object");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    if ((ray_obj->obj->type == TYPE_I64 || ray_obj->obj->type == TYPE_F64) && ray_obj->obj->len == 0)
    {
        result->obj = f64(0.0);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create zero result");
            return NULL;
        }
        return (PyObject *)result;
    }

    // F64 vectors are not supported by the core's ray_max function
    if (ray_obj->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for maximum operation");
        return NULL;
    }

    result->obj = ray_max(ray_obj->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform maximum operation");
        return NULL;
    }

    return (PyObject *)result;
}
// END MATH OPERATIONS
// ---------------------------------------------------------------------------

// DATABASE OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_select(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *query_dict;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &query_dict))
    {
        return NULL;
    }

    // Validate that the query object exists and is a dictionary
    if (query_dict->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Query object cannot be NULL");
        return NULL;
    }

    if (query_dict->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Query must be a dictionary (TYPE_DICT)");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = EVAL_WITH_CTX(ray_select(query_dict->obj), NULL_OBJ);
    return (PyObject *)result;
}
static PyObject *raypy_update(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *update_dict;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &update_dict)) { return NULL; }

    // Validate that the update object exists and is a dictionary
    if (update_dict->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Update object cannot be NULL");
        return NULL;
    }

    if (update_dict->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Update parameters must be a dictionary (TYPE_DICT)");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = EVAL_WITH_CTX(ray_update(update_dict->obj), NULL_OBJ);
    return (PyObject *)result;
}

static PyObject *raypy_insert(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *table_obj;
    RayObject *data_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &table_obj, &RayObjectType, &data_obj))
    {
        return NULL;
    }

    // Validate that the objects exist
    if (table_obj->obj == NULL || data_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Insert objects cannot be NULL");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Create array for ray_insert function call
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
    {
        return NULL;
    }

    // Validate that the objects exist
    if (table_obj->obj == NULL || keys_obj->obj == NULL || data_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Upsert objects cannot be NULL");
        return NULL;
    }

    // Allocate memory for py object
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Create array for ray_upsert function call
    obj_p ray_args[3] = {table_obj->obj, keys_obj->obj, data_obj->obj};
    
    result->obj = EVAL_WITH_CTX(ray_upsert(ray_args, 3), NULL_OBJ);
    return (PyObject *)result;
}

// END DATABASE OPERATIONS
// ---------------------------------------------------------------------------

// LAMBDA OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_lambda_get_args(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *lambda_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &lambda_obj))
    {
        return NULL;
    }

    if (lambda_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Lambda object cannot be NULL");
        return NULL;
    }

    if (lambda_obj->obj->type != TYPE_LAMBDA)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a lambda function");
        return NULL;
    }

    lambda_p lambda_data = AS_LAMBDA(lambda_obj->obj);

    // Return the arguments list
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = clone_obj(lambda_data->args);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to clone lambda arguments");
            return NULL;
        }
    }

    return (PyObject *)result;
}
static PyObject *raypy_lambda_get_body(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *lambda_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &lambda_obj))
    {
        return NULL;
    }

    if (lambda_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Lambda object cannot be NULL");
        return NULL;
    }

    if (lambda_obj->obj->type != TYPE_LAMBDA)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a lambda function");
        return NULL;
    }

    lambda_p lambda_data = AS_LAMBDA(lambda_obj->obj);

    // Return the body
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = clone_obj(lambda_data->body);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to clone lambda body");
            return NULL;
        }
    }

    return (PyObject *)result;
}
// TODO: Add lambda call
// END LAMBDA OPERATIONS
// ---------------------------------------------------------------------------

// IO OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_hopen(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *path_obj;
    RayObject *timeout_obj = NULL;

    if (!PyArg_ParseTuple(args, "O!|O!", &RayObjectType, &path_obj, &RayObjectType, &timeout_obj))
    {
        return NULL;
    }

    if (path_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Path object cannot be NULL");
        return NULL;
    }

    if (path_obj->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Path must be a string (TYPE_C8)");
        return NULL;
    }

    // Prepare arguments array for ray_hopen
    obj_p ray_args[2];
    i64_t arg_count = 1;
    
    ray_args[0] = path_obj->obj;
    
    if (timeout_obj != NULL)
    {
        if (timeout_obj->obj == NULL)
        {
            PyErr_SetString(PyExc_ValueError, "Timeout object cannot be NULL");
            return NULL;
        }
        
        if (timeout_obj->obj->type != -TYPE_I64)
        {
            PyErr_SetString(PyExc_TypeError, "Timeout must be an i64");
            return NULL;
        }
        
        ray_args[1] = timeout_obj->obj;
        arg_count = 2;
    }

    // Allocate memory for result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

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
    {
        return NULL;
    }

    if (handle_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Handle object cannot be NULL");
        return NULL;
    }

    if (handle_obj->obj->type != -TYPE_I32 && handle_obj->obj->type != -TYPE_I64)
    {
        PyErr_SetString(PyExc_TypeError, "Handle must be an i32 (file descriptor) or i64 (socket descriptor)");
        return NULL;
    }

    // Allocate memory for result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

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
    {
        return NULL;
    }

    if (handle_obj->obj == NULL || data_obj->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Handle and data objects cannot be NULL");
        return NULL;
    }

    if (handle_obj->obj->type != -TYPE_I32 && handle_obj->obj->type != -TYPE_I64)
    {
        PyErr_SetString(PyExc_TypeError, "Handle must be an i32 (file descriptor) or i64 (socket descriptor)");
        return NULL;
    }

    // Allocate memory for result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

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
    {"init_lambda", raypy_init_lambda, METH_VARARGS, "Create a new lambda function"},

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

    // Lambda operations
    {"get_lambda_args", raypy_lambda_get_args, METH_VARARGS, "Get lambda arguments vector"},
    {"get_lambda_body", raypy_lambda_get_body, METH_VARARGS, "Get lambda body"},

    // Type introspection
    {"is_vector", raypy_is_vector, METH_VARARGS, "Check if object is a vector"},

    // Table operations
    {"table_keys", raypy_table_keys, METH_VARARGS, "Get table keys"},
    {"table_values", raypy_table_values, METH_VARARGS, "Get table values"},
    {"repr_table", raypy_repr_table, METH_VARARGS, "Format table"},

    // Dictionary operations
    {"dict_length", raypy_dict_length, METH_VARARGS, "Get dictionary length"},
    {"dict_keys", raypy_dict_keys, METH_VARARGS, "Get dictionary keys"},
    {"dict_values", raypy_dict_values, METH_VARARGS, "Get dictionary values"},
    {"dict_get", raypy_dict_get, METH_VARARGS, "Get value from dictionary"},

    // Vector operations
    {"at_idx", raypy_at_idx, METH_VARARGS, "Get element at index"},
    {"insert_obj", raypy_insert_obj, METH_VARARGS, "Insert object at index"},
    {"push_obj", raypy_push_obj, METH_VARARGS, "Push object to the end of iterable"},
    {"remove_idx", raypy_remove_idx, METH_VARARGS, "Remove item at index"},

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
    {"get_obj_attrs", raypy_get_obj_attrs, METH_VARARGS, "Get object attributes"},
    {"set_obj_attrs", raypy_set_obj_attrs, METH_VARARGS, "Set object attributes"},
    
    // Math operations
    {"math_add", raypy_math_add, METH_VARARGS, "Add two objects"},
    {"math_sub", raypy_math_sub, METH_VARARGS, "Subtract two objects"},
    {"math_mul", raypy_math_mul, METH_VARARGS, "Multiply two objects"},
    {"math_div", raypy_math_div, METH_VARARGS, "Divide two objects"},
    {"math_fdiv", raypy_math_fdiv, METH_VARARGS, "Floating-point divide two objects"},
    {"math_mod", raypy_math_mod, METH_VARARGS, "Modulo operation on two objects"},
    {"math_sum", raypy_math_sum, METH_VARARGS, "Sum all elements in vector"},
    {"math_avg", raypy_math_avg, METH_VARARGS, "Average of vector elements"},
    {"math_med", raypy_math_med, METH_VARARGS, "Median of vector elements"},
    {"math_dev", raypy_math_dev, METH_VARARGS, "Standard deviation of vector elements"},
    {"math_min", raypy_math_min, METH_VARARGS, "Minimum value in vector"},
    {"math_max", raypy_math_max, METH_VARARGS, "Maximum value in vector"},

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
