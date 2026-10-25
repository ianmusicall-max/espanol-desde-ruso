# Metodología: cómo está hecho el curso y cómo es una sesión de 30 minutos

Para el profesor. Las lecciones (en `curso/`) están escritas para el alumno,
en ruso con el español como lengua meta. Este documento explica las decisiones
que hay detrás, para que quien escriba o revise una lección las respete.

## 1. Quién es el alumno y qué se le promete

- Adulto rusohablante, sin español previo, que estudia **solo** (sin profesor
  presente) o con tutoría ligera, **30 minutos al día, 365 días**.
- Promesa: al terminar el año **se desenvuelve en A2** (MCER) y está preparado
  para presentarse al **DELE A2**. No se promete B1: 182 horas no dan para más
  con honestidad (ver `alineacion-mcer-pcic.md`, §4).
- El ruso es la lengua de las instrucciones y de las explicaciones en A1 y se
  retira progresivamente en A2 (§6).

## 2. Diez principios

1. **Un punto nuevo por día.** Cada lección presenta UNA estructura gramatical
   o UN campo léxico. Si hacen falta dos, son dos días. Es lo que cabe en 30
   minutos y lo que se recuerda al día siguiente.
2. **De 6 a 10 palabras nuevas por lección**, elegidas por frecuencia y por
   utilidad para la tarea del día, nunca por completar una lista temática. Las
   demás palabras del tema se recogen en los domingos de cultura y en los
   repasos. Objetivo: ~900 palabras en A1, ~1 900 acumuladas en A2.
3. **Gramática explícita y contrastiva.** El alumno ruso viene de una
   tradición escolar analítica: espera la regla, la tabla y el porqué. Se le
   da, pero **después** de ver la estructura en un ejemplo y **siempre** con
   el contraste con el ruso («⚠️ Контраст с русским»). El contraste no es un
   adorno: es lo que convierte un curso genérico en un curso «desde el ruso».
4. **Input antes de output.** Cada lección abre con un diálogo o texto breve
   que contiene la estructura nueva, se lee (y se escucha, si hay audio) antes
   de explicar nada.
5. **Práctica en escalera**: formas aisladas → frases con banco de palabras →
   diálogo con huecos → producción guiada. Tres ejercicios por lección, nunca
   un ejercicio libre antes de dos controlados (tomado del cuaderno de
   referencia, ver `referencias/tochka-ru-a2-tetrad-2.md`, §3).
6. **Salida diaria**: la lección termina con algo que el alumno PRODUCE (6-10
   frases escritas, un audio de 1 minuto, un diálogo grabado). Está en la
   columna `salida` del calendario y es obligatoria.
7. **Repetición espaciada.** Las palabras de cada lección van a un mazo
   (`scripts/exportar_anki.py` las extrae de las lecciones) y la razminka de
   cada día empieza con 10 tarjetas. Sin esto, el 60 % del léxico se pierde en
   un mes.
8. **Pronunciación desde el día 1 y ortografía desde el día 4.** La tilde es
   una regla, no un adorno; un rusohablante que escribe sin tildes escribe mal
   en el DELE. Tres minutos de fonética al día durante las primeras ocho
   semanas; después, un minuto dentro de la razminka.
9. **Español neutro con la variación señalada.** Se enseña la forma más
   extendida (coger/tomar, vosotros/ustedes, perfecto/indefinido) con una nota
   «🌎» cuando España y América difieren. No se enseña una variante «pura».
10. **Autoevaluación constante**: tres preguntas al cierre de cada lección,
    mini-test cada sábado, prueba de 15 ítems cada dos semanas, listas can-do
    al final de cada nivel (ver `evaluacion.md`).

## 3. La sesión de 30 minutos (día de lección)

