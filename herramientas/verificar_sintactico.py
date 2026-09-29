#!/usr/bin/env python3
"""Verificación sintáctica de gramatica.txt y tokens.txt contra todos los casos.

Lee tokens.txt y gramatica.txt directamente, construye las reglas y analiza
todos los archivos en casos/ y pruebas-grupo/ evaluando:
  - Casos OK -> Léxico OK y Sintáctico OK.
  - Casos ERROR LEXICO -> Detecta error léxico en la línea esperada.
  - Casos ERROR SINTACTICO -> Léxico OK y error sintáctico en la línea esperada.

Uso: python herramientas/verificar_sintactico.py
"""

import csv
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_TOKENS = RAIZ / "tokens.txt"
RUTA_GRAMATICA = RAIZ / "gramatica.txt"


def compilar(nombre, patron, linea):
    try:
        return re.compile(patron)
    except re.error as exc:
        raise SystemExit(f"tokens.txt:{linea}: regex inválida para {nombre}: {exc}")


def cargar_tokens(ruta):
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
                raise SystemExit(f"tokens.txt:{num}: nombre de token inválido: {nombre!r}")
            tokens.append((nombre, compilar(nombre, patron, num)))
    return ignorar, tokens


def cargar_gramatica(ruta, tokens_validos):
    """Carga gramatica.txt y valida que cumpla las restricciones de la sección 8.2."""
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    reglas = {}  # no_terminal -> list of list of symbols
    orden_no_terminales = []
    linea_acumulada = ""
    linea_inicio = 0

    for num, linea in enumerate(lineas, 1):
        texto = linea.strip()
        if not texto or texto.startswith("#"):
            continue
        if not linea_acumulada:
            linea_inicio = num
            linea_acumulada = texto
        else:
            linea_acumulada += " " + texto

        if linea_acumulada.endswith("|"):
            continue

        partes = linea_acumulada.split("->", 1)
        if len(partes) != 2:
            raise SystemExit(f"gramatica.txt:{linea_inicio}: formato inválido (se esperaba 'no_terminal -> ...'): {linea_acumulada}")

        lhs = partes[0].strip()
        if not lhs or " " in lhs:
            raise SystemExit(f"gramatica.txt:{linea_inicio}: no terminal izquierdo inválido: {lhs!r}")

        if lhs not in reglas:
            reglas[lhs] = []
            orden_no_terminales.append(lhs)

        alternativas_str = partes[1].split("|")
        for alt_str in alternativas_str:
            simbolos = alt_str.strip().split()
            if not simbolos:
                raise SystemExit(f"gramatica.txt:{linea_inicio}: no se admiten alternativas vacías en {lhs}")
            reglas[lhs].append(simbolos)

        linea_acumulada = ""

    if linea_acumulada.endswith("|"):
        raise SystemExit("gramatica.txt: el archivo termina con '|' sin alternativa siguiente")

    if not orden_no_terminales:
        raise SystemExit("gramatica.txt: no se encontraron reglas")

    simbolo_inicial = orden_no_terminales[0]

    # Validar que todos los símbolos en el lado derecho sean no terminales o tokens de tokens.txt
    nombres_tokens = {nombre for nombre, _ in tokens_validos}
    for lhs, alts in reglas.items():
        for alt in alts:
            for sym in alt:
                if sym not in reglas and sym not in nombres_tokens:
                    raise SystemExit(f"gramatica.txt: símbolo desconocido {sym!r} en regla de {lhs}")

    return simbolo_inicial, reglas


def lexear(texto, ignorar, tokens):
    linea = 1
    pos = 0
    largo = len(texto)
    lexemas = []
    while pos < largo:
        caracter = texto[pos]
        if caracter == "\n":
            linea += 1
            pos += 1
            continue
        descarto = False
        for patron in ignorar:
            match = patron.match(texto, pos)
            if match is not None and match.end() > pos:
                linea += texto.count("\n", pos, match.end())
                pos = match.end()
                descarto = True
                break
        if descarto:
            continue
        fin, ganador = pos, None
        for nombre, patron in tokens:
            match = patron.match(texto, pos)
            if match is not None and match.end() > fin:
                fin, ganador = match.end(), nombre
        if ganador is None:
            return lexemas, (linea, f"carácter {caracter!r} (U+{ord(caracter):04X})")
        lexemas.append((ganador, texto[pos:fin], linea))
        pos = fin
    return lexemas, None


