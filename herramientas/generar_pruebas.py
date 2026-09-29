#!/usr/bin/env python3
"""Genera la suite propia de pruebas en pruebas-grupo/ (archivos .txt + esperado.csv).

La carpeta casos/ contiene los 9 casos públicos de la cátedra y no se toca.
pruebas-grupo/ contiene casos propios: a mayor número de casos, menor
probabilidad de fallo en la corrección automática.

Para cada caso se declara:
  nombre  -> archivo .txt generado
  esperado-> OK | ERROR LEXICO | ERROR SINTACTICO
  linea   -> número de línea exigido (solo se evalúa para ERROR LEXICO;
             para OK y ERROR SINTACTICO la verificación léxica solo exige
             que no haya error léxico)
  texto   -> contenido exacto del archivo

Uso:  python herramientas/generar_pruebas.py
      python herramientas/verificar_lexico.py
"""

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR = RAIZ / "pruebas-grupo"

# (nombre, esperado, linea, texto)
CASOS = [
    # ------------------------------------------------------------------
    # OK — programas que deben compilar sin ningún error
    # ------------------------------------------------------------------
    ("ok-01-una-sentencia", "OK", "", """\
map(1);
"""),
    ("ok-02-ambas-definiciones", "OK", "", """\
void setup() {
  float x = 1.5;
}
void loop() {
  x += 2;
}
"""),
    # definiciones en cualquier orden, con sentencias intercaladas arriba
    ("ok-03-definiciones-desordenadas", "OK", "", """\
void loop() {
    delay(1000);
}
map(42);
void setup() {
    float a;
}
"""),
    # "en cualquier orden y cantidad": dos setup y dos loop
    ("ok-04-definiciones-multiples", "OK", "", """\
void setup() {
    char c = 'a';
}
void setup() {
    boolean b = true;
}
void loop() {
    delay(1);
}
void loop() {
    Serial.println("hola");
}
"""),
    # programa sin definiciones: solo sentencias en el nivel superior
    ("ok-05-solo-sentencias", "OK", "", """\
float total = 1 + 2 * 3;
total -= 4;
Serial.println(total);
"""),
    # precedencia, paréntesis y llamadas anidadas como operandos
    ("ok-06-expresiones", "OK", "", """\
float r = (1 + 2) * 3 / 4 - 5;
r = map(r + 1) * 2;
delay(map(1) + 2);
"""),
    # los tres tipos, con y sin inicializador
    ("ok-07-tipos-declaraciones", "OK", "", """\
boolean b = false;
char c = 'x';
float f = 3.25;
char sinInicializador;
boolean otro;
float otro2;
"""),
    ("ok-08-constantes", "OK", "", """\
float a = HIGH;
float b = LOW;
float c = INPUT;
float d = OUTPUT;
float e = INPUT_PULLUP;
float f = LED_BUILTIN;
"""),
    # ambos delimitadores, cadenas vacías y la otra comilla adentro;
    # una cadena admite caracteres no ASCII (la restricción es solo para identificadores)
    ("ok-09-cadenas", "OK", "", """\
Serial.println("hola mundo");
Serial.println('x');
Serial.println("");
Serial.println('');
Serial.println("comilla simple ' adentro");
Serial.println('doble " adentro');
Serial.println("señal € ok");
"""),
    # comentarios: multilínea, en línea, /**/, vacíos y con símbolos raros adentro
    ("ok-10-comentarios", "OK", "", """\
/* uno */
/* multi
   lineas
   con é y € y // y " */
map(1);   /* inline */
/**/
/*
*/
map(2);
"""),
    # formato libre: tabulaciones como separador y líneas en blanco
    ("ok-11-formato-libre", "OK", "", "\tfloat\tx\t=\t1;\n\n\n\tx += 2;\t\nSerial.println( x );\n"),
    # archivo sin salto de línea final
    ("ok-12-sin-newline-final", "OK", "", "map(1);"),
    # fin de línea Windows (el \r lo descarta @ignorar)
    ("ok-13-crlf", "OK", "", "map(1);\r\nfloat x = 2;\r\nSerial.println(x);\r\n"),
    # prefijos de palabras reservadas: gana el identificador más largo
    ("ok-14-identificadores-parecidos", "OK", "", """\
float loopx = 1;
float HIGHWAY = 2;
float INPUTX = 3;
float mapa = 4;
float setupx = 5;
float _contador = 6;
float x1 = 7;
"""),
    # las palabras se escriben exactamente como figuran (sensibles a mayúsculas)
    ("ok-15-sensibilidad-mayusculas", "OK", "", """\
float Loop = 1;
float Setup = 2;
float Void = 3;
float True = 4;
float INPUTx = 5;
"""),
    ("ok-16-numeros", "OK", "", """\
float a = 0007;
float b = 0;
float c = 0.5;
float d = 420.46;
float e = 1234567890;
"""),
    # una o más argumentos separados por coma
    ("ok-17-argumentos-multiples", "OK", "", """\
float m = map(1, 2, 3, 4);
delay(1, 2);
Serial.println(1, 2, 3);
"""),
    ("ok-18-todo-una-linea", "OK", "", "void setup() { float x = 1; } void loop() { delay(x); }\n"),
    ("ok-19-lineas-en-blanco", "OK", "", "map(1);\n\n\nmap(2);\n"),
    # dentro de una cadena, los delimitadores del lenguaje son texto
    ("ok-20-cadenas-con-simbolos", "OK", "", """\
Serial.println("{;}");
Serial.println("/* no es comentario */");
Serial.println("// tampoco");
Serial.println("ruta\\archivo");
"""),
    # identificadores más largos que la palabra reservada que les da el prefijo
    ("ok-21-prefijos-inversos", "OK", "", """\
float INPUT_PULLUPX = 1;
float HIGHLOW = 2;
float SETUP = 3;
float voidx = 4;
float true1 = 5;
"""),
    ("ok-22-decimales-limite", "OK", "", """\
float a = 0.0;
float b = 3.141592653589793;
float c = 00.00;
"""),
    ("ok-23-enteros-largos", "OK", "", """\
float a = 99999999999999999999;
float b = 0000;
"""),
    ("ok-24-identificadores-limites", "OK", "", """\
float _ = 1;
float __ = 2;
float _1 = 3;
float a_1_b = 4;
"""),
    # el comentario se descarta aunque esté en el medio de una construcción
    ("ok-25-comentario-entre-tokens", "OK", "", """\
map /* entre */ (1);
void setup() { /* adentro */ float x = 1; }
"""),
    ("ok-26-sin-espacios", "OK", "", "void setup(){float x=1;}void loop(){x+=2;}\n"),
    ("ok-27-llamadas-anidadas", "OK", "", """\
Serial.println(map(1) + 2 * 3);
delay((1 + 2) * 3);
float m = map(map(1), 2);
"""),
    # la gramática no valida tipos: solo que la expresión sea sintácticamente válida
    ("ok-28-tipos-no-se-verifican", "OK", "", """\
char c = "hola";
boolean b = 1;
float f = false;
"""),
    ("ok-29-comments-consecutivos", "OK", "", """\
/* a */ /* b */
/* c */
map(1);
"""),
    ("ok-30-expresiones-anidadas", "OK", "", """\
x = ((1 + 2) * (3 + 4));
float y = HIGH + LOW * INPUT;
"""),
    ("ok-31-asignaciones-compuestas", "OK", "", """\
x += 1;
x -= 2;
x = x + 1;
"""),
    # CRLF adentro de un comentario multilínea
    ("ok-32-crlf-con-comment-multilinea", "OK", "", "/* a\r\n   b */\r\nmap(1);\r\nfloat x = 2;\r\n"),
    # comentario como última línea, sin sentencia después
    ("ok-33-comment-al-final", "OK", "", "map(1);\n/* cierre */"),
    # keywords pegadas a operadores sin espacios
    ("ok-34-todo-pegado-con-keywords", "OK", "", "float a=HIGH+LOW*INPUT;boolean b=true;char c='x';\n"),
    # programa estilo Arduino completo: sentencia arriba + las dos definiciones
    ("ok-35-programa-completo", "OK", "", """\
float inicio = 1;

void setup() {
    float velocidad = 1.5;
    delay(velocidad);
}

void loop() {
    velocidad -= 0.5;
    Serial.println(velocidad);
}
"""),
    # el comentario se descarta por completo: no interrumpe la construcción
    ("ok-36-comentario-entre-void-y-setup", "OK", "", "void /* c */ setup() {\n    map(1);\n}\n"),
    # formato libre hasta dentro de una misma producción
    ("ok-37-newlines-dentro-definicion", "OK", "", "void\nsetup\n(\n)\n{\nmap(1);\n}\n"),
    # todos los tipos de operando en una sola expresión (la gramática no valida tipos)
    ("ok-38-operandos-todos", "OK", "", 'x = a + 1.5 * "s" + true + HIGH + map(1);\n'),
    # asociatividad por la izquierda y paréntesis que agrupan
    ("ok-39-asociatividad", "OK", "", "x = 1 - 2 - 3;\ny = 8 / 4 / 2;\nz = ((1));\n"),
    # fin de línea antiguo (solo \\r): se descarta y no cuenta como línea
    ("ok-40-solo-cr", "OK", "", "map(1);\rfloat x = 2;\rSerial.println(x);\r"),
    ("ok-41-muchos-argumentos", "OK", "", "map(1,2,3,4,5,6,7,8,9,10);\n"),
    ("ok-42-identificador-largo", "OK", "", "float aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1 = 1;\n"),
    ("ok-43-definiciones-identicas", "OK", "", "void setup() {\n    map(1);\n}\nvoid setup() {\n    map(1);\n}\n"),

    # ------------------------------------------------------------------
    # ERROR LEXICO — el primer carácter que no forma ningún token
    # (la línea es obligatoria: sección 7.2)
    # ------------------------------------------------------------------
    # letra con tilde: IDENTIFICADOR es solo ASCII
    ("lex-01-letra-con-tilde", "ERROR LEXICO", "2", """\
float a = 1;
float café = 2;
"""),
    ("lex-02-comilla-doble-sin-cerrar", "ERROR LEXICO", "3", """\
map(1);
float a = 2;
Serial.println("hola);
"""),
    ("lex-03-comilla-simple-sin-cerrar", "ERROR LEXICO", "2", """\
map(1);
Serial.println('hola);
"""),
    # 3. no es decimal: gana ENTERO y el punto queda suelto
    ("lex-04-decimal-punto-colgante", "ERROR LEXICO", "2", """\
float a = 1;
float b = 3.;
"""),
    # gana DECIMAL (1.2) y el segundo punto queda suelto
    ("lex-05-dos-puntos", "ERROR LEXICO", "2", """\
map(1);
x = 1.2.3;
"""),
    # operador de otro lenguaje: el anexo F acepta léxico o sintáctico;
    # nuestro analizador lo detecta como léxico
    ("lex-06-exclamacion", "ERROR LEXICO", "2", """\
float a = 1;
boolean b = a ! a;
"""),
    ("lex-07-arroba", "ERROR LEXICO", "2", """\
void setup() {
    @marcar(1);
}
"""),
    ("lex-08-corchete", "ERROR LEXICO", "2", """\
map(1);
x = y[0];
"""),
    ("lex-09-interrogacion", "ERROR LEXICO", "2", """\
map(1);
x = a ? b;
"""),
    # moneda: carácter desconocido, la línea sí se evalúa
    ("lex-10-euro", "ERROR LEXICO", "2", """\
float precio = 100;
float total = 200 €;
"""),
    ("lex-11-numeral", "ERROR LEXICO", "2", """\
map(1);
# define X 1
"""),
    # nombre con punto: se escribe sin espacios alrededor del punto
    ("lex-12-serial-con-espacios", "ERROR LEXICO", "2", """\
void setup() {
    Serial . println(1);
}
"""),
    # sensibilidad a mayúsculas también en las funciones
    ("lex-13-serial-en-minusculas", "ERROR LEXICO", "2", """\
void loop() {
    serial.println(1);
}
"""),
    # dos errores en la misma línea: gana el primero
    ("lex-14-primer-error-gana", "ERROR LEXICO", "2", """\
float a = 1;
@ €
"""),
    # los saltos de línea dentro del comentario descartado cuentan (1-3) -> error en 5
    ("lex-15-error-tras-comment-multilinea", "ERROR LEXICO", "5", """\
/* uno
   dos
   tres */
map(1);
€
"""),
    ("lex-16-error-tras-lineas-en-blanco", "ERROR LEXICO", "4", """\
map(1);


@
"""),
    ("lex-17-error-linea-1", "ERROR LEXICO", "1", "€hola\n"),
    ("lex-18-error-ultima-linea", "ERROR LEXICO", "2", "float a = 1;\n€\n"),
    # una cadena ocupa una sola línea: el " de apertura nunca se cierra
    ("lex-19-cadena-multilinea", "ERROR LEXICO", "1", """\
Serial.println("hola
mundo");
"""),
    # nombre con punto mal escrito: el punto no forma ningún token
    ("lex-20-punto-suelto", "ERROR LEXICO", "2", """\
map(1);
x = y.z;
"""),
    # .5 no es decimal: el punto delante no forma ningún token
    ("lex-21-punto-inicial", "ERROR LEXICO", "2", "map(1);\nx = .5;\n"),
    ("lex-22-puntos-seguidos", "ERROR LEXICO", "2", "map(1);\nx = 1..2;\n"),
    # prefijo delante: SERIAL_PRINTLN no puede empezar en la x
    ("lex-23-prefijo-de-serial", "ERROR LEXICO", "2", "map(1);\nxSerial.println(1);\n"),
    # el comentario descartado no cambia el número de línea
    ("lex-24-comment-luego-error-misma-linea", "ERROR LEXICO", "1", "/* c */ €\n"),
    ("lex-25-error-tras-comment-1-linea", "ERROR LEXICO", "3", "/* c */\nmap(1);\n€\n"),
    # fin de línea Windows: el \r se descarta y no cuenta como línea
    ("lex-26-error-despues-de-crlf", "ERROR LEXICO", "3", "map(1);\r\nfloat x = 2;\r\n€\r\n"),
    ("lex-27-error-tras-comment-crlf", "ERROR LEXICO", "4", "/* a\r\n   b */\r\nmap(1);\r\n€\r\n"),
    # sin salto de línea final
    ("lex-28-error-sin-newline-final", "ERROR LEXICO", "2", "float a = 1;\n€"),
    # no hay secuencias de escape: la barra no salta la comilla ni el salto de línea
    ("lex-29-backslash-no-es-escape", "ERROR LEXICO", "1", "Serial.println(\"abc\\\n"),
    ("lex-30-ampersand", "ERROR LEXICO", "2", "map(1);\nx = 1 & 2;\n"),
    # "" es cadena vacía y la tercera comilla queda sin cerrar
    ("lex-31-triple-comilla", "ERROR LEXICO", "2", 'map(1);\nx = """;\n'),
    ("lex-32-corchete-cierre", "ERROR LEXICO", "2", "map(1);\nx = ];\n"),
    # la comilla escapada cierra la cadena (no hay escapes): queda otra sin cerrar
    ("lex-33-comilla-escapada", "ERROR LEXICO", "1", "x = \"a\\\"b\";\n"),
    # el ignorar es [ \\t\\r]+: el form feed no se descarta
    ("lex-34-form-feed", "ERROR LEXICO", "1", "x = 1\f;\n"),
    # error en una línea de dos dígitos
    ("lex-35-error-linea-12", "ERROR LEXICO", "12", "map(1);\nmap(1);\nmap(1);\nmap(1);\nmap(1);\nmap(1);\nmap(1);\nmap(1);\nmap(1);\nmap(1);\nmap(1);\n€\n"),
    ("lex-36-dos-comments-y-error", "ERROR LEXICO", "1", "/* a */ /* b */ @\n"),
    # recorre toda una línea cargada antes de fallar al final
    ("lex-37-error-al-final-de-linea-cargada", "ERROR LEXICO", "1", "map(1); delay(2); Serial.println(3); @\n"),
    # error léxico dentro de un bloque
    ("lex-38-error-dentro-de-bloque", "ERROR LEXICO", "3", "void setup() {\n    map(1);\n    @\n}\n"),
    # la cadena entera se descarta aunque contenga /* y */
    ("lex-39-error-tras-string-con-comment", "ERROR LEXICO", "1", 'Serial.println("texto;(){}=/*fin*/"); @\n'),
    # Serial.print y Serial.begin no existen: el punto queda suelto
    ("lex-40-serial-print", "ERROR LEXICO", "2", "map(1);\nSerial.print(1);\n"),
    ("lex-41-serial-begin", "ERROR LEXICO", "1", "Serial.begin(9600);\n"),
    # operadores de otros lenguajes que acá no son ningún token
    ("lex-42-porcentaje", "ERROR LEXICO", "2", "map(1);\nx = 5 % 2;\n"),
    ("lex-43-menor-que", "ERROR LEXICO", "2", "map(1);\nx = 1 < 2;\n"),
    ("lex-44-mayor-que", "ERROR LEXICO", "1", "x = a > b;\n"),
    # cadena que cierra, identificador y comilla que queda sin cerrar
    ("lex-45-comillas-mezcladas", "ERROR LEXICO", "1", "'abc'def'\n"),
    # espacio no separable (pegado de Word/Excel): no está en [ \t\r]+
    ("lex-46-espacio-no-separable", "ERROR LEXICO", "2", "map(1);\nx = 1\u00a0;\n"),
    ("lex-47-tab-vertical", "ERROR LEXICO", "1", "x = 1\vy;\n"),

    # ------------------------------------------------------------------
    # ERROR SINTACTICO — debe lexear sin error; la línea es la del primer
    # token con el que el programa ya no puede ser válido (sección 7.2);
    # si termina el archivo, la del último token.
    # ------------------------------------------------------------------
    # apartado C: un archivo vacío es error sintáctico en la línea 1
    ("sin-01-archivo-vacio", "ERROR SINTACTICO", "1", ""),
    ("sin-02-solo-comentarios", "ERROR SINTACTICO", "1", "/* nada que ver */\n"),
    # DUDA (registrada en Historico.md): D escribe { sentencias } y E define
    # sentencias como "una o más": lectura estricta -> cuerpo vacío inválido.
    ("sin-03-bloque-vacio-setup", "ERROR SINTACTICO", "1", "void setup() { }\nmap(1);\n"),
    ("sin-04-bloque-vacio-loop", "ERROR SINTACTICO", "2", "void loop() {\n}\nfloat x = 1;\n"),
    # E: no hay operadores unarios
    ("sin-05-unario-menos-numero", "ERROR SINTACTICO", "1", "float x = -5;\n"),
    ("sin-06-unario-menos-identificador", "ERROR SINTACTICO", "1", "x = -y;\n"),
    # E: no hay llamadas sin argumentos
    ("sin-07-delay-sin-argumentos", "ERROR SINTACTICO", "1", "delay();\n"),
    ("sin-08-println-sin-argumentos", "ERROR SINTACTICO", "1", "Serial.println();\n"),
    # E: delay y Serial.println no devuelven valor: nunca dentro de una expresión
    ("sin-09-delay-como-operando", "ERROR SINTACTICO", "1", "float x = delay(1);\n"),
    ("sin-10-println-como-operando", "ERROR SINTACTICO", "1", "x = Serial.println(1);\n"),
    ("sin-11-falta-pc-entre-sentencias", "ERROR SINTACTICO", "2", "float x = 1\nmap(2);\n"),
    ("sin-12-falta-pc-antes-de-llave", "ERROR SINTACTICO", "3", "void setup() {\n    float x = 1\n}\n"),
    ("sin-13-falta-pc-eof", "ERROR SINTACTICO", "1", "map(1)"),
    ("sin-14-falta-llave-eof", "ERROR SINTACTICO", "2", "void setup() {\n    float x = 1;\n"),
    ("sin-15-falta-llave-eof-sentencias", "ERROR SINTACTICO", "3", "void setup() {\n    float x = 1;\nmap(2);\n"),
    ("sin-16-llave-sobrante", "ERROR SINTACTICO", "2", "map(1);\n}\n"),
    # una sentencia no puede ser un identificador suelto ni una expresión suelta
    ("sin-17-identificador-solo", "ERROR SINTACTICO", "1", "y\n"),
    ("sin-18-expresion-incompleta", "ERROR SINTACTICO", "1", "y + 2\n"),
    ("sin-19-declaracion-sin-pc-eof", "ERROR SINTACTICO", "1", "float x = 1"),
    # == no es un token: dos asignaciones seguidas
    ("sin-20-igual-doble", "ERROR SINTACTICO", "1", "x == 1;\n"),
    # int es un tipo de otro lenguaje (anexo F: se acepta léxico o sintáctico)
    ("sin-21-tipo-de-otro-lenguaje", "ERROR SINTACTICO", "1", "int x = 1;\n"),
    ("sin-22-coma-final", "ERROR SINTACTICO", "1", "map(1,);\n"),
    ("sin-23-argumentos-sin-coma", "ERROR SINTACTICO", "1", "map(1 2);\n"),
    ("sin-24-operador-sin-operando", "ERROR SINTACTICO", "1", "x = 1 + ;\n"),
    # C: las definiciones no pueden aparecer dentro de un bloque
    ("sin-25-definicion-anidada-setup", "ERROR SINTACTICO", "2", "void setup() {\n    void loop() {\n    }\n}\nmap(1);\n"),
    ("sin-26-definicion-anidada-loop", "ERROR SINTACTICO", "2", "void loop() {\n    void setup() {\n    }\n}\n"),
    # un tipo no es un operando
    ("sin-27-tipo-como-operando", "ERROR SINTACTICO", "1", "float x = float;\n"),
    # map sin paréntesis no es un operando (no es un identificador)
    ("sin-28-funcion-sin-llamada", "ERROR SINTACTICO", "1", "float x = map;\n"),
    # anexo F: comentario con estilo de otro lenguaje; nuestro analizador
    # lo lee como DIVISION DIVISION y falla en la sintaxis
    ("sin-29-comentario-cpp", "ERROR SINTACTICO", "1", "// comentario de otro lenguaje\n"),
    # anexo F: comentario de bloque que no se cierra
    ("sin-30-comentario-sin-cerrar", "ERROR SINTACTICO", "1", "/* abierto\n"),
    # loop/setup solo encabezan una definición, no una sentencia
    ("sin-31-palabra-reservada-como-sentencia", "ERROR SINTACTICO", "1", "loop = 1;\n"),
    ("sin-32-solo-llaves", "ERROR SINTACTICO", "1", "{ }\n"),
    ("sin-33-asignacion-incompleta-eof", "ERROR SINTACTICO", "1", "x ="),
    # solo espacios y saltos de línea: programa vacío (apartado C)
    ("sin-34-solo-espacios", "ERROR SINTACTICO", "1", "   \n\n\t\n"),
    # la definición necesita void, paréntesis y cuerpo { ... }
    ("sin-35-setup-sin-void", "ERROR SINTACTICO", "1", "setup() {\n}\n"),
    ("sin-36-void-sin-llaves", "ERROR SINTACTICO", "1", "void setup();\n"),
    ("sin-37-void-sin-parentesis", "ERROR SINTACTICO", "1", "void setup { }\n"),
    # la definición no recibe argumentos (falla en int, la línea 1 igual)
    ("sin-38-definicion-con-argumentos", "ERROR SINTACTICO", "1", "void setup(int x) {\n}\n"),
    # declaración: después del tipo viene el identificador
    ("sin-39-declaracion-sin-identificador", "ERROR SINTACTICO", "1", "float = 1;\n"),
    ("sin-40-solo-tipo", "ERROR SINTACTICO", "1", "float;\n"),
    # expresión: dos operadores seguidos y dos operandos sin operador
    ("sin-41-dos-operadores", "ERROR SINTACTICO", "1", "x = 1 * * 2;\n"),
    ("sin-42-dos-operandos", "ERROR SINTACTICO", "1", "x = 1 2;\n"),
    # paréntesis: sin cerrar, sobrante o vacío
    ("sin-43-parentesis-sin-cerrar", "ERROR SINTACTICO", "1", "x = (1 + 2;\n"),
    ("sin-44-parentesis-suelto", "ERROR SINTACTICO", "1", "x = 1);\n"),
    ("sin-45-llamada-sin-cerrar", "ERROR SINTACTICO", "1", "map(1;\n"),
    ("sin-46-llave-en-llamada", "ERROR SINTACTICO", "1", "map{1};\n"),
    # un argumento es una expresión, no una asignación
    ("sin-47-argumento-con-asignacion", "ERROR SINTACTICO", "1", "delay(x = 1);\n"),
    # una sentencia no puede empezar con una cadena ni con un número
    ("sin-48-cadena-como-sentencia", "ERROR SINTACTICO", "1", '"hola";\n'),
    ("sin-49-numero-como-sentencia", "ERROR SINTACTICO", "1", "1 + 2;\n"),
    # no se puede declarar una variable con nombre de palabra reservada
    ("sin-50-nombre-reservado-como-variable", "ERROR SINTACTICO", "1", "float HIGH = 1;\n"),
    # *= no existe: son MULTIPLICACION e IGUAL
    ("sin-51-operador-inexistente", "ERROR SINTACTICO", "1", "x *= 2;\n"),
    # el cierre de comentario solo no es un comentario
    ("sin-52-asterisco-de-comment-suelto", "ERROR SINTACTICO", "1", "*/\n"),
    # EOF al empezar una definición: línea del último token (regla 7.2)
    ("sin-53-void-sin-cuerpo-eof", "ERROR SINTACTICO", "2", "map(1);\nvoid"),
    # Serial.println con letras pegadas atrás
    ("sin-54-println-con-sufijo", "ERROR SINTACTICO", "1", "Serial.printlnx(1);\n"),
    ("sin-55-unario-en-argumento", "ERROR SINTACTICO", "1", "delay(-1);\n"),
    ("sin-56-parentesis-vacio", "ERROR SINTACTICO", "1", "x = ();\n"),
    ("sin-57-doble-punto-y-coma", "ERROR SINTACTICO", "1", "map(1);;\n"),
    # el guion bajo sí forma parte del identificador; el guion, no
    ("sin-58-identificador-con-guion", "ERROR SINTACTICO", "1", "mi-var = 1;\n"),
    # DUDA (registrada en Historico.md): C dice "un programa es una secuencia de
    # una o más sentencias" y las definiciones pueden aparecer "además de sentencias".
    # Lectura estricta: un archivo con SOLO definiciones, sin ninguna sentencia en el
    # nivel superior, no es programa válido y el error cae al EOF (línea del último token).
    ("sin-59-solo-definiciones", "ERROR SINTACTICO", "3", "void setup() {\n    map(1);\n}\n"),
    # no hay operador unario tampoco para +
    ("sin-60-unario-mas", "ERROR SINTACTICO", "1", "x = +1;\n"),
    # += va pegado: con espacio son dos tokens y la asignación queda incompleta
    ("sin-61-compuesto-con-espacio", "ERROR SINTACTICO", "1", "x+ =1;\n"),
    ("sin-62-doble-asignacion", "ERROR SINTACTICO", "1", "x = y = 1;\n"),
    # delay y Serial.println no devuelven valor: tampoco como argumento
    ("sin-63-delay-como-argumento", "ERROR SINTACTICO", "1", "delay(delay(1));\n"),
    ("sin-64-println-como-argumento", "ERROR SINTACTICO", "1", "map(Serial.println(1));\n"),
    # una función sin paréntesis no es una sentencia
    ("sin-65-mapa-sin-parentesis", "ERROR SINTACTICO", "1", "map;\n"),
    # el número termina en la letra: quedan dos piezas pegadas
    ("sin-66-numero-pegado-a-identificador", "ERROR SINTACTICO", "1", "float x = 1abc;\n"),
    # no hay literales hexadecimales
    ("sin-67-hexadecimal", "ERROR SINTACTICO", "1", "float x = 0x1F;\n"),
    # palabra reservada en minúscula como nombre de variable
    ("sin-68-nombre-reservado-minuscula", "ERROR SINTACTICO", "1", "float delay = 1;\n"),
    ("sin-69-mapa-sin-argumentos", "ERROR SINTACTICO", "1", "map();\n"),
    # EOF con la expresión o la llamada a medias: línea del último token
    ("sin-70-expresion-corta-al-eof", "ERROR SINTACTICO", "1", "x = 1 +"),
    ("sin-71-llamada-incompleta-eof", "ERROR SINTACTICO", "1", "Serial.println(1"),
    ("sin-72-parentesis-izq-al-eof", "ERROR SINTACTICO", "1", "map("),
    # los comentarios no se anidan: el primer */ cierra y el resto sobra
    ("sin-73-comentario-no-anidado", "ERROR SINTACTICO", "1", "/* a /* b */ c */\n"),
    ("sin-74-tipo-en-medio-de-expresion", "ERROR SINTACTICO", "1", "x = 1 + float;\n"),
    # paréntesis de más en la definición
    ("sin-75-parentesis-sobrante-en-definicion", "ERROR SINTACTICO", "1", "void setup()) { map(1); }\n"),
    # llave de más al final del programa
    ("sin-76-llave-sobrante-al-final", "ERROR SINTACTICO", "1", "void setup() { map(1); }}\n"),
    # la coma separa argumentos, no integra una expresión
    ("sin-77-coma-en-expresion", "ERROR SINTACTICO", "1", "x = 1, 2;\n"),
    # funciones de Arduino que no existen en este lenguaje: la llamada empieza
    # con un identificador y después hace falta un signo = (apartado F)
    ("sin-78-pinmode", "ERROR SINTACTICO", "2", "void setup() {\n    pinMode(LED_BUILTIN, OUTPUT);\n}\n"),
    # no hay ++
    ("sin-79-incremento", "ERROR SINTACTICO", "1", "x++;\n"),
    # la coma no separa declaraciones
    ("sin-80-coma-en-declaracion", "ERROR SINTACTICO", "1", "float x, y;\n"),
    # después de un identificador declarado solo puede venir = o ;
    ("sin-81-declaracion-con-mas-igual", "ERROR SINTACTICO", "1", "float x += 1;\n"),
    # EOF con líneas en blanco y comentario después del último token:
    # la línea es la del último token (1), no la del final del archivo (4)
    ("sin-82-eof-con-blanco-y-comment", "ERROR SINTACTICO", "1", "x = 1\n\n/* fin */\n"),
    # no hay notación exponencial: 1e5 son dos piezas pegadas
    ("sin-83-notacion-exponencial", "ERROR SINTACTICO", "1", "float x = 1e5;\n"),
]