| Minutos | Sección (en la lección) | Qué pasa | Por qué |
|---|---|---|---|
| 0-3 | **1. Разминка** | 10 tarjetas del mazo (ayer + hace una semana) y una pregunta de lo de ayer | Activar la memoria antes de meter nada nuevo |
| 3-6 | **2. Фонетика** (A1, semanas 1-8) / **2. Аудирование** (después) | Un sonido o contraste con 6-8 palabras, leídas en voz alta y grabadas; o 1 minuto de audio con 2 preguntas | La interferencia fonética rusa se fija en las primeras semanas o no se quita nunca |
| 6-16 | **3. Новое** | Пример (diálogo/texto de 6-10 líneas) → Объяснение (regla + tabla) → ⚠️ Контраст с русским | Input, regla, contraste. Diez minutos es el máximo de atención para explicación |
| 16-26 | **4. Практика** | Упражнение А (controlado), Б (semicontrolado), В (traducción ru→es o diálogo con huecos) | La escalera. Las claves van al final de la lección |
| 26-29 | **5. Выход** | La producción del día (la `salida` del calendario) | Sin producir no hay adquisición |
| 29-30 | **6. Итог** | Tres preguntas de autoevaluación (sí/no) y «añade las palabras de hoy al mazo» | Cierre y enganche con mañana |

Los números de los apartados y las franjas de minutos **van en los títulos**
(`## 3. Новое (6–16 мин)`), y `scripts/validar.py` comprueba que empiecen en
0, sean contiguas y terminen en 30. No se puede escribir una lección de 45
minutos sin que el validador se ponga en rojo.

### Sábado (repaso)

| Minutos | Sección | Qué pasa |
|---|---|---|
| 0-3 | 1. Разминка | 20 tarjetas (toda la semana) |
| 3-13 | 2. Повторение | Resumen de la semana en una tabla; 2 ejercicios mezclados |
| 13-23 | 3. Мини-тест | 10-15 ítems con clave y puntuación |
| 23-28 | 4. Разбор ошибок | Cada error → la regla → una frase nueva correcta |
| 28-30 | 5. Итог | Lista de control de la semana (5 «puedo…») |

El sábado de la segunda semana de cada unidad es la **Prueba de la unidad**
(`tipo: prueba`): 15 ítems de opción múltiple (léxico 6, gramática 6,
ortografía/pronunciación 3), copiando la forma del Тест del cuaderno de
referencia. Menos de 10/15 → se repite la semana de repaso antes de seguir.

### Domingo (cultura)

| Minutos | Sección | Qué pasa |
|---|---|---|
| 0-3 | 1. Разминка | 10 tarjetas |
| 3-15 | 2. Материал | Un texto, canción, vídeo o mapa sobre el mundo hispano (en español, con glosas) |
| 15-20 | 3. Слова | 10-20 palabras del material, con el ruso al lado |
| 20-28 | 4. Задание | Verdadero/falso + transferencia («y en tu país…»), 5 frases |
| 28-30 | 5. Итог | Qué me sorprendió (una frase) |

El domingo es ligero a propósito: un día de descanso real al séptimo día haría
que el alumno rompiera la cadena; un día de carga completa haría que la
abandonara. Treinta minutos agradables mantienen el hábito.

## 4. Tipología de ejercicios

Los 40 tipos del cuaderno de referencia están catalogados y asignados a
unidades en `referencias/tochka-ru-a2-tetrad-2.md`, §2. Reglas de uso:

- **Banco de palabras antes de los huecos** en A1 y hasta la unidad 18.
- **Modelo resuelto (Модель:)** antes de cualquier transformación.
- **Pista de tiempo entre paréntesis** —(наст.), (прош.), (буд.)— cuando la
  forma no se deduce del contexto.
- **Traducción ruso→español** como ejercicio В desde la unidad 3: es el que
  destapa la interferencia (artículo, ser/estar, posición del adjetivo). Lleva
  clave comentada: no solo la frase correcta, sino «aquí el ruso te empuja
  a…».
- **Las fórmulas de instrucción son fijas** (lista en §5 del análisis):
  Прочитайте, Дополните, Соедините, Выберите, Проспрягайте, Поставьте в
  правильном порядке, Исправьте ошибки, Переведите, Ответьте на вопросы,
  Расскажите, Опишите, Напишите. El alumno no tiene que descifrar qué se le
  pide.

## 5. El contraste con el ruso

