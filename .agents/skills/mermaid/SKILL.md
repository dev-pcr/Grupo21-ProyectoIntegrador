---
name: mermaid
description: >-
  Escribe, valida, diseña y renderiza diagramas en sintaxis Mermaid (flowcharts, sequence,
  class, state, ER, gantt, gitGraph, pie, mindmaps, timelines). Usa esta skill cuando el usuario
  pida crear diagramas Mermaid en Markdown, necesite exportar o renderizar diagramas Mermaid a
  SVG/PNG usando tools/mermaid_generator.py, o cuando se requiera validar y corregir sintaxis
  de diagramas Mermaid existentes.
---

# Mermaid Diagram Skill

Guía completa para diseñar, redactar, validar y renderizar diagramas utilizando la sintaxis estándar de **Mermaid.js**, junto con la herramienta de automatización `tools/mermaid_generator.py` para exportar a **SVG** o **PNG**.

---

## 1. Herramienta de Soporte: `tools/mermaid_generator.py`

El proyecto incluye un script autónomo en Python estándar (sin dependencias adicionales obligatorias) para procesar diagramas Mermaid:

### Comandos Frecuentes

1. **Renderizar texto directo a SVG o PNG:**
   ```bash
   python tools/mermaid_generator.py --text "flowchart TD; A[Inicio]-->B[Fin]" -o img/flujo.svg
   python tools/mermaid_generator.py --text "sequenceDiagram; A->>B: Hola" -o img/secuencia.png --theme dark
   ```

2. **Renderizar desde un archivo `.mmd` o `.txt`:**
   ```bash
   python tools/mermaid_generator.py -i diagrama.mmd -o img/diagrama.svg --theme forest
   ```

3. **Extraer y renderizar todos los bloques ```` ```mermaid ```` de un archivo Markdown:**
   ```bash
   python tools/mermaid_generator.py --extract Documento.md --output-dir img/
   ```

4. **Validar sintaxis y buenas prácticas:**
   ```bash
   python tools/mermaid_generator.py --validate diagrama.mmd
   ```

5. **Obtener plantilla de ejemplo:**
   ```bash
   python tools/mermaid_generator.py --example <flowchart|sequence|class|state|er|gantt|gitGraph|pie|mindmap|timeline>
   ```

---

## 2. Reglas de Oro de Sintaxis (Evitar Errores Comunes)

1. **Entrecomillar SIEMPRE etiquetas con caracteres especiales:**
   * ❌ **Incorrecto:** `A[Proceso (Principal)]` o `B[Archivo: data.csv]` (los paréntesis y dos puntos rompen el parser).
   * ✅ **Correcto:** `A["Proceso (Principal)"]` o `B["Archivo: data.csv"]`.
2. **Evitar etiquetas HTML complejas:**
   * No usar `<div>`, `<span>` o estilos en línea dentro de los nodos. Para saltos de línea utilizar `<br/>`.
3. **Preferir `flowchart` en lugar de `graph`:**
   * `flowchart TD` y `flowchart LR` ofrecen mejor cálculo de curvas, soporte de subgrafos y formas modernas.
4. **Nombres de identificadores limpios:**
   * Usa IDs alfanuméricos simples sin espacios: `proc1["Mi Proceso"]`, no `Mi Proceso["Mi Proceso"]`.
5. **No mezclar direcciones en el mismo nivel:**
   * `TD` / `TB` (Arriba a abajo) para jerarquías y árboles.
   * `LR` (Izquierda a derecha) para procesos, pipelines y autómatas.

---

## 3. Catálogo Rápido de Diagramas Mermaid

### A. Diagramas de Flujo (`flowchart`)
```mermaid
flowchart TD
    inicio(["Inicio"]) --> decision{"¿Es válido?"}
    decision -->|Sí| proceso["Procesar datos"]
    decision -->|No| error["Reportar error"]
    proceso --> db[("Base de Datos")]
    error --> fin(["Fin"])
    db --> fin

    subgraph Modulo ["Módulo de Persistencia"]
        db
    end

    style inicio fill:#d4edda,stroke:#28a745,stroke-width:2px
    style error fill:#f8d7da,stroke:#dc3545,stroke-width:2px
