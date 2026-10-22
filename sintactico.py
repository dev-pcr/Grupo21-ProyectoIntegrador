#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Analizador Sintáctico (ply.yacc) — Subconjunto de Arduino (C++ microcontrolador)
Facultad de Ingeniería — UCASAL — Compiladores 2026
Grupo N.º 21
Responsable: Pablo (Persona 2)
================================================================================
Implementa las reglas gramaticales estratificadas (sin tabla precedence)
según la especificación formal aprobada en gramatica.txt.

Resumen de decisiones de diseño (útil para la defensa oral):

1. PRECEDENCIA POR ESTRATIFICACIÓN
   La precedencia y la asociatividad de los operadores aritméticos NO se
   resuelven con una tabla `precedence` de PLY, sino con la propia forma de la
   gramática (igual que el modelo de la cátedra, calcyacc.py):

        expresion -> expresion (+|-) termino | termino      (menor precedencia)
        termino   -> termino (*|/) factor    | factor       (mayor precedencia)
        factor    -> operandos básicos o ( expresion )

   La recursión por la IZQUIERDA (expresion -> expresion SUMA termino) da la
   asociatividad izquierda; el hecho de que '*' y '/' vivan un nivel más abajo
   que '+' y '-' hace que se agrupen primero. Resultado: 0 conflictos.

2. BLINDAJE ANTE FIN DE ARCHIVO PREMATURO (EOF)
   Cuando el archivo termina "antes de tiempo", PLY invoca p_error(None). Los
   ejemplos de la cátedra acceden a p.lineno sin comprobar None y por eso
   fallan con AttributeError. Aquí:
     - p_error comprueba explícitamente `p is None`.
     - TrackingLexer (adaptador del lexer) memoriza la línea del ÚLTIMO token
       entregado al parser; esa es la línea que se informa ante un EOF.

3. PRIMER ERROR GANA
   p_error registra el error y lanza una excepción: el análisis se interrumpe
   en el primer error sintáctico (no hay recuperación de errores).
