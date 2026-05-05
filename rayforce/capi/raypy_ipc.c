/*
 * raypy_ipc.c — Python wrappers for v2's native IPC.
 *
 * Client side (rayforce.h public API): ray_ipc_connect / ray_ipc_send /
 * ray_ipc_send_async / ray_ipc_close.
 *
 * Server side (core/ipc.h legacy API): ray_ipc_server_init / ray_ipc_poll /
 * ray_ipc_server_destroy. The struct is heap-allocated here and handed to
 * Python as an integer pointer; Python drives the poll loop so Ctrl-C and
 * Python-level cancellation work naturally.
 */

#include "rayforce_c.h"
#include "core/ipc.h"
#include <stdlib.h>

/* ---- Client ---- */

PyObject *raypy_ipc_connect(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  const char *host;
  int port;
  const char *user = "";
  const char *password = "";
  if (!PyArg_ParseTuple(args, "si|ss", &host, &port, &user, &password))
    return NULL;

  if (port < 1 || port > 65535) {
    PyErr_SetString(PyExc_ValueError, "ipc: port must be in 1..65535");
    return NULL;
  }

  int64_t handle = ray_ipc_connect(host, (uint16_t)port, user, password);
  if (handle < 0) {
    PyErr_Format(PyExc_RuntimeError, "ipc: connect to %s:%d failed", host,
                 port);
    return NULL;
  }
  return PyLong_FromLongLong((long long)handle);
}

PyObject *raypy_ipc_close(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  long long handle;
  if (!PyArg_ParseTuple(args, "L", &handle))
    return NULL;

  ray_ipc_close((int64_t)handle);
  Py_RETURN_NONE;
}

PyObject *raypy_ipc_send(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  long long handle;
  RayObject *msg;
  if (!PyArg_ParseTuple(args, "LO!", &handle, &RayObjectType, &msg))
    return NULL;

  ray_t *result = ray_ipc_send((int64_t)handle, msg->obj);
  if (result == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "ipc: send failed");
    return NULL;
  }
  /* RAY_ERROR is wrapped through; the Python error_handler maps the code. */
  return raypy_wrap_ray_object(result);
}

PyObject *raypy_ipc_send_async(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  long long handle;
  RayObject *msg;
  if (!PyArg_ParseTuple(args, "LO!", &handle, &RayObjectType, &msg))
    return NULL;

  ray_err_t err = ray_ipc_send_async((int64_t)handle, msg->obj);
  if (err != RAY_OK) {
    PyErr_Format(PyExc_RuntimeError, "ipc: send_async failed (%s)",
                 ray_err_code_str(err));
    return NULL;
  }
  Py_RETURN_NONE;
}

/* ---- Server (legacy blocking poll API) ---- */

PyObject *raypy_ipc_server_init(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int port;
  if (!PyArg_ParseTuple(args, "i", &port))
    return NULL;

  if (port < 1 || port > 65535) {
    PyErr_SetString(PyExc_ValueError, "ipc: port must be in 1..65535");
    return NULL;
  }

  ray_ipc_server_t *srv = calloc(1, sizeof(ray_ipc_server_t));
  if (srv == NULL)
    return PyErr_NoMemory();

  ray_err_t err = ray_ipc_server_init(srv, (uint16_t)port);
  if (err != RAY_OK) {
    free(srv);
    PyErr_Format(PyExc_RuntimeError, "ipc: server bind on :%d failed (%s)",
                 port, ray_err_code_str(err));
    return NULL;
  }
  return PyLong_FromVoidPtr(srv);
}

PyObject *raypy_ipc_server_poll(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  unsigned long long srv_addr;
  int timeout_ms;
  if (!PyArg_ParseTuple(args, "Ki", &srv_addr, &timeout_ms))
    return NULL;

  int n = ray_ipc_poll((ray_ipc_server_t *)(uintptr_t)srv_addr, timeout_ms);
  return PyLong_FromLong((long)n);
}

PyObject *raypy_ipc_server_destroy(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  unsigned long long srv_addr;
  if (!PyArg_ParseTuple(args, "K", &srv_addr))
    return NULL;

  ray_ipc_server_t *srv = (ray_ipc_server_t *)(uintptr_t)srv_addr;
  if (srv != NULL) {
    ray_ipc_server_destroy(srv);
    free(srv);
  }
  Py_RETURN_NONE;
}
