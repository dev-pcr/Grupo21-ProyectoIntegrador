#!/usr/bin/env python3
"""Generador y Renderizador de Diagramas Mermaid a SVG/PNG.

Herramienta autónoma sin dependencias externas obligatorias (usa Python 3 estándar).
Permite:
  1. Renderizar código Mermaid directo o desde archivo a SVG o PNG.
  2. Extraer bloques ```mermaid de archivos Markdown y exportarlos a SVG/PNG en img/.
  3. Validar sintaxis común y buenas prácticas (comillas en caracteres especiales).
  4. Generar plantillas y ejemplos para cualquier tipo de diagrama.

Uso rápido:
  python tools/mermaid_generator.py --text "flowchart TD; A-->B" -o img/demo.svg
  python tools/mermaid_generator.py -i diagrama.mmd -o img/diagrama.svg --theme dark
  python tools/mermaid_generator.py --extract README.md --output-dir img/
  python tools/mermaid_generator.py --example sequence
"""

import argparse
import base64
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TEMPLATES = {
    "flowchart": """flowchart TD
    %% Estilos y formas de nodos
    inicio(["Inicio"]) --> decision{"¿Es válido?"}
    decision -->|Sí| proceso["Procesar datos (normal)"]
    decision -->|No| error["Registrar error"]
    proceso --> subproceso[["Subrutina externa"]]
    subproceso --> db[("Base de Datos")]
    error --> fin(["Fin"])
    db --> fin

    %% Subgrafos
    subgraph Gestion ["Gestión de Estado"]
        db
    end

    %% Clases y colores
    style inicio fill:#d4edda,stroke:#28a745,stroke-width:2px
    style fin fill:#d4edda,stroke:#28a745,stroke-width:2px
    style error fill:#f8d7da,stroke:#dc3545,stroke-width:2px
""",
    "sequence": """sequenceDiagram
    autonumber
    actor U as Usuario
    participant C as Cliente Web
    participant S as Servidor API
    participant DB as Base de Datos

    U->>C: Solicita acción
    activate C
    C->>S: POST /api/procesar
    activate S
    S->>DB: SELECT * FROM items
    activate DB
    DB-->>S: Filas encontradas
    deactivate DB

    alt Éxito
        S-->>C: 200 OK (datos)
        C-->>U: Muestra resultado
    else Error
        S-->>C: 400 Bad Request
        C-->>U: Notifica error
    end
    deactivate S
    deactivate C
""",
    "class": """classDiagram
    class Compilador {
        -String archivoFuente
        -Lexer lexer
        -Parser parser
        +compilar() bool
        +obtenerErrores() List~String~
    }

    class Lexer {
        +List~Token~ tokens
        +escanear(String texto) List~Token~
        -reconocerToken() Token
    }

    class Parser {
        -AST ast
        +analizar(List~Token~ tokens) AST
        +reportarError(int linea, String msg)
    }

    class Token {
        +String tipo
        +String valor
        +int linea
    }

    Compilador *-- Lexer : compone
    Compilador *-- Parser : compone
    Lexer ..> Token : genera
    Parser ..> Token : consume
""",
    "state": """stateDiagram-v2
    [*] --> Inactivo

    Inactivo --> EnEjecucion : Iniciar tarea
    state EnEjecucion {
        [*] --> AnalisisLexico
        AnalisisLexico --> AnalisisSintactico : Tokens OK
        AnalisisSintactico --> GeneracionCodigo : Sintaxis OK
    }

    EnEjecucion --> Pausado : Pausar
    Pausado --> EnEjecucion : Reanudar
    EnEjecucion --> ConError : Error detectado
    EnEjecucion --> Completado : Éxito total

    ConError --> Inactivo : Reintentar
    Completado --> [*]
""",
    "er": """erDiagram
    ESTUDIANTE ||--o{ ENTREGA : realiza
    GRUPO ||--|{ ESTUDIANTE : contiene
    GRUPO ||--o{ ENTREGA : entrega
    ENTREGA ||--|{ CASO_PRUEBA : valida

    GRUPO {
        int id_grupo PK
        string tema
        int semilla
    }
    ESTUDIANTE {
        int id_estudiante PK
        string nombre
        string apellido
    }
    ENTREGA {
        int id_entrega PK
        int numero_incremento
        date fecha_entrega
        string calificacion
    }
    CASO_PRUEBA {
        int id_caso PK
        string nombre_archivo
        string resultado_esperado
        int linea_error
    }
""",
    "gantt": """gantt
    title Cronograma de Desarrollo - Incremento 2
    dateFormat  YYYY-MM-DD
    section Lectura y Setup
    Lectura de especificación   :done, 2026-10-18, 1d
    Setup de entorno (PLY 3.11) :done, 2026-10-19, 1d
    section Desarrollo Paralelo
    Léxico - lexico.py (Emiliano) :active, 2026-10-20, 2d
    Sintáctico - sintactico.py (Pablo) :active, 2026-10-20, 2d
    Integración compilador.py   :2026-10-21, 1d
    section Testing Cruzado
    Testing cruzado con IA      :2026-10-22, 2d
    Casos de prueba propios     :2026-10-23, 1d
    Validación en Linux         :2026-10-24, 1d
    section Contingencia
    Redacción informe.txt       :2026-10-25, 1d
    Empaquetado Grupo-21.zip    :2026-10-26, 1d
    Entrega final               :crit, 2026-10-27, 1d
""",
    "gitGraph": """gitGraph
    commit id: "Init repo"
    commit id: "tokens.txt"
    commit id: "gramatica.txt"
    branch feature-lexico
    checkout feature-lexico
    commit id: "ply.lex base"
    commit id: "manejo lineno"
    checkout main
    branch feature-sintactico
    checkout feature-sintactico
    commit id: "ply.yacc base"
    commit id: "precedencias"
    checkout main
    merge feature-lexico id: "Merge Lexer"
    merge feature-sintactico id: "Merge Parser"
    commit id: "compilador.py CLI" tag: "v2.0"
""",
    "pie": """pie title Distribución de Casos de Prueba (Grupo 21)
    "Casos Válidos (OK)" : 53
    "Errores Léxicos" : 56
    "Errores Sintácticos" : 99
""",
    "mindmap": """mindmap
  root((Compilador Arduino))
    Fase Léxica
      Tokens
      Palabras Reservadas
      Comentarios /* */
      Manejo lineno
    Fase Sintáctica
      Gramática LL/LR
      Precedencias
      Recuperación EOF
    Entrega
      compilador.py
      informe.txt
      pruebas/
""",
    "timeline": """timeline
    title Hitos del Proyecto
    2026-09-29 : Asignación de Tema : Entrega de Anexo
    2026-10-10 : Entrega 1 : tokens.txt y gramatica.txt aprobados
    2026-10-18 : Inicio Incremento 2 : PLY 3.11
    2026-10-27 : Entrega 2 Definitiva : Compilador final
""",
}


