/*
 * raypy_kdb.c — KDB+ IPC client.
 *
 * Sends raw query strings (or any rayforce object) to a KDB+ server using
 * the documented KDB+ wire format and returns the response decoded into
 * rayforce types. Blocking sockets, no event loop.
 *
 * Supported KDB+ wire types
 *   atoms:   -KB -KG -KH -KI -KJ -KE -KF -KC -KS -KP -KM -KD -KN -KU -KV
 *            -KT -UU
 *   vectors: KB UU KG KH KI KJ KE KF KC KS KP KM KD KZ KN KU KV KT
 *   nested:  0 (general list), XT (table), XD (dict)
 *   error:   -128
 */

#include "rayforce_c.h"

#include <errno.h>
#include <netdb.h>
#include <stdlib.h>
#include <sys/socket.h>

/* ================================================================
 * KDB+ wire-format constants
 * ================================================================ */
#define KDB_KB 1   /* boolean      */
#define KDB_UU 2   /* guid (16B)   */
#define KDB_KG 4   /* byte         */
#define KDB_KH 5   /* short        */
#define KDB_KI 6   /* int          */
#define KDB_KJ 7   /* long         */
#define KDB_KE 8   /* real (f32)   */
#define KDB_KF 9   /* float (f64)  */
#define KDB_KC 10  /* char         */
#define KDB_KS 11  /* symbol       */
#define KDB_KP 12  /* timestamp    */
#define KDB_KM 13  /* month        */
#define KDB_KD 14  /* date         */
#define KDB_KZ 15  /* datetime     */
#define KDB_KN 16  /* timespan     */
#define KDB_KU 17  /* minute       */
#define KDB_KV 18  /* second       */
#define KDB_KT 19  /* time         */
#define KDB_XT 98  /* table        */
#define KDB_XD 99  /* dict         */
#define KDB_ERR (-128)

#define KDB_MSG_SYNC 1

typedef struct {
  uint8_t endianness;
  uint8_t msgtype;
  uint8_t compressed;
  uint8_t reserved;
  uint32_t size;
} kdb_header_t;

#define KDB_MAX_CONNS 256
static int kdb_conn_fd[KDB_MAX_CONNS];
static int kdb_conn_init = 0;

static void kdb_init_table(void) {
  if (kdb_conn_init)
    return;
  for (int i = 0; i < KDB_MAX_CONNS; i++)
    kdb_conn_fd[i] = -1;
  kdb_conn_init = 1;
}

static int kdb_alloc_slot(int fd) {
  kdb_init_table();
  for (int i = 0; i < KDB_MAX_CONNS; i++) {
    if (kdb_conn_fd[i] == -1) {
      kdb_conn_fd[i] = fd;
      return i;
    }
  }
  return -1;
}

/* ================================================================
 * Socket helpers
 * ================================================================ */

static ssize_t kdb_recv_all(int fd, void *buf, size_t n) {
  size_t total = 0;
  uint8_t *p = (uint8_t *)buf;
  while (total < n) {
    ssize_t r = recv(fd, p + total, n - total, 0);
    if (r == 0)
      return -1;
    if (r < 0) {
      if (errno == EINTR)
        continue;
      return -1;
    }
    total += (size_t)r;
  }
  return (ssize_t)total;
}

static ssize_t kdb_send_all(int fd, const void *buf, size_t n) {
  size_t total = 0;
  const uint8_t *p = (const uint8_t *)buf;
  while (total < n) {
    ssize_t r = send(fd, p + total, n - total, 0);
    if (r <= 0) {
      if (r < 0 && errno == EINTR)
        continue;
      return -1;
    }
    total += (size_t)r;
  }
  return (ssize_t)total;
}

static int kdb_open_socket(const char *host, int port) {
  char service[16];
  snprintf(service, sizeof(service), "%d", port);

  struct addrinfo hints = {0};
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;

  struct addrinfo *res = NULL;
  if (getaddrinfo(host, service, &hints, &res) != 0 || res == NULL)
    return -1;

  int fd = -1;
  for (struct addrinfo *p = res; p != NULL; p = p->ai_next) {
    fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
    if (fd < 0)
      continue;
    if (connect(fd, p->ai_addr, p->ai_addrlen) == 0)
      break;
    close(fd);
    fd = -1;
  }
  freeaddrinfo(res);
  return fd;
}

