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
        result->obj = lambda(args_obj->obj, body_obj->obj, nfo_ptr);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to create lambda");
            return NULL;
        }
    }
    return (PyObject *)result;
}
static PyObject *raypy_lambda_call(PyObject *self, PyObject *args)
{
    (void)self;
    RayObject *lambda_obj;
    PyObject *py_args_list;

    if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &lambda_obj, &PyList_Type, &py_args_list))
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

    // Convert Python list to array of RayObjects
    Py_ssize_t arg_count = PyList_Size(py_args_list);
    if (arg_count < 0)
    {
        return NULL;
    }

    obj_p *ray_args = NULL;
    if (arg_count > 0)
    {
        ray_args = malloc(sizeof(obj_p) * arg_count);
        if (!ray_args)
        {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate arguments array");
            return NULL;
        }

        for (Py_ssize_t i = 0; i < arg_count; i++)
        {
            PyObject *py_arg = PyList_GetItem(py_args_list, i);
            if (!PyObject_IsInstance(py_arg, (PyObject *)&RayObjectType))
            {
                free(ray_args);
                PyErr_SetString(PyExc_TypeError, "All arguments must be RayObject instances");
                return NULL;
            }

            RayObject *ray_arg = (RayObject *)py_arg;
            if (ray_arg->obj == NULL)
            {
                free(ray_args);
                PyErr_SetString(PyExc_ValueError, "Argument object cannot be NULL");
                return NULL;
            }

            ray_args[i] = ray_arg->obj;
        }
    }

    // Allocate memory for result
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result == NULL)
    {
        if (ray_args) free(ray_args);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate result object");
        return NULL;
    }

    // Call the lambda function
    result->obj = lambda_call(lambda_obj->obj, ray_args, (i64_t)arg_count);
    
    // Cleanup
    if (ray_args) free(ray_args);

    if (result->obj == NULL)
    {
        Py_DECREF(result);
        PyErr_SetString(PyExc_RuntimeError, "Failed to call lambda function");
        return NULL;
    }

    if (result->obj->type == TYPE_ERR)
    {
        return (PyObject *)result;
    }
    
    return (PyObject *)result;
}
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
static PyObject *raypy_lambda_get_nfo(PyObject *self, PyObject *args)
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
    
    if (lambda_data->nfo == NULL_OBJ || lambda_data->nfo == NULL)
    {
        Py_RETURN_NONE;
    }
    
    // Return the nfo (metadata)
    RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
    if (result != NULL)
    {
        result->obj = clone_obj(lambda_data->nfo);
        if (result->obj == NULL)
        {
            Py_DECREF(result);
            PyErr_SetString(PyExc_MemoryError, "Failed to clone lambda nfo");
            return NULL;
        }
    }
    
    return (PyObject *)result;
}
static PyObject *raypy_is_lambda(PyObject *self, PyObject *args)
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

    if (ray_obj->obj->type == TYPE_LAMBDA)
    {
        Py_RETURN_TRUE;
    }
    else
    {
        Py_RETURN_FALSE;
    }
}
// END MISC 

static PyMethodDef module_methods[] = {
    {"init_vector", raypy_init_vector, METH_VARARGS, "Create a new vector object"},
    {"init_lambda", raypy_init_lambda, METH_VARARGS, "Create a new lambda function"},
    
    // Readers
    {NULL, NULL, 0, NULL}
}; 