def validar_sintaxis(codigo: str) -> list[str]:
    """Realiza validaciones preliminares de sintaxis y buenas prácticas Mermaid."""
    advertencias = []
    lineas = codigo.splitlines()

    # Comprobar que no esté vacío
    lineas_con_contenido = [l.strip() for l in lineas if l.strip() and not l.strip().startswith("%%")]
    if not lineas_con_contenido:
        return ["El código Mermaid está vacío."]

    primer_comando = lineas_con_contenido[0].split()[0]
    tipos_validos = (
        "flowchart", "graph", "sequenceDiagram", "classDiagram",
        "stateDiagram", "stateDiagram-v2", "erDiagram", "gantt",
        "gitGraph", "pie", "mindmap", "timeline", "C4Context",
        "journey", "quadrantChart", "architecture"
    )
    if not any(primer_comando.startswith(t) for t in tipos_validos):
        advertencias.append(
            f"La primera línea '{lineas_con_contenido[0]}' no parece iniciar un diagrama Mermaid reconocido."
        )

    # Detectar paréntesis o corchetes sin comillas dentro de formas de nodo [ ... ( ... ) ... ]
    for num, linea in enumerate(lineas, 1):
        # Detectar patrón id[Texto con (paréntesis) sin comillas]
        match = re.search(r'([A-Za-z0-9_]+)\[([^"\]]*\([^\)]*\)[^"\]]*)\]', linea)
        if match:
            nodo = match.group(1)
            advertencias.append(
                f"Línea {num}: El nodo '{nodo}' contiene paréntesis dentro de corchetes sin entrecomillar. "
                f'Usa formato con comillas dobles: {nodo}["{match.group(2)}"]'
            )

        # Detectar etiquetas HTML peligrosas
        if re.search(r"<[^>]+>", linea) and not re.search(r"<br\s*/?>", linea, re.IGNORECASE):
            advertencias.append(
                f"Línea {num}: Se detectaron etiquetas HTML. Usa texto plano o <br/> para saltos."
            )

    return advertencias