/* ================================================================
 * Wire-format size + serialize (rayforce v2 → KDB+)
 * ================================================================ */

static int8_t kdb_type_of(int8_t ray_type) {
  int sign = (ray_type < 0) ? -1 : 1;
  int t = (ray_type < 0) ? -ray_type : ray_type;
  switch (t) {
  case RAY_BOOL: return (int8_t)(sign * KDB_KB);
  case RAY_U8: return (int8_t)(sign * KDB_KG);
  case RAY_I16: return (int8_t)(sign * KDB_KH);
  case RAY_I32: return (int8_t)(sign * KDB_KI);
  case RAY_I64: return (int8_t)(sign * KDB_KJ);
  case RAY_F32: return (int8_t)(sign * KDB_KE);
  case RAY_F64: return (int8_t)(sign * KDB_KF);
  case RAY_DATE: return (int8_t)(sign * KDB_KD);
  case RAY_TIME: return (int8_t)(sign * KDB_KT);
  case RAY_TIMESTAMP: return (int8_t)(sign * KDB_KP);
  case RAY_GUID: return (int8_t)(sign * KDB_UU);
  case RAY_SYM: return (int8_t)(sign * KDB_KS);
  case RAY_STR: return (int8_t)(sign * KDB_KC);
  case RAY_LIST: return 0;
  case RAY_TABLE: return KDB_XT;
  case RAY_DICT: return KDB_XD;
  case RAY_ERROR: return KDB_ERR;
  default: return 0;
  }
}

static int kdb_elem_size(int8_t ray_type) {
  switch (ray_type < 0 ? -ray_type : ray_type) {
  case RAY_BOOL:
  case RAY_U8: return 1;
  case RAY_I16: return 2;
  case RAY_I32:
  case RAY_DATE:
  case RAY_TIME:
  case RAY_F32: return 4;
  case RAY_I64:
  case RAY_TIMESTAMP:
  case RAY_F64: return 8;
  case RAY_GUID: return 16;
  default: return 0;
  }
}

/* Forward */
static int64_t kdb_size_obj(ray_t *obj);
static int64_t kdb_ser_obj(uint8_t *buf, ray_t *obj);
static ray_t *kdb_des_obj(uint8_t **buf, int64_t *len);

/* Build a v2 table from a RAY_SYM-vec of column names and a RAY_LIST of
 * column vectors. Consumes references to `keys` and `vals` on success. */
static ray_t *kdb_make_table(ray_t *keys, ray_t *vals) {
  if (keys == NULL || vals == NULL || keys->type != RAY_SYM ||
      vals->type != RAY_LIST || keys->len != vals->len) {
    if (keys) ray_release(keys);
    if (vals) ray_release(vals);
    return ray_error("kdb: malformed table — expected (sym-vec, list)", NULL);
  }
  int64_t ncols = keys->len;
  ray_t *tbl = ray_table_new(ncols);
  if (tbl == NULL || RAY_IS_ERR(tbl)) {
    ray_release(keys);
    ray_release(vals);
    return tbl ? tbl : ray_error("kdb: table_new failed", NULL);
  }
  int64_t *ids = (int64_t *)ray_data(keys);
  ray_t **cols = (ray_t **)ray_data(vals);
  for (int64_t i = 0; i < ncols; i++) {
    ray_t *res = ray_table_add_col(tbl, ids[i], cols[i]);
    if (res == NULL || RAY_IS_ERR(res)) {
      ray_release(tbl);
      ray_release(keys);
      ray_release(vals);
      return res ? res : ray_error("kdb: table_add_col failed", NULL);
    }
    tbl = res;
  }
  ray_release(keys);
  ray_release(vals);
  return tbl;
}

