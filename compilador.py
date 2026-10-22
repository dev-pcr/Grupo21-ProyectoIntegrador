#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Compilador para el Subconjunto de Arduino (C++ para microcontrolador)
Facultad de Ingeniería — UCASAL — Compiladores 2026
Grupo N.º 21
Integrantes:
- Emiliano (Persona 1) — Analizador Léxico (lexico.py)
- Pablo (Persona 2) — Analizador Sintáctico (sintactico.py)
================================================================================
Punto de entrada principal para el análisis léxico y sintáctico.

Ejecución desde la raíz del proyecto:
    python3 compilador.py <archivo_fuente.txt>

Formato estricto de la primera línea escrita en stdout:
    OK
    ERROR LEXICO linea N: descripcion
    ERROR SINTACTICO linea N: descripcion

Regla de oro:
    Ante la presencia de errores múltiples, se reporta siempre el primer error
    en el orden de lectura del archivo fuente.
    Si L_lex <= L_sint -> se reporta ERROR LEXICO.
    Si L_sint < L_lex  -> se reporta ERROR SINTACTICO.
================================================================================
"""

import os
import sys

import lexico
import sintactico


def compilar_codigo(contenido):
    """
    Analiza una cadena de código fuente en memoria y determina el resultado.
    Retorna la cadena exacta que debe imprimirse en la primera línea de stdout:
      - 'OK'
      - 'ERROR LEXICO linea N: descripcion'
      - 'ERROR SINTACTICO linea N: descripcion'
    """
    # 1. Escaneo léxico completo del archivo
    # Permite capturar todos los errores léxicos presentes, incluso si ocurren en
    # la misma línea o antes de un corte sintáctico.
    lexer_scan = lexico.crear_lexer()
    lexer_scan.input(contenido)
    while True:
        tok = lexer_scan.token()
        if not tok:
            break

    todos_errores_lexicos = list(lexico.errores_lexicos)
    primer_lex = todos_errores_lexicos[0] if todos_errores_lexicos else None

    # 2. Análisis sintáctico mediante PLY (sintactico.py)
    exito, error_sint = sintactico.analizar(contenido)

    # 3. Aplicación estricta de la Regla de Oro (orden de lectura en el archivo)
    if primer_lex and error_sint:
        # Si ambos componentes detectan errores, gana el que aparece en la línea menor.
        # Si ocurren en la misma línea (L_lex == L_sint), prevalece el error léxico.
        if primer_lex['linea'] <= error_sint['linea']:
            return f"ERROR LEXICO linea {primer_lex['linea']}: {primer_lex['mensaje']}"
        else:
            return f"ERROR SINTACTICO linea {error_sint['linea']}: {error_sint['mensaje']}"

    elif primer_lex:
        # Solo se detectaron errores léxicos
        return f"ERROR LEXICO linea {primer_lex['linea']}: {primer_lex['mensaje']}"

    elif error_sint:
        # Solo se detectó error sintáctico
        return f"ERROR SINTACTICO linea {error_sint['linea']}: {error_sint['mensaje']}"

    else:
        # Programa léxica y sintácticamente válido
        return "OK"


def compilar(ruta_archivo):
    """
    Lee el archivo fuente indicado en UTF-8 y emite el resultado del análisis
    por la salida estándar (stdout).
    """
    if not os.path.exists(ruta_archivo):
        print(f"ERROR: No se encontró el archivo '{ruta_archivo}'")
        return

    try:
        # newline='' para preservar saltos de línea originales (CR, LF, CRLF)
        with open(ruta_archivo, 'r', encoding='utf-8', newline='') as f:
            contenido = f.read()
    except Exception as e:
        print(f"ERROR: No se pudo leer el archivo '{ruta_archivo}': {e}")
        return

    resultado = compilar_codigo(contenido)
    print(resultado)


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 compilador.py <archivo_fuente.txt>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]
    compilar(ruta_archivo)


if __name__ == '__main__':
    main()
