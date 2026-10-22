# -*- coding: utf-8 -*-
""" 

(basado en https://www.dabeaz.com/ply/ply.html#ply_nn24)

Gramática para generar expresiones aritméticas
============================================

expresión --> expresión + término
           | expresión - término
           | término

término --> término * factor
           | término / factor
           | factor

factor --> NÚMERO
           | ( expresión )


ANALIZADOR LEXICO para la gramática anterior."""



# Instalar librerías

#!pip install ply

#Importar librerías

import warnings
warnings.simplefilter('ignore')

# Importar libreria LEX
from ply import lex


# Declaración de tokens de la gramática
tokens = ['NUMERO', 'MAS','MENOS','MULT','DIV', 'PARAB','PARCI']

# Definicion de Tokens (ER)
t_MAS = r'\+'
t_MENOS = r'\-'
t_MULT = r'\*'
t_DIV = r'\/'

def t_NUMERO(t): #define número sin signo
    r"[0-9]+"
    t.value = int(t.value)
    return t

t_PARAB = r"\("
t_PARCI = r"\)"

t_ignore = r' '

# Definir la función t_error para el tratamiento de errores.
def t_error(t):
    print("__________________")
    print("Error: %s en linea %s" % (repr(t.value[0]), lexer.lineno))
    t.lexer.skip(1)


# Construcción del analizador léxico
lexer = lex.lex()
