/* Thin libgcrypt facade for Emacs cryptographic hashes.

Copyright (C) 2026 Free Software Foundation, Inc.

This file is part of GNU Emacs.

GNU Emacs is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GNU Emacs is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GNU Emacs.  If not, see <https://www.gnu.org/licenses/>.

This header re-exports the subset of gnulib's md5.h / sha1.h /
sha256.h / sha512.h / sha3.h interface that Emacs and its lib-src
helpers consume.  The implementation lives in emacs-hash.c and is
backed by libgcrypt's message-digest API.

Keeping the function names and struct names identical to gnulib's
means C call sites only swap their includes.  The struct layouts are
opaque (a single gcry_md_hd_t handle); callers must not poke into
their fields.  */

#ifndef EMACS_HASH_H
#define EMACS_HASH_H

#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>
#include <gcrypt.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Digest sizes (bytes), matching gnulib's lib/<algo>.h.  */
#define MD5_DIGEST_SIZE      16
#define SHA1_DIGEST_SIZE     20
enum { SHA224_DIGEST_SIZE  = 28 };
enum { SHA256_DIGEST_SIZE  = 32 };
enum { SHA384_DIGEST_SIZE  = 48 };
enum { SHA512_DIGEST_SIZE  = 64 };
enum { SHA3_224_DIGEST_SIZE = 28 };
enum { SHA3_256_DIGEST_SIZE = 32 };
enum { SHA3_384_DIGEST_SIZE = 48 };
enum { SHA3_512_DIGEST_SIZE = 64 };

/* Streaming contexts.  The struct names match gnulib's so existing
   stack-allocated `struct md5_ctx ctx;' declarations compile
   unchanged.  Callers must not access fields directly.  */
struct md5_ctx    { gcry_md_hd_t h; };
struct sha1_ctx   { gcry_md_hd_t h; };
struct sha256_ctx { gcry_md_hd_t h; };
struct sha512_ctx { gcry_md_hd_t h; };
/* SHA-3 is exposed only through the one-shot sha3_*_buffer functions
   below; no streaming context is provided.  */

/* One-shot interfaces: compute hash of LEN bytes at BUF, write the
   digest into RESBLOCK, return RESBLOCK.  */
extern void *md5_buffer    (const char *buf, size_t len, void *resblock);
extern void *sha1_buffer   (const char *buf, size_t len, void *resblock);
extern void *sha224_buffer (const char *buf, size_t len, void *resblock);
extern void *sha256_buffer (const char *buf, size_t len, void *resblock);
extern void *sha384_buffer (const char *buf, size_t len, void *resblock);
extern void *sha512_buffer (const char *buf, size_t len, void *resblock);
extern void *sha3_224_buffer (const char *buf, size_t len, void *resblock);
extern void *sha3_256_buffer (const char *buf, size_t len, void *resblock);
extern void *sha3_384_buffer (const char *buf, size_t len, void *resblock);
extern void *sha3_512_buffer (const char *buf, size_t len, void *resblock);

/* Stream-from-FILE interfaces.  Return 0 on success, 1 on failure
   (matches gnulib's md5_stream contract).  */
extern int md5_stream  (FILE *stream, void *resblock);
extern int sha1_stream (FILE *stream, void *resblock);

/* MD5 streaming.  */
extern void  md5_init_ctx      (struct md5_ctx *ctx);
extern void  md5_process_bytes (const void *buf, size_t len,
				struct md5_ctx *ctx);
/* gnulib distinguishes a block-aligned fast path; libgcrypt does the
   blocking itself, so md5_process_block is a synonym.  */
extern void  md5_process_block (const void *buf, size_t len,
				struct md5_ctx *ctx);
extern void *md5_finish_ctx    (struct md5_ctx *ctx, void *resbuf);

/* SHA-1 streaming.  */
extern void  sha1_init_ctx      (struct sha1_ctx *ctx);
extern void  sha1_process_bytes (const void *buf, size_t len,
				 struct sha1_ctx *ctx);
extern void *sha1_finish_ctx    (struct sha1_ctx *ctx, void *resbuf);

/* SHA-256 streaming.  */
extern void  sha256_init_ctx      (struct sha256_ctx *ctx);
extern void  sha256_process_bytes (const void *buf, size_t len,
				   struct sha256_ctx *ctx);
extern void *sha256_finish_ctx    (struct sha256_ctx *ctx, void *resbuf);

#ifdef __cplusplus
}
#endif

#endif /* EMACS_HASH_H */
