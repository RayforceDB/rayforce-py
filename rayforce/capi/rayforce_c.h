#ifndef RAYFORCE_C_H
#define RAYFORCE_C_H

/* Also passed via -DPY_SSIZE_T_CLEAN from the build flags. Guard the local
 * define so GCC (which has no -Wno-macro-redefined and turns the redefinition
 * into a hard error under -Werror) does not fail the build. */
#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif

/* v2 public API */
#include <rayforce.h>

/* v2 internal headers (under src/; we build with -Isrc) */
#include "lang/env.h"      /* ray_env_get, ray_env_set */
#include "lang/eval.h"     /* ray_eval */
#include "lang/format.h"   /* ray_fmt */
#include "lang/internal.h" /* collection_elem, ray_cast_fn, ray_dict_fn, ... */
#include "ops/ops.h"       /* ray_is_lazy, ray_lazy_materialize */
#include "store/serde.h"   /* ray_ser, ray_de, ray_obj_save */
#include "table/sym.h"     /* RAY_SYM_W64 */

/* core/runtime.h would re-define ray_vm_t (also defined in lang/eval.h),
 * so we forward-declare just the runtime symbols we use here. */
typedef struct ray_runtime_s ray_runtime_t;
ray_runtime_t *ray_runtime_create(int argc, char **argv);
const char *ray_error_msg(void);

/* v2 stores dicts as RAY_LIST + this attr bit. Not exposed by any public
 * v2 header we include, so re-declared here; the value must match
 * src/mem/heap.h. (Distinct enough from the other 0x02 attr — RAY_ATTR_GRAPH
 * — because that one only ever appears on RAY_LAZY objects.) */
#ifndef RAY_ATTR_DICT
#define RAY_ATTR_DICT 0x02
#endif

#include <Python.h>
#include <string.h>
#include <unistd.h>

extern PyTypeObject RayObjectType;

typedef struct {
  PyObject_HEAD ray_t *obj;
} RayObject;

extern void *g_runtime;

int check_main_thread(void);

#define CHECK_MAIN_THREAD()                                                    \
  do {                                                                         \
    if (!check_main_thread())                                                  \
      return NULL;                                                             \
  } while (0)

ray_t *raypy_init_i16_from_py(PyObject *item);
ray_t *raypy_init_i32_from_py(PyObject *item);
ray_t *raypy_init_i64_from_py(PyObject *item);
ray_t *raypy_init_f64_from_py(PyObject *item);
ray_t *raypy_init_b8_from_py(PyObject *item);
ray_t *raypy_init_u8_from_py(PyObject *item);
ray_t *raypy_init_symbol_from_py(PyObject *item);
ray_t *raypy_init_string_from_py(PyObject *item);
ray_t *raypy_init_list_from_py(PyObject *item);
ray_t *raypy_init_guid_from_py(PyObject *item);
ray_t *raypy_init_date_from_py(PyObject *item);
ray_t *raypy_init_time_from_py(PyObject *item);
ray_t *raypy_init_timestamp_from_py(PyObject *item);
ray_t *raypy_init_dict_from_py(PyObject *item);

PyObject *raypy_wrap_ray_object(ray_t *ray_obj);

