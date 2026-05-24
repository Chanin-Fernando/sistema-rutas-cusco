import tkinter as tk
from tkinter import ttk
import time
from ...data import construir_grafo, NODOS
from ...algorithms import Backtracking

class BacktrackingTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = tk.Frame(notebook, bg=app.COLORES["bg"])
        notebook.add(self.tab, text="🔙 BACKTRACKING")
        self._crear_widgets()

    def _crear_widgets(self):
        self._seccion(self.tab, "Rutas con restricciones – Todas las rutas posibles  |  O(V!)")
        ctrl = tk.Frame(self.tab, bg=self.app.COLORES["bg"])
        ctrl.pack(fill=tk.X, pady=4)
        nodos_lista = list(NODOS.keys())
        tk.Label(ctrl, text="Origen:", bg=self.app.COLORES["bg"],
                 fg=self.app.COLORES["text2"], font=("Courier New",9)).pack(side=tk.LEFT)
        self.var_origen = tk.StringVar(value="San Blas")
        cb1 = ttk.Combobox(ctrl, textvariable=self.var_origen, values=nodos_lista, width=16,
                           state="readonly", font=("Courier New",9))
        cb1.pack(side=tk.LEFT, padx=4)
        tk.Label(ctrl, text="Destino:", bg=self.app.COLORES["bg"],
                 fg=self.app.COLORES["text2"], font=("Courier New",9)).pack(side=tk.LEFT, padx=(8,0))
        self.var_destino = tk.StringVar(value="Wanchaq")
        cb2 = ttk.Combobox(ctrl, textvariable=self.var_destino, values=nodos_lista, width=16,
                           state="readonly", font=("Courier New",9))
        cb2.pack(side=tk.LEFT, padx=4)
        ctrl2 = tk.Frame(self.tab, bg=self.app.COLORES["bg"])
        ctrl2.pack(fill=tk.X, pady=4)
        tk.Label(ctrl2, text="Calles bloqueadas (ej: San Blas-San Cristóbal):",
                 bg=self.app.COLORES["bg"], fg=self.app.COLORES["text2"], font=("Courier New",9)).pack(side=tk.LEFT)
        self.var_bloqueadas = tk.StringVar(value="")
        tk.Entry(ctrl2, textvariable=self.var_bloqueadas, width=40,
                 bg=self.app.COLORES["card"], fg=self.app.COLORES["text"],
                 font=("Courier New",9)).pack(side=tk.LEFT, padx=6)
        self._boton(self.tab, "▶ Buscar rutas (Backtracking)", self._ejecutar_backtracking).pack(pady=6, anchor=tk.W, padx=8)
        self.txt_bt = self._text_area(self.tab)

    def _ejecutar_backtracking(self):
        origen = self.var_origen.get()
        destino = self.var_destino.get()
        bloq_raw = self.var_bloqueadas.get()
        bloqueadas = [b.strip() for b in bloq_raw.split(",") if b.strip()]
        grafo = construir_grafo(bloqueadas)
        bt = Backtracking(grafo)
        t0 = time.perf_counter()
        mejor_ruta, costo = bt.encontrar_rutas(origen, destino)
        elapsed = (time.perf_counter()-t0)*1000
        lines = [f"── Backtracking: Búsqueda Exhaustiva ──",
                 f"Origen: {origen}  →  Destino: {destino}",
                 f"Calles bloqueadas: {bloqueadas or 'ninguna'}",
                 f"Tiempo de ejecución: {elapsed:.3f} ms", ""]
        lines.extend(bt.log_pasos)
        self._actualizar_text(self.txt_bt, lines)
        if mejor_ruta:
            self.app.actualizar_mapa(ruta_resaltada=mejor_ruta, pedidos_resaltados=self.app.pedidos[:3])
            self.app.set_info_mapa(f"Backtracking: mejor ruta en rojo ({costo} min)")

    def _seccion(self, parent, titulo):
        c = self.app.COLORES
        f = tk.Frame(parent, bg=c["card"], height=26)
        f.pack(fill=tk.X, padx=6, pady=(8,2))
        f.pack_propagate(False)
        tk.Label(f, text=titulo, bg=c["card"], fg=c["accent2"], font=("Courier New",9,"bold")).pack(side=tk.LEFT, padx=8)

    def _boton(self, parent, texto, comando):
        c = self.app.COLORES
        return tk.Button(parent, text=texto, command=comando,
                         bg=c["accent"], fg="white", font=("Courier New",9,"bold"),
                         relief=tk.FLAT, padx=12, pady=4,
                         activebackground=c["card"], activeforeground=c["accent"], cursor="hand2")

    def _text_area(self, parent):
        c = self.app.COLORES
        frame = tk.Frame(parent, bg=c["bg"])
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        sb = ttk.Scrollbar(frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt = tk.Text(frame, bg=c["panel"], fg=c["text"], font=("Courier New",9),
                      relief=tk.FLAT, padx=10, pady=8, yscrollcommand=sb.set,
                      insertbackground=c["accent"], selectbackground=c["card"])
        txt.pack(fill=tk.BOTH, expand=True)
        sb.config(command=txt.yview)
        txt.tag_config("titulo", foreground=c["accent"], font=("Courier New",10,"bold"))
        txt.tag_config("ok", foreground=c["success"])
        txt.tag_config("warn", foreground=c["warning"])
        txt.tag_config("info", foreground=c["info"])
        return txt

    def _actualizar_text(self, txt, lines):
        txt.config(state=tk.NORMAL)
        txt.delete("1.0", tk.END)
        for ln in lines:
            if ln.startswith("──") or ln.startswith("🏆") or ln.startswith("Total"):
                txt.insert(tk.END, ln+"\n", "titulo")
            elif ln.startswith("✓") or ln.startswith("✔"):
                txt.insert(tk.END, ln+"\n", "ok")
            elif ln.startswith("✗") or ln.startswith("✘") or ln.startswith("⚠") or ln.startswith("❌"):
                txt.insert(tk.END, ln+"\n", "warn")
            else:
                txt.insert(tk.END, ln+"\n")
        txt.config(state=tk.DISABLED)
        txt.see(tk.END)