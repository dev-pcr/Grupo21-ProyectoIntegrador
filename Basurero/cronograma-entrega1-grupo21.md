# Cronograma Entrega 1 — Grupo 21 (Compiladores)

Fecha límite: **27/10/2026** — Entrega: `tokens.txt` + `gramatica.txt` (Grupo-21.zip)
Cronograma visual: https://docs.google.com/spreadsheets/d/1w3fv_nT0hsmPideLIj8_u12wagmQ3UiuRsQxQmmbkAA/edit?gid=0#gid=0

Leyenda: 👥 Conjunto · 🅰️ Persona A (Emi) · 🅱️ Persona B (Pablo)

---

## Semana 1 — Setup y Repaso (19/9 – 25/9)

### Sábado 19/9 y Domingo 20/9 — 👥 Leer y entender el proyecto

- [ ] Leer el enunciado completo (secciones 1 a 9)
- [ ] Leer el Anexo completo (secciones A a G)
- [ ] Anotar dudas o partes poco claras para discutirlas juntos en un documento "Historico.md".

### Lunes 21/9 — 👥 Corregir cronograma

- [ ] Ajustar fechas y responsables según la planificación actual.
- [ ] Crear repositorio (privado) e invitar al otro integrante. Subir mds.

### Miércoles 23/9 — 👥 Repaso técnico

- [ ] Repasar expresiones regulares de Python (módulo `re`): clases de caracteres, cuantificadores, grupos, alternancia
- [ ] Repasar el Anexo completo.
- [ ] Repasar gramáticas libres de contexto: terminal, no terminal, recursión, cómo se logra precedencia sin `%left`/`%right`

---

## Semana 2 — Nombres y Primeros Archivos (26/9 – 2/10)

### Sábado 26/9 — 👥 Configurar GitHub

- [ ] Crear estructura de carpetas: `tokens.txt`, `gramatica.txt`, `casos/`, `README.md`
- [ ] Copiar los 9 casos públicos a `casos/`
- [ ] Primer commit y push

### Domingo 27/9 — 👥 Acordar la lista de nombres de tokens

- [ ] Listar todos los tokens necesarios según el Anexo (palabras reservadas, tipos, booleanos, constantes, funciones, operadores/signos, identificador, número entero, número decimal, cadena)
- [ ] Definir el nombre de cada uno (mayúsculas, sin espacios, sin tildes)
- [ ] Guardar la lista acordada en el repo (borrador, puede ir en el README)

### Lunes 28/9 a Viernes 2/10 — 🅰️🅱️ Inicio de trabajo en paralelo

- [ ] 🅰️ **Emi:** `tokens.txt` (patrones regex, descripciones, ejemplos, observaciones).
- [ ] 🅱️ **Pablo:** `gramatica.txt` (reglas, jerarquía de precedencia con no terminales tipo `expresion`/`termino`/`factor`).

---

## Semana 3 — Trabajo en Paralelo (3/10 – 9/10)

### Sábado 3/10 a Viernes 9/10 — 🅰️🅱️ Desarrollo continuo

- [ ] 🅰️ **Emi:** Continuar con `tokens.txt`.
  - [ ] `tokens.txt`: patrones de `loop`, `setup`, `void`, `boolean`, `char`, `float`
  - [ ] `tokens.txt`: booleanos (`false`, `true`) y constantes (`HIGH`, `INPUT`, `INPUT_PULLUP`, `LED_BUILTIN`, `LOW`, `OUTPUT`)
  - [ ] `tokens.txt`: identificador, número entero, número decimal, cadena
  - [ ] `tokens.txt`: operadores y signos `( ) * + , - / ; = { } += -=`
  - [ ] `tokens.txt`: directiva `@ignorar` (espacios/tabs/saltos de línea, comentarios de bloque `/* */` multilínea)
- [ ] 🅱️ **Pablo:** Continuar con `gramatica.txt`.
  - [ ] `gramatica.txt`: reglas de asignación (`=`, `-=`, `+=`) y llamada a función como sentencia
  - [ ] `gramatica.txt`: esqueleto — `programa -> definicion | programa definicion`, reglas de `setup()`/`loop()`
  - [ ] `gramatica.txt`: regla de declaración de variable (con y sin inicialización)
  - [ ] `gramatica.txt`: jerarquía de precedencia — `expresion -> expresion + termino | expresion - termino | termino`, `termino -> termino * factor | termino / factor | factor`
  - [ ] `gramatica.txt`: regla de `factor`/operando (identificador, número, `( expresion )`, llamada, cadena, booleano, constante)

