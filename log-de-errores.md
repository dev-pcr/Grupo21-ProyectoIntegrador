# Log de Errores

Historial de errores reportados, diagnósticos y soluciones aplicadas.

---

### Entrada: 2026-10-22 13:56 — Conflicto de precedencia en PLY entre `t_IDENTIFICADOR` y `t_SERIAL_PRINTLN`

- **Fecha y Hora:** 2026-10-22 13:56
- **Título:** Conflicto de precedencia en PLY entre `t_IDENTIFICADOR` y `t_SERIAL_PRINTLN`
- **Descripción:** Al ejecutar la batería de pruebas sintácticas (`herramientas/verificar_sintactico_ply.py`) sobre los 151 casos de `pruebas-grupo/`, fallaron 18 casos que involucraban `Serial.println(...)` (tanto casos `ok-*` como `sin-*`). El diagnóstico determinó que en PLY (`ply.lex`) las reglas definidas como funciones (`def t_*`) tienen prioridad absoluta y se evalúan antes que las reglas definidas con cadenas literales (`t_* = '...'`). Como `t_IDENTIFICADOR` era una función y `t_SERIAL_PRINTLN` era una cadena, PLY tokenizaba el prefijo `Serial` como un `IDENTIFICADOR` y el carácter `.` subsiguiente como un error léxico no reconocido, partiendo el token compuesto y generando errores sintácticos inesperados.
- **Solución:** Se transformó `t_SERIAL_PRINTLN` en una función (`def t_SERIAL_PRINTLN(t):`) y se posicionó en `lexico.py` estrictamente antes de `def t_IDENTIFICADOR(t)`. Con este cambio de precedencia, PLY empareja `Serial.println` de forma prioritaria y atómica. Se volvió a correr la batería completa sobre `pruebas-grupo/`, logrando **151/151 casos aprobados (100% de éxito)** y **0 conflictos shift/reduce y reduce/reduce** en `parser.out`.

### Entrada: 2026-10-23 16:38 — Regla de oro: error léxico posterior en el archivo perdía frente a un EOF prematuro

- **Fecha y Hora:** 2026-10-23 16:38
- **Título:** Regla de oro: error léxico posterior en el archivo perdía frente a un EOF prematuro
- **Descripción:** Al correr la nueva batería (herramientas/bateria_pruebas_compilador.py) falló la micro-prueba `/* a\nb\nc */\n@`: se esperaba `ERROR LEXICO linea 4` y `compilador.py` devolvía `ERROR SINTACTICO linea 1` (fin de archivo prematuro). Causa: `p_error(None)` informa como línea la del ÚLTIMO TOKEN (aquí 1, por el programa vacío de tokens) y `compilador.py` comparaba solo por línea (`L_lex <= L_sint`). Como el EOF está físicamente después de cualquier carácter, el error léxico (línea 4) debía ganar. Además, un primer intento de corrección comparando por posición absoluta (`lexpos`) provocó una REGRESIÓN en `lex-33-comilla-escapada` y `lex-45-comillas-mezcladas` (207 casos: 205/207): en esos casos el error sintáctico y el léxico están en la misma línea y el diseño del grupo es que en la misma línea prevalece el léxico, cosa que la comparación por posición invertía.
- **Solución:** `sintactico.p_error` ahora marca el error con `'eof': True` (EOF) o `'eof': False` (token). `compilador.compilar_codigo` aplica: si el error sintáctico es de EOF, gana siempre el léxico; si es de token, se mantiene la comparación por línea (`L_lex <= L_sint` => léxico). Se descartó la comparación por posición. Se revalidó todo: micro-pruebas 28/28, casos públicos 9/9, pruebas de entrega 2/2, pruebas-grupo 207/207, CLI 6/6, 0 conflictos shift/reduce y reduce/reduce; los verificadores previos (`verificar_lexico_ply.py`, `verificar_sintactico_ply.py`) siguen en 100%.