static int64_t kdb_size_obj(ray_t *obj) {
  if (obj == NULL || obj == RAY_NULL_OBJ)
    return 1 + 1 + 4; /* type + attrs + len(0) */

  int8_t t = obj->type;

  /* Atoms */
  if (t < 0) {
    int abs_t = -t;
    switch (abs_t) {
    case RAY_BOOL:
    case RAY_U8: return 1 + 1;
    case RAY_I16: return 1 + 2;
    case RAY_I32:
    case RAY_DATE:
    case RAY_TIME:
    case RAY_F32: return 1 + 4;
    case RAY_I64:
    case RAY_TIMESTAMP:
    case RAY_F64: return 1 + 8;
    case RAY_GUID: return 1 + 16;
    case RAY_SYM: {
      ray_t *s = ray_sym_str(obj->i64);
      int64_t n = s ? (int64_t)ray_str_len(s) : 0;
      if (s) ray_release(s);
      return 1 + n + 1; /* null-terminated */
    }
    case RAY_STR: {
      /* Single char goes as -KC atom; multi-char as KC vector. */
      int64_t n = (int64_t)ray_str_len(obj);
      if (n == 1) return 1 + 1;
      return 1 + 1 + 4 + n;
    }
    }
    return 0;
  }

  /* Vectors / containers */
  if (t == RAY_LIST) {
    int64_t size = 1 + 1 + 4;
    ray_t **elems = (ray_t **)ray_data(obj);
    for (int64_t i = 0; i < obj->len; i++)
      size += kdb_size_obj(elems[i]);
    return size;
  }
  if (t == RAY_SYM) {
    int64_t size = 1 + 1 + 4;
    int64_t *ids = (int64_t *)ray_data(obj);
    for (int64_t i = 0; i < obj->len; i++) {
      ray_t *s = ray_sym_str(ids[i]);
      size += s ? (int64_t)ray_str_len(s) + 1 : 1;
      if (s) ray_release(s);
    }
    return size;
  }
  if (t == RAY_TABLE) {
    /* Wire form: XT byte + attrs(0) + XD marker + KS-vec of names +
     * list-0 of column vectors. v2 RAY_TABLE is opaque — extract via the
     * public accessors instead of indexing ray_data directly. */
    int64_t ncols = ray_table_ncols(obj);
    int64_t names = 1 + 1 + 4; /* KS type + attrs + count */
    for (int64_t i = 0; i < ncols; i++) {
      ray_t *s = ray_sym_str(ray_table_col_name(obj, i));
      names += s ? (int64_t)ray_str_len(s) + 1 : 1;
      if (s) ray_release(s);
    }
    int64_t cols = 1 + 1 + 4; /* list type + attrs + count */
    for (int64_t i = 0; i < ncols; i++)
      cols += kdb_size_obj(ray_table_get_col_idx(obj, i));
    return 3 + names + cols; /* XT + attrs + XD */
  }
  if (t == RAY_ERROR) {
    const char *msg = ray_err_code(obj);
    int64_t n = msg ? (int64_t)strlen(msg) : 0;
    return 1 + n + 1; /* type byte + msg + null */
  }
  if (t == RAY_NULL)
    return 1 + 1 + 4;

  int esz = kdb_elem_size(t);
  if (esz == 0)
    return 0;
  return 1 + 1 + 4 + obj->len * esz;
}

