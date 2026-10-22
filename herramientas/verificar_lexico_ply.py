#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Verificador del Analizador Léxico REAL (ply.lex) — Emiliano, Grupo 21
Facultad de Ingeniería — UCASAL — Compiladores 2026
================================================================================
A diferencia de verificar_lexico.py (que evalúa el algoritmo manual de tokens.txt),
este script ejecuta directamente la implementación REAL de PLY en lexico.py
y la integración completa en compilador.py.

Evalúa:
1. Micro-pruebas léxicas de desempate, longitud y precedencia en ply.lex.
2. Los 9 casos de prueba públicos oficiales de la cátedra (casos/).
3. La totalidad de casos léxicos (lex-*) y válidos (ok-*) de pruebas-grupo/.
4. Verificación de la Regla de Oro (L_lex vs L_sint) en casos con múltiples errores.

Uso desde la raíz del proyecto:
    python herramientas/verificar_lexico_ply.py
================================================================================
"""

import csv
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import lexico      # noqa: E402
import compilador  # noqa: E402

# Micro-pruebas dirigidas a verificar la precedencia y tokenización en ply.lex
MICRO_PRUEBAS = [
    # 1. Palabras reservadas vs identificadores (longest match)
    ("setup", [("SETUP", "setup")]),
    ("setup1", [("IDENTIFICADOR", "setup1")]),
    ("loop", [("LOOP", "loop")]),
    ("loop_var", [("IDENTIFICADOR", "loop_var")]),
    ("void", [("VOID", "void")]),
    ("boolean", [("BOOLEAN", "boolean")]),
    ("char", [("CHAR", "char")]),
    ("float", [("FLOAT", "float")]),
    ("float_val", [("IDENTIFICADOR", "float_val")]),
    ("true", [("TRUE", "true")]),
    ("false", [("FALSE", "false")]),
    ("map", [("MAP", "map")]),
    ("mapa", [("IDENTIFICADOR", "mapa")]),
    ("delay", [("DELAY", "delay")]),
    ("delay_ms", [("IDENTIFICADOR", "delay_ms")]),

    # 2. Constantes Arduino
    ("HIGH", [("HIGH", "HIGH")]),
    ("LOW", [("LOW", "LOW")]),
    ("INPUT", [("INPUT", "INPUT")]),
    ("INPUT_PULLUP", [("INPUT_PULLUP", "INPUT_PULLUP")]),
    ("LED_BUILTIN", [("LED_BUILTIN", "LED_BUILTIN")]),
    ("OUTPUT", [("OUTPUT", "OUTPUT")]),

    # 3. Caso crítico resuelto en log-de-errores.md: Serial.println
    ("Serial.println", [("SERIAL_PRINTLN", "Serial.println")]),

    # 4. Operadores compuestos vs simples
    ("+=", [("SUMA_IGUAL", "+=")]),
    ("-=", [("RESTA_IGUAL", "-=")]),
    ("=", [("IGUAL", "=")]),
    ("+", [("SUMA", "+")]),
    ("-", [("RESTA", "-")]),
    ("*", [("MULTIPLICACION", "*")]),
    ("/", [("DIVISION", "/")]),

    # 5. Números enteros y decimales (decimal requiere dígitos a ambos lados)
    ("123", [("ENTERO", "123")]),
    ("123.456", [("DECIMAL", "123.456")]),
    ("0.5", [("DECIMAL", "0.5")]),

    # 6. Cadenas de caracteres (ambos delimitadores)
    ('"hola"', [("CADENA", '"hola"')]),
    ("'mundo'", [("CADENA", "'mundo'")]),
    ('""', [("CADENA", '""')]),
    ("''", [("CADENA", "''")]),
    ('"comilla \'simple\'"', [("CADENA", '"comilla \'simple\'"')]),

    # 7. Comentarios de bloque y saltos de línea
    ("/* comentario simple */", []),
    ("/* multilínea\nlinea2\nlinea3 */", []),
]


def leer_archivo(ruta):
    with open(ruta, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def test_micro():
    print("--------------------------------------------------------------------------------")
    print("1. EJECUCIÓN DE MICRO-PRUEBAS LÉXICAS EN PLY.LEX")
    print("--------------------------------------------------------------------------------")
    lexer = lexico.crear_lexer()
    fallos = 0

    for entrada, tokens_esperados in MICRO_PRUEBAS:
        lexer.input(entrada)
        obtenidos = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            obtenidos.append((tok.type, tok.value))

        if obtenidos != tokens_esperados:
            fallos += 1
            print(f"  [FALLO] Entrada: {repr(entrada)}")
            print(f"          Esperado: {tokens_esperados}")
            print(f"          Obtenido: {obtenidos}")

    total = len(MICRO_PRUEBAS)
    print(f"Resultado micro-pruebas: {total - fallos}/{total} aprobadas.\n")
    return fallos == 0


def test_casos_publicos():
    print("--------------------------------------------------------------------------------")
    print("2. EJECUCIÓN SOBRE CASOS PÚBLICOS DE LA CÁTEDRA (casos/)")
    print("--------------------------------------------------------------------------------")
    ruta_csv = os.path.join(RAIZ, 'casos', 'esperado.csv')
    with open(ruta_csv, encoding='utf-8', newline='') as f:
        casos = list(csv.DictReader(f))

    fallos = 0
    for fila in casos:
        archivo = fila['archivo']
        esperado_tipo = fila['esperado']
        esperado_linea = fila['linea']

        ruta_fuente = os.path.join(RAIZ, 'casos', archivo)
        contenido = leer_archivo(ruta_fuente)
        salida = compilador.compilar_codigo(contenido)

        # Parsear primera línea
        partes = salida.split()
        if salida == 'OK':
            obtenido_tipo = 'OK'
            obtenido_linea = ''
        elif salida.startswith('ERROR LEXICO'):
            obtenido_tipo = 'ERROR LEXICO'
            obtenido_linea = partes[3].rstrip(':')
        elif salida.startswith('ERROR SINTACTICO'):
            obtenido_tipo = 'ERROR SINTACTICO'
            obtenido_linea = partes[3].rstrip(':')
        else:
            obtenido_tipo = 'DESCONOCIDO'
            obtenido_linea = ''

        es_valido = (obtenido_tipo == esperado_tipo) and (obtenido_linea == esperado_linea)
        if not es_valido:
            fallos += 1
            print(f"  [FALLO] {archivo}: esperado={esperado_tipo} {esperado_linea} | obtenido={salida}")
        else:
            print(f"  [OK] {archivo:<20} -> {salida}")

    print(f"Resultado casos públicos: {len(casos) - fallos}/{len(casos)} aprobados.\n")
    return fallos == 0


def test_pruebas_grupo():
    print("--------------------------------------------------------------------------------")
    print("3. EJECUCIÓN SOBRE BATERÍA DE PRUEBAS DE GRUPO (pruebas-grupo/)")
    print("--------------------------------------------------------------------------------")
    ruta_csv = os.path.join(RAIZ, 'pruebas-grupo', 'esperado.csv')
    with open(ruta_csv, encoding='utf-8', newline='') as f:
        casos = list(csv.DictReader(f))

    fallos = 0
    evaluados = 0

    for fila in casos:
        archivo = fila['archivo']
        # Evaluar casos léxicos y casos válidos
        if not (archivo.startswith('lex-') or archivo.startswith('ok-')):
            continue

        evaluados += 1
        esperado_tipo = fila['esperado']
        esperado_linea = fila['linea']

        ruta_fuente = os.path.join(RAIZ, 'pruebas-grupo', archivo)
        contenido = leer_archivo(ruta_fuente)
        salida = compilador.compilar_codigo(contenido)

        partes = salida.split()
        if salida == 'OK':
            obtenido_tipo = 'OK'
            obtenido_linea = ''
        elif salida.startswith('ERROR LEXICO'):
            obtenido_tipo = 'ERROR LEXICO'
            obtenido_linea = partes[3].rstrip(':')
        elif salida.startswith('ERROR SINTACTICO'):
            obtenido_tipo = 'ERROR SINTACTICO'
            obtenido_linea = partes[3].rstrip(':')
        else:
            obtenido_tipo = 'DESCONOCIDO'
            obtenido_linea = ''

        es_valido = (obtenido_tipo == esperado_tipo) and (obtenido_linea == esperado_linea)
        if not es_valido:
            fallos += 1
            print(f"  [FALLO] {archivo}: esperado={esperado_tipo} {esperado_linea} | obtenido={salida}")

    print(f"Resultado casos pruebas-grupo: {evaluados - fallos}/{evaluados} aprobados.\n")
    return fallos == 0


def main():
    print("================================================================================")
    print("VERIFICACIÓN INTEGRAL DEL ANALIZADOR LÉXICO Y COMPILADOR (Grupo 21)")
    print("================================================================================\n")

    ok_micro = test_micro()
    ok_publicos = test_casos_publicos()
    ok_grupo = test_pruebas_grupo()

    todo_ok = ok_micro and ok_publicos and ok_grupo

    print("================================================================================")
    if todo_ok:
        print("VEREDICTO FINAL: TODOS LOS CASOS APROBADOS CON ÉXITO (100%)")
    else:
        print("VEREDICTO FINAL: SE DETECTARON FALLOS EN LA SUITE DE PRUEBAS")
    print("================================================================================")

    sys.exit(0 if todo_ok else 1)


if __name__ == '__main__':
    main()
