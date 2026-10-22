# -*- coding: utf-8 -*-
""" 

Lenguaje L = {(ab)^n bc| n>=0}
===========================================

ANALIZADOR LEXICO para el lenguaje L."""


#!pip install ply

#Importar librerías

import warnings
warnings.simplefilter('ignore')

# Importar libreria LEX
from ply import lex


# Declaración de tokens de la gramática
tokens = ['LETRAA', 'LETRAB','LETRAC']

# Definicion de Tokens (ER)
t_LETRAA = r'[aA]'
t_LETRAB = r'[bB]'
t_LETRAC = r'[cC]'

t_ignore = r' \n\t'

# Definir la función t_error para el tratamiento de errores.
def t_error(t):
    print("Error: Símbolo no válido: "+t.value[0])
    t.lexer.skip(1)


# Construcción del analizador léxico
lexer = lex.lex()

