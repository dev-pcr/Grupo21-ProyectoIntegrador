---
name: diagram-generator
description: >-
  Genera diagramas SVG limpios, ordenados y profesionales (sin dependencias) de cualquier cosa:
  flujos de proceso, diagramas de flujo, autómatas y máquinas de estados, árboles (sintácticos,
  jerárquicos, organigramas), pipelines, arquitecturas en capas, diagramas de secuencia, líneas de
  tiempo, grafos de dependencias y relaciones. Usa esta skill SIEMPRE que el usuario pida un
  diagrama, esquema, gráfico de flujo, "dibújame/muéstrame cómo funciona X", una figura para
  documentación, apuntes, README o presentación, o cuando una explicación mejore con un esquema
  visual, aunque no diga la palabra "diagrama". También para mejorar o rehacer un diagrama
  existente. No uses bloques Mermaid: muchos visores de Markdown no los renderizan.
---

# Diagram Generator

Convierte una especificación JSON en un SVG vectorial limpio. El **layout es automático**
(capas, minimización de cruces, aristas enrutadas sin atravesar nodos), así que normalmente
solo hay que describir *qué* se conecta con *qué*, no dónde dibujarlo.

- Script: `tools/diagram_generator.py` (Python 3 estándar, sin dependencias)
- Ejemplos listos: `python tools/diagram_generator.py --example <tipo>` imprime un JSON de partida

## Flujo de trabajo (síguelo siempre)

1. **Elige el tipo** de diagrama con la tabla de abajo.
2. **Escribe el JSON** (`spec.json`). Empieza con `--example <tipo>` y modifícalo.
3. **Genera**:
   ```bash
   python tools/diagram_generator.py --json spec.json --output "<Carpeta>/img/nombre.svg" --png /tmp/preview.png
   ```
4. **Revisa el resultado** si hay `--png` disponible (el script prueba cairosvg, rsvg-convert,
   inkscape o ImageMagick; si no hay ninguno avisa y se omite). Mira la imagen y aplica la
   checklist de calidad. Corrige el JSON y regenera; una o dos iteraciones suelen bastar.
5. **Incrusta** en el Markdown y no dejes el `.png` de preview en el repo.

## Qué tipo usar

| Quiero mostrar…                                        | `type`                  |
|--------------------------------------------------------|-------------------------|
| Pasos con decisiones y bucles                          | `flowchart`             |
| Estados y transiciones (AFD, AFN, AP, máquina de estados) | `automaton` / `state` |
| Etapas encadenadas (compilador, CI/CD, ETL)            | `pipeline`              |
| Jerarquía (árbol sintáctico, organigrama, taxonomía)   | `tree`                  |
| Relaciones arbitrarias (dependencias, red, módulos)    | `graph`                 |
| Interacción entre actores en el tiempo                 | `sequence`              |
| Niveles apilados (arquitectura, modelo OSI)            | `layers`                |
| Hitos cronológicos                                     | `timeline`              |

Si lo pedido no encaja (gráficos de barras, mapas, UML de clases detallado), dilo y propón la
alternativa más cercana en vez de forzar un tipo.

## Reglas de diseño: que salga limpio y ordenado

Estas reglas importan más que cualquier opción técnica.

- **Un diagrama, una idea.** Más de ~12–15 nodos se vuelve ilegible: divide en varios diagramas
  (visión general + detalle) en lugar de comprimir.
- **Una sola dirección de lectura.** `LR` (izquierda→derecha) para procesos y autómatas,
  `TB` (arriba→abajo) para jerarquías y flujos con decisiones. No mezcles.
- **Etiquetas cortas.** Nodos: 1–3 palabras (usa `sub` para el detalle secundario). Aristas:
  1 palabra o símbolo. Lo que no cabe, va en el texto del documento, no en el diagrama.
- **El color significa algo, y poco.** Máximo 3–4 colores con rol fijo (p. ej. `green` =
  inicio/fin/éxito, `amber` = decisión, `red` = error, `blue` = elemento destacado, `gray` =
  neutro). No uses color solo por decorar.
- **La forma significa algo.** Misma forma para el mismo tipo de cosa en todo el diagrama
  (`decision` solo para decisiones, `db` solo para almacenes, `circle` para estados).
