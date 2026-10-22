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

# ANALIZADOR SINTACTICO para la gramática anterior.

Además se agrega código (gramática dirigida por la sintaxis) para calcular el valor de la expresión ingresada.
Se utiliza el analizador léxico escrito en otro archivo """



import warnings
warnings.simplefilter('ignore')


# Importar libreria Yacc y tokens definidos en CalcLex
import calclex
from ply import yacc

#a partir de aqui se definen los procedimientos asociados a las reglas de producción de la gramática
# --------------------------------------------------------------------------------------------------

#expresión --> expresión + término | expresión - término | término
def p_expresion(p):
  '''expresion : expresion MAS termino
               | expresion MENOS termino
               | termino'''


  if(len(p)>2):
    if p[2] == '+':
      p[0] = p[1] + p[3]
    elif p[2] == '-':
      p[0] = p[1]-p[3]
  else:
    p[0] = p[1]

  pass

#término --> término * factor | término / factor | factor
def p_termino(p):
    '''termino : termino MULT factor
               | termino DIV factor
               | factor
    '''

    if(len(p)>2):
      if p[2] == '*':
        p[0] = p[1] * p[3]
      elif p[2] == '/':
        p[0] = p[1]/p[3]
    else:
      p[0] = p[1]

    pass

#factor --> NÚMERO | ( expresión )
def p_factor(p):
    '''factor : NUMERO
              | PARAB expresion PARCI
    '''

    if len(p)==2:
       p[0] = p[1]
    else:
       p[0] = p[2]

    pass

def p_error(p):
  print("Error sintáctico en la línea: " + str(p.lineno)
              + ". No se esperaba el token: " + str(p.value))
  raise Exception('syntax', 'error')


# construcción del parser:
parser = yacc.yacc(write_tables=False)