================================================================================
"""

import os
import re
import sys

import ply.yacc as yacc
from lexico import tokens
import lexico

# Variable para almacenar el error sintáctico detectado
error_sintactico = None

# Variable auxiliar para recordar la línea del último token procesado (crucial para EOF)
ultimo_token_lineno = 1


# -----------------------------------------------------------------------------
# 1. ESTRUCTURA DEL PROGRAMA Y NIVEL SUPERIOR
# -----------------------------------------------------------------------------
# Un programa es una secuencia NO vacía de elementos. Un archivo vacío o con
# solo comentarios es un error sintáctico (ver sin-01 y sin-02).
# La recursión izquierda (programa elemento) permite encadenar elementos sin
# consumir pila de forma innecesaria en LALR.

def p_programa(p):
    '''programa : elemento
                | programa elemento'''
    pass

# Un elemento de nivel superior es una sentencia suelta o una definición
# (setup/loop). Pueden aparecer mezcladas, repetidas y en cualquier orden.
def p_elemento(p):
    '''elemento : sentencia
                | definicion'''
    pass


# -----------------------------------------------------------------------------
# 2. DEFINICIONES DE SETUP Y LOOP
# -----------------------------------------------------------------------------
# void setup() { sentencias }  /  void loop() { sentencias }
# El cuerpo exige AL MENOS una sentencia (sin-03 y sin-04: bloque vacío = error)
# y no admite parámetros ni anidamiento de definiciones.

def p_definicion(p):
    '''definicion : VOID SETUP PARENTESIS_IZQ PARENTESIS_DER LLAVE_IZQ sentencias LLAVE_DER
                  | VOID LOOP PARENTESIS_IZQ PARENTESIS_DER LLAVE_IZQ sentencias LLAVE_DER'''
    pass


# -----------------------------------------------------------------------------
# 3. BLOQUES Y SENTENCIAS
# -----------------------------------------------------------------------------

# Lista de una o más sentencias (cuerpo de setup/loop).
def p_sentencias(p):
    '''sentencias : sentencia
                  | sentencias sentencia'''
    pass

# Tres clases de sentencia. Cada declaración y asignación ya incluye su ';';
# las llamadas a función lo reciben aquí.
def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | llamada_sentencia PUNTO_Y_COMA'''
    pass

# Declaración con o sin inicialización:  float x;   float x = 1.5;
def p_declaracion(p):
    '''declaracion : tipo IDENTIFICADOR PUNTO_Y_COMA
                   | tipo IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA'''
    pass

# Asignación simple y compuesta:  x = e;   x += e;   x -= e;
def p_asignacion(p):
    '''asignacion : IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA
                  | IDENTIFICADOR SUMA_IGUAL expresion PUNTO_Y_COMA
                  | IDENTIFICADOR RESTA_IGUAL expresion PUNTO_Y_COMA'''
    pass

# Tipos de dato del lenguaje (el compilador NO verifica tipos, ver ok-28).
def p_tipo(p):
    '''tipo : BOOLEAN
            | CHAR
            | FLOAT'''
    pass


# -----------------------------------------------------------------------------
# 4. LLAMADAS A FUNCIONES
# -----------------------------------------------------------------------------
# Distinción clave: las funciones SIN valor (delay, Serial.println) solo pueden
# usarse como sentencia; la función CON valor (map) puede además ser operando
# dentro de una expresión (aparece también en la regla de factor).

def p_llamada_sentencia(p):
    '''llamada_sentencia : llamada_sin_valor
                         | llamada_valor'''
    pass

def p_llamada_sin_valor(p):
    '''llamada_sin_valor : DELAY PARENTESIS_IZQ argumentos PARENTESIS_DER
                         | SERIAL_PRINTLN PARENTESIS_IZQ argumentos PARENTESIS_DER'''
    pass

def p_llamada_valor(p):
    '''llamada_valor : MAP PARENTESIS_IZQ argumentos PARENTESIS_DER'''
    pass

# Uno o más argumentos separados por coma (no se admiten listas vacías ni
# comas sobrantes: sin-07, sin-22, sin-92, sin-93).
def p_argumentos(p):
    '''argumentos : expresion
                  | argumentos COMA expresion'''
    pass


# -----------------------------------------------------------------------------
# 5. EXPRESIONES JERÁRQUICAS ESTRATIFICADAS (Sin tabla precedence externa)
# -----------------------------------------------------------------------------
# Nivel 1 (menor precedencia): suma y resta, asociativos por la izquierda.
def p_expresion(p):
    '''expresion : expresion SUMA termino
                 | expresion RESTA termino
                 | termino'''
    pass

# Nivel 2 (mayor precedencia): multiplicación y división, asoc. por la izquierda.
def p_termino(p):
    '''termino : termino MULTIPLICACION factor
               | termino DIVISION factor
               | factor'''
    pass

# Nivel 3: operandos. Notar que NO hay operadores unarios (sin-05, sin-06) y que
# delay/Serial.println no figuran aquí (sin-09, sin-10).
def p_factor(p):
    '''factor : IDENTIFICADOR
              | numero
              | PARENTESIS_IZQ expresion PARENTESIS_DER
              | llamada_valor
              | CADENA
              | booleano
              | constante'''
    pass

# Números sin signo: enteros y decimales.
def p_numero(p):
    '''numero : ENTERO
              | DECIMAL'''
    pass

# Literales booleanos.
def p_booleano(p):
    '''booleano : TRUE
                | FALSE'''
    pass

# Constantes predefinidas de Arduino.
def p_constante(p):
    '''constante : HIGH
                 | INPUT
                 | INPUT_PULLUP
                 | LED_BUILTIN
                 | LOW
                 | OUTPUT'''
    pass


# -----------------------------------------------------------------------------
# 6. MANEJO ROBUSTO DE ERRORES SINTÁCTICOS (Incluye blindaje ante EOF)
# -----------------------------------------------------------------------------

def p_error(p):
    """
    Captura de errores sintácticos.
    IMPORTANTE: Si el archivo termina inesperadamente (EOF), p es None.
    Se debe consultar ultimo_token_lineno para no provocar AttributeError.
    """
    global error_sintactico
    if p is None:
        # Fin de archivo inesperado
        error_sintactico = {
            'linea': ultimo_token_lineno,
            'mensaje': "fin de archivo prematuro inesperado"
        }
    else:
        # Token inesperado
        error_sintactico = {
            'linea': p.lineno,
            'token': p.value,
            'mensaje': f"se encontro '{p.value}' no esperado"
        }
    
    # Interrumpir el análisis inmediatamente (modelo visto en calcyacc.py)
    raise Exception('syntax', 'error')


# -----------------------------------------------------------------------------
# 7. CONSTRUCTOR DEL ANALIZADOR SINTÁCTICO
# -----------------------------------------------------------------------------

def crear_parser():
    """Construye y retorna la instancia del parser de PLY."""
    global error_sintactico
    error_sintactico = None
    # write_tables=False para no generar archivos parsetab.py innecesarios en corrida limpia.
    # debug=False para no escribir parser.out en cada ejecución (ver auditar_conflictos()).
    return yacc.yacc(module=sys.modules[__name__], write_tables=False, debug=False)


# -----------------------------------------------------------------------------
# 8. ADAPTADOR DEL LEXER (SEGUIMIENTO DE LA LÍNEA DEL ÚLTIMO TOKEN)
# -----------------------------------------------------------------------------

class TrackingLexer:
    """
    Envoltorio transparente del lexer de PLY.

    PLY solo necesita que el objeto exponga input() y token(). Cada vez que el
    parser pide un token, este adaptador lo delega al lexer real y guarda su
    número de línea en `ultimo_token_lineno`. Si más adelante el archivo termina
    antes de tiempo, p_error(None) usa ese valor como línea del error.
    """

    def __init__(self, lexer):
        self.lexer = lexer

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        global ultimo_token_lineno
        tok = self.lexer.token()
        if tok is not None:
            ultimo_token_lineno = tok.lineno
        return tok


# -----------------------------------------------------------------------------
# 9. FUNCIÓN DE ALTO NIVEL: analizar()
# -----------------------------------------------------------------------------

_parser = None  # Parser construido una sola vez y reutilizado entre llamadas


def analizar(codigo):
    """
    Analiza sintácticamente `codigo` (str) y retorna una tupla (exito, error):
      - (True,  None)         si el programa es sintácticamente correcto.
      - (False, dict_error)   con claves 'linea' y 'mensaje' (y 'token' si no
                              fue EOF) ante el PRIMER error sintáctico.

    Los errores léxicos NO se reportan aquí: quedan acumulados en
    lexico.errores_lexicos para que compilador.py aplique la regla de orden.
    """
    global error_sintactico, ultimo_token_lineno, _parser

    if _parser is None:
        _parser = crear_parser()

    error_sintactico = None
    ultimo_token_lineno = 1

    lexer = lexico.crear_lexer()   # también reinicia lexico.errores_lexicos
    lexer.lineno = 1
    tracking = TrackingLexer(lexer)

    try:
        _parser.parse(codigo, lexer=tracking)
    except Exception:
        if error_sintactico is None:
            # Excepción inesperada ajena a p_error: no ocultarla.
            raise
        return False, error_sintactico

    return True, None


# -----------------------------------------------------------------------------
# 10. AUDITORÍA DE CONFLICTOS (parser.out)
# -----------------------------------------------------------------------------

class _RegistroPLY:
    """Logger mínimo que acumula las advertencias que PLY emite al construir."""

    def __init__(self):
        self.mensajes = []

    def debug(self, msg, *args, **kwargs):
        pass

    info = debug

    def warning(self, msg, *args, **kwargs):
        self.mensajes.append(msg % args if args else msg)

    error = warning
    critical = warning


def auditar_conflictos():
    """
    Reconstruye la tabla LALR escribiendo parser.out (junto a este archivo) y
    retorna un dict con la cantidad de conflictos shift/reduce y reduce/reduce.
    El objetivo del proyecto es {'shift_reduce': 0, 'reduce_reduce': 0}.
    """
    registro = _RegistroPLY()
    carpeta = os.path.dirname(os.path.abspath(__file__))
    yacc.yacc(module=sys.modules[__name__], write_tables=False, debug=True,
              debugfile='parser.out', outputdir=carpeta, errorlog=registro)

    conteo = {'shift_reduce': 0, 'reduce_reduce': 0}
    for msg in registro.mensajes:
        m = re.search(r'(\d+) (shift/reduce|reduce/reduce) conflict', msg)
        if m:
            clave = 'shift_reduce' if m.group(2) == 'shift/reduce' else 'reduce_reduce'
            conteo[clave] += int(m.group(1))
    conteo['advertencias'] = registro.mensajes
    return conteo
