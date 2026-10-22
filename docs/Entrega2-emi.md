# Entrega 2 — Parte de Emiliano: Analizador Léxico (guía de estudio para el oral)

**Grupo N.º 21 — Compiladores 2026 — UCASAL**  
**Archivo principal:** `lexico.py` · **Integración:** `compilador.py` · **Verificación:** `herramientas/verificar_lexico_ply.py`

> Este documento explica **qué se hizo y por qué**, en lenguaje conceptual y riguroso, para que Emi y Pablo puedan responder con solidez en la defensa oral y realizar la modificación en vivo del analizador léxico sin vacilar. No hace falta memorizar código: hay que entender las ideas y la mecánica interna de `ply.lex`.

---

## 1. ¿Qué hace el analizador léxico y dónde encaja?

El analizador léxico (o *scanner*) es la **primera fase** del compilador. Trabaja en cadena alimentando al analizador sintáctico:

```
Código fuente  ──►  LÉXICO (Emi)  ──►  flujo de tokens  ──►  SINTÁCTICO (Pablo)  ──►  OK / ERROR
(texto plano)       lexico.py          (piezas léxicas)       sintactico.py
```

- **Misión del analizador léxico:** Lee el archivo fuente carácter por carácter, agrupa secuencias de caracteres que tienen significado coherente en **componentes léxicos (tokens)** y descarta aquello que no aporta a la sintaxis (espacios en blanco, tabulaciones, retornos de carro y comentarios).
- **Aislamiento de errores:** Detecta caracteres ilegales que no pertenecen al alfabeto del lenguaje (por ejemplo: `@`, `€`, `\`, letras con tilde como `á`).
- **Coordinación:** Registra los errores con su número de línea exacto para que `compilador.py` pueda cotejar si el primer error del archivo fue léxico o sintáctico.

### Token, Lexema y Patrón (Pregunta fija de examen)

| Concepto | Definición teórica | Ejemplo en nuestro proyecto |
| :-- | :-- | :-- |
| **Token** | Nombre abstracto o categoría terminal que maneja la gramática. | `IDENTIFICADOR`, `FLOAT`, `DECIMAL`, `SERIAL_PRINTLN` |
| **Lexema** | Secuencia concreta de caracteres del código fuente que coincide con el patrón. | `temperatura`, `float`, `195.39`, `Serial.println` |
| **Patrón** | Regla formal (expresión regular) que describe el conjunto de lexemas válidos. | `[a-zA-Z_][a-zA-Z0-9_]*`, `float`, `[0-9]+\.[0-9]+` |

---

## 2. Los componentes léxicos del lenguaje (qué se acepta y qué se rechaza)

Nuestro lenguaje es un **subconjunto de Arduino (C++ para microcontrolador)** formalizado en `tokens.txt`:

| Categoría | Tokens del lenguaje | Expresión regular / Regla en PLY | Observaciones |
| :-- | :-- | :-- | :-- |
| **Palabras reservadas** | `SETUP`, `LOOP`, `VOID` | `setup`, `loop`, `void` | Minúsculas exactas; no pueden usarse como identificador. |
| **Tipos de datos** | `BOOLEAN`, `CHAR`, `FLOAT` | `boolean`, `char`, `float` | Minúsculas exactas. |
| **Booleanos** | `FALSE`, `TRUE` | `false`, `true` | Minúsculas exactas. |
| **Constantes Arduino** | `HIGH`, `LOW`, `INPUT`, `INPUT_PULLUP`, `LED_BUILTIN`, `OUTPUT` | Mapeo textual en mayúsculas | `INPUT` es prefijo de `INPUT_PULLUP`: desempata por longitud. |
| **Funciones** | `MAP`, `DELAY`, `SERIAL_PRINTLN` | `map`, `delay`, `Serial\.println` | `Serial.println` lleva punto pegado; no admite espacios. |
| **Asignación** | `IGUAL`, `SUMA_IGUAL`, `RESTA_IGUAL` | `=`, `+=`, `-=` | No hay `*=` ni `/=`. `+=` y `-=` sin espacios. |
| **Aritméticos** | `SUMA`, `RESTA`, `MULTIPLICACION`, `DIVISION` | `+`, `-`, `*`, `/` | Solo binarios: no hay operadores unarios (`-5` o `-x`). |
| **Delimitadores** | `PARENTESIS_IZQ/DER`, `LLAVE_IZQ/DER`, `COMA`, `PUNTO_Y_COMA` | `(`, `)`, `{`, `}`, `,`, `;` | Caracteres simples escapados según sintaxis regex. |
| **Números** | `ENTERO`, `DECIMAL` | `[0-9]+` / `[0-9]+\.[0-9]+` | Sin signo ni exponente (`1e3` o `3.` no son válidos). |
| **Cadenas** | `CADENA` | `"[^"\n]*"\|'[^'\n]*'` | Comillas dobles o simples en una sola línea; sin escapes. |
| **Identificadores** | `IDENTIFICADOR` | `[a-zA-Z_][a-zA-Z0-9_]*` | Solo ASCII (sin ñ ni tildes). No puede ser palabra clave. |

