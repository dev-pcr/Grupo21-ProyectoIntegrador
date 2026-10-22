# -*- coding: utf-8 -*-
""""

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

"""    
"""
 Programa - Calculador
#########################

Se analiza una expresión aritmética y si es válida se devuelve el valor calculado, usando los analizadores léxico y sintáctico definidos en otros archivos.

Ejemplo:
Si la cadena de entrada es: 32 + 15/3  el programa devolverá 37 e indicará que la cadena es correcta.
Caso contrario, indicará que el análisis sintáctico no se pudo realizar.
"""

# se importa el analizador sintáctico      
import calcyacc
from calcyacc import *

# ingrese una cadena para analizar y calcular el resultado
data= input('Ingrese una expresión artimética para analizar y calcular el resultado: ')

try:
         resultado = parser.parse(data)
         print('\n ¡Analisis sintactico correcto!','\n')
         print('El resultado de la expresión es: ', resultado)
except:
         print('\n Analisis sintactico incorrecto')