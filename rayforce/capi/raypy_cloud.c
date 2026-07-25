/*
 * raypy_cloud.c — bindings for rfcloud, the RayforceDB Cloud client.
 *
 * rfcloud (rayforce-cloud-sdk) owns the transport, authentication, the job
 * protocol and paging, and hands result pages back as bytes without decoding
 * them. Decoding happens here, through the same ray_de every other path in this
 * binding uses — which is the whole reason the SDK carries no decoder: one wire
 * format, one implementation.
 *
 * Clients and jobs cross into Python as capsules rather than integers, so a
 * stale or invented handle raises instead of dereferencing whatever it names.
 * Their lifetime is Python's: CloudClient closes them explicitly.
 */

#include "rayforce_c.h"

#include <rfcloud.h>

static const char CLIENT_CAPSULE[] = "rfcloud.client";
static const char JOB_CAPSULE[] = "rfcloud.job";

/* Every failure a caller can act on differently is a distinct exception in
 * rayforce.errors; the rest land on RayforceUserError with the SDK's message.
 */
static const char *exception_for(rfc_status status) {
  switch (status) {
  case RFC_ERR_ARG:
    return "RayforceValueError";
  case RFC_ERR_DNS:
  case RFC_ERR_CONNECT:
  case RFC_ERR_TLS:
  case RFC_ERR_HANDSHAKE:
  case RFC_ERR_IO:
  case RFC_ERR_PROTOCOL:
    return "RayforceWSError";
  case RFC_ERR_AUTH:
    return "RayforceCloudAuthError";
  case RFC_ERR_NOMEM:
    return "RayforceLimitError";
  default:
    return "RayforceUserError";
  }
}

/* Raise the rayforce.errors class matching `status`, carrying `detail`. */
static void *raise_cloud_error(rfc_status status, const char *detail) {
  PyObject *module = PyImport_ImportModule("rayforce.errors");
  if (module == NULL)
    return NULL;

  PyObject *exc = PyObject_GetAttrString(module, exception_for(status));
  Py_DECREF(module);
  if (exc == NULL)
    return NULL;

  PyErr_SetString(exc, detail != NULL ? detail : "cloud call failed");
  Py_DECREF(exc);
  return NULL;
}

static rfc_client *client_from(PyObject *capsule) {
  rfc_client *client =
      (rfc_client *)PyCapsule_GetPointer(capsule, CLIENT_CAPSULE);
  if (client == NULL)
    PyErr_SetString(PyExc_ValueError, "cloud: not an open client");
  return client;
}

static rfc_job *job_from(PyObject *capsule) {
  rfc_job *job = (rfc_job *)PyCapsule_GetPointer(capsule, JOB_CAPSULE);
  if (job == NULL)
    PyErr_SetString(PyExc_ValueError, "cloud: not a live job");
  return job;
}

/* Decode one page into a RayObject.
 *
 * The bytes are the native wire format, ipc header and all, so ray_de reads
 * them exactly as it reads an IPC frame — including its wire-version and
 * byte-order checks, which is what keeps a client from silently mis-parsing an
 * instance built from different code. An empty page is a result with no value
 * (a null), and decodes to None rather than to an error. */
static PyObject *decode_page(const rfc_page *page) {
  if (page->data == NULL || page->len == 0)
    Py_RETURN_NONE;

  ray_t *bytes = ray_vec_new(RAY_U8, (int64_t)page->len);
  if (bytes == NULL || RAY_IS_ERR(bytes)) {
    PyErr_SetString(PyExc_MemoryError,
                    "cloud: could not allocate a page buffer");
    return NULL;
  }
  bytes->len = (int64_t)page->len;
  memcpy(ray_data(bytes), page->data, page->len);

  ray_t *value = ray_de(bytes);
  ray_release(bytes);

  if (value == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "cloud: page decoded to nothing");
    return NULL;
  }
  if (RAY_IS_ERR(value)) {
    PyErr_Format(PyExc_RuntimeError,
                 "cloud: could not decode a result page: %s",
                 ray_err_code(value));
    ray_release(value);
    return NULL;
  }
  return raypy_wrap_ray_object(value);
}

/* (value, offset, returned, total, unit) — the page and how it sits in the
 * whole result. `total` can exceed `returned`; that is what says there is more
 * to fetch. */
