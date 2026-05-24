import tkinter as tk
from tkinter import ttk
import time
from ...algorithms import OrdenacionBusqueda

class OrdenacionTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = tk.Frame(notebook, bg=app.COLORES["bg"])
        notebook.add(self.tab, text="🔢 ORDENACIÓN")
        self._crear_widgets()

    def _crear_widgets(self):
        c = self.app.COLORES
        self._seccion(self.tab, "QuickSort  |  O(n log n) promedio")
        ctrl = tk.Frame(self.tab, bg=c["bg"])
        ctrl.pack(fill=tk.X, pady=4)
        tk.Label(ctrl, text="Ordenar por:", bg=c["bg"],
                 fg=c["text2"], font=("Courier New", 9)).pack(side=tk.LEFT)
        self.var_criterio = tk.StringVar(value="prioridad")
        cb = ttk.Combobox(ctrl, textvariable=self.var_criterio, width=16,
                          values=["prioridad", "valor", "peso", "distancia_origen"],
                          state="readonly", font=("Courier New", 9))
        cb.pack(side=tk.LEFT, padx=6)
        self._boton(ctrl, "▶ Ordenar", self._ejecutar_ordenacion).pack(side=tk.LEFT, padx=4)

        cols = ("ID", "Cliente", "Sector", "Prioridad", "Peso (kg)", "Valor (S/)")
        self.tree_ord = self._tabla(self.tab, cols)

        self._seccion(self.tab, "Búsqueda Binaria  |  O(log n)")
        ctrl2 = tk.Frame(self.tab, bg=c["bg"])
        ctrl2.pack(fill=tk.X, pady=4)
        tk.Label(ctrl2, text="ID pedido:", bg=c["bg"],
                 fg=c["text2"], font=("Courier New", 9)).pack(side=tk.LEFT)
        self.var_busq_id = tk.IntVar(value=1)
        tk.Spinbox(ctrl2, from_=1, to=50, textvariable=self.var_busq_id,
                   width=5, bg=c["card"], fg=c["text"],
                   font=("Courier New", 9), buttonbackground=c["card"]
                   ).pack(side=tk.LEFT, padx=6)
        self._boton(ctrl2, "🔍 Buscar por ID", self._buscar_id).pack(side=tk.LEFT, padx=4)
        tk.Label(ctrl2, text="  |  Sector:", bg=c["bg"],
                 fg=c["text2"], font=("Courier New", 9)).pack(side=tk.LEFT)
        self.var_busq_sec = tk.StringVar(value="Wanchaq")
        tk.Entry(ctrl2, textvariable=self.var_busq_sec, width=14,
                 bg=c["card"], fg=c["text"],
                 font=("Courier New", 9)).pack(side=tk.LEFT, padx=4)
        self._boton(ctrl2, "🔍 Buscar por sector", self._buscar_sector).pack(side=tk.LEFT)

        self.lbl_busq = tk.Label(self.tab, text="",
            bg=c["bg"], fg=c["success"], font=("Courier New", 9),
            wraplength=700, justify=tk.LEFT)
        self.lbl_busq.pack(pady=4, anchor=tk.W, padx=8)

    def _ejecutar_ordenacion(self):
        ob = OrdenacionBusqueda()
        t0 = time.perf_counter()
        ordenados = ob.quicksort_pedidos(self.app.pedidos, self.var_criterio.get())
        elapsed = (time.perf_counter() - t0) * 1000
        PRIO = {1: "🔴 Urgente", 2: "🟡 Normal", 3: "🟢 Baja"}
        self.tree_ord.delete(*self.tree_ord.get_children())
        for p in ordenados:
            self.tree_ord.insert("", tk.END, values=(
                p.id, p.cliente, p.sector, PRIO[p.prioridad], p.peso, f"{p.valor:.2f}"
            ))
        self.lbl_busq.config(
            text=f"QuickSort por «{self.var_criterio.get()}» "
                 f"| {len(ordenados)} pedidos | Tiempo: {elapsed:.3f} ms",
            fg=self.app.COLORES["success"]
        )
        self.app.actualizar_mapa(pedidos_resaltados=ordenados[:5])

    def _buscar_id(self):
        ob = OrdenacionBusqueda()
        ordenados = sorted(self.app.pedidos, key=lambda p: p.id)
        target = self.var_busq_id.get()
        t0 = time.perf_counter()
        resultado = ob.busqueda_binaria_por_id(ordenados, target)
        elapsed = (time.perf_counter() - t0) * 1000
        if resultado:
            self.lbl_busq.config(
                text=f"✔ Encontrado: #{resultado.id} – {resultado.cliente} "
                     f"| {resultado.sector} | {elapsed:.4f} ms",
                fg=self.app.COLORES["success"]
            )
            self.app.actualizar_mapa(pedidos_resaltados=[resultado])
        else:
            self.lbl_busq.config(
                text=f"✘ ID #{target} no encontrado",
                fg=self.app.COLORES["accent"]
            )

    def _buscar_sector(self):
        ob = OrdenacionBusqueda()
        sector = self.var_busq_sec.get()
        resultados = ob.busqueda_por_sector(self.app.pedidos, sector)
        self.lbl_busq.config(
            text=f"Sector «{sector}»: {len(resultados)} pedido(s) encontrado(s) "
                 f"| IDs: {[p.id for p in resultados]}",
            fg=self.app.COLORES["info"]
        )
        self.app.actualizar_mapa(pedidos_resaltados=resultados)

    # Métodos auxiliares (botón, tabla, sección) igual que en datos_tab
    def _boton(self, parent, texto, comando):
        c = self.app.COLORES
        return tk.Button(parent, text=texto, command=comando,
                         bg=c["accent"], fg="white",
                         font=("Courier New", 9, "bold"),
                         relief=tk.FLAT, padx=12, pady=4,
                         activebackground=c["card"],
                         activeforeground=c["accent"],
                         cursor="hand2")

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

    def _seccion(self, parent, titulo):
        c = self.app.COLORES
        f = tk.Frame(parent, bg=c["card"], height=26)
        f.pack(fill=tk.X, padx=6, pady=(8, 2))
        f.pack_propagate(False)
        tk.Label(f, text=titulo, bg=c["card"], fg=c["accent2"],
                 font=("Courier New", 9, "bold")).pack(side=tk.LEFT, padx=8)