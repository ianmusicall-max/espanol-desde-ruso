# Español desde el ruso · contexto para Claude Code

Curso de español para rusohablantes desde cero, un año, 30 minutos al día,
A0 → A2 (DELE A2). Lo mantiene un profesor con máster en lenguas (español
nativo, inglés). Las lecciones están en ruso con el español como lengua meta;
la documentación del programa, en español.

## Dónde está cada cosa

- `programa/calendario.yaml` — **la única fuente de verdad** de días, semanas,
  unidades y temas. 365 días, 24 unidades + fase final + día 365 de reserva.
  Cualquier cuenta de turnos, horas o temas sale de aquí, nunca de un .md.
- `programa/plan-anual.md` — lectura en prosa; su tabla la genera
  `scripts/plan.py --actualizar` y `tests/` exige que esté al día.
- `programa/metodologia.md` — la sesión de 30 minutos, los diez principios, la
  retirada progresiva del ruso, el plan de fonética.
- `programa/contrastiva-ru-es.md` — qué le ayuda y qué le estorba al
  rusohablante; la «lista negra» de 20 errores que alimenta los distractores
  de las pruebas.
- `programa/alineacion-mcer-pcic.md` — PCIC A1-A2, DELE A2, horas. Escrito de
  memoria porque las páginas del Cervantes no se pudieron descargar: cotejar.
- `programa/evaluacion.md` — instrumentos, reglas de decisión, rúbrica.
- `referencias/` — análisis estructural de los libros de referencia. No se
  copia contenido ajeno; los PDF no se versionan.
- `curso/plantilla-leccion.md` — la forma de toda lección. `curso/semana-XX/dia-N.md`.
- `scripts/` — `plan.py` (modelo), `validar.py` (forma de las lecciones),
  `escribir_leccion.py` (borrador con Claude), `exportar_anki.py` (léxico →
  TSV), `construir_sitio.py` (Markdown → `docs/`).
- `tests/test_curso.py` — `.venv/bin/python -m unittest tests.test_curso`.

## Reglas

