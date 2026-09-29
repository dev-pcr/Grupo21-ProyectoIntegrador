# Guía de Tokens y Análisis Léxico — Desde Cero
**Para entender `tokens.txt`, cómo funciona y cómo defenderlo**

---

## 1. La idea general: ¿Qué es un token? (Explicado simple)

Imaginá el idioma español. Para leer un texto, primero rompés todo en "palabras": "El perro corre". Cada palabra es una unidad mínima con significado.

En programación pasa exactamente lo mismo:
1. **El Analizador Léxico (`tokens.txt`)**: Reconoce las "palabras" sueltas (los **tokens** como `FLOAT`, `IDENTIFICADOR`, `IGUAL`, `PUNTO_Y_COMA`).
2. **El Analizador Sintáctico (`gramatica.txt`)**: Revisa que esas "palabras" estén ordenadas según las reglas del lenguaje.

> **Token ≈ palabra.** Es la unidad mínima que el lexer entrega al parser. Si el parser habla de "oraciones", el lexer habla de "palabras".

---

## 2. Conceptos clave que tenés que saber

| Concepto | Qué significa | Ejemplo en nuestro proyecto |
| :--- | :--- | :--- |
| **Token** | Una "palabra" que reconoce el lexer. Se escribe en **MAYÚSCULAS** en la primera columna. | `FLOAT`, `IDENTIFICADOR`, `IGUAL`, `PUNTO_Y_COMA`, `SETUP` |
| **Lexema** | El texto exacto que aparece en el código fuente y que produce el token. | `float`, `x`, `=`, `;`, `setup` |
| **Directiva** | Una instrucción especial para el lexer, que no produce un token sino que controla su comportamiento. Empieza con `@`. | `@ignorar` |
| **Patrón (regex)** | La expresión regular que define qué lexemas reconoce cada token. Usa la sintaxis de `re` de Python (la que usa PLY). | `[a-zA-Z_][a-zA-Z0-9_]*`, `\+`, `\/\*[\s\S]*?\*\/` |
| **Precedencia por orden** | Cuando dos tokens empatan en longitud, gana el que está **escrito primero** en el archivo. | `INPUT` aparece antes que `IDENTIFICADOR`, así "INPUT" no se lee como un identificador. |

---

## 3. ¿Cómo está armado `tokens.txt` paso a paso?

Vamos desde lo más estructural (las directivas) hasta lo más concreto (los tokens).

### Nivel 1: Directivas — lo que el lexer descarta o controla

Antes de buscar tokens, el lexer necesita saber qué **ignorar**. Las directivas `@ignorar` definen patrones que se consumen pero **no producen token alguno**.

```text
# descarta: espacios, tabulaciones y retornos de carro
@ignorar [ \t\r]+

# descarta: comentarios de bloque, que empiezan con /* y terminan en el primer */ posterior
@ignorar /\*[\s\S]*?\*/
```

- **¿Por qué `@ignorar`?** Porque el parser no le interesan los espacios ni los comentarios: son "ruido" que separa tokens pero no son tokens en sí.
- **¿Qué pasa con los saltos de línea?** El enunciado dice que el salto de línea lo descarta el "paso 1 del algoritmo" (un mecanismo externo al lexer). Por eso no aparece como `@ignorar` aquí.

> **¿Por qué se escribe así?**  
> Separar la "descartabilidad" (`@ignorar`) de los tokens reales mantiene la gramática limpia: el parser solo recibe lo que realmente importa.

### Nivel 2: Palabras reservadas, tipos, booleanos, constantes y funciones

Estos son tokens que reconocen **palabras exactas** del lenguaje. Son "palabras clave" que **no pueden usarse como identificadores**.

```text
# --- Palabras reservadas ---
SETUP  setup
LOOP   loop
VOID   void

# --- Tipos ---
BOOLEAN  boolean
CHAR     char
FLOAT    float

# --- Booleanos ---
FALSE  false
TRUE   true

# --- Constantes ---
HIGH         HIGH
INPUT        INPUT
INPUT_PULLUP INPUT_PULLUP
LED_BUILTIN  LED_BUILTIN
LOW          LOW
OUTPUT       OUTPUT

# --- Funciones ---
MAP            map
DELAY          delay
SERIAL_PRINTLN Serial\.println
```

#### Explicación detallada con ejemplos:

1. **¿Por qué están antes de `IDENTIFICADOR`?**  
   Porque el orden importa: si `IDENTIFICADOR` estuviera primero, palabras como `setup` o `INPUT` se leerían como identificadores. Al ponerlas primero, el lexer reconoce la palabra exacta y la etiqueta con su token correspondiente.

2. **¿Por qué `INPUT_PULLUP` aparece después que `INPUT`?**  
   Por **prelongitud**: `INPUT_PULLUP` es más largo que `INPUT`. Aunque `INPUT` aparece antes en el archivo, PLY resuelve los empates de longitud eligiendo el patrón que reconoce **más caracteres**. Así, en el texto `INPUT_PULLUP` el lexer lee todo de una vez y produce `INPUT_PULLUP`, no `INPUT` seguido de un identificador.

