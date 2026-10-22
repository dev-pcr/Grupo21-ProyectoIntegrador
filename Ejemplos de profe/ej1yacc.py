# -*- coding: utf-8 -*-
""" 

Lenguaje L = {(ab)^n bc| n>=0}
===========================================

Gramática:
    S -> a b S | b P
    P -> c 


ANALIZADOR SINTACTICO para el lenguaje L.
Además de verificar la cadena de entrada, mostrar la cantidad de repeticiones de "ab" (valor de n)


Nota: la gramática que genera este lenguaje puede ser distinta (pruebe otra forma)

"""

import warnings
warnings.simplefilter('ignore')

# Importar libreria Yacc y tokens definidos en otro archivo
from ej1lex import tokens
from ply import yacc

#a partir de aqui se definen los procedimientos asociados a las reglas de producción de la gramática
# --------------------------------------------------------------------------------------------------


#S -> b P
def p_S_2(p):
  '''S : LETRAB P'''
  p[0] = 0
  pass

#S -> a b S
def p_S_1(p):
  '''S : LETRAA LETRAB S'''
  p[0] = 1 + p[3]
  pass

# P -> c
def p_P_1(p):
    '''P : LETRAC'''  
    pass

def p_error(p):
  print("Error sintáctico. No se esperaba el token: " + str(p.value))
  raise Exception('syntax', 'error')


# construcción del parser:
parser = yacc.yacc()
