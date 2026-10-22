# Entrega 2 — Parte de Pablo: Analizador Sintáctico (guía de estudio para el oral)

**Grupo N.º 21 — Compiladores 2026 — UCASAL**
**Archivo principal:** `sintactico.py` · **Verificación:** `herramientas/verificar_sintactico_ply.py`

> Este documento explica **qué se hizo y por qué**, en lenguaje conceptual, para que Emi y Pablo puedan responder en la defensa oral y hacer la modificación en vivo. No hace falta memorizar código: hay que entender las ideas.

---

## 1. ¿Qué hace el analizador sintáctico y dónde encaja?

El compilador tiene dos etapas que trabajan en cadena:

```
Código fuente  ──►  LÉXICO (Emi)  ──►  tokens  ──►  SINTÁCTICO (Pablo)  ──►  OK / ERROR SINTACTICO linea N
(texto plano)       lexico.py         (piezas)       sintactico.py
```

- **Analizador léxico:** lee caracteres y los agrupa en **tokens** (`float`, `x`, `=`, `1.5`, `;`). Detecta caracteres inválidos.
- **Analizador sintáctico:** recibe los tokens y verifica que estén **en un orden válido según la gramática**. No mira caracteres: mira tokens.
- **Importante:** nuestro sintáctico solo **valida la forma** del programa. No calcula nada, no verifica tipos, no comprueba si una variable fue declarada (eso sería análisis semántico, fuera del alcance).

**Token vs. lexema:** el *lexema* es el texto concreto (`edad`), el *token* es la categoría (`IDENTIFICADOR`). La gramática trabaja con categorías, no con textos.

---

## 2. La gramática del lenguaje (qué se acepta)

Es una **gramática libre de contexto** (GLC) escrita en `gramatica.txt` y traducida a funciones `p_*` de PLY. Cada función = una o más producciones.

| Concepto | Qué dice la gramática | Ejemplo válido |
| :-- | :-- | :-- |
| **Programa** | Una o más piezas (`elemento`), cada una es una sentencia suelta o una definición | `float x = 1;` seguido de `void loop(){...}` |
| **Definición** | `void setup()` o `void loop()` con llaves y **al menos una sentencia** | `void setup() { map(1); }` |
| **Declaración** | tipo + identificador, con o sin `= expresión`, termina en `;` | `float edad = 22.0;` |
| **Asignación** | `=`, `+=` o `-=` | `edad += 1.0;` |
| **Llamada** | `delay(...)`, `Serial.println(...)`, `map(...)` con ≥ 1 argumento | `Serial.println("hola");` |
| **Expresión** | sumas/restas de términos; términos son productos/divisiones de factores | `1 + 2 * (3 - x)` |
| **Factor** | identificador, número, `( expresión )`, `map(...)`, cadena, `true/false`, constante Arduino | `LED_BUILTIN` |

**Qué NO acepta (y por qué es error):**
- Archivo vacío o solo comentarios → `programa` exige al menos un elemento.
- Bloque vacío `void setup() { }` → `sentencias` exige al menos una.
- Signo unario `-5` → no existe producción con operador unario.
- `delay()` o `Serial.println()` sin argumentos → `argumentos` exige al menos una expresión.
- `delay(...)` o `Serial.println(...)` **dentro** de una expresión → solo `map` devuelve valor y puede ser operando.
- `x++`, `x *= 2`, `==`, `//` → no existen en el subconjunto.
- Definiciones anidadas, `void` sin cuerpo, parámetros en `setup()`.

---

## 3. Idea central 1: precedencia por **gramática estratificada** (sin tabla `precedence`)

**Problema:** en `2 + 3 * 4` ¿se hace primero la suma o la multiplicación? Una gramática ingenua `expresion → expresion + expresion | expresion * expresion | número` es **ambigua**: admite dos árboles distintos (`(2+3)*4` y `2+(3*4)`).