**Qué se descarta (@ignorar):**
- Espacios, tabulaciones y retornos de carro (`[ \t\r]+`).
- Comentarios de bloque (`/* ... */`): pueden ocupar múltiples líneas y no se anidan.

**Qué NO pertenece al lenguaje (y genera error léxico):**
- Caracteres fuera del conjunto ASCII o símbolos no contemplados: `@`, `#`, `$`, `%`, `&`, `|`, `~`, `^`, `\`, `€`, `¿`, `ñ`, tildes, emojis.
- Comillas no cerradas en una misma línea (`"hola` o `'mundo`).
- Puntos decimales colgantes (`.5` o `3.`).

---

## 3. Idea central 1: resolución de palabras clave con diccionario `reserved`

### El problema: colisiones y desempates
Si definiéramos una expresión regular independiente para cada palabra clave (por ejemplo: `t_FLOAT = r'float'`) y otra para identificadores (`t_IDENTIFICADOR = r'[a-zA-Z_][a-zA-Z0-9_]*'`), surgirían graves conflictos:
1. En un lexema como `float1` o `mapa`, PLY podría partir erróneamente el texto reconociendo `FLOAT` o `MAP` y dejando `1` o `a` como identificador suelto.
2. Si un identificador coincide en longitud con una palabra clave (empate exacto), el orden de evaluación dictamina quién gana.

### La solución estándar de la industria
Se define una **única regla** para todos los identificadores (`t_IDENTIFICADOR`) y se consulta un diccionario hash `reserved`:

```python
reserved = {
    'setup': 'SETUP', 'loop': 'LOOP', 'void': 'VOID',
    'boolean': 'BOOLEAN', 'char': 'CHAR', 'float': 'FLOAT',
    'false': 'FALSE', 'true': 'TRUE',
    'HIGH': 'HIGH', 'LOW': 'LOW', 'INPUT': 'INPUT',
    'INPUT_PULLUP': 'INPUT_PULLUP', 'LED_BUILTIN': 'LED_BUILTIN', 'OUTPUT': 'OUTPUT',
    'map': 'MAP', 'delay': 'DELAY',
}

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFICADOR')
    return t
```

**Por qué funciona:**
- Por la regla del **patrón más largo** (*longest match*), `float1` se consume completo como un identificador de 6 caracteres. Luego se busca en `reserved`: al no estar, queda como `IDENTIFICADOR`.
- Si entra `float`, se consume completo, se busca en `reserved` y se transforma en el token `FLOAT`.
- Búsqueda en $O(1)$ sin colisiones de prefijo.

---

## 4. Idea central 2: orden de evaluación en PLY y el caso `Serial.println`