---

## Semana 4 — Intercambio y Validación (10/10 – 16/10)

### Sábado 10/10 y Domingo 11/10 — 🅰️🅱️ Últimos detalles individuales

- [ ] 🅰️ **Emi:** Revisar `tokens.txt`: cada token tiene `# descripción`, `# ejemplos` y, si corresponde, `# observaciones`
- [ ] 🅱️ **Pablo:** Revisar `gramatica.txt`: todo no terminal usado tiene regla definida; todo terminal existe en `tokens.txt`

### Domingo 11/10 a Viernes 16/10 — 👥 Validar e intercambiar archivos

- [ ] Cada uno lee el archivo del otro
- [ ] Anotar observaciones (sin corregir todavía en "Historico.md")
- [ ] Realizar las correcciones pertinentes.
- [ ] 🅰️ Incorporar observaciones recibidas sobre `tokens.txt`
- [ ] 🅱️ Incorporar observaciones recibidas sobre `gramatica.txt`
- [ ] Revisar el orden en `tokens.txt`: palabras reservadas, tipos, booleanos y constantes van **antes** que el token de identificador (por el desempate de "cadena más larga, primero escrito")
- [ ] Revisar que la jerarquía de precedencia en `gramatica.txt` esté completa y sin alternativas vacías
- [ ] Dar por completos `tokens.txt` y `gramatica.txt`, listos para verificación (Versión candidata)

---

## Semana 5 — Estudio del Código (17/10 – 23/10)

### Sábado 17/10 a Viernes 23/10 — 👥 Semana de estudio del código

- [ ] **Verificar casos válidos:** `valido-01.txt`, `valido-02.txt`, `valido-03.txt` → deben dar OK
- [ ] **Verificar casos léxicos:** `lexico-01.txt` → ERROR LEXICO línea 3; `lexico-02.txt` → ERROR LEXICO línea 5; `lexico-03.txt` → ERROR LEXICO línea 8
- [ ] **Verificar casos sintácticos:** `sintactico-01.txt` → ERROR SINTACTICO línea 2; `sintactico-02.txt` → ERROR SINTACTICO línea 5; `sintactico-03.txt` → ERROR SINTACTICO línea 4
- [ ] Corregir cualquier desajuste encontrado.
- [ ] Repaso general: Repasar el Anexo, `tokens.txt` y `gramatica.txt` completos, pensando en poder explicar cualquier decisión.
- [ ] Segunda verificación: Volver a correr los 9 casos contra la versión corregida.
- [ ] Resolver cualquier duda pendiente antes de la contingencia.

---

## Semana 6 — Contingencia y Entrega (24/10 – 27/10)

### Sábado 24/10 y Domingo 25/10 — 👥 Días de contingencia

- [ ] Ajustes finales de redacción (descripciones, ejemplos, observaciones)
- [ ] Revisión de prolijidad: formato, comentarios con `#`, nombres de tokens sin tildes ni espacios

### Lunes 26/10 y Martes 27/10 — 👥 Entrega: Tokens + Gramática

- [ ] Armar `Grupo-21.zip` con `tokens.txt` y `gramatica.txt`
- [ ] Subir a la plataforma
- [ ] Confirmar que la entrega quedó registrada
- [ ] (Solo usar el 27/10 si algo falló el día anterior: plataforma, archivo corrupto, etc.)

---

## Checklist final antes de entregar

- [ ] `tokens.txt` contiene **todos** los tokens del Anexo (apartado B) y ninguno más
- [ ] Cada token tiene `# descripción`, `# ejemplos` y `# observaciones` cuando corresponde
- [ ] Palabras reservadas / tipos / booleanos / constantes están **antes** del identificador en el archivo
- [ ] Hay al menos una directiva `@ignorar` que cubre espacios, tabs, saltos de línea y comentarios de bloque
- [ ] `gramatica.txt` cubre **todas** las construcciones del apartado D y ninguna otra
- [ ] Todo no terminal usado tiene regla definida; todo terminal existe en `tokens.txt`
- [ ] La precedencia de `*`/`/` sobre `+`/`-` está resuelta con jerarquía de no terminales, no con operadores unarios
- [ ] Ninguna alternativa de la gramática está vacía
- [ ] Los 9 casos públicos dan el resultado esperado (tipo y línea)
- [ ] `Grupo-21.zip` contiene exactamente `tokens.txt` y `gramatica.txt`
- [ ] Entrega subida a la plataforma antes del 27/10
