# Lisp Runtime Internals

Sources: src/lisp.h, src/eval.c, src/data.c, src/alloc.c,
src/intervals.{c,h}, src/bytecode.c,
https://thecloudlet.github.io/technical/project/emacs-01/.

Navigation map from the blog series "Emacs Internal" framing of GNU
Emacs as a C-hosted Lisp runtime.  Cites file:line landmarks in this
tree so we do not have to re-grep on every visit.  Identifier names
only -- read the source for the bodies.

## Why a Lisp runtime in C

The blog post traces Emacs from TECO's macro language through
Stallman and Steele's decision to embed a Turing-complete Lisp, to
Gosling's C-hosted virtual machine and interpreter core.  The result
is a concrete instance of Greenspun's tenth rule: the C body of Emacs
is, in effect, an implementation of a substantial Lisp.  Everything
in this note flows from that one design choice.

## `Lisp_Object` representation

- Definition: `src/lisp.h:591` (tagged-struct variant under
  `CHECK_LISP_OBJECT_TYPE`) and `src/lisp.h:597` (plain
  `Lisp_Word` variant).  The struct variant exists only to let the C
  compiler catch `Lisp_Object x = 0;` thinkos.
- Type tag enum: `enum Lisp_Type` at `src/lisp.h:498`.
- Tag placement: `USE_LSB_TAG` selection at `src/lisp.h:252-258`;
  least-significant-bit tagging is used when pointer alignment makes
  the low bits free.
- Accessor and constructor macros: `XTYPE` (`src/lisp.h:422`),
  `XCONS` (`src/lisp.h:407`), `make_fixnum` (`src/lisp.h:461`).
- Distinguished singletons: `Qnil` and `Qt` at `src/lisp.h:376-387`.

Debug build with `--enable-check-lisp-object-type` (Meson:
`-Dcheck-lisp-object-type=true`, see `build-system.md`) selects the
struct variant so type confusion becomes a compile-time error.

## The seven primitives

The McCarthy/Graham minimal set from the blog post, located in this
tree:

| Primitive | DEFUN site         |
|-----------|--------------------|
| quote     | `src/eval.c:507`   |
| eq        | `src/data.c:168`   |
| atom      | `src/data.c:321`   |
| car       | `src/data.c:659`   |
| cdr       | `src/data.c:677`   |
| cons      | `src/alloc.c:2577` |
| cond      | `src/eval.c:403`   |

`quote` and `cond` live in `eval.c` because they are special forms:
their arguments are not evaluated before dispatch.  `car`, `cdr`,
`atom`, and `eq` are ordinary subrs in `data.c`.  `cons` is in
`alloc.c` because constructing a cons cell is fundamentally an
allocation.

## Evaluator core

- `Feval` -- the Lisp-callable entry point: `src/eval.c:2529`.
- `eval_sub` -- the recursive workhorse used by both `Feval` and
  internal callers: `src/eval.c:2566`.
- `Ffuncall` -- function application: `src/eval.c:3166`.
- `apply_lambda` -- closure application path: `src/eval.c:3296`.

`eval_sub` dispatches on the form's head: special forms run inline,
macros expand and recurse, everything else funnels through
`Ffuncall`.  This is the tree-walking interpreter; the bytecode VM
below is the compiled fast path.

## Cons allocator

- Block struct: `struct cons_block` at `src/alloc.c:2517`.
- Block-pool management and free list: `src/alloc.c:2539-2603`.
- `Fcons` itself: `src/alloc.c:2577`.

Cells are carved out of fixed-size blocks rather than malloc'd
individually, which keeps GC scanning cache-friendly.  Per
`.claude/rules/c-core.md`, GCPRO is gone -- use
`record_unwind_protect` and avoid holding raw C pointers to Lisp data
across calls that can trigger a collection.

## Interval tree

Text properties and overlay metadata hang off a self-balancing
interval tree per buffer or string.

- `create_root_interval`: `src/intervals.c:87`.
- `split_interval_left` / `split_interval_right`: `src/intervals.c:534`
  / `src/intervals.c:490`.
- `balance_an_interval`: `src/intervals.c:375`.
- Public declarations: `src/intervals.h:251-261`.

The tree's invariants -- segment lengths, parent pointers, and
text-property inheritance -- are what make `put-text-property` and
overlays cheap on large buffers.

## Bytecode VM

`exec_byte_code` at `src/bytecode.c:481` is the stack-based VM that
runs compiled Lisp.  It is the optimised counterpart to `eval_sub`
above: same semantics, different dispatch.  Compiled-function objects
are produced by `lisp/emacs-lisp/bytecomp.el` and consumed here.

## Open follow-ups

Hook for later installments in the blog series.  Topics flagged in
post #01 that this note will need when they land:

- Minimal Lisp interpreter walkthrough built from the seven
  primitives.
- `Lisp_Object` deep dive (the full tag table, conversion paths).
- Tagged-union design alternatives and why Emacs chose its scheme.
- Interval-tree algorithmic details (balancing, merging).
