#!/usr/bin/env python3
"""Verificación léxica de tokens.txt contra todos los grupos de casos.

Grupos: casos/ (9 casos públicos de la cátedra) y pruebas-grupo/ (suite propia,
generada con herramientas/generar_pruebas.py). Cada carpeta con un esperado.csv
en la raíz del proyecto se evalúa con el mismo criterio.

Implementa el algoritmo de la sección 8.1 del enunciado:

  1. si es un salto de línea, se descarta;
  2. si no, se prueban los patrones de @ignorar en el orden escrito: el primero
     que reconoce al menos un carácter descarta lo reconocido;
  3. si ninguno lo hizo, se prueban los patrones de los tokens: gana el que
     reconoce la cadena más larga y, ante un empate, el que está escrito primero;
  4. si ningún patrón reconoce al menos un carácter, es un error léxico.

Los saltos de línea que caen dentro de un comentario descartado también cuentan
para el número de línea (lo exige esperado.csv: lexico-02 falla en la línea 5
después de un comentario que ocupa las líneas 1 y 2).

Alcance: solo la fase léxica. Los casos OK y ERROR SINTACTICO deben lexear sin
error; la sintaxis se verifica con gramatica.txt, que específica aparte.

Uso:  python herramientas/verificar_lexico.py
"""

import csv
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_TOKENS = RAIZ / "tokens.txt"

# Casos mínimos que fijan las decisiones de diseño de tokens.txt
# (desempates por longitud, orden de escritura, comentarios, errores).
MICRO_PRUEBAS = [
    # palabra reservada empatada con identificador -> gana la palabra
    ("loop", ["LOOP"]),
    ("loopx", ["IDENTIFICADOR"]),
    ("map", ["MAP"]),
    ("mapa", ["IDENTIFICADOR"]),
    ("true", ["TRUE"]),
    ("truex", ["IDENTIFICADOR"]),
    ("float", ["FLOAT"]),
    ("float1", ["IDENTIFICADOR"]),
    ("HIGH", ["HIGH"]),
    ("INPUT", ["INPUT"]),
    # prefijo: INPUT empataría con INPUT_PULLUP solo por longitud
    ("INPUT_PULLUP", ["INPUT_PULLUP"]),
    # Serial.println sin espacios alrededor del punto
    ("Serial.println", ["SERIAL_PRINTLN"]),
    ("Serial . println", ("ERROR_LX", 1)),
    # números: gana el más largo (DECIMAL) sobre ENTERO
    ("420.46", ["DECIMAL"]),
    ("0.5", ["DECIMAL"]),
    ("420", ["ENTERO"]),
    # cadenas: ambos delimitadores, comilla simple dentro de doble
    ('"hola"', ["CADENA"]),
    ("'a'", ["CADENA"]),
    ('""', ["CADENA"]),
    ('"it\'s"', ["CADENA"]),
    # operadores compuestos: gana la cadena más larga
    ("+=", ["SUMA_IGUAL"]),
    ("-=", ["RESTA_IGUAL"]),
    ("+ +", ["SUMA", "SUMA"]),
    ("=", ["IGUAL"]),
    # // no es comentario de este lenguaje
    ("//", ["DIVISION", "DIVISION"]),
    # comentario de bloque se descarta entero
    ("/* c */", []),
    ("x=1", ["IDENTIFICADOR", "IGUAL", "ENTERO"]),
    # comentarios multilínea: los saltos de línea adentro cuentan
    ("/* x\ny */ @", ("ERROR_LX", 2)),
    ("a\n@", ("ERROR_LX", 2)),
    # caracteres que no forman ningún token
    ("@x", ("ERROR_LX", 1)),
    ("€", ("ERROR_LX", 1)),
    ("\\", ("ERROR_LX", 1)),
    # comentario sin cerrar: no es comentario -> // como DIVISION, después
    # el contenido lexea; el enunciado (F) acepta error léxico o sintáctico
    ("/* abierto", ["DIVISION", "MULTIPLICACION", "IDENTIFICADOR"]),
]


def compilar(nombre, patron, linea):
    try:
        return re.compile(patron)
    except re.error as exc:
        raise SystemExit(f"tokens.txt:{linea}: regex inválida para {nombre}: {exc}")


def cargar_especificacion(ruta):
    """Devuelve (directivas_ignorar, tokens) con los patrones ya compilados,
    en el orden del archivo (el orden importa en el desempate)."""
    ignorar = []
    tokens = []
    for num, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        texto = linea.strip()
        if not texto or texto.startswith("#"):
            continue
        partes = texto.split(None, 1)
        nombre = partes[0]
        if len(partes) < 2:
            raise SystemExit(f"tokens.txt:{num}: falta el patrón de {nombre}")
        patron = partes[1].rstrip()
        if nombre == "@ignorar":
            ignorar.append(compilar(nombre, patron, num))
        else:
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", nombre):
                raise SystemExit(
                    f"tokens.txt:{num}: nombre de token inválido: {nombre!r} "
                    "(debe empezar con mayúscula y seguir con mayúsculas, dígitos o _)"
                )
            tokens.append((nombre, compilar(nombre, patron, num)))
    if not tokens:
        raise SystemExit("tokens.txt: no se encontró ningún token")
    return ignorar, tokens