- **Aristas siempre etiquetadas cuando hay bifurcación** (Sí/No, símbolos de transición).
  Sin etiqueta cuando el significado es obvio.
- **Orden de declaración = orden de lectura.** Declara los nodos en el orden lógico: el
  algoritmo lo usa como pista inicial para colocar y acaba más limpio.
- **Título corto** (`title`) que diga qué es el diagrama; `subtitle` opcional para el contexto.
- **Texto accesible:** añade `"alt"` con una descripción de una frase.
- No pongas texto dentro de las aristas largas ni superpongas leyendas; si hace falta una
  leyenda, explícala en el texto del documento.

### Checklist visual (revisa el PNG antes de entregar)
- [ ] Ninguna arista atraviesa un nodo ni se solapa con otra de forma confusa
- [ ] Ninguna etiqueta tapa una flecha o está pegada a un nodo
- [ ] Mínimos cruces de aristas; el flujo principal se lee en línea recta
- [ ] Márgenes equilibrados, nada recortado en los bordes
- [ ] Texto legible a ancho de documento (~700 px); si no, hay demasiado contenido
- [ ] Colores y formas consistentes con su significado

## Esquema JSON

Campos comunes a todos los tipos: `type`, `title`, `subtitle`, `alt`, `theme`
(`light` | `dark`), `background` (`"none"` para fondo transparente). **No hay que dar
`width`/`height`**: el lienzo se ajusta solo al contenido.

### Grafos: `graph`, `flowchart`, `automaton`, `state`, `pipeline`

```json
{
  "type": "flowchart",
  "direction": "TB",
  "nodes": [
    {"id": "s", "label": "Inicio", "shape": "start", "color": "green"},
    {"id": "v", "label": "¿Válido?", "shape": "decision", "color": "amber"}
  ],
  "edges": [
    {"from": "s", "to": "v"},
    {"from": "v", "to": "s", "label": "No", "style": "dashed"}
  ]
}
```

**Nodo:** `id` (obligatorio), `label`, `sub` (segunda línea tenue), `shape`, `color`,
`highlight` (atajo para `color: blue`), `initial`, `final`.

| `shape`            | Uso                                   |
|--------------------|---------------------------------------|
| `rounded` (defecto)| Proceso / componente                  |
| `box`              | Rectángulo de esquinas casi rectas    |
| `pill` / `start` / `end` / `terminal` | Inicio y fin       |
| `decision` (diamond)| Decisión                              |
| `io`               | Entrada/salida (paralelogramo)        |
| `db` (cylinder)    | Base de datos / almacén               |
| `circle` / `ellipse`| Estados (`automaton` usa `circle`)   |
| `doublecircle`     | Estado final (automático con `final`) |

**Colores:** `gray`, `blue`, `green`, `amber`, `red`, `purple`, `coral`, `pink`, o un hex
(`"#3366cc"`; se derivan relleno y texto automáticamente).

**Arista:** `from`, `to`, `label` (o `labels: [...]` para varias líneas, útil en autómatas de
pila), `style` (`solid` | `dashed` | `dotted`), `color`, `arrow` (`end` | `both` | `none`),
`loop` (`up` | `down` | `left` | `right`, solo para auto-bucles; por defecto `up` en `LR`).
Los auto-bucles (`from == to`) y las aristas bidireccionales (A→B y B→A) se separan solos.

**Opciones del diagrama:** `direction` (`LR`, `RL`, `TB`, `BT`), `routing` (`curve` |
`ortho` | `straight`; por defecto `ortho` en flowchart y `curve` en el resto),
`align_leaves` (alinea los nodos sin salida en la última capa), `max_label_width`.

**`automaton`/`state`** aceptan además los nombres `states` y `transitions` en lugar de
`nodes` y `edges`. `initial: true` dibuja la flecha de entrada y `final: true` el doble círculo.

**`pipeline`** es un atajo:
```json
{"type": "pipeline",
 "stages": [
   {"title": "Fuente", "sub": "Código"},
   {"title": "Léxico", "sub": "Scanner", "output_label": "Tokens"},
   {"title": "Parser", "highlight": true}]}
```
Encadena las etapas automáticamente; `output_label` etiqueta la flecha de salida. Para
aristas extra (p. ej. retroalimentación) añade `edges` con `id`s `s0`, `s1`, …

