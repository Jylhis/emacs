;;; cedet.el --- Setup CEDET environment  -*- lexical-binding: t; -*-

;; Copyright (C) 2002-2026 Free Software Foundation, Inc.

;; Author: David Ponce <david@dponce.com>
;; Maintainer: Eric M. Ludlam <zappo@gnu.org>
;; Version: 2.0
;; Keywords: OO, lisp

;; This file is part of GNU Emacs.

;; GNU Emacs is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; GNU Emacs is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with GNU Emacs.  If not, see <https://www.gnu.org/licenses/>.

;;; Commentary:

;;; Code:


(defconst cedet-version "2.0"
  "Current version of CEDET.")
(make-obsolete-variable 'cedet-version 'emacs-version "29.1")

(defconst cedet-packages
  `(
    ;;PACKAGE   MIN-VERSION      INSTALLDIR  DOCDIR
    (cedet         ,cedet-version "common"   "common" 	        )
    (eieio         "1.4"           nil       "eieio"       )
    (semantic      "2.2"           nil       "semantic/doc")
    (srecode       "1.2"           nil       "srecode"     )
    (ede           "1.2"           nil       "ede"         )
    )
  "Table of CEDET packages to install.")
(make-obsolete-variable 'cedet-packages 'package-built-in-p "29.1")

(defvar cedet-menu-map ;(make-sparse-keymap "CEDET menu")
  (let ((map (make-sparse-keymap "CEDET menu")))
    (define-key map [semantic-force-refresh]     #'undefined)
    (define-key map [semantic-edit-menu]         #'undefined)
    (define-key map [navigate-menu]              #'undefined)
    (define-key map [semantic-options-separator] #'undefined)
    (define-key map [global-semantic-highlight-func-mode]   #'undefined)
    (define-key map [global-semantic-stickyfunc-mode]       #'undefined)
    (define-key map [global-semantic-decoration-mode]       #'undefined)
    (define-key map [global-semantic-idle-completions-mode] #'undefined)
    (define-key map [global-semantic-idle-summary-mode]     #'undefined)
    (define-key map [global-semantic-idle-scheduler-mode]   #'undefined)
    (define-key map [global-semanticdb-minor-mode]          #'undefined)
    (define-key map [cedet-menu-separator] #'undefined)
    (define-key map [ede-find-file]        #'undefined)
    (define-key map [ede-speedbar]         #'undefined)
    (define-key map [ede]                  #'undefined)
    (define-key map [ede-new]              #'undefined)
    (define-key map [ede-target-options]   #'undefined)
    (define-key map [ede-project-options]  #'undefined)
    (define-key map [ede-build-forms-menu] #'undefined)
    map)
  "Menu keymap for the CEDET package.
This is used by `semantic-mode' and `global-ede-mode'.")

(defun cedet-version ()
  "Display the CEDET version.
This used to display per-package version information that depended
on the inversion library, which has been removed."
  (declare (obsolete emacs-version "28.1"))
  (interactive)
  (message "CEDET Version: %s" cedet-version))

(provide 'cedet)

;;; cedet.el ends here
