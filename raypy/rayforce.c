#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <string.h>
#include "./core/rayforce.h"

// Forward declaration for memcpy if needed
#ifndef memcpy
extern void *memcpy(void *dest, const void *src, size_t n);
#endif

// Forward declaration of RayObjectType
static PyTypeObject RayObjectType;


typedef struct {
    PyObject_HEAD obj_p obj;
} RayObject;


// Deallocator for RayObject
static void RayObject_dealloc(RayObject* self) {
    if (self->obj != NULL) {
        self->obj->rc--;
        if (self->obj->rc == 0) {
            drop_obj(self->obj);
        }
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

// INTEGERS GETTERS / SETTERS {{
static PyObject* RayObject_from_i16(PyTypeObject* type, PyObject* args) {
    short value;
    if (!PyArg_ParseTuple(args, "h", &value)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = i16(value);
    }
    return (PyObject*)self;
}
static PyObject* RayObject_from_i32(PyTypeObject* type, PyObject* args) {
    int value;
    if (!PyArg_ParseTuple(args, "i", &value)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = i32(value);
    }
    return (PyObject*)self;
}
static PyObject* RayObject_from_i64(PyTypeObject* type, PyObject* args) {
    long long value;
    if (!PyArg_ParseTuple(args, "L", &value)) {
        return NULL;
    }
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = i64(value);
    }
    return (PyObject*)self;
}
static PyObject* RayObject_get_i16_value(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != -TYPE_I16) {
        PyErr_SetString(PyExc_TypeError, "Object is not an i16");
        return NULL;
    }
    return PyLong_FromLong(self->obj->i16);
}
static PyObject* RayObject_get_i32_value(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != -TYPE_I32) {
        PyErr_SetString(PyExc_TypeError, "Object is not an i32");
        return NULL;
    }
    return PyLong_FromLong(self->obj->i32);
}
static PyObject* RayObject_get_i64_value(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != -TYPE_I64) {
        PyErr_SetString(PyExc_TypeError, "Object is not an i64");
        return NULL;
    }
    return PyLong_FromLongLong(self->obj->i64);
}
// }}

// FLOAT GETTERS / SETTERS {{
static PyObject* RayObject_from_f64(PyTypeObject* type, PyObject* args) {
    double value;
    if (!PyArg_ParseTuple(args, "d", &value)) {
        return NULL;
    }
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = f64(value);
    }
    return (PyObject*)self;
}

static PyObject* RayObject_get_f64_value(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != -TYPE_F64) {
        PyErr_SetString(PyExc_TypeError, "Object is not an f64");
        return NULL;
    }
    return PyFloat_FromDouble(self->obj->f64);
}
// }}

// STRING OPERATIONS {{
// Create a character (c8)
static PyObject* RayObject_from_c8(PyTypeObject* type, PyObject* args) {
    const char* value;
    Py_ssize_t len;
    
    if (!PyArg_ParseTuple(args, "s#", &value, &len)) {
        return NULL;
    }
    
    if (len != 1) {
        PyErr_SetString(PyExc_ValueError, "Character must be a single character");
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = c8(value[0]);
    }
    return (PyObject*)self;
}

// Get character value
static PyObject* RayObject_get_c8_value(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != -TYPE_C8) {
        PyErr_SetString(PyExc_TypeError, "Object is not a c8");
        return NULL;
    }
    return PyUnicode_FromStringAndSize(&self->obj->c8, 1);
}

// Create a string from a Python string
static PyObject* RayObject_from_string(PyTypeObject* type, PyObject* args) {
    const char* value;
    Py_ssize_t len;
    
    if (!PyArg_ParseTuple(args, "s#", &value, &len)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        // Create a vector of TYPE_C8 with the right length
        self->obj = vector(TYPE_C8, len);
        if (self->obj == NULL) {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create string");
            return NULL;
        }
        
        // Copy the string data
        memcpy(AS_C8(self->obj), value, len);
    }
    return (PyObject*)self;
}

