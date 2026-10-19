#!/usr/bin/env python3
"""
markdown_to_pdf.py - Conversor de documentos Markdown a PDF A4 de alta fidelidad.
Soporta:
- Formato A4 con margenes configurables, fondo blanco y tipografia negra/oscura legible.
- Renderizado de formulas matematicas LaTeX ($ y $$) mediante KaTeX.
- Bloques de codigo con resaltado de sintaxis.
- Diagramas e imagenes locales (SVG, PNG, etc.) con resolucion de rutas absolutas.
- Callouts / Admonitions estilo GitHub (> [!NOTE], > [!WARNING], > [!CAUTION], > [!IMPORTANT]).
- Automatizacion via Google Chrome o Microsoft Edge en modo headless.
"""

import sys
import os
import re
import argparse
import subprocess
import tempfile
import pathlib
import urllib.parse

try:
    import markdown
except ImportError:
    print("Error: El paquete 'markdown' es requerido. Instálelo con: pip install markdown")
    sys.exit(1)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  
  <!-- KaTeX para renderizado de fórmulas matemáticas -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

  <style>
    @page {{
      size: {page_size};
      margin: {margin};
    }}

    @media print {{
      body {{
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }}
      h1, h2, h3, h4, h5, h6 {{
        page-break-after: avoid;
        break-after: avoid;
      }}
      pre, blockquote, table, figure, img, svg, .callout {{
        page-break-inside: avoid;
        break-inside: avoid;
      }}
      tr {{
        page-break-inside: avoid;
        break-inside: avoid;
      }}
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.55;
      color: #0f172a;
      background-color: #ffffff;
      margin: 0;
      padding: 0;
    }}

    h1, h2, h3, h4, h5, h6 {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.25;
      margin-top: 1.4em;
      margin-bottom: 0.5em;
    }}

    h1 {{
      font-size: 20pt;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 0.3em;
      margin-top: 0;
    }}

    h2 {{
      font-size: 15pt;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 0.25em;
      margin-top: 1.6em;
    }}

    h3 {{
      font-size: 12.5pt;
      margin-top: 1.3em;
    }}

    h4 {{
      font-size: 11pt;
    }}

    p {{
      margin: 0.6em 0;
    }}

    ul, ol {{
      margin: 0.5em 0;
      padding-left: 1.8em;
    }}

    li {{
      margin: 0.25em 0;
    }}

    hr {{
      border: 0;
      height: 1px;
      background: #cbd5e1;
      margin: 1.6em 0;
    }}

    /* Tablas */
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1em 0;
      font-size: 9.5pt;
      page-break-inside: avoid;
    }}

    th, td {{
      border: 1px solid #cbd5e1;
      padding: 6px 10px;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background-color: #f1f5f9;
      font-weight: 600;
      color: #0f172a;
    }}

    tr:nth-child(even) {{
      background-color: #f8fafc;
    }}

    /* Código */
    code {{
      font-family: "Cascadia Code", Consolas, "Courier New", monospace;
      font-size: 9pt;
      background-color: #f1f5f9;
      color: #0f172a;
      padding: 1.5px 5px;
      border-radius: 4px;
      border: 1px solid #e2e8f0;
    }}

    pre {{
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 14px;
      font-family: "Cascadia Code", Consolas, "Courier New", monospace;
      font-size: 9pt;
      line-height: 1.45;
      overflow-x: auto;
      margin: 0.8em 0;
      page-break-inside: avoid;
    }}

    pre code {{
      background: none;
      padding: 0;
      border: none;
      font-size: 9pt;
    }}

    /* Imágenes y Gráficos */
    img, svg {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 1.2em auto;
      border-radius: 6px;
    }}

    /* Callouts / Admonitions estilo GitHub */
    .callout {{
      border-left: 4px solid #3b82f6;
      background-color: #f8fafc;
      padding: 10px 14px;
      margin: 1em 0;
      border-radius: 0 6px 6px 0;
      font-size: 9.5pt;
      page-break-inside: avoid;
    }}

    .callout-title {{
      font-weight: 700;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .callout-note {{
      border-color: #2563eb;
      background-color: #eff6ff;
    }}
    .callout-note .callout-title {{ color: #1d4ed8; }}

    .callout-tip {{
      border-color: #16a34a;
      background-color: #f0fdf4;
    }}
    .callout-tip .callout-title {{ color: #15803d; }}

    .callout-important {{
      border-color: #9333ea;
      background-color: #faf5ff;
    }}
    .callout-important .callout-title {{ color: #7e22ce; }}

    .callout-warning {{
      border-color: #d97706;
      background-color: #fffbeb;
    }}
    .callout-warning .callout-title {{ color: #b45309; }}

    .callout-caution {{
      border-color: #dc2626;
      background-color: #fef2f2;
    }}
    .callout-caution .callout-title {{ color: #b91c1c; }}

    /* Fórmulas matemáticas display */
    .katex-display {{
      margin: 0.8em 0 !important;
      overflow-x: auto;
      overflow-y: hidden;
      padding: 4px 0;
    }}
  </style>

  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      if (typeof renderMathInElement !== 'undefined') {{
        renderMathInElement(document.body, {{
          delimiters: [
            {{left: '$$', right: '$$', display: true}},
            {{left: '$', right: '$', display: false}},
            {{left: '\\\\(', right: '\\\\)', display: false}},
            {{left: '\\\\[', right: '\\\\]', display: true}}
          ],
          throwOnError: false
        }});
      }}
    }});
  </script>
</head>
<body>
{content}
</body>
</html>
"""

def find_browser() -> str:
    """Busca Chrome o Edge en rutas comunes de Windows y PATH."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p

    # Búsqueda en PATH
    for prog in ["chrome", "google-chrome", "msedge", "chromium"]:
        try:
            res = subprocess.run(["where.exe" if os.name == "nt" else "which", prog],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                line = res.stdout.strip().splitlines()[0]
                if os.path.exists(line):
                    return line
        except Exception:
            pass

    raise FileNotFoundError("No se encontró ningún navegador (Chrome o Edge) para generar el PDF.")


def process_github_alerts(text: str) -> str:
    """Convierte blockquotes con [!NOTE], [!WARNING], etc. en HTML con clases de callout."""
    alert_types = {
        "NOTE": ("Nota", "callout-note"),
        "TIP": ("Consejo", "callout-tip"),
        "IMPORTANT": ("Importante", "callout-important"),
        "WARNING": ("Advertencia", "callout-warning"),
        "CAUTION": ("Atención", "callout-caution")
    }

    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        m = re.match(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", line.strip(), re.IGNORECASE)
        if m:
            atype = m.group(1).upper()
            title_text, css_class = alert_types.get(atype, ("Nota", "callout-note"))
            body_lines = []
            i += 1
            while i < n and (lines[i].startswith(">") or lines[i].strip() == ""):
                content_line = lines[i]
                if content_line.startswith(">"):
                    content_line = content_line[1:].lstrip()
                body_lines.append(content_line)
                i += 1
            
            body_md = "\n".join(body_lines).strip()
            # Convertir a bloque especial
            out.append(f'<div class="callout {css_class}">')
            out.append(f'  <div class="callout-title">{title_text}</div>')
            out.append(f'  <div class="callout-body">\n{body_md}\n  </div>')
            out.append('</div>')
            continue
        else:
            out.append(line)
            i += 1

    return "\n".join(out)


def resolve_image_paths(html_content: str, base_dir: str) -> str:
    """Transforma rutas relativas de imágenes en file:/// URLs absolutas."""
    def repl(match):
        src = match.group(1)
        if src.startswith("http://") or src.startswith("https://") or src.startswith("data:") or src.startswith("file:"):
            return match.group(0)
        
        abs_path = os.path.abspath(os.path.join(base_dir, urllib.parse.unquote(src)))
        if os.path.exists(abs_path):
            file_url = pathlib.Path(abs_path).as_uri()
            return f'src="{file_url}"'
        return match.group(0)

    return re.sub(r'src=["\']([^"\']+)["\']', repl, html_content)


def convert_markdown_to_pdf(input_md: str, output_pdf: str, page_size: str = "A4", margin: str = "18mm 16mm 18mm 16mm") -> None:
    """Convierte archivo Markdown a PDF A4 usando Chrome headless."""
    input_path = os.path.abspath(input_md)
    output_path = os.path.abspath(output_pdf)
    base_dir = os.path.dirname(input_path)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Archivo de entrada no encontrado: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Título del documento
    title_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(input_path)

    # Pre-procesar callouts
    preprocessed_md = process_github_alerts(md_text)

    # Extensiones de Markdown
    extensions = [
        "extra",
        "tables",
        "fenced_code",
        "codehilite",
        "toc",
        "sane_lists"
    ]
    
    html_body = markdown.markdown(
        preprocessed_md,
        extensions=extensions,
        extension_configs={
            "codehilite": {
                "guess_lang": False,
                "noclasses": True,
                "pygments_style": "default"
            }
        }
    )

    # Resolver rutas de imágenes y gráficos vectoriales SVG
    html_body = resolve_image_paths(html_body, base_dir)

    # Armar HTML completo
    full_html = HTML_TEMPLATE.format(
        title=title,
        page_size=page_size,
        margin=margin,
        content=html_body
    )

    # Guardar en archivo temporal en el mismo directorio base para respetar rutas relativas
    temp_html_path = os.path.join(base_dir, f"_temp_print_{os.path.basename(input_path)}.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    browser_bin = find_browser()
    temp_html_uri = pathlib.Path(temp_html_path).as_uri()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        browser_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=6000",
        f"--print-to-pdf={output_path}",
        temp_html_uri
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError(f"Fallo al generar el PDF: {res.stderr or res.stdout}")
        print(f"PDF generado con éxito ({os.path.getsize(output_path)} bytes) en: {output_path}")
    finally:
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser(description="Conversor de Markdown a PDF A4 con fórmulas KaTeX y gráficos SVG")
    parser.add_argument("--input", "-i", required=True, help="Ruta al archivo Markdown de entrada")
    parser.add_argument("--output", "-o", required=True, help="Ruta de salida del PDF generado")
    parser.add_argument("--page-size", default="A4", help="Tamaño de página (default: A4)")
    parser.add_argument("--margin", default="18mm 16mm 18mm 16mm", help="Márgenes CSS (default: 18mm 16mm 18mm 16mm)")

    args = parser.parse_args()
    convert_markdown_to_pdf(args.input, args.output, page_size=args.page_size, margin=args.margin)


if __name__ == "__main__":
    main()