class ParserEarley:
    """Implementación de analizador sintáctico Earley para CFG arbitrarias."""
    def __init__(self, start_sym, rules):
        self.start_sym = start_sym
        self.rules = rules

    def parse(self, tokens_stream):
        """tokens_stream: list of (token_name, lexeme, line)
        Devuelve (es_valido, error_linea, token_error)
        """
        n = len(tokens_stream)
        if n == 0:
            return False, 1, "EOF"

        # Item format: (lhs, tuple(rhs), dot_index, origin_index)
        chart = [set() for _ in range(n + 1)]

        # Augment grammar with start item
        for alt in self.rules[self.start_sym]:
            chart[0].add((self.start_sym, tuple(alt), 0, 0))

        def expand_chart(k):
            added = True
            current_set = chart[k]
            while added:
                added = False
                new_items = []
                for item in list(current_set):
                    lhs, rhs, dot, origin = item
                    if dot < len(rhs):
                        next_sym = rhs[dot]
                        if next_sym in self.rules:  # Non-terminal -> Predict
                            for alt in self.rules[next_sym]:
                                new_item = (next_sym, tuple(alt), 0, k)
                                if new_item not in current_set:
                                    current_set.add(new_item)
                                    added = True
                    else:  # Complete
                        for p_lhs, p_rhs, p_dot, p_origin in list(chart[origin]):
                            if p_dot < len(p_rhs) and p_rhs[p_dot] == lhs:
                                new_item = (p_lhs, p_rhs, p_dot + 1, p_origin)
                                if new_item not in current_set:
                                    current_set.add(new_item)
                                    added = True

        expand_chart(0)

        for i, (tok_name, tok_val, tok_line) in enumerate(tokens_stream):
            next_set = chart[i + 1]
            for lhs, rhs, dot, origin in chart[i]:
                if dot < len(rhs) and rhs[dot] == tok_name:
                    next_set.add((lhs, rhs, dot + 1, origin))

            expand_chart(i + 1)

            # Si el conjunto queda vacío, no se pudo avanzar con este token
            if not chart[i + 1]:
                return False, tok_line, tok_name

        # Verificar si se completó el símbolo inicial en chart[n] originando en 0
        for lhs, rhs, dot, origin in chart[n]:
            if lhs == self.start_sym and dot == len(rhs) and origin == 0:
                return True, None, None

        # Si llegó al final sin completar, error al EOF -> línea del último token
        ultimo_token_linea = tokens_stream[-1][2]
        return False, ultimo_token_linea, "EOF"


def main():
    if not RUTA_TOKENS.exists():
        raise SystemExit(f"No existe {RUTA_TOKENS}")
    if not RUTA_GRAMATICA.exists():
        raise SystemExit(f"No existe {RUTA_GRAMATICA}")

    ignorar, tokens = cargar_tokens(RUTA_TOKENS)
    start_sym, reglas = cargar_gramatica(RUTA_GRAMATICA, tokens)
    parser = ParserEarley(start_sym, reglas)

    print(f"tokens.txt: {len(tokens)} tokens, {len(ignorar)} directivas @ignorar")
    print(f"gramatica.txt: {len(reglas)} no terminales, símbolo inicial: {start_sym}")

    grupos = sorted(RAIZ.glob("*/esperado.csv"))
    if not grupos:
        raise SystemExit("No se encontró ningún */esperado.csv")

    total_fallos = 0
    for ruta_csv in grupos:
        print(f"\n-- Verificando {ruta_csv.parent.name} (Léxico + Sintáctico) --")
        print(f"  {'archivo':<38} {'esperado':<22} {'obtenido':<26} veredicto")
        with ruta_csv.open(encoding="utf-8-sig", newline="") as archivo:
            for fila in csv.DictReader(archivo):
                nombre = fila["archivo"].strip()
                esperado = fila["esperado"].strip()
                linea_esperada = fila["linea"].strip()
                ruta = ruta_csv.parent / nombre
                if not ruta.exists():
                    raise SystemExit(f"{ruta_csv}: falta el archivo {nombre}")

                with ruta.open(encoding="utf-8", newline="") as caso:
                    texto = caso.read()

                lexemas, error_lex = lexear(texto, ignorar, tokens)

                if error_lex:
                    tipo_obtenido = "ERROR LEXICO"
                    linea_obtenida = str(error_lex[0])
                else:
                    es_valido, linea_sin, _ = parser.parse(lexemas)
                    if es_valido:
                        tipo_obtenido = "OK"
                        linea_obtenida = ""
                    else:
                        tipo_obtenido = "ERROR SINTACTICO"
                        linea_obtenida = str(linea_sin)

                if esperado == "OK":
                    correcto = tipo_obtenido == "OK"
                else:
                    # Debe coincidir el tipo y la línea
                    correcto = tipo_obtenido == esperado and (not linea_esperada or linea_obtenida == linea_esperada)

                visto = f"{tipo_obtenido} {linea_obtenida}".strip()
                esp = f"{esperado} {linea_esperada}".strip()
                veredicto = "OK" if correcto else "FALLO"
                if not correcto:
                    total_fallos += 1
                print(f"  {nombre:<38} {esp:<22} {visto:<26} {veredicto}")

    print(f"\nResultado final: {'TODO CORRECTO (100% OK)' if total_fallos == 0 else str(total_fallos) + ' FALLOS'}")
    return 1 if total_fallos else 0


if __name__ == "__main__":
    sys.exit(main())