static PyObject *page_tuple(const rfc_page *page) {
  PyObject *value = decode_page(page);
  if (value == NULL)
    return NULL;

  /* "N" steals the reference to `value`, and releases it itself if the build
   * fails — decrementing again here would free it twice. */
  return Py_BuildValue("(NKKKs)", value, (unsigned long long)page->offset,
                       (unsigned long long)page->returned,
                       (unsigned long long)page->total,
                       page->unit != NULL ? page->unit : "");
}

PyObject *raypy_cloud_connect(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  const char *url;
  const char *token;
  int binary = 1;
  int connect_timeout = 0;
  int request_timeout = 0;
  if (!PyArg_ParseTuple(args, "ss|iii", &url, &token, &binary, &connect_timeout,
                        &request_timeout))
    return NULL;

  rfc_config config = {
      .url = url,
      .token = token,
      .codec = binary ? RFC_CODEC_BINARY : RFC_CODEC_JSON,
      .connect_timeout = connect_timeout,
      .request_timeout = request_timeout,
  };

  rfc_status status;
  rfc_client *client;
  /* A connect is a DNS lookup, a TCP connect, a TLS handshake and a round trip;
   * holding the GIL through all of it would freeze every other thread. */
  Py_BEGIN_ALLOW_THREADS client = rfc_connect(&config, &status);
  Py_END_ALLOW_THREADS

      if (client == NULL) return raise_cloud_error(status,
                                                   rfc_last_error(NULL));

  PyObject *capsule = PyCapsule_New(client, CLIENT_CAPSULE, NULL);
  if (capsule == NULL) {
    rfc_close(client);
    return NULL;
  }
  return capsule;
}

PyObject *raypy_cloud_submit(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *capsule;
  const char *source;
  Py_ssize_t page_size;
  if (!PyArg_ParseTuple(args, "Osn", &capsule, &source, &page_size))
    return NULL;

  rfc_client *client = client_from(capsule);
  if (client == NULL)
    return NULL;
  if (page_size <= 0) {
    PyErr_SetString(PyExc_ValueError,
                    "cloud: page_size must be greater than zero");
    return NULL;
  }

  rfc_job *job = NULL;
  rfc_status status;
  Py_BEGIN_ALLOW_THREADS status =
      rfc_submit(client, source, (size_t)page_size, &job);
  Py_END_ALLOW_THREADS

      if (status != RFC_OK) return raise_cloud_error(status,
                                                     rfc_last_error(client));

  PyObject *page = page_tuple(rfc_job_page(job));
  if (page == NULL) {
    rfc_job_free(client, job);
    return NULL;
  }

  PyObject *handle = PyCapsule_New(job, JOB_CAPSULE, NULL);
  if (handle == NULL) {
    Py_DECREF(page);
    rfc_job_free(client, job);
    return NULL;
  }

  PyObject *result = PyTuple_Pack(2, handle, page);
  Py_DECREF(handle);
  Py_DECREF(page);
  return result;
}

/* Submit a serialized expression — what a query builder produces.
 *
 * The bytes are the same framed wire format ser_obj writes, so a query object
 * reaches the instance as the tree it already is. Rendering it to source text
 * would be the lossy route: a query carries its own data, and an insert's rows
 * have no faithful spelling as a literal. */
PyObject *raypy_cloud_submit_expr(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *capsule;
  Py_buffer expr;
  Py_ssize_t page_size;
  if (!PyArg_ParseTuple(args, "Oy*n", &capsule, &expr, &page_size))
    return NULL;

  rfc_client *client = client_from(capsule);
  if (client == NULL) {
    PyBuffer_Release(&expr);
    return NULL;
  }
  if (page_size <= 0) {
    PyBuffer_Release(&expr);
    PyErr_SetString(PyExc_ValueError,
                    "cloud: page_size must be greater than zero");
    return NULL;
  }
  if (expr.len <= 0) {
    PyBuffer_Release(&expr);
    PyErr_SetString(PyExc_ValueError, "cloud: expression is empty");
    return NULL;
  }

  rfc_job *job = NULL;
  rfc_status status;
  Py_BEGIN_ALLOW_THREADS status =
      rfc_submit_expr(client, (const uint8_t *)expr.buf, (size_t)expr.len,
                      (size_t)page_size, &job);
  Py_END_ALLOW_THREADS PyBuffer_Release(&expr);

  if (status != RFC_OK)
    return raise_cloud_error(status, rfc_last_error(client));

  PyObject *page = page_tuple(rfc_job_page(job));
  if (page == NULL) {
    rfc_job_free(client, job);
    return NULL;
  }

  PyObject *handle = PyCapsule_New(job, JOB_CAPSULE, NULL);
  if (handle == NULL) {
    Py_DECREF(page);
    rfc_job_free(client, job);
    return NULL;
  }

  PyObject *result = PyTuple_Pack(2, handle, page);
  Py_DECREF(handle);
  Py_DECREF(page);
  return result;
}

