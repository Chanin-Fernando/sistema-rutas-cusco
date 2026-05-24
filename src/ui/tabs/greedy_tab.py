import tkinter as tk
from tkinter import ttk
import time
from ...algorithms import AlgoritmoGreedy

class GreedyTab:
    def __init__(self, notebook, app):
        self.app = app
        self.tab = tk.Frame(notebook, bg=app.COLORES["bg"])
        notebook.add(self.tab, text="⚡ GREEDY")
        self._crear_widgets()

    def _crear_widgets(self):
        self._seccion(self.tab, "Asignación al repartidor más cercano  |  O(n × m)")
        self._boton(self.tab, "▶ Ejecutar asignación Greedy",
                    self._ejecutar_greedy).pack(pady=6, anchor=tk.W, padx=8)
        self.txt_greedy = self._text_area(self.tab)

    def _ejecutar_greedy(self):
        g = AlgoritmoGreedy(self.app.repartidores)
        t0 = time.perf_counter()
        asignaciones, rutas = g.asignar_pedidos(self.app.pedidos)
        elapsed = (time.perf_counter() - t0) * 1000
        lines = [
            f"── Greedy: Asignación de Pedidos ──",
            f"Tiempo de ejecución: {elapsed:.3f} ms",
            f"",
        ]
        lines.extend(g.log_pasos)
        lines.append("\n── Rutas Greedy (Vecino más cercano) ──")
        todos_pedidos_ruta = []
        for rep in self.app.repartidores:
            ruta = rutas[rep.id]
            lines.append(f"\n{rep.nombre}:")
            if not ruta:
                lines.append("  (sin pedidos asignados)")
                continue
            orden = " → ".join(f"#{p.id}" for p in ruta)
            lines.append(f"  Orden de visita: {orden}")
            dist_total = 0.0
            cx, cy = rep.pos_x, rep.pos_y
            for p in ruta:
                d = p.distancia_a(cx, cy)
                dist_total += d
                cx, cy = p.coord_x, p.coord_y
            lines.append(f"  Distancia total recorrida: {dist_total:.1f} u")
            todos_pedidos_ruta.extend(ruta)
        self._actualizar_text(self.txt_greedy, lines)
        primer_rep = self.app.repartidores[0]
        self.app.actualizar_mapa(pedidos_resaltados=rutas.get(primer_rep.id, []))
        self.app.set_info_mapa(f"Greedy: se muestra la ruta de {primer_rep.nombre}")

    def _seccion(self, parent, titulo):
        c = self.app.COLORES
        f = tk.Frame(parent, bg=c["card"], height=26)
        f.pack(fill=tk.X, padx=6, pady=(8, 2))
        f.pack_propagate(False)
        tk.Label(f, text=titulo, bg=c["card"], fg=c["accent2"],
                 font=("Courier New", 9, "bold")).pack(side=tk.LEFT, padx=8)

    def _boton(self, parent, texto, comando):
        c = self.app.COLORES
        return tk.Button(parent, text=texto, command=comando,
                         bg=c["accent"], fg="white",
                         font=("Courier New", 9, "bold"),
                         relief=tk.FLAT, padx=12, pady=4,
                         activebackground=c["card"],
                         activeforeground=c["accent"],
                         cursor="hand2")

    def _text_area(self, parent):
        c = self.app.COLORES
        frame = tk.Frame(parent, bg=c["bg"])
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        sb = ttk.Scrollbar(frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt = tk.Text(frame, bg=c["panel"], fg=c["text"],
                      font=("Courier New", 9),
                      relief=tk.FLAT, padx=10, pady=8,
                      yscrollcommand=sb.set,
                      insertbackground=c["accent"],
                      selectbackground=c["card"])
        txt.pack(fill=tk.BOTH, expand=True)
        sb.config(command=txt.yview)
        txt.tag_config("titulo", foreground=c["accent"], font=("Courier New", 10, "bold"))
        txt.tag_config("ok",    foreground=c["success"])
        txt.tag_config("warn",  foreground=c["warning"])
        txt.tag_config("info",  foreground=c["info"])
        return txt

    def _actualizar_text(self, txt, lines):
        txt.config(state=tk.NORMAL)
        txt.delete("1.0", tk.END)
        for ln in lines:
            if ln.startswith("──") or ln.startswith("🏆") or ln.startswith("Total"):
                txt.insert(tk.END, ln + "\n", "titulo")
            elif ln.startswith("✓") or ln.startswith("✔"):
                txt.insert(tk.END, ln + "\n", "ok")
            elif ln.startswith("✗") or ln.startswith("✘") or ln.startswith("⚠") or ln.startswith("❌"):
                txt.insert(tk.END, ln + "\n", "warn")
            else:
                txt.insert(tk.END, ln + "\n")
        txt.config(state=tk.DISABLED)
        txt.see(tk.END)