**Posiciones manuales (modo compatible):** si *todos* los nodos traen `x` e `y`, no se
auto-coloca nada y se respetan tus coordenadas. Úsalo solo cuando necesites una disposición
exacta; para todo lo demás deja que el auto-layout trabaje.

### Árbol: `tree`
```json
{"type": "tree", "leaf_color": "green", "align_leaves": true,
 "root": {"label": "E", "children": [
   {"label": "E", "children": [{"label": "3"}]},
   {"label": "+"},
   {"label": "T", "children": [{"label": "4"}]}]}}
```
Cada nodo acepta los mismos campos que un nodo de grafo (`sub`, `shape`, `color`).
`leaf_color` / `leaf_shape` estilizan las hojas (terminales). `align_leaves: true` pone todas
las hojas en la fila inferior: recomendado para árboles sintácticos. `direction: "LR"` lo gira.

### Secuencia: `sequence`
```json
{"type": "sequence", "numbered": true,
 "participants": ["Cliente", "API", {"id": "db", "label": "BD", "shape": "cylinder"}],
 "messages": [
   {"from": "Cliente", "to": "API", "label": "GET /items"},
   {"from": "API", "to": "db", "label": "SELECT"},
   {"note": "Cacheado 60 s", "over": "API"},
   {"from": "db", "to": "API", "label": "filas", "type": "return"},
   {"from": "API", "to": "API", "label": "serializar"}]}
```
`type`: `call` (defecto) o `return` (discontinua). `from == to` genera un auto-mensaje.
`note` + `over` (id o lista de ids) pone una nota sobre uno o varios participantes.

### Capas: `layers`
```json
{"type": "layers",
 "layers": [
   {"title": "Presentación", "color": "blue", "items": ["Web", "Móvil"]},
   {"title": "Datos", "color": "amber", "items": [{"label": "PostgreSQL", "sub": "primaria"}]}]}
```
Opciones: `arrows` (flechas entre capas, defecto `true`), `bidirectional`, `max_width`
(ancho de la zona de ítems; se ajustan en varias filas).

### Línea de tiempo: `timeline`
```json
{"type": "timeline",
 "events": [{"date": "Ene", "title": "Kick-off", "desc": "Equipo definido"},
            {"date": "Mar", "title": "Prototipo"}]}
```
Opciones: `card_width`, `colorful` (un color por evento), `color` por evento.

## Incrustar en Markdown

Guarda siempre los diagramas en `<Carpeta>/img/<nombre>.svg` e incrústalos así:
```markdown
![Descripción breve y útil](img/<nombre>.svg)
```
Usa nombres descriptivos en minúsculas (`automata-ab.svg`, no `diagrama1.svg`). El SVG lleva
fondo blanco por defecto; usa `"theme": "dark"` para documentos oscuros o
`"background": "none"` para fondo transparente. No uses bloques Mermaid.

## Solución de problemas

| Síntoma                                         | Qué hacer                                                              |
|-------------------------------------------------|------------------------------------------------------------------------|
| `Arista referencia un nodo inexistente`         | Revisa que `from`/`to` coincidan con algún `id`                        |
| Diagrama enorme o ilegible                       | Demasiados nodos: divídelo; acorta etiquetas; usa `max_label_width`    |
| Muchas aristas largas que dan la vuelta          | Cambia `direction`, reordena la declaración de nodos o activa `align_leaves` |
| Etiqueta pegada a un nodo                        | Acórtala o ponla en `sub` del nodo                                     |
| Auto-bucle choca con un vecino                   | Cambia su `loop` a `down` (o `left`/`right`)                           |
| Aviso `nodos solapados` (modo manual)            | Separa las coordenadas o quita `x`/`y` para usar auto-layout           |
| No aparece el PNG                                | No hay conversor instalado: revisa el SVG abriéndolo en un navegador   |

## Límites conocidos
- No hay agrupación en clústeres/subgrafos; para eso usa `layers` o divide el diagrama.
- El tamaño del texto se estima (sin fuentes reales): deja holgura con etiquetas cortas.
- Pensado para diagramas de hasta ~15–20 nodos; más allá, divide.

