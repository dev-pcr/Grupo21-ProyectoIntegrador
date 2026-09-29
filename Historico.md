### Registros de dudas

> **Fecha:**
> [YYYY-MM-DD].
> **Persona:**
> Emiliano o Pablo
>
> **Titulo:**
> Titulo corto que resuma la informacion.
>
> **Asunto:**
> Descripción clara y concreta de la duda, obervacion u otra cosa.
>
> **Respuesta:**
> _(Completar cuando se resuelva)_

---

> **Fecha:**
> 2026-09-29.
> **Persona:**
> Emiliano
>
> **Titulo:**
> Bloques vacíos en setup() y loop()
>
> **Asunto:**
> El apartado D escribe las definiciones como `void setup ( ) { sentencias }` y el apartado E define sentencias como "una o más sentencias de las de esta sección, una detrás de otra". Por una lectura estricta, el cuerpo vacío `void setup() { }` no sería válido: el error sintáctico caería en la línea de la llave que cierra el bloque. ¿Es así, o un cuerpo vacío está permitido? Afecta a los casos `sin-03-bloque-vacio-setup` y `sin-04-bloque-vacio-loop` de `pruebas-grupo/`.
>
> **Por qué existe esta duda y por qué no se corrigió:**
> No es un error de `tokens.txt` ni de los casos: el problema existe **porque falta `gramatica.txt`**. `tokens.txt` solo define el léxico (qué es un token); si el cuerpo vacío vale o no es una regla sintáctica que se decide al escribir la gramática, y esa gramática todavía no existe. Por eso no hay nada que corregir todavía: los casos quedaron con la lectura estricta del anexo y se ajustan recién cuando se defina `gramatica.txt` (o responda la cátedra en el foro).
>
> **Respuesta:**
> Resuelto según la especificación formal: `sentencias` exige al menos una sentencia (no se admiten alternativas vacías según la sección 8.2), por lo que los bloques vacíos dan `ERROR SINTACTICO` en la llave de cierre. Se valida correctamente en `sin-03` y `sin-04`.

---

> **Fecha:**
> 2026-09-29.
> **Persona:**
> Emiliano
>
> **Titulo:**
> Programa que solo tiene definiciones
>
> **Asunto:**
> El apartado C dice "Un programa es una secuencia de una o más sentencias" y que en el nivel superior "además de sentencias, pueden aparecer las definiciones". Por una lectura estricta, un archivo que contiene únicamente `void setup() { … }` y/o `void loop() { … }`, sin ninguna sentencia en el nivel superior, no sería programa válido: el error caería al EOF, en la línea de la última llave. Es el formato más común de Arduino, pero los tres casos válidos públicos tienen sentencias en el nivel superior y ninguno es "solo definiciones". ¿Es así o las definiciones también valen como programa completo? Afecta al caso `sin-59-solo-definiciones` de `pruebas-grupo/`.
>
> **Por qué existe esta duda y por qué no se corrigió:**
> Igual que la anterior: no es un error de `tokens.txt` ni de los casos, sino que el problema existe **porque falta `gramatica.txt`**. Qué cuenta como "programa completo" es una regla sintáctica y la gramática que la define todavía no existe. No se corrigió porque no hay nada que corregir hasta que `gramatica.txt` defina la regla (o responda la cátedra en el foro); hasta entonces el caso `sin-59-solo-definiciones` queda con la lectura estricta del anexo.
>
> **Respuesta:**
> En la gramática formal, el nivel superior está compuesto por `elemento -> sentencia | definicion` con `programa -> elemento | programa elemento`. Esto permite programas formados solo por definiciones (como en los casos `ok-02`, `ok-04`, `ok-18`, `ok-26`, `ok-43`), solo por sentencias (`ok-05`), o una mezcla de ambas (`ok-03`, `ok-35`). Se eliminó el caso redundante `sin-59`.

---

> **Fecha:**
> 2026-09-29.
> **Persona:**
> Pablo
>
> **Titulo:**
> Rol de setup(), loop() y operadores de asignación
>
> **Asunto:**
> Aclaración sobre el comportamiento y ciclo de vida de las funciones principales en Arduino y cómo operan las asignaciones en la gramática.
>
> **Respuesta:**
> - `setup()`: Se ejecuta una sola vez al encender/reiniciar el microcontrolador para inicializar variables y datos.
> - `loop()`: Se ejecuta de manera continua e infinita mientras la placa permanezca encendida, procesando sentencias y modificando el estado del sistema.
> - **Asignaciones (`=`, `+=`, `-=`):** `=` asigna un valor directo, mientras que `+=` y `-=` incrementan o decrementan el valor de la variable de forma acumulativa.

---

> **Fecha:**
> 2026-09-29.
> **Persona:**
> Pablo
>
> **Titulo:**
> Comportamiento gramatical de funciones (delay, Serial.println, map)
>
> **Asunto:**
> Reglas sintácticas y diferencia entre funciones que devuelven valor y las que no dentro de la gramática.
>
> **Respuesta:**
> - `delay()` y `Serial.println()`: **NO devuelven valor**. Solo pueden usarse como sentencias independientes finalizadas en `;` (ej: `delay(1000);`, detiene a arduino por 1 seg). Intentar usarlas dentro de una expresión o asignación (ej: `x = delay(100);`) produce error sintáctico. En el caso de serial print imprime un mensaje en el puerto serial. 
> - `map()`: **SÍ devuelve valor**. Se puede usar tanto dentro de expresiones matemáticas/asignaciones (ej: `x = map(...);`) como de sentencia suelta. Este sirve para transformar rangos, por ejemplo de 1 a 123 -> 0% a 100%

