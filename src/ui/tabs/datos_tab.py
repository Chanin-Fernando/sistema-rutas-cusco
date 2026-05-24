import tkinter as tk
from tkinter import ttk
from ...data import generar_pedidos

class DatosTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = tk.Frame(notebook, bg=app.COLORES["bg"])
        notebook.add(self.tab, text="📦 DATOS")
        self._crear_widgets()

    def _crear_widgets(self):
        c = self.app.COLORES
        ctrl = tk.Frame(self.tab, bg=c["bg"])
        ctrl.pack(fill=tk.X, pady=4)

        self._boton(ctrl, "⟳ Regenerar pedidos", self._regenerar).pack(side=tk.LEFT, padx=4)

        tk.Label(ctrl, text="Cantidad:", bg=c["bg"],
                 fg=c["text2"], font=("Courier New", 9)).pack(side=tk.LEFT, padx=6)
        self.var_n = tk.IntVar(value=12)
        sp = tk.Spinbox(ctrl, from_=4, to=20, textvariable=self.var_n,
                        width=4, bg=c["card"], fg=c["text"],
                        font=("Courier New", 9), buttonbackground=c["card"])
        sp.pack(side=tk.LEFT)

        cols = ("ID", "Cliente", "Sector", "Coord X", "Coord Y",
                "Prioridad", "Peso (kg)", "Valor (S/)")
        self.tree_datos = self._tabla(self.tab, cols)
        self._llenar_datos()

        tk.Label(self.tab, text="REPARTIDORES",
                 bg=c["bg"], fg=c["accent"],
                 font=("Courier New", 10, "bold")).pack(pady=(10, 2))

        cols_r = ("ID", "Nombre", "Pos X", "Pos Y", "Capacidad (kg)")
        self.tree_reps = self._tabla(self.tab, cols_r, height=4)
        for r in self.app.repartidores:
            self.tree_reps.insert("", tk.END,
                values=(r.id, r.nombre, r.pos_x, r.pos_y, r.capacidad_max))

        self.app.actualizar_mapa(pedidos_resaltados=self.app.pedidos)

    def _llenar_datos(self):
        self.tree_datos.delete(*self.tree_datos.get_children())
        PRIO = {1: "🔴 Urgente", 2: "🟡 Normal", 3: "🟢 Baja"}
        for p in self.app.pedidos:
            self.tree_datos.insert("", tk.END, values=(
                p.id, p.cliente, p.sector, p.coord_x, p.coord_y,
                PRIO[p.prioridad], p.peso, f"{p.valor:.2f}"
            ))

    def _regenerar(self):
        self.app.pedidos = generar_pedidos(self.var_n.get())
        self._llenar_datos()
        self.app.actualizar_mapa(pedidos_resaltados=self.app.pedidos)

    def _tabla(self, parent, cols, height=10):
        frame = tk.Frame(parent, bg=self.app.COLORES["bg"])
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        sb_h = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             height=height,
                             yscrollcommand=sb.set,
                             xscrollcommand=sb_h.set)
        sb.config(command=tree.yview)
        sb_h.config(command=tree.xview)
        for col in cols:
            ancho = 80 if len(col) < 8 else 120
            tree.heading(col, text=col)
            tree.column(col, width=ancho, anchor=tk.CENTER)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        sb_h.pack(side=tk.BOTTOM, fill=tk.X)
        return tree

    def _boton(self, parent, texto, comando):
        c = self.app.COLORES
        return tk.Button(parent, text=texto, command=comando,
                         bg=c["accent"], fg="white",
                         font=("Courier New", 9, "bold"),
                         relief=tk.FLAT, padx=12, pady=4,
                         activebackground=c["card"],
                         activeforeground=c["accent"],
                         cursor="hand2")