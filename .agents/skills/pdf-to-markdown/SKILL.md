---
name: pdf-to-markdown
description: Convert local PDF documents to Markdown (.md) using Microsoft MarkItDown across individual files or folders, with support for directory exclusions.
---

# PDF to Markdown Converter Tool

Use this skill when asked to extract text, tables, or convert `.pdf` documents into clean `.md` Markdown files in local workspace folders.

## Command Line Interface

The Python script is located at `tools/pdf_to_md.py`.

### Basic Usage

Convert all PDFs in a folder (automatically excluding `Contenido complementario` by default):
```bash
python tools/pdf_to_md.py "path/to/folder"
```

Convert a single PDF file:
```bash
python tools/pdf_to_md.py "path/to/file.pdf"
```

### JSON Mode (Recommended for AI Agents)

Pass `--json` to receive structured machine-readable results:
```bash
python tools/pdf_to_md.py "path/to/folder" --json
```

Output format:
```json
{
  "success": true,
  "total": 2,
  "converted": 2,
  "skipped": 0,
  "failed": 0,
  "results": [
    {
      "input": "...",
      "output": "...",
      "status": "converted",
      "bytes": 5432
    }
  ]
}
```

### Options

- `--exclude-dir <dir1> <dir2>`: Exclude specific subdirectories by name (default: `Contenido complementario`).
- `--overwrite`: Force re-conversion even if `.md` already exists.
- `--no-recursive`: Scan only top-level files in the specified directory.
- `--json`: Output detailed progress and summary in JSON.
