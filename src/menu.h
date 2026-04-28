/* Functions to manipulate menus.
   Copyright (C) 2008-2026 Free Software Foundation, Inc.

This file is part of GNU Emacs.

GNU Emacs is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

GNU Emacs is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with GNU Emacs.  If not, see <https://www.gnu.org/licenses/>.  */

#ifndef MENU_H
#define MENU_H

#include "lisp.h"

/* Widget value structure used to describe menu items.  Inlined from
   the former lwlib/lwlib-widget.h.  */

enum button_type
{
  BUTTON_TYPE_NONE,
  BUTTON_TYPE_TOGGLE,
  BUTTON_TYPE_RADIO
};

typedef struct _widget_value
{
  /* Name of widget.  */
  Lisp_Object lname;
  char *name;

  /* Value (meaning depend on widget type).  */
  char *value;

  /* Keyboard equivalent.  */
  Lisp_Object lkey;
  char *key;

  /* Help string or nil if none.  */
  Lisp_Object help;

  /* True if enabled.  */
  bool enabled;

  /* True if selected.  */
  bool selected;

  /* True if was edited (maintained by get_value).  */
  bool edited;

  /* The type of a button.  */
  enum button_type button_type;

  /* Contents of the sub-widgets, also selected slot for checkbox.  */
  struct _widget_value *contents;

  /* Data passed to callback.  */
  void *call_data;

  /* Next one in the list.  */
  struct _widget_value *next;
} widget_value;

/* Bit fields used by terminal-specific menu_show_hook.  */

enum {
  MENU_KEYMAPS = 0x1,
  MENU_FOR_CLICK = 0x2,
  MENU_KBD_NAVIGATION = 0x4
};

extern void init_menu_items (void);
extern void finish_menu_items (void);
extern void discard_menu_items (void);
extern void save_menu_items (void);
extern bool parse_single_submenu (Lisp_Object, Lisp_Object, Lisp_Object);
extern void list_of_panes (Lisp_Object);
#ifdef HAVE_EXT_MENU_BAR
extern void free_menubar_widget_value_tree (widget_value *);
extern void update_submenu_strings (widget_value *);
extern void find_and_call_menu_selection (struct frame *, int,
                                          Lisp_Object, void *);
extern widget_value *make_widget_value (const char *, char *, bool, Lisp_Object);
extern widget_value *digest_single_submenu (int, int, bool);
#endif

#if defined (HAVE_X_WINDOWS) || defined (MSDOS)
extern Lisp_Object x_menu_show (struct frame *, int, int, int,
				Lisp_Object, const char **);
extern void x_activate_menubar (struct frame *);
#endif
#ifdef HAVE_NS
extern Lisp_Object ns_menu_show (struct frame *, int, int, int,
				 Lisp_Object, const char **);
extern void ns_activate_menubar (struct frame *);
#endif
#ifdef HAVE_PGTK
extern Lisp_Object pgtk_menu_show (struct frame *, int, int, int,
				 Lisp_Object, const char **);
extern void pgtk_activate_menubar (struct frame *);
#endif

extern Lisp_Object tty_menu_show (struct frame *, int, int, int,
				  Lisp_Object, const char **);
extern ptrdiff_t menu_item_width (const unsigned char *);
extern Lisp_Object x_popup_menu_1 (Lisp_Object position, Lisp_Object menu);
#endif /* MENU_H */
