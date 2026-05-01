# Conventions and Style Notes

Sources: CONTRIBUTE, admin/notes/documentation, admin/notes/spelling,
admin/notes/newfile, admin/notes/versioning, admin/notes/jargon,
.dir-locals.el.

## Language and spelling (admin/notes/spelling)

- American English: "behavior" not "behaviour".
- Two spaces between sentences.
- Emacs's (not Emacs') for possessive.
- "Point" is a proper name -- no article.  "Move point" not "Move the
  point".
- Prefer active voice over passive.
- Do not abbreviate "Emacs Lisp" in docs.  Say "Lisp" if unambiguous.
  If you must abbreviate, capitalize: "Elisp".

## etc/NEWS style (admin/notes/documentation)

- Entry headings: one line, end with period.
- Section headings: not full sentences, not Lisp symbols.
  "Random mode" not "'random-mode'".
- Lisp symbols quoted 'like-this' (clickable in view-emacs-news).
- Arguments in UPPER CASE, not quoted.
- File/buffer/process names in "double quotes".
- External programs in "double quotes".
- Manuals referenced as "(elisp) Documentation Tips".
- Check result with `emacs-news-view-mode` before pushing.

## Adding new files (admin/notes/newfile)

1. Verify copyright assignment/disclaimer.
2. Match standard Emacs header template.
3. Check filename is DOS-safe (8+3): `find . -print | doschk`.
4. Commit in author's name, not yours.
5. Verify it compiles and Emacs builds.
6. Consider acknowledgment in doc/emacs/emacs.texi.
7. Add NEWS entry if appropriate.
8. Update make-dist if non-standard filename.

## Versioning (admin/notes/versioning)

Format: major.minor[.devel].build

- Bugfix releases: minor += 1.
- Non-bugfix releases: major += 1, minor = 1.
- Development: devel = 50 (e.g., 31.0.50).
- Pretests: devel = 90, 91, ...
- Release candidates: devel component removed.

## .dir-locals.el key settings

- `tab-width`: 8 (all modes)
- `sentence-end-double-space`: t
- `fill-column`: 72
- `c-file-style`: "GNU" (C, Java, ObjC)
- `indent-tabs-mode`: t (C, Java, ObjC), nil (Elisp, lisp-data)
- `log-edit`: fill-column 64, summary target 50 chars
- `bug-reference-url-format`: https://debbugs.gnu.org/%s

## Jargon (admin/notes/jargon)

Common terms on emacs-devel:
- **DTRT**: Do The Right Thing
- **DWIM**: Do What I Mean
- **ENOPATCH**: No patch attached
- **gross**: Inelegant but working solution
- **hysterical raisins**: Historical reasons
- **install on <foo>**: Push to Git branch <foo>
- **paper cut**: Minor annoying issue, easy to fix
- **yak shaving**: Tangential tasks to reach a goal
- **notabug/wontfix**: Issue classifications

Common abbreviations: IIRC, IIUC, FWIW, LGTM, WIP, YMMV, IOW, OTOH.