3. **`SERIAL_PRINTLN` usa `\.`**  
   El punto es un carácter especial en regex, así que se escapa con `\` para que coincida literalmente con `Serial.println`.

### Nivel 3: Signos y operadores

Son los símbolos que estructuran las sentencias y expresiones. Cada uno tiene su propio token:

```text
# --- Signos y operadores ---
PARENTESIS_IZQ   \(
PARENTESIS_DER   \)
LLAVE_IZQ        \{
LLAVE_DER        \}
COMA             ,
PUNTO_Y_COMA     ;
IGUAL            =
SUMA_IGUAL       \+=
RESTA_IGUAL      -=
SUMA             \+
RESTA            -
MULTIPLICACION   \*
DIVISION         /
```

#### ¿Por qué están en este orden?

El orden **dentro de esta sección** importa para resolver ambigüedades de longitud:

- **`SUMA_IGUAL` (`\+=`) aparece antes que `SUMA` (`\+`)**: si vieras `+=`, el lexer debe reconocerlo como un solo token (`SUMA_IGUAL`), no como `SUMA` seguido de `IGUAL`. Al poner `\+=` primero, gana el patrón más largo.
- **`RESTA_IGUAL` (`-=`) aparece antes que `RESTA` (`-`)**: igual razón.

> **Regla de oro:** siempre que un símbolo es **prefijo** de otro (como `-` es prefijo de `-=`), el más largo va primero.

### Nivel 4: Literales — números y cadenas

```text
# --- Literales ---
CADENA  "[^"\n]*"|'[^'\n]*'
DECIMAL [0-9]+\.[0-9]+
ENTERO  [0-9]+
IDENTIFICADOR [a-zA-Z_][a-zA-Z0-9_]*
```

#### ¿Por qué `DECIMAL` aparece antes que `ENTERO`?

Por **prelongitud**: `3.25` contiene `3` (que matchearía `ENTERO`) y `3.25` (que matchea `DECIMAL`). Al poner `DECIMAL` primero, el lexer reconoce la cadena más larga: `3.25` como `DECIMAL`, no como `ENTERO` seguido de un punto.

#### ¿Por qué `CADENA` aparece antes que `IDENTIFICADOR`?

Aunque no empaten directamente (una cadena empieza con `"` o `'` y un identificador con letra o `_`), se mantiene el orden de "cosas más específicas primero".

### Nivel 5: Identificador — el último token

```text
IDENTIFICADOR [a-zA-Z_][a-zA-Z0-9_]*
```

- Es el **"catch-all"**: reconoce cualquier nombre que no haya sido reconocido por un token anterior.
- Por eso **va al final** de todo: si está al principio, todo lo que empiece con letra se leería como identificador, y perderíamos `SETUP`, `FLOAT`, `map`, etc.

---

## 4. Reglas estrictas que pide la cátedra y que cumplimos al 100%

1. **Orden por longitud (prelongitud):** Cuando un patrón es prefijo de otro (`INPUT` vs `INPUT_PULLUP`, `-` vs `-=`), el más largo va primero o PLY lo resuelve por longitud máxima. En ambos casos, el token correcto gana.

2. **Palabras clave antes que `IDENTIFICADOR`:** Todas las palabras reservadas, tipos, booleanos, constantes y funciones están **antes** de `IDENTIFICADOR` para que no colisionen.

3. **Tokens en MAYÚSCULAS:** Usamos exactamente los nombres en mayúsculas para los tokens (`SETUP`, `FLOAT`, `IDENTIFICADOR`, etc.), que luego la gramática consume.

4. **Sin operador unario:** El guión medio `-` solo aparece como `RESTA` (binario) o dentro de `RESTA_IGUAL` (`-=`). No hay token para `-5` como número negativo: `-5` se lee como `RESTA` + `ENTERO`, y la gramática rechaza esa secuencia.

5. **`SERIAL_PRINTLN` respeta la sintaxis real:** Se escribe `Serial\.println` porque en Arduino el método es `Serial.println` (con punto). El patrón escapa el punto para que coincida literalmente.

6. **Comentarios de bloque no anidados:** `/\*[\s\S]*?\*/` usa un cuantificador no greedy (`*?`) que se detiene en el **primer** `*/`, evitando que un comentario "coma" el resto del archivo.

7. **`CADENA` no permite secuencias de escape:** El patrón `"[^"\n]*"` solo reconoce texto entre comillas sin diagonales invertidas especiales. Un `\n` dentro de una cadena sería un error léxico.

8. **`DECIMAL` exige dígitos a ambos lados del punto:** `[0-9]+\.[0-9]+` rechaza `3.` (sin dígitos decimales) y `.5` (sin parte entera). Estos casos deben escribirse como `3.0` o `0.5`.

---

## 5. ¿Cómo probás que `tokens.txt` funciona?

Tenés en el proyecto un script automático creado especialmente para verificar la parte léxica:

### Paso 1: Abrir la terminal en la carpeta del proyecto
```powershell
cd "c:\Users\pablo\Desktop\UCASAL 26 NOTEBOOK 2 SEM\CO\Grupo21-ProyectoIntegrador"
```

### Paso 2: Ejecutar el verificador léxico
```powershell
python herramientas/verificar_lexico.py
```

### Qué hace este script cuando lo corrés:
1. Lee `tokens.txt` y construye el lexer con PLY.
2. Evalúa los **9 casos públicos de la cátedra** (los 3 válidos dan `OK`, los 3 léxicos dan `ERROR LEXICO` y los 3 sintácticos dan `ERROR SINTACTICO`).
3. Evalúa los **172 casos de prueba propios** de `pruebas-grupo/`.
4. Si todo está perfecto, te muestra en verde:
   `Resultado final: TODO CORRECTO (100% OK)`

---

## 6. Resumen de comandos útiles para recordar

```powershell
# Probar la parte léxica (tu tokens.txt)
python herramientas/verificar_lexico.py

# Probar la parte sintáctica (tu gramatica.txt)
python herramientas/verificar_sintactico.py

# Subir cambios a GitHub
git add .
git commit -m "Mensaje"
git push
```
