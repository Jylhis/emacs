# Lisp_Object Tagging Notes

## Source

Synthesis of <https://thecloudlet.github.io/technical/project/emacs-03/>
("Emacs Internal #03: Tagged Union, Tagged Pointer, and Poor Man's
Inheritance"), grounded in the current source.  The post describes the
existing implementation -- nothing in `src/` needs to change.

## Why pointer tagging

Emacs implements dynamic typing in C.  Three options for "any value":

- **Tagged union (unboxed)**: `struct { int tag; union { ... }; }`.
  Sized by the largest member, wastes memory.  Like C++17
  `std::variant`.
- **Tagged pointer (boxed)**: pointer with type bits stuffed into the
  alignment slack.  Word-sized, requires aligned heap allocation.
  Emacs's choice.
- **Fat pointer**: `(tag, pointer)` pair, double-word.  Used by Go,
  Rust trait objects.  Unlimited types but doubles size.

## Primary tags (3 bits)

`enum Lisp_Type` at `src/lisp.h:498-525`, with the layout diagram
preceding it at `src/lisp.h:488-497`:

| Tag             | Value (LSB)     | Payload                                      |
|-----------------|-----------------|----------------------------------------------|
| `Lisp_Symbol`   | 0               | offset from `lispsym` to `struct Lisp_Symbol` |
| `Lisp_Type_Unused0` | 1           | reserved (blog post omits this)              |
| `Lisp_Int0`     | 2               | fixnum, low bit 0                            |
| `Lisp_Int1`     | 6 (LSB) / 3 (MSB) | fixnum, low bit 1                          |
| `Lisp_String`   | 4               | pointer to `struct Lisp_String`              |
| `Lisp_Vectorlike` | 5             | pointer to `union vectorlike_header`         |
| `Lisp_Cons`     | 3 (LSB) / 6 (MSB) | pointer to `struct Lisp_Cons`              |
| `Lisp_Float`    | 7               | pointer to `struct Lisp_Float`               |

Note: `Lisp_Cons` and `Lisp_Int1` swap numeric values depending on
`USE_LSB_TAG` (`src/lisp.h:508,521`).

Supporting machinery in `src/lisp.h`:

- `:76-78` -- `GCTYPEBITS = 3` (number of tag bits)
- `:222-228` -- `VALBITS = EMACS_INT_WIDTH - GCTYPEBITS`,
  `FIXNUM_BITS = VALBITS + 1`
- `:245,277-282` -- `IDEAL_GCALIGNMENT = 8`, with
  `static_assert (GCALIGNMENT == 1 << GCTYPEBITS)`
- `:252-260` -- `USE_LSB_TAG` is true when the host's pointer width
  fits within `VAL_MAX / 2`; otherwise tags go in the high bits
- `:582-597` -- `Lisp_Object` is either `Lisp_Word` (a plain integer)
  or, with `CHECK_LISP_OBJECT_TYPE`, a one-field struct wrapper to
  catch implicit `Lisp_Object x = 0;` mistakes
- `:697-735` -- `XLI` / `XIL` / `XLP` / `XTYPE` -- the only sanctioned
  conversions between `Lisp_Object`, the underlying integer, and a
  `void *`.  Bitwise ops on raw pointers are UB; these go through
  integer types.

## Secondary tags (pvec_type)

When the primary tag is `Lisp_Vectorlike`, the pointed-to object's
first word (the `union vectorlike_header`, `src/lisp.h:924-956`) is
either a plain vector size or a pseudovector descriptor.  Layout
diagram is in the source comments at the same lines:

```
  1   1                    W-2
+---+---+-------------------------------------+
| M | 0 |                 SIZE                |  vector
+---+---+-------------------------------------+

  1   1    W-32      6       12         12
+---+---+--------+------+----------+----------+
| M | 1 | unused | TYPE | RESTSIZE | LISPSIZE |  pseudovector
+---+---+--------+------+----------+----------+
```

- `M` = `ARRAY_MARK_FLAG` (GC mark bit), `src/lisp.h:967-969`
- bit below it = `PSEUDOVECTOR_FLAG`, `src/lisp.h:973-975`
- `TYPE` = `enum pvec_type` value, extracted with `PVEC_TYPE_MASK`
  (`src/lisp.h:1041`) shifted by `PSEUDOVECTOR_AREA_BITS`
  (`src/lisp.h:1040`)
- `LISPSIZE` Lisp_Object slots get traced by GC; `RESTSIZE` raw words
  do not

The full pseudovector tag set is `enum pvec_type` at
`src/lisp.h:980-1021` -- ~35 entries through `PVEC_FONT`, with
`PVEC_TAG_MAX = PVEC_FONT` as the upper bound.  Set with
`XSETPSEUDOVECTOR` (`src/lisp.h:1362`).

## Poor man's inheritance: header-first invariant

Every pseudovector struct embeds `union vectorlike_header header` as
its first field, so a `union vectorlike_header *` can be safely cast
to the concrete type after inspecting the TYPE bits.  Examples:

- `src/lisp.h:958-963` -- `struct Lisp_Symbol_With_Pos`
- `src/lisp.h:1729` -- `struct Lisp_Vector`
- `src/buffer.h:319-321` -- `struct buffer`
- `src/window.h:100-103` -- `struct window`
- `src/frame.h:144` -- `struct frame`
- `src/process.h:44` -- `struct Lisp_Process`

Aligned via `GCALIGNED_STRUCT` (`src/lisp.h:307`) so the low 3 bits
remain free for tagging; `static_assert (GCALIGNED (T))` enforces it
(e.g. `src/lisp.h:830,1447,1580,2214`).

## Defining a new Lisp type

In-source recipe at `src/lisp.h:539-580`.  Summary:

1. Add a member to `enum pvec_type`.
2. Add switch arms in `src/print.c` (`print_object`, possibly
   `print_preprocess`) and `src/alloc.c` (`mark_object`, `gc_sweep`).
3. Add a switch arm in `src/data.c` (`Fcl_type_of`) and a clause in
   `lisp/emacs-lisp/cl-preloaded.el` (`cl--define-builtin-type`).
4. Keep the type below `VBLOCK_BYTES_MAX` (defined in `alloc.c`) or
   teach `sweep_vectors` about it.
5. For pointer-to-C-struct payloads with no Lisp slots, prefer the
   existing `Lisp_Misc_Ptr` / `PVEC_OTHER` instead of inventing a new
   tag.

## Related upstream documentation

`doc/lispref/internals.texi:~2151` already documents the tagged-pointer
model in the Lisp Reference Manual.  Do not duplicate that text in
docstrings or NEWS; cross-reference it instead.

## Outside-Emacs analogues (from the article)

- LLVM disables RTTI (`-fno-rtti`) and reimplements via integer
  `SubclassID` plus templated `isa<>` / `cast<>`; provides
  `PointerIntPair<>` for the same trick at smaller granularity.
- Linux kernel red-black trees stash node color in the parent
  pointer's low bits.
- LuaJIT NaN-boxes pointers inside IEEE-754 double payloads.
- PostgreSQL packs flags into tuple-header bit fields.
- ARM64 Top Byte Ignore makes the high 8 bits of a virtual address
  available as hardware-level tags.

## Safety caveat

Direct pointer-bit arithmetic is undefined behavior under modern
C/C++.  Emacs routes everything through `Lisp_Word`-as-integer and the
`XLI` / `XIL` / `XLP` macros (`src/lisp.h:697-735`), which is why
those macros exist instead of inline pointer casts at every call
site.  Don't bypass them.
