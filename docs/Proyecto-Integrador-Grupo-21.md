Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
Proyecto Integrador de Compiladores
Grupo N.º 21 Lenguaje asignado: Arduino (C++ para microcontrolador)
1. Unidades de aprendizaje
Unidades programáticas enmarcadas en esta actividad:
Unidad 1. Introducción
Unidad 2. Análisis léxico
Unidad 3. Análisis sintáctico
Unidad 4. Análisis semántico
Unidad 5. Código intermedio
2. Resultado de aprendizaje
El resultado de aprendizaje que se pretende lograr con este práctico es: desarrolla un programa
que realice las primeras fases de un compilador utilizando herramientas típicas.
3. Presentación
Un compilador es un programa que traduce los programas escritos en un lenguaje de
programación (lenguaje fuente) a otro lenguaje (lenguaje objeto). El lenguaje fuente (LF)
generalmente es un lenguaje de alto nivel y el lenguaje objeto (LO), un lenguaje de bajo nivel. A lo
largo de la asignatura se estudian las diferentes etapas involucradas en la construcción de un
compilador y las técnicas utilizadas para especificar e implementar lenguajes de programación.
En este proyecto integrador se propone aplicar estos conocimientos en el diseño e
implementación de un analizador léxico y sintáctico para un lenguaje de programación definido
por la cátedra: en este caso, el subconjunto de Arduino (C++ para microcontrolador) que se
define en el Anexo de este enunciado.
Básicamente, deberá construir una aplicación que:
1. Analice instrucciones escritas en el lenguaje fuente.
2. Diferencie los componentes léxicos.
3. Implemente la gramática del lenguaje.
4. Determine e informe si el programa es léxica y sintácticamente correcto.
Compiladores — Grupo N.º 21 Página 1 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
compilador.py
programa.txt
LEX YACC $ python3 compilador.py ok.txt
token OK
Analizador Analizador
1 int x = 3;
léxico sintáctico
2 int y = x + 1 ¿el próximo?
3 print(y);
la línea 1, en tokens
INT ID(x) IGUAL NUM(3) PYC
falta el ; $ python3 compilador.py programa.txt
ERROR SINTACTICO
linea 2: se esperaba ;
Manejador
de errores
error léxico error sintáctico
El proyecto se desarrollará en dos entregas secuenciales. La primera estará orientada a la
especificación formal del lenguaje y la segunda a su implementación mediante Lex y Yacc.
El análisis es léxico y sintáctico, no semántico. Que una variable reciba un valor de otro tipo, o que se use
sin haberla declarado, no es un error para este trabajo: eso corresponde al análisis semántico y no forma
parte del proyecto.
4. Objetivos
El proyecto tiene como objetivos que los estudiantes sean capaces de:
identificar y clasificar los componentes léxicos de un lenguaje;
definir tokens y sus patrones;
especificar formalmente la sintaxis de un lenguaje mediante una gramática;
utilizar correctamente la notación formal definida por la cátedra;
relacionar una especificación formal con su implementación;
implementar un analizador léxico utilizando Lex;
implementar un analizador sintáctico utilizando Yacc;
integrar ambos componentes en una única aplicación;
detectar y reportar errores léxicos y sintácticos;
diseñar y ejecutar casos de prueba;
analizar y justificar las decisiones tomadas durante el desarrollo.
Compiladores — Grupo N.º 21 Página 2 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
5. Modalidad de trabajo
El proyecto se realizará en grupos de uno o dos estudiantes. Cada grupo recibirá un único tema,
correspondiente a un lenguaje definido por la cátedra. Los integrantes de un grupo serán
responsables conjuntamente de las entregas realizadas.
Los lenguajes asignados son diferentes entre los grupos, pero mantienen un nivel de complejidad
y carga de trabajo equivalente. El lenguaje asignado no podrá ser redefinido libremente por los
estudiantes: la especificación del Anexo constituye el punto de partida obligatorio del proyecto.
6. Asignación del tema
La conformación de los grupos y la asignación de los temas se realizará mediante los recursos
disponibles en el aula virtual. Una vez conformado el grupo y asignado el tema, los estudiantes
podrán acceder a este enunciado, cuyo Anexo indica las construcciones que deberán ser
consideradas en el proyecto.
Las dudas sobre el enunciado se plantean en el foro del grupo. La cátedra podrá proporcionar
aclaraciones generales o particulares cuando sea necesario para garantizar una interpretación
consistente de las especificaciones.
7. Etapas del proyecto
El proyecto consta de dos entregas obligatorias y secuenciales:
Entrega 1 — Especificación del lenguaje. Cada grupo deberá analizar el lenguaje asignado y
elaborar su especificación léxica y sintáctica utilizando la notación definida por la cátedra
(sección 8). La Entrega 1 deberá ser evaluada por la cátedra antes de avanzar a la
implementación.
Entrega 2 — Implementación. A partir de la especificación desarrollada y evaluada en la
Entrega 1, los estudiantes deberán implementar el analizador léxico y sintáctico utilizando
obligatoriamente Lex y Yacc, con la detección de errores y un conjunto de pruebas que
permita verificar su funcionamiento. La Entrega 2 constituye la entrega final y definitiva del
proyecto.
7.1. Entrega 1 — Especificación del lenguaje
La primera entrega tiene como objetivo demostrar que el grupo comprende el lenguaje asignado
y puede formalizar sus características léxicas y sintácticas. Consiste en dos archivos de texto,
escritos en la notación de la sección 8:
Compiladores — Grupo N.º 21 Página 3 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
1. tokens.txt — la lista de tokens del lenguaje asignado. Para cada token: nombre,
descripción, patrón (expresión regular), ejemplos de lexemas y, cuando corresponda,
observaciones o restricciones relevantes.
2. gramatica.txt — la gramática del lenguaje fuente: las reglas sintácticas que describen
cómo se generan los programas del lenguaje asignado, usando como terminales los nombres
de los tokens.
La especificación deberá contemplar todas las construcciones del Anexo y ninguna otra, ser
consistente con ellas y utilizar adecuadamente símbolos terminales y no terminales.
Evaluación de la Entrega 1
La notación de la sección 8 se puede ejecutar: con los dos archivos se construye un analizador —
los patrones de tokens.txt como analizador léxico y gramatica.txt como analizador sintáctico
— y se lo ejecuta contra los casos de prueba públicos y contra casos de la cátedra que no se
publican. Una especificación que rechaza programas válidos o acepta programas inválidos no
describe el lenguaje asignado. La devolución informa cuántos casos de cada tipo fallan.
A partir de ese resultado y de la lectura de los archivos, la Entrega 1 tendrá una evaluación
cualitativa:
Aprobado: la entrega cumple con lo solicitado y presenta una especificación correcta y
consistente. El grupo puede avanzar con la siguiente etapa.
Aprobado con observaciones: la entrega cumple con los requisitos necesarios para avanzar,
pero presenta aspectos que deben ser mejorados o tenidos en cuenta durante la
implementación. No es necesario presentar una nueva versión. El grupo puede avanzar y
deberá considerar las observaciones realizadas por la cátedra.
Reelaborar: la entrega presenta una cantidad o importancia significativa de errores,
inconsistencias o incumplimientos de la consigna que impiden considerarla adecuada como
base para la implementación. El grupo deberá corregirla y presentar una nueva versión. La
implementación no podrá comenzar hasta que la Entrega 1 sea aprobada.
Desaprobado: la entrega no fue presentada o no cumple con los requisitos fundamentales de
la consigna.
Importante. La Entrega 1 constituye la especificación de referencia para la implementación. La Entrega 2
deberá corresponderse con ella y con las observaciones realizadas por la cátedra. Si durante la
implementación se detectara un problema que requiera modificar la especificación, el grupo deberá
comunicarlo a la cátedra y justificar la modificación en el informe.
Compiladores — Grupo N.º 21 Página 4 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
7.2. Entrega 2 — Implementación
Una vez aprobada la Entrega 1, el grupo deberá implementar el analizador correspondiente al
lenguaje asignado utilizando obligatoriamente Lex para el análisis léxico y Yacc para el análisis
sintáctico, en su versión para Python: PLY ( ply.lex y ply.yacc ). Ambos componentes deberán
integrarse en una única aplicación.
El analizador léxico deberá reconocer los tokens definidos en la especificación aprobada y
detectar los errores léxicos. El analizador sintáctico deberá implementar la gramática definida
para el lenguaje: reconocer las construcciones válidas, rechazar las inválidas y detectar los errores
sintácticos.
Ejecución y formato de salida
La aplicación se ejecuta exactamente así, desde la carpeta del proyecto:
python3 compilador.py programa.txt
donde programa.txt es un archivo de texto en UTF-8. La primera línea que escribe en la salida
estándar tiene que tener uno de estos tres formatos:
OK
ERROR LEXICO linea N: descripcion
ERROR SINTACTICO linea N: descripcion
OK , ERROR LEXICO , ERROR SINTACTICO y linea se escriben tal cual: en mayúsculas las tres
primeras, sin tildes.
OK significa que el programa es léxica y sintácticamente correcto.
Si hay errores, se informa el primero en el orden de lectura del programa.
N es un número de línea, contando desde 1. En un error léxico, la línea del carácter que no
forma ningún token. En un error sintáctico, la línea del primer token con el que el programa ya
no puede ser válido; si el archivo termina antes de que el programa esté completo, la línea del
último token.
La descripción es obligatoria y la redacta el grupo: indica qué se encontró y, cuando sea
posible, qué se esperaba.
Después de la primera línea la aplicación puede escribir lo que quiera —por ejemplo, otros
errores, porque la recuperación de múltiples errores no es obligatoria—, pero solo la primera
línea se evalúa automáticamente.
Compiladores — Grupo N.º 21 Página 5 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
Ejemplo del formato (no corresponde al lenguaje de este grupo). Si en la línea 4 aparece ) donde se
esperaba una expresión, la primera línea de la salida es:
ERROR SINTACTICO linea 4: se encontro ")" y se esperaba una expresion
Una aplicación que funciona pero escribe Error en la línea 4 no cumple el formato, y se evalúa como
incorrecta en ese caso.
Casos de prueba
Con este enunciado se entregan 9 casos públicos (Anexo, apartado G): 3 válidos, 3 con error
léxico y 3 con error sintáctico. Además, cada grupo deberá incluir en la carpeta pruebas/ de la
entrega dos casos propios, distintos de los públicos:
valido.txt — un programa válido que use todas las construcciones del Anexo (apartado
D), con comentarios —escritos en el estilo de comentario del lenguaje— que expliquen qué
construcción es cada parte.
error.txt — un programa con un único error, léxico o sintáctico, que no sea de los del
apartado F del Anexo, con un comentario que indique en qué línea está, de qué tipo es y por
qué es un error.
esperado.csv — la salida esperada de los dos, en el mismo formato que el de los casos
públicos: una línea de encabezado archivo,esperado,linea y una fila por caso, con
esperado igual a OK , ERROR LEXICO o ERROR SINTACTICO y la línea del error (vacía si es
OK ).
Los dos casos se verifican: la salida de esperado.csv tiene que coincidir con lo que define el
Anexo. Además de los casos públicos y de los del grupo, la cátedra utilizará casos de prueba
propios, que no se publican, para evaluar las implementaciones.
Requisitos técnicos
Python 3 con PLY 3.11, sin otras bibliotecas que no sean las de la biblioteca estándar de
Python, en Linux.
compilador.py en la raíz de la carpeta del proyecto, junto con todos los archivos que necesite
para ejecutarse.
Sin leer ni escribir archivos fuera de la carpeta del proyecto, sin acceso a la red y sin esperar
datos del teclado.
Cada ejecución tiene un límite de 10 segundos.
Compiladores — Grupo N.º 21 Página 6 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
Importante. No se considerará completa una entrega que dependa de configuraciones, archivos o
componentes que no hayan sido incluidos. La cátedra descarga la entrega y la ejecuta tal como llega.
Informe
La entrega incluye un informe, informe.txt o informe.pdf , con estos apartados:
1. Grupo: número de grupo e integrantes.
2. Especificación: los cambios respecto de la Entrega 1 aprobada y su justificación, o la
indicación de que no hubo cambios.
3. Implementación: cómo se tradujo la especificación a Lex y Yacc, los conflictos que informó
Yacc y cómo se resolvieron, y las decisiones tomadas en la detección de errores.
4. Uso de inteligencia artificial: según la sección 13.
5. Fuentes consultadas.
Evaluación de la Entrega 2
La Entrega 2 será evaluada considerando, entre otros, los siguientes aspectos:
correcta implementación del análisis léxico;
correcta implementación del análisis sintáctico;
correspondencia con la especificación del lenguaje;
detección de errores léxicos y de errores sintácticos;
información proporcionada en los mensajes de error;
correcto funcionamiento ante casos válidos y ante casos inválidos;
calidad y cobertura de los casos de prueba;
correcta ejecución;
organización y claridad del código;
documentación e instrucciones de uso.
El funcionamiento se mide ejecutando compilador.py contra los casos públicos, los casos del
grupo y los casos no publicados de la cátedra: un caso es correcto si la primera línea de la salida
tiene el tipo esperado y, en los errores, la línea esperada. La evaluación de la Entrega 2 forma
parte de la evaluación final de la asignatura, de acuerdo con lo establecido en la propuesta de
cátedra.
Compiladores — Grupo N.º 21 Página 7 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
8. Notación de la cátedra
Los dos archivos de la Entrega 1 son de texto plano en UTF-8. En los dos, una línea que empieza
con # es un comentario y una línea vacía se ignora.
8.1. tokens.txt
Cada token se escribe en una línea con su nombre y su patrón, separados por uno o más
espacios:
NOMBRE patrón
El nombre empieza con una letra mayúscula y sigue con mayúsculas, dígitos o guiones bajos.
Es el nombre con el que el token aparece en la gramática.
El patrón es una expresión regular con la sintaxis del módulo re de Python —la misma que
usa PLY—, desde el primer carácter que no es espacio hasta el final de la línea, sin los espacios
finales.
Inmediatamente arriba de cada token van, en este orden, dos líneas obligatorias y una
opcional:
# descripción: qué representa el token
# ejemplos: lexema, lexema, lexema
# observaciones: restricciones o aclaraciones
Además de los tokens, hay directivas, que empiezan con @ :
@ignorar patrón — lo que el analizador descarta: espacios, comentarios. Puede haber
varias.
El analizador que se construye con el archivo lee el programa de izquierda a derecha y, en cada
posición:
1. si es un salto de línea, lo descarta;
2. si no, prueba los patrones de @ignorar en el orden en que están escritos: el primero que
reconoce al menos un carácter descarta lo reconocido;
3. si ninguno lo hizo, prueba los patrones de los tokens: gana el que reconoce la cadena más
larga y, ante un empate, el que está escrito primero;
4. si ningún patrón reconoce al menos un carácter, es un error léxico.
Compiladores — Grupo N.º 21 Página 8 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
8.2. gramatica.txt
no_terminal -> simbolo simbolo simbolo | otra alternativa
Cada regla tiene un no terminal a la izquierda de -> y una o más alternativas a la derecha,
separadas por | . Si una línea termina en | , la regla continúa en la línea siguiente. Un mismo
no terminal puede tener varias reglas: sus alternativas se suman.
Los símbolos se separan con espacios. Un símbolo es no terminal si aparece a la izquierda de
alguna regla; si no, tiene que ser el nombre de un token de tokens.txt . No se escriben
símbolos literales: un signo como ; se escribe por el nombre de su token.
El símbolo inicial es el no terminal de la primera regla.
Toda alternativa tiene al menos un símbolo: no se admiten alternativas vacías.
Ejemplo de la notación (un lenguaje inventado, no el de este grupo):
# descripción: palabra reservada que muestra un valor
# ejemplos: mostrar
MOSTRAR mostrar
# descripción: número entero
# ejemplos: 0, 42, 1500
ENTERO [0-9]+
@ignorar [ \t]+
programa -> orden | programa orden
orden -> MOSTRAR ENTERO
9. Entrega y presentación
De manera obligatoria y condicionante para obtener la regularidad de la materia (ver propuesta
de cátedra), cada grupo deberá presentar y aprobar la Entrega 1. Los alumnos que no la
presenten o no la aprueben quedarán en condición de libres.
Todas las entregas se realizan a través de la plataforma, en el espacio destinado a tal fin y dentro
del plazo establecido en el aula virtual. No se recibirán entregas fuera de ese plazo ni por mail.
Entrega 1: un archivo Grupo-21.zip que contiene tokens.txt y gramatica.txt .
Entrega 2: un archivo Grupo-21.zip con esta estructura:
Compiladores — Grupo N.º 21 Página 9 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
compilador.py y los demás archivos .py del proyecto
tokens.txt la especificación final
gramatica.txt
pruebas/ valido.txt, error.txt y esperado.csv
informe.txt o informe.pdf
Antes de finalizar el cursado (plazo en la plataforma): alumnos en condiciones de
promocionar la materia.
Turno de exámenes finales: alumnos que regularicen pero no promocionen rinden el
examen final, que consiste en la presentación del trabajo final y su defensa oral. La entrega
se sube a la plataforma hasta 72 horas hábiles antes de la fecha del examen.
El día de la defensa, cada alumno responderá las preguntas de los docentes sobre el desarrollo
del trabajo y realizará una modificación en vivo sobre la especificación y la implementación
entregadas. Si bien el trabajo es grupal, la nota individual dependerá del desarrollo del proyecto y
de su defensa oral. La nota de este trabajo integrador realiza su aporte a la nota final de la
materia, según lo indicado en la propuesta de cátedra.
10. Recursos y lugar de aprendizaje
Los recursos que debe utilizar para realizar este práctico son:
Lecciones teóricas (aula virtual).
Actividades prácticas (aula virtual).
Material provisto por la cátedra (aula virtual).
Bibliografía básica y complementaria (ver propuesta de cátedra).
Documentación oficial de PLY: https://www.dabeaz.com/ply/ply.html
11. Tiempo estimado de realización
Horas presenciales 7 h
Horas de trabajo 15 h
autónomo
Tiempo total 22 h
Compiladores — Grupo N.º 21 Página 10 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
12. Consideraciones finales
El proyecto integrador propone recorrer el proceso que comienza con la especificación formal de
un lenguaje y culmina con la implementación de un analizador léxico-sintáctico capaz de
reconocer sus construcciones y detectar errores.
Se espera que los estudiantes comprendan la relación entre la especificación formal y su
implementación mediante Lex y Yacc, y que puedan fundamentar las decisiones adoptadas
utilizando los conceptos y técnicas estudiados en la asignatura. El objetivo no es únicamente
obtener un programa que funcione, sino integrar los conocimientos adquiridos durante la
cursada y aplicarlos en el desarrollo de una solución concreta.
13. Uso de herramientas de inteligencia artificial
Se permite el uso de herramientas de inteligencia artificial (IA) durante el desarrollo del proyecto
como recurso de consulta, aprendizaje y apoyo. El uso de IA no reemplaza el trabajo de
análisis, diseño e implementación que corresponde a los estudiantes.
Los integrantes del grupo deberán comprender y poder explicar las decisiones tomadas en su
proyecto. No se espera que soliciten a una herramienta de IA la resolución completa de la
consigna y presenten el resultado sin analizarlo, verificarlo y comprenderlo.
En el informe de la Entrega 2 se deberá incluir, por cada uso: la herramienta utilizada, el tipo de
consulta, su finalidad, el resultado o aporte obtenido y cómo fue verificado o adaptado por el
grupo. Si no se usó ninguna, se lo indica.
Compiladores — Grupo N.º 21 Página 11 de 14

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
Anexo — Lenguaje fuente asignado al Grupo N.º 21
Este anexo define el lenguaje del proyecto: un subconjunto de Arduino (C++ para
microcontrolador). Lo que figura acá pertenece al lenguaje, con la forma exacta con que figura,
y nada más. Donde el subconjunto difiere de Arduino (C++ para microcontrolador) real, vale lo
que dice el anexo.
A. Resumen
| Lenguaje fuente        | Arduino (C++ para microcontrolador)       |     |     |     |
| ---------------------- | ----------------------------------------- | --- | --- | --- |
| Construcciones         | setup() y loop() · asignación (=, -=, +=) |     |     |     |
| Tipos de datos         | boolean, char, float                      |     |     |     |
| Funciones              | map, Serial.println, delay                |     |     |     |
| Operadores aritméticos | + - * /                                   |     |     |     |
| Comentarios            | /* COMENTARIO */                          |     |     |     |
B. Componentes léxicos
Identificadores una letra o un guion bajo, seguido de cero o más letras, dígitos o guiones bajos.
Letras sin tilde ni eñe.
Números enteros (uno o más dígitos) y decimales (uno o más dígitos, un punto y uno o más
|     | dígitos:  | 3.25 ). Sin signo ni exponente. |     |     |
| --- | --------- | ------------------------------- | --- | --- |
Cadenas texto entre comillas dobles o entre comillas simples, en una sola línea. Termina en la
primera comilla igual a la de apertura; no hay secuencias de escape.
| Palabras reservadas | loop ,  setup | ,  void          |     |     |
| ------------------- | ------------- | ---------------- | --- | --- |
| Tipos               | boolean       | ,  char ,  float |     |     |
| Booleanos           | ,             |                  |     |     |
false true
Constantes HIGH ,  INPUT ,  INPUT_PULLUP ,  LED_BUILTIN ,  LOW ,  OUTPUT
| Funciones | map ,  Serial.println |     | ,  delay |     |
| --------- | --------------------- | --- | -------- | --- |
Sobre las palabras Ninguna de las palabras de las filas anteriores puede usarse como identificador. Se
escriben exactamente como figuran, respetando mayúsculas y minúsculas. Un
nombre con punto se escribe sin espacios alrededor del punto.
| Operadores y signos | (   )   * |   +   ,   -   / |   ;   =   {   } |   +=   -= |
| ------------------- | --------- | --------------- | --------------- | --------- |
Compiladores — Grupo N.º 21 Página 12 de 14