**Dos formas de resolverlo:**
1. Tabla `precedence` de PLY: se le "avisa" al generador qué operador pesa más. Es un parche externo.
2. **Estratificar la gramática** (lo que hicimos): escribir niveles, de menor a mayor precedencia.

```
expresion → expresion + termino | expresion - termino | termino     ← nivel 1: + y −
termino   → termino * factor    | termino / factor    | factor      ← nivel 2: * y /
factor    → número | identificador | ( expresion ) | ...            ← nivel 3: operandos
```

**Por qué funciona:** para que aparezca un `*` hay que estar **más abajo** en el árbol que un `+`. Entonces `3 * 4` se agrupa primero como un `termino` y recién después se suma. Los paréntesis "reinician" el nivel: `( expresion )` es un `factor`, por eso `(2+3)*4` funciona.

**Árbol de `2 + 3 * 4`:**
```
        expresion
       /    |    \
 expresion  +   termino
     |         /   |   \
  termino  termino * factor
     |        |        |
  factor   factor      4
     |        |
     2        3
```

**Asociatividad izquierda:** la recursión está a la **izquierda** (`expresion → expresion + termino`). Así `5 - 3 - 2` se interpreta `(5 - 3) - 2` y no `5 - (3 - 2)`.

**Ventaja:** 0 conflictos, no depende de un mecanismo externo y es el mismo modelo que la cátedra (`calcyacc.py`).

---

## 4. Idea central 2: conflictos shift/reduce y reduce/reduce

PLY genera un analizador **LALR(1)**: lee tokens de izquierda a derecha, usa **1 token de anticipación** y una **pila**. En cada paso decide entre:

- **Shift (desplazar):** meter el token en la pila (seguir leyendo).
- **Reduce (reducir):** reemplazar en la pila lo que coincide con el lado derecho de una regla por su lado izquierdo.

Un **conflicto** ocurre cuando, con el mismo estado y el mismo token, hay dos acciones posibles:
- **shift/reduce:** no sabe si seguir leyendo o reducir (típico de gramáticas ambiguas, ej. la de expresiones sin estratificar).
- **reduce/reduce:** dos reglas distintas podrían reducirse a la vez.

**Resultado en nuestro proyecto:** `parser.out` (el archivo que PLY escribe con la tabla de estados) reporta **0 conflictos shift/reduce y 0 reduce/reduce**. Lo comprobamos con `auditar_conflictos()`. Eso demuestra que la gramática es **no ambigua** para LALR(1).

---

## 5. Idea central 3: blindaje ante fin de archivo prematuro (EOF)

**El problema:** cuando el programa termina "antes de tiempo" (por ejemplo falta una `}` o un `;` final), PLY llama a `p_error(p)` con **`p = None`**, porque no hay ningún token que culpar. Los ejemplos de la cátedra hacen `p.lineno` sin controlar y **explotan con `AttributeError`**.

**Nuestra solución, en dos partes:**
1. `p_error` pregunta explícitamente `if p is None` y trata el caso aparte.
2. Una clase **`TrackingLexer`** envuelve al lexer: cada vez que el parser pide un token, la clase lo pasa y **anota su número de línea**. Si después llega el EOF, usamos la línea del **último token real leído**.

**Ejemplos (de `pruebas-grupo/`):**
| Caso | Contenido | Línea informada | Por qué |
| :-- | :-- | :-: | :-- |
| `sin-14` | `void setup() {` / `float x = 1;` / (línea vacía) | **2** | último token real: el `;` de la línea 2 |
| `sin-82` | `x = 1` / vacío / `/* fin */` | **1** | el comentario no genera tokens; el último es `1` |
| `sin-53` | `map(1);` / `void` | **2** | último token: `void` |
| `sin-01` | archivo vacío | **1** | no hubo tokens: se usa el valor por defecto (1) |

---

## 6. Idea central 4: "el primer error gana"

