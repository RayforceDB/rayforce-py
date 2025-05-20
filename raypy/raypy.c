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

// Forward declaration for memcpy if needed
#ifndef memcpy
extern void *memcpy(void *dest, const void *src, size_t n);
#endif

// Forward declaration of RayObjectType
static PyTypeObject RayObjectType;

typedef struct
{
    PyObject_HEAD obj_p obj;
} RayObject;

// Deallocator for RayObject
static void RayObject_dealloc(RayObject *self)
{
    if (self->obj != NULL)
    {
        self->obj->rc--;
        if (self->obj->rc == 0)
        {
            drop_obj(self->obj);
        }
    }
    Py_TYPE(self)->tp_free((PyObject *)self);
}

// INTEGERS GETTERS / SETTERS {{
static PyObject *RayObject_from_i16(PyTypeObject *type, PyObject *args)
{
    short value;
    if (!PyArg_ParseTuple(args, "h", &value))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = i16(value);
    }
    return (PyObject *)self;
}
static PyObject *RayObject_from_i32(PyTypeObject *type, PyObject *args)
{
    int value;
    if (!PyArg_ParseTuple(args, "i", &value))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = i32(value);
    }
    return (PyObject *)self;
}
static PyObject *RayObject_from_i64(PyTypeObject *type, PyObject *args)
{
    long long value;
    if (!PyArg_ParseTuple(args, "L", &value))
    {
        return NULL;
    }
    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = i64(value);
    }
    return (PyObject *)self;
}
static PyObject *RayObject_get_i16_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_I16)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an i16");
        return NULL;
    }
    return PyLong_FromLong(self->obj->i16);
}
static PyObject *RayObject_get_i32_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_I32)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an i32");
        return NULL;
    }
    return PyLong_FromLong(self->obj->i32);
}
static PyObject *RayObject_get_i64_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_I64)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an i64");
        return NULL;
    }
    return PyLong_FromLongLong(self->obj->i64);
}
// }}

// FLOAT GETTERS / SETTERS {{
static PyObject *RayObject_from_f64(PyTypeObject *type, PyObject *args)
{
    double value;
    if (!PyArg_ParseTuple(args, "d", &value))
    {
        return NULL;
    }
    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = f64(value);
    }
    return (PyObject *)self;
}

static PyObject *RayObject_get_f64_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an f64");
        return NULL;
    }
    return PyFloat_FromDouble(self->obj->f64);
}
// }}

// STRING OPERATIONS {{
// Create a character (c8)
static PyObject *RayObject_from_c8(PyTypeObject *type, PyObject *args)
{
    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
    {
        return NULL;
    }

    if (len != 1)
    {
        PyErr_SetString(PyExc_ValueError, "Character must be a single character");
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = c8(value[0]);
    }
    return (PyObject *)self;
}

// Get character value
static PyObject *RayObject_get_c8_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a c8");
        return NULL;
    }
    return PyUnicode_FromStringAndSize(&self->obj->c8, 1);
}

// Create a string from a Python string
static PyObject *RayObject_from_string(PyTypeObject *type, PyObject *args)
{
    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        // Create a vector of TYPE_C8 with the right length
        self->obj = vector(TYPE_C8, len);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create string");
            return NULL;
        }

        // Copy the string data
        memcpy(AS_C8(self->obj), value, len);
    }
    return (PyObject *)self;
}

// Get string value
static PyObject *RayObject_get_string_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a string");
        return NULL;
    }

    return PyUnicode_FromStringAndSize(AS_C8(self->obj), self->obj->len);
}

// Get string length
static PyObject *RayObject_get_string_length(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a string");
        return NULL;
    }

    return PyLong_FromUnsignedLongLong(self->obj->len);
}

// Get character at index
static PyObject *RayObject_get_string_char(RayObject *self, PyObject *args)
{
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index))
    {
        return NULL;
    }

    if (self->obj == NULL || self->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a string");
        return NULL;
    }

    if (index < 0 || index >= (Py_ssize_t)self->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "String index out of range");
        return NULL;
    }

    char c = AS_C8(self->obj)[index];
    return PyUnicode_FromStringAndSize(&c, 1);
}

// Check if object is a string
static PyObject *RayObject_is_string(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (self->obj->type == TYPE_C8)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}

// Check if object is a character
static PyObject *RayObject_is_c8(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (self->obj->type == -TYPE_C8)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}
// }}

// SYMBOL OPERATIONS {{
// Create a symbol from a string
static PyObject *RayObject_from_symbol(PyTypeObject *type, PyObject *args)
{
    const char *value;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#", &value, &len))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = symbol(value, len);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create symbol");
            return NULL;
        }
    }
    return (PyObject *)self;
}

// Create a symbol from an integer ID
static PyObject *RayObject_from_symbol_id(PyTypeObject *type, PyObject *args)
{
    long long id;

    if (!PyArg_ParseTuple(args, "L", &id))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = symboli64(id);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create symbol from ID");
            return NULL;
        }
    }
    return (PyObject *)self;
}

// Get symbol string value
static PyObject *RayObject_get_symbol_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_SYMBOL)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a symbol");
        return NULL;
    }

    // Get the symbol ID
    i64_t symbol_id = self->obj->i64;

    // Get the string representation
    const char *str = str_from_symbol(symbol_id);
    if (str == NULL)
    {
        Py_RETURN_NONE;
    }

    return PyUnicode_FromString(str);
}

// Get symbol ID value
static PyObject *RayObject_get_symbol_id(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_SYMBOL)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a symbol");
        return NULL;
    }

    return PyLong_FromLongLong(self->obj->i64);
}