```

* **Formas de nodos:**
  - `[Rectángulo]`
  - `(["Píldora / Terminal"])`
  - `{"Rombo / Decisión"}`
  - `[("Cilindro / BD")]`
  - `[["Subrutina"]]`
  - `(("Círculo"))`

---

### B. Diagramas de Secuencia (`sequenceDiagram`)
```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant C as Compilador
    participant L as Lexer
    participant P as Parser

    U->>C: Ejecuta python3 compilador.py
    activate C
    C->>L: Escanear archivo.txt
    activate L
    L-->>C: Lista de Tokens
    deactivate L
    C->>P: Analizar sintaxis
    activate P
    alt Sintaxis Correcta
        P-->>C: AST OK
        C-->>U: Imprime OK
    else Error Sintáctico
        P-->>C: Error en línea N
        C-->>U: Imprime ERROR SINTACTICO linea N
    end
    deactivate P
    deactivate C
```

---

### C. Diagramas de Clases (`classDiagram`)
```mermaid
classDiagram
    class Compilador {
        -String archivoFuente
        +compilar() bool
    }
    class Lexer {
        +escanear() List~Token~
    }
    class Parser {
        +analizar() AST
    }
    Compilador *-- Lexer : contiene
    Compilador *-- Parser : contiene
```

* **Relaciones:**
  - `<|--` Herencia
  - `*--` Composición
  - `o--` Agregación
  - `-->` Asociación
  - `..>` Dependencia

---

### D. Diagramas de Estados (`stateDiagram-v2`)
```mermaid
stateDiagram-v2
    [*] --> Inactivo
    Inactivo --> Compilando : Iniciar
    state Compilando {
        [*] --> AnalisisLexico
        AnalisisLexico --> AnalisisSintactico : Tokens válidos
    }
    Compilando --> Exito : Sin errores
    Compilando --> Fallo : Error detectado
    Exito --> [*]
    Fallo --> [*]
```

---

### E. Diagramas Entidad-Relación (`erDiagram`)
```mermaid
erDiagram
    GRUPO ||--|{ ESTUDIANTE : integra
    GRUPO ||--o{ ENTREGA : presenta
    ENTREGA ||--|{ PRUEBA : evalua

    GRUPO {
        int id PK
        string tema
    }
    ENTREGA {
        int numero PK
        date fecha
        string calificacion
    }
```

---

### F. Diagramas de Gantt (`gantt`)
```mermaid
gantt
    title Cronograma de Entrega
    dateFormat YYYY-MM-DD
    section Desarrollo
    Léxico (Emiliano)   :active, 2026-10-20, 2d
    Sintáctico (Pablo)  :active, 2026-10-20, 2d
    section Testing
    Testing Cruzado IA  :2026-10-22, 3d
    section Cierre
    Entrega final       :crit, 2026-10-27, 1d
```

---

### G. Gráficos de Git (`gitGraph`)
```mermaid
gitGraph
    commit id: "Init"
    branch dev
    checkout dev
    commit id: "lexico.py"
    commit id: "sintactico.py"
    checkout main
    merge dev id: "Release 2.0" tag: "v2.0"
```

---

## 4. Cuándo Usar Mermaid vs. SVG Estático

| Criterio | Bloque ```` ```mermaid ```` en Markdown | SVG Exportado con `tools/` |
| :--- | :--- | :--- |
| **Ventaja principal** | 100% editable directamente en el texto | Renderizado garantizado en cualquier visor |
| **Soporte GitHub / VS Code** | Excelente (nativo) | Excelente (nativo) |
| **Soporte en visores PDF / texto plano** | Requiere conversor externo | Se incrusta directamente |
| **Recomendación de uso** | Apuntes, documentación viva, PRs | Entregas formales, README finales, informes |