Compiladores 2026
| Facultad de Ingeniería    |     |     |     | Mg. Lic. Carolina Cardoso |                       |
| ------------------------- | --- | --- | --- | ------------------------- | --------------------- |
| Ingeniería en Informática |     |     |     |                           | Ing. Miguel N. Tolaba |
Comentarios de bloque: empieza con  /*  y termina en el primer  */  que aparezca después;
puede ocupar varias líneas y no se anida. Se descartan: no forman parte de ninguna
construcción.
Espacios Los espacios, tabulaciones y saltos de línea separan piezas y se descartan: el
formato es libre.
C. Estructura del programa
Un programa es una secuencia de una o más sentencias. Un archivo vacío, o que solo tiene
comentarios, es un error sintáctico en la línea 1. En el nivel superior, además de sentencias,
| pueden aparecer las definiciones  |     |                    |     |  y                | , en cualquier |
| --------------------------------- | --- | ------------------ | --- | ----------------- | -------------- |
|                                   |     | void setup() { … } |     | void loop() { … } |                |
orden y cantidad. No pueden aparecer dentro de un bloque.
D. Construcciones
Cada fila es una construcción, y cada línea de la fila, una forma válida de escribirla. Lo escrito en
 va tal cual; lo escrito en cursiva es una parte que se define en el apartado E o en el B.