// Check if object is a symbol
static PyObject *RayObject_is_symbol(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (self->obj->type == -TYPE_SYMBOL)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}
// }}

// LIST OPERATIONS {{
// Create an empty list
static PyObject *RayObject_create_list(PyTypeObject *type, PyObject *args)
{
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

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = vector(TYPE_LIST, (u64_t)initial_size);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create list");
            return NULL;
        }
    }
    return (PyObject *)self;
}

// Get list length
static PyObject *RayObject_list_length(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }

    return PyLong_FromUnsignedLongLong(self->obj->len);
}

// Append an item to the list
static PyObject *RayObject_list_append(RayObject *self, PyObject *args)
{
    RayObject *item;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    {
        return NULL;
    }

    if (self->obj == NULL || self->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }

    // We need to clone the item since push_obj will own the object
    obj_p clone = clone_obj(item->obj);
    if (clone == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    // Push the item to the list
    if (push_obj(&self->obj, clone) == NULL)
    {
        // If push_obj fails, we need to free the clone
        drop_obj(clone);
        PyErr_SetString(PyExc_RuntimeError, "Failed to append item to list");
        return NULL;
    }

    Py_RETURN_NONE;
}

// Get item at index
static PyObject *RayObject_list_get_item(RayObject *self, PyObject *args)
{
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index))
    {
        return NULL;
    }

    if (self->obj == NULL || self->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }

    if (index < 0 || index >= (Py_ssize_t)self->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "List index out of range");
        return NULL;
    }

    // Get the item at the index
    obj_p item = at_idx(self->obj, (i64_t)index);
    if (item == NULL)
    {
        Py_RETURN_NONE;
    }

    // Create a new RayObject with the item
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // We need to clone the item since it's owned by the list
    result->obj = clone_obj(item);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    return (PyObject *)result;
}

// Set item at index
static PyObject *RayObject_list_set_item(RayObject *self, PyObject *args)
{
    Py_ssize_t index;
    RayObject *item;
    if (!PyArg_ParseTuple(args, "nO!", &index, &RayObjectType, &item))
    {
        return NULL;
    }

    if (self->obj == NULL || self->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }

    if (index < 0 || index >= (Py_ssize_t)self->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "List index out of range");
        return NULL;
    }

    // Clone the item
    obj_p clone = clone_obj(item->obj);
    if (clone == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    // Set the item at the index
    if (set_idx(&self->obj, (i64_t)index, clone) == NULL)
    {
        // If set_idx fails, we need to free the clone
        drop_obj(clone);
        PyErr_SetString(PyExc_RuntimeError, "Failed to set item in list");
        return NULL;
    }

    Py_RETURN_NONE;
}

// Remove item at index
static PyObject *RayObject_list_remove_item(RayObject *self, PyObject *args)
{
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index))
    {
        return NULL;
    }

    if (self->obj == NULL || self->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }

    if (index < 0 || index >= (Py_ssize_t)self->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "List index out of range");
        return NULL;
    }

    // Remove the item at the index
    if (remove_idx(&self->obj, (i64_t)index) == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to remove item from list");
        return NULL;
    }

    Py_RETURN_NONE;
}

// Check if object is a list
static PyObject *RayObject_is_list(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (self->obj->type == TYPE_LIST)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}
// }}

// Get object type (references are in rayforce.h)
static PyObject *RayObject_get_type(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }
    return PyLong_FromLong(self->obj->type);
}

/*
 * B8 (Boolean) type handling functions
 */

// Convert a Python boolean to a RayObject with B8 type
static PyObject *
RayObject_from_b8(PyTypeObject *type, PyObject *args)
{
    int bool_value;

    if (!PyArg_ParseTuple(args, "p", &bool_value))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = b8(bool_value ? 1 : 0);
    }
    return (PyObject *)self;
}

// Get the boolean value from a RayObject of B8 type
static PyObject *
RayObject_get_b8_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_B8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a B8 type");
        return NULL;
    }

    if (self->obj->b8)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

/*
 * U8 (Unsigned 8-bit integer) type handling functions
 */

// Convert a Python integer to a RayObject with U8 type
static PyObject *
RayObject_from_u8(PyTypeObject *type, PyObject *args)
{
    unsigned char byte_value;

    if (!PyArg_ParseTuple(args, "b", &byte_value))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = u8(byte_value);
    }
    return (PyObject *)self;
}

// Get the unsigned 8-bit integer value from a RayObject of U8 type
static PyObject *
RayObject_get_u8_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_U8)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a U8 type");
        return NULL;
    }

    return PyLong_FromLong((long)self->obj->u8);
}

/*
 * DATE type handling functions
 */

// Convert a Python integer (days since epoch) to a RayObject with DATE type
static PyObject *
RayObject_from_date(PyTypeObject *type, PyObject *args)
{
    int days_value;

    if (!PyArg_ParseTuple(args, "i", &days_value))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = adate(days_value);
    }
    return (PyObject *)self;
}

// Get the date value (days since epoch) from a RayObject of DATE type
static PyObject *
RayObject_get_date_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_DATE)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DATE type");
        return NULL;
    }

    return PyLong_FromLong(self->obj->i32);
}

/*
 * TIME type handling functions
 */

