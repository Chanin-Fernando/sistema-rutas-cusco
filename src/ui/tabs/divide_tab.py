import tkinter as tk
from tkinter import ttk
import time
from ...algorithms import DivideYVenceras

class DivideTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = tk.Frame(notebook, bg=app.COLORES["bg"])
        notebook.add(self.tab, text="🗺 DIVIDE Y VENCERÁS")
        self._crear_widgets()

    def _crear_widgets(self):
        self._seccion(self.tab, "Segmentación por cuadrantes  |  O(n log n)")
        ctrl = tk.Frame(self.tab, bg=self.app.COLORES["bg"])
        ctrl.pack(fill=tk.X, pady=4)
        tk.Label(ctrl, text="Profundidad máx:", bg=self.app.COLORES["bg"],
                 fg=self.app.COLORES["text2"], font=("Courier New",9)).pack(side=tk.LEFT)
        self.var_prof = tk.IntVar(value=2)
        tk.Spinbox(ctrl, from_=1, to=3, textvariable=self.var_prof, width=3,
                   bg=self.app.COLORES["card"], fg=self.app.COLORES["text"],
                   font=("Courier New",9), buttonbackground=self.app.COLORES["card"]).pack(side=tk.LEFT, padx=6)
        self._boton(ctrl, "▶ Segmentar mapa", self._ejecutar_divide).pack(side=tk.LEFT)
        self.txt_divide = self._text_area(self.tab)

    def _ejecutar_divide(self):
        dv = DivideYVenceras()
        t0 = time.perf_counter()
        cuadrantes = dv.segmentar(self.app.pedidos, max_prof=self.var_prof.get())
        elapsed = (time.perf_counter()-t0)*1000
        asignacion = dv.asignar_repartidores(cuadrantes, self.app.repartidores)
        lines = [f"── Divide y Vencerás: Segmentación ──",
                 f"Profundidad máxima: {self.var_prof.get()}",
                 f"Tiempo de ejecución: {elapsed:.3f} ms", "",
                 "── Árbol de Recursión ──"]
        lines.extend(dv.log_pasos)
        lines.append("\n── Asignación de repartidores ──")
        for k, v in asignacion.items():
            bnd = v["cuadrante"]["bounds"]
            rep = v["repartidor"]
            npeds = len(v["cuadrante"]["pedidos"])
            lines.append(f"  Cuadrante ({bnd[0]:.0f},{bnd[2]:.0f})→({bnd[1]:.0f},{bnd[3]:.0f}) | {npeds} pedido(s) → {rep.nombre}")
        self._actualizar_text(self.txt_divide, lines)
        self.app.actualizar_mapa(pedidos_resaltados=self.app.pedidos, cuadrantes=cuadrantes)
        self.app.set_info_mapa(f"Divide y Vencerás: {len(cuadrantes)} cuadrantes generados")

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