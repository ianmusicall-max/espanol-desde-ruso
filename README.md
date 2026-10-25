# Español desde el ruso · Испанский с нуля для русскоговорящих

Curso de español para rusohablantes adultos, **desde cero**, **30 minutos al
día durante un año**: de A0 a **A2** (MCER), con preparación para el DELE A2.
Las lecciones están escritas en ruso con el español como lengua meta; la
documentación del programa, en español, para el profesor.

## Qué hay

| Carpeta | Qué contiene |
|---|---|
| `programa/calendario.yaml` | **El programa entero**: 365 días, 52 semanas, 24 unidades + fase final. Cada día tiene tema (es/ru), foco y la producción que el alumno entrega. Es la única fuente de verdad. |
| `programa/plan-anual.md` | El año en prosa y la tabla de unidades (generada del YAML). |
| `programa/metodologia.md` | Cómo es una sesión de 30 minutos, los diez principios, la retirada progresiva del ruso, el plan de fonética. |
| `programa/contrastiva-ru-es.md` | Análisis contrastivo ruso → español: lo que ayuda, lo que estorba, los 20 errores típicos, falsos amigos. |
| `programa/alineacion-mcer-pcic.md` | Alineación con el MCER, los inventarios del Plan Curricular del Instituto Cervantes y la estructura del DELE A2. |
| `programa/evaluacion.md` | Pruebas, reglas de decisión, rúbrica, registro de progreso. |
| `referencias/` | Análisis de los libros de referencia (hoy: Точка Ру A2, cuaderno 2). Sin copiar contenido. |
| `curso/` | Las lecciones. Semanas 1 y 2 completas y revisadas (unidad 1, 14 sesiones). Plantilla en `curso/plantilla-leccion.md`. |
| `vocabulario/` | El léxico de las lecciones en TSV para Anki (generado). |
| `docs/` | El curso como sitio web estático, para leerlo en el móvil (generado). |
| `scripts/` | Herramientas (abajo). |
| `tests/` | Pruebas que mantienen todo coherente. |

## Cómo se usa

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python scripts/plan.py                      # las 24 unidades
.venv/bin/python scripts/plan.py --semana 3           # qué toca cada día de la semana 3
.venv/bin/python scripts/plan.py --dia 120            # un día por su número

.venv/bin/python scripts/validar.py                   # la forma de todas las lecciones
.venv/bin/python scripts/exportar_anki.py             # léxico → vocabulario/*.tsv
.venv/bin/python scripts/construir_sitio.py           # lecciones → docs/ (abrir docs/index.html)
.venv/bin/python -m unittest tests.test_curso         # todo coherente
```

**Para escribir las lecciones que faltan** (semanas 3-52) hay un generador que
redacta un borrador con Claude a partir del calendario, la plantilla, la
metodología, el análisis contrastivo y las lecciones ya escritas de la unidad:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
.venv/bin/python scripts/escribir_leccion.py --semana 3 --dia 1 --ver   # ver el prompt, sin gastar
.venv/bin/python scripts/escribir_leccion.py --semana 3 --dia 1         # escribir el borrador
.venv/bin/python scripts/escribir_leccion.py --semana 3 --todos         # la semana entera
```

Cada borrador se guarda con `revisado: false` y pasa por el validador. **El
profesor lo lee, corrige lo que haga falta y pone `revisado: true`.** Lo que
hay que mirar primero: el contraste con el ruso (¿es verdad?), las claves, el
número de palabras y que la salida sea la del calendario. El prompt está
partido en tres bloques (estable, unidad, día) para que la caché de la API
pague el contexto una vez por unidad y no por lección; el generador lleva
activado el *fallback* de la API por si una petición es declinada.

## La forma del año

```
Semanas  1-22   A1   Unidades 1-11    77 h    U11 = repaso y examen de A1
Semanas 23-48   A2   Unidades 12-24   91 h    U24 = repaso integral de A2
Semanas 49-52   Final                 14 h    dos simulacros DELE A2, proyecto, examen
Día 365         Reserva                        182,5 horas en total
```

Una unidad son dos semanas: lunes a viernes lección nueva (un punto, 6-10
palabras), sábado repaso (el segundo sábado, prueba de 15 ítems), domingo
cultura. Una sesión de lección: razminka (3 min) → fonética o audio (3) →
nuevo con contraste ruso-español (10) → tres ejercicios (10) → producción (3)
→ cierre (1). El validador no deja pasar una lección que no dure 30 minutos.

## Lo que hace que sea «desde el ruso»

- Cada lección tiene un apartado «⚠️ Контраст с русским» con el error que el
  alumno ruso va a cometer antes de que lo cometa.
- El orden de los contenidos sigue las dificultades del rusohablante: artículo,
  ser/estar y posición del adjetivo en las unidades 2-4; *gustar* pronto porque
  es «мне нравится»; los tres pasados a través del aspecto ruso.
- Los distractores de las pruebas son los errores de la «lista negra», no
  formas al azar.
- Doscientas palabras internacionales desde el primer día: el alumno no
  empieza de cero.

## Lo que falta

- Lecciones de las semanas 3-52: se generan con `escribir_leccion.py` y se
  revisan. Las de la unidad 1 son el modelo.
- Audio de los diálogos: cada lección marca `[AUDIO]` donde iría; hoy el
  alumno lee en voz alta y se graba.
- Más libros de referencia: cada uno se analiza en `referencias/` antes de
  tocar nada.
- Cotejar `alineacion-mcer-pcic.md` con las páginas oficiales del Instituto
  Cervantes (no se pudieron descargar al escribirlo).

## Licencia

Contenido propio del autor del curso. Los libros de referencia conservan los
derechos de sus autores y no se incluyen.
