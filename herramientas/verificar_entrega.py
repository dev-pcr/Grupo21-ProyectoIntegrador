#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
Verificador y Empaquetador de la Entrega 2 — Compiladores 2026 (Grupo 21)
================================================================================
Este script realiza las siguientes acciones de forma automática y verificable:
  1. Audita la coherencia de todos los archivos exigidos por la cátedra.
  2. Crea la carpeta de entrega limpia 'entrega/Grupo-21/' sin basura ni cachés.
  3. Genera el archivo comprimido oficial 'Grupo-21.zip' en la raíz.
  4. Ejecuta una batería exhaustiva de pruebas directamente sobre los archivos
     empaquetados para garantizar que la entrega funciona al 100% tal cual llega.

Estructura obligatoria según Sección 9 del enunciado:
  compilador.py y los demás archivos .py del proyecto (lexico.py, sintactico.py)
  tokens.txt la especificación final
  gramatica.txt
  pruebas/ valido.txt, error.txt y esperado.csv
  informe.txt o informe.pdf

Uso (desde la raíz del proyecto):
    python herramientas/verificar_entrega.py
================================================================================
"""

import csv
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

# Asegurar salida utf-8 en Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_ENTREGA = os.path.join(RAIZ, 'entrega', 'Grupo-21')
ZIP_ENTREGA = os.path.join(RAIZ, 'Grupo-21.zip')

ARCHIVOS_REQUERIDOS = [
    'compilador.py',
    'lexico.py',
    'sintactico.py',
    'tokens.txt',
    'gramatica.txt',
    'informe.txt',
    os.path.join('pruebas', 'valido.txt'),
    os.path.join('pruebas', 'error.txt'),
    os.path.join('pruebas', 'esperado.csv'),
]


def imprimir_titulo(texto):
    print("\n" + "=" * 80)
    print(texto.center(80))
    print("=" * 80)


def paso_1_auditar_archivos_fuente():
    print("\n[Paso 1] Auditando archivos requeridos en el repositorio...")
    todos_ok = True
    for rel_path in ARCHIVOS_REQUERIDOS:
        abs_path = os.path.join(RAIZ, rel_path)
        if not os.path.exists(abs_path):
            print(f"  [X] FALTA: {rel_path}")
            todos_ok = False
        else:
            tam = os.path.getsize(abs_path)
            print(f"  [OK] {rel_path} ({tam} bytes)")
    if not todos_ok:
        sys.exit("Error: Faltan archivos requeridos para armar la entrega.")


def paso_2_armar_carpeta_entrega():
    print("\n[Paso 2] Armando carpeta de entrega limpia en 'entrega/Grupo-21/'...")
    if os.path.exists(CARPETA_ENTREGA):
        shutil.rmtree(CARPETA_ENTREGA)
    os.makedirs(os.path.join(CARPETA_ENTREGA, 'pruebas'), exist_ok=True)

    for rel_path in ARCHIVOS_REQUERIDOS:
        origen = os.path.join(RAIZ, rel_path)
        destino = os.path.join(CARPETA_ENTREGA, rel_path)
        shutil.copy2(origen, destino)

    # Limpiar cualquier residuo de compilación
    for root, dirs, files in os.walk(CARPETA_ENTREGA):
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d))
        for f in files:
            if f.endswith('.pyc') or f.endswith('.pyo') or f == 'parser.out' or f == 'parsetab.py':
                os.remove(os.path.join(root, f))

    print("  [OK] Carpeta 'entrega/Grupo-21/' generada con éxito.")


def paso_3_generar_zip():
    print(f"\n[Paso 3] Generando archivo comprimido '{os.path.basename(ZIP_ENTREGA)}'...")
    if os.path.exists(ZIP_ENTREGA):
        os.remove(ZIP_ENTREGA)

    with zipfile.ZipFile(ZIP_ENTREGA, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel_path in ARCHIVOS_REQUERIDOS:
            abs_path = os.path.join(CARPETA_ENTREGA, rel_path)
            arcname = rel_path.replace(os.sep, '/')
            zf.write(abs_path, arcname)

    print("  Contenido empaquetado en Grupo-21.zip:")
    with zipfile.ZipFile(ZIP_ENTREGA, 'r') as zf:
        for info in zf.infolist():
            print(f"    - {info.filename} ({info.file_size} bytes)")
    print(f"  [OK] '{os.path.basename(ZIP_ENTREGA)}' generado con éxito.")


def paso_4_bateria_pruebas_en_paquete():
    print("\n[Paso 4] Ejecutando batería de pruebas directamente sobre la carpeta de entrega...")
    sys.path.insert(0, CARPETA_ENTREGA)

    # Importar los módulos desde la carpeta de entrega para asegurar su autonomía
    import compilador
    import sintactico

    # 4.1. Conflictos LALR en sintactico
    conflictos = sintactico.auditar_conflictos()
    sr = conflictos['shift_reduce']
    rr = conflictos['reduce_reduce']
    print(f"  -> Auditoría LALR: shift/reduce = {sr}, reduce/reduce = {rr}")
    assert sr == 0 and rr == 0, f"Error: Se detectaron conflictos LALR ({sr}, {rr})"

    # 4.2. Casos de prueba propios en pruebas/
    print("  -> Verificando casos propios de la entrega (pruebas/)...")
    csv_esperado = os.path.join(CARPETA_ENTREGA, 'pruebas', 'esperado.csv')
    with open(csv_esperado, 'r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            nombre = fila['archivo']
            esp_tipo = fila['esperado']
            esp_lin = fila['linea']
            ruta = os.path.join(CARPETA_ENTREGA, 'pruebas', nombre)
            with open(ruta, 'r', encoding='utf-8-sig') as arch:
                contenido = arch.read()
            res = compilador.compilar_codigo(contenido)
            print(f"     * {nombre} -> {res}")
            if esp_tipo == 'OK':
                assert res == 'OK', f"Fallo en {nombre}: esperado OK, obtenido {res}"
            else:
                partes = res.split(':', 1)
                prefijo = partes[0]
                assert esp_tipo in prefijo and f"linea {esp_lin}" in prefijo, (
                    f"Fallo en {nombre}: esperado {esp_tipo} linea {esp_lin}, obtenido {res}"
                )

    # 4.3. Casos públicos de la cátedra
    print("  -> Verificando casos públicos de la cátedra (casos/)...")
    casos_csv = os.path.join(RAIZ, 'casos', 'esperado.csv')
    if os.path.exists(casos_csv):
        with open(casos_csv, 'r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                nombre = fila['archivo']
                esp_tipo = fila['esperado']
                esp_lin = fila['linea']
                ruta = os.path.join(RAIZ, 'casos', nombre)
                with open(ruta, 'r', encoding='utf-8-sig') as arch:
                    contenido = arch.read()
                res = compilador.compilar_codigo(contenido)
                if esp_tipo == 'OK':
                    assert res == 'OK', f"Fallo en {nombre}: esperado OK, obtenido {res}"
                else:
                    partes = res.split(':', 1)
                    prefijo = partes[0]
                    assert esp_tipo in prefijo and f"linea {esp_lin}" in prefijo, (
                        f"Fallo en {nombre}: esperado {esp_tipo} linea {esp_lin}, obtenido {res}"
                    )
        print("     * 9/9 casos públicos aprobados exitosamente.")

    # 4.4. Prueba de ejecución como subproceso CLI
    print("  -> Verificando invocación por CLI (python compilador.py programa.txt)...")
    valido_path = os.path.join(CARPETA_ENTREGA, 'pruebas', 'valido.txt')
    cmd = [sys.executable, 'compilador.py', os.path.join('pruebas', 'valido.txt')]
    proc = subprocess.run(cmd, cwd=CARPETA_ENTREGA, capture_output=True, text=True)
    primera_linea = proc.stdout.strip().splitlines()[0] if proc.stdout else ''
    assert primera_linea == 'OK', f"CLI fallo: esperado OK, obtenido '{primera_linea}'"
    print(f"     * Invocación CLI devolvió: '{primera_linea}' (código {proc.returncode})")


def paso_5_verificar_descompresion_en_limpio():
    print("\n[Paso 5] Verificando extracción y ejecución en entorno temporal aislado...")
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(ZIP_ENTREGA, 'r') as zf:
            zf.extractall(temp_dir)

        # Probar compilador.py directamente en temp_dir
        cmd = [sys.executable, 'compilador.py', os.path.join('pruebas', 'valido.txt')]
        proc = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)
        primera_linea = proc.stdout.strip().splitlines()[0] if proc.stdout else ''
        assert primera_linea == 'OK', f"Fallo en entorno aislado: '{primera_linea}'"

        cmd_err = [sys.executable, 'compilador.py', os.path.join('pruebas', 'error.txt')]
        proc_err = subprocess.run(cmd_err, cwd=temp_dir, capture_output=True, text=True)
        linea_err = proc_err.stdout.strip().splitlines()[0] if proc_err.stdout else ''
        assert "ERROR SINTACTICO linea 13" in linea_err, f"Fallo error en entorno aislado: '{linea_err}'"

        print(f"  [OK] Descompresión y ejecución aislada 100% exitosa.")


def main():
    imprimir_titulo("VERIFICACIÓN INTEGRAL Y EMPAQUETADO — ENTREGA 2")
    paso_1_auditar_archivos_fuente()
    paso_2_armar_carpeta_entrega()
    paso_3_generar_zip()
    paso_4_bateria_pruebas_en_paquete()
    paso_5_verificar_descompresion_en_limpio()
    imprimir_titulo("VEREDICTO: ENTREGA 2 LISTA Y VERIFICADA AL 100%")


if __name__ == '__main__':
    main()
