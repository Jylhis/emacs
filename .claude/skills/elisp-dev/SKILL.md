---
description: Write, modify, and review Emacs Lisp code following GNU Emacs conventions. Auto-invoked when working with .el files.
user-invocable: false
---

# Emacs Lisp Development

## Conventions

### File Template

New `.el` files must follow this structure:

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

### Naming Rules

- All global symbols prefixed with the library name: `my-lib-function`
- Internal symbols use double-dash: `my-lib--helper`
- Predicates: `thingp` (one word) or `thing-valid-p` (multi-word)
- Commands that toggle: `my-lib-mode`, `my-lib-toggle-feature`
- Custom variables: `my-lib-default-value`
- Constants: `my-lib-version`

### Idiomatic Patterns

Prefer:
```elisp
(when condition body...)          ; not (if condition (progn body...))
(unless condition body...)        ; not (when (not condition) body...)
(pcase val clauses...)            ; for complex conditional dispatch
(seq-filter #'pred sequence)      ; for filtering
(thread-last val (f1) (f2) (f3)) ; for data pipelines
(with-current-buffer buf body...) ; not (save-excursion (set-buffer ...))
(1+ n)                            ; not (+ n 1)
```

Avoid:
```elisp
(eval-after-load ...)            ; use with-eval-after-load
(setq my-hook (cons ...))        ; use add-hook
'(lambda ...)                    ; use #'(lambda ...) or (lambda ...)
```

### Docstring Rules

```elisp
(defun my-lib-do-thing (buffer &optional quietly)
  "Perform the thing on BUFFER.
If QUIETLY is non-nil, suppress messages.
Return the result as a string."
  ...)
```

- First line: complete imperative sentence, fits in one line
- Arguments mentioned in UPPERCASE
- Mention return value
- Run `M-x checkdoc` to validate

### Defcustom Guidelines

```elisp
(defcustom my-lib-threshold 10
  "Maximum number of items to display.
Setting this to nil means no limit."
  :type 'natnum
  :version "31.1"
  :group 'my-lib)
```

- Always include `:type`, `:version`, and `:group`
- `:version` is the first Emacs version where the option appears or changes default

### Testing

- Write ERT tests in `test/lisp/` mirroring the source path
- Tag slow tests with `:tags '(:expensive-test)`
- Test structure:

```elisp
(ert-deftest my-lib-test-basic-behavior ()
  "Verify that my-lib-do-thing returns expected result."
  (should (equal (my-lib-do-thing (get-buffer-create "*test*"))
                 "expected")))
```

### Byte-Compilation

- All code must byte-compile cleanly without warnings
- Run `make lisp/path/to/file.elc` to check
- Fix free variable warnings with `(defvar my-external-var)` declarations
- Fix unused variable warnings by prefixing with `_`

### Validation Checklist

Before submitting changes to `.el` files:

1. Byte-compiles without warnings
2. `checkdoc` passes on all modified functions
3. ERT tests pass: `make -C test relevant-tests`
4. Follows naming conventions (prefix, predicates, private symbols)
5. Docstrings present for all public API
6. `lexical-binding` enabled in file header