---

> **Fecha:**
> 2026-09-29.
> **Persona:**
> Pablo
>
> **Titulo:**
> Constantes reservadas de Arduino (HIGH, LOW, INPUT, OUTPUT, INPUT_PULLUP, LED_BUILTIN)
>
> **Asunto:**
> Significado y uso de las constantes reservadas del lenguaje Arduino.
>
> **Respuesta:**
> Son las **constantes reservadas de Arduino** para manejar el estado de los pines y el hardware. En la gramática todas pertenecen a la regla `constante`:
>
> ### 1. Estados lógicos de un pin
> * **`HIGH`**: Representa **alto voltaje** (5V o 3.3V según la placa) / estado encendido / `1` lógico.
> * **`LOW`**: Representa **bajo voltaje** (0V / Tierra - GND) / estado apagado / `0` lógico.
>
> ### 2. Modos de configuración de un pin (usados habitualmente en `pinMode`)
> * **`INPUT`**: Configura el pin digital como **entrada** para leer sensores o botones externos.
> * **`OUTPUT`**: Configura el pin digital como **salida** para enviar energía a componentes (LEDs, motores, etc.).
> * **`INPUT_PULLUP`**: Configura el pin como **entrada**, pero activa la resistencia interna de *pull-up* del microcontrolador (evita lecturas falsas/ruido en botones sin necesidad de agregar una resistencia física externa).
>
> ### 3. Pin integrado de la placa
> * **`LED_BUILTIN`**: Es una constante numérica que apunta al pin físico donde está conectado el **LED interno propio de la placa Arduino** (habitualmente es el pin digital 13).

---

> **Fecha:**
> 2026-09-29.
> **Persona:**
> Pablo
>
> **Titulo:**
> Estructura del programa, nivel superior y prohibición de definiciones anidadas
>
> **Asunto:**
> Reglas del nivel superior del programa, requerimiento de al menos un elemento y restricción de definiciones dentro de bloques.
>
> **Respuesta:**
> ### 1. "Un programa es una secuencia de 1 o más sentencias/definiciones"
> El compilador **exige que haya código real**. No se permiten archivos vacíos ni archivos con solo comentarios.
>
> * ❌ **Error Sintáctico en Línea 1 (Archivo vacío)**:
>   ```cpp
>   
>   ```
> * ❌ **Error Sintáctico en Línea 1 (Solo comentarios)**:
>   ```cpp
>   // Este es un comentario
>   /* Otro comentario */
>   ```
> * ✅ **Válido (Tiene al menos 1 elemento)**:
>   ```cpp
>   float x;
>   ```
>
> ---
>
> ### 2. "En el nivel superior pueden aparecer `setup()` y `loop()` en cualquier orden y cantidad"
> El "nivel superior" es el código que está libre afuera de todo. Ahí podés poner sentencias o funciones en el orden que quieras y repetir cuantas veces quieras.
>
> * ✅ **Válido (Mezclados y en cualquier orden)**:
>   ```cpp
>   float x = 1.0;          // Sentencia afuera
>   
>   void loop() {           // loop() primero
>       x += 1.0;
>   }
>   
>   void setup() {          // setup() después
>       delay(100);
>   }
>   
>   void setup() {          // Otro setup() más (la gramática lo permite)
>       delay(200);
>   }
>   ```
>
> ---
>
> ### 3. "No pueden aparecer dentro de un bloque"
> No podés meter un `setup()` o `loop()` adentro de otro `setup()` o `loop()` (no existen funciones anidadas).
>
> * ❌ **Error Sintáctico (setup dentro de loop)**:
>   ```cpp
>   void loop() {
>       void setup() {    // ERROR: No se permite definir una función dentro de otra
>           delay(100);
>       }
>   }
>   ```

---

> **Fecha:**
> 2026-09-29.
> **Persona:**
> Pablo
>
> **Titulo:**
> Operaciones entre operandos/factores y diferencia entre etapa sintáctica y semántica
>
> **Asunto:**
> Consulta sobre si los elementos definidos en la regla `factor` (identificadores, números, paréntesis, llamadas con valor, cadenas, booleanos, constantes) se pueden operar entre sí.
>
> **Respuesta:**
> **SÍ, sintácticamente se pueden mezclar y operar entre sí.**
> 
> Para el analizador sintáctico, todo elemento dentro de la regla `factor` es un operando válido:
> - `x + 5` (variables y números)
> - `(x + 5) * 2` (expresiones entre paréntesis)
> - `HIGH + 10` (constantes y números)
> - `true * 5` (booleanos y números)
> - `"Hola" + x` (cadenas y variables)
> - `map(val, 0, 1023, 0, 100) + 5` (llamadas con valor)
> 
> **Diferencia clave:**
> - **Etapa Sintáctica (esta entrega):** Valida únicamente que la estructura `factor operador factor` sea correcta. Expresiones como `HIGH + "hola"` son sintácticamente válidas.
> - **Etapa Semántica (futuras entregas):** Es la encargada de verificar compatibilidad de tipos de datos y marcar error si las operaciones carecen de sentido semántico.






