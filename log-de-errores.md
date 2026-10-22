# Log de Errores

Historial de errores reportados, diagnósticos y soluciones aplicadas.

---

### Entrada: 2026-10-22 13:56 — Conflicto de precedencia en PLY entre `t_IDENTIFICADOR` y `t_SERIAL_PRINTLN`

- **Fecha y Hora:** 2026-10-22 13:56
- **Título:** Conflicto de precedencia en PLY entre `t_IDENTIFICADOR` y `t_SERIAL_PRINTLN`
- **Descripción:** Al ejecutar la batería de pruebas sintácticas (`herramientas/verificar_sintactico_ply.py`) sobre los 151 casos de `pruebas-grupo/`, fallaron 18 casos que involucraban `Serial.println(...)` (tanto casos `ok-*` como `sin-*`). El diagnóstico determinó que en PLY (`ply.lex`) las reglas definidas como funciones (`def t_*`) tienen prioridad absoluta y se evalúan antes que las reglas definidas con cadenas literales (`t_* = '...'`). Como `t_IDENTIFICADOR` era una función y `t_SERIAL_PRINTLN` era una cadena, PLY tokenizaba el prefijo `Serial` como un `IDENTIFICADOR` y el carácter `.` subsiguiente como un error léxico no reconocido, partiendo el token compuesto y generando errores sintácticos inesperados.
- **Solución:** Se transformó `t_SERIAL_PRINTLN` en una función (`def t_SERIAL_PRINTLN(t):`) y se posicionó en `lexico.py` estrictamente antes de `def t_IDENTIFICADOR(t)`. Con este cambio de precedencia, PLY empareja `Serial.println` de forma prioritaria y atómica. Se volvió a correr la batería completa sobre `pruebas-grupo/`, logrando **151/151 casos aprobados (100% de éxito)** y **0 conflictos shift/reduce y reduce/reduce** en `parser.out`.

