# Guía de Gramáticas y Análisis Sintáctico — Desde Cero
**Para entender `gramatica.txt`, cómo funciona y cómo defenderlo**

---

## 1. La idea general: ¿Qué es una gramática? (Explicado simple)

Imaginate el idioma español. Para formar una oración válida, hay reglas:
- `Oración -> Sujeto + Verbo + Predicado`
- `Sujeto -> Artículo + Sustantivo` (ej: "El perro")

Si alguien dice *"Perro el corre ladrillo"*, entendés las palabras sueltas (léxico OK), pero el orden no tiene sentido: **es un error sintáctico**.

En programación pasa exactamente lo mismo:
1. **El Analizador Léxico (`tokens.txt`)**: Reconoce las "palabras" sueltas (los **Tokens** como `FLOAT`, `IDENTIFICADOR`, `IGUAL`, `PUNTO_Y_COMA`).
2. **El Analizador Sintáctico (`gramatica.txt`)**: Revisa que esas "palabras" estén ordenadas según las reglas del lenguaje.

---

## 2. Conceptos clave que tenés que saber

| Concepto | Qué significa | Ejemplo en nuestro proyecto |
| :--- | :--- | :--- |
| **Terminal** | Una palabra real / token final que viene del archivo de código. Se escriben en **MAYÚSCULAS**. | `FLOAT`, `IDENTIFICADOR`, `IGUAL`, `PUNTO_Y_COMA`, `SETUP` |
| **No Terminal** | Una categoría o estructura que inventamos para agrupar terminales u otras reglas. Se escriben en **minúsculas**. | `programa`, `sentencia`, `expresion`, `termino`, `factor` |
| **Producción / Regla** | Dice cómo se construye un No Terminal. Usa `->` ("se compone de") y `|` ("o bien"). | `numero -> ENTERO \| DECIMAL` |
| **Símbolo Inicial** | La primera regla del archivo, que representa todo el programa completo. | `programa` |

---

## 3. ¿Cómo está armado `gramatica.txt` paso a paso?

Vamos desde lo más grande (el archivo completo) hasta lo más chico (un número o variable).

### Nivel 1: El Programa completo
Un archivo de Arduino está formado por una o más cosas (sentencias o definiciones de funciones):
```text
programa -> elemento | programa elemento
elemento -> sentencia | definicion
```
- ¿Por qué `programa elemento`? Porque es la forma estándar de decir: *"un programa puede tener 1 elemento, o muchos elementos uno atrás de otro"*.

#### Explicación detallada con ejemplos:

La regla se define como:
```text
programa -> elemento | programa elemento
```

1. **Caso base (`elemento`)**: El programa más pequeño posible tiene **un solo** elemento.
2. **Caso recursivo (`programa elemento`)**: Un programa puede ser **otro programa previo** seguido de **un elemento nuevo**.

##### Ejemplos de derivación:

* **Caso 1: Programa con 1 solo elemento** (`x = 5;`)
  ```text
  programa -> elemento (x = 5;)
  ```

* **Caso 2: Programa con 2 elementos** (`int x;` y luego `void setup() {}`)
  1. `programa -> programa elemento_2` (donde `elemento_2` es `void setup() {}`)
  2. `programa -> elemento_1` (donde `elemento_1` es `int x;`)
  * Resultado: `int x; void setup() {}`

* **Caso 3: Programa con 3 elementos** (`int x;`, `void setup() {}`, `void loop() {}`)
  1. `programa -> programa elemento_3` (`void loop() {}`)
  2. `programa -> programa elemento_2` (`void setup() {}`)
  3. `programa -> elemento_1` (`int x;`)
  * Resultado: `int x; void setup() {} void loop() {}`

> **¿Por qué se escribe así?**  
> Garantiza que exista **al menos 1 elemento** (no permite programas vacíos) y utiliza **recursividad por la izquierda**, que es el estándar en analizadores sintácticos LR (como Yacc/Bison) para procesar secuencias eficientemente.

---

### Nivel 2: Las Definiciones (`setup` y `loop`)
El enunciado pide que `setup()` y `loop()` tengan adentro una o más sentencias entre llaves `{ ... }`:
```text
definicion -> VOID SETUP PARENTESIS_IZQ PARENTESIS_DER LLAVE_IZQ sentencias LLAVE_DER | VOID LOOP PARENTESIS_IZQ PARENTESIS_DER LLAVE_IZQ sentencias LLAVE_DER
```
Y un bloque de sentencias es:
```text
sentencias -> sentencia | sentencias sentencia
```

---

### Nivel 3: ¿Qué es una Sentencia?
Una sentencia es una orden individual que termina con `;`:
1. **Declaración de variable:** `float x;` o `float x = 5.0;`
   ```text
   declaracion -> tipo IDENTIFICADOR PUNTO_Y_COMA | tipo IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA
   tipo -> BOOLEAN | CHAR | FLOAT
   ```
