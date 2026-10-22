#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Analizador Léxico (ply.lex) — Subconjunto de Arduino (C++ microcontrolador)
Facultad de Ingeniería — UCASAL — Compiladores 2026
Grupo N.º 21
Responsable: Emiliano (Persona 1)
================================================================================
Implementa la especificación formal aprobada en tokens.txt:
- 34 componentes léxicos (tokens).
- 2 directivas de descarte (@ignorar: espacios/tabs/CR y comentarios de bloque).
- Seguimiento riguroso de números de línea (lineno).
- Detección precisa de errores léxicos sin descarte ruidoso en stdout.

Resumen de decisiones de diseño (útil para la defensa oral):

1. PALABRAS RESERVADAS Y CONSTANTES MEDIANTE DICCIONARIO
   En lugar de definir una regla léxica independiente por cada palabra clave,
   se utiliza una única regla t_IDENTIFICADOR combinada con un diccionario
   `reserved`. Esto evita colisiones donde un identificador como 'mapa' o 'float1'
   pueda ser partido erróneamente en tokens separados, asegurando la regla del
   patrón más largo (longest match).

2. ORDEN DE EVALUACIÓN Y PRECEDENCIA EN PLY (CRÍTICO)
   En PLY (ply.lex), las reglas definidas como funciones (def t_*) se evalúan
   SIEMPRE antes que las reglas definidas con cadenas de expresiones regulares
   (t_* = r'...'), y en el orden exacto de aparición en el archivo.
   Por este motivo:
     - `t_SERIAL_PRINTLN` DEBE ser una función y estar ubicada estrictamente
       ANTES de `t_IDENTIFICADOR`; de lo contrario, el prefijo 'Serial' sería
       absorbido como un IDENTIFICADOR y el '.' como un carácter inválido.
     - `t_DECIMAL` se define antes de `t_ENTERO` para que un número como 3.25
       sea reconocido como DECIMAL y no como ENTERO (3) seguido de error (.).

3. GESTIÓN DE COMENTARIOS Y SALTOS DE LÍNEA
   - Los comentarios de bloque /* ... */ se descartan mediante la función
     `t_COMMENT_BLOCK`, la cual suma a `lexer.lineno` la cantidad de saltos de
     línea '\\n' contenidos dentro del bloque comentado.
   - Los saltos de línea se procesan con `t_newline` incrementando `lineno`.
   - Espacios, tabulaciones y retornos de carro ('\\r') se ignoran con t_ignore.

4. REGLA DE ORO Y AISLAMIENTO DE ERRORES LÉXICOS
   La función `t_error(t)` NO imprime directamente en stdout. En su lugar,
   almacena el carácter no válido y su número de línea en la lista
   `errores_lexicos` y ejecuta `t.lexer.skip(1)`. Esto permite que compilador.py
   coordine si el primer error del archivo fue léxico o sintáctico.
