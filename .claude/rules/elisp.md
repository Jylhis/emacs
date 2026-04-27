---
paths:
  - "lisp/**/*.el"
---

# Emacs Lisp Rules

## File Header

Every `.el` file must start with:
```
;;; filename.el --- Short description  -*- lexical-binding: t; -*-
```

## Indentation

- Indent with spaces only (`indent-tabs-mode: nil`), never tabs
- Use default Emacs indentation; never put closing parens on separate lines
- Fill column: 72 (including docstrings)

## Naming

- Prefix all global symbols with the library name: `my-pkg-function`
- Private/internal symbols use double-dash: `my-pkg--helper`
- Predicates: `thingp` (one word), `thing-valid-p` (multi-word)
- Face names do NOT end in `-face`

## Style

- Use `when` instead of `(if x (progn ...))`
- Use `unless` instead of `(when (not ...) ...)`
- Use `#'function-name` for function references
- Use `(1+ x)` not `(+ x 1)`, `(1- x)` not `(- x 1)`
- Use `require` for dependencies, not `load`

## Docstrings

- Every public function/variable needs a docstring
- First line: complete imperative sentence ("Return the buffer name.")
- Arguments mentioned in UPPERCASE, unquoted
- American English, two spaces between sentences
- Fill column: 72
- "Point" is a proper name (no article): "Point is at end" not "The point is at end"
- Run `checkdoc` to validate

## Defcustom

- Always include `:type`, `:version`, and `:group`
- `:version` is the first Emacs version where the option appears or its default changes

## Autoloads

- Add `;;;###autoload` cookies for user-facing commands and mode definitions
- Do not add autoload cookies for internal functions

## Byte-Compilation

- All code must byte-compile cleanly without warnings
- Fix free variable warnings with `(defvar my-external-var)` declarations
- Fix unused variable warnings by prefixing with `_`

## File Footer

```elisp
(provide 'filename)
;;; filename.el ends here
```