static int64_t kdb_ser_obj(uint8_t *buf, ray_t *obj) {
  uint8_t *start = buf;

  if (obj == NULL || obj == RAY_NULL_OBJ) {
    *buf++ = 101; /* identity / null */
    *buf++ = 0;
    return buf - start;
  }

  int8_t t = obj->type;
  *buf++ = (uint8_t)kdb_type_of(t);

  if (t < 0) {
    int abs_t = -t;
    switch (abs_t) {
    case RAY_BOOL:
    case RAY_U8: *buf++ = obj->u8; return buf - start;
    case RAY_I16: memcpy(buf, &obj->i16, 2); return buf + 2 - start;
    case RAY_I32:
    case RAY_DATE:
    case RAY_TIME: memcpy(buf, &obj->i32, 4); return buf + 4 - start;
    case RAY_F32: {
      float f = (float)obj->f64;
      memcpy(buf, &f, 4);
      return buf + 4 - start;
    }
    case RAY_I64:
    case RAY_TIMESTAMP: memcpy(buf, &obj->i64, 8); return buf + 8 - start;
    case RAY_F64: memcpy(buf, &obj->f64, 8); return buf + 8 - start;
    case RAY_GUID: memcpy(buf, ray_data(obj), 16); return buf + 16 - start;
    case RAY_SYM: {
      ray_t *s = ray_sym_str(obj->i64);
      size_t n = s ? ray_str_len(s) : 0;
      if (s) {
        memcpy(buf, ray_str_ptr(s), n);
        ray_release(s);
      }
      buf[n] = 0;
      return buf + n + 1 - start;
    }
    case RAY_STR: {
      size_t n = ray_str_len(obj);
      if (n == 1) {
        *buf++ = (uint8_t)ray_str_ptr(obj)[0];
        return buf - start;
      }
      /* RAY_STR atom (n>1) → KC vector */
      start[0] = (uint8_t)KDB_KC;
      *buf++ = 0;            /* attrs */
      uint32_t len32 = (uint32_t)n;
      memcpy(buf, &len32, 4);
      buf += 4;
      memcpy(buf, ray_str_ptr(obj), n);
      return buf + n - start;
    }
    }
    return -1;
  }

  /* Containers/vectors */
  if (t == RAY_LIST) {
    *buf++ = 0;
    uint32_t len32 = (uint32_t)obj->len;
    memcpy(buf, &len32, 4);
    buf += 4;
    ray_t **elems = (ray_t **)ray_data(obj);
    for (int64_t i = 0; i < obj->len; i++) {
      int64_t r = kdb_ser_obj(buf, elems[i]);
      if (r < 0) return -1;
      buf += r;
    }
    return buf - start;
  }
  if (t == RAY_SYM) {
    *buf++ = 0;
    uint32_t len32 = (uint32_t)obj->len;
    memcpy(buf, &len32, 4);
    buf += 4;
    int64_t *ids = (int64_t *)ray_data(obj);
    for (int64_t i = 0; i < obj->len; i++) {
      ray_t *s = ray_sym_str(ids[i]);
      size_t n = s ? ray_str_len(s) : 0;
      if (s) {
        memcpy(buf, ray_str_ptr(s), n);
        ray_release(s);
      }
      buf[n] = 0;
      buf += n + 1;
    }
    return buf - start;
  }
  if (t == RAY_TABLE) {
    int64_t ncols = ray_table_ncols(obj);
    *buf++ = 0;                /* attrs */
    *buf++ = (uint8_t)KDB_XD;  /* table is dict-of-cols on the wire */

    /* keys: KS vector of column names */
    *buf++ = (uint8_t)KDB_KS;
    *buf++ = 0;                /* attrs */
    uint32_t kn = (uint32_t)ncols;
    memcpy(buf, &kn, 4); buf += 4;
    for (int64_t i = 0; i < ncols; i++) {
      ray_t *s = ray_sym_str(ray_table_col_name(obj, i));
      size_t n = s ? ray_str_len(s) : 0;
      if (s) {
        memcpy(buf, ray_str_ptr(s), n);
        ray_release(s);
      }
      buf[n] = 0;
      buf += n + 1;
    }

    /* values: general list of column vectors */
    *buf++ = 0;                /* list type */
    *buf++ = 0;                /* attrs */
    memcpy(buf, &kn, 4); buf += 4;
    for (int64_t i = 0; i < ncols; i++) {
      int64_t r = kdb_ser_obj(buf, ray_table_get_col_idx(obj, i));
      if (r < 0) return -1;
      buf += r;
    }
    return buf - start;
  }
  /* RAY_DICT (type code 99) is never produced by v2; dicts present as
   * RAY_LIST + RAY_ATTR_DICT and are serialized through the RAY_LIST path
   * above (losing the dict-ness on the wire). */
  if (t == RAY_ERROR) {
    const char *msg = ray_err_code(obj);
    size_t n = msg ? strlen(msg) : 0;
    if (n) memcpy(buf, msg, n);
    buf[n] = 0;
    return buf + n + 1 - start;
  }
  if (t == RAY_NULL) {
    *buf++ = 0;
    memset(buf, 0, 4);
    return buf + 4 - start;
  }

  int esz = kdb_elem_size(t);
  if (esz == 0)
    return -1;
  *buf++ = 0;
  uint32_t len32 = (uint32_t)obj->len;
  memcpy(buf, &len32, 4);
  buf += 4;
  size_t n = (size_t)obj->len * esz;
  if (t == RAY_F32) {
    /* Already F32-sized; ray_data is f32-packed. */
    memcpy(buf, ray_data(obj), n);
  } else {
    memcpy(buf, ray_data(obj), n);
  }
  return buf + n - start;
}

/* ================================================================
 * Wire-format deserialize (KDB+ → rayforce v2)
 * ================================================================ */

#define KDB_NEED(n)                                                            \
  do {                                                                         \
    if (*len < (int64_t)(n))                                                   \
      return ray_error("kdb: buffer underflow", NULL);                         \
  } while (0)