def lexear(texto, ignorar, tokens):
    """Recorre el texto con el algoritmo de la sección 8.1.

    Devuelve (lexemas, error): lexemas es [(NOMBRE, lexema), ...] y error es
    None, o (linea, detalle) en el primer carácter que no forma ningún token."""
    linea = 1
    pos = 0
    largo = len(texto)
    lexemas = []
    while pos < largo:
        caracter = texto[pos]
        if caracter == "\n":                      # paso 1
            linea += 1
            pos += 1
            continue
        descarto = False
        for patron in ignorar:                    # paso 2, en orden escrito
            match = patron.match(texto, pos)
            if match is not None and match.end() > pos:
                linea += texto.count("\n", pos, match.end())
                pos = match.end()
                descarto = True
                break
        if descarto:
            continue
        fin, ganador = pos, None                  # paso 3: más largo, luego el primero
        for nombre, patron in tokens:
            match = patron.match(texto, pos)
            if match is not None and match.end() > fin:
                fin, ganador = match.end(), nombre
        if ganador is None:                       # paso 4: error léxico
            return lexemas, (linea, f"carácter {caracter!r} (U+{ord(caracter):04X})")
        lexemas.append((ganador, texto[pos:fin]))
        pos = fin
    return lexemas, None


def probar_micro(ignorar, tokens):
    fallos = 0
    for entrada, esperado in MICRO_PRUEBAS:
        lexemas, error = lexear(entrada, ignorar, tokens)
        if isinstance(esperado, tuple):           # se esperaba error léxico
            ok = error is not None and error[0] == esperado[1]
            obtenido = f"error línea {error[0]}" if error else "sin error"
        else:                                     # se esperaba ese flujo de tokens
            ok = error is None and [n for n, _ in lexemas] == esperado
            obtenido = (
                f"error línea {error[0]} ({error[1]})"
                if error
                else " ".join(n for n, _ in lexemas) or "(vacío)"
            )
        if not ok:
            fallos += 1
            print(
                f"  FALLO micro: entrada {entrada!r} -> {obtenido}; "
                f"esperado {'error ' + str(esperado[1]) if isinstance(esperado, tuple) else ' '.join(esperado)}"
            )
    return fallos


def probar_cobertura(ignorar, tokens):
    """Todos los tokens de tokens.txt deben aparecer en al menos un caso OK.

    Si algún token nunca se usa en un programa válido, la suite no está cubriendo
    ese patrón y un cambio futuro en tokens.txt pasaría inadvertido."""
    vistos = set()
    for ruta_csv in sorted(RAIZ.glob("*/esperado.csv")):
        with ruta_csv.open(encoding="utf-8-sig", newline="") as archivo:
            for fila in csv.DictReader(archivo):
                if fila["esperado"].strip() != "OK":
                    continue
                ruta = ruta_csv.parent / fila["archivo"].strip()
                with ruta.open(encoding="utf-8", newline="") as caso:
                    lexemas, error = lexear(caso.read(), ignorar, tokens)
                if error is None:
                    vistos.update(nombre for nombre, _ in lexemas)
    faltan = [nombre for nombre, _ in tokens if nombre not in vistos]
    if faltan:
        print(f"  FALLO cobertura: ningún caso OK usa: {', '.join(faltan)}")
    else:
        print(f"  {len(tokens)}/{len(tokens)} tokens usados en al menos un caso OK")
    return len(faltan)


def main():
    if not RUTA_TOKENS.exists():
        raise SystemExit(f"No existe {RUTA_TOKENS}")
    ignorar, tokens = cargar_especificacion(RUTA_TOKENS)
    print(f"tokens.txt: {len(tokens)} tokens, {len(ignorar)} directivas @ignorar")

    print("\n-- Pruebas internas (desempates y decisiones de diseño) --")
    fallos_micro = probar_micro(ignorar, tokens)
    total_micro = len(MICRO_PRUEBAS)
    print(f"  {total_micro - fallos_micro}/{total_micro} correctas")

    print("\n-- Cobertura de tokens --")
    fallos_cobertura = probar_cobertura(ignorar, tokens)

    grupos = sorted(RAIZ.glob("*/esperado.csv"))
    if not grupos:
        raise SystemExit("No se encontró ningún */esperado.csv")
    fallos = fallos_micro + fallos_cobertura
    for ruta_csv in grupos:
        print(f"\n-- Casos de {ruta_csv.parent.name}: solo fase léxica --")
        print(f"  {'archivo':<38} {'esperado':<22} {'léxico':<26} veredicto")
        with ruta_csv.open(encoding="utf-8-sig", newline="") as archivo:
            for fila in csv.DictReader(archivo):
                nombre = fila["archivo"].strip()
                esperado = fila["esperado"].strip()
                linea_esperada = fila["linea"].strip()
                ruta = ruta_csv.parent / nombre
                if not ruta.exists():
                    raise SystemExit(f"{ruta_csv}: falta el archivo {nombre}")
                # newline="" para leer los finales de línea tal cual están (CRLF)
                with ruta.open(encoding="utf-8", newline="") as caso:
                    texto = caso.read()
                _, error = lexear(texto, ignorar, tokens)

                if esperado == "ERROR LEXICO":
                    # el caso exige error léxico en una línea concreta
                    correcto = error is not None and str(error[0]) == linea_esperada
                    visto = f"error línea {error[0]}" if error else "sin error"
                    if error and not correcto:
                        visto += f" ({error[1]})"
                else:
                    # OK y ERROR SINTACTICO: la fase léxica debe pasar sin errores
                    correcto = error is None
                    visto = "sin error" if error is None else f"error línea {error[0]} ({error[1]})"

                veredicto = "OK" if correcto else "FALLO"
                fallos += 0 if correcto else 1
                print(f"  {nombre:<38} {esperado + (' ' + linea_esperada if linea_esperada else ''):<22} {visto:<26} {veredicto}")

    print(f"\nResultado: {'TODO CORRECTO' if fallos == 0 else str(fallos) + ' FALLO(S)'}")
    if fallos:
        print("Nota: los casos ERROR SINTACTICO se validan con gramatica.txt, no acá.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
