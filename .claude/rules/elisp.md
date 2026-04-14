---
paths:
  - "lisp/**/*.el"
  - "test/**/*.el"
---

# Emacs Lisp Rules

## File Header

Every `.el` file must start with:
```
;;; filename.el --- Short description  -*- lexical-binding: t; -*-
```

## Naming

- Prefix all global symbols with the library name: `my-pkg-function`
- Private/internal symbols use double-dash: `my-pkg--helper`
- Predicates: `thingp` (one word), `thing-valid-p` (multi-word)
- Face names do NOT end in `-face`

## Style

- Use default Emacs indentation; never put closing parens on separate lines
- Lines should not exceed 80 characters
- Use `when` instead of `(if x (progn ...))`
- Use `unless` instead of `(when (not ...) ...)`
- Use `#'function-name` for function references
- Use `(1+ x)` not `(+ x 1)`, `(1- x)` not `(- x 1)`
- Use `require` for dependencies, not `load`

## Docstrings

- Every public function/variable needs a docstring
- First line: complete imperative sentence ("Return the buffer name.")
- Arguments mentioned in UPPERCASE
- American English, two spaces between sentences
- Run `checkdoc` to validate

## File Footer

End every file with:
```elisp
(provide 'filename)
;;; filename.el ends here
```

## Autoloads

- Add `;;;###autoload` cookies for user-facing commands and mode definitions
- Do not add autoload cookies for internal functions

## Defcustom

- Always include `:type`, `:version`, and `:group`
- `:version` is the first Emacs version where the option appears or its default changes