// Convert a Python integer (milliseconds since midnight) to a RayObject with TIME type
static PyObject *
RayObject_from_time(PyTypeObject *type, PyObject *args)
{
    int ms_value;

    if (!PyArg_ParseTuple(args, "i", &ms_value))
    {
        return NULL;
    }

    // Check if the value is within the valid range (0-86399999 milliseconds in a day)
    if (ms_value < 0 || ms_value > 86399999)
    {
        PyErr_SetString(PyExc_ValueError, "Time value must be in range 0-86399999 milliseconds");
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = atime(ms_value);
    }
    return (PyObject *)self;
}

// Get the time value (milliseconds since midnight) from a RayObject of TIME type
static PyObject *
RayObject_get_time_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_TIME)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TIME type");
        return NULL;
    }

    return PyLong_FromLong(self->obj->i32);
}

/*
 * TIMESTAMP type handling functions
 */

// Convert a Python integer (milliseconds since epoch) to a RayObject with TIMESTAMP type
static PyObject *
RayObject_from_timestamp(PyTypeObject *type, PyObject *args)
{
    long long ms_value;

    if (!PyArg_ParseTuple(args, "L", &ms_value))
    {
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = timestamp(ms_value);
    }
    return (PyObject *)self;
}

// Get the timestamp value (milliseconds since epoch) from a RayObject of TIMESTAMP type
static PyObject *
RayObject_get_timestamp_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_TIMESTAMP)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TIMESTAMP type");
        return NULL;
    }

    return PyLong_FromLongLong(self->obj->i64);
}

/*
 * GUID type handling functions
 */

// Convert a Python bytes/bytearray object to a RayObject with GUID type
static PyObject *
RayObject_from_guid(PyTypeObject *type, PyObject *args)
{
    Py_buffer buffer;

    if (!PyArg_ParseTuple(args, "y*", &buffer))
    {
        return NULL;
    }

    // Check if the buffer size is 16 bytes (standard GUID size)
    if (buffer.len != 16)
    {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_ValueError, "GUID must be exactly 16 bytes");
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        // Create a GUID object and copy the bytes
        self->obj = vector(TYPE_GUID, 16);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyBuffer_Release(&buffer);
            PyErr_SetString(PyExc_MemoryError, "Failed to create GUID");
            return NULL;
        }

        // Copy the GUID data
        memcpy(AS_U8(self->obj), buffer.buf, 16);
    }

    // Release the buffer
    PyBuffer_Release(&buffer);

    return (PyObject *)self;
}

// Get the GUID value as bytes from a RayObject of GUID type
static PyObject *
RayObject_get_guid_value(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_GUID)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a GUID type");
        return NULL;
    }

    return PyBytes_FromStringAndSize((const char *)AS_U8(self->obj), 16);
}

// Check if object is a GUID
static PyObject *RayObject_is_guid(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (self->obj->type == TYPE_GUID)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}

// Check if object is a vector (has a positive type)
static PyObject *RayObject_is_vector(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    // Настоящие векторы имеют положительные типы, но исключаем специальные типы:
    // - TYPE_LIST=0 не является вектором
    // - TYPE_GUID=11 не является вектором (хотя формально является)
    // - TYPE_DICT=99 не является вектором
    // - TYPE_TABLE=98 не является вектором
    // - TYPE_LAMBDA=100 и другие специальные типы не являются векторами
    if (self->obj->type > 0 &&
        self->obj->type != TYPE_GUID &&
        self->obj->type != TYPE_DICT &&
        self->obj->type != TYPE_TABLE &&
        self->obj->type != TYPE_LAMBDA &&
        self->obj->type != TYPE_UNARY &&
        self->obj->type != TYPE_BINARY &&
        self->obj->type != TYPE_VARY &&
        self->obj->type != TYPE_TOKEN)
    {

        // Проверяем, что у объекта есть длина
        if (self->obj->len >= 0)
        {
            Py_RETURN_TRUE;
        }
    }

    Py_RETURN_FALSE;
}

// Get vector type code (for vectors with positive type)
static PyObject *RayObject_get_vector_type(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    // Проверяем, что это вектор - положительный тип, исключая специальные типы
    if (self->obj->type <= 0 ||
        self->obj->type == TYPE_GUID ||
        self->obj->type == TYPE_DICT ||
        self->obj->type == TYPE_TABLE ||
        self->obj->type == TYPE_LAMBDA ||
        self->obj->type == TYPE_UNARY ||
        self->obj->type == TYPE_BINARY ||
        self->obj->type == TYPE_VARY ||
        self->obj->type == TYPE_TOKEN)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a vector");
        return NULL;
    }

    // Дополнительно проверяем, что у объекта есть атрибут len
    if (self->obj->len < 0)
    {
        PyErr_SetString(PyExc_TypeError, "Object does not have a valid length attribute");
        return NULL;
    }

    // Возвращаем тип вектора
    return PyLong_FromLong(self->obj->type);
}

/*
 * TABLE type handling functions
 */

// Create a table from keys and values lists
static PyObject *
RayObject_create_table(PyTypeObject *type, PyObject *args)
{
    RayObject *keys_obj;
    RayObject *vals_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType, &vals_obj))
    {
        return NULL;
    }

    if (vals_obj->obj == NULL || vals_obj->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Values must be a list");
        return NULL;
    }

    // Check that lists have the same length
    if (keys_obj->obj->len != vals_obj->obj->len)
    {
        PyErr_SetString(PyExc_ValueError, "Keys and values lists must have the same length");
        return NULL;
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = table(keys_obj->obj, vals_obj->obj);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create table");
            return NULL;
        }
    }

    return (PyObject *)self;
}

