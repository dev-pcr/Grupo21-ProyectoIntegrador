# Resumen del trabajo — Entrega 1

Estado del trabajo hecho hasta el 2026-09-29: `tokens.txt` está escrito y probado, y hay una suite de 173 casos propios que lo verifica con un script (más los 9 casos públicos). Este documento existe para que puedas retomar el trabajo sin preguntar qué hay y por qué.

## Qué hay en el repo

| Archivo / carpeta | Qué es |
| --- | --- |
| `tokens.txt` | **Entregable.** 34 tokens + 2 directivas `@ignorar`, en notación de la sección 8.1, con `# descripción:` y `# ejemplos:` en cada token. |
| `herramientas/verificar_lexico.py` | Analizador de prueba: implementa el algoritmo de la sección 8.1 y evalúa todos los `esperado.csv` del repo. |
| `herramientas/generar_pruebas.py` | Genera la suite propia. Si querés cambiar un caso, se cambia ahí y se regenera. |
| `casos/` | Los 9 casos públicos de la cátedra. **No se toca.** |
| `pruebas-grupo/` | Los 173 casos propios (173 `.txt` + `esperado.csv`). |
| `Historico.md` | Registro de dudas del equipo. Hay dos dudas abiertas (ver más abajo). |

## Cómo correrlo

```bash
python herramientas/generar_pruebas.py    # regenera pruebas-grupo/ (opcional)
python herramientas/verificar_lexico.py   # corre todo
```

Salida esperada: `33/33` micro-pruebas + `34/34` cobertura de tokens + `9/9` casos públicos + `173/173` propios → `TODO CORRECTO`, exit code 0.

## Qué cubre la suite propia