### El modelo interno de precedencia de `ply.lex`
PLY sigue dos reglas fijas para determinar qué regla regex se prueba primero:

1. **Prioridad absoluta de funciones:** Las reglas definidas como funciones (`def t_*`) se evalúan **SIEMPRE ANTES** que las reglas definidas como cadenas (`t_* = r'...'`).
2. **Orden interno:**
   - Entre funciones: se evalúan en el **orden estricto de declaración en el archivo** (de arriba hacia abajo).
   - Entre cadenas: PLY las ordena automáticamente por **longitud de expresión regular decreciente** (patrón más largo primero).

### El bug documentado en `log-de-errores.md`
En las primeras pruebas, 18 casos fallaron porque `Serial.println` se rompía:
- `t_IDENTIFICADOR` era una **función** (`def t_IDENTIFICADOR`).
- `t_SERIAL_PRINTLN` era una **cadena** (`t_SERIAL_PRINTLN = r'Serial\.println'`).
- Al ejecutarse, PLY probó primero `t_IDENTIFICADOR`: reconoció `Serial` como identificador válido y dejó el punto `.` como un carácter no reconocido, arruinando el token compuesto.

### La corrección definitiva
Transformar `t_SERIAL_PRINTLN` en una **función** y ubicarla en el archivo estrictamente **antes** de `t_IDENTIFICADOR`:

```python
def t_SERIAL_PRINTLN(t):
    r'Serial\.println'
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFICADOR')
    return t
```

Del mismo modo, `def t_DECIMAL` se ubica antes de `def t_ENTERO` para que un lexema como `3.25` se empareje como decimal antes de que `t_ENTERO` intente tomar el `3`.

---

## 5. Idea central 3: descarte de comentarios y seguimiento de líneas (`lineno`)

### ¿Por qué los comentarios no pueden ser simplemente una regex en `t_ignore`?
La variable `t_ignore` de PLY solo admite caracteres simples que se descartan de forma estática (espacios, tabs). No permite ejecutar código Python.

Un comentario de bloque `/* ... */` puede ocupar **múltiples líneas**:
```cpp
/* Este es un comentario
   que ocupa dos líneas */
float x = @;
```
Si el lexer simplemente saltara el comentario sin contar cuántos saltos de línea contenía, el error léxico en `@` se reportaría en una línea errónea, reprobando el caso de prueba.

### Implementación con función de descarte
```python
def t_COMMENT_BLOCK(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')
```
- `[\s\S]*?` empareja cualquier carácter (incluidos saltos de línea) de manera no codiciosa (*non-greedy*), deteniéndose en el primer `*/`.
- Al no devolver `t`, PLY descarta el token automáticamente.
- `t.lexer.lineno += t.value.count('\n')` mantiene sincronizado el número de línea.

### Compatibilidad CRLF (`\r\n`) y CR
En Windows o fuentes importadas, los saltos de línea pueden ser `\r\n` o `\r`. Al incluir `\r` en `t_ignore = ' \t\r'`, el retorno de carro se descarta silenciosamente y solo `\n` gatilla el conteo de líneas en `t_newline(t)`.

---

## 6. Idea central 4: captura y aislamiento de errores léxicos (`t_error`) y la Regla de Oro

### El problema de `t_error` por defecto
En los ejemplos básicos de la cátedra (`calclex.py`), `t_error` contiene:
```python
def t_error(t):
    print("Error léxico en línea...", t.value[0])
    t.lexer.skip(1)
```
Si hiciéramos eso, ante cualquier carácter extraño la consola imprimiría texto anticipado. Esto violaría la consigna estricta de la cátedra: **solo la primera línea de stdout es evaluada**. Además, si en la línea 2 hay un error sintáctico y en la 5 un carácter inválido, ¡el print imprimiría el error léxico antes de tiempo!

