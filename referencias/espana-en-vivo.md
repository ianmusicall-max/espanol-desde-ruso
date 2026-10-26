# España en vivo — análisis estructural

> Leído el 2026-10-26 del PDF del profesor (Google Drive). **No se copia ningún
> contenido**: aquí van la estructura, la tipología de secciones y las
> decisiones pedagógicas, que es para lo que sirve esta carpeta.

## Ficha

| | |
|---|---|
| Título | *España en vivo* · «Курс современного испанского языка для продолжающих» |
| Autores | Georgy Nuzhdin (idea original), Paloma Martín Lora-Tamayo (la audionovela), Carmen Marín Estremera (los talleres y buena parte de los debates) |
| Edición | 3.ª ed., Айрис-пресс, 2009 (© 2006). **368 pp.** ISBN 978-5-8112-3600-8 |
| Lengua vehicular | Ruso, con el español como lengua meta |
| Extensión | 6 unidades + 3 pruebas finales + claves |
| Material sonoro | CD con la audionovela, grabada por **diez** locutores españoles |
| Nivel declarado | A partir de **180 horas** y ~1400 palabras, con pasados y las bases de subjuntivo y condicional; pero el libro dice estar pensado sobre todo para **300+ horas** |

> **El título español y el ruso son del MISMO libro**, y eso costó una
> confusión: en la carpeta del profesor hay dos escaneos distintos de él,
> `Espana_en_vivo.pdf` y `624873791-…-Для-продолжающих.pdf`. No son dos obras.
> Se vio al abrir la portada del segundo, no al leer los nombres de archivo.

**Es el mismo equipo de autores que *Español en vivo***, y esto es lo que
responde la pregunta de los niveles que quedó abierta el 2026-10-26: el autor
**sí** tiene material por encima de B1, y es este. Por contenido y por horas
declaradas, está en territorio **B2**.

## Cómo está construido

Seis unidades **de estructura idéntica**, cada una sobre uno o dos problemas de
la España contemporánea: inmigración, terrorismo, paro, vivienda, familia,
drogas, ocio. Cada tema se aborda desde varios ángulos —prensa, debate,
entrevista, literatura y diálogo hablado—, y hay una prueba final cada dos
unidades, más claves detalladas que incluyen comentario cultural.

**Lo que define el libro es que es modular.** Dentro de cada unidad corren en
paralelo los mismos «cursos», y el libro declara explícitamente que se puede
trabajar de dos maneras:

- **en horizontal**: se toma un tema (p. ej. la familia) y se recorren todos
  los aspectos — prensa, debate, gramática, habla, pragmática…;
- **en vertical**: se toma un aspecto (p. ej. la lengua hablada) y se recorre
  en las seis unidades.

### Las secciones de cada unidad, en orden

Medido sobre el índice de la Unidad I (*España y los españoles*, pp. 7-52), que
es el reparto real y no el que uno supondría:

| Sección | Páginas | Cuánto ocupa |
|---|---|---|
| Precalentamiento | 8-10 | 2 |
| Texto | 10-12 | 2 |
| Ejercicios de poslectura (+ **de traducción** como subapartado propio) | 12-15 | 3 |
| Debate | 15-19 | 4 |
| Gramática reflexiva | 19-24 | 5 |
| **Audionovela** | 24-35 | **11** |
| Pragmática | 35-43 | 8 |
| Interculturalidad | 43-49 | 6 |
| Taller | 49-52 | 3 |

**La audionovela y la pragmática se llevan 19 de las 45 páginas: el 42% de la
unidad.** Es lo que más sorprende al ver el índice, porque por la descripción
uno esperaría que el texto y la gramática mandaran, y ocupan 7 páginas entre
los dos. El libro invierte el reparto habitual de un manual: lo hablado pesa
más que lo leído.

Dos detalles que el prefacio no dice y el índice sí: la gramática se llama
**«reflexiva»** (el prefacio en ruso la llamaba inductiva), y **la audionovela
lleva título propio en cada unidad** —en la I, *Buscando un hueco*—, o sea que
cada entrega es un capítulo con nombre, no un anexo.

### Las secciones, una por una