================================================================================
"""

import ply.lex as lex

# -----------------------------------------------------------------------------
# 1. DICCIONARIO DE PALABRAS RESERVADAS Y CONSTANTES
# -----------------------------------------------------------------------------
# Mapea el texto exacto (lexema) al nombre de su token terminal.
# Se evalúa dentro de t_IDENTIFICADOR para evitar colisiones y desempates.
reserved = {
    # Palabras reservadas estructurales (Apartado B del Anexo)
    'setup': 'SETUP',
    'loop': 'LOOP',
    'void': 'VOID',

    # Tipos de datos soportados
    'boolean': 'BOOLEAN',
    'char': 'CHAR',
    'float': 'FLOAT',

    # Literales booleanos
    'false': 'FALSE',
    'true': 'TRUE',

    # Constantes predefinidas de Arduino
    'HIGH': 'HIGH',
    'INPUT': 'INPUT',
    'INPUT_PULLUP': 'INPUT_PULLUP',
    'LED_BUILTIN': 'LED_BUILTIN',
    'LOW': 'LOW',
    'OUTPUT': 'OUTPUT',

    # Funciones del lenguaje
    'map': 'MAP',
    'delay': 'DELAY',
}

# -----------------------------------------------------------------------------
# 2. LISTA COMPLETA DE TOKENS (34 TERMINALES)
# -----------------------------------------------------------------------------
# Obligatorio para PLY. Debe contener todos los nombres de tokens terminales
# que utiliza el analizador sintáctico (sintactico.py).
tokens = [
    # Signos de puntuación y delimitadores
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

    # Operadores aritméticos binarios
    'SUMA',
    'RESTA',
    'MULTIPLICACION',
    'DIVISION',

    # Llamada a función con punto
    'SERIAL_PRINTLN',

    # Literales e identificadores
    'CADENA',
    'DECIMAL',
    'ENTERO',
    'IDENTIFICADOR',
] + sorted(list(set(reserved.values())))


# -----------------------------------------------------------------------------
# 3. REGLAS DE TOKENS SIMPLES (EXPRESIONES REGULARES DE CADENA)
# -----------------------------------------------------------------------------
# PLY ordena internamente las reglas definidas como strings por longitud
# decreciente de la expresión regular. Por ello, '+=' se evalúa antes que '+',
# y '-=' antes que '-'.

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
# 4. REGLAS DE TOKENS DEFINIDAS COMO FUNCIONES (ORDEN ESTRICTO EN PLY)
# -----------------------------------------------------------------------------
# En PLY, las funciones t_* tienen precedencia absoluta sobre las cadenas y
# se evalúan en el orden EXACTO en que aparecen en el código fuente.

def t_SERIAL_PRINTLN(t):
    r'Serial\.println'
    # Debe ser función y ubicarse antes de t_IDENTIFICADOR.
    # De lo contrario, 'Serial' coincidiría con t_IDENTIFICADOR y '.' fallaría.
    return t


def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Busca si el identificador coincide exactamente con una palabra reservada.
    # Si coincide, se le asigna su token específico; de lo contrario, queda
    # como 'IDENTIFICADOR'.
    t.type = reserved.get(t.value, 'IDENTIFICADOR')
    return t


def t_DECIMAL(t):
    r'[0-9]+\.[0-9]+'
    # Requiere obligatoriamente dígitos a ambos lados del punto decimal.
    # Se define antes de t_ENTERO para que gane la coincidencia más larga.
    return t


def t_ENTERO(t):
    r'[0-9]+'
    # Uno o más dígitos decimales sin signo.
    return t


def t_CADENA(t):
    r'"[^"\n]*"|\'[^\'\n]*\''
    # Cadena delimitada por comillas dobles o comillas simples en una sola línea.
    # No admite saltos de línea internos ni secuencias de escape.
    return t


# -----------------------------------------------------------------------------
# 5. CARACTERES IGNORADOS Y CONTROL DE LÍNEAS
# -----------------------------------------------------------------------------

# Espacios en blanco, tabulaciones y retornos de carro (CR) se descartan.
t_ignore = ' \t\r'


def t_COMMENT_BLOCK(t):
    r'/\*[\s\S]*?\*/'
    # Descarta comentarios de bloque /* ... */ (pueden ser multilínea y no anidados).
    # Se debe actualizar manualmente el contador de líneas sumando los '\n'.
    t.lexer.lineno += t.value.count('\n')


def t_newline(t):
    r'\n+'
    # Actualiza el contador de líneas del analizador ante saltos de línea.
    t.lexer.lineno += len(t.value)


# -----------------------------------------------------------------------------
# 6. MANEJO DE ERRORES LÉXICOS
# -----------------------------------------------------------------------------

# Lista global acumulativa de errores léxicos detectados durante el escaneo.
errores_lexicos = []


def t_error(t):
    """
    Captura caracteres que no pertenecen al vocabulario del lenguaje.
    Registra el número de línea, el carácter erróneo y su posición,
    y avanza el puntero de lectura en 1 carácter sin emitir prints ruidosos.
    """
    global errores_lexicos
    caracter = t.value[0]
    errores_lexicos.append({
        'linea': t.lexer.lineno,
        'caracter': caracter,
        'posicion': t.lexpos,
        'mensaje': f"carácter no válido '{caracter}'"
    })
    t.lexer.skip(1)


# -----------------------------------------------------------------------------
# 7. CONSTRUCTOR DEL ANALIZADOR LÉXICO
# -----------------------------------------------------------------------------

def crear_lexer():
    """
    Construye y retorna una nueva instancia del analizador léxico de PLY,
    reiniciando la lista de errores léxicos acumulados.
    """
    global errores_lexicos
    errores_lexicos = []
    return lex.lex(optimize=False)