- PLY pide tokens **a demanda**: el parser avanza token por token.
- En el primer error, `p_error` **guarda** el error (línea y mensaje) y **lanza una excepción** para cortar el análisis. No hay recuperación de errores.
- Consecuencia: todo lo que viene después del primer error ni siquiera se analiza. Así se cumple la "regla de oro": se informa el **primer error en orden de lectura**.

**Coordinación con el léxico (Emi):** el lexer, ante un carácter inválido, lo **registra** en `lexico.errores_lexicos` y sigue (no imprime). Luego `compilador.py` compara: si la línea del error léxico es **≤** la del sintáctico, informa el léxico; si no, el sintáctico; si no hay errores, `OK`. (Esa integración es tarea conjunta, aún pendiente.)

---

## 7. Cómo está organizado `sintactico.py`

| Sección | Qué contiene | Para qué sirve |
| :-- | :-- | :-- |
| 1–5 | Funciones `p_*` (reglas gramaticales) | Cada docstring es una producción. El cuerpo es `pass`: solo validamos. |
| 6 | `p_error` | Registra el primer error; maneja `p is None`. |
| 7 | `crear_parser()` | Construye el parser con `write_tables=False` (no genera `parsetab.py`) y `debug=False` (no escribe `parser.out` cada vez). |
| 8 | `TrackingLexer` | Adaptador que memoriza la línea del último token. |
| 9 | `analizar(codigo)` | Función de alto nivel: devuelve `(True, None)` o `(False, {linea, mensaje})`. Reinicia el estado en cada llamada. |
| 10 | `auditar_conflictos()` | Regenera `parser.out` y cuenta conflictos. |

**¿Por qué las funciones `p_*` tienen `pass`?** PLY necesita la función solo por su docstring (la regla). Como no construimos árbol ni calculamos valores, no hay nada más que hacer. (En `calcyacc.py` de la cátedra sí calculan el resultado; nosotros no lo necesitamos.)

**Dos detalles de PLY que conviene saber:**
- El **símbolo inicial** es la **primera regla** definida (`programa`).
- Los nombres de tokens de la gramática deben coincidir exactamente con la lista `tokens` de `lexico.py`.

---

## 8. Cómo lo probamos

- **Script:** `python herramientas/verificar_sintactico_ply.py` (usar `python`; con `py` el *shebang* puede elegir otro intérprete sin PLY).
- **Qué hace:** corre el parser real contra los casos `ok-*` y `sin-*` de `pruebas-grupo/` y compara con `esperado.csv`:
  - `ok-*` → debe dar OK y sin errores léxicos.
  - `sin-*` → debe fallar **y** la línea debe coincidir exactamente.
- **Resultados:**
  - **0 conflictos** shift/reduce y reduce/reduce.
  - **151/151** casos aprobados (100% de éxito).
  - La precedencia de `t_SERIAL_PRINTLN` quedó resuelta definiéndola como función antes de `t_IDENTIFICADOR` en `lexico.py` (ver detalle en `log-de-errores.md`).

---

## 9. Preguntas probables del oral (con respuesta corta)

**1. ¿Qué diferencia hay entre análisis léxico y sintáctico?**
El léxico agrupa caracteres en tokens y detecta símbolos inválidos; el sintáctico verifica que la secuencia de tokens respete la gramática.

**2. ¿Qué es una gramática libre de contexto?**
Un conjunto de producciones `A → α` donde el lado izquierdo es un único no terminal. Describe la estructura anidada del lenguaje (paréntesis, bloques, expresiones).

**3. ¿Cómo resolvieron la precedencia de operadores?**
Estratificando la gramática en tres niveles (`expresion`, `termino`, `factor`). Los operadores de mayor precedencia viven en un nivel inferior, por lo que se agrupan antes. No usamos tabla `precedence`.

**4. ¿Por qué recursión a la izquierda?**
Da asociatividad izquierda (`a - b - c = (a - b) - c`) y es la forma natural para parsers LR/LALR, que la manejan sin problemas (los descendentes recursivos no).