// Get a value from a table by key
static PyObject *
RayObject_table_get(RayObject *self, PyObject *args)
{
    RayObject *key_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &key_obj))
    {
        return NULL;
    }

    if (self->obj == NULL || self->obj->type != TYPE_TABLE)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TABLE type");
        return NULL;
    }

    obj_p result = at_obj(self->obj, key_obj->obj);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_KeyError, "Key not found in table");
        return NULL;
    }

    // Create a new RayObject to wrap the result
    RayObject *ray_result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (ray_result != NULL)
    {
        ray_result->obj = result;
    }

    return (PyObject *)ray_result;
}

// Check if object is a table
static PyObject *
RayObject_is_table(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (self->obj->type == TYPE_TABLE)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}

// Get all keys from a table
static PyObject *
RayObject_table_keys(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_TABLE)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TABLE type");
        return NULL;
    }

    // Таблица содержит список ключей в AS_LIST(self->obj)[0]
    obj_p keys_list = AS_LIST(self->obj)[0];
    if (keys_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Table has no keys list");
        return NULL;
    }

    // Возвращаем сам объект списка ключей
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = clone_obj(keys_list);
    }
    return (PyObject *)result;
}

// Get all values from a table
static PyObject *
RayObject_table_values(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_TABLE)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a TABLE type");
        return NULL;
    }

    // Таблица содержит список значений в AS_LIST(self->obj)[1]
    obj_p values_list = AS_LIST(self->obj)[1];
    if (values_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Table has no values list");
        return NULL;
    }

    // Возвращаем сам объект списка значений
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = clone_obj(values_list);
    }
    return (PyObject *)result;
}

/*
 * DICT type handling functions
 */

// Create a dictionary from keys and values lists
static PyObject *
RayObject_create_dict(PyTypeObject *type, PyObject *args)
{
    RayObject *keys_obj;
    RayObject *vals_obj;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType, &vals_obj))
    {
        return NULL;
    }

    // Check that inputs are lists
    if (keys_obj->obj == NULL || keys_obj->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Keys must be a list");
        return NULL;
    }

    if (vals_obj->obj == NULL || vals_obj->obj->type != TYPE_LIST)
    {
        PyErr_SetString(PyExc_TypeError, "Values must be a list");
        return NULL;
    }

    // Check that lists have the same length
    if (keys_obj->obj->len != vals_obj->obj->len)
    {
        PyErr_SetString(PyExc_ValueError, "Keys and values lists must have the same length");
        return NULL;
    }

    // Make sure all keys are either symbols or strings
    for (i64_t i = 0; i < keys_obj->obj->len; i++)
    {
        obj_p key = at_idx(keys_obj->obj, i);
        if (key == NULL)
        {
            PyErr_SetString(PyExc_ValueError, "Invalid key at index");
            return NULL;
        }

        if (key->type != -TYPE_SYMBOL && key->type != TYPE_C8)
        {
            PyErr_SetString(PyExc_TypeError, "Keys must be symbols or strings");
            return NULL;
        }
    }

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = dict(keys_obj->obj, vals_obj->obj);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create dictionary");
            return NULL;
        }
    }

    return (PyObject *)self;
}

// Get the number of items in a dictionary
static PyObject *
RayObject_dict_length(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    // Словарь содержит список ключей в AS_LIST(self->obj)[0]
    obj_p keys_list = AS_LIST(self->obj)[0];
    if (keys_list == NULL)
    {
        return PyLong_FromLong(0);
    }

    // Возвращаем длину списка ключей
    return PyLong_FromUnsignedLongLong(keys_list->len);
}

// Get all keys from a dictionary
static PyObject *
RayObject_dict_keys(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    // Словарь содержит список ключей в AS_LIST(self->obj)[0]
    obj_p keys_list = AS_LIST(self->obj)[0];
    if (keys_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Dictionary has no keys list");
        return NULL;
    }

    // Создаем новый Python-список для хранения ключей
    PyObject *py_list = PyList_New(keys_list->len);
    if (py_list == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to create Python list for keys");
        return NULL;
    }

    // Копируем каждый ключ в новый список
    for (i64_t i = 0; i < keys_list->len; i++)
    {
        obj_p key = at_idx(keys_list, i);
        if (key == NULL)
        {
            Py_DECREF(py_list);
            PyErr_SetString(PyExc_RuntimeError, "Failed to retrieve key at index");
            return NULL;
        }

        // Создаем RayObject для каждого ключа
        RayObject *key_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
        if (key_obj == NULL)
        {
            Py_DECREF(py_list);
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate key object");
            return NULL;
        }

        key_obj->obj = clone_obj(key);
        if (key_obj->obj == NULL)
        {
            Py_DECREF(key_obj);
            Py_DECREF(py_list);
            PyErr_SetString(PyExc_MemoryError, "Failed to clone key");
            return NULL;
        }

        PyList_SET_ITEM(py_list, i, (PyObject *)key_obj);
    }

    return py_list;
}