código
setup() y loop()
|     | void   setup |   (   )   |   {  sentencias  | }   |     |
| --- | ------------ | --------- | ---------------- | --- | --- |
|     | void   loop  |   (   )   | {  sentencias    | }   |     |
asignación (=, -=, +=)
|     | identificador  | =  expresión   | ;   |     |     |
| --- | -------------- | -------------- | --- | --- | --- |
|     | identificador  | -=  expresión  | ;   |     |     |
|     | identificador  |  expresión     |     |     |     |
|     |                | +=             | ;   |     |     |
llamada a función
llamada  ;
declaración de variable
|     | tipo identificador  | =  expresión  | ;   |     |     |
| --- | ------------------- | ------------- | --- | --- | --- |
tipo identificador
;
E. Definiciones
sentencias
Una o más sentencias de las de esta sección, una detrás de otra.
expresión
Un operando, o dos o más operandos unidos por los operadores aritméticos  + ,  - ,  *  y  / .  *  y  /
tienen mayor precedencia que  +  y  - ; entre operadores de la misma precedencia se asocia de
izquierda a derecha. No hay operadores unarios:  -x  y  -5  no son expresiones.
| Compiladores — Grupo N.º 21 |     |     |     |     | Página 13 de 14 |
| --------------------------- | --- | --- | --- | --- | --------------- |