/* Decode a width-byte atom and re-tag as the requested ray_type. Works
 * because v2's atom union shares storage by width: BOOL/U8 → u8;
 * I16 → i16; I32/DATE/TIME → i32; I64/TIMESTAMP → i64. */
static ray_t *kdb_des_atom_i(uint8_t **buf, int64_t *len, int8_t ray_type,
                              int width) {
  KDB_NEED(width);
  ray_t *o = NULL;
  switch (width) {
  case 1: o = ray_u8(**buf); break;
  case 2: {
    int16_t v;
    memcpy(&v, *buf, 2);
    o = ray_i16(v);
    break;
  }
  case 4: {
    int32_t v;
    memcpy(&v, *buf, 4);
    o = ray_i32(v);
    break;
  }
  case 8: {
    int64_t v;
    memcpy(&v, *buf, 8);
    o = ray_i64(v);
    break;
  }
  }
  if (o)
    o->type = -ray_type; /* tag with the requested ray atom type */
  *buf += width;
  *len -= width;
  return o;
}

static ray_t *kdb_des_vec_i(uint8_t **buf, int64_t *len, int8_t ray_type,
                            int width) {
  KDB_NEED(1 + 4);
  (*buf)++;
  *len -= 1; /* attrs */
  int32_t n;
  memcpy(&n, *buf, 4);
  *buf += 4;
  *len -= 4;
  if (n < 0)
    return ray_error("kdb: negative vector length", NULL);
  int64_t bytes = (int64_t)n * width;
  if (*len < bytes)
    return ray_error("kdb: buffer underflow (vec body)", NULL);

  ray_t *vec = ray_vec_new(ray_type, n);
  if (vec == NULL || RAY_IS_ERR(vec)) {
    if (vec) ray_release(vec);
    return ray_error("kdb: vector alloc failed", NULL);
  }
  memcpy(ray_data(vec), *buf, bytes);
  vec->len = n;
  *buf += bytes;
  *len -= bytes;
  return vec;
}

