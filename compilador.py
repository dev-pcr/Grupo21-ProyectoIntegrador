#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Compilador para el Subconjunto de Arduino (C++ para microcontrolador)
Facultad de Ingeniería — UCASAL — Compiladores 2026
Grupo N.º 21
Integrantes:
- Emiliano (Persona 1)
- Pablo (Persona 2)
================================================================================
Punto de entrada principal para el análisis léxico y sintáctico.
Ejecución:
    python3 compilador.py programa.txt

Formato estricto de la primera línea de salida:
    OK
    ERROR LEXICO linea N: descripcion
    ERROR SINTACTICO linea N: descripcion

Regla de oro:
    Ante la presencia de errores múltiples, se reporta siempre el primer error
    en el orden de lectura del archivo fuente.
================================================================================
"""

import sys
import os

# Importación de los módulos del analizador
# (Se completarán e integrarán en lexico.py y sintactico.py)
try:
    import lexico
    import sintactico
except ImportError:
    pass


def compilar(ruta_archivo):
    """
    Lee y analiza el archivo fuente indicado.
    Determina si el programa es correcto (OK) o emite el primer error léxico o
    sintáctico encontrado en orden de lectura.
    """
    if not os.path.exists(ruta_archivo):
        print(f"ERROR: No se encontró el archivo '{ruta_archivo}'")
        return

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        print(f"ERROR: No se pudo leer el archivo: {e}")
        return

    # TODO [Emiliano y Pablo]: Integración de análisis léxico y sintáctico.
    # 1. Ejecutar escaneo / captura de errores léxicos con lexico.py.
    # 2. Ejecutar análisis sintáctico con sintactico.py.
    # 3. Aplicar regla de orden: comparar línea de primer error léxico vs sintáctico.
    # 4. Imprimir en stdout: OK / ERROR LEXICO / ERROR SINTACTICO.

    # Esqueleto inicial:
    # print("OK")


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 compilador.py <archivo_fuente.txt>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]
    compilar(ruta_archivo)


if __name__ == '__main__':
    main()
