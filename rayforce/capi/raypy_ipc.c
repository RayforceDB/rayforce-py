/*
 * raypy_ipc.c — Python wrappers for v2's native IPC.
 *
 * Client side (rayforce.h public API): ray_ipc_connect / ray_ipc_send /
 * ray_ipc_send_async / ray_ipc_close.
 *
 * Server side (core/ipc.h + core/poll.h): the server owns a dedicated poll
 * with an IPC listener registered on it (ray_poll_create / ray_ipc_listen),
 * handed to Python as an integer pointer. Python drives the loop with bounded
 * ray_poll_run_for passes so Ctrl-C and Python-level cancellation work
 * naturally; ray_poll_destroy tears the listener and its connections down.
 */

#include "core/ipc.h"
#include "core/poll.h"
#include "core/runtime.h"
#include "rayforce_c.h"

/* ---- Client ---- */

static int ensure_runtime_poll(void) {
  if (ray_runtime_get_poll() != NULL)
    return 0;
  ray_poll_t *poll = ray_poll_create();
  if (poll == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "ipc: failed to create poll");
    return -1;
  }
  ray_runtime_set_poll(poll);
  return 0;
}

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

  if (ensure_runtime_poll() < 0)
    return NULL;

  /* timeout_ms <= 0 uses the core's default connect/handshake budget,
   * preserving the pre-timeout behavior of this binding. */
  int64_t handle = ray_ipc_connect(host, (uint16_t)port, user, password, 0);
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

/* ---- Server (poll-based API) ---- */

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

  ray_poll_t *poll = ray_poll_create();
  if (poll == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "ipc: failed to create poll");
    return NULL;
  }

  if (ray_ipc_listen(poll, (uint16_t)port) < 0) {
    ray_poll_destroy(poll);
    PyErr_Format(PyExc_RuntimeError, "ipc: server bind on :%d failed", port);
    return NULL;
  }
  return PyLong_FromVoidPtr(poll);
}

PyObject *raypy_ipc_server_poll(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  unsigned long long srv_addr;
  int timeout_ms;
  if (!PyArg_ParseTuple(args, "Ki", &srv_addr, &timeout_ms))
    return NULL;

  /* One bounded pass: serves whatever is ready within timeout_ms, then
   * returns to Python so the loop stays interruptible. */
  int64_t rc = ray_poll_run_for((ray_poll_t *)(uintptr_t)srv_addr, timeout_ms);
  return PyLong_FromLongLong((long long)rc);
}

PyObject *raypy_ipc_server_destroy(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  unsigned long long srv_addr;
  if (!PyArg_ParseTuple(args, "K", &srv_addr))
    return NULL;

  ray_poll_t *poll = (ray_poll_t *)(uintptr_t)srv_addr;
  if (poll != NULL)
    ray_poll_destroy(poll);
  Py_RETURN_NONE;
}
