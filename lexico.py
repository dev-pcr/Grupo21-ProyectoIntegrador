#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Analizador Léxico (ply.lex) — Subconjunto de Arduino (C++ microcontrolador)
Facultad de Ingeniería — UCASAL — Compiladores 2026
Grupo N.º 21
Responsable: Emiliano (Persona 1)
================================================================================
Define los tokens, palabras reservadas, expresiones regulares y control de
líneas de acuerdo con la especificación aprobada en tokens.txt.
================================================================================
"""

import ply.lex as lex

# -----------------------------------------------------------------------------
# 1. PALABRAS RESERVADAS Y CONSTANTES
# -----------------------------------------------------------------------------
# Se mapean en un diccionario para asignarlas en la regla de IDENTIFICADOR,
# garantizando que tengan prioridad sobre los identificadores comunes.
reserved = {
    # Palabras clave y definiciones
    'setup': 'SETUP',
    'loop': 'LOOP',
    'void': 'VOID',
    # Tipos
    'boolean': 'BOOLEAN',
    'char': 'CHAR',
    'float': 'FLOAT',
    # Booleanos
    'false': 'FALSE',
    'true': 'TRUE',
    # Constantes Arduino
    'HIGH': 'HIGH',
    'INPUT': 'INPUT',
    'INPUT_PULLUP': 'INPUT_PULLUP',
    'LED_BUILTIN': 'LED_BUILTIN',
    'LOW': 'LOW',
    'OUTPUT': 'OUTPUT',
    # Funciones
    'map': 'MAP',
    'delay': 'DELAY',
}

# -----------------------------------------------------------------------------
# 2. LISTA DE TOKENS
# -----------------------------------------------------------------------------
tokens = [
    # Signos y delimitadores
    'PARENTESIS_IZQ',
    'PARENTESIS_DER',
    'LLAVE_IZQ',
    'LLAVE_DER',
    'COMA',
    'PUNTO_Y_COMA',
    # Operadores de asignación
    'IGUAL',
    'SUMA_IGUAL',
    'RESTA_IGUAL',
    # Operadores aritméticos
    'SUMA',
    'RESTA',
    'MULTIPLICACION',
    'DIVISION',
    # Función compuesta con punto
    'SERIAL_PRINTLN',
    # Literales e identificadores
    'CADENA',
    'DECIMAL',
    'ENTERO',
    'IDENTIFICADOR',
] + list(set(reserved.values()))

# -----------------------------------------------------------------------------
# 3. REGLAS DE TOKENS SIMPLES (EXPRESIONES REGULARES)
# -----------------------------------------------------------------------------
# TODO [Emiliano]: Completar las expresiones regulares según tokens.txt.
# Cuidado con el orden de precedencia de PLY (patrones más largos primero).

t_SUMA_IGUAL        = r'\+='
t_RESTA_IGUAL       = r'-='
t_IGUAL             = r'='
t_SUMA              = r'\+'
t_RESTA             = r'-'
t_MULTIPLICACION    = r'\*'
t_DIVISION          = r'/'
t_PARENTESIS_IZQ    = r'\('
t_PARENTESIS_DER    = r'\)'
t_LLAVE_IZQ         = r'\{'
t_LLAVE_DER         = r'\}'
t_COMA              = r','
t_PUNTO_Y_COMA      = r';'

# -----------------------------------------------------------------------------
# 4. REGLAS DE TOKENS CON FUNCIONES (LITERALES Y ACCIONES)
# -----------------------------------------------------------------------------
# NOTA DE PRECEDENCIA EN PLY:
# PLY evalúa primero las reglas definidas como funciones (def t_*) en el orden
# exacto en que aparecen en el archivo, antes que las reglas definidas con
# strings (t_* = '...'). Por eso, t_SERIAL_PRINTLN DEBE ser una función y estar
# ubicada ANTES de t_IDENTIFICADOR; de lo contrario, el prefijo 'Serial' sería
# capturado como IDENTIFICADOR y el '.' como un error léxico.

def t_SERIAL_PRINTLN(t):
    r'Serial\.println'
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFICADOR')
    return t

def t_DECIMAL(t):
    r'[0-9]+\.[0-9]+'
    return t

def t_ENTERO(t):
    r'[0-9]+'
    return t

def t_CADENA(t):
    r'"[^"\n]*"|\'[^\'\n]*\''
    return t

# -----------------------------------------------------------------------------
# 5. CARACTERES IGNORADOS Y CONTROL DE LÍNEAS
# -----------------------------------------------------------------------------
# Espacios, tabulaciones y retornos de carro
t_ignore = ' \t\r'

# Comentarios multilínea /* ... */
def t_COMMENT_BLOCK(t):
    r'/\*[\s\S]*?\*/'
    # Sumar los saltos de línea contenidos en el comentario
    t.lexer.lineno += t.value.count('\n')

# Control de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# -----------------------------------------------------------------------------
# 6. MANEJO DE ERRORES LÉXICOS
# -----------------------------------------------------------------------------
# Lista para registrar errores léxicos detectados durante el escaneo
errores_lexicos = []

def t_error(t):
    """
    Registra el carácter no reconocido junto con su número de línea.
    No descarta con print directo para no romper la regla de oro de la salida.
    """
    errores_lexicos.append({
        'linea': t.lexer.lineno,
        'caracter': t.value[0],
        'posicion': t.lexpos
    })
    # TODO [Emiliano]: Definir si se hace skip o si se corta el escaneo
    t.lexer.skip(1)

# -----------------------------------------------------------------------------
# 7. CONSTRUCTOR DEL ANALIZADOR LÉXICO
# -----------------------------------------------------------------------------
def crear_lexer():
    """Inicializa y retorna una nueva instancia del lexer de PLY."""
    global errores_lexicos
    errores_lexicos = []
    return lex.lex()