PyObject *raypy_init_i16(PyObject *self, PyObject *args);
PyObject *raypy_init_i32(PyObject *self, PyObject *args);
PyObject *raypy_init_i64(PyObject *self, PyObject *args);
PyObject *raypy_init_f64(PyObject *self, PyObject *args);
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
PyObject *raypy_init_vector_from_arrow_array(PyObject *self, PyObject *args);
PyObject *raypy_init_vector_from_raw_buffer(PyObject *self, PyObject *args);
PyObject *raypy_read_i16(PyObject *self, PyObject *args);
PyObject *raypy_read_i32(PyObject *self, PyObject *args);
PyObject *raypy_read_i64(PyObject *self, PyObject *args);
PyObject *raypy_read_f64(PyObject *self, PyObject *args);
PyObject *raypy_read_string(PyObject *self, PyObject *args);
PyObject *raypy_read_symbol(PyObject *self, PyObject *args);
PyObject *raypy_read_b8(PyObject *self, PyObject *args);
PyObject *raypy_read_u8(PyObject *self, PyObject *args);
PyObject *raypy_read_date(PyObject *self, PyObject *args);
PyObject *raypy_read_time(PyObject *self, PyObject *args);
PyObject *raypy_read_timestamp(PyObject *self, PyObject *args);
PyObject *raypy_read_guid(PyObject *self, PyObject *args);
PyObject *raypy_get_obj_type(PyObject *self, PyObject *args);
PyObject *raypy_table_keys(PyObject *self, PyObject *args);
PyObject *raypy_table_values(PyObject *self, PyObject *args);
PyObject *raypy_repr_table(PyObject *self, PyObject *args);
PyObject *raypy_dict_keys(PyObject *self, PyObject *args);
PyObject *raypy_dict_values(PyObject *self, PyObject *args);
PyObject *raypy_dict_get(PyObject *self, PyObject *args);
PyObject *raypy_at_idx(PyObject *self, PyObject *args);
PyObject *raypy_insert_obj(PyObject *self, PyObject *args);
PyObject *raypy_push_obj(PyObject *self, PyObject *args);
PyObject *raypy_set_obj(PyObject *self, PyObject *args);
PyObject *raypy_get_obj_length(PyObject *self, PyObject *args);
PyObject *raypy_eval_str(PyObject *self, PyObject *args);
PyObject *raypy_get_error_obj(PyObject *self, PyObject *args);
PyObject *raypy_binary_set(PyObject *self, PyObject *args);
PyObject *raypy_env_get_internal_fn_by_name(PyObject *self, PyObject *args);
PyObject *raypy_env_get_internal_name_by_fn(PyObject *self, PyObject *args);
PyObject *raypy_eval_obj(PyObject *self, PyObject *args);
PyObject *raypy_quote(PyObject *self, PyObject *args);
PyObject *raypy_rc(PyObject *self, PyObject *args);
PyObject *raypy_obj_addr(PyObject *self, PyObject *args);
PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args);
PyObject *raypy_update(PyObject *self, PyObject *args);
PyObject *raypy_insert(PyObject *self, PyObject *args);
PyObject *raypy_upsert(PyObject *self, PyObject *args);
PyObject *raypy_read_csv(PyObject *self, PyObject *args);
PyObject *raypy_write_csv(PyObject *self, PyObject *args);
PyObject *raypy_set_splayed(PyObject *self, PyObject *args);
PyObject *raypy_get_splayed(PyObject *self, PyObject *args);
PyObject *raypy_get_parted(PyObject *self, PyObject *args);
PyObject *raypy_ser_obj(PyObject *self, PyObject *args);
PyObject *raypy_de_obj(PyObject *self, PyObject *args);
PyObject *raypy_read_u8_vector(PyObject *self, PyObject *args);
PyObject *raypy_read_vector_raw(PyObject *self, PyObject *args);
PyObject *raypy_vec_is_null(PyObject *self, PyObject *args);
PyObject *raypy_vec_set_null(PyObject *self, PyObject *args);
PyObject *raypy_vec_slice(PyObject *self, PyObject *args);
PyObject *raypy_ipc_connect(PyObject *self, PyObject *args);
PyObject *raypy_ipc_close(PyObject *self, PyObject *args);
PyObject *raypy_ipc_send(PyObject *self, PyObject *args);
PyObject *raypy_ipc_send_async(PyObject *self, PyObject *args);
PyObject *raypy_ipc_server_init(PyObject *self, PyObject *args);
PyObject *raypy_ipc_server_poll(PyObject *self, PyObject *args);
PyObject *raypy_ipc_server_destroy(PyObject *self, PyObject *args);
PyObject *raypy_kdb_connect(PyObject *self, PyObject *args);
PyObject *raypy_kdb_close(PyObject *self, PyObject *args);
PyObject *raypy_kdb_send(PyObject *self, PyObject *args);

#endif