2. **Asignación:** `x = 10;`, `x += 2;`, `x -= 3;`
   ```text
   asignacion -> IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA | IDENTIFICADOR SUMA_IGUAL expresion PUNTO_Y_COMA | IDENTIFICADOR RESTA_IGUAL expresion PUNTO_Y_COMA
   ```
3. **Llamadas a funciones que no devuelven valor o sentencias:** `delay(100);`, `Serial.println("hola");`, `map(1, 2);`
   ```text
   sentencia -> declaracion | asignacion | llamada_sentencia PUNTO_Y_COMA
   ```

---

### Nivel 4: Expresiones y Matemática (Precedencia de Operadores)

**El gran desafío:** En matemática `2 + 3 * 4` debe dar `14` (multiplica primero) y no `20`.
¿Cómo le enseñamos a la gramática que `*` y `/` van antes que `+` y `-` sin usar trucos raros?
Se divide en **3 pisos o niveles jerárquicos**:

```
[ Piso 1: expresion ] -> Sumas y Restas (menor prioridad)
          ↓
[ Piso 2: termino ]   -> Multiplicaciones y Divisiones (mayor prioridad)
          ↓
[ Piso 3: factor ]    -> Cosas individuales: números, variables, paréntesis, etc.
```

En código de gramática:
```text
# Nivel 1: Suma y resta
expresion -> expresion SUMA termino | expresion RESTA termino | termino

# Nivel 2: Multiplicación y división
termino -> termino MULTIPLICACION factor | termino DIVISION factor | factor

# Nivel 3: Los valores concretos (Operandos)
factor -> IDENTIFICADOR | numero | PARENTESIS_IZQ expresion PARENTESIS_DER | llamada_valor | CADENA | booleano | constante
```

#### ¿Por qué funciona esto?
Si el analizador lee `a + b * c`:
1. Entra por `expresion`.
2. Ve `a` como `termino` a la izquierda del `+`.
3. A la derecha del `+`, exige un `termino`.
4. El `termino` junta `b * c` antes de volver a subir a la suma.
5. ¡Listo! La multiplicación se agrupa antes que la suma.

Y si hay paréntesis `(a + b) * c`:
- `(a + b)` entra como `factor` (porque tiene paréntesis), baja hasta `expresion`, resuelve la suma adentro, y luego se multiplica por `c`.

---

## 4. Reglas estrictas que pide la cátedra y que cumplimos al 100%

1. **No hay alternativas vacías:** Ninguna regla produce la nada (`ε` o lambda). Todo tiene al menos un token.
2. **Tokens en Mayúsculas:** Usamos exactamente los nombres definidos en `tokens.txt` (`BOOLEAN`, `IDENTIFICADOR`, etc.).
3. **No hay operadores unarios:** `-5` o `-x` no están en el lenguaje (daría error sintáctico si alguien escribe `-5`).
4. **`delay` y `Serial.println` NO devuelven valor:** Solo pueden usarse como sentencia (`delay(10);`), nunca adentro de una cuenta (`x = delay(10) + 2;` es error sintáctico).
5. **`map` SÍ devuelve valor:** Puede usarse como sentencia (`map(1);`) o adentro de una expresión (`x = map(1) + 5;`).

---

## 5. ¿Cómo probás que `gramatica.txt` funciona?

Tenés en el proyecto un script automático creado especialmente para verificar todo:

### Paso 1: Abrir la terminal en la carpeta del proyecto
```powershell
cd "c:\Users\pablo\Desktop\UCASAL 26 NOTEBOOK 2 SEM\CO\Grupo21-ProyectoIntegrador"
```

### Paso 2: Ejecutar el verificador sintáctico
```powershell
python herramientas/verificar_sintactico.py
```

### Qué hace este script cuando lo corrés:
1. Lee `tokens.txt` y `gramatica.txt`.
2. Valida que no haya símbolos desconocidos ni nombres mal escritos.
3. Evalúa los **9 casos públicos de la cátedra** (los 3 válidos dan `OK`, los 3 léxicos dan `ERROR LEXICO` y los 3 sintácticos dan `ERROR SINTACTICO`).
4. Evalúa los **172 casos de prueba propios** de `pruebas-grupo/`.
5. Si todo está perfecto, te muestra en verde:
   `Resultado final: TODO CORRECTO (100% OK)`

---

## 6. Resumen de comandos útiles para recordar

```powershell
# Probar la parte léxica
python herramientas/verificar_lexico.py

# Probar la parte sintáctica (tu gramática)
python herramientas/verificar_sintactico.py

# Subir cambios a GitHub
git add .
git commit -m "Mensaje"
git push
```