def renderizar_mermaid(codigo: str, formato: str = "svg", tema: str = "default") -> bytes:
    """Renderiza código Mermaid a SVG o PNG utilizando la API Mermaid.ink."""
    formato = formato.lower().strip()
    if formato not in ("svg", "png"):
        raise ValueError(f"Formato '{formato}' no soportado. Usa 'svg' o 'png'.")

    # Estructurar JSON con el código y tema
    payload = {
        "code": codigo,
        "mermaid": {"theme": tema if tema else "default"}
    }
    json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    b64 = base64.urlsafe_b64encode(json_bytes).decode("ascii")

    subpath = "img" if formato == "png" else "svg"
    url = f"https://mermaid.ink/{subpath}/pako:{b64}"
    # Si la url con pako o json directo
    # mermaid.ink soporta base64 urlsafe directo de json:
    url = f"https://mermaid.ink/{subpath}/{b64}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) mermaid-generator/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status != 200:
                raise RuntimeError(f"El servicio mermaid.ink respondió con código HTTP {res.status}")
            return res.read()
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Error de sintaxis o renderizado Mermaid (HTTP {exc.code}): {detalle}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Error de conexión al renderizar Mermaid: {exc.reason}")


def extraer_de_markdown(ruta_md: Path, salida_dir: Path, formato: str = "svg", tema: str = "default") -> list[Path]:
    """Extrae todos los bloques ```mermaid de un archivo Markdown y los guarda como imágenes."""
    contenido = ruta_md.read_text(encoding="utf-8")
    patron = re.compile(r"```mermaid[ \t]*\r?\n([\s\S]*?)```", re.MULTILINE)
    coincidencias = patron.findall(contenido)

    if not coincidencias:
        print(f"No se encontraron bloques ```mermaid en '{ruta_md}'.")
        return []

    salida_dir.mkdir(parents=True, exist_ok=True)
    generados = []
    base_nombre = ruta_md.stem.lower().replace(" ", "-")

    for idx, codigo in enumerate(coincidencias, 1):
        nombre_archivo = f"{base_nombre}-diagrama-{idx}.{formato}"
        destino = salida_dir / nombre_archivo
        print(f"Renderizando diagrama {idx}/{len(coincidencias)} -> {destino}...")
        datos = renderizar_mermaid(codigo.strip(), formato=formato, tema=tema)
        destino.write_bytes(datos)
        generados.append(destino)

    return generados