### Nuestra solución: lista acumulativa y `skip(1)`
```python
errores_lexicos = []

def t_error(t):
    global errores_lexicos
    caracter = t.value[0]
    errores_lexicos.append({
        'linea': t.lexer.lineno,
        'caracter': caracter,
        'posicion': t.lexpos,
        'mensaje': f"carácter no válido '{caracter}'"
    })
    t.lexer.skip(1)
```
- No produce ninguna salida por pantalla.
- Registra el carácter exacto y su número de línea.
- `skip(1)` avanza un carácter y continúa el escaneo para no colgar el proceso.

### Coordinación en `compilador.py` (La Regla de Oro)
Ante la presencia de múltiples anomalías, el compilador aplica el criterio de **primer error en el orden de lectura**:

```python
# Escaneo léxico completo
primer_lex = todos_errores_lexicos[0] if todos_errores_lexicos else None

# Análisis sintáctico
exito, error_sint = sintactico.analizar(contenido)

if primer_lex and error_sint:
    if primer_lex['linea'] <= error_sint['linea']:
        return f"ERROR LEXICO linea {primer_lex['linea']}: {primer_lex['mensaje']}"
    else:
        return f"ERROR SINTACTICO linea {error_sint['linea']}: {error_sint['mensaje']}"
elif primer_lex:
    return f"ERROR LEXICO linea {primer_lex['linea']}: {primer_lex['mensaje']}"
elif error_sint:
    return f"ERROR SINTACTICO linea {error_sint['linea']}: {error_sint['mensaje']}"
else:
    return "OK"
```
Si $L_{lex} \le L_{sint}$, se reporta el error léxico. Si $L_{sint} < L_{lex}$, se reporta el error sintáctico.

---

## 7. Cómo está organizado `lexico.py`

| Sección | Componentes | Rol en la arquitectura |
| :-- | :-- | :-- |
| **1. Diccionario `reserved`** | 16 palabras clave y constantes | Mapeo de lexemas a nombres de tokens para evitar colisiones. |
| **2. Lista `tokens`** | 34 nombres de terminales | Exporta los nombres de tokens válidos que requiere `ply.yacc`. |
| **3. Tokens simples** | `t_SUMA_IGUAL`, `t_RESTA_IGUAL`, etc. | Expresiones regulares de cadena ordenadas por PLY por longitud. |
| **4. Tokens con funciones** | `SERIAL_PRINTLN`, `IDENTIFICADOR`, etc. | Acciones semánticas y orden de precedencia estricto en PLY. |
| **5. Caracteres ignorados** | `t_ignore`, `t_COMMENT_BLOCK`, `t_newline` | Limpieza de espacios, comentarios y avance del contador `lineno`. |
| **6. Manejo de errores** | `t_error`, `errores_lexicos` | Captura limpia de caracteres inválidos sin print ruidoso. |
| **7. Constructor** | `crear_lexer()` | Fabrica una instancia limpia del lexer reseteando los errores. |

---

## 8. Cómo lo probamos

Diseñamos y ejecutamos una suite de verificación integral (`herramientas/verificar_lexico_ply.py`) ejecutando el motor real de PLY:

1. **39 micro-pruebas internas:** Validación de desempates (`setup` vs `setup1`, `INPUT` vs `INPUT_PULLUP`), constantes, números decimales, cadenas y descarte de comentarios.
2. **9 casos públicos de cátedra (`casos/`):** 3 válidos (`OK`), 3 léxicos y 3 sintácticos (100% de coincidencia exacta).
3. **109 casos de `pruebas-grupo/`:** 53 casos válidos (`ok-*`) y 56 casos léxicos (`lex-*`), evaluando caracteres extraños, cadenas sin cerrar, números mal formados y saltos de línea con CRLF.
4. **Verificación cruzada con sintáctico:** 151/151 casos en `verificar_sintactico_ply.py` y 0 conflictos en `parser.out`.