static ray_t *kdb_des_obj(uint8_t **buf, int64_t *len) {
  if (*len < 1)
    return ray_error("kdb: buffer underflow (type)", NULL);

  int8_t type = (int8_t)**buf;
  (*buf)++;
  (*len)--;

  switch (type) {
  /* Atoms (negative type). The deserializer reads raw bytes then re-tags. */
  case -KDB_KB: return kdb_des_atom_i(buf, len, RAY_BOOL, 1);
  case -KDB_KG: return kdb_des_atom_i(buf, len, RAY_U8, 1);
  case -KDB_KH: return kdb_des_atom_i(buf, len, RAY_I16, 2);
  case -KDB_KI: return kdb_des_atom_i(buf, len, RAY_I32, 4);
  case -KDB_KJ: return kdb_des_atom_i(buf, len, RAY_I64, 8);
  case -KDB_KP: return kdb_des_atom_i(buf, len, RAY_TIMESTAMP, 8);
  case -KDB_KN: return kdb_des_atom_i(buf, len, RAY_TIMESTAMP, 8);
  case -KDB_KD:
  case -KDB_KM: return kdb_des_atom_i(buf, len, RAY_DATE, 4);
  case -KDB_KT:
  case -KDB_KU:
  case -KDB_KV: return kdb_des_atom_i(buf, len, RAY_TIME, 4);
  case -KDB_KE: {
    KDB_NEED(4);
    float f;
    memcpy(&f, *buf, 4);
    *buf += 4;
    *len -= 4;
    return ray_f64((double)f);
  }
  case -KDB_KF: {
    KDB_NEED(8);
    double f;
    memcpy(&f, *buf, 8);
    *buf += 8;
    *len -= 8;
    return ray_f64(f);
  }
  case -KDB_KC: {
    KDB_NEED(1);
    char c = (char)**buf;
    *buf += 1;
    *len -= 1;
    return ray_str(&c, 1);
  }
  case -KDB_KS: {
    int64_t n = 0;
    while (n < *len && (*buf)[n] != '\0') n++;
    if (n >= *len)
      return ray_error("kdb: symbol not null-terminated", NULL);
    int64_t id = ray_sym_intern((const char *)*buf, (size_t)n);
    *buf += n + 1;
    *len -= n + 1;
    return (id < 0) ? ray_error("kdb: symbol intern failed", NULL)
                    : ray_sym(id);
  }
  case -KDB_UU: {
    KDB_NEED(16);
    ray_t *g = ray_guid(*buf);
    *buf += 16;
    *len -= 16;
    return g;
  }

  /* Vectors */
  case KDB_KB: return kdb_des_vec_i(buf, len, RAY_BOOL, 1);
  case KDB_KG: return kdb_des_vec_i(buf, len, RAY_U8, 1);
  case KDB_KH: return kdb_des_vec_i(buf, len, RAY_I16, 2);
  case KDB_KI: return kdb_des_vec_i(buf, len, RAY_I32, 4);
  case KDB_KJ: return kdb_des_vec_i(buf, len, RAY_I64, 8);
  case KDB_KP: return kdb_des_vec_i(buf, len, RAY_TIMESTAMP, 8);
  case KDB_KN: return kdb_des_vec_i(buf, len, RAY_TIMESTAMP, 8);
  case KDB_KD:
  case KDB_KM: return kdb_des_vec_i(buf, len, RAY_DATE, 4);
  case KDB_KT:
  case KDB_KU:
  case KDB_KV: return kdb_des_vec_i(buf, len, RAY_TIME, 4);
  case KDB_KZ: return kdb_des_vec_i(buf, len, RAY_TIMESTAMP, 8);
  case KDB_KE: {
    /* Real (4-byte float) vector — convert to F64 vec for v2. */
    KDB_NEED(1 + 4);
    (*buf)++;
    *len -= 1;
    int32_t n;
    memcpy(&n, *buf, 4);
    *buf += 4;
    *len -= 4;
    if (n < 0) return ray_error("kdb: negative real-vec length", NULL);
    int64_t bytes = (int64_t)n * 4;
    if (*len < bytes) return ray_error("kdb: buffer underflow (real-vec)", NULL);
    ray_t *vec = ray_vec_new(RAY_F64, n);
    if (vec == NULL || RAY_IS_ERR(vec)) {
      if (vec) ray_release(vec);
      return ray_error("kdb: vector alloc failed", NULL);
    }
    double *out = (double *)ray_data(vec);
    for (int32_t i = 0; i < n; i++) {
      float f;
      memcpy(&f, *buf + i * 4, 4);
      out[i] = (double)f;
    }
    vec->len = n;
    *buf += bytes;
    *len -= bytes;
    return vec;
  }
  case KDB_KF: return kdb_des_vec_i(buf, len, RAY_F64, 8);
  case KDB_UU: return kdb_des_vec_i(buf, len, RAY_GUID, 16);
  case KDB_KC: {
    /* KC vector → RAY_STR atom of length n */
    KDB_NEED(1 + 4);
    (*buf)++;
    *len -= 1;
    int32_t n;
    memcpy(&n, *buf, 4);
    *buf += 4;
    *len -= 4;
    if (n < 0) return ray_error("kdb: negative char-vec length", NULL);
    if (*len < n) return ray_error("kdb: buffer underflow (char-vec)", NULL);
    ray_t *s = ray_str((const char *)*buf, (size_t)n);
    *buf += n;
    *len -= n;
    return s;
  }
  case KDB_KS: {
    KDB_NEED(1 + 4);
    (*buf)++;
    *len -= 1;
    int32_t n;
    memcpy(&n, *buf, 4);
    *buf += 4;
    *len -= 4;
    if (n < 0) return ray_error("kdb: negative symbol-vec length", NULL);
    ray_t *vec = ray_sym_vec_new(RAY_SYM_W64, n);
    if (vec == NULL || RAY_IS_ERR(vec)) {
      if (vec) ray_release(vec);
      return ray_error("kdb: symbol vector alloc failed", NULL);
    }
    int64_t *ids = (int64_t *)ray_data(vec);
    for (int32_t i = 0; i < n; i++) {
      int64_t k = 0;
      while (k < *len && (*buf)[k] != '\0') k++;
      if (k >= *len) {
        ray_release(vec);
        return ray_error("kdb: symbol not null-terminated in vec", NULL);
      }
      int64_t id = ray_sym_intern((const char *)*buf, (size_t)k);
      if (id < 0) {
        ray_release(vec);
        return ray_error("kdb: symbol intern failed", NULL);
      }
      ids[i] = id;
      *buf += k + 1;
      *len -= k + 1;
    }
    vec->len = n;
    return vec;
  }

  case 0: { /* general list */
    KDB_NEED(1 + 4);
    (*buf)++;
    *len -= 1;
    int32_t n;
    memcpy(&n, *buf, 4);
    *buf += 4;
    *len -= 4;
    if (n < 0) return ray_error("kdb: negative list length", NULL);
    ray_t *list = ray_list_new(0);
    for (int32_t i = 0; i < n; i++) {
      ray_t *elem = kdb_des_obj(buf, len);
      if (elem == NULL || RAY_IS_ERR(elem)) {
        ray_release(list);
        return elem ? elem : ray_error("kdb: list element decode failed", NULL);
      }
      list = ray_list_append(list, elem);
      if (list == NULL || RAY_IS_ERR(list))
        return list ? list : ray_error("kdb: list append failed", NULL);
    }
    return list;
  }

  case KDB_XT: { /* table = attrs(0) + dict_marker(99) + keys + values */
    KDB_NEED(2);
    (*buf) += 2;
    *len -= 2;
    ray_t *keys = kdb_des_obj(buf, len);
    if (keys == NULL || RAY_IS_ERR(keys)) return keys;
    ray_t *vals = kdb_des_obj(buf, len);
    if (vals == NULL || RAY_IS_ERR(vals)) {
      ray_release(keys);
      return vals;
    }
    return kdb_make_table(keys, vals);
  }

  case KDB_XD: { /* dict = keys + values; could be a keyed table */
    ray_t *keys = kdb_des_obj(buf, len);
    if (keys == NULL || RAY_IS_ERR(keys)) return keys;
    ray_t *vals = kdb_des_obj(buf, len);
    if (vals == NULL || RAY_IS_ERR(vals)) {
      ray_release(keys);
      return vals;
    }
    /* Plain dict — represent as RAY_LIST + RAY_ATTR_DICT. */
    ray_t *dict = ray_list_new(0);
    dict = ray_list_append(dict, keys);
    dict = ray_list_append(dict, vals);
    if (dict) dict->attrs |= RAY_ATTR_DICT;
    return dict;
  }

  case KDB_ERR:
    return ray_error((const char *)*buf, NULL);

  default:
    return ray_error("kdb: unsupported wire type", NULL);
  }
}

