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
> **Respuesta:**
> _(Completar cuando se resuelva)_

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
> **Respuesta:**
> _(Completar cuando se resuelva)_
