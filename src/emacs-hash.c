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
along with GNU Emacs.  If not, see <https://www.gnu.org/licenses/>.  */

#include <config.h>

#include "emacs-hash.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Initialize libgcrypt once, before any other gcry_* call.

   Using an ELF constructor guarantees the call happens before main
   (and before any pthread is created by glibc's dynamic loader),
   which is the order libgcrypt's manual demands.  When the library
   is statically linked into a binary on systems without constructor
   support, callers should explicitly call emacs_hash_init.  */

static void
emacs_hash_init_once (void)
{
  if (! gcry_control (GCRYCTL_INITIALIZATION_FINISHED_P))
    {
      gcry_check_version (NULL);
      /* Plain digests do not need secure-memory; turn the warning off.  */
      gcry_control (GCRYCTL_DISABLE_SECMEM, 0);
      gcry_control (GCRYCTL_INITIALIZATION_FINISHED, 0);
    }
}

__attribute__ ((constructor))
static void
emacs_hash_ctor (void)
{
  emacs_hash_init_once ();
}

static void
emacs_hash_die (const char *where, int algo, gcry_error_t err)
{
  fprintf (stderr, "emacs-hash: %s failed for algorithm %d: %s\n",
	   where, algo, gcry_strerror (err));
  abort ();
}

static const unsigned char *
emacs_hash_read (gcry_md_hd_t h, int algo)
{
  const unsigned char *digest = gcry_md_read (h, algo);
  if (! digest)
    emacs_hash_die ("gcry_md_read", algo, GPG_ERR_DIGEST_ALGO);
  return digest;
}

/* One-shot hash of LEN bytes at BUF, written into RESBLOCK.
   Returns RESBLOCK.  */
static void *
emacs_hash_oneshot (int algo, size_t digest_size,
		    const char *buf, size_t len, void *resblock)
{
  emacs_hash_init_once ();

  gcry_md_hd_t hd;
  gcry_error_t err = gcry_md_open (&hd, algo, 0);
  if (err)
    emacs_hash_die ("gcry_md_open", algo, err);

  gcry_md_write (hd, buf, len);
  memcpy (resblock, emacs_hash_read (hd, algo), digest_size);
  gcry_md_close (hd);
  return resblock;
}

void *
md5_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_MD5, MD5_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha1_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA1, SHA1_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha224_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA224, SHA224_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha256_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA256, SHA256_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha384_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA384, SHA384_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha512_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA512, SHA512_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha3_224_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA3_224, SHA3_224_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha3_256_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA3_256, SHA3_256_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha3_384_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA3_384, SHA3_384_DIGEST_SIZE,
			     buf, len, resblock);
}

void *
sha3_512_buffer (const char *buf, size_t len, void *resblock)
{
  return emacs_hash_oneshot (GCRY_MD_SHA3_512, SHA3_512_DIGEST_SIZE,
			     buf, len, resblock);
}

/* Hash bytes read from STREAM until EOF.  Returns 0 on success,
   1 on read error or libgcrypt failure.  */
static int
emacs_hash_stream (int algo, size_t digest_size,
		   FILE *stream, void *resblock)
{
  emacs_hash_init_once ();

  gcry_md_hd_t hd;
  gcry_error_t err = gcry_md_open (&hd, algo, 0);
  if (err)
    return 1;

  enum { CHUNK = 32 * 1024 };
  char *buf = malloc (CHUNK);
  if (! buf)
    {
      gcry_md_close (hd);
      return 1;
    }

  for (;;)
    {
      size_t n = fread (buf, 1, CHUNK, stream);
      if (n)
	gcry_md_write (hd, buf, n);
      if (n < CHUNK)
	break;
    }

  int rc = ferror (stream) ? 1 : 0;
  free (buf);

  if (rc == 0)
    memcpy (resblock, emacs_hash_read (hd, algo), digest_size);
  gcry_md_close (hd);
  return rc;
}

int
md5_stream (FILE *stream, void *resblock)
{
  return emacs_hash_stream (GCRY_MD_MD5, MD5_DIGEST_SIZE,
			    stream, resblock);
}

int
sha1_stream (FILE *stream, void *resblock)
{
  return emacs_hash_stream (GCRY_MD_SHA1, SHA1_DIGEST_SIZE,
			    stream, resblock);
}

/* Streaming context helpers.  CTX->h is owned by libgcrypt; we open
   it on init and close it on finish.  Callers must not use a ctx
   after finish.  */
static void
ctx_init (gcry_md_hd_t *h, int algo)
{
  emacs_hash_init_once ();
  gcry_error_t err = gcry_md_open (h, algo, 0);
  if (err)
    {
      *h = NULL;
      emacs_hash_die ("gcry_md_open", algo, err);
    }
}

static void *
ctx_finish (gcry_md_hd_t *h, int algo, size_t digest_size, void *resbuf)
{
  if (! *h)
    emacs_hash_die ("gcry_md_read", algo, GPG_ERR_DIGEST_ALGO);
  memcpy (resbuf, emacs_hash_read (*h, algo), digest_size);
  gcry_md_close (*h);
  *h = NULL;
  return resbuf;
}

void
md5_init_ctx (struct md5_ctx *ctx)
{
  ctx_init (&ctx->h, GCRY_MD_MD5);
}

void
md5_process_bytes (const void *buf, size_t len, struct md5_ctx *ctx)
{
  if (ctx->h && len)
    gcry_md_write (ctx->h, buf, len);
}

void
md5_process_block (const void *buf, size_t len, struct md5_ctx *ctx)
{
  md5_process_bytes (buf, len, ctx);
}

void *
md5_finish_ctx (struct md5_ctx *ctx, void *resbuf)
{
  return ctx_finish (&ctx->h, GCRY_MD_MD5, MD5_DIGEST_SIZE, resbuf);
}

void
sha1_init_ctx (struct sha1_ctx *ctx)
{
  ctx_init (&ctx->h, GCRY_MD_SHA1);
}

void
sha1_process_bytes (const void *buf, size_t len, struct sha1_ctx *ctx)
{
  if (ctx->h && len)
    gcry_md_write (ctx->h, buf, len);
}

void *
sha1_finish_ctx (struct sha1_ctx *ctx, void *resbuf)
{
  return ctx_finish (&ctx->h, GCRY_MD_SHA1, SHA1_DIGEST_SIZE, resbuf);
}

void
sha256_init_ctx (struct sha256_ctx *ctx)
{
  ctx_init (&ctx->h, GCRY_MD_SHA256);
}

void
sha256_process_bytes (const void *buf, size_t len, struct sha256_ctx *ctx)
{
  if (ctx->h && len)
    gcry_md_write (ctx->h, buf, len);
}

void *
sha256_finish_ctx (struct sha256_ctx *ctx, void *resbuf)
{
  return ctx_finish (&ctx->h, GCRY_MD_SHA256, SHA256_DIGEST_SIZE, resbuf);
}
