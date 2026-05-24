#!/usr/bin/env python3
"""
Sistema de Gestión de Rutas Óptimas en Cusco
Punto de entrada principal.
"""
from src.ui.app import AppCusco

if __name__ == "__main__":
    app = AppCusco()
    app.mainloop()