// Get string value
static PyObject* RayObject_get_string_value(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != TYPE_C8) {
        PyErr_SetString(PyExc_TypeError, "Object is not a string");
        return NULL;
    }
    
    return PyUnicode_FromStringAndSize(AS_C8(self->obj), self->obj->len);
}

// Get string length
static PyObject* RayObject_get_string_length(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != TYPE_C8) {
        PyErr_SetString(PyExc_TypeError, "Object is not a string");
        return NULL;
    }
    
    return PyLong_FromUnsignedLongLong(self->obj->len);
}

// Get character at index
static PyObject* RayObject_get_string_char(RayObject* self, PyObject* args) {
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index)) {
        return NULL;
    }
    
    if (self->obj == NULL || self->obj->type != TYPE_C8) {
        PyErr_SetString(PyExc_TypeError, "Object is not a string");
        return NULL;
    }
    
    if (index < 0 || index >= (Py_ssize_t)self->obj->len) {
        PyErr_SetString(PyExc_IndexError, "String index out of range");
        return NULL;
    }
    
    char c = AS_C8(self->obj)[index];
    return PyUnicode_FromStringAndSize(&c, 1);
}

// Check if object is a string
static PyObject* RayObject_is_string(RayObject* self, PyObject* args) {
    if (self->obj == NULL) {
        Py_RETURN_FALSE;
    }
    
    if (self->obj->type == TYPE_C8) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

// Check if object is a character
static PyObject* RayObject_is_c8(RayObject* self, PyObject* args) {
    if (self->obj == NULL) {
        Py_RETURN_FALSE;
    }
    
    if (self->obj->type == -TYPE_C8) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}
// }}

// SYMBOL OPERATIONS {{
// Create a symbol from a string
static PyObject* RayObject_from_symbol(PyTypeObject* type, PyObject* args) {
    const char* value;
    Py_ssize_t len;
    
    if (!PyArg_ParseTuple(args, "s#", &value, &len)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = symbol(value, len);
        if (self->obj == NULL) {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create symbol");
            return NULL;
        }
    }
    return (PyObject*)self;
}

// Create a symbol from an integer ID
static PyObject* RayObject_from_symbol_id(PyTypeObject* type, PyObject* args) {
    long long id;
    
    if (!PyArg_ParseTuple(args, "L", &id)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = symboli64(id);
        if (self->obj == NULL) {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create symbol from ID");
            return NULL;
        }
    }
    return (PyObject*)self;
}

// Get symbol string value
static PyObject* RayObject_get_symbol_value(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != -TYPE_SYMBOL) {
        PyErr_SetString(PyExc_TypeError, "Object is not a symbol");
        return NULL;
    }
    
    // Get the symbol ID
    i64_t symbol_id = self->obj->i64;
    
    // Get the string representation
    const char* str = str_from_symbol(symbol_id);
    if (str == NULL) {
        Py_RETURN_NONE;
    }
    
    return PyUnicode_FromString(str);
}

// Get symbol ID value
static PyObject* RayObject_get_symbol_id(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != -TYPE_SYMBOL) {
        PyErr_SetString(PyExc_TypeError, "Object is not a symbol");
        return NULL;
    }
    
    return PyLong_FromLongLong(self->obj->i64);
}

// Check if object is a symbol
static PyObject* RayObject_is_symbol(RayObject* self, PyObject* args) {
    if (self->obj == NULL) {
        Py_RETURN_FALSE;
    }
    
    if (self->obj->type == -TYPE_SYMBOL) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}
// }}

// LIST OPERATIONS {{
// Create an empty list
static PyObject* RayObject_create_list(PyTypeObject* type, PyObject* args) {
    Py_ssize_t initial_size = 0;
    if (!PyArg_ParseTuple(args, "|n", &initial_size)) {
        return NULL;
    }
    
    if (initial_size < 0) {
        PyErr_SetString(PyExc_ValueError, "List size cannot be negative");
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = vector(TYPE_LIST, (u64_t)initial_size);
        if (self->obj == NULL) {
            Py_DECREF(self);
            PyErr_SetString(PyExc_MemoryError, "Failed to create list");
            return NULL;
        }
    }
    return (PyObject*)self;
}