**5. ¿Qué es un conflicto shift/reduce? ¿Tienen alguno?**
Cuando el parser, con el mismo estado y token, puede desplazar o reducir. Es síntoma de ambigüedad. Tenemos 0, verificado en `parser.out`.

**6. ¿Qué es LALR(1)?**
Look-Ahead LR con 1 token de anticipación: un parser ascendente (construye el árbol de las hojas hacia la raíz) que fusiona estados de LR(1) con el mismo núcleo para tener tablas más chicas.

**7. ¿Qué pasa si el archivo termina antes de tiempo?**
PLY llama `p_error(None)`. Lo controlamos con `if p is None` y usamos la línea del último token, que guarda el `TrackingLexer`.

**8. ¿Por qué `delay` y `Serial.println` no pueden estar dentro de una expresión pero `map` sí?**
Porque en la gramática solo `llamada_valor` (`map`) aparece como `factor`. `delay` y `Serial.println` no devuelven valor, así que solo son sentencias.

**9. ¿Qué es `parser.out`?**
El archivo de depuración de PLY con las producciones numeradas, los estados LALR, las acciones y los conflictos. Lo generamos con `auditar_conflictos()`.

**10. ¿Para qué sirve `write_tables=False`?**
Evita que PLY genere/lea `parsetab.py` (caché de la tabla). Así la corrida es siempre limpia y no queda un archivo viejo desincronizado con la gramática.

**11. ¿Qué es un símbolo terminal y uno no terminal?**
Terminales: tokens (`IDENTIFICADOR`, `PUNTO_Y_COMA`). No terminales: categorías que se expanden con reglas (`expresion`, `sentencia`).

**12. ¿Por qué tu parser no verifica tipos ni variables declaradas?**
Eso es análisis semántico. El enunciado solo pide léxico y sintáctico.

---

## 10. Modificaciones en vivo — cómo encararlas

**A) Agregar un operador, p. ej. `%` (módulo)**
1. `tokens.txt` y `lexico.py`: nuevo token `MODULO` con regex `%`.
2. `gramatica.txt` y `sintactico.py`: agregar `termino MODULO factor` en `termino` (misma precedencia que `*` y `/`).
3. Regenerar y correr `verificar_sintactico_ply.py`: seguir en 0 conflictos.
   - Si se pide otra precedencia (p. ej. menor que `+`), se agrega **un nivel nuevo** de la jerarquía.

**B) Permitir `delay();` sin argumentos**
- Opción 1: agregar la alternativa `DELAY PARENTESIS_IZQ PARENTESIS_DER` a `llamada_sin_valor`.
- Opción 2: crear `argumentos_opt → argumentos | ε`. Ojo: PLY escribe la regla vacía como `empty :` y puede generar conflictos; verificar en `parser.out`.

**C) Aceptar bloques vacíos**
- Cambiar `sentencias` por una versión que admita vacío, o agregar las alternativas `VOID SETUP ( ) { }` y `VOID LOOP ( ) { }`.
- Impacto: `sin-03`, `sin-04` y `sin-99` pasarían a ser válidos; actualizar `esperado.csv`.

**Receta general:** *cambiar gramática → cambiar el `p_*` correspondiente (si hace falta, el lexer) → correr la suite → mirar los conflictos → actualizar `esperado.csv` si cambió el comportamiento esperado.*

---

## 11. Resumen en cinco frases

1. El sintáctico valida que los tokens respeten la gramática; no calcula ni verifica tipos.
2. La precedencia se logra con **tres niveles** de gramática (`expresion → termino → factor`), no con tabla externa.
3. PLY genera un parser LALR(1); en `parser.out` comprobamos **0 conflictos**.
4. Ante un EOF prematuro (`p is None`), el `TrackingLexer` nos da la línea del último token real.
5. El **primer error corta el análisis**, y `compilador.py` decide entre léxico y sintáctico comparando líneas.
