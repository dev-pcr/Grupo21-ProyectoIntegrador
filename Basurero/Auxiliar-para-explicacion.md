# Explicación de la Gramática: Estructura del Programa y Nivel Superior

```text
programa -> elemento | programa elemento
elemento -> sentencia | definicion
```

---

## 1. Explicación Simple

Esta regla define el **esqueleto completo de un archivo de Arduino**.

* **`elemento`**: Es la unidad básica que puede vivir en el nivel superior (afuera de cualquier función). Puede ser una **`sentencia`** (como declarar o asignar una variable) o una **`definicion`** (las funciones `setup()` o `loop()`).
* **`programa`**: Representa todo el archivo. Se define con **recursividad por la izquierda** (`programa elemento`), lo que significa que un programa es **una secuencia de 1 o más elementos acumulados uno detrás de otro**.

---

## 2. Puntos Clave

1. **Exige al menos 1 elemento**: No se permiten archivos vacíos ni archivos que solo contengan comentarios.
2. **Permite cualquier combinación y orden**: En el nivel superior podés mezclar sentencias sueltas y definiciones de `setup()` o `loop()` en el orden que quieras y cuantas veces quieras.

---

## 3. Ejemplo Práctico de Derivación

Si el analizador sintáctico recibe este código:

```cpp
float x = 5.0;

void setup() {
    delay(100);
}
```

El árbol sintáctico desglosa el programa paso a paso así:

1. Reconoce que hay 2 elementos:
   * **Elemento 1:** `float x = 5.0;` (es una `sentencia`).
   * **Elemento 2:** `void setup() { delay(100); }` (es una `definicion`).

2. Aplica las reglas sintácticas:
   * `programa` $\rightarrow$ `programa` + `elemento_2` (`definicion`)
   * El `programa` interno se reduce al caso base: `programa` $\rightarrow$ `elemento_1` (`sentencia`)

---

## 4. Errores Sintácticos Frecuentes

* **Archivo vacío o solo comentarios:** Falla en la línea 1 porque no hay ningún `elemento`.
* **Funciones anidadas:** Poner un `setup()` dentro de otro `setup()` falla porque las definiciones solo están permitidas como `elemento` del nivel superior, no dentro del bloque de sentencias.
