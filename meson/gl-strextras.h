/* Phase-2 stopgap for streq/memeq, normally provided by gnulib's
   string.in.h via configure_file substitution.  Until lib/string.in.h
   is processed natively in Meson, declare the inline functions here.
   See .claude/plans/migrate-from-current-build-replicated-gadget.md.  */

#ifndef EMACS_GL_STREXTRAS_H
#define EMACS_GL_STREXTRAS_H 1

#include <stdbool.h>
#include <string.h>

#ifndef _GL_STREQ_INLINE
# define _GL_STREQ_INLINE _GL_INLINE
#endif
#ifndef _GL_MEMEQ_INLINE
# define _GL_MEMEQ_INLINE _GL_INLINE
#endif

#ifdef __cplusplus
extern "C" {
#endif

_GL_STREQ_INLINE bool
streq (char const *__s1, char const *__s2)
{
  return !strcmp (__s1, __s2);
}

_GL_MEMEQ_INLINE bool
memeq (void const *__s1, void const *__s2, size_t __n)
{
  return !memcmp (__s1, __s2, __n);
}

#ifndef _GL_STRNUL_INLINE
# define _GL_STRNUL_INLINE _GL_INLINE
#endif

_GL_STRNUL_INLINE const char *gl_strnul (const char *__s);
_GL_STRNUL_INLINE const char *gl_strnul (const char *__s)
{
  return __s + strlen (__s);
}

/* strnul: type-generic macro that returns a pointer to STRING's
   terminating NUL byte, preserving const-ness, mirroring gnulib's
   string.in.h:1287.  */
#define strnul(s) \
  _Generic ((1 ? (s) : (void *) 0),     \
            void *       : (char *) gl_strnul (s), \
            char *       : (char *) gl_strnul (s), \
            const void * : gl_strnul (s),          \
            const char * : gl_strnul (s))

#ifdef __cplusplus
}
#endif

#endif /* EMACS_GL_STREXTRAS_H */
