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

extern ray_runtime_t *g_runtime;

int check_main_thread(void);

#define CHECK_MAIN_THREAD()                                                    \
  do {                                                                         \
    if (!check_main_thread())                                                  \
      return NULL;                                                             \
  } while (0)

/* Absolute value of a type code — atoms are negative, vecs are positive,
 * |t| is the canonical type id. */
static inline int ray_abs_type(int t) { return t < 0 ? -t : t; }

/* Byte width of a fixed-size scalar/vec element. Handles both atom (negative)
 * and vec (positive) type codes. Returns 0 for variable-width or unknown
 * types (RAY_LIST, RAY_SYM, RAY_STR, RAY_TABLE, RAY_DICT, ...). Callers
 * needing RAY_SYM (8) / RAY_STR (16) sizes must layer that on top. */
static inline size_t ray_scalar_elem_size(int8_t type) {
  switch (type < 0 ? -type : type) {
  case RAY_BOOL:
  case RAY_U8:
    return 1;
  case RAY_I16:
    return 2;
  case RAY_I32:
  case RAY_DATE:
  case RAY_TIME:
  case RAY_F32:
    return 4;
  case RAY_I64:
  case RAY_F64:
  case RAY_TIMESTAMP:
    return 8;
  case RAY_GUID:
    return 16;
  default:
    return 0;
  }
}

/* Scratch buffer for narrowing a ray atom payload into the natural storage
 * width of a typed vec, used by ray_vec_append / ray_vec_set / etc. */
typedef union {
  uint8_t u8;
  int16_t i16;
  int32_t i32;
  int64_t i64;
  float f32;
  double f64;
} scalar_scratch_t;

/* Pack an atom's payload into `scratch` and return a pointer to it, suitable
 * for ray_vec_append / ray_vec_insert_at / ray_vec_set. Returns NULL for
 * types that need out-of-band handling (GUID, STR, LIST). */
static inline const void *atom_scalar_ptr(ray_t *atom, int8_t vec_type,
                                          scalar_scratch_t *scratch) {
  switch (vec_type) {
  case RAY_BOOL:
  case RAY_U8:
    scratch->u8 = atom->u8;
    return &scratch->u8;
  case RAY_I16:
    scratch->i16 = atom->i16;
    return &scratch->i16;
  case RAY_I32:
  case RAY_DATE:
  case RAY_TIME:
    scratch->i32 = atom->i32;
    return &scratch->i32;
  case RAY_I64:
  case RAY_TIMESTAMP:
  case RAY_SYM:
    scratch->i64 = atom->i64;
    return &scratch->i64;
  /* v2 has no F32 atom — narrow from an F64 atom. */
  case RAY_F32:
    scratch->f32 = (float)atom->f64;
    return &scratch->f32;
  case RAY_F64:
    scratch->f64 = atom->f64;
    return &scratch->f64;
  default:
    return NULL;
  }
}

/* Build a v2 table from parallel arrays of column sym-ids and ray_t* columns.
 * Does not take ownership of `col_ids` or `cols`; `ray_table_add_col` retains
 * each column internally. On failure returns a RAY_IS_ERR ray_t (never NULL,
 * never PyErr — caller maps to its own error channel). */
ray_t *raypy_build_table(const int64_t *col_ids, ray_t *const *cols,
                         int64_t ncols);

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
