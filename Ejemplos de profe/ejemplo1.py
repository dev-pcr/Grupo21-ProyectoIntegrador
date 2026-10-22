# -*- coding: utf-8 -*-
""" 

Lenguaje L = {(ab)^n bc| n>=0}
===========================================

Gramática:
    S -> a b S | b P
    P -> c 


Programa principal
===================

Se analiza una cadena de símbolos A, B y C, usando los analizadores léxico y sintáctico definidos en otros archivos.
Debe comenzar con subcadenas "ab" y finaliza con "bc". También debe indicar la cantidad de repeticiones de "ab"

"""

# se importa el analizador sintáctico      
import ej1yacc
from ej1yacc import *


# ingrese una cadena para analizar y calcular el resultado
data= input('Ingrese una cadena para analizar: ')

try:
         resultado = parser.parse(data)
         print('\n ¡Analisis sintactico correcto!','\n')
         print('La cantidad de repeticiones de "ab" es: ', resultado)
except:
         print('\n Analisis sintactico incorrecto')