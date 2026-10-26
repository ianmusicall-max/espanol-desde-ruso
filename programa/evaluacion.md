# Evaluación: cómo sabe el alumno (y el profesor) que avanza

## 1. Los instrumentos y su ritmo

| Cuándo | Instrumento | Formato | Dónde está |
|---|---|---|---|
| Cada día | **Итог**: tres preguntas de autoevaluación (sí / no) | Al final de cada lección | `curso/semana-XX/dia-N.md`, apartado 6 |
| Cada día | **Salida**: la producción del día | Texto, audio o vídeo que el alumno guarda en su carpeta de progreso | columna `salida` del calendario |
| Sábado | **Mini-test** de la semana | 10-15 ítems con clave | lección del sábado, apartado 3 |
| Sábado de la 2.ª semana de la unidad | **Prueba de la unidad** | 15 ítems de opción múltiple: léxico 6 · gramática 6 · ortografía y pronunciación 3 (desde la unidad 14 el tercer bloque es «expresiones») | lección `tipo: prueba` |
| Semana 21-22 | **Simulacro y examen de A1** | Lectura + audio, escrita, oral (simulacros) y examen de 40 ítems | unidad 11 |
| Semana 47-48 | **Prueba integral de A2** | 40 ítems de gramática y léxico | unidad 24 |
| Semanas 49 y 51 | **Simulacros completos del DELE A2** | Las 4 pruebas, repartidas en 7 sesiones de 30 minutos | fase final |
| Semana 52 | **Examen final del curso** y **proyecto «Un año en español»** | 60 ítems + presentación de 3 min + texto de 150-200 palabras | fase final |

## 2. Reglas de decisión

- **Prueba de unidad < 10/15**: antes de empezar la unidad siguiente se
  repite el sábado de repaso de la unidad (la lección `repaso` de su primera
  semana) y se vuelve a hacer la prueba. Dos días, no más: el calendario tiene
  el día 365 de reserva y los domingos pueden absorber un retraso de un día.
- **Examen A1 < 60 %**: una semana de repaso con las lecciones de la unidad
  11 antes de empezar A2.
- **Simulacro DELE A2**: se aprueba cada grupo por separado al 60 %, y los
  grupos **no** son «lo receptivo» frente a «lo productivo»: **grupo 1 =
  comprensión de lectura + expresión escrita**; **grupo 2 = comprensión
  auditiva + expresión oral**. Cada prueba vale 25 puntos y cada grupo, 50; se
  necesitan 30 en cada uno. El grupo que no llegue decide los cuatro días de
  refuerzo de la semana 50. Consecuencia práctica: la escritura floja hunde a
  la lectura buena, y el oral flojo hunde al audio bueno.
- **Examen final < 60 %**: el alumno termina el curso en A2.1 y se le propone
  el plan de 3 meses de repaso de la semana 52 antes del DELE real.

## 3. Rúbrica para las producciones (escrita y oral)

Adaptada de los criterios del DELE A2. Cuatro criterios, cada uno de 0 a 3;
se aprueba con 7/12 y ningún criterio a 0.

| Criterio | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| **Adecuación** (cumple la tarea: tema, extensión, registro, formato) | Hace todo lo que pide la tarea, con la extensión y el registro adecuados | Cumple la tarea con alguna omisión | Cumple a medias o con el registro equivocado | No cumple la tarea |
| **Coherencia** (orden, conectores, se entiende) | Ideas ordenadas, conectores sencillos bien usados | Se entiende con esfuerzo mínimo | Frases sueltas, se entiende a trozos | No se entiende |
| **Corrección** (gramática y ortografía / pronunciación del nivel) | Errores escasos que no impiden entender | Errores frecuentes pero el sentido llega | Errores sistemáticos en estructuras del nivel (ser / estar, artículo, pasados) | Errores que impiden entender |
| **Alcance** (léxico y estructuras del nivel) | Usa el léxico y las estructuras de la unidad con variedad | Usa lo básico de la unidad | Léxico muy limitado, repite | No usa lo del nivel |

Para la oral se añade **pronunciación** (de 0 a 3, con la lista de
interferencias de `contrastiva-ru-es.md`, §1) y se aprueba con 9/15.

## 4. Formato de la prueba de unidad (15 ítems)

Copiado del Тест del cuaderno de referencia. Cada ítem es una frase con un
hueco y cuatro opciones (tres en el tercer bloque).

```
1. Лексика (6 ítems, 1 punto cada uno)
   Прочитайте предложения и выберите правильный ответ.
2. Грамматика (6 ítems, 1 punto cada uno)
   Прочитайте предложения и выберите правильный ответ.
3. Орфография и произношение (3 ítems, 1 punto cada uno)   [desde la U14: Выражения]
   Выберите слово, написанное правильно. / Выберите слово с другим звуком.
Всего: ___ / 15
```

Los distractores se construyen **con los errores de la lista negra** del
rusohablante (`contrastiva-ru-es.md`, §8): la opción equivocada es la que el
alumno ruso diría, no una forma al azar.

## 5. Listas can-do

Al cerrar A1 (semana 22) y A2 (semana 52) el alumno marca una lista de 20
descriptores «Я умею…» tomados de los objetivos de las unidades del nivel
(columna `objetivos` del calendario). Se guarda con la fecha; la de A1 se
vuelve a mirar en la semana 48 para ver el camino recorrido.

## 6. Registro de progreso

Cada alumno lleva una carpeta `progreso/` propia (fuera del repositorio) con:

- `salidas/` — la producción de cada día, con el nombre `S01-D1.md` o `.m4a`.
- `pruebas.csv` — `fecha, unidad, puntos, de, observaciones`.
- `errores.md` — la lista personal de errores, con la regla al lado, que se
  actualiza en las semanas 22 y 48.

No hay plataforma: un alumno autónomo que escribe su puntuación en una tabla
ve su progreso con más claridad que con una barra de colores. Si algún día
hay bot o web con cuentas, estos tres archivos son el modelo de datos.