// Get all values from a dictionary
static PyObject *
RayObject_dict_values(RayObject *self, PyObject *args)
{
    if (self->obj == NULL || self->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    // Словарь содержит список значений в AS_LIST(self->obj)[1]
    obj_p values_list = AS_LIST(self->obj)[1];
    if (values_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Dictionary has no values list");
        return NULL;
    }

    // Словарь содержит список ключей в AS_LIST(self->obj)[0]
    obj_p keys_list = AS_LIST(self->obj)[0];
    if (keys_list == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Dictionary has no keys list");
        return NULL;
    }

    // Создаем новый Python-список для хранения значений
    PyObject *py_list = PyList_New(values_list->len);
    if (py_list == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to create Python list for values");
        return NULL;
    }

    // Копируем каждое значение в новый список
    for (i64_t i = 0; i < values_list->len; i++)
    {
        obj_p value = at_idx(values_list, i);
        if (value == NULL)
        {
            Py_DECREF(py_list);
            PyErr_SetString(PyExc_RuntimeError, "Failed to retrieve value at index");
            return NULL;
        }

        // Создаем RayObject для каждого значения
        RayObject *val_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
        if (val_obj == NULL)
        {
            Py_DECREF(py_list);
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate value object");
            return NULL;
        }

        val_obj->obj = clone_obj(value);
        if (val_obj->obj == NULL)
        {
            Py_DECREF(val_obj);
            Py_DECREF(py_list);
            PyErr_SetString(PyExc_MemoryError, "Failed to clone value");
            return NULL;
        }

        PyList_SET_ITEM(py_list, i, (PyObject *)val_obj);
    }

    return py_list;
}

// Check if object is a dictionary
static PyObject *
RayObject_is_dict(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        Py_RETURN_FALSE;
    }

    if (self->obj->type == TYPE_DICT)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}

// Get a value from a dictionary by key
static PyObject *
RayObject_dict_get(RayObject *self, PyObject *args)
{
    RayObject *key_obj;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &key_obj))
    {
        return NULL;
    }

    if (self->obj == NULL || self->obj->type != TYPE_DICT)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not a DICT type");
        return NULL;
    }

    // Check that key is a symbol or string
    if (key_obj->obj->type != -TYPE_SYMBOL && key_obj->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Key must be a symbol or string");
        return NULL;
    }

    obj_p result = at_obj(self->obj, key_obj->obj);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_KeyError, "Key not found in dictionary");
        return NULL;
    }

    // Create a new RayObject to wrap the result
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

// Vector operations
static PyObject *RayObject_vector(PyTypeObject *type, PyObject *args)
{
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

    RayObject *self = (RayObject *)type->tp_alloc(type, 0);
    if (self != NULL)
    {
        self->obj = vector(type_code, (u64_t)length);
        if (self->obj == NULL)
        {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create vector");
            return NULL;
        }
    }
    return (PyObject *)self;
}

// Get vector element at index
static PyObject *RayObject_at_idx(RayObject *self, PyObject *args)
{
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index))
    {
        return NULL;
    }

    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (index < 0 || index >= (Py_ssize_t)self->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "Vector index out of range");
        return NULL;
    }

    obj_p item = at_idx(self->obj, (i64_t)index);
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

// Set vector element at index
static PyObject *RayObject_set_idx(RayObject *self, PyObject *args)
{
    Py_ssize_t index;
    RayObject *item;
    if (!PyArg_ParseTuple(args, "nO!", &index, &RayObjectType, &item))
    {
        return NULL;
    }

    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (index < 0 || index >= (Py_ssize_t)self->obj->len)
    {
        PyErr_SetString(PyExc_IndexError, "Vector index out of range");
        return NULL;
    }

    obj_p clone = clone_obj(item->obj);
    if (clone == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }

    if (set_idx(&self->obj, (i64_t)index, clone) == NULL)
    {
        drop_obj(clone);
        PyErr_SetString(PyExc_RuntimeError, "Failed to set item in vector");
        return NULL;
    }

    Py_RETURN_NONE;
}

/*
 * Get vector length for any object that has a length attribute
 */
static PyObject *RayObject_get_vector_length(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    // Проверяем, является ли объект вектором или другим типом, имеющим len
    if (self->obj->type > 0 ||
        self->obj->type == TYPE_LIST ||
        self->obj->type == TYPE_DICT ||
        self->obj->type == TYPE_TABLE)
    {

        return PyLong_FromUnsignedLongLong(self->obj->len);
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "Object does not have a length attribute");
        return NULL;
    }
}

/*
 * Addition operation for RayObjects
 */
