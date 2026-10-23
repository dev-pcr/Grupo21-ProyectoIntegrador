#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Batería integral de pruebas y regresión del compilador (Grupo 21)
================================================================================
Ejecuta TODO en una sola corrida y termina con código 0 solo si todo pasa:

  1. Micro-pruebas de regla de oro, bordes y robustez (en memoria).
  2. Casos públicos de la cátedra            (casos/esperado.csv).
  3. Casos propios de la entrega             (pruebas/esperado.csv).
  4. Batería masiva del grupo                (pruebas-grupo/esperado.csv).
  5. Pruebas end-to-end de la CLI            (subproceso `compilador.py archivo`).
  6. Auditoría de conflictos LALR            (0 shift/reduce y 0 reduce/reduce).

Criterio de la cátedra: un caso es correcto si la primera línea de stdout tiene
el tipo esperado y, en errores, la línea esperada.
Excepción (Anexo F): en los casos "tolerantes" se acepta ERROR LEXICO o ERROR
SINTACTICO indistintamente y no se evalúa la línea.

Uso (desde la raíz del proyecto):
    py herramientas/bateria_pruebas_compilador.py
================================================================================
"""

import csv
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import compilador   # noqa: E402
import sintactico   # noqa: E402

# Casos donde el Anexo F admite cualquiera de los dos tipos de error sin línea:
# comentario de otro lenguaje, comentario de bloque sin cerrar, operador ajeno.
TOLERANTES = {
    'sin-29-comentario-cpp.txt',
    'sin-30-comentario-sin-cerrar.txt',
}

# (nombre, código fuente, tipo esperado, línea esperada ('' si OK))
MICRO = [
    ('vacío', '', 'ERROR SINTACTICO', '1'),
    ('solo espacios y saltos', '  \n\n  ', 'ERROR SINTACTICO', '1'),
    ('solo comentarios', '/* a */\n/* b */', 'ERROR SINTACTICO', '1'),
    ('sentencia mínima', 'delay(1);', 'OK', ''),
    ('léxico antes que sintáctico', 'x = 1\n@\ny = 2;', 'ERROR LEXICO', '2'),
    ('sintáctico antes que léxico', 'x = ;\n@', 'ERROR SINTACTICO', '1'),
    ('misma línea gana léxico', 'x = @ ;', 'ERROR LEXICO', '1'),
    ('línea tras comentario multilínea', '/* a\nb\nc */\n@', 'ERROR LEXICO', '4'),
    ('EOF usa la línea del último token', 'x = 1\n\n\n', 'ERROR SINTACTICO', '1'),
    ('EOF con comentario final', 'x = 1 +\n/* fin */\n', 'ERROR SINTACTICO', '1'),
    ('CRLF cuenta una línea', 'x = 1;\r\ny = 2;\r\n@', 'ERROR LEXICO', '3'),
    ('CR solo no ensucia', 'delay(1);\rdelay(2);', 'OK', ''),
    ('sin newline final', 'delay(1);', 'OK', ''),
    ('Serial.println atómico', 'Serial.println("a");', 'OK', ''),
    ('Serial . println separado', 'Serial . println("a");', 'ERROR LEXICO', '1'),
    ('precedencia sin paréntesis', 'x = 1 + 2 * 3 - 4 / 2;', 'OK', ''),
    ('unario prohibido', 'x = -5;', 'ERROR SINTACTICO', '1'),
    ('delay como operando', 'x = 1 + delay(1);', 'ERROR SINTACTICO', '1'),
    ('map como sentencia y operando', 'map(1,2);\nx = map(1,2) + 1;', 'OK', ''),
    ('llamada sin argumentos', 'delay();', 'ERROR SINTACTICO', '1'),
    ('definición anidada', 'void setup() { void loop() { x = 1; } }', 'ERROR SINTACTICO', '1'),
    ('bloque vacío', 'void setup() { }', 'ERROR SINTACTICO', '1'),
    ('cadena simple y doble', 'char a = "x";\nchar b = \'y\';', 'OK', ''),
    ('cadena sin cerrar', 'char a = "x;', 'ERROR LEXICO', '1'),
    ('decimal con punto colgante', 'x = 3.;', 'ERROR LEXICO', '1'),
    ('identificador con guion bajo', '_a1 = 2;', 'OK', ''),
    ('palabra reservada como variable', 'float loop;', 'ERROR SINTACTICO', '1'),
    ('no hay incremento', 'x++;', 'ERROR SINTACTICO', '1'),
]


def leer(ruta):
    with open(ruta, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def descomponer(salida):
    """Devuelve (tipo, linea) de la primera línea de salida."""
    if salida == 'OK':
        return 'OK', ''
    for tipo in ('ERROR LEXICO', 'ERROR SINTACTICO'):
        if salida.startswith(tipo + ' linea '):
            resto = salida[len(tipo) + len(' linea '):]
            return tipo, resto.split(':')[0].strip()
    return 'DESCONOCIDO', ''


def coincide(salida, tipo_esp, linea_esp, tolerante=False):
    tipo, linea = descomponer(salida)
    if tolerante:
        return tipo in ('ERROR LEXICO', 'ERROR SINTACTICO')
    return tipo == tipo_esp and linea == linea_esp


def seccion(titulo):
    print('-' * 78)
    print(titulo)
    print('-' * 78)


def correr_csv(carpeta, etiqueta):
    """Ejecuta todos los casos de <carpeta>/esperado.csv en memoria."""
    ruta = os.path.join(RAIZ, carpeta, 'esperado.csv')
    with open(ruta, encoding='utf-8', newline='') as f:
        filas = [fila for fila in csv.DictReader(f) if fila['archivo']]
    fallos = 0
    for fila in filas:
        nombre = fila['archivo']
        salida = compilador.compilar_codigo(leer(os.path.join(RAIZ, carpeta, nombre)))
        if not coincide(salida, fila['esperado'], fila['linea'], nombre in TOLERANTES):
            fallos += 1
            print(f"  [FALLA] {nombre}: esperado={fila['esperado']} {fila['linea']} | obtenido={salida}")
    print(f"{etiqueta}: {len(filas) - fallos}/{len(filas)} aprobados\n")
    return fallos == 0


def test_micro():
    seccion('1. MICRO-PRUEBAS (regla de oro, bordes y robustez)')
    fallos = 0
    for nombre, codigo, tipo, linea in MICRO:
        salida = compilador.compilar_codigo(codigo)
        if not coincide(salida, tipo, linea):
            fallos += 1
            print(f"  [FALLA] {nombre}: esperado={tipo} {linea} | obtenido={salida}")
    print(f"Micro-pruebas: {len(MICRO) - fallos}/{len(MICRO)} aprobadas\n")
    return fallos == 0


def test_cli():
    seccion('5. END-TO-END DE LA CLI (python compilador.py archivo)')
    pares = [
        ('pruebas/valido.txt', 'OK', ''),
        ('pruebas/error.txt', 'ERROR SINTACTICO', '13'),
        ('casos/lexico-01.txt', 'ERROR LEXICO', '3'),
        ('casos/sintactico-03.txt', 'ERROR SINTACTICO', '4'),
    ]
    fallos = 0
    for rel, tipo, linea in pares:
        r = subprocess.run([sys.executable, 'compilador.py', rel], cwd=RAIZ,
                           capture_output=True, timeout=10)
        primera = r.stdout.decode('utf-8', errors='replace').splitlines()
        primera = primera[0] if primera else ''
        if not coincide(primera, tipo, linea):
            fallos += 1
            print(f"  [FALLA] {rel}: esperado={tipo} {linea} | obtenido={primera!r} | stderr={r.stderr[:200]!r}")
    # Archivo inexistente: no debe lanzar traceback.
    r = subprocess.run([sys.executable, 'compilador.py', 'no-existe.txt'], cwd=RAIZ,
                       capture_output=True, timeout=10)
    if b'Traceback' in r.stderr:
        fallos += 1
        print('  [FALLA] archivo inexistente produjo traceback')
    # Sin argumentos: debe mostrar uso, sin traceback.
    r = subprocess.run([sys.executable, 'compilador.py'], cwd=RAIZ,
                       capture_output=True, timeout=10)
    if b'Traceback' in r.stderr or b'Uso' not in r.stdout:
        fallos += 1
        print('  [FALLA] sin argumentos no muestra el uso')
    total = len(pares) + 2
    print(f"CLI: {total - fallos}/{total} aprobados\n")
    return fallos == 0


def test_conflictos():
    seccion('6. AUDITORÍA DE CONFLICTOS LALR (parser.out)')
    c = sintactico.auditar_conflictos()
    for adv in c['advertencias']:
        print(f"  advertencia PLY: {adv}")
    print(f"Conflictos shift/reduce: {c['shift_reduce']} | reduce/reduce: {c['reduce_reduce']}\n")
    return c['shift_reduce'] == 0 and c['reduce_reduce'] == 0


def main():
    print('=' * 78)
    print('BATERÍA INTEGRAL DE PRUEBAS Y REGRESIÓN — COMPILADOR GRUPO 21')
    print('=' * 78 + '\n')

    resultados = [test_micro()]
    seccion('2. CASOS PÚBLICOS DE LA CÁTEDRA (casos/)')
    resultados.append(correr_csv('casos', 'Casos públicos'))
    seccion('3. CASOS PROPIOS DE LA ENTREGA (pruebas/)')
    resultados.append(correr_csv('pruebas', 'Casos de entrega'))
    seccion('4. BATERÍA MASIVA DEL GRUPO (pruebas-grupo/)')
    resultados.append(correr_csv('pruebas-grupo', 'Batería de grupo'))
    resultados.append(test_cli())
    resultados.append(test_conflictos())

    print('=' * 78)
    ok = all(resultados)
    print('VEREDICTO FINAL:', 'TODO CORRECTO (100%)' if ok else 'HAY FALLOS (ver [FALLA] arriba)')
    print('=' * 78)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