1. **Una lección = 30 minutos exactos.** Los títulos de apartado llevan la
   franja («## 3. Новое (6–16 мин)»); `validar.py` exige 0 → 30 contiguo.
2. **Una lección = un punto nuevo y 6-10 palabras.** Si no cabe, son dos días
   y se cambia el calendario, no la duración.
3. **Toda lección de tipo `leccion` lleva «⚠️ Контраст с русским»** con el
   error predecible. Es lo que hace que el curso sea «desde el ruso».
4. **El tema de la lección es el del calendario** (`tema_es` igual, carácter
   por carácter). Si hay que cambiarlo, se cambia primero el YAML.
5. **Las claves (Ответы) son obligatorias** si hay ejercicios.
6. **Nada generado con Claude se publica sin revisión del profesor.** El
   generador escribe en `curso/` con `revisado: false` en el frontmatter;
   el profesor lo pone en `true` al revisar.
7. No se inventan datos (precios, fechas históricas, cifras) en las lecciones
   de cultura: si no se sabe, se pone un marcador `[VERIFICAR]`.
8. Variación España / América: se enseña lo más extendido y se señala la
   variante con 🌎, nunca se impone una.

## Pendiente de revision del profesor

- **La unidad 5 mezcla los dos titulos del apartado 2**: la semana 9 usa
  Фонетика y la semana 10, Аудирование. La regla esta en `metodologia.md` §3 y
  dice que dentro de una unidad no se mezclan. Hay que elegir uno para las
  catorce sesiones.
- **Once entradas de vocabulario se ensenan dos veces** en semanas distintas, de
  528. `scripts/revisar_lexico.py` las lista con el dia de cada aparicion.
- **Los titulos de ejercicio siguen en ruso en la unidad 7**, pero
  `metodologia.md` §6 pide «espanol + ruso» desde ahi. O se retocan las
  semanas 13-14 (dos lineas por leccion) o se corre la tabla de §6 hasta la
  unidad 12, que es el salto de nivel y una frontera mas natural.
- **Las 69 lecciones de las semanas 4 en adelante son borradores**
  (`revisado: false`) y el sitio las marca como tales. Las 21 primeras estan
  revisadas.

## Progreso del lector, sin registro (2026-10-26)

El sitio es estático: GitHub Pages sirve archivos, no ejecuta nada. Registro
con usuario y contraseña necesita un servidor, pero «cerré la página, ¿dónde
iba?» no: lo resuelve el propio navegador.

`docs/progreso.js` guarda dos cosas en `localStorage`: `curso.hechas` (los
números marcados) y `curso.ultima` (la última abierta). De ahí salen el botón
«continuar» de la portada, el contador propio, las marcas del índice y el botón
de marcar al pie de cada lección.

Lo que hay que saber si alguien lo toca:

- **El contrato entre el HTML y el guion son tres atributos**:
  `<article data-leccion="N">` en la lección, `<li data-leccion="N">` en el
  índice y los ids `marcar-caja`, `enlace-siguiente`, `continuar`, `empezar`,
  `mio`, `borrar-progreso`. Cambiar uno no rompe ninguna página: deja de
  funcionar el progreso en silencio. Por eso hay pruebas que los fijan.
- **El guion busca `article[data-leccion]` y no `[data-leccion]` a secas.** En
  el índice el primero que aparece es un `<li>` de la lección 1, así que con el
  selector corto abrir «todas las lecciones» movía «la última leída» al
  principio del curso y «continuar» mandaba al día 1.
- **`[hidden]{display:none!important}` en el CSS.** El `[hidden]` del navegador
  pierde contra `.boton{display:inline-block}`, así que «continuar» se veía como
  un botón naranja vacío en la primera visita.
- **Todo nace oculto y lo enciende el navegador.** Un contador en cero y un
  botón «continuar» que no lleva a ninguna parte desaniman en la primera visita.
- **Toda lectura y escritura va en try/catch.** En navegación privada
  `localStorage` puede tirar al leerlo; hay una prueba en navegador que lo
  bloquea y exige que la lección se lea igual y sin un solo error de JS.
- **Solo las lecciones escritas entran en `CURSO_DIAS`**: «continuar» no puede
  mandar a una página que no existe.
- **El aviso es parte de la función**: en los tres idiomas se dice que el
  progreso vive solo en ese navegador, que no hay registro y que no viaja a otro
  teléfono. Prometer una cuenta que no existe sería peor que no ofrecer nada.

**Lo que esto NO hace**: no sincroniza entre aparatos ni sobrevive a un borrado
de datos del navegador. Eso ya pide cuentas de verdad —un servicio aparte
(Supabase, Firebase), responsabilidad sobre datos personales, contraseñas que se
pierden y soporte— y se decidió no hacerlo hasta que alguien lo pida.

**De paso, el tachado.** `~~h~~otel` y `~~Yo gusto~~` salían con las tildes a la
vista en ocho lecciones: Python-Markdown no trae tachado. La extensión `Tachado`
de `construir_sitio.py` lo añade en ocho líneas, sin dependencia nueva. Importa
porque es donde el sentido depende de que se vea tachado: la letra muda y la
forma incorrecta. Una prueba recorre las cien lecciones publicadas y falla si
queda una tilde doble.

## Estado (2026-10-26)

- Programa anual completo (365 días) y documentación del método.
- **100 lecciones escritas** (semanas 1-14 enteras y los dos primeros días de
  la 15): unidades 1 a 7 completas, 908 tarjetas de vocabulario. Las 21
  primeras revisadas; el resto son borradores.
- Sitio público en `docs/` con portada, índice, «О курсе», contacto y política
  de privacidad. Tres idiomas (ru/es/en), tema claro y oscuro, y progreso del
  lector guardado en su navegador sin registro. La publicidad se configura en `web/sitio.yaml` y está
  apagada; sin identificador de AdSense no se carga nada de terceros.
- Falta activar GitHub Pages (Settings → Pages → rama main, carpeta /docs).
- Pendiente: lecciones 101-365, audio de los diálogos (TTS), más libros de
  referencia, y lo de «Pendiente de revision del profesor» de arriba.