Compiladores 2026
Facultad de Ingeniería Mg. Lic. Carolina Cardoso
Ingeniería en Informática Ing. Miguel N. Tolaba
operando
Es un identificador, un número, una expresión entre paréntesis, una llamada a una función que devuelve
valor, una cadena, un booleano o una constante.
llamada
El nombre de una función seguido de ( , uno o más argumentos separados por , y ) . Cada
argumento es una expresión. No hay llamadas sin argumentos. Devuelven un valor, y pueden usarse
como operando: map . No devuelven valor, y solo pueden usarse como sentencia, nunca dentro de una
expresión: Serial.println y delay .
F. Lo que no pertenece al lenguaje
Un programa que usa algo que no está en este anexo es incorrecto. Si ese elemento es un
operador, un tipo, una palabra o un estilo de comentario de otro lenguaje, o un comentario
de bloque que no se cierra, según cómo esté construido el analizador puede detectarse como
error léxico o como error sintáctico: en esos casos se acepta cualquiera de los dos y no se evalúa
la línea. En todo otro error, el tipo y la línea son los que resultan de este anexo y de la sección 7.2.
G. Casos de prueba públicos
Los archivos están en la carpeta casos/ que acompaña este enunciado, con esperado.csv .
Archivo Primera línea de la salida
valido-01.txt OK
valido-02.txt OK
valido-03.txt OK
lexico-01.txt ERROR LEXICO linea 3
lexico-02.txt ERROR LEXICO linea 5
lexico-03.txt ERROR LEXICO linea 8
sintactico-01.txt ERROR SINTACTICO linea 2
sintactico-02.txt ERROR SINTACTICO linea 5
sintactico-03.txt ERROR SINTACTICO linea 4
Enunciado generado para el grupo 21 · semilla 2026 · cada grupo tiene un subconjunto distinto.
Compiladores — Grupo N.º 21 Página 14 de 14