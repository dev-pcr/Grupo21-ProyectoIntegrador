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
import tempfile

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
    ('misma línea: léxico a la izquierda gana', 'x = @ ;', 'ERROR LEXICO', '1'),
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
    # ------------------------------------------------------------------
    # Casos agregados por Emiliano (23/10): auditoría de integración.
    # Nomenclatura E-<grupo><n>: a = mezcla léxico/sintáctico, b = léxicos,
    # c = sintácticos. Los casos E-a3, E-a12, E-a13..E-a15 fijan la regla de
    # oro por POSICIÓN: en la misma línea gana el error más a la izquierda.
    # ------------------------------------------------------------------
    # --- a) Mezcla de errores léxicos y sintácticos (regla de oro) ---
    ('E-a1 sint l2 antes de lex l3', 'x = 1;\ny = ;\n@', 'ERROR SINTACTICO', '2'),
    ('E-a2 lex l2 antes de sint l3', 'x = 1;\n@\ny = ;', 'ERROR LEXICO', '2'),
    ('E-a3 misma linea: sint a la izquierda', 'x = ; @', 'ERROR SINTACTICO', '1'),
    ('E-a4 EOF y lex en l3', 'x = 1 +\n\n@', 'ERROR LEXICO', '3'),
    ('E-a5 dos lex misma linea', '@ @\nx = ;', 'ERROR LEXICO', '1'),
    ('E-a6 varios lex, gana el primero', 'x = 1;\n$\n#', 'ERROR LEXICO', '2'),
    ('E-a7 EOF tras ) y lex l2', 'delay(1)\n@', 'ERROR LEXICO', '2'),
    ('E-a8 sint l1 con lex l2', 'x = 1 2;\n@', 'ERROR SINTACTICO', '1'),
    ('E-a9 lex al inicio, sint despues', '@\nx = ;', 'ERROR LEXICO', '1'),
    ('E-a10 lex dentro de comentario no cuenta', '/* @ */\nx = ;', 'ERROR SINTACTICO', '2'),
    ('E-a11 sint tras comentario multilinea', '/* a\nb */ x = ;', 'ERROR SINTACTICO', '2'),
    ('E-a12 sint a la izquierda del lex, misma linea', 'x = 1 2 @;', 'ERROR SINTACTICO', '1'),
    ('E-a13 lex a la izquierda del sint, misma linea', 'x = 1 @ 2;', 'ERROR LEXICO', '1'),
    ('E-a14 ex lex-33: sint (b) antes de comilla sin cerrar', 'x = "a\\"b";', 'ERROR SINTACTICO', '1'),
    ('E-a15 ex lex-45: sint (cadena inicial) antes de comilla', "'abc'def'", 'ERROR SINTACTICO', '1'),
    ('E-a16 solo lex: comilla escapada al final', 'x = "a\\" + b";', 'ERROR LEXICO', '1'),
    # --- b) Casos límite léxicos ---
    ('E-b1 comentario sin cerrar', 'x = 1; /* abierto\ny = 2;', 'ERROR SINTACTICO', '1'),
    ('E-b2 dos comentarios', '/* a */ /* b */ x = 1;', 'OK', ''),
    ('E-b3 no anidado', '/* a /* b */ x = 1;', 'OK', ''),
    ('E-b4 cierre suelto', 'x = 1; */', 'ERROR SINTACTICO', '1'),
    ('E-b5 cadena con salto', 'char a = "abc\nb";', 'ERROR LEXICO', '1'),
    ('E-b6 comilla simple sin cerrar', "char a = 'abc;", 'ERROR LEXICO', '1'),
    ('E-b7 .5', 'x = .5;', 'ERROR LEXICO', '1'),
    ('E-b8 1.2.3', 'x = 1.2.3;', 'ERROR LEXICO', '1'),
    ('E-b9 1..5', 'x = 1..5;', 'ERROR LEXICO', '1'),
    ('E-b10 float setup', 'float setup;', 'ERROR SINTACTICO', '1'),
    ('E-b11 float HIGH', 'float HIGH;', 'ERROR SINTACTICO', '1'),
    ('E-b12 float map', 'float map;', 'ERROR SINTACTICO', '1'),
    ('E-b13 float delay', 'float delay;', 'ERROR SINTACTICO', '1'),
    ('E-b14 float void', 'float void;', 'ERROR SINTACTICO', '1'),
    ('E-b15 float true', 'float true;', 'ERROR SINTACTICO', '1'),
    ('E-b16 identificadores parecidos', 'mapa = 1;\nfloat1 = 2;\nHIGH2 = 1;\nloopx = 1;\nINPUT_PULLUP2 = 1;\nSerialx = 1;\nserial = 1;\nDelay = 1;\nINPUTS = 1;', 'OK', ''),
    ('E-b17 Serial.print', 'Serial.print("a");', 'ERROR LEXICO', '1'),
    ('E-b18 Serial.println con espacio antes (', 'Serial.println ("a");', 'OK', ''),
    ('E-b19 Serial .println', 'Serial .println("a");', 'ERROR LEXICO', '1'),
    ('E-b20 ==', 'x = a == b;', 'ERROR SINTACTICO', '1'),
    ('E-b21 !', 'x = !a;', 'ERROR LEXICO', '1'),
    ('E-b22 &', 'x = a & b;', 'ERROR LEXICO', '1'),
    ('E-b23 enie', 'ñ = 1;', 'ERROR LEXICO', '1'),
    ('E-b24 enie en cadena', 'x = "ñ";', 'OK', ''),
    ('E-b25 tilde', 'x = é;', 'ERROR LEXICO', '1'),
    ('E-b26 tabs', 'x\t=\t1;', 'OK', ''),
    ('E-b27 cadenas juntas', 'x = "a" "b";', 'ERROR SINTACTICO', '1'),
    ('E-b28 cadena vacia', 'x = "";', 'OK', ''),
    ('E-b29 08', 'x = 08;', 'OK', ''),
    ('E-b30 1_0', 'x = 1_0;', 'ERROR SINTACTICO', '1'),
    ('E-b31 3x', '3x = 1;', 'ERROR SINTACTICO', '1'),
    ('E-b32 comentario en expresion', 'x = /* c */ 1;', 'OK', ''),
    ('E-b33 comentario multilinea y sint', 'x = 1 /* a\nb */ + ;', 'ERROR SINTACTICO', '2'),
    ('E-b34 // ', 'x = 1; // c', 'ERROR SINTACTICO', '1'),
    ('E-b35 comilla cruzada', 'x = "a\'b";\ny = \'a"b\';', 'OK', ''),
    ('E-b37 lex en l5 tras comentario', '/*\n\n\n*/ @', 'ERROR LEXICO', '4'),
    ('E-b38 tab y CR en cadena', 'x = "a\tb";', 'OK', ''),
    ('E-b39 # directiva', '#define X 1', 'ERROR LEXICO', '1'),
    ('E-b40 simbolo [', 'x = a[1];', 'ERROR LEXICO', '1'),
    ('E-b41 punto suelto', 'x = a.b;', 'ERROR LEXICO', '1'),
    # --- c) Casos límite sintácticos ---
    ('E-c1 x =', 'x =', 'ERROR SINTACTICO', '1'),
    ('E-c2 map(', 'map(', 'ERROR SINTACTICO', '1'),
    ('E-c3 void setup() {', 'void setup() {', 'ERROR SINTACTICO', '1'),
    ('E-c4 float', 'float', 'ERROR SINTACTICO', '1'),
    ('E-c5 float x', 'float x', 'ERROR SINTACTICO', '1'),
    ('E-c6 float x =', 'float x =', 'ERROR SINTACTICO', '1'),
    ('E-c7 delay(1', 'delay(1', 'ERROR SINTACTICO', '1'),
    ('E-c8 delay(1;', 'delay(1;', 'ERROR SINTACTICO', '1'),
    ('E-c9 EOF en l2', 'void setup() {\n x = 1;\n', 'ERROR SINTACTICO', '2'),
    ('E-c10 setup con param', 'void setup(int a) { x = 1; }', 'ERROR SINTACTICO', '1'),
    ('E-c11 sin void', 'setup() { x = 1; }', 'ERROR SINTACTICO', '1'),
    ('E-c12 llave de mas', 'void setup() { x = 1; } }', 'ERROR SINTACTICO', '1'),
    ('E-c13 setup anidado', 'void setup() { void setup() { x = 1; } }', 'ERROR SINTACTICO', '1'),
    ('E-c14 void main', 'void main() { x = 1; }', 'ERROR SINTACTICO', '1'),
    ('E-c15 -x', 'x = -x;', 'ERROR SINTACTICO', '1'),
    ('E-c16 1 - -1', 'x = 1 - -1;', 'ERROR SINTACTICO', '1'),
    ('E-c17 +1', 'x = +1;', 'ERROR SINTACTICO', '1'),
    ('E-c18 (1;', 'x = (1;', 'ERROR SINTACTICO', '1'),
    ('E-c19 1);', 'x = 1);', 'ERROR SINTACTICO', '1'),
    ('E-c20 ()', 'x = ();', 'ERROR SINTACTICO', '1'),
    ('E-c21 coma final', 'delay(1,);', 'ERROR SINTACTICO', '1'),
    ('E-c22 coma inicial', 'delay(,1);', 'ERROR SINTACTICO', '1'),
    ('E-c23 map 5 args', 'map(1,2,3,4,5);', 'OK', ''),
    ('E-c24 map()', 'map();', 'ERROR SINTACTICO', '1'),
    ('E-c25 ; suelto', ';', 'ERROR SINTACTICO', '1'),
    ('E-c26 ;;', 'x = 1;;', 'ERROR SINTACTICO', '1'),
    ('E-c27 Serial anidado', 'Serial.println(Serial.println(1));', 'ERROR SINTACTICO', '1'),
    ('E-c28 x = Serial.println', 'x = Serial.println(1);', 'ERROR SINTACTICO', '1'),
    ('E-c29 x = delay', 'x = delay(1);', 'ERROR SINTACTICO', '1'),
    ('E-c30 delay(map)', 'delay(map(1,2));', 'OK', ''),
    ('E-c31 delay(delay)', 'delay(delay(1));', 'ERROR SINTACTICO', '1'),
    ('E-c32 parens profundos', 'x = ((((((1+2))))));', 'OK', ''),
    ('E-c33 precedencia larga', 'x = 1+2*3-4/2*5;', 'OK', ''),
    ('E-c34 * *', 'x = a * * b;', 'ERROR SINTACTICO', '1'),
    ('E-c35 * a', 'x = * a;', 'ERROR SINTACTICO', '1'),
    ('E-c36 x * 1;', 'x * 1;', 'ERROR SINTACTICO', '1'),
    ('E-c37 x;', 'x;', 'ERROR SINTACTICO', '1'),
    ('E-c38 1 = x', '1 = x;', 'ERROR SINTACTICO', '1'),
    ('E-c39 falta ; y sigue', 'x = 1\ny = 2;', 'ERROR SINTACTICO', '2'),
    ('E-c40 float x = 1, y', 'float x = 1, y = 2;', 'ERROR SINTACTICO', '1'),
    ('E-c41 float x, y', 'float x, y;', 'ERROR SINTACTICO', '1'),
    ('E-c42 float x = float', 'float x = float;', 'ERROR SINTACTICO', '1'),
    ('E-c43 tipos', 'boolean b = true;\nchar c = HIGH;\nfloat f = 1.5;', 'OK', ''),
    ('E-c44 x += ;', 'x += ;', 'ERROR SINTACTICO', '1'),
    ('E-c45 =+', 'x =+ 1;', 'ERROR SINTACTICO', '1'),
    ('E-c46 + =', 'x + = 1;', 'ERROR SINTACTICO', '1'),
    ('E-c47 - =', 'x - = 1;', 'ERROR SINTACTICO', '1'),
    ('E-c48 x+=1', 'x+=1;', 'OK', ''),
    ('E-c49 loop solo comentario', 'void loop() {\n /* c */\n}', 'ERROR SINTACTICO', '3'),
    ('E-c50 orden libre', 'void setup() { x = 1; }\nvoid loop() { y = 2; }\nvoid setup() { z = 3; }', 'OK', ''),
    ('E-c51 mezcla top', 'delay(1);\nvoid setup() { x = 1; }\nx = 2;', 'OK', ''),
    ('E-c52 formato libre', 'void\nsetup\n(\n)\n{\nx=1;\n}', 'OK', ''),
    ('E-c53 Serial.println()', 'Serial.println();', 'ERROR SINTACTICO', '1'),
    ('E-c54 sin tipos', 'x = "a" + 1;\nx = true + HIGH;', 'OK', ''),
    ('E-c55 llamada con constante', 'delay(HIGH);', 'OK', ''),
    ('E-c56 decl sin ;', 'float x = 1\n', 'ERROR SINTACTICO', '1'),
    ('E-c57 asign sin ident', '= 1;', 'ERROR SINTACTICO', '1'),
    ('E-c58 }', '}', 'ERROR SINTACTICO', '1'),
    ('E-c59 {', '{ x = 1; }', 'ERROR SINTACTICO', '1'),
    ('E-c60 void solo', 'void', 'ERROR SINTACTICO', '1'),
    ('E-c61 void setup', 'void setup', 'ERROR SINTACTICO', '1'),
    ('E-c62 void setup()', 'void setup()', 'ERROR SINTACTICO', '1'),
    ('E-c63 setup solo', 'setup', 'ERROR SINTACTICO', '1'),
    ('E-c64 llamada map(x)(y)', 'map(1,2)(3);', 'ERROR SINTACTICO', '1'),
    ('E-c65 map(1,2)+1;', 'map(1,2) + 1;', 'ERROR SINTACTICO', '1'),
    ('E-c66 decl en lugar de llamada', 'float delay(1);', 'ERROR SINTACTICO', '1'),
    ('E-c69 multiplos EOF l5', 'x = 1;\ny = 2;\n\n\n\nz =', 'ERROR SINTACTICO', '6'),
    ('E-c70 CR solo y sint', 'x = 1;\ry = ;', 'ERROR SINTACTICO', '1'),
    # --- Robustez ante entradas grandes ---
    ('E-c67 5000 sentencias', 'x = 1;\n' * 5000, 'OK', ''),
    ('E-c68 300 paréntesis anidados', 'x = ' + '(' * 300 + '1' + ')' * 300 + ';', 'OK', ''),
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
    # (Emiliano) Archivo UTF-8 con BOM: debe analizarse como si no lo tuviera.
    with tempfile.TemporaryDirectory(dir=RAIZ) as tmp:
        ruta_bom = os.path.join(tmp, 'bom.txt')
        with open(ruta_bom, 'wb') as f:
            f.write(b'\xef\xbb\xbfdelay(1);')
        r = subprocess.run([sys.executable, 'compilador.py', ruta_bom], cwd=RAIZ,
                           capture_output=True, timeout=10)
        primera = r.stdout.decode('utf-8', errors='replace').splitlines()
        if (primera[0] if primera else '') != 'OK':
            fallos += 1
            print(f"  [FALLA] archivo con BOM: esperado=OK | obtenido={primera!r}")
    total = len(pares) + 3
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