def main():
    DIR.mkdir(exist_ok=True)
    for viejo in DIR.glob("*.txt"):          # limpia casos renombrados
        viejo.unlink()

    for nombre, esperado, linea, texto in CASOS:
        if esperado not in ("OK", "ERROR LEXICO", "ERROR SINTACTICO"):
            raise SystemExit(f"{nombre}: esperado inválido: {esperado}")
        if esperado == "ERROR LEXICO" and not linea:
            raise SystemExit(f"{nombre}: ERROR LEXICO exige línea")
        # newline="" para que \n y \r\n se escriban tal cual
        with (DIR / f"{nombre}.txt").open("w", encoding="utf-8", newline="") as archivo:
            archivo.write(texto)

    with (DIR / "esperado.csv").open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(["archivo", "esperado", "linea"])
        for nombre, esperado, linea, _ in CASOS:
            escritor.writerow([f"{nombre}.txt", esperado, linea])

    resumen = {}
    for _, esperado, _, _ in CASOS:
        resumen[esperado] = resumen.get(esperado, 0) + 1
    detalle = ", ".join(f"{v} {k}" for k, v in sorted(resumen.items()))
    print(f"generados {len(CASOS)} casos en {DIR.relative_to(RAIZ)}/ ({detalle})")


if __name__ == "__main__":
    main()
