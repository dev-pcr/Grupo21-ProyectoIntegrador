#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificador del analizador sintáctico REAL (ply.yacc) — Pablo, Grupo 21.

A diferencia de verificar_sintactico.py (que valida la especificación leyendo
tokens.txt y gramatica.txt), este script ejecuta sintactico.analizar() de PLY
contra los casos ok-*.txt y sin-*.txt de pruebas-grupo/ y compara con
pruebas-grupo/esperado.csv:
  - ok-*  : debe ser sintácticamente correcto y sin errores léxicos.
  - sin-* : debe fallar y la línea informada debe coincidir con el CSV.
Además audita parser.out (0 conflictos shift/reduce y reduce/reduce).

Uso (desde la raíz del proyecto):
    py herramientas/verificar_sintactico_ply.py
"""

import csv
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import lexico        # noqa: E402
import sintactico    # noqa: E402

CARPETA = os.path.join(RAIZ, 'pruebas-grupo')


def leer_fuente(ruta):
    # newline='' conserva \r y \r\n tal cual (ok-13, ok-40, lex-26...).
    with open(ruta, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def main():
    with open(os.path.join(CARPETA, 'esperado.csv'), encoding='utf-8', newline='') as f:
        filas = list(csv.DictReader(f))

    total = fallos = 0
    for fila in filas:
        nombre = fila['archivo']
        if not (nombre.startswith('ok-') or nombre.startswith('sin-')):
            continue  # los lex-* corresponden al analizador léxico (Emiliano)
        total += 1

        exito, error = sintactico.analizar(leer_fuente(os.path.join(CARPETA, nombre)))
        hubo_lex = bool(lexico.errores_lexicos)

        if fila['esperado'] == 'OK':
            correcto = exito and not hubo_lex
            detalle = f"obtenido={'OK' if exito else 'SINTACTICO linea ' + str(error['linea'])}"
        else:
            correcto = (not exito) and str(error['linea']) == fila['linea'] and not hubo_lex
            detalle = (f"esperado=SINTACTICO linea {fila['linea']} | obtenido="
                       + ('OK' if exito else f"SINTACTICO linea {error['linea']} ({error['mensaje']})"))
            if hubo_lex:
                detalle += f" | errores lexicos inesperados: {lexico.errores_lexicos}"

        if not correcto:
            fallos += 1
            print(f"[FALLA] {nombre}: {detalle}")

    print(f"\nCasos ejecutados: {total} | Aprobados: {total - fallos} | Fallos: {fallos}")

    conflictos = sintactico.auditar_conflictos()
    print(f"Conflictos shift/reduce: {conflictos['shift_reduce']} | "
          f"reduce/reduce: {conflictos['reduce_reduce']}")
    for adv in conflictos['advertencias']:
        print(f"  advertencia PLY: {adv}")

    ok = fallos == 0 and conflictos['shift_reduce'] == 0 and conflictos['reduce_reduce'] == 0
    print("RESULTADO:", "TODO CORRECTO" if ok else "HAY PROBLEMAS")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
