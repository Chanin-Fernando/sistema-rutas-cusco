"""Utilidades para aplicar cambios de tema a widgets Tk existentes."""

import tkinter as tk
from typing import Dict, Optional


def _norm(color) -> Optional[str]:
    if not color or not isinstance(color, str):
        return None
    c = color.strip().lower()
    if c in ("", "systembuttonface", "systemwindow"):
        return None
    return c


def build_color_map(old_palette: dict, new_palette: dict) -> dict:
    """Mapea colores del tema anterior al nuevo (por clave de paleta)."""
    mapping = {}
    for key in old_palette:
        old_c = _norm(old_palette.get(key))
        new_c = new_palette.get(key)
        if old_c and new_c and old_c not in mapping:
            mapping[old_c] = new_c
    return mapping


def translate(color: Optional[str], color_map: Dict[str, str]) -> Optional[str]:
    if not color:
        return None
    n = _norm(color)
    if n and n in color_map:
        return color_map[n]
    return None


def apply_text_tags(txt: tk.Text, palette: dict) -> None:
    txt.tag_config("titulo", foreground=palette["accent"],
                   font=("Segoe UI", 10, "bold"))
    txt.tag_config("subtitulo", foreground=palette["text2"],
                   font=("Segoe UI", 9, "bold"))
    txt.tag_config("ok", foreground=palette["success"])
    txt.tag_config("warn", foreground=palette["danger"])
    txt.tag_config("info", foreground=palette["info"])
    txt.tag_config("dim", foreground=palette["text3"])
    txt.tag_config("yellow", foreground=palette["warning"])


def retheme_widget(widget, color_map: dict, palette: dict) -> None:
    cls = widget.winfo_class()

    try:
        if cls in ("Frame", "Toplevel", "Label", "Button", "Canvas", "Spinbox", "Entry"):
            bg = translate(widget.cget("bg"), color_map)
            if bg:
                widget.config(bg=bg)

        if cls in ("Label", "Button", "Entry", "Spinbox"):
            fg = translate(widget.cget("fg"), color_map)
            if fg:
                widget.config(fg=fg)

        if cls == "Button":
            for opt in ("activebackground", "activeforeground"):
                try:
                    val = translate(widget.cget(opt), color_map)
                    if val:
                        widget.config(**{opt: val})
                except tk.TclError:
                    pass

        if cls in ("Entry", "Spinbox"):
            for opt in ("highlightbackground", "insertbackground"):
                try:
                    val = translate(widget.cget(opt), color_map)
                    if val:
                        widget.config(**{opt: val})
                except tk.TclError:
                    pass
            if cls == "Spinbox":
                try:
                    val = translate(widget.cget("buttonbackground"), color_map)
                    if val:
                        widget.config(buttonbackground=val)
                except tk.TclError:
                    pass

        if cls == "Text":
            bg = translate(widget.cget("bg"), color_map)
            fg = translate(widget.cget("fg"), color_map)
            if bg:
                widget.config(bg=bg)
            if fg:
                widget.config(fg=fg)
            ins = translate(widget.cget("insertbackground"), color_map)
            sel = translate(widget.cget("selectbackground"), color_map)
            if ins:
                widget.config(insertbackground=ins)
            if sel:
                widget.config(selectbackground=sel)
            apply_text_tags(widget, palette)

    except tk.TclError:
        pass

    for child in widget.winfo_children():
        retheme_widget(child, color_map, palette)


def retheme_tree(root, old_palette: dict, new_palette: dict) -> None:
    color_map = build_color_map(old_palette, new_palette)
    retheme_widget(root, color_map, new_palette)