/* ================================================================
 * IPC decompression for compressed KDB+ responses.
 * ================================================================ */

static int kdb_decompress(const uint8_t *src, int64_t src_len,
                          uint8_t **out_buf, int64_t *out_len) {
  if (src_len < 4) return -1;

  uint32_t header_size;
  memcpy(&header_size, src, 4);
  int64_t out_size = (int64_t)header_size - (int64_t)sizeof(kdb_header_t);
  if (out_size <= 0) return -1;

  uint32_t buffer[256] = {0};
  uint8_t *result = (uint8_t *)malloc((size_t)out_size);
  if (result == NULL) return -1;

  int64_t i = 0, n = 0, f = 0, s = 0, p = 0, d = 4;
  while (s < out_size) {
    if (i == 0) {
      if (d >= src_len) { free(result); return -1; }
      f = src[d++];
      i = 1;
    }
    if (f & i) {
      if (d >= src_len) { free(result); return -1; }
      int64_t r = buffer[src[d++]];
      result[s++] = result[r++];
      result[s++] = result[r++];
      if (d >= src_len) { free(result); return -1; }
      n = src[d++];
      for (int64_t m = 0; m < n; m++)
        result[s + m] = result[r + m];
    } else {
      if (d >= src_len) { free(result); return -1; }
      result[s++] = src[d++];
    }
    while (p < s - 1) {
      int64_t pp = p++;
      buffer[result[pp] ^ result[p]] = (uint32_t)pp;
    }
    if (f & i) {
      s += n;
      p = s;
    }
    i *= 2;
    if (i == 256) i = 0;
  }
  *out_buf = result;
  *out_len = out_size;
  return 0;
}

/* ================================================================
 * Pyext entry points
 * ================================================================ */