def main():
    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Generador y conversor de diagramas Mermaid a SVG/PNG."
    )
    parser.add_argument("-i", "--input", help="Archivo de entrada con código Mermaid (.mmd / .txt)")
    parser.add_argument("-t", "--text", help="Código Mermaid en texto directo")
    parser.add_argument("-o", "--output", help="Ruta del archivo de salida (.svg o .png)")
    parser.add_argument(
        "--format", choices=["svg", "png"], default="svg",
        help="Formato de salida (por defecto svg)"
    )
    parser.add_argument(
        "--theme", choices=["default", "dark", "forest", "neutral", "base"], default="default",
        help="Tema visual de Mermaid"
    )
    parser.add_argument(
        "--extract", help="Ruta de un archivo .md del cual extraer y renderizar bloques ```mermaid"
    )
    parser.add_argument(
        "--output-dir", default="img", help="Directorio de salida para la extracción de bloques (por defecto 'img')"
    )
    parser.add_argument(
        "--validate", help="Valida sintaxis y buenas prácticas de un archivo Mermaid"
    )
    parser.add_argument(
        "--example", choices=list(TEMPLATES.keys()),
        help="Imprime una plantilla de ejemplo lista para usar y sale"
    )

    args = parser.parse_args()

    # Caso 1: Imprimir ejemplo
    if args.example:
        print(TEMPLATES[args.example])
        return 0

    # Caso 2: Validar archivo
    if args.validate:
        ruta = Path(args.validate)
        if not ruta.exists():
            print(f"Error: No existe el archivo '{ruta}'", file=sys.stderr)
            return 1
        contenido = ruta.read_text(encoding="utf-8")
        advertencias = validar_sintaxis(contenido)
        if advertencias:
            print(f"Se encontraron {len(advertencias)} observaciones en '{ruta}':")
            for adv in advertencias:
                print(f"  - {adv}")
            return 1
        else:
            print(f"Sintaxis básica y estilo OK en '{ruta}'.")
            return 0

    # Caso 3: Extraer de Markdown
    if args.extract:
        ruta_md = Path(args.extract)
        if not ruta_md.exists():
            print(f"Error: No existe el archivo '{ruta_md}'", file=sys.stderr)
            return 1
        dir_salida = Path(args.output_dir)
        archivos = extraer_de_markdown(ruta_md, dir_salida, formato=args.format, tema=args.theme)
        print(f"Completado. Se generaron {len(archivos)} diagramas en '{dir_salida}'.")
        return 0

    # Caso 4: Renderizado de texto o archivo individual
    codigo = None
    if args.input:
        if args.input == "-":
            codigo = sys.stdin.read().strip()
        else:
            ruta = Path(args.input)
            if not ruta.exists():
                print(f"Error: No existe el archivo de entrada '{ruta}'", file=sys.stderr)
                return 1
            codigo = ruta.read_text(encoding="utf-8").strip()
    elif args.text:
        if args.text == "-":
            codigo = sys.stdin.read().strip()
        else:
            codigo = args.text.strip()
    elif not sys.stdin.isatty():
        codigo = sys.stdin.read().strip()

    if not codigo:
        parser.print_help()
        return 1

    # Validar advertencias
    advs = validar_sintaxis(codigo)
    for adv in advs:
        print(f"[Aviso] {adv}", file=sys.stderr)

    # Determinar formato desde la extensión de salida si no se forzó
    formato = args.format
    if args.output:
        if args.output.lower().endswith(".png"):
            formato = "png"
        elif args.output.lower().endswith(".svg"):
            formato = "svg"

    try:
        resultado = renderizar_mermaid(codigo, formato=formato, tema=args.theme)
    except Exception as exc:
        print(f"Error al generar diagrama: {exc}", file=sys.stderr)
        return 1

    if args.output:
        ruta_out = Path(args.output)
        ruta_out.parent.mkdir(parents=True, exist_ok=True)
        ruta_out.write_bytes(resultado)
        print(f"OK: Diagrama generado en '{ruta_out}' ({len(resultado)} bytes)")
    else:
        # Enviar a stdout si no se especificó archivo
        if formato == "svg":
            sys.stdout.write(resultado.decode("utf-8", errors="replace"))
        else:
            sys.stdout.buffer.write(resultado)

    return 0


if __name__ == "__main__":
    sys.exit(main())
