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

## Publicidad y plataforma (2026-10-26)

El usuario pidió «subirlo a WordPress o algo parecido» y meterle Google AdSense.
Lo que se encontró al ir a hacerlo cambia cuál de las dos cosas hace falta.

**AdSense no pide WordPress. Pide un dominio propio.** Los requisitos son
contenido original (100 lecciones), una forma de contacto, una política de
privacidad, y un sitio que sea tuyo. `ianmusicall-max.github.io/espanol-desde-ruso`
es una ruta dentro del dominio de GitHub. Y hay una prueba técnica, no una
opinión: **`ads.txt` tiene que estar en la RAÍZ del dominio**, y ahí cae en
`/espanol-desde-ruso/ads.txt`, donde AdSense no mira nunca. Mudarse a un
`algo.wordpress.com` gratis no arregla nada: cambia un subdominio ajeno por
otro.

**WordPress además cuesta y sigue necesitando el dominio.** Las redes de
terceros como AdSense están limitadas al plan Business (la cuenta del usuario
factura en rublos: ₽17.988/año), mientras que el dominio propio sobre GitHub
Pages son unos 10-15 USD al año con el alojamiento y el HTTPS gratis. No se
pudo abrir `wordpress.com/support/monetize-your-site/` ni las páginas de ayuda
de AdSense desde este contenedor (el proxy devuelve 403), así que la regla del
plan viene de foros y de la documentación citada en ellos: **cotejar antes de
pagar**, igual que `alineacion-mcer-pcic.md`.

**El límite que decide los ingresos no es técnico.** AdSense no sirve anuncios
a usuarios dentro de Rusia desde marzo de 2022 y desactivó las cuentas de
editores rusos en agosto de 2024. El curso está en ruso, así que lo que se
puede monetizar es el público rusohablante FUERA de Rusia: Alemania, España,
Israel, Kazajistán, Estados Unidos. Eso ya se había decidido al elegir público,
pero es lo que hay que mirar antes de contar con una cifra.

**Lo que falta para cobrar, y no es código**: un CMP certificado por Google
para el tráfico de la UE y el Reino Unido (obligatorio desde el 16/1/2024, y
Suiza desde el 31/7/2024). La banda de cookies de aquí **no** lo es: es un
aviso. El CMP gratis de Google está dentro de AdSense, en «Privacidad y
mensajes». Sin él no se sirven anuncios personalizados.

**Lo que el generador ya hace solo**, con solo rellenar `web/sitio.yaml`:

- `ads.txt` en la raíz, pero **solo si hay cliente**: un ads.txt vacío es peor
  que ninguno. Y `CNAME` solo si el dominio no es de github.io, porque un CNAME
  con github.io dentro deja el sitio sin servir.
- Los tres bloques, la banda de cookies y los párrafos de la política de
  privacidad se encienden juntos. Vacío = cero scripts de terceros, que es lo
  que deja que la política diga la verdad.
- **El bloque de cabecera NO va antes del título.** Ahí ocupaba la primera
  pantalla entera del móvil y empujaba la lección fuera de la vista, que es lo
  que las políticas de AdSense llaman diseño engañoso. Va en el primer `<h2>`,
  después de los objetivos del día. Se vio en una captura, no razonándolo.
- `main()` avisa de lo que falta para cobrar: correo, dominio propio y CMP.

**`scripts/exportar_wordpress.py`** existe para que la decisión no cueste
trabajo: deja un XML que WordPress importa en Herramientas → Importar. Una
entrada por lección, una categoría por unidad y una página con el índice
—hace falta porque un blog ordena por fecha descendente y un curso se lee del 1
al 100—. Dos cosas que no son de forma: **las lecciones sin revisar entran como
BORRADOR**, porque la regla 6 tiene que sobrevivir al cambio de plataforma, y
el bloque de contraste lleva el estilo dentro, porque es la firma del curso y
es lo único que un tema ajeno se llevaría por delante del todo.

### Netlify, preguntado el mismo día

**No resuelve lo que bloquea AdSense, y lo dice su propio soporte**: con
`xxx.netlify.app` «no tienes acceso ni control del dominio netlify.app», que es
exactamente el problema de `github.io`. La respuesta de Netlify a quien
preguntó por AdSense fue registrar un dominio propio y enlazarlo. O sea que el
dominio hay que comprarlo igual, y con él GitHub Pages ya sirve en la raíz.

**Lo que Netlify sí añade** sobre GitHub Pages: formularios sin servidor —un
contacto sin publicar el correo, que es justo lo que AdSense pide y hoy
falta—, funciones (el camino a las cuentas de verdad del apartado anterior), y
control de cabeceras y redirecciones.

**Lo que quita, y es lo que decide**: las cuentas nuevas desde septiembre de
2025 tienen un bote de 300 créditos al mes —unos 15 GB y unos 20 despliegues
de producción— y **el sitio SE PAUSA al agotarlo**. Con anuncios puestos, un
pico de visitas deja la web caída justo cuando más vale. GitHub Pages tiene
100 GB al mes de límite blando y no apaga nada. No se pudo abrir
`netlify.com/pricing` desde aquí (proxy, 403), así que los números vienen de
blogs de terceros: **cotejar antes de mover nada**.

`netlify.toml` está en el repo por si algún día se decide, con el comando de
construcción y las cabeceras. GitHub Pages lo ignora. Tres pruebas lo leen y
lo comprueban contra el repo —que el guion exista, que la carpeta publicada sea
la que el generador escribe y que `ads.txt` no se cachee de más—, porque un
archivo de despliegue que no se usa es el primero que se queda viejo, y el día
que se conecte el fallo sería un sitio vacío con un «Page not found» que no
apunta aquí.

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
- Para AdSense falta un dominio propio, un correo de contacto en
  `web/sitio.yaml` y el CMP de Google. El código ya está: ver la nota de
  arriba.
- Pendiente: lecciones 101-365, audio de los diálogos (TTS), más libros de
  referencia, y lo de «Pendiente de revision del profesor» de arriba.