| Grupo | Cantidad | Qué prueba |
| --- | --- | --- |
| `ok-*` | 43 | Programas válidos: construcciones del apartado D, definiciones en cualquier orden y cantidad (incluidas dos idénticas), programa completo estilo Arduino, tipos con y sin inicializador, precedencia y asociatividad por la izquierda, paréntesis anidados y llamadas anidadas, todos los tipos de operando en una expresión, cadenas (ambos delimitadores, vacías, con la otra comilla adentro, con `ñ`/`€`, con `{;}`, `/* */`, `//` y `\` adentro), comentarios (multilínea, `/**/`, entre tokens, entre `void` y `setup`, consecutivos, al final del archivo), formato libre con tabs, sin espacios, con saltos de línea dentro de una producción, sin salto de línea final, CRLF y solo-CR, identificadores límite (`_`, `__`, `_1`, nombres largos) y parecidos a palabras reservadas (`loopx`, `HIGHWAY`, `INPUTX`, `SETUP`, `voidx`), sensibilidad a mayúsculas, decimales y enteros con formas raras (`00.00`, `0.0`, 20 dígitos), keywords pegadas a operadores. |
| `lex-*` | 47 | Error léxico con **línea exacta**: letra con tilde, comillas sin cerrar (doble, simple, multilínea, `"""`, con `\` que no escapa), `3.`, `.5`, `1..2`, `1.2.3`, `!`, `@`, `[`, `]`, `?`, `€`, `#`, `&`, `%`, `<`, `>`, form feed (no se descarta), tab vertical, espacio no separable U+00A0 (el de Word/Excel, que no entra en `[ \t\r]+`), `Serial . println`, `serial.println`, `xSerial.println` (prefijo delante), `Serial.print(1)` y `Serial.begin(9600)` (esas funciones no existen: el punto queda suelto), `'abc'def'` (comillas de distinto tipo), punto suelto, gana el primero con dos errores en la misma línea, error tras comentario (una línea, multilínea, dos seguidos, contando saltos), error tras líneas en blanco, error dentro de un bloque, error al final de una línea cargada, error tras una cadena que contiene `/*` y `*/`, error con y sin salto de línea final, error en CRLF y tras comentario multilínea con CRLF, error en líneas 1, 2, 3, 4, 5 y 12. |
| `sin-*` | 83 | Error sintáctico (hasta ahora solo se exige que **lexee sin error**): archivo vacío, solo espacios, solo comentarios, **solo definiciones (duda abierta)**, bloque vacío, definiciones mal formadas (`setup` sin `void`, sin llaves, sin paréntesis, con argumentos, con paréntesis o llave de más), operadores unarios `+` y `-` (en asignación y en argumento), `delay()`/`map()` sin argumentos, `delay`/`Serial.println` usados como operando o como argumento, `Serial.printlnx`, `map;`, falta de `;` y de `}` (incluido corte de archivo en expresión, llamada y definición), `==`, `*=`, `int`, `0x1F`, `1abc`, `1e5` (notación exponencial: son dos piezas pegadas), número pegado a identificador, definiciones anidadas dentro de un bloque, `//`, comentario sin cerrar, comentario no anidado, `*/` suelto, paréntesis sin cerrar/sobrante/vacío, dos operadores seguidos, dos operandos sin operador, doble asignación, coma dentro de una expresión, coma en una declaración (`float x, y;`), `+=` con espacio, `+=` en una declaración (`float x += 1;`), `x++` (no existe `++`), `pinMode(...)` (función inexistente: identificador seguido de `(`), argumento que es una asignación, cadena o número como sentencia, nombre reservado como variable (`HIGH`, `delay`), tipo en medio de una expresión, `mi-var` (el guion no es parte del identificador), sentencia incompleta al final, y EOF con líneas en blanco y comentario después del último token (la línea esperada es la del último token, no la del cierre del archivo). |

Los casos `sin-*` traen una línea calculada con la regla 7.2 (línea del primer token con el que el programa ya no puede ser válido; si termina el archivo, línea del último token; vacío o solo comentarios = línea 1), pero el script todavía no la evalúa: eso se activa cuando exista `gramatica.txt`.

## Decisiones de `tokens.txt` que te afectan en `gramatica.txt`

1. **Usá exactamente estos nombres de token** (si los escribís distinto, PLY no los va a encontrar):

   ```
   SETUP LOOP VOID BOOLEAN CHAR FLOAT FALSE TRUE
   HIGH INPUT INPUT_PULLUP LED_BUILTIN LOW OUTPUT
   MAP DELAY SERIAL_PRINTLN
   PARENTESIS_IZQ PARENTESIS_DER LLAVE_IZQ LLAVE_DER
   COMA PUNTO_Y_COMA IGUAL SUMA_IGUAL RESTA_IGUAL
   SUMA RESTA MULTIPLICACION DIVISION
   CADENA DECIMAL ENTERO IDENTIFICADOR
   ```

2. **`delay` y `Serial.println` no devuelven valor**: solo sentencia, nunca dentro de una expresión (apartado E). `map` sí devuelve valor: puede ser operando o sentencia.
3. **No hay operadores unarios** (`-5` y `+5` no son expresiones), **no hay llamadas sin argumentos**, y **`==` no es un token** (son dos `IGUAL`).
4. **`Serial.println` es un solo token** sin espacios alrededor del punto.
5. El orden del archivo no cambia el léxico, pero sí documenta los desempates: palabras reservadas, tipos, booleanos, constantes y funciones van antes de `IDENTIFICADOR`; `DECIMAL` gana sobre `ENTERO` por longitud.

## Dudas abiertas (están en `Historico.md`)

1. **Cuerpos vacíos**: `void setup() { }`. El apartado D escribe `{ sentencias }` y E define sentencias como "una o más", así que la lectura estricta los rechaza con error sintáctico en la llave que cierra. Afecta a `sin-03-bloque-vacio-setup` y `sin-04-bloque-vacio-loop`.
2. **Programa con solo definiciones**: el apartado C dice "un programa es una secuencia de una o más sentencias" y que las definiciones aparecen "además de sentencias". Lectura estricta: un archivo con solo `void setup() { … }` / `void loop() { … }` y ninguna sentencia arriba no sería válido (error al EOF). Es el formato más común de Arduino, pero los tres casos válidos públicos tienen sentencias en el nivel superior. Afecta a `sin-59-solo-definiciones`.

**Convendría consultar las dos en el foro** antes de que tu gramática decida algo distinto.

## Decisiones que quedan para Entrega 2 (`compilador.py`)

1. **Leer los tokens bajo demanda, no tokenizar todo el archivo antes de parsear.** La línea 168 del enunciado dice textual: *"Si hay errores, se informa el primero en el orden de lectura del programa"*. Si el léxico recorre el archivo completo de una, un error sintáctico en la línea 1 queda tapado por un error léxico que está más abajo: se informaría el equivocado. La lectura correcta es el sintáctico pidiendo tokens de a uno, y el léxico produciéndolos solo cuando se los piden.
2. **Casos mixtos (error sintáctico + error léxico en el mismo archivo): fuera de la suite por ahora.** `verificar_lexico.py` solo evalúa la fase léxica (para un `ERROR SINTACTICO` exige que no haya error léxico en ningún lado), así que hoy los marcaría como FALLO rojo injusto. Van en una carpeta aparte cuando exista `compilador.py` (por ejemplo `pruebas-mixtos/`). La respuesta correcta según la línea 168 es siempre el error de más arriba en el orden de lectura:

   | Programa | Salida correcta |
   | --- | --- |
   | `x = = 1;` / `y = ñ;` | `ERROR SINTACTICO linea 1` (el sintáctico de la línea 1 va antes que el léxico de la línea 2) |
   | `void setup() {` / `  delay(1 2);` / `  $x;` / `}` | `ERROR SINTACTICO linea 2` (va antes que el léxico de la línea 3) |
   | `x = @ 1;` | `ERROR LEXICO linea 1` (para seguir decidindo hay que leer el token que viene y ahí cae el análisis) |

3. **BOM UTF-8**: leer con `encoding="utf-8-sig"` (quita el BOM si está y no toca nada si no está). Con `utf-8` común, un archivo con BOM daría `ERROR LEXICO linea 1` por el carácter U+FEFF — que es lo que hace hoy el verificador de prueba. Definirlo antes de entregar.
4. **Cobertura de tokens**: `verificar_lexico.py` ya valida que los 34 tokens de `tokens.txt` aparezcan al menos una vez en algún caso `ok-*` (`34/34`). Si agregás tokens nuevos, la suite te avisa.
5. **Límite de 10 segundos** (apartado de la Entrega 2): los casos actuales son chicos, así que no cubren gramáticas con recursión improductiva ni archivos grandes. Antes de entregar, probá con un programa de miles de líneas y, si querés, con casos generados automáticamente para estresar el lexer.

## Checklist

- [x] `gramatica.txt` usa los nombres de token de arriba, tal cual.
- [x] Corres `python herramientas/verificar_lexico.py` y da `TODO CORRECTO`.
- [x] `herramientas/verificar_sintactico.py` implementado y pasa al 100% (`TODO CORRECTO`).
- [x] Se resuelven las dos dudas de `Historico.md` y se regenera `pruebas-grupo/`.
- [x] Con `gramatica.txt` funcionando, se valida la **línea** de los 82 casos `sin-*` y se confirma que los 43 `ok-*` son sintácticamente válidos.
- [ ] En Entrega 2: tokens leídos bajo demanda, `utf-8-sig`, y los casos mixtos en su carpeta aparte (sección anterior).
- [ ] Falta el `README` del repo (figura en `cronograma-entrega1-grupo21.md`).