static PyObject *RayObject_ray_add(RayObject *self, PyObject *args)
{
    RayObject *other;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &other))
    {
        return NULL;
    }

    if (self->obj == NULL || other->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot add NULL objects");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's add operation directly
    result->obj = ray_add(self->obj, other->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform addition operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Subtraction operation for RayObjects
 */
static PyObject *RayObject_ray_sub(RayObject *self, PyObject *args)
{
    RayObject *other;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &other))
    {
        return NULL;
    }

    if (self->obj == NULL || other->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot subtract NULL objects");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's subtract operation directly
    result->obj = ray_sub(self->obj, other->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform subtraction operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Multiplication operation for RayObjects
 */
static PyObject *RayObject_ray_mul(RayObject *self, PyObject *args)
{
    RayObject *other;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &other))
    {
        return NULL;
    }

    if (self->obj == NULL || other->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot multiply NULL objects");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's multiply operation directly
    result->obj = ray_mul(self->obj, other->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform multiplication operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Division operation for RayObjects
 */
static PyObject *RayObject_ray_div(RayObject *self, PyObject *args)
{
    RayObject *other;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &other))
    {
        return NULL;
    }

    if (self->obj == NULL || other->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot divide NULL objects");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's divide operation directly
    result->obj = ray_div(self->obj, other->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform division operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Floating-point division operation for RayObjects
 */
static PyObject *RayObject_ray_fdiv(RayObject *self, PyObject *args)
{
    RayObject *other;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &other))
    {
        return NULL;
    }

    if (self->obj == NULL || other->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot divide NULL objects");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's floating-point divide operation directly
    result->obj = ray_fdiv(self->obj, other->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform floating-point division operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Modulo operation for RayObjects
 */
static PyObject *RayObject_ray_mod(RayObject *self, PyObject *args)
{
    RayObject *other;

    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &other))
    {
        return NULL;
    }

    if (self->obj == NULL || other->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot perform modulo operation on NULL objects");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's modulo operation directly
    result->obj = ray_mod(self->obj, other->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform modulo operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Sum operation for RayObject vectors
 */
static PyObject *RayObject_ray_sum(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot sum NULL object");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's sum operation directly
    result->obj = ray_sum(self->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform sum operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Average operation for RayObject vectors
 */
static PyObject *RayObject_ray_avg(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute average of NULL object");
        return NULL;
    }

    // Handle empty vector case
    if ((self->obj->type == TYPE_I64 || self->obj->type == TYPE_F64) && self->obj->len == 0)
    {
        // Create a new RayObject for the result
        RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
        if (result == NULL)
        {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
            return NULL;
        }

        result->obj = f64(0.0);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create zero result");
            return NULL;
        }
        return (PyObject *)result;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's average operation directly
    result->obj = ray_avg(self->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform average operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Median operation for RayObject vectors
 */
static PyObject *RayObject_ray_med(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute median of NULL object");
        return NULL;
    }

    // Handle empty vector case
    if ((self->obj->type == TYPE_I64 || self->obj->type == TYPE_F64) && self->obj->len == 0)
    {
        // Create a new RayObject for the result
        RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
        if (result == NULL)
        {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
            return NULL;
        }

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
    if (self->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for median operation");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's median operation directly
    result->obj = ray_med(self->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform median operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Standard deviation operation for RayObject vectors
 */
static PyObject *RayObject_ray_dev(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute standard deviation of NULL object");
        return NULL;
    }

    // Handle empty vector case
    if ((self->obj->type == TYPE_I64 || self->obj->type == TYPE_F64) && self->obj->len == 0)
    {
        // Create a new RayObject for the result
        RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
        if (result == NULL)
        {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
            return NULL;
        }

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
    if (self->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for standard deviation operation");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's standard deviation operation directly
    result->obj = ray_dev(self->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform standard deviation operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Minimum value operation for RayObject vectors
 */
static PyObject *RayObject_ray_min(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute minimum of NULL object");
        return NULL;
    }

    // Handle empty vector case
    if ((self->obj->type == TYPE_I64 || self->obj->type == TYPE_F64) && self->obj->len == 0)
    {
        // Create a new RayObject for the result
        RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
        if (result == NULL)
        {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
            return NULL;
        }

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
    if (self->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for minimum operation");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's minimum operation directly
    result->obj = ray_min(self->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform minimum operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Maximum value operation for RayObject vectors
 */
static PyObject *RayObject_ray_max(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot compute maximum of NULL object");
        return NULL;
    }

    // Handle empty vector case
    if ((self->obj->type == TYPE_I64 || self->obj->type == TYPE_F64) && self->obj->len == 0)
    {
        // Create a new RayObject for the result
        RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
        if (result == NULL)
        {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
            return NULL;
        }

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
    if (self->obj->type == TYPE_F64)
    {
        PyErr_SetString(PyExc_TypeError, "F64 vectors are not supported for maximum operation");
        return NULL;
    }

    // Create a new RayObject for the result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call rayforce's maximum operation directly
    result->obj = ray_max(self->obj);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to perform maximum operation");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Evaluate a Rayforce expression
 */
static PyObject *RayObject_ray_eval(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Cannot evaluate NULL object");
        return NULL;
    }

    if (self->obj->type != TYPE_C8)
    {
        PyErr_SetString(PyExc_TypeError, "Object must be a string (TYPE_C8) for evaluation");
        return NULL;
    }

    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    result->obj = ray_eval_str(self->obj, NULL);
    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate expression");
        return NULL;
    }

    return (PyObject *)result;
}

/*
 * Get error message from an error object
 */
static PyObject *RayObject_get_error_message(RayObject *self, PyObject *args)
{
    if (self->obj == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Object is NULL");
        return NULL;
    }

    if (self->obj->type != TYPE_ERR)
    {
        PyErr_SetString(PyExc_TypeError, "Object is not an error type");
        return NULL;
    }

    ray_error_p err = AS_ERROR(self->obj);

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

// Методы RayObject
static PyMethodDef RayObject_methods[] = {
    // Integer methods
    {"from_i16", (PyCFunction)RayObject_from_i16, METH_VARARGS | METH_CLASS,
     "Create a new i16 object"},
    {"from_i32", (PyCFunction)RayObject_from_i32, METH_VARARGS | METH_CLASS,
     "Create a new i32 object"},
    {"from_i64", (PyCFunction)RayObject_from_i64, METH_VARARGS | METH_CLASS,
     "Create a new i64 object"},
    {"get_i16_value", (PyCFunction)RayObject_get_i16_value, METH_NOARGS,
     "Get the i16 value"},
    {"get_i32_value", (PyCFunction)RayObject_get_i32_value, METH_NOARGS,
     "Get the i32 value"},
    {"get_i64_value", (PyCFunction)RayObject_get_i64_value, METH_NOARGS,
     "Get the i64 value"},

    // Float methods
    {"from_f64", (PyCFunction)RayObject_from_f64, METH_VARARGS | METH_CLASS,
     "Create a new f64 (double) object"},
    {"get_f64_value", (PyCFunction)RayObject_get_f64_value, METH_NOARGS,
     "Get the f64 (double) value"},

    // String methods
    {"from_c8", (PyCFunction)RayObject_from_c8, METH_VARARGS | METH_CLASS,
     "Create a new c8 (character) object"},
    {"get_c8_value", (PyCFunction)RayObject_get_c8_value, METH_NOARGS,
     "Get the c8 (character) value"},
    {"from_string", (PyCFunction)RayObject_from_string, METH_VARARGS | METH_CLASS,
     "Create a new string from a Python string"},
    {"get_string_value", (PyCFunction)RayObject_get_string_value, METH_NOARGS,
     "Get the string value"},
    {"get_string_length", (PyCFunction)RayObject_get_string_length, METH_NOARGS,
     "Get the length of the string"},
    {"get_string_char", (PyCFunction)RayObject_get_string_char, METH_VARARGS,
     "Get the character at the specified index in the string"},
    {"is_string", (PyCFunction)RayObject_is_string, METH_NOARGS,
     "Check if the object is a string"},
    {"is_c8", (PyCFunction)RayObject_is_c8, METH_NOARGS,
     "Check if the object is a c8 (character)"},

    // Symbol methods
    {"from_symbol", (PyCFunction)RayObject_from_symbol, METH_VARARGS | METH_CLASS,
     "Create a new symbol from a string"},
    {"from_symbol_id", (PyCFunction)RayObject_from_symbol_id, METH_VARARGS | METH_CLASS,
     "Create a new symbol from an integer ID"},
    {"get_symbol_value", (PyCFunction)RayObject_get_symbol_value, METH_NOARGS,
     "Get the symbol value as a string"},
    {"get_symbol_id", (PyCFunction)RayObject_get_symbol_id, METH_NOARGS,
     "Get the symbol ID"},
    {"is_symbol", (PyCFunction)RayObject_is_symbol, METH_NOARGS,
     "Check if the object is a symbol"},

    // List methods
    {"create_list", (PyCFunction)RayObject_create_list, METH_VARARGS | METH_CLASS,
     "Create a new list with optional initial size"},
    {"list_length", (PyCFunction)RayObject_list_length, METH_NOARGS,
     "Get the length of the list"},
    {"list_append", (PyCFunction)RayObject_list_append, METH_VARARGS,
     "Append an item to the list"},
    {"list_get_item", (PyCFunction)RayObject_list_get_item, METH_VARARGS,
     "Get an item from the list by index"},
    {"list_set_item", (PyCFunction)RayObject_list_set_item, METH_VARARGS,
     "Set an item in the list at the given index"},
    {"list_remove_item", (PyCFunction)RayObject_list_remove_item, METH_VARARGS,
     "Remove an item from the list at the given index"},
    {"is_list", (PyCFunction)RayObject_is_list, METH_NOARGS,
     "Check if the object is a list"},

    // Common methods
    {"get_type", (PyCFunction)RayObject_get_type, METH_NOARGS,
     "Get the type of the object"},

    // B8 methods
    {"from_b8", (PyCFunction)RayObject_from_b8, METH_VARARGS | METH_CLASS,
     "Create a new B8 object from a Python boolean"},
    {"get_b8_value", (PyCFunction)RayObject_get_b8_value, METH_NOARGS,
     "Get the value of a B8 object"},

    // U8 methods
    {"from_u8", (PyCFunction)RayObject_from_u8, METH_VARARGS | METH_CLASS,
     "Create a new U8 object from a Python integer"},
    {"get_u8_value", (PyCFunction)RayObject_get_u8_value, METH_NOARGS,
     "Get the value of a U8 object"},

    // DATE methods
    {"from_date", (PyCFunction)RayObject_from_date, METH_VARARGS | METH_CLASS,
     "Create a new DATE object from a Python integer (days since epoch)"},
    {"get_date_value", (PyCFunction)RayObject_get_date_value, METH_NOARGS,
     "Get the date value (days since epoch) from a DATE object"},

    // TIME methods
    {"from_time", (PyCFunction)RayObject_from_time, METH_VARARGS | METH_CLASS,
     "Create a new TIME object from a Python integer (milliseconds since midnight)"},
    {"get_time_value", (PyCFunction)RayObject_get_time_value, METH_NOARGS,
     "Get the time value (milliseconds since midnight) from a TIME object"},

    // TIMESTAMP methods
    {"from_timestamp", (PyCFunction)RayObject_from_timestamp, METH_VARARGS | METH_CLASS,
     "Create a new TIMESTAMP object from a Python integer (milliseconds since epoch)"},
    {"get_timestamp_value", (PyCFunction)RayObject_get_timestamp_value, METH_NOARGS,
     "Get the timestamp value (milliseconds since epoch) from a TIMESTAMP object"},

    // GUID methods
    {"from_guid", (PyCFunction)RayObject_from_guid, METH_VARARGS | METH_CLASS,
     "Create a new GUID object from a Python bytes/bytearray object"},
    {"get_guid_value", (PyCFunction)RayObject_get_guid_value, METH_NOARGS,
     "Get the GUID value as bytes from a GUID object"},
    {"is_guid", (PyCFunction)RayObject_is_guid, METH_NOARGS,
     "Check if the object is a GUID"},
    {"is_vector", (PyCFunction)RayObject_is_vector, METH_NOARGS,
     "Check if the object is a vector (has a positive type)"},
    {"get_vector_type", (PyCFunction)RayObject_get_vector_type, METH_NOARGS,
     "Get the type code of a vector"},

    // TABLE methods
    {"create_table", (PyCFunction)RayObject_create_table, METH_VARARGS | METH_CLASS,
     "Create a new TABLE object from keys and values lists"},
    {"table_get", (PyCFunction)RayObject_table_get, METH_VARARGS,
     "Get a value from a TABLE by key"},
    {"is_table", (PyCFunction)RayObject_is_table, METH_NOARGS,
     "Check if the object is a TABLE"},
    {"table_keys", (PyCFunction)RayObject_table_keys, METH_NOARGS,
     "Get keys from a table"},
    {"table_values", (PyCFunction)RayObject_table_values, METH_NOARGS,
     "Get values from a table"},

    // DICT methods
    {"create_dict", (PyCFunction)RayObject_create_dict, METH_VARARGS | METH_CLASS,
     "Create a new DICT object from keys and values lists"},
    {"dict_keys", (PyCFunction)RayObject_dict_keys, METH_NOARGS,
     "Get all keys from a DICT"},
    {"dict_values", (PyCFunction)RayObject_dict_values, METH_NOARGS,
     "Get all values from a DICT"},
    {"is_dict", (PyCFunction)RayObject_is_dict, METH_NOARGS,
     "Check if the object is a DICT"},
    {"dict_get", (PyCFunction)RayObject_dict_get, METH_VARARGS,
     "Get a value from a DICT by key"},
    {"dict_length", (PyCFunction)RayObject_dict_length, METH_NOARGS,
     "Get the number of items in a DICT"},

    // Vector methods
    {"vector", (PyCFunction)RayObject_vector, METH_VARARGS | METH_CLASS,
     "Create a new vector of specified type and length"},
    {"at_idx", (PyCFunction)RayObject_at_idx, METH_VARARGS,
     "Get element at index from vector"},
    {"set_idx", (PyCFunction)RayObject_set_idx, METH_VARARGS,
     "Set element at index in vector"},

    // Get vector length
    {"get_vector_length", (PyCFunction)RayObject_get_vector_length, METH_NOARGS,
     "Get the length of a vector"},

    // Addition method
    {"ray_add", (PyCFunction)RayObject_ray_add, METH_VARARGS,
     "Add two RayObjects"},

    // Subtraction method
    {"ray_sub", (PyCFunction)RayObject_ray_sub, METH_VARARGS,
     "Subtract two RayObjects"},

    // Multiplication method
    {"ray_mul", (PyCFunction)RayObject_ray_mul, METH_VARARGS,
     "Multiply two RayObjects"},

    // Division method
    {"ray_div", (PyCFunction)RayObject_ray_div, METH_VARARGS,
     "Divide two RayObjects"},

    // Floating-point division method
    {"ray_fdiv", (PyCFunction)RayObject_ray_fdiv, METH_VARARGS,
     "Perform floating-point division of two RayObjects"},

    // Modulo method
    {"ray_mod", (PyCFunction)RayObject_ray_mod, METH_VARARGS,
     "Perform modulo operation on two RayObjects"},

    // Sum method
    {"ray_sum", (PyCFunction)RayObject_ray_sum, METH_VARARGS,
     "Sum all elements in a vector"},

    // Average method
    {"ray_avg", (PyCFunction)RayObject_ray_avg, METH_VARARGS,
     "Compute the average of a vector or scalar"},

    // Median method
    {"ray_med", (PyCFunction)RayObject_ray_med, METH_VARARGS,
     "Compute the median of a vector or scalar"},

    // Standard deviation method
    {"ray_dev", (PyCFunction)RayObject_ray_dev, METH_VARARGS,
     "Compute the standard deviation of a vector or scalar"},

    // Minimum method
    {"ray_min", (PyCFunction)RayObject_ray_min, METH_VARARGS,
     "Compute the minimum value of a vector or scalar"},

    // Maximum method
    {"ray_max", (PyCFunction)RayObject_ray_max, METH_VARARGS,
     "Compute the maximum value of a vector or scalar"},

    // Eval method
    {"ray_eval", (PyCFunction)RayObject_ray_eval, METH_NOARGS,
     "Evaluate a Rayforce expression"},

    // Error handling
    {"get_error_message", (PyCFunction)RayObject_get_error_message, METH_NOARGS,
     "Get the error message from an error object"},

    {NULL, NULL, 0, NULL}};

// Define the RayObject type
static PyTypeObject RayObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_rayforce.RayObject",
    .tp_basicsize = sizeof(RayObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)RayObject_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "RayObject objects",
    .tp_methods = RayObject_methods,
    .tp_new = PyType_GenericNew,
};

// List of module methods
static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}};

// Define the module
static struct PyModuleDef rayforce_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_rayforce",
    .m_doc = "Python interface to Rayforce",
    .m_size = -1,
    .m_methods = module_methods,
};

// Module initialization function
PyMODINIT_FUNC PyInit__rayforce(void)
{
    PyObject *m;

    // Prepare RayObjectType
    if (PyType_Ready(&RayObjectType) < 0)
        return NULL;

    // Prepare python module from rayforce_module description
    m = PyModule_Create(&rayforce_module);
    if (m == NULL)
        return NULL;

    // Init reference counter for RayObjectType
    Py_INCREF(&RayObjectType);

    // Make RayObjectType accessible from .RayObject
    if (PyModule_AddObject(m, "RayObject", (PyObject *)&RayObjectType) < 0)
    {
        Py_DECREF(&RayObjectType);
        Py_DECREF(m);
        return NULL;
    }

    // Export Ray type constants to Python
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

    // Initialize the Rayforce runtime
    if (ray_init() != 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize Rayforce");
        return NULL;
    }

    return m;
}