PyObject *raypy_cloud_fetch_page(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *client_capsule;
  PyObject *job_capsule;
  unsigned long long offset;
  Py_ssize_t limit;
  if (!PyArg_ParseTuple(args, "OOKn", &client_capsule, &job_capsule, &offset,
                        &limit))
    return NULL;

  rfc_client *client = client_from(client_capsule);
  if (client == NULL)
    return NULL;
  rfc_job *job = job_from(job_capsule);
  if (job == NULL)
    return NULL;
  if (limit <= 0) {
    PyErr_SetString(PyExc_ValueError, "cloud: limit must be greater than zero");
    return NULL;
  }

  const rfc_page *page = NULL;
  rfc_status status;
  Py_BEGIN_ALLOW_THREADS status =
      rfc_fetch_page(client, job, (uint64_t)offset, (size_t)limit, &page);
  Py_END_ALLOW_THREADS

      if (status != RFC_OK) return raise_cloud_error(status,
                                                     rfc_last_error(client));
  return page_tuple(page);
}

PyObject *raypy_cloud_bind_result(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *client_capsule;
  PyObject *job_capsule;
  const char *name;
  if (!PyArg_ParseTuple(args, "OOs", &client_capsule, &job_capsule, &name))
    return NULL;

  rfc_client *client = client_from(client_capsule);
  if (client == NULL)
    return NULL;
  rfc_job *job = job_from(job_capsule);
  if (job == NULL)
    return NULL;

  char bound[80] = {0};
  rfc_status status;
  Py_BEGIN_ALLOW_THREADS status =
      rfc_bind_result(client, job, name, bound, sizeof(bound));
  Py_END_ALLOW_THREADS

      if (status != RFC_OK) return raise_cloud_error(status,
                                                     rfc_last_error(client));
  return PyUnicode_FromString(bound);
}

PyObject *raypy_cloud_cancel(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *client_capsule;
  PyObject *job_capsule;
  if (!PyArg_ParseTuple(args, "OO", &client_capsule, &job_capsule))
    return NULL;

  rfc_client *client = client_from(client_capsule);
  if (client == NULL)
    return NULL;
  rfc_job *job = job_from(job_capsule);
  if (job == NULL)
    return NULL;

  /* Best-effort by contract: the job may already have finished. */
  rfc_cancel(client, job);
  Py_RETURN_NONE;
}

PyObject *raypy_cloud_job_free(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *client_capsule;
  PyObject *job_capsule;
  if (!PyArg_ParseTuple(args, "OO", &client_capsule, &job_capsule))
    return NULL;

  rfc_client *client = client_from(client_capsule);
  if (client == NULL)
    return NULL;
  rfc_job *job = job_from(job_capsule);
  if (job == NULL)
    return NULL;

  /* Releasing tells the instance to drop the retained result — memory held
   * there, not here — so it must not be skipped just because we are done. */
  Py_BEGIN_ALLOW_THREADS rfc_job_free(client, job);
  Py_END_ALLOW_THREADS

      /* Rename the capsule so a second free cannot reach freed memory: job_from
       * looks the pointer up by name and now reports a dead job instead. */
      PyCapsule_SetName(job_capsule, "rfcloud.job.freed");
  Py_RETURN_NONE;
}

PyObject *raypy_cloud_close(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *capsule;
  if (!PyArg_ParseTuple(args, "O", &capsule))
    return NULL;

  rfc_client *client = client_from(capsule);
  if (client == NULL)
    return NULL;

  Py_BEGIN_ALLOW_THREADS rfc_close(client);
  Py_END_ALLOW_THREADS

      PyCapsule_SetPointer(capsule, (void *)1);
  PyCapsule_SetName(capsule, "rfcloud.client.closed");
  Py_RETURN_NONE;
}