**Resultado:** **100% de casos aprobados** en todas las suites.

---

## 9. Preguntas probables del oral (con respuesta corta)

**1. ¿Qué es un analizador léxico y cuál es su objetivo?**  
Es la primera fase del compilador; lee caracteres de texto plano, descarta elementos irrelevantes (espacios, comentarios) y agrupa los caracteres válidos en tokens para el parser.

**2. ¿Cuál es la diferencia entre token, lexema y patrón?**  
El *token* es la categoría sintáctica (`IDENTIFICADOR`); el *lexema* es el texto concreto del programa (`contador`); el *patrón* es la expresión regular que define cómo se forma (`[a-zA-Z_][a-zA-Z0-9_]*`).

**3. ¿Cómo maneja PLY la precedencia entre reglas léxicas?**  
Las reglas definidas como funciones (`def t_*`) se evalúan primero y en orden de aparición en el archivo. Las reglas definidas como cadenas (`t_* = '...'`) se evalúan después, ordenadas por longitud decreciente de su regex.

**4. ¿Por qué `Serial.println` es una función y no una cadena?**  
Porque contiene un punto y su prefijo `Serial` coincide con `IDENTIFICADOR`. Como las funciones tienen prioridad sobre las cadenas, si fuera cadena, la función `t_IDENTIFICADOR` se comería `Serial` y el punto daría error. Siendo función antes de `t_IDENTIFICADOR`, gana `Serial.println`.

**5. ¿Por qué no pusieron cada palabra reservada como un token `t_LOOP = 'loop'`?**  
Porque generaría problemas con identificadores que empiezan con esas palabras (ej. `loop_1` o `mapa`). Al usar una sola regla `t_IDENTIFICADOR` con el diccionario `reserved`, el principio del patrón más largo (*longest match*) garantiza que `loop_1` sea un identificador completo.

**6. ¿Qué autómata implementa el analizador léxico?**  
Un Autómata Finito Determinista (DFA). PLY compila las expresiones regulares de los tokens en un motor de autómatas que avanza estado por estado reconociendo caracteres.

**7. ¿Cómo se cuentan las líneas dentro de un comentario multilínea?**  
Mediante la función `t_COMMENT_BLOCK`, calculando `t.lexer.lineno += t.value.count('\n')`.

**8. ¿Por qué `t_error` no imprime directamente a pantalla?**  
Para cumplir la consigna de salida única (`OK` o primer error). Si imprimiera directamente, rompería la regla de oro cuando ocurra un error sintáctico previo o generaría salidas múltiples no permitidas.

**9. ¿Qué ocurre con un número como `3.` o `.5`?**  
El patrón de `DECIMAL` exige dígitos a ambos lados (`[0-9]+\.[0-9]+`). En `3.`, el `3` se lee como `ENTERO` y el `.` queda suelto como carácter inválido (error léxico). En `.5`, el `.` inicial no coincide con nada y genera error léxico en el punto.

**10. ¿Cómo se reconocen las cadenas y por qué no admiten saltos de línea?**  
Con la regex `"[^"\n]*"|'[^'\n]*'`. El uso de `\n` negado dentro del conjunto (`[^"\n]`) asegura que la cadena termine obligatoriamente en la misma línea en que abrió.

**11. ¿Qué es la regla del patrón más largo (*longest match*)?**  
Entre dos patrones que coinciden a partir de la misma posición, el analizador elige el que reconoce la mayor cantidad de caracteres (ejemplo: `+=` sobre `+`, o `INPUT_PULLUP` sobre `INPUT`).

**12. Si en la línea 2 hay un error léxico y en la 4 uno sintáctico, ¿qué se informa?**  
`ERROR LEXICO linea 2: ...`, porque el compilador siempre reporta el primer error en el orden de lectura del archivo.

---

## 10. Modificaciones en vivo — cómo encararlas