El análisis completo está en `contrastiva-ru-es.md`. En cada lección el
apartado «⚠️ Контраст с русским» hace tres cosas, en este orden:

1. Dice qué hace el ruso en ese punto (en una frase).
2. Dice qué hace el español y en qué se diferencia.
3. Da el **error predecible** («Вы захотите сказать…») y la forma correcta.

Y cuando el ruso AYUDA (gustar = «мне нравится», reflexivos = -ся, el
imperfecto = несовершенный вид), se dice con la misma claridad: el paralelo es
un atajo y hay que usarlo.

## 6. El ruso se retira poco a poco

| Unidades | Instrucciones | Explicación gramatical | Títulos de ejercicio |
|---|---|---|---|
| 1-6 | ruso | ruso | ruso |
| 7-11 | ruso | ruso | español + ruso |
| 12-18 | español + glosa en ruso | ruso | español |
| 19-24 | español | español con el contraste en ruso | español |

Al final del año el alumno lee instrucciones en español, que es lo que se va a
encontrar en el DELE. El contraste con el ruso no desaparece nunca: es el
valor del curso.

## 7. Pronunciación: el plan de ocho semanas

| Semana | Foco | Interferencia rusa que se corrige |
|---|---|---|
| 1 | Vocales, b=v, h muda | Reducción de o/a átonas (аканье); б≠в |
| 2 | c/z/qu, g/j, ñ, ll/y, r/rr, ch, x | j no es [ʒ]; ñ no es [nj] estricto; rr vibrante |
| 3 | Sílaba tónica y tilde | «Acento móvil» ruso ≠ acento escrito con reglas |
| 4 | d y t dentales; d intervocálica suave | d/t alveolares y duras del ruso |
| 5 | Sin palatalización ante e/i | te, de, ni, li palatalizados (тэ/те) |
| 6 | Diptongos ie/ue; hiatos | Rupturas y reducciones |
| 7 | Entonación: pregunta, exclamación, enumeración | Curva descendente rusa en preguntas |
| 8 | Enlace y ritmo silábico | Ritmo acentual ruso; consonantes finales ensordecidas |

Después de la semana 8 la fonética vive dentro de la razminka (un minuto) y
en los días de repaso.

## 8. Audio

El curso es texto. Cada diálogo y cada ejercicio de fonética **indica** qué hay
que leer en voz alta y grabar. Opciones para tener audio:

- El profesor graba los diálogos (ideal: dos voces).
- Texto a voz: cualquier TTS en español de calidad sirve para los diálogos de
  A1; en `escribir_leccion.py` queda un marcador `[AUDIO]` donde iría el
  archivo. Generar audio con TTS automáticamente es trabajo pendiente
  (ver `README.md`, «Lo que falta»).

## 9. Cómo se escribe una lección nueva

1. `scripts/plan.py --dia N` dice qué toca ese día (tema, foco, salida).
2. Se copia `curso/plantilla-leccion.md` o se llama a
   `scripts/escribir_leccion.py --semana S --dia D`, que redacta un borrador
   con Claude a partir del calendario, la plantilla, esta metodología y las
   lecciones ya escritas de la unidad.
3. **El profesor revisa**: el borrador no se publica sin leerlo. Lo que hay que
   mirar primero: el contraste con el ruso (¿es verdad?), las claves (¿están
   bien?), el léxico (¿6-10?), la salida (¿coincide con el calendario?).
4. `scripts/validar.py` comprueba la forma; las pruebas (`tests/`) comprueban
   que todo el curso siga coherente.
5. `scripts/construir_sitio.py` regenera `docs/` para leer la lección en el
   móvil.

## 10. Lo que este curso no hace, a propósito

- No enseña el subjuntivo salvo en fórmulas fijas (¡Que aproveche!): es B1.
- No separa «español de España» y «español de América»: señala la variación.
- No usa transliteración cirílica de las palabras españolas después de la
  semana 1: el alumno aprende a leer con las reglas, que son regulares.
- No incluye ilustraciones propias: donde el cuaderno de referencia usa
  viñetas, aquí la escena se describe en una línea.
