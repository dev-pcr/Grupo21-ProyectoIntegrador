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