PyObject *raypy_kdb_connect(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  const char *host;
  int port;
  if (!PyArg_ParseTuple(args, "si", &host, &port))
    return NULL;
  if (port < 1 || port > 65535) {
    PyErr_SetString(PyExc_ValueError, "kdb: port must be in 1..65535");
    return NULL;
  }

  int fd = kdb_open_socket(host, port);
  if (fd < 0) {
    PyErr_Format(PyExc_RuntimeError, "kdb: connect to %s:%d failed", host,
                 port);
    return NULL;
  }

  /* KDB+ handshake: send {0x03, 0x00}, read 1 byte. */
  uint8_t hello[2] = {0x03, 0x00};
  if (kdb_send_all(fd, hello, 2) < 0 || kdb_recv_all(fd, hello, 1) < 0) {
    close(fd);
    PyErr_SetString(PyExc_RuntimeError, "kdb: handshake failed");
    return NULL;
  }

  int slot = kdb_alloc_slot(fd);
  if (slot < 0) {
    close(fd);
    PyErr_SetString(PyExc_RuntimeError, "kdb: connection table is full");
    return NULL;
  }
  return PyLong_FromLong(slot);
}

PyObject *raypy_kdb_close(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int slot;
  if (!PyArg_ParseTuple(args, "i", &slot))
    return NULL;
  kdb_init_table();
  if (slot < 0 || slot >= KDB_MAX_CONNS || kdb_conn_fd[slot] < 0) {
    PyErr_SetString(PyExc_RuntimeError, "kdb: invalid handle");
    return NULL;
  }
  close(kdb_conn_fd[slot]);
  kdb_conn_fd[slot] = -1;
  Py_RETURN_NONE;
}

PyObject *raypy_kdb_send(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int slot;
  RayObject *msg;
  if (!PyArg_ParseTuple(args, "iO!", &slot, &RayObjectType, &msg))
    return NULL;
  kdb_init_table();
  if (slot < 0 || slot >= KDB_MAX_CONNS || kdb_conn_fd[slot] < 0) {
    PyErr_SetString(PyExc_RuntimeError, "kdb: invalid handle");
    return NULL;
  }
  int fd = kdb_conn_fd[slot];

  int64_t body_size = kdb_size_obj(msg->obj);
  if (body_size <= 0) {
    PyErr_SetString(PyExc_RuntimeError, "kdb: cannot serialize message");
    return NULL;
  }

  size_t total = sizeof(kdb_header_t) + (size_t)body_size;
  uint8_t *buf = (uint8_t *)malloc(total);
  if (buf == NULL) return PyErr_NoMemory();

  int64_t written = kdb_ser_obj(buf + sizeof(kdb_header_t), msg->obj);
  if (written < 0) {
    free(buf);
    PyErr_SetString(PyExc_RuntimeError, "kdb: serialization failed");
    return NULL;
  }
  kdb_header_t header = {
      .endianness = 1,
      .msgtype = KDB_MSG_SYNC,
      .compressed = 0,
      .reserved = 0,
      .size = (uint32_t)(written + sizeof(kdb_header_t)),
  };
  memcpy(buf, &header, sizeof(header));

  if (kdb_send_all(fd, buf, header.size) < 0) {
    free(buf);
    PyErr_SetString(PyExc_RuntimeError, "kdb: send failed");
    return NULL;
  }
  free(buf);

  /* Receive response. */
  if (kdb_recv_all(fd, &header, sizeof(header)) < 0) {
    PyErr_SetString(PyExc_RuntimeError, "kdb: recv header failed");
    return NULL;
  }
  int64_t body_len = (int64_t)header.size - (int64_t)sizeof(header);
  if (body_len <= 0) {
    PyErr_SetString(PyExc_RuntimeError, "kdb: empty response body");
    return NULL;
  }

  uint8_t *body = (uint8_t *)malloc((size_t)body_len);
  if (body == NULL) return PyErr_NoMemory();
  if (kdb_recv_all(fd, body, (size_t)body_len) < 0) {
    free(body);
    PyErr_SetString(PyExc_RuntimeError, "kdb: recv body failed");
    return NULL;
  }

  uint8_t *decoded = body;
  int64_t decoded_len = body_len;
  uint8_t *decompressed = NULL;
  if (header.compressed) {
    if (kdb_decompress(body, body_len, &decompressed, &decoded_len) < 0) {
      free(body);
      PyErr_SetString(PyExc_RuntimeError, "kdb: decompression failed");
      return NULL;
    }
    decoded = decompressed;
  }

  uint8_t *cursor = decoded;
  int64_t remaining = decoded_len;
  ray_t *result = kdb_des_obj(&cursor, &remaining);
  free(body);
  if (decompressed) free(decompressed);
  if (result == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "kdb: deserialization returned null");
    return NULL;
  }
  return raypy_wrap_ray_object(result);
}
