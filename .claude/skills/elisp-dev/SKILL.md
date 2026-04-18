---
description: Write, modify, and review Emacs Lisp code following GNU Emacs conventions. Auto-invoked when working with .el files.
user-invocable: false
---

# Emacs Lisp Development

## File Template

```elisp
;;; filename.el --- Short description  -*- lexical-binding: t; -*-

;; Copyright (C) 2026 Free Software Foundation, Inc.

;; Author: Name <email>
;; Keywords: relevant, keywords

;; This file is part of GNU Emacs.

;;; Commentary:

;; Description of the file's purpose.

;;; Code:

(require 'needed-dependency)

;; ... implementation ...

(provide 'filename)
;;; filename.el ends here
```

## Naming

- All global symbols prefixed with the library name: `my-lib-function`
- Internal symbols use double-dash: `my-lib--helper`
- Predicates: `thingp` (one word) or `thing-valid-p` (multi-word)
- Commands that toggle: `my-lib-mode`
- Face names do NOT end in `-face`

## Idiomatic Patterns

```elisp
(when condition body...)          ; not (if condition (progn body...))
(unless condition body...)        ; not (when (not condition) body...)
(pcase val clauses...)            ; for complex conditional dispatch
(with-current-buffer buf body...) ; not (save-excursion (set-buffer ...))
(1+ n)                            ; not (+ n 1)
#'function-name                   ; not 'function-name for function refs
```

## Docstrings

```elisp
(defun my-lib-do-thing (buffer &optional quietly)
  "Perform the thing on BUFFER.
If QUIETLY is non-nil, suppress messages.  Return the
result as a string."
  ...)
```

- First line: complete imperative sentence, fits in one line
- Arguments in UPPERCASE, unquoted
- Fill column: 72 (per .dir-locals.el)
- Two spaces between sentences
- "Point" with no article: "Move point" not "Move the point"
- Run `M-x checkdoc` to validate

## Defcustom

```elisp
(defcustom my-lib-threshold 10
  "Maximum number of items to display.
Setting this to nil means no limit."
  :type 'natnum
  :version "31.1"
  :group 'my-lib)
```

- Always include `:type`, `:version`, and `:group`
- `:version` is the first Emacs version where the option appears or its default changes

## Indentation and Whitespace

- Spaces only (`indent-tabs-mode: nil`), never tabs
- Fill column: 72
- No trailing whitespace
- No SPC immediately followed by TAB in indentation (commit hook rejects this)

## Testing

- Write ERT tests in `test/lisp/` mirroring the source path
- Tag slow tests with `:tags '(:expensive-test)`
- Run before committing: `make && make -C test relevant-tests`

## Byte-Compilation

- All code must byte-compile cleanly without warnings
- Fix free variable warnings with `(defvar my-external-var)` declarations
- Fix unused variable warnings by prefixing with `_`
