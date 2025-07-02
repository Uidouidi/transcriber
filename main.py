#!/usr/bin/env python3
"""
Punto de entrada de la aplicación de grabación y transcripción v2.0
"""
import sys
import os
from pathlib import Path

# Asegurar que el directorio de grabaciones existe
Path("./grabaciones").mkdir(exist_ok=True)

# Importar el controlador principal
from controlador import ControladorPrincipal

def main():
    """Función principal de la aplicación"""
    print("🎙️ Iniciando aplicación de grabación y transcripción v2.0")
    
    try:
        controlador = ControladorPrincipal()
        controlador.iniciar()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupción detectada")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()