// Get list length
static PyObject* RayObject_list_length(RayObject* self, PyObject* args) {
    if (self->obj == NULL || self->obj->type != TYPE_LIST) {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }
    
    return PyLong_FromUnsignedLongLong(self->obj->len);
}

// Append an item to the list
static PyObject* RayObject_list_append(RayObject* self, PyObject* args) {
    RayObject* item;
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item)) {
        return NULL;
    }
    
    if (self->obj == NULL || self->obj->type != TYPE_LIST) {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }
    
    // We need to clone the item since push_obj will own the object
    obj_p clone = clone_obj(item->obj);
    if (clone == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }
    
    // Push the item to the list
    if (push_obj(&self->obj, clone) == NULL) {
        // If push_obj fails, we need to free the clone
        drop_obj(clone);
        PyErr_SetString(PyExc_RuntimeError, "Failed to append item to list");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

// Get item at index
static PyObject* RayObject_list_get_item(RayObject* self, PyObject* args) {
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index)) {
        return NULL;
    }
    
    if (self->obj == NULL || self->obj->type != TYPE_LIST) {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }
    
    if (index < 0 || index >= (Py_ssize_t)self->obj->len) {
        PyErr_SetString(PyExc_IndexError, "List index out of range");
        return NULL;
    }
    
    // Get the item at the index
    obj_p item = at_idx(self->obj, (i64_t)index);
    if (item == NULL) {
        Py_RETURN_NONE;
    }
    
    // Create a new RayObject with the item
    RayObject* result = (RayObject*)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }
    
    // We need to clone the item since it's owned by the list
    result->obj = clone_obj(item);
    if (result->obj == NULL) {
        Py_DECREF(result);
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }
    
    return (PyObject*)result;
}

// Set item at index
static PyObject* RayObject_list_set_item(RayObject* self, PyObject* args) {
    Py_ssize_t index;
    RayObject* item;
    if (!PyArg_ParseTuple(args, "nO!", &index, &RayObjectType, &item)) {
        return NULL;
    }
    
    if (self->obj == NULL || self->obj->type != TYPE_LIST) {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }
    
    if (index < 0 || index >= (Py_ssize_t)self->obj->len) {
        PyErr_SetString(PyExc_IndexError, "List index out of range");
        return NULL;
    }
    
    // Clone the item
    obj_p clone = clone_obj(item->obj);
    if (clone == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
        return NULL;
    }
    
    // Set the item at the index
    if (set_idx(&self->obj, (i64_t)index, clone) == NULL) {
        // If set_idx fails, we need to free the clone
        drop_obj(clone);
        PyErr_SetString(PyExc_RuntimeError, "Failed to set item in list");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

// Remove item at index
static PyObject* RayObject_list_remove_item(RayObject* self, PyObject* args) {
    Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "n", &index)) {
        return NULL;
    }
    
    if (self->obj == NULL || self->obj->type != TYPE_LIST) {
        PyErr_SetString(PyExc_TypeError, "Object is not a list");
        return NULL;
    }
    
    if (index < 0 || index >= (Py_ssize_t)self->obj->len) {
        PyErr_SetString(PyExc_IndexError, "List index out of range");
        return NULL;
    }
    
    // Remove the item at the index
    if (remove_idx(&self->obj, (i64_t)index) == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to remove item from list");
        return NULL;
    }
    
    Py_RETURN_NONE;
}

// Check if object is a list
static PyObject* RayObject_is_list(RayObject* self, PyObject* args) {
    if (self->obj == NULL) {
        Py_RETURN_FALSE;
    }
    
    if (self->obj->type == TYPE_LIST) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}
// }}