En el examen oral nos pedirán modificar el analizador en tiempo real. Aquí está la receta exacta para los cambios léxicos más habituales:

### A) Agregar un nuevo operador (ej. `%` módulo o `==` igualdad)
1. Abrir `tokens.txt` y agregar:
   ```text
   MODULO %
   ```
2. Abrir `lexico.py`:
   - En la lista `tokens`, agregar `'MODULO'`.
   - En la sección 3 (tokens simples), agregar:
     ```python
     t_MODULO = r'%'
     ```
   *(Si fuera `==`, agregar `t_IGUAL_IGUAL = r'=='`; PLY la ordenará antes de `t_IGUAL` por longitud).*
3. Si el profesor pide integrarlo a la gramática, avisarle a Pablo para que agregue `MODULO` en `sintactico.py` (`termino`).
4. Correr `python herramientas/verificar_lexico_ply.py` para asegurar que no se rompieron casos previos.

### B) Agregar una nueva palabra reservada o constante (ej. `HIGH_IMPEDANCE` o `pinMode`)
1. Abrir `tokens.txt` y agregar el token.
2. Abrir `lexico.py`:
   - En el diccionario `reserved`, agregar:
     ```python
     'HIGH_IMPEDANCE': 'HIGH_IMPEDANCE',
     ```
   *(No hace falta tocar la lista `tokens` porque se genera dinámicamente con `set(reserved.values())`, ni agregar reglas `t_*` porque lo captura `t_IDENTIFICADOR`).*
3. Guardar y verificar con `python herramientas/verificar_lexico_ply.py`.

### C) Permitir comentarios de una sola línea estilo C++ (`// comentario`)
1. Abrir `lexico.py` en la sección 5 (caracteres ignorados).
2. Agregar la función de descarte:
   ```python
   def t_COMMENT_LINE(t):
       r'//[^\n]*'
       pass  # Se descarta hasta el fin de línea
   ```
3. *(Ojo: no sumar `\n` a `lineno` aquí, porque el salto de línea posterior será capturado por `t_newline`).*

### D) Soportar secuencias de escape en cadenas (ej. `\"`, `\'`, `\n`)
1. Modificar la regex de `t_CADENA`:
   ```python
   def t_CADENA(t):
       r'"([^"\n\\]|\\.)*"|\'([^\'\n\\]|\\.)*\''
       return t
   ```
2. Esto permite que una barra invertida `\` escape el carácter siguiente sin cerrar la cadena anticipadamente.

### E) Detectar comentarios de bloque sin cerrar (`/*`) como error léxico
Si el docente pide reportar un comentario de bloque que llega a fin de archivo sin `*/` directamente como error léxico en la línea donde abrió:
1. Agregar una regla de función al final de los comentarios:
   ```python
   def t_COMMENT_UNCLOSED(t):
       r'/\*[\s\S]*'
       errores_lexicos.append({
           'linea': t.lexer.lineno,
           'caracter': '/*',
           'posicion': t.lexpos,
           'mensaje': "comentario de bloque no cerrado"
       })
       t.lexer.skip(len(t.value))
   ```

---

## 11. Resumen en cinco frases

1. El analizador léxico transforma texto plano en un flujo de **tokens tipificados** y limpia caracteres descartables.
2. Usamos el diccionario **`reserved` dentro de `t_IDENTIFICADOR`** para garantizar la regla del patrón más largo y evitar colisiones de palabras clave.
3. En PLY, **las funciones tienen prioridad absoluta sobre las cadenas**; por eso `t_SERIAL_PRINTLN` es una función ubicada antes de `t_IDENTIFICADOR`.
4. El contador **`lineno` se actualiza manualmente** en comentarios multilínea (`count('\n')`) para preservar la exactitud de las líneas de error.
5. Los errores léxicos se registran limpiamente en `t_error` **sin salidas por stdout**, permitiendo que `compilador.py` aplique la **Regla de Oro** del primer error en orden de lectura.
