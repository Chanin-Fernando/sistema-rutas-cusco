"""
Clase base para todos los tabs. Provee utilidades de UI con estilo Google Maps.
"""
import tkinter as tk
from tkinter import ttk

class BaseTab:
    """Mixin con helpers de UI para los tabs del sidebar."""

    def _make_frame(self, notebook_parent):
        """Crea el frame principal del tab y lo registra en la app."""
        c = self.app.COLORES
        frame = tk.Frame(notebook_parent, bg=c["panel_bg"])
        self.app.register_tab_frame(frame)
        return frame

    # ── Encabezado de sección ─────────────────────────────────────────────
    def _seccion(self, parent, titulo, subtitulo=""):
        c = self.app.COLORES
        f = tk.Frame(parent, bg=c["panel_bg"])
        f.pack(fill=tk.X, padx=16, pady=(14, 4))
        tk.Label(f, text=titulo, bg=c["panel_bg"], fg=c["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        if subtitulo:
            tk.Label(f, text=subtitulo, bg=c["panel_bg"], fg=c["text3"],
                     font=("Segoe UI", 8)).pack(anchor=tk.W)
        tk.Frame(parent, bg=c["separator"], height=1).pack(fill=tk.X, padx=0)

    # ── Botón primario estilo Google ──────────────────────────────────────
    def _boton(self, parent, texto, comando, color=None):
        c = self.app.COLORES
        col = color or c["accent"]
        btn = tk.Button(parent, text=texto, command=comando,
                        bg=col, fg="white",
                        font=("Segoe UI", 9, "bold"),
                        relief=tk.FLAT, padx=16, pady=7,
                        cursor="hand2", bd=0,
                        activebackground=c["accent_dark"],
                        activeforeground="white")
        def on_enter(e): btn.config(bg=c["accent_dark"])
        def on_leave(e): btn.config(bg=col)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ── Botón secundario (chip) ───────────────────────────────────────────
    def _chip(self, parent, texto, comando):
        c = self.app.COLORES
        btn = tk.Button(parent, text=texto, command=comando,
                        bg=c["chip_bg"], fg=c["accent"],
                        font=("Segoe UI", 9), relief=tk.FLAT,
                        padx=12, pady=5, cursor="hand2", bd=0,
                        activebackground=c["tag_blue"],
                        activeforeground=c["accent"])
        return btn

    # ── Área de texto con scroll (log) ────────────────────────────────────
    def _text_area(self, parent, height=None):
        c = self.app.COLORES
        outer = tk.Frame(parent, bg=c["separator"], bd=0)
        outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 10))

        inner = tk.Frame(outer, bg=c["panel_bg"])
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        sb = ttk.Scrollbar(inner, style="TScrollbar")
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        kw = dict(height=height) if height else {}
        txt = tk.Text(inner, bg=c["panel_bg"], fg=c["text"],
                      font=("Consolas", 9), relief=tk.FLAT,
                      padx=12, pady=10, yscrollcommand=sb.set,
                      insertbackground=c["accent"],
                      selectbackground=c["tag_blue"],
                      wrap=tk.WORD, **kw)
        txt.pack(fill=tk.BOTH, expand=True)
        sb.config(command=txt.yview)
        # Tags
        txt.tag_config("titulo", foreground=c["accent"],
                       font=("Segoe UI", 10, "bold"))
        txt.tag_config("subtitulo", foreground=c["text2"],
                       font=("Segoe UI", 9, "bold"))
        txt.tag_config("ok", foreground=c["success"])
        txt.tag_config("warn", foreground=c["danger"])
        txt.tag_config("info", foreground=c["info"])
        txt.tag_config("dim", foreground=c["text3"])
        txt.tag_config("yellow", foreground=c["warning"])
        return txt

    def _actualizar_text(self, txt, lines):
        txt.config(state=tk.NORMAL)
        txt.delete("1.0", tk.END)
        for ln in lines:
            if ln.startswith("──") or ln.startswith("🏆"):
                txt.insert(tk.END, ln + "\n", "titulo")
            elif ln.startswith("  ★") or ln.startswith("Valor máx"):
                txt.insert(tk.END, ln + "\n", "subtitulo")
            elif any(ln.startswith(x) for x in ["✓", "✔", "Nueva mejor"]):
                txt.insert(tk.END, ln + "\n", "ok")
            elif any(ln.startswith(x) for x in ["✗", "✘", "⚠", "❌", "ERROR"]):
                txt.insert(tk.END, ln + "\n", "warn")
            elif ln.startswith("  •") or ln.startswith("  Ruta") or ln.startswith("  Cuad"):
                txt.insert(tk.END, ln + "\n", "info")
            elif ln.strip() == "":
                txt.insert(tk.END, "\n", "dim")
            else:
                txt.insert(tk.END, ln + "\n")
        txt.config(state=tk.DISABLED)
        txt.see(tk.END)

    # ── Tabla Treeview ────────────────────────────────────────────────────
    def _tabla(self, parent, cols, height=8):
        c = self.app.COLORES
        outer = tk.Frame(parent, bg=c["panel_border"])
        outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 8))
        inner = tk.Frame(outer, bg=c["panel_bg"])
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        sb_v = ttk.Scrollbar(inner, orient=tk.VERTICAL)
        sb_h = ttk.Scrollbar(inner, orient=tk.HORIZONTAL)
        tree = ttk.Treeview(inner, columns=cols, show="headings",
                             height=height,
                             yscrollcommand=sb_v.set,
                             xscrollcommand=sb_h.set)
        sb_v.config(command=tree.yview)
        sb_h.config(command=tree.xview)
        for col in cols:
            w = 55 if len(col) <= 4 else (95 if len(col) <= 8 else 120)
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=tk.CENTER, minwidth=40)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_v.pack(side=tk.RIGHT, fill=tk.Y)
        sb_h.pack(side=tk.BOTTOM, fill=tk.X)
        return tree

    # ── Label resultado ───────────────────────────────────────────────────
    def _resultado_label(self, parent):
        c = self.app.COLORES
        f = tk.Frame(parent, bg=c["tag_blue"], relief=tk.FLAT)
        lbl = tk.Label(f, text="", bg=c["tag_blue"], fg=c["accent"],
                       font=("Segoe UI", 9), wraplength=330,
                       justify=tk.LEFT, padx=10, pady=6)
        lbl.pack(fill=tk.X)
        return f, lbl

    # ── Fila de control ───────────────────────────────────────────────────
    def _ctrl_row(self, parent):
        c = self.app.COLORES
        row = tk.Frame(parent, bg=c["panel_bg"])
        row.pack(fill=tk.X, padx=12, pady=4)
        return row

    def _label(self, parent, text, small=False):
        c = self.app.COLORES
        size = 8 if small else 9
        return tk.Label(parent, text=text, bg=c["panel_bg"], fg=c["text2"],
                        font=("Segoe UI", size))

    def _separador(self, parent):
        tk.Frame(parent, bg=self.app.COLORES["separator"], height=1).pack(
            fill=tk.X, pady=6)
