/*
 * raypy_kdb.c — CPython glue for the KDB+ IPC client.
 *
 * The wire-format core lives in the standalone `rayforce-q` repo (q.c/q.h),
 * shared across language bindings. This file is the thin Python layer: it
 * parses arguments, calls q_connect/q_close/q_send, and maps their return
 * codes / error strings onto Python exceptions. The blocking network round-trip
 * runs with the GIL released so other Python threads stay live.
 */

#include "rayforce_c.h"

#include "q.h"

PyObject *raypy_kdb_connect(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  const char *host;
  int port;
  const char *user = "";
  const char *password = "";
  int timeout_ms = 0;
  if (!PyArg_ParseTuple(args, "si|ssi", &host, &port, &user, &password,
                        &timeout_ms))
    return NULL;
  if (port < 1 || port > 65535) {
    PyErr_SetString(PyExc_ValueError, "kdb: port must be in 1..65535");
    return NULL;
  }

  int fd = q_connect(host, port, user, password, timeout_ms);
  if (fd < 0) {
    switch (fd) {
    case Q_ERR_TIMEOUT:
      PyErr_Format(PyExc_TimeoutError, "kdb: connect to %s:%d timed out", host,
                   port);
      break;
    case Q_ERR_HANDSHAKE:
      PyErr_SetString(PyExc_RuntimeError, "kdb: handshake/auth failed");
      break;
    default:
      PyErr_Format(PyExc_RuntimeError, "kdb: connect to %s:%d failed", host,
                   port);
      break;
    }
    return NULL;
  }
  return PyLong_FromLong(fd);
}

PyObject *raypy_kdb_close(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int fd;
  if (!PyArg_ParseTuple(args, "i", &fd))
    return NULL;
  if (q_close(fd) < 0) {
    PyErr_SetString(PyExc_RuntimeError, "kdb: invalid handle");
    return NULL;
  }
  Py_RETURN_NONE;
}

PyObject *raypy_kdb_send(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int fd;
  RayObject *msg;
  if (!PyArg_ParseTuple(args, "iO!", &fd, &RayObjectType, &msg))
    return NULL;

  char err[128] = {0};

  /* Encode and decode touch the rayforce symbol table, so keep the GIL for
   * those; release it only around the blocking server round-trip. */
  uint8_t *req = NULL;
  int64_t req_len = 0;
  if (q_encode(msg->obj, &req, &req_len, err, sizeof err) < 0) {
    PyErr_SetString(PyExc_RuntimeError, err[0] ? err : "kdb: encode failed");
    return NULL;
  }

  uint8_t *resp = NULL;
  int64_t resp_len = 0;
  int compressed = 0;
  int rc;
  Py_BEGIN_ALLOW_THREADS;
  rc = q_exchange(fd, req, req_len, &resp, &resp_len, &compressed, err,
                  sizeof err);
  Py_END_ALLOW_THREADS;
  free(req);
  if (rc < 0) {
    PyErr_SetString(PyExc_RuntimeError, err[0] ? err : "kdb: send failed");
    return NULL;
  }

  ray_t *result = q_decode(resp, resp_len, compressed, err, sizeof err);
  free(resp);
  if (result == NULL) {
    PyErr_SetString(PyExc_RuntimeError, err[0] ? err : "kdb: decode failed");
    return NULL;
  }
  return raypy_wrap_ray_object(result);
}