// Get object type (references are in rayforce.h)
static PyObject* RayObject_get_type(RayObject* self, PyObject* args) {
    if (self->obj == NULL) {
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
RayObject_from_b8(PyTypeObject* type, PyObject* args)
{
    int bool_value;
    
    if (!PyArg_ParseTuple(args, "p", &bool_value)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = b8(bool_value ? 1 : 0);
    }
    return (PyObject*)self;
}

// Get the boolean value from a RayObject of B8 type
static PyObject *
RayObject_get_b8_value(RayObject* self, PyObject* args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_B8) {
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
RayObject_from_u8(PyTypeObject* type, PyObject* args)
{
    unsigned char byte_value;
    
    if (!PyArg_ParseTuple(args, "b", &byte_value)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = u8(byte_value);
    }
    return (PyObject*)self;
}

// Get the unsigned 8-bit integer value from a RayObject of U8 type
static PyObject *
RayObject_get_u8_value(RayObject* self, PyObject* args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_U8) {
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
RayObject_from_date(PyTypeObject* type, PyObject* args)
{
    int days_value;
    
    if (!PyArg_ParseTuple(args, "i", &days_value)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = adate(days_value);
    }
    return (PyObject*)self;
}

// Get the date value (days since epoch) from a RayObject of DATE type
static PyObject *
RayObject_get_date_value(RayObject* self, PyObject* args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_DATE) {
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
RayObject_from_time(PyTypeObject* type, PyObject* args)
{
    int ms_value;
    
    if (!PyArg_ParseTuple(args, "i", &ms_value)) {
        return NULL;
    }
    
    // Check if the value is within the valid range (0-86399999 milliseconds in a day)
    if (ms_value < 0 || ms_value > 86399999) {
        PyErr_SetString(PyExc_ValueError, "Time value must be in range 0-86399999 milliseconds");
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = atime(ms_value);
    }
    return (PyObject*)self;
}

// Get the time value (milliseconds since midnight) from a RayObject of TIME type
static PyObject *
RayObject_get_time_value(RayObject* self, PyObject* args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_TIME) {
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
RayObject_from_timestamp(PyTypeObject* type, PyObject* args)
{
    long long ms_value;
    
    if (!PyArg_ParseTuple(args, "L", &ms_value)) {
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = timestamp(ms_value);
    }
    return (PyObject*)self;
}

// Get the timestamp value (milliseconds since epoch) from a RayObject of TIMESTAMP type
static PyObject *
RayObject_get_timestamp_value(RayObject* self, PyObject* args)
{
    if (self->obj == NULL || self->obj->type != -TYPE_TIMESTAMP) {
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
RayObject_from_guid(PyTypeObject* type, PyObject* args)
{
    Py_buffer buffer;
    
    if (!PyArg_ParseTuple(args, "y*", &buffer)) {
        return NULL;
    }
    
    // Check if the buffer size is 16 bytes (standard GUID size)
    if (buffer.len != 16) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_ValueError, "GUID must be exactly 16 bytes");
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        // Create a GUID object and copy the bytes
        self->obj = vector(TYPE_GUID, 16);
        if (self->obj == NULL) {
            Py_DECREF(self);
            PyBuffer_Release(&buffer);
            PyErr_SetString(PyExc_MemoryError, "Failed to create GUID");
            return NULL;
        }
        
        // Copy the GUID data
        memcpy(self->obj->arr, buffer.buf, 16);
    }
    
    // Release the buffer
    PyBuffer_Release(&buffer);
    
    return (PyObject*)self;
}

// Get the GUID value as bytes from a RayObject of GUID type
static PyObject *
RayObject_get_guid_value(RayObject* self, PyObject* args)
{
    if (self->obj == NULL || self->obj->type != TYPE_GUID) {
        PyErr_SetString(PyExc_TypeError, "Object is not a GUID type");
        return NULL;
    }
    
    return PyBytes_FromStringAndSize((const char*)self->obj->arr, 16);
}

// Check if object is a GUID
static PyObject* RayObject_is_guid(RayObject* self, PyObject* args)
{
    if (self->obj == NULL) {
        Py_RETURN_FALSE;
    }
    
    if (self->obj->type == TYPE_GUID) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

/*
 * TABLE type handling functions
 */

// Create a table from keys and values lists
static PyObject *
RayObject_create_table(PyTypeObject* type, PyObject* args)
{
    RayObject* keys_obj;
    RayObject* vals_obj;
    
    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType, &vals_obj)) {
        return NULL;
    }
    
    // Check that inputs are lists
    if (keys_obj->obj == NULL || keys_obj->obj->type != TYPE_LIST) {
        PyErr_SetString(PyExc_TypeError, "Keys must be a list");
        return NULL;
    }
    
    if (vals_obj->obj == NULL || vals_obj->obj->type != TYPE_LIST) {
        PyErr_SetString(PyExc_TypeError, "Values must be a list");
        return NULL;
    }
    
    // Check that lists have the same length
    if (keys_obj->obj->len != vals_obj->obj->len) {
        PyErr_SetString(PyExc_ValueError, "Keys and values lists must have the same length");
        return NULL;
    }
    
    RayObject* self = (RayObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->obj = table(keys_obj->obj, vals_obj->obj);
        if (self->obj == NULL) {
            Py_DECREF(self);
            PyErr_SetString(PyExc_RuntimeError, "Failed to create table");
            return NULL;
        }
    }
    
    return (PyObject*)self;
}

// Get a value from a table by key
static PyObject *
RayObject_table_get(RayObject* self, PyObject* args)
{
    RayObject* key_obj;
    
    if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &key_obj)) {
        return NULL;
    }
    
    if (self->obj == NULL || self->obj->type != TYPE_TABLE) {
        PyErr_SetString(PyExc_TypeError, "Object is not a TABLE type");
        return NULL;
    }
    
    obj_p result = at_obj(self->obj, key_obj->obj);
    if (result == NULL) {
        PyErr_SetString(PyExc_KeyError, "Key not found in table");
        return NULL;
    }
    
    // Create a new RayObject to wrap the result
    RayObject* ray_result = (RayObject*)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (ray_result != NULL) {
        ray_result->obj = result;
    }
    
    return (PyObject*)ray_result;
}

// Check if object is a table
static PyObject* 
RayObject_is_table(RayObject* self, PyObject* args)
{
    if (self->obj == NULL) {
        Py_RETURN_FALSE;
    }
    
    if (self->obj->type == TYPE_TABLE) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
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
     
    // TABLE methods
    {"create_table", (PyCFunction)RayObject_create_table, METH_VARARGS | METH_CLASS,
     "Create a new TABLE object from keys and values lists"},
    {"table_get", (PyCFunction)RayObject_table_get, METH_VARARGS,
     "Get a value from a TABLE by key"},
    {"is_table", (PyCFunction)RayObject_is_table, METH_NOARGS,
     "Check if the object is a TABLE"},
     
    {NULL, NULL, 0, NULL}
};


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
    {NULL, NULL, 0, NULL}
};


// Define the module
static struct PyModuleDef rayforce_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_rayforce",
    .m_doc = "Python interface to Rayforce",
    .m_size = -1,
    .m_methods = module_methods,
};


// Module initialization function
PyMODINIT_FUNC PyInit__rayforce(void) {
    PyObject* m;

    // Prepare RayObjectType
    if (PyType_Ready(&RayObjectType) < 0) return NULL;

    // Prepare python module from rayforce_module description
    m = PyModule_Create(&rayforce_module); if (m == NULL) return NULL;

    // Init reference counter for RayObjectType
    Py_INCREF(&RayObjectType);

    // Make RayObjectType accessible from .RayObject
    if (PyModule_AddObject(m, "RayObject", (PyObject*)&RayObjectType) < 0) {
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
    if (ray_init() != 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize Rayforce");
        return NULL;
    }

    return m;
}