| Sección | Qué hace |
|---|---|
| Introducción | Ejercicios breves que presentan el problema: léxico básico y hechos |
| Texto | O una página para todo el grupo, o 2-3 páginas repartidas entre alumnos para comentarlas luego juntos |
| Ejercicios post-texto | Comprensión y léxico nuevo. **Cierran siempre con un bloque de traducción ruso↔español**, y eso es obligatorio en todas las unidades |
| Debate | Textos polémicos y fragmentos de entrevista para montar una clase-discusión; al final, expresiones útiles para debatir |
| Gramática inductiva | Los puntos que peor se asientan: artículo, subjuntivo, énfasis, condicionales, intensificadores |
| **Audionovela** | Una historia seriada en diálogos que atraviesa el libro entero, en lengua hablada de hoy. Cada entrega cierra con glosario coloquial, ejercicios de léxico, de comprensión y de diferencias socioculturales |
| Pragmática | Cómo conseguir algo hablando: abrir y cerrar una conversación, quejarse, aconsejar, pedir, aceptar o rehusar, halagar |
| Interculturalidad | Diferencias entre España y otros países (en particular Rusia): rituales, refranes, colores, chistes, cómo ven los españoles al extranjero |
| Taller creativo | Leer textos literarios y escribir textos propios de distinto tipo |

Dos secciones llevan icono: trabajo en parejas o grupo, y ejercicios de
audición.

**La audionovela es la pieza que sostiene el resto**: la pragmática y la
interculturalidad no se explican y ya, sino que se ven funcionando dentro de la
historia. El libro lo dice tal cual: la audionovela es la ilustración viva de
esas dos secciones.

## Qué se toma

1. **La historia seriada con personajes fijos, como columna vertebral.** Este
   curso ya tiene a **Ana e Iván** desde la lección 1, pero hoy son dos nombres
   que reaparecen, no una historia que avanza. Convertirlos en un hilo con
   trama —y grabarlo— es exactamente lo que este libro demuestra que funciona,
   y llega justo cuando el audio ya está montado (`generar_audio.py`).
2. **La sección de pragmática como curso propio.** «Quejarse, aconsejar, pedir,
   rehusar» no es vocabulario ni gramática: es la tercera cosa, y el PCIC la
   recoge en su inventario de funciones, con el que este curso ya se alinea.
   Hoy las funciones están repartidas por las lecciones; aquí se ve el valor de
   darles un recorrido reconocible.
3. **Interculturalidad más allá del error gramatical.** El bloque
   «⚠️ Контраст с русским» de este curso es la firma de la casa, pero solo
   contrasta **lengua**. Este libro contrasta **costumbre**: rituales, refranes,
   cómo se ve al extranjero. Es la extensión natural del bloque que ya existe, y
   para un rusohablante que va a vivir en España vale tanto como la gramática.
4. **El bloque de traducción ruso↔español obligatorio al cerrar.** Es un tipo
   de ejercicio que este curso casi no usa y que aquí es sistemático. Aprovecha
   justo lo que un rusohablante trae puesto.
5. **La prueba cada dos unidades.** Aquí hay evaluación en las semanas 45-52;
   este libro la distribuye a lo largo de todo el recorrido.

## Qué NO se toma

- **La modularidad horizontal/vertical.** Está pensada para un profesor con un
  grupo que elige qué aspectos cubrir. Este curso es un camino de 30 minutos al
  día en el que el alumno no decide nada, y esa es su ventaja: no hay que
  elegir, se abre y se estudia. Tomar la modularidad sería romperlo.
- **Los temas.** Terrorismo, drogas y paro son materia B2 para debatir en
  grupo; aquí el alumno está en A1-A2 y estudia solo.
- **El formato de clase presencial**: debates de grupo, textos repartidos entre
  alumnos, trabajo en parejas. No hay grupo.

## Dónde se aplica

| Qué | Dónde |
|---|---|
| Historia seriada con Ana e Iván | `programa/metodologia.md` y la plantilla de lección; encaja con el audio ya construido |
| Curso de pragmática | `programa/alineacion-mcer-pcic.md` §3 (funciones PCIC), hoy repartidas |
| Interculturalidad en el bloque de contraste | `programa/contrastiva-ru-es.md`, que hoy es solo lingüístico |
| Traducción ru↔es como tipo de ejercicio | `curso/plantilla-leccion.md`, apartado de práctica |
| Evaluación periódica | `programa/evaluacion.md` |

**Para el segundo año (B1).** Este libro arranca donde el curso actual termina
—180 horas, 1400 palabras, pasados y bases de subjuntivo— así que su nivel de
entrada es casi exactamente la salida prevista de los 365 días (182,5 horas).
Como modelo de continuación encaja; como fuente de temas, no, por lo dicho
arriba.
