/*
 * raypy_compat.h — v1 → v2 compatibility shim for rayforce-py.
 *
 * Keeps Python C bindings written against rayforce v1 names largely textually
 * unchanged while the underlying library moved to v2. Include AFTER
 * <rayforce.h> and any v2 internal headers.
 *
 * Non-goals: this is not an emulation layer. Features with no v2 equivalent
 * (TYPE_ENUM, TYPE_C8, TYPE_PARTEDLIST, TYPE_MAP*, TYPE_TOKEN, IPC) are NOT
 * aliased — their call sites must be rewritten or deleted.
 */

#ifndef RAYPY_COMPAT_H
#define RAYPY_COMPAT_H

#include <limits.h>
#include <stdint.h>

/* ---- typedefs ---- */
typedef ray_t *obj_p;
typedef int8_t i8_t;
typedef int16_t i16_t;
typedef int32_t i32_t;
typedef int64_t i64_t;
typedef uint8_t u8_t;
typedef uint8_t b8_t;
typedef uint32_t u32_t;
typedef uint64_t u64_t;
typedef char c8_t;
typedef double f64_t;
typedef const char *str_p;
typedef const char *lit_p;
typedef void *raw_p;
typedef void nil_t;
typedef uint8_t guid_t[16];

/* ---- type-code aliases (v1 name → v2 value) ---- */
#define TYPE_LIST RAY_LIST
#define TYPE_B8 RAY_BOOL
#define TYPE_U8 RAY_U8
#define TYPE_I16 RAY_I16
#define TYPE_I32 RAY_I32
#define TYPE_I64 RAY_I64
#define TYPE_F64 RAY_F64
#define TYPE_DATE RAY_DATE
#define TYPE_TIME RAY_TIME
#define TYPE_TIMESTAMP RAY_TIMESTAMP
#define TYPE_GUID RAY_GUID
#define TYPE_SYMBOL RAY_SYM
#define TYPE_TABLE RAY_TABLE
#define TYPE_DICT RAY_DICT
#define TYPE_LAMBDA RAY_LAMBDA
#define TYPE_UNARY RAY_UNARY
#define TYPE_BINARY RAY_BINARY
#define TYPE_VARY RAY_VARY
#define TYPE_NULL RAY_NULL
#define TYPE_ERR RAY_ERROR
/* Deliberately NOT aliased — these are removed in v2:
 *   TYPE_C8 (use RAY_STR), TYPE_ENUM, TYPE_MAP*, TYPE_PARTEDLIST, TYPE_TOKEN.
 */

/* ---- constructor aliases ---- */
#define b8(v) ray_bool(v)
#define u8(v) ray_u8(v)
#define i16(v) ray_i16(v)
#define i32(v) ray_i32(v)
#define i64(v) ray_i64(v)
#define f64(v) ray_f64(v)

/* v1 c8(ch) produced a single-char atom. v2: length-1 SSO string. */
static inline ray_t *c8(char ch) { return ray_str(&ch, 1); }

/* v1 symbol(ptr, len) produced a symbol atom. v2: intern + wrap. */
static inline ray_t *symbol(const char *s, int64_t len) {
  int64_t id = ray_sym_intern(s, (size_t)len);
  return (id < 0) ? NULL : ray_sym(id);
}

/* v1 str_from_symbol(i64) returned the interned C string. */
static inline const char *str_from_symbol(int64_t id) {
  ray_t *s = ray_sym_str(id);
  return s ? ray_str_ptr(s) : NULL;
}

#define vector(type, len) ray_vec_new((int8_t)(type), (int64_t)(len))

/* ---- refcount helpers ---- */
/* v1 clone_obj returned the same pointer with an incremented rc.
 * v2 ray_retain is void; we inline it and return the pointer for
 * drop-in compatibility with `x = clone_obj(y)` style code. */
static inline ray_t *clone_obj(ray_t *v) {
  if (v)
    ray_retain(v);
  return v;
}
#define drop_obj(v)                                                            \
  do {                                                                         \
    if (v)                                                                     \
      ray_release(v);                                                          \
  } while (0)
#define rc_obj(v) ((v) ? (v)->rc : 0u)

/* ---- typed-vector accessor macros (AS_*) ---- */
#define AS_I16(v) ((int16_t *)ray_data(v))
#define AS_I32(v) ((int32_t *)ray_data(v))
#define AS_I64(v) ((int64_t *)ray_data(v))
#define AS_F64(v) ((double *)ray_data(v))
#define AS_B8(v) ((uint8_t *)ray_data(v))
#define AS_U8(v) ((uint8_t *)ray_data(v))
#define AS_C8(v) ((char *)ray_data(v))
#define AS_DATE(v) ((int32_t *)ray_data(v))
#define AS_TIME(v) ((int32_t *)ray_data(v))
#define AS_TIMESTAMP(v) ((int64_t *)ray_data(v))
#define AS_GUID(v) ((uint8_t *)ray_data(v))
#define AS_LIST(v) ((ray_t **)ray_data(v))
#define AS_SYMBOL(v) ((int64_t *)ray_data(v))

/* ---- vector / list append reassign helpers ----
 * v2's ray_vec_append / ray_list_append apply COW (releases old if shared)
 * and may realloc-grow (ray_scratch_realloc frees the old block). The
 * returned pointer is the only valid handle. Forgetting to reassign leaves
 * a dangling pointer; releasing the old separately is use-after-free.
 *
 * These macros standardize the reassignment so call sites cannot forget. */
#define RAY_APPEND_REASSIGN(vec, elem)                                         \
  do {                                                                         \
    (vec) = ray_vec_append((vec), (elem));                                     \
  } while (0)

#define RAY_LIST_APPEND_REASSIGN(lst, obj)                                     \
  do {                                                                         \
    (lst) = ray_list_append((lst), (obj));                                     \
  } while (0)

/* ---- attribute flags (defined only in v2 internal headers) ----
 * Pyext deliberately does not include v2 src/lang/eval.h or src/mem/heap.h.
 * Re-declare the attrs we depend on here; values must match v2 source. */
#ifndef RAY_ATTR_DICT
#define RAY_ATTR_DICT 0x02 /* RAY_LIST + this bit = dict {k: v ...} */
#endif

/* ---- NULL singleton ---- */
#define NULL_OBJ RAY_NULL_OBJ

/* ---- null sentinel scalar values ---- */
#define NULL_I16 INT16_MIN
#define NULL_I32 INT32_MIN
#define NULL_I64 INT64_MIN

/* ---- eval / serde ---- */
#define ser_obj(x) ray_ser(x)
#define de_obj(x) ray_de(x)
#define eval_obj(x) ray_eval(x)

/* v2 public builtins end in _fn. The pyext code was written against the
 * shorter names; route them through. */
#define ray_key(x) ray_key_fn(x)
#define ray_value(x) ray_value_fn(x)
#define ray_at(x, y) ray_at_fn((x), (y))
#define ray_update(args, n) ray_update_fn((args), (n))
#define ray_insert(args, n) ray_insert_fn((args), (n))
#define ray_upsert(args, n) ray_upsert_fn((args), (n))

/* v1 error check */
#define IS_ERR(obj) RAY_IS_ERR(obj)
#define IS_ATOM(obj) ((obj)->type < 0)
#define IS_VECTOR(obj) ((obj)->type > 0 && (obj)->type <= RAY_STR)

#endif /* RAYPY_COMPAT_H */
