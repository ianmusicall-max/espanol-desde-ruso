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
- `programa/historia.md` — el arco de Ana e Iván: 24 episodios, uno por unidad.
  Los títulos y sinopsis viven en `calendario.yaml` (campo `episodio` de cada
  unidad); el .md los explica. Hay pruebas que exigen que coincidan.
- `programa/test-nivel.yaml` — las 14 preguntas del test de nivel, cada una con
  la unidad que la ensena y el error del rusohablante que encarna su
  distractor. El error va en ruso (lo lee el alumno) y en español (lo revisa
  el profesor).
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
- **Trece entradas de vocabulario se ensenan dos veces** en semanas distintas,
  de 956, y todas son de las semanas 1 a 14. `scripts/revisar_lexico.py` las
  lista con el dia de cada aparicion.
- **Los titulos de ejercicio siguen en ruso en la unidad 7**, pero
  `metodologia.md` §6 pide «espanol + ruso» desde ahi. O se retocan las
  semanas 13-14 (dos lineas por leccion) o se corre la tabla de §6 hasta la
  unidad 12, que es el salto de nivel y una frontera mas natural.
- **Las catorce preguntas del test de nivel** (`programa/test-nivel.yaml`,
  2026-10-26) estan en `revisado: false` y la pagina lo avisa. Hay que
  comprobar que cada distractor sea de verdad el error que dice y que la unidad
  asignada sea donde el curso lo ensena.
- **Las 105 lecciones de las semanas 4 en adelante son borradores**
  (`revisado: false`) y el sitio las marca como tales. Las 21 primeras estan
  revisadas.
- **El orden de los pasados: se recomendo NO cambiarlo** (2026-10-26, de
  `referencias/espanol-en-vivo.md`). Nuzhdin pone el indefinido antes que el
  perfecto porque en casi toda Hispanoamerica el indefinido ocupa su lugar.
  Pero la **tabla de `alineacion-mcer-pcic.md` §2 pone el perfecto en A1 y el
  indefinido en A2**: es la secuencia del Instituto Cervantes, y la salida de
  este curso es el DELE A2, que es de Cervantes y peninsular. Ademas el
  perfecto es morfologicamente mas barato (haber + participio) que dos
  paradigmas con una docena de raices irregulares, que es lo que importa a
  30 minutos diarios desde cero.
  **Lo que la regla 8 pedia no era reordenar sino marcar**, y eso faltaba: el
  `contraste_ru` de la unidad 9 senalaba coger/tomar pero no la variacion del
  propio tiempo. Se anadio la marca 🌎 («hoy comi» / «hoy he comido»). Las
  lecciones de la semana 18 aun no estaban escritas, asi que no costo nada.
  Queda abierto solo si el profesor discrepa del PCIC.
- **Las tablas de conjugacion**: 19 lecciones las llevan completas. Nuzhdin las
  evita y usa oposiciones minimas (1.ª/2.ª sg., 1.ª/3.ª sg., 3.ª sg./3.ª pl.).
  Se puede dejar la tabla como consulta y practicar por oposiciones.
- **La audionovela: hecha** (`programa/historia.md`, 2026-10-26). Queda que el
  profesor decida si quiere los episodios 1-7, que caen en semanas ya
  revisadas y pedirian reescribir lecciones dadas por buenas. Del 8 en
  adelante entran con la leccion, sin retrofit.

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

### El conmutador de idioma llevaba a 404 (2026-10-26)

Lo encontró `scripts/revisar_adsense.py` al estrenarse: **215 enlaces internos
rotos**, y llevaban meses ahí.

`pagina()` escribe el conmutador apuntando a la MISMA página en el otro idioma,
que es lo correcto para la portada, el índice y las estáticas. Pero las 100
lecciones existen **solo en ruso** —son el curso— y los 7 documentos del
programa **solo en español**. En esas 107 páginas el conmutador apuntaba a una
URL que no existe: el lector pulsaba «ES» en una lección y le salía un 404. Y
el `hreflang` declaraba esas mismas URL inexistentes como traducciones.

Ninguna prueba lo vio porque se comprobaba que el conmutador llevara a la misma
página, no que esa página ESTUVIERA. Es la forma del error que más se repite en
este tipo de sitios: la regla era correcta y el caso que no cumple la regla no
estaba contemplado.

- `pagina(..., traducida=False)` para esas dos familias (y desde el 27 también
  el test de nivel). El `hreflang` **desaparece**, no se redirige: `hreflang`
  declara que dos URL son la misma página traducida, y apuntarlo a la portada
  le cuenta a Google algo falso, que es peor que callarse.

- El roto 215 era otro: un documento del programa citaba a otro por su nombre
  `.md`, correcto al leerlo en el repositorio y roto en la web.
  `_enlaces_entre_documentos` lo reescribe a `.html`, con el prefijo `ref-` si
  viene de `referencias/`.
- Cuatro pruebas: ninguna página con un enlace roto, el conmutador de una
  lección no lleva a ninguna parte (ver abajo), una página sin traducir no
  declara `hreflang`, y las que SÍ están en tres idiomas conservan los suyos
  —el arreglo no podía llevárselos por delante—.

### Y la portada tampoco servía: el conmutador, tercera versión (2026-10-27)

Lo reportó el profesor en cuanto usó el sitio: **«cuando cambio el idioma se
regresa a la página del inicio»**. La segunda versión mandaba a la portada de
ese idioma en esas 108 páginas, y sobre el papel era razonable —mejor que un
404—. En la mano no: pulsas «ES» esperando *esta* página en español y apareces
en la portada, **habiendo perdido la lección que estabas leyendo**.

Esa versión dejó, donde no hay gemela, **ninguno de los tres como enlace**: los
otros dos apagados y con el motivo en el `title` («Эта страница есть только на
русском»), y el activo resaltado pero inerte. **El `title` es lo que la hizo
fallar también** —ver la cuarta versión, abajo—.

Tres cosas que importan si alguien lo toca:

- **El idioma ACTIVO también era un enlace, y también movía.** Apuntaba a
  `index.html` como los demás, así que pulsar «ru» desde una lección en ruso te
  sacaba de la lección. Se vio al probarlo en navegador, no leyendo el código.
- **Apagados y no escondidos**: el conmutador es la señal de que el sitio tiene
  tres idiomas. Quitarlo en 108 de 125 páginas lo haría parecer monolingüe.
- **El resaltado colgaba de `.idiomas a[aria-current]`**, con la `a` dentro. Al
  dejar de ser un enlace, en esas 108 páginas no se veía cuál era el idioma
  activo. Ahora el selector es `.idiomas [aria-current]`, y hay una prueba que
  lo fija.

La prueba que exigía el comportamiento anterior se reescribió, no se aflojó:
ahora exige que el conmutador de una lección **no contenga ni un `<a>`**. Y hay
otra nueva que exige lo contrario donde sí hay traducción —las cinco páginas de
tres idiomas—, porque el arreglo no podía apagar el conmutador en todo el
sitio.

### Y la cuarta: apagados no bastaba, hay que DECIRLO (2026-10-27)

El profesor volvió el mismo día: **«verifiqué y no cambian los idiomas en la
página»**. Y tenía razón las tres veces, porque las tres versiones fallaban en
lo mismo y ninguna lo arregló:

| | Qué hacía | Qué se veía |
|---|---|---|
| 1.ª | enlazaba a la gemela | 404 (215 enlaces rotos) |
| 2.ª | enlazaba a la portada | «se regresa a la página del inicio» |
| 3.ª | no hacía nada | «no cambian los idiomas» |

**Lo que faltaba no era un destino mejor: era que la página DIJERA que aquí no
hay versión en ese idioma.** El motivo estaba en el `title` del botón, o sea en
un tooltip que **en el móvil no existe** y que en escritorio pide pararse un
segundo encima. Sin eso, un botón apagado no se lee como «esta página solo está
en ruso»: se lee como un botón roto. Por eso la 3.ª versión, que era correcta
en lo que hacía, se denunció igual que las otras dos.

Ahora los dos idiomas ajenos **se pulsan** y lo que abren es un aviso visible en
la propia cabecera:

> Эта страница есть только на русском. **Открыть главную страницу (Español) →**

O sea que la portada del otro idioma sigue estando —era lo útil de la segunda
versión— pero como una **elección del lector** y no como un salto que le pasa
encima. Nadie se mueve sin querer y nadie se queda sin saber por qué.

Lo que importa si alguien lo toca:

- **El aviso nace oculto y lo enciende el navegador**, como el resto del sitio.
  Sin JavaScript los botones no abren nada, y un aviso suelto en la cabecera
  diciendo «esta página solo existe en ruso» no explicaría nada de nada.
- **El destino viaja en un `data-portada` y NADIE lo revisaba.**
  `revisar_adsense.enlaces_rotos` se salta los `<script>` (desde el 26) y
  también el `href=""` vacío que rellena el navegador, así que la ruta relativa
  de ese botón no la miraba ningún revisor. Es exactamente el fallo que esta
  suite ya cazó dos veces por el mismo motivo —el conmutador de idioma y las
  tarjetas del mapa de unidades: una ruta escrita sin tener en cuenta en qué
  carpeta está la página—, así que hay una prueba que resuelve los dos destinos
  contra el disco en cuatro páginas de tres profundidades distintas.
- **El aviso ocupa la fila entera de la cabecera** (`flex:1 0 100%;order:4`) y
  no un hueco entre los botones y la luna. La barra se acababa de arreglar el 26
  y fallaba por cuatro píxeles con tres enlaces: una frase más dentro de la fila
  la vuelve a partir.
- **`solo_este_idioma` está en los tres idiomas y se escoge por el de la
  PÁGINA**, no por el del botón: en una lección rusa el aviso llega en ruso,
  que es el idioma del que lo lee. Lo único que cambia con el botón es el nombre
  del idioma que se ofrece.

La prueba de la tercera versión se reescribió al contrato nuevo —ningún `<a>`,
dos botones apagados, el activo en un `<span aria-current>`— y se le sumaron las
dos que faltaban: que el aviso exista, nazca oculto y traiga su texto, y que la
portada que ofrece exista de verdad.

### `scripts/revisar_adsense.py`

Dice qué le falta al sitio para que lo aprueben, y **solo lee**. Separa tres
cosas que desde fuera se ven igual: lo comprobado contra el sitio construido
(LISTO), lo que bloquea de verdad (FALTA) y lo que no se puede comprobar desde
aquí (MIRAR). Hoy: 100 lecciones y 179.511 palabras listas; falta el correo de
contacto y el dominio propio.

Los dominios gratis de las cuatro plataformas —`github.io`, `netlify.app`,
`vercel.app`, `wordpress.com`— se marcan por igual, y hay una prueba con las
cuatro: si una se escapara, el revisor diría «listo» y el rechazo llegaría un
mes después sin decir por qué.

**AdSense no cuesta nada**: no hay cuota de alta ni mensual, no piden un mínimo
de visitas para solicitarlo, el reparto es del ~68% para el editor y se cobra a
partir de 100 USD acumulados. Un rechazo no penaliza y se puede volver a pedir.
O sea que **solicitar el alta hoy es gratis**, y lo único de toda esta lista que
cuesta dinero es el dominio.

### AdSense encendido (2026-10-27)

El dominio se compró en Cloudflare Registrar (`espanoldesderuso.com`, 10,46
USD/año al coste) y con él `scripts/revisar_adsense.py` pasa a **10 listo · 0
falta**. Lo que queda son las tres cosas que no se pueden comprobar desde este
contenedor: que la web cargue, el candado y el CMP.

**La cuenta del profesor es UNA, estándar, `ca-pub-6339208855562328`.** Esto
costó un rodeo que conviene no repetir: la primera pantalla que se vio decía
«No se aprobó su cuenta — cierre su otra cuenta», y se leyó como que había dos
cuentas en conflicto. **Era una lectura equivocada**: esa pantalla es la
sección *AdSense para YouTube*, que dentro de la MISMA cuenta tiene su propio
problema de duplicados. La parte de webs estaba sana —Sitios, Anuncios, Pagos
con la información ya dada—, y el identificador es el mismo en las dos.

La señal que lo resuelve: si la barra lateral enseña **Sitios**, **Anuncios** y
**Pagos**, es la cuenta estándar completa, aunque la sección de YouTube se
queje. El `pub-…` de la URL es el mismo para las dos.

**Los tres bloques siguen vacíos a propósito.** `anuncio()` no escribe el
contenedor sin el id de bloque, así que hoy el sitio lleva el script de la
cabecera y el `ads.txt` y nada más: eso es suficiente para los **anuncios
automáticos**, que es lo que AdSense coloca mientras el profesor no cree
bloques manuales. Si algún día los crea, van en `adsense.bloques` y aparecen
los tres huecos (arriba, entre teoría y ejercicios, y al pie).

**De paso, una prueba que dependía de producción.** `TestLaPublicidad._con()`
partía del `web/sitio.yaml` real, así que `_con()` sin argumentos significaba
«sin anuncios» **por casualidad**: funcionaba solo mientras ese fichero
estuviera vacío. Al poner el identificador, las dos pruebas del caso «sin
anuncios» se pusieron en rojo sin que nadie hubiera tocado el generador. Ahora
el ayudante apaga la publicidad y la analítica a mano, y la prueba que quiera
anuncios los pide. Es el mismo error de siempre con otra cara: lo que se prueba
y lo que corre tienen que ser lo que la prueba DICE, no lo que había ese día.

### El dominio: precios buscados el 2026-10-26

El usuario pidió «el más barato de todos». La respuesta corta es que **el
precio del primer año no es el precio**: lo que se paga todos los años es la
renovación, y ahí el orden cambia del todo.

- **La trampa**: `.store` cuesta ~1 USD el primer año y **~67 la renovación**;
  `.online` ~2 y **~35**. Son los que salen primero al buscar «dominio barato».
- **Lo más barato de verdad**: `.top`, con renovación ~1-4 USD. `.xyz` es
  barato al registrar pero renueva por ~11-13.
- **`.com` al coste**: Cloudflare Registrar lo vende sin margen, ~10,44 USD/año
  y la renovación igual, con WHOIS privado incluido. Spaceship anda por ~9,98 y
  Porkbun ~10,67-11,08. Namecheap renueva bastante más caro (~14-18).

**Se recomendó `.com` y no `.top`**, aunque la pregunta era por el más barato:
la diferencia es de unos 8 USD al año y el dominio es la cara del curso. `.top`
y `.click` cargan con fama de spam, y este sitio tiene que pasar por un revisor
de AdSense y que un lector se fíe al compartirlo por WhatsApp. Es el único sitio
de todo el proyecto donde ahorrar ocho dólares cuesta credibilidad.

**El GitHub Teacher Toolbox da un dominio gratis un año** (vía Name.com, 25
extensiones elegibles) a profesores verificados, y el usuario lo es. Pide
verificación como docente de una institución, y la renovación ya es a precio
normal. Queda anotado como la vía gratis del primer año.

**Nada de esto se pudo verificar en su fuente oficial**: el proxy de este
contenedor bloquea `education.github.com`, `name.com`, `netlify.com`,
`wordpress.com` y las páginas de ayuda de Google. Los números vienen de
comparadores de terceros, varios con enlaces de afiliado, y **se contradicen
entre sí**: cotejar en la web del registrador antes de pagar, igual que
`alineacion-mcer-pcic.md`. Tampoco hay DNS aquí —ni `google.com` resuelve—, así
que la disponibilidad de un nombre no se puede comprobar desde el repositorio.

### `scripts/poner_dominio.py`

El día de la compra hay tres pasos y es fácil dejarse uno: escribir el dominio
en `web/sitio.yaml`, reconstruir, y crear los registros DNS. El guion hace los
dos primeros e imprime el tercero. `--ver` enseña sin tocar.

- **Edita solo la línea del dominio**, con una expresión regular y no con
  `yaml.dump`: medio `sitio.yaml` son comentarios que explican cada ajuste, y
  un volcado los borraría sin que nadie lo notara hasta necesitarlos. Hay una
  prueba que cuenta los comentarios y las líneas.
- **Rechaza lo que dejaría el sitio sin servir**: `www.` delante, `https://`
  dentro, y los subdominios gratis de las cinco plataformas. Un `CNAME` mal
  escrito no sirve nada y GitHub Pages no dice por qué: la página no carga y ya.
- **Las cuatro A y las cuatro AAAA de GitHub Pages** van en una constante con
  una prueba que cuenta que sean cuatro y cuatro: recortada la lista, el
  dominio resuelve unas veces sí y otras no según a qué IP caiga, que es el
  fallo más difícil de leer que hay.
- **Avisa de lo de Cloudflare**: los registros tienen que ir en gris («DNS
  only»). Con el proxy naranja puesto, GitHub no puede validar el dominio, no
  emite el certificado y «Enforce HTTPS» se queda apagado para siempre.

### El correo de contacto (2026-10-26)

`espanoldesderuso@gmail.com`, una cuenta **aparte y hecha para el curso**, que
es lo que se le recomendó al usuario: publicar una dirección en una web abierta
atrae spam, y así no cae en la personal. La suya no aparece en ninguna parte del
repositorio ni del sitio, y no debe aparecer.

Con esto `scripts/revisar_adsense.py` pasa a **8 listo y 2 falta**, y los dos
que faltan son el mismo: el dominio propio.

**Las lecciones llevan cinco correos inventados** (`ivan.petrov@gmail.com` y
compañía) y eso es material didáctico, no una fuga: la lección 3-5 enseña a
dictar una dirección en español («arroba», «punto»). La prueba que vigila esto
excluye el CUERPO de las lecciones por esa razón, y hay una segunda que
comprueba que la cabecera y el pie que el generador pone alrededor **no** traen
ninguno: la excepción vale para lo que escribe el profesor, no para lo que
genera el código.

La primera versión de esa prueba no distinguía las dos cosas y se puso en rojo
con un correo de la lección 3-5. El fallo era de la prueba y no del sitio, y
vale anotarlo: una regla de seguridad demasiado ancha acaba desactivándose, que
es peor que no tenerla.

## El audio de las lecciones (2026-10-26)

El usuario preguntó si añadir audios. **Sí, y cuesta 1,30 USD una sola vez**
para las 100 lecciones, no una suscripción: medido con `--ver`, son 3.543
frases distintas y 81.505 caracteres a ~16 USD el millón. Proyectado a las 365
lecciones, menos de 5 USD. El curso ya traía 82 marcas `[AUDIO]` en 72
lecciones esperando esto desde el principio.

`scripts/generar_audio.py` deja un MP3 por frase en `docs/audio/` y un índice
`indice.json`. `construir_sitio.py` lo lee y pone un ▶ delante de cada frase
que esté locutada.

Lo que hay que saber si alguien lo toca:

- **El nombre del archivo es un hash del pedido entero** (texto + voz + modelo
  + instrucciones), no un número de lección. Así «Buenos días» se locuta y se
  paga UNA vez aunque salga en diez lecciones, volver a correr el guion no
  vuelve a pagar nada, y cambiar de voz es otro archivo en vez de una mezcla
  silenciosa de dos voces. Es la cache de imágenes del proyecto de salud.
- **Se miran TODAS las columnas de la tabla, no la primera.** La primera
  versión miraba solo la primera y en las tablas de fonética eso es la LETRA
  («a»): la palabra de ejemplo («casa») está en la cuarta y es justo la que
  hay que oír. Se vio en una captura del reproductor ya montado, no
  razonándolo. Son 0,49 USD más y vale cada céntimo.
- **La columna rusa se cae sola por el cirílico**, y hay una prueba que recorre
  las 3.543 frases y falla si una trae una letra rusa: una voz española
  leyendo «Спокойной ночи» sería el audio inútil y el doble de caro.
- **Fuera la transcripción fonética** (`[a]`, `/kasa/`): es un símbolo para
  leer con los ojos y una voz diría «corchete a corchete».
- **Se escribe en `.parcial` y se renombra**, y un MP3 de cero bytes no cuenta
  como locutado: una descarga cortada dejaría un archivo que el sitio serviría
  como bueno y el lector pulsaría ▶ sin que sonara nada.
- **Un solo `<audio>` para toda la página**, creado en JS y reutilizado: con
  uno por frase el navegador abriría decenas de conexiones. Al empezar una se
  para la anterior, que es lo que se quiere al ir comparando frases.
- **El reproductor solo se carga en las lecciones que tienen algún botón**, y
  sin `docs/audio/` el sitio se construye igual y sin un solo ▶. El audio se
  genera por tandas, así que «algunas frases sí y otras no» es el estado normal
  durante un tiempo y ninguna página puede romperse por eso.
- **`docs/audio/` SE VERSIONA** desde el 2026-10-26, que es el día que el
  audio se generó de verdad. Antes estaba en `.gitignore` y se probó el
  reproductor con tonos de ffmpeg que **se borraron antes de subir nada**:
  publicar un pitido donde el lector espera una voz es peor que no tener
  audio. Lo único que sigue ignorado es `docs/audio/*.parcial`.

**El camino quedó abierto el 2026-10-26**, y costó encontrar los dos
escalones porque el segundo no se ve hasta que se tropieza con él:

1. **`OPENAI_API_KEY`**: va como secreto del entorno, nunca pegada en el chat
   ni en el repo.
2. **`api.openai.com` tiene que estar en los dominios permitidos** del
   entorno. Con la clave puesta y el dominio cerrado no se llega a OpenAI
   siquiera; la señal de que YA está abierto es que `curl` devuelva **401** y
   no `000`: 401 significa que la petición llegó y solo faltaba la clave.
   La caja de *Allowed domains* no aparece hasta elegir el nivel «Limited»,
   que es donde se atascó el profesor dos veces.

### Hecho el 2026-10-26: 3.543 audios, 1,30 USD, sin un solo fallo

**La voz es `shimmer` y la eligió el profesor**, oyendo las tres candidatas con
la misma frase (`--muestra 3 --voz …`). Está puesta como `VOZ` por defecto; si
alguien la cambia, que sea después de volver a escucharlas, porque es otro hash
y son 1,30 USD otra vez.

**Se generan en paralelo** (`HILOS = 6`). De una en una son hora y media y casi
todo es esperar a que OpenAI conteste; de seis en seis, unos diez minutos. No
más de seis a propósito: el límite de peticiones de la cuenta es lo siguiente
que se rompería, y un 429 se paga en reintentos.

**El tamaño se calculó mal DOS veces, y conviene saber por qué**: primero 50 MB
a ojo, luego 97 MB extrapolando de la muestra… y salieron **164 MB**. El error
está en que la muestra son las frases más LARGAS, y la media real es de 23
caracteres: una frase corta tiene el mismo encabezado y los mismos silencios de
guarda que una larga, así que el coste por carácter no es constante. Lo medido
de verdad: **179 minutos en 3.543 archivos**, 3,0 s de media.

**Se publican a 64 kbps mono y lo decidió el profesor**, sobre las dos muestras
a la vez. Vienen de OpenAI a 128 kbps mono 24 kHz, que para voz es tirar bits
que el oído no recoge. La cuenta que decidió:

    128 kbps → 164 MB hoy · 598 MB con las 365 lecciones
     64 kbps →  92 MB hoy · 299 MB con las 365 lecciones
                            (el límite de GitHub Pages es 1024 MB)

**Se recodificó ANTES del primer commit, y eso es lo que importa**: git guarda
el historial para siempre, así que subir los de 128 y recodificar después
dejaría el repositorio cargando con los dos juegos. El nombre NO cambia —es la
llave del índice— y se escribe aparte y se renombra encima, igual que el
`.parcial` del generador: si ffmpeg se corta a la mitad, lo que queda es el
original intacto y no un MP3 truncado que el sitio serviría como bueno.

**Comprobado en navegador, no deducido**: 4.225 botones en 94 lecciones, el ▶
suena, y al pulsar otro se para el anterior. La primera comprobación dio «no se
creó ningún `<audio>`» y **el fallo era de la prueba**: el reproductor usa
`new Audio()`, que no inserta nada en el DOM. La señal observable es el
`aria-pressed` del botón, que solo se pone a `true` si `play()` resolvió.

Anthropic **no tiene servicio de voz**, así que el audio no lo puede poner
Claude: tiene que venir de un TTS de fuera. OpenAI es el que está programado
(1,30 USD, sin cuenta de nube) pero no es el único: Azure, Polly y Google
tienen capa gratis que cubriría los 81.505 caracteres, y la voz del propio
profesor —nativo y profesor de lenguas— sería mejor que cualquiera de las
tres. Cambiar de proveedor es tocar una función; el hash, el ▶ y el
reproductor valen igual.

**`--muestra N` y `--voz`** (2026-10-26). Cambiar de voz es otro hash, o sea
1,30 USD otra vez, así que hay que poder oírla ANTES: `--muestra 5` locuta
cinco frases por céntimos. Coge las más **largas** y no las primeras, porque
por orden de lección la primera es la letra «a», que no dice nada de cómo
suena. Y la voz entra en el nombre del archivo, así que dos voces conviven en
disco y se pueden comparar sin que la segunda pise a la primera —y el índice
nunca mezcla dos—. Hay prueba de las dos cosas.

## Los PDF del profesor: tres de cuatro son escaneos (2026-10-26)

El usuario compartió una carpeta de Drive con cuatro manuales. **El conector de
Google Drive funciona** —busca y lee archivos suyos, y el tamaño no estorba—,
pero aquí el problema era otro.

| Archivo | Peso | Capa de texto |
|---|---|---|
| `...Нуждин-Г-Espanol-en-Vivo.pdf` | 56,8 MB | **no** |
| `...Нуждин-Курс...Для-продолжающих.pdf` | 51,9 MB | **no** (369 páginas vacías) |
| `610554902-Испанский-Нуждин.pdf` | 46 MB | **no** |
| `Espana_en_vivo.pdf` | 30,6 MB | **sí** (184 páginas) |

Los dos que el usuario señaló como principales son justo los dos ilegibles. Un
escaneo no tiene texto que extraer, así que no es un límite del conector.

**Las tres vías para sacar el texto están cerradas desde aquí**, y conviene que
quede escrito para no volver a recorrerlas: `read_file_content` devuelve vacío
porque no hay nada que devolver; `download_file_content` entrega base64 y 56 MB
se convierten en ~75 MB de texto que no caben en el contexto; y
`drive.google.com` está bloqueado por el proxy del contenedor, así que tampoco
se puede descargar con `curl`. Hay `pdftoppm`, `pdftotext` y `pypdf`, pero no
`tesseract`: sin OCR local no hay forma de leer un escaneo.

**La salida es que el OCR lo haga Google**: abrir el PDF en Drive con
«Abrir con → Documentos de Google» crea un documento con el texto reconocido, y
ese sí se lee entero. Puede que solo convierta parte de un libro grande. La
alternativa segura son capturas de las páginas que hagan falta —el índice y una
unidad completa bastan para un análisis estructural— porque las imágenes sí se
leen.

**Probar si un PDF tiene texto sin descargarlo** se hace con una consulta de
búsqueda, `fullText contains 'que'` sobre la carpeta: los que no salen son
escaneos. Sale barato y evita descargas inútiles.

### Los dos libros son uno, y el curso base es otro (corregido el 2026-10-26)

El profesor pasó los dos escaneos por «Abrir con → Documentos de Google». El
OCR **no corrió**: el .docx trae 16 páginas como IMÁGENES y cero texto. Pero
16 páginas bastan, porque son las del prefacio y el índice, que es donde un
manual explica su método. Las imágenes sí se leen.

Al abrir la portada apareció el error: **`Espana_en_vivo.pdf` y
`624873791-…-Для-продолжающих.pdf` son el MISMO libro**, dos escaneos de
*España en vivo* / «Курс современного испанского языка для продолжающих»
(3.ª ed., Айрис-пресс, 2009, 368 pp.). Antes se habían dado por dos obras
distintas leyendo solo los nombres de archivo.

O sea que la serie son **dos** libros y no tres: *Español en vivo* (base, desde
cero) y *España en vivo* (continuación, B2).

### `referencias/espanol-en-vivo.md` — el curso base

Lo que vale de este libro es el método, y **tres de sus decisiones chocan con
este curso**. Ninguna se tocó: son decisiones del profesor, y la regla 4 pide
cambiar antes el YAML.

- **El orden de los pasados.** Aquí el perfecto entra en la semana 18 y el
  indefinido después; Nuzhdin defiende el orden contrario, y su argumento
  principal es que en casi toda Hispanoamérica el indefinido ocupa el lugar
  del perfecto. Eso **choca con la regla 8** —enseñar lo más extendido—, que
  empujaría a su orden. Es la decisión de más peso que queda abierta.
- **Las tablas de conjugación.** Nuzhdin las evita a propósito y usa
  oposiciones mínimas (1.ª/2.ª sg., 1.ª/3.ª sg., 3.ª sg./3.ª pl.): dice que la
  tabla hace que el alumno la reconstruya entera para encontrar una forma.
  Este curso usa tabla completa en **19 lecciones**.
- **Los átonos antes.** Él los mete desde el principio y por una razón
  contrastiva explícita: evitar el orden ruso «я его вижу». Aquí los reflexivos
  entran en la 9 y el objeto directo en la 13, ya con esa advertencia puesta;
  o sea que el contraste existe, solo que más tarde.

Y lo que se confirma mirando los dos libros juntos: **la audionovela atraviesa
la serie entera**, no es un recurso del libro avanzado. En el base trabaja el
léxico y la gramática de su propia lección.

### `referencias/espana-en-vivo.md`

La continuación de la serie: un manual de **B2** sobre la España contemporánea,
del mismo equipo. **Eso contesta la pregunta de niveles que quedó abierta**: el
autor sí tiene material por encima de B1.

Y su nivel de entrada —180 horas, 1400 palabras, pasados y bases de subjuntivo—
es casi exactamente la salida prevista de este curso (182,5 horas), así que
sirve de referencia para un segundo año.

Lo que se toma, anotado entero en el análisis: la **historia seriada con
personajes fijos** como columna vertebral (este curso ya tiene a Ana e Iván,
pero como nombres, no como trama, y el audio acaba de construirse), la
**pragmática como curso propio**, la **interculturalidad** más allá del error
gramatical —el bloque de contraste de aquí solo contrasta lengua, no costumbre—
y el **bloque de traducción ru↔es** al cerrar los ejercicios. Lo que no se toma:
la modularidad horizontal/vertical, que presupone un profesor y un grupo que
eligen, y este curso es un camino fijo de 30 minutos donde no hay que decidir
nada.

## La historia de Ana e Iván (2026-10-26)

El usuario lo pidió así: «haz que las personas entren y terminen el curso».

**El hallazgo es que el arco no hubo que inventarlo: estaba en el temario.**
Las 24 unidades leídas en orden ya son la historia de alguien que se muda a
España —llega, se orienta, come, compra, viaja, enferma; y en A2 cuenta su
vida, busca trabajo, pelea con la burocracia, decide, alquila, celebra y se
examina—. La historia solo lo hace visible.

**Y por eso el final del curso deja de ser un trámite**: la fase final son
simulacros del DELE A2, e Iván necesita ese papel para quedarse. El alumno se
examina a la vez que él. Es la pieza que más empuja a terminar y no cuesta ni
una lección más.

Cómo encaja sin romper nada:

- **Un episodio por unidad, en el día `cultura` de la segunda semana.** Esos
  días ya existen (50, uno por semana) y ya no son de gramática nueva: el
  episodio no añade un día ni un minuto. **No sustituye el contenido cultural:
  lo encarna** —la semana 18 habla del Camino y el episodio es Iván haciendo un
  tramo—.
- **Cero vocabulario nuevo.** El episodio usa solo lo que la unidad ya dio, así
  que la regla 2 no se toca y además el episodio **mide la unidad**: si la
  escena se entiende sin diccionario, funcionó. En el ejemplo escrito (el 8)
  Ana dice «yo voy a llevar una chaqueta» y no «lleva una chaqueta» porque el
  imperativo llega dos unidades más tarde.
- **Ana no es profesora ni pareja de Iván**, que son los dos clichés que
  convierten al alumno en espectador: es su vecina, con sus propios problemas,
  que le corrige poco y le entiende mucho.
- **Se puede saltar**: no introduce materia evaluable. Eso es lo que permite
  que exista sin obligar a nadie.

**Los títulos y las sinopsis viven en el YAML**, no en el .md, porque el
calendario es la única fuente de verdad. El .md explica el arco y una prueba
exige que nombre los mismos episodios. **Esa prueba se puso en rojo en su
primera ejecución** y tenía razón: el documento describía lo que pasa en cada
unidad pero no nombraba los episodios del YAML. Es exactamente la deriva que
este proyecto sufre una y otra vez —lo escrito y lo que corre dejan de
coincidir— cazada esta vez el mismo día.

**Lo que la historia NO hace, y conviene no confundirlo**: hace volver a quien
ya empezó. No hace entrar a nadie. Entrar es la portada, la primera lección y
que la web cargue: otro problema, y el siguiente.

## Entrar: «100 de 365» decía lo que no era (2026-10-26)

La historia hace volver a quien ya empezó; **entrar es otro problema**, y al
mirarlo en el movil aparecio uno concreto.

Lo tercero que ve quien llega, justo debajo del boton principal, era
**«100 / 365 уроков открыто»**. Es verdad y hay que decirlo, pero en ese sitio
contesta la pregunta equivocada: se lee como «el curso esta a medias», que es
una razon para irse y volver otro dia.

La pregunta que el visitante si se hace es **«¿me voy a quedar sin curso?»**, y
la respuesta es que no: 100 lecciones a una por dia son **mas de tres meses**.
Mismo dato, dicho de forma que invita en vez de avisar. Debajo del contador va
ahora esa linea.

- **El numero de meses se calcula**, no se escribe: «mas de tres meses»
  envejeceria el dia que se escriba la leccion 101 y nadie volveria a mirarlo.
- **El ruso declina** (2-4 «месяца», 5+ «месяцев», con la excepcion de 12-14).
  Un «3 месяцев» en la portada delata que el sitio no lo escribio nadie. Hay
  una prueba con seis casos.
- **Por debajo de 60 lecciones el aviso no sale**, porque ahi la respuesta
  honrada a «¿me quedare sin curso?» seria que si.

De paso, medido: `kurs.html` pesa **96 KB** —es la pagina mas pesada y esta en
el menu principal— y el CSS va en linea, 11 KB que son la mitad de cada pagina
y se repiten en las 125. En linea es lo correcto para la PRIMERA pintada (una
peticion menos) y caro al navegar leccion a leccion. No se toco: es un cambio
con dos lados y hace falta medir trafico real para decidirlo.

## La cabecera se partia en escritorio (2026-10-26)

El usuario recordo que habia mandado una pagina de referencia para el diseno.
**No se pudo abrir** (`curso-ingles.com`, proxy 403), asi que de ese diseno no
se copio nada: inventarse una referencia que no se ve es peor que no tenerla.
Lo que si se hizo fue mirar el sitio propio en ESCRITORIO, que hasta entonces
solo se habia visto en movil.

Y ahi habia un fallo en todas las paginas: **el boton del tema caia a una
segunda fila** en todos los anchos de escritorio, con 700 px de pantalla libres
al lado. La cabecera media 83 px de alto en vez de 47.

La causa no era la que parecia. El primer arreglo —quitarle el `flex:1 1 auto`
al titulo, que solo tiene sentido en movil— era correcto y **no cambio nada**.
Midiendo los hijos del flex en el navegador aparecio la cuenta de verdad:

    marca 304 + nav 215 + idiomas 112 + luna 30 + huecos ≈ 708 px
    columna                                                704 px

**Fallaba por cuatro pixeles**, y por eso no se veia mirando una captura.

El arreglo es conceptual, no un parche: **la barra de navegacion no tiene por
que caber en la columna de lectura**. Una columna de prosa es estrecha a
proposito (44rem, para no pasar de ~75 caracteres por linea); una barra con el
titulo, tres enlaces, tres idiomas y un boton, no. La cabecera pasa a 60rem y
el texto se queda en 44.

De paso se recuperan **36 px de alto en todas las paginas** en escritorio.

Las pruebas fijan la **invariante** (la barra mas ancha que el texto, y el
texto por debajo de 48rem) y no el numero, porque el numero puede cambiar y lo
que no puede es volver a igualarse. Son comprobaciones del CSS y no del dibujo:
la suite es Python y no abre un navegador, asi que lo que cazan es que alguien
vuelva a meter la cabecera en la columna de prosa.

**Lo que sigue pendiente del diseno**: la captura de la pagina de referencia.
Sin verla no hay nada que decir.

## El diseno de referencia, y el mapa de unidades (2026-10-26)

El profesor mando capturas de `curso-ingles.com`, que no se podia abrir desde
aqui. Con ellas delante se pudo separar lo que vale de lo que no.

**Lo que NO se copio, y conviene que quede escrito**: su piel. Azul marino con
naranja es la combinacion de cualquier portal de idiomas; la crema con salmon
y celeste de esta casa no se parece a nada y ademas aguanta mejor una pagina
que es casi toda texto. Tampoco sus mega-menus (ellos tienen ~15 destinos
colgando de 3 menus; aqui hay 3 destinos en total), ni «Accede / Registrate»
—se decidio no tener cuentas—, ni su buscador como accion principal del heroe:
eso sirve a un portal de consulta, y este curso es un camino donde lo primero
tiene que ser «empieza por la leccion 1».

**Lo que si se tomo es una idea estructural**: ellos entran a cada curso por
una **tarjeta**, no por una lista. Aqui el indice eran **365 filas, 21.482 px
de alto y 100 KB** —24 pantallas de scroll—, y nadie navega eso.

`_mapa_de_unidades` pone **24 tarjetas** antes de la lista dia a dia: numero,
nivel, titulo, **el titulo del episodio de Ana e Ivan** —que es donde la
historia se ve sin abrir ninguna leccion— y cuantas lecciones estan escritas,
con su barra. Las unidades sin escribir salen apagadas y anclan a su seccion
de abajo en vez de prometer una puerta que no abre.

Tres cosas que costaron una vuelta:

- **El mapa se sale de la columna de prosa**, igual que la cabecera y por el
  mismo motivo: encerrado en los 44rem del texto solo caben **dos** columnas y
  medía 1.806 px, tan ilegible como la lista que viene a sustituir. Centrado
  sobre la VENTANA (`left:50%;translate:-50%`) y no sobre el padre, que asi no
  hace falta saber cuanto mide el padre. Con eso: 4 columnas y 1.016 px.
- **El pie de la tarjeta va con `margin-top:auto`.** La rejilla estira las
  tarjetas de una fila a la misma altura, pero sin eso el pie queda pegado al
  texto y dos barras vecinas salen a distinta altura segun si el titulo ocupa
  una linea o dos.
- **Las tarjetas necesitan `raiz`.** Sin ella, desde `/es/kurs.html` el enlace
  relativo apuntaba a `/es/semana-01/...`, que no existe: las lecciones viven
  solo en la raiz. **Lo cazo la prueba de enlaces rotos**, la misma que
  encontro los 404 del conmutador de idioma. Es la segunda vez que ese fallo
  aparece por el mismo motivo, y la segunda vez que esa prueba lo para.

## El test de nivel: la segunda puerta (2026-10-26)

El sitio tenia **una sola entrada, la leccion 1**. Quien llega sabiendo algo de
espanol lee «Начать с первого урока», piensa «esto no es para mi» y se va. Es
la otra mitad del problema de entrar: la historia de Ana e Ivan hace volver a
quien ya empezo, pero no hace entrar a nadie.

De la referencia del profesor (`curso-ingles.com`) se tomo **la idea** —un
«test de nivel» junto a «primeros pasos»— y nada mas: las catorce preguntas
salen de `programa/contrastiva-ru-es.md`, o sea de la lista negra de errores
del rusohablante que ya alimenta los distractores de las pruebas del curso.
Por eso el resultado puede decir POR QUE se fallo y no solo cuantas van bien, y
por eso **el test ensena aunque se suspenda**.

**La recomendacion es la unidad de la PRIMERA pregunta fallada**, o sea donde
se acaba lo que ya se sabe —no un porcentaje, que no dice por donde empezar—.
De ahi salen las tres cosas que lo romperian en silencio, y las tres tienen
prueba:

- **Las preguntas van en orden de unidad.** Desordenadas, fallar la ultima
  podria colocar a alguien antes que fallar la primera, y nada avisaria.
- **El destino se calcula al construir** (`inicios_de_unidad`), no en el
  navegador: el guion no puede saber que lecciones existen. Mandar a una que no
  esta es el fallo que esta suite ya caza dos veces —el conmutador de idioma y
  las tarjetas del mapa—.
- **Una unidad sin lecciones escritas cae en la ultima escrita.** No es un
  parche: el curso tiene 100 de 365, asi que fallar en la unidad 17 significa
  que ya sabe todo lo que el curso cubre, y ahi es exactamente donde empieza.
  Sin ese `|| D.ultima` la pantalla de resultado se quedaba sin su boton.

**El error se dice dos veces y no es redundancia.** La primera version mandaba
al navegador la explicacion en espanol, que es justo el idioma que el lector
viene a aprender: a un principiante ruso explicarle su propio error en espanol
no le ensena nada. Ahora `error_ru` es lo que se lee y lo unico que viaja, y
`error_es` es la regla para el profesor, que es quien revisa (regla 6) y lee la
documentacion de este curso en espanol. Una prueba exige las dos y que ninguna
este vacia, y otra exige que el espanol NO aparezca en la pagina.

**Hay una sola pagina y esta en ruso**, igual que las lecciones y por la misma
razon: las preguntas son frases rusas que hay que decir en espanol, asi que un
lector que no lee ruso no puede contestarlas. Traducir la interfaz alrededor
dejaria un test que no se puede hacer, que es peor que no ofrecerlo. Lo que si
se traduce es **el enlace**, igual que la portada en espanol manda a una
leccion en ruso. Por eso la pagina va con `traducida=False`: el conmutador
lleva a la portada de ese idioma y no declara un `hreflang` que seria falso.

**No esta en el menu de la cabecera, y es una decision.** Esa barra se acababa
de arreglar el mismo dia: con tres enlaces fallaba por cuatro pixeles. Un
cuarto la volveria a apretar justo en tableta. Y el test solo hace falta en el
momento de entrar —dentro de una leccion ya no sirve de nada—, asi que va donde
se toma la decision: una linea bajo los botones de la portada («Уже знаете
немного испанского?») y otra en el indice, mas el pie, que envuelve sin
pelearse con nada.

Dos detalles menores que importan si alguien lo toca:

- **La instruccion («como se dice esto en espanol») la pone la pagina una sola
  vez**, no cada pregunta. Asi las catorce son la frase rusa y nada mas, y
  traducirla no toca el YAML.
- **El boton nace oculto y lo enciende el navegador**, como el resto del sitio.
  Sin JavaScript seria un boton que no hace nada; para ese caso esta el
  `<noscript>`, que manda a la leccion 1.

**La respuesta correcta viaja al navegador** y en un sitio estatico no hay
forma de evitarlo. No importa: esto coloca a quien quiere estudiar, no
certifica nada.

**De paso, el revisor de enlaces miraba dentro de los `<script>`.** El guion
del test arma el enlace del resultado concatenando `href="'+dest.url+'"`, y
leido como marca eso es un enlace a un fichero llamado `'+dest.url+'` que por
supuesto no existe: `revisar_adsense.py` cantaba un roto que ningun lector
puede pulsar. Ahora los `<script>` se quitan antes de mirar. Es la misma prueba
que caza los 404 de verdad -215 del conmutador de idioma, y los del mapa de
unidades-, asi que hay una segunda prueba que exige que un roto autentico siga
saliendo: un revisor ciego seria peor que uno que se equivoca.

### El cronómetro, por pregunta (2026-10-27)

Lo pidió el profesor. Se puso **por pregunta y no para todo el test**, que no
es lo mismo: un reloj global solo mete prisa, y lo que hace falta es que no dé
tiempo a buscar la respuesta. **Quien la busca queda colocado más adelante de
lo que sabe y se pierde en la primera lección**, o sea que el test le haría más
daño que no existir.

- **30 segundos**, en `segundos_por_pregunta` del YAML para que se ajuste sin
  tocar código; a 0 se apaga y una prueba lo comprueba construyendo el sitio
  con esa configuración.
- **Al agotarse cuenta como fallada y pasa**, que es lo que significa para
  colocar a alguien. Se anota aparte (`tarde`) y el resultado lo dice —«Не
  успели ответить»— porque no es lo mismo equivocarse que no llegar.
- **`parar()` al contestar y al terminar.** Sin eso, el reloj de la pregunta
  anterior seguiría corriendo y dispararía un `responder(-1)` encima de la
  siguiente. Hay prueba de las dos llamadas.

**Pendiente**: las catorce preguntas estan en `revisado: false` y la pagina lo
avisa. Lo que el profesor tiene que comprobar es que cada distractor sea de
verdad el error que dice, y que la unidad asignada sea donde el curso lo
ensena.

## La prueba de unidad se contesta, no se lee (2026-10-27)

El profesor lo pidió así: *«¿no debería haber un pequeño test para continuar a
la siguiente clase o tema?»*. La primera respuesta fue proponerle escribir
120 preguntas nuevas. **Era innecesario: ya estaban escritas.**

El calendario tiene **23 días de tipo `prueba`**, uno al cerrar cada unidad, y
cada uno trae **15 preguntas de opción múltiple** en tres bloques con su clave.
Siete están escritos y el de la unidad 1 está `revisado: true`. El cierre de la
clave ya decía lo mismo que el test de nivel:

> «Los distractores no son al azar: а) Por favor, а) francés, а) eres son justo
> lo que dice un rusohablante. Si los elegiste, encontraste tu error. Eso vale
> más que 15 de 15.»

**Es la cuarta vez que pasa** —la receta, beneficios, la escena en el proyecto
de salud— y por eso ahora se comprueba ANTES de escribir nada. Lo que faltaba
no era contenido: en la web ese día era una página de texto con la clave a un
scroll, que es como nadie se autoevalúa.

### `scripts/pruebas.py`

Lee las preguntas de la **propia lección**. Si vivieran además en un YAML, el
día que el profesor corrigiera una en el Markdown la web seguiría con la vieja:
este proyecto ya se ha tropezado varias veces con lo escrito y lo que corre
dejando de coincidir.

**Y falla de forma segura**: `leer` devuelve `None` en cuanto algo no cuadra
—menos respuestas que preguntas, una letra que no está entre las opciones, un
bloque descolgado— y esa unidad se queda como está. Decirle a alguien que
acertó cuando falló es mucho peor que no ofrecerle el test.

**Se corta por el marcador `а)` y no por el `·` que separa las opciones.** La
primera versión cortaba por el punto y dejaba fuera dos de las siete: en la
unidad 4 una opción es una transcripción fonética con su propio «·» dentro
(`а) [дос · а-би-та-сьо-нес]`) y en la unidad 5 las opciones se parten entre
dos renglones. El fallo seguro las descartó en vez de inventarse una respuesta
—que es para lo que está— y al mirar POR QUÉ se arreglaron las dos.

**La clave regala algo que no se esperaba**: dice de qué lección sale cada
respuesta («нед. 2, день 5»). Así el resultado no solo corrige, sino que
**enlaza a la lección donde se enseña lo que acabas de fallar**. De 105
preguntas, 91 lo traen.

### Cómo queda en la página

- **Sin JavaScript no cambia nada**: las quince preguntas y la clave siguen en
  el HTML, para leer o imprimir. Es el guion el que las esconde cuando de
  verdad puede ofrecer algo mejor.
- **El envoltorio se hace sobre el HTML ya convertido**, no sobre el Markdown:
  envolver Markdown en un `<div>` haría que Python-Markdown lo pasara tal cual
  y las quince preguntas saldrían en crudo. Los tres trozos se marcan de atrás
  adelante, porque cada inserción mueve las posiciones siguientes.
- **La clave se enseña al terminar, con un botón.** El discurso sobre los
  distractores es lo mejor del día y solo enseña DESPUÉS de contestar: antes
  sería la respuesta.
- **No bloquea el paso a la unidad siguiente**, y es una decisión: en un curso
  gratis de autoestudio una puerta cerrada hace que la gente abandone, no que
  repase.

**Los enlaces del resultado viven dentro del JSON de un `<script>`**, así que
el revisor de enlaces rotos NO los mira desde que salta los scripts (2026-10-26).
Hay una prueba que los comprueba uno a uno: o se comprueban ahí o no los
comprueba nadie.

## Los dibujos del vocabulario (2026-10-27)

El profesor preguntó si se pueden añadir imágenes educativas. **Sí, y cuestan
1,50 USD una sola vez**: 300 sustantivos dibujados con `gpt-image-1-mini`, que
salen delante de la palabra en las tablas de vocabulario. 341 dibujos en 69 de
las 100 lecciones, 4,7 MB.

**No se dibujan las 976 entradas del vocabulario, y ese es el dato que manda.**
471 llevan artículo; las otras 505 son saludos, adjetivos y palabras
funcionales —`hola`, `muy`, `mi/mis`, `mayor`— que no tienen dibujo posible.
De los sustantivos se quitan a mano 66 abstractos: `el IVA`, `la fianza`, `el
huso horario`, `la tilde`, `el patronímico`… y `la regla`, que es regla de
medir Y norma, así que el dibujo enseñaría la acepción equivocada.

**`la Península` y `el Día del Padre` quedan fuera por la regla 7**: una imagen
generada de un sitio o una fiesta reales es un invento con pinta de dato.

### Lo que decidió la muestra, y por qué se hizo muestra

Igual que con la voz del audio: **tres estilos, seis palabras, 0,09 USD**, y el
profesor eligió **plano** sobre acuarela y foto. No es cuestión de gusto:

- **Es el único inequívoco.** «La profesora» en plano trae puntero y libro, así
  que se lee «profesora»; en foto es una señora con una carpeta, que podría ser
  cualquiera.
- **Es la paleta del sitio** (crema `#f4f1ea`). Las fotos meten grises de
  estudio que al lado de una lección cantan.
- **Pesa un tercio** (10-13 KB contra 27-31) y **sigue legible a 56 px**, que
  es justo lo que una foto no aguanta.
- **No inventa personas.** Las de «foto» eran caras generadas con pinta de
  persona real.

**Y la muestra encontró un fallo que ninguna lectura habría encontrado**: «el
trabajo» salió como un señor en un escritorio CON CASCO DE OBRA en plano, y
como un hombre con una pala en acuarela. Ninguna dice «trabajo»: dicen
«oficina» y «obrero». Es un abstracto y no avisa de que lo es hasta que se ve
dibujado. Está fuera, con «el grupo».

### `scripts/generar_imagenes.py`

Hermano de `generar_audio.py` y con sus tres decisiones: el hash del pedido
entero como nombre, el `.parcial` que se renombra al final, y el índice
reconstruido de lo que hay en disco. Lo propio:

- **Ni una letra en la imagen.** Los modelos escriben texto con faltas, y un
  dibujo de «la mesa» con «MEZA» encima le enseña al alumno la falta. Los tres
  estilos comparten esa cláusula y hay una prueba que la exige. En las 300
  generadas no salió ni una.
- **Un solo estilo**, que entra en el hash: sueltas saldrían 300 estilos y el
  curso parecería un vertedero de clipart. Así además dos estilos conviven en
  disco y se comparan sin pisarse.
- **512 px y webp, no los 1024 que vienen.** Se ven a 56 px, y git guarda el
  historial para siempre: subir las grandes y encogerlas después deja el
  repositorio con los dos juegos. Es la lección del audio, recodificado a
  64 kbps ANTES del primer commit.
- **TRES hilos y no seis.** La primera tanda con seis perdió **142 de 300** con
  un 429: el límite de imágenes por minuto es mucho más bajo que el de voz,
  porque cada imagen cuesta mucho más de generar. Ahora reintenta hasta cuatro
  veces y **respeta el «try again in 2.48s»** que el propio mensaje de OpenAI
  trae, que sabe mejor que nosotros cuánto falta. Lo que NO hace es tragarse el
  último error: una tanda que miente sobre lo que consiguió es peor que una que
  falla.

**`--modelos` pregunta a la cuenta qué modelos de imagen tiene**, y fue útil el
primer día: las fuentes de terceros decían que `gpt-image-1` se había retirado
el 23 de octubre, y la cuenta lo listaba tan vivo como `gpt-image-2.5`. Un dato
de un blog sobre un proveedor se comprueba contra el proveedor.

### Cómo salen en la página

- **Encima de la palabra, no al lado.** A 420 px la columna española mide unos
  110, así que con el dibujo en línea le quedaban 50 a la palabra y «el marido»
  se partía por la mitad. **Se vio en una captura del móvil, no razonándolo.**
- **56 px**, porque la palabra manda y el dibujo acompaña. Crece al pasar el
  ratón en escritorio, que sale gratis.
- **El `alt` va vacío a propósito.** La palabra está al lado y su traducción en
  la columna siguiente: un lector de pantalla que leyera el dibujo diría lo
  mismo dos veces.
- **Las DOS tablas de vocabulario**, que tienen formas distintas: `Словарь дня`
  (Español·Русский·Пример, columna 0) y el `3. Слова` de los domingos de
  cultura (Español·Русский·Español·Русский, columnas 0 y 2). El domingo se
  descubrió tarde: las 50 lecciones de cultura generaban sus dibujos y no los
  enseñaba ninguna, porque el extractor del vocabulario SÍ lee esa tabla y el
  montaje no la miraba. Eran 193 dibujos; con ella, 341.
- **Ninguna otra tabla.** En las de fonética la primera columna es una letra y
  en las de conjugación una forma verbal: un dibujo ahí no enseñaría nada.

**Y el fallo que costó una construcción entera en blanco**: `_botones_de_audio`
corre ANTES e inserta un `<button>▶</button>` en la celda. Quitando solo las
etiquetas para leer el texto, el «▶» se quedaba y la celda decía `▶el marido`,
que no casa con ninguna entrada del índice. **Las 100 lecciones se
construyeron sin un solo dibujo mientras la prueba de al lado seguía en
verde**, porque su HTML de mentira no tenía botones. Ahora se quita el
`<button>` ENTERO —no solo sus etiquetas, que así aguanta que mañana lleve otro
signo— y hay una prueba que pone el botón, que es el camino real.

**El índice se copia a la construcción de prueba**, como el del audio desde el
26: si no, `test_docs_esta_al_dia` compara un sitio con dibujos contra uno sin
ellos y acusa a `docs/` de estar desactualizado.

**Lo que esto NO hace**: las 300 están sin revisar. Por la regla 6 el profesor
tiene que verlas una a una, y no es trámite —si «el sobrino» sale dibujado como
una niña, el alumno aprende lo contrario y nada falla—. Las que más conviene
mirar son las ambiguas que sí se dejaron: `el banco` (asiento o entidad), `la
planta` (vegetal o piso), `el partido` (deporte o político), `la entrada`
(billete o puerta) y `la carta` (misiva o menú).

## La baraja de tarjetas (2026-10-27)

El profesor preguntó qué era Anki y para qué sirve. **La respuesta estaba en su
propio curso**: 92 de las 100 lecciones empiezan con «Карточки: 10 слов» y 87
cierran pidiendo «añade 5 palabras a tu baraja». El método está construido
sobre las tarjetas desde el principio. Lo que no existía era la baraja: los
TSV de `exportar_anki.py` vivían solo en el repositorio y `docs/vocabulario/`
estaba vacío, así que el alumno leía «repasa tus tarjetas» el primer día y no
tenía ninguna.

**Se publican DOS formatos y eso no es indecisión:**

- **`.apkg`** (`scripts/exportar_apkg.py`, con `genanki`): 908 notas, 1213
  tarjetas, 21,8 MB, con los 305 dibujos y las 905 voces **dentro**. Se abre de
  un clic. Pero necesita Anki, y Anki en iPhone cuesta unos 25 USD (pago único;
  en ordenador, Android y AnkiWeb es gratis).
- **`.tsv`**, el que ya existía: sin medios, pero lo abre Excel, Google Sheets,
  Quizlet y cualquier app de tarjetas. Es lo que evita que el curso dependa de
  una app de pago para quien tenga iPhone.

**Dos tipos de tarjeta, y el segundo es el que justifica los dibujos:**

1. `español → русский`, que entrena a traducir.
2. `рисунок → español`, que entrena a PENSAR en español sin pasar por el ruso.
   Solo se crea cuando hay dibujo, con la plantilla condicional de Anki
   (`{{#Imagen}}…{{/Imagen}}`): sin eso, las 603 palabras sin dibujo tendrían
   una tarjeta con el anverso en blanco, imposible de contestar. Por eso son
   1213 tarjetas y no 1816.

### Lo que rompe esto sin avisar

- **Los identificadores son FIJOS**, derivados de un texto fijo. Anki reconoce
  baraja, modelo y nota por su id: con ids al azar, volver a importar no
  actualizaría la baraja del alumno sino que le crearía otra al lado, y
  perdería meses de repasos. **Es el único fallo de este guion que no se vería
  hasta meses después y en el ordenador de otro.** Lo mismo el `guid` de cada
  nota, que sale de la palabra y no del orden: así cambiar el reparto de
  unidades no le borra el progreso a nadie.
- **El bloque de descarga sale de un manifiesto** (`docs/vocabulario/baraja.json`,
  cinco números), no de abrir el `.apkg`. Dos razones: construir el sitio no
  tiene que leer 22 MB, y la prueba que compara `docs/` puede copiar el
  manifiesto entero sin arrastrarlos. Es el mismo patrón que los `indice.json`
  del audio y los dibujos.
- **Sin manifiesto —o con manifiesto y sin archivo— el bloque no sale.** Un
  botón de descarga que lleva a un 404 es peor que no ofrecer la baraja.
- **El índice del curso recibe DOS carpetas**: la del idioma y la raíz del
  sitio. La baraja vive una sola vez en `docs/vocabulario/` para los tres
  idiomas, así que buscándola en `docs/es/vocabulario/` no se encontraría y el
  bloque se caía en dos de las tres páginas. Se vio construyendo, no leyendo.
- **El copiado de los TSV va ANTES del bucle de idiomas.** Puesto después, el
  índice se construía antes de que los archivos estuvieran y el bloque se caía
  en la primera corrida.

**Lo que esto cuesta en el repositorio, y hay que saberlo**: el `.apkg` son
22 MB de zip, que git no puede comprimir ni deltar. Cada regeneración es un
blob nuevo entero. Por eso **no se genera al construir el sitio**: es un
comando aparte y deliberado, como el audio y los dibujos. Si algún día pesa
demasiado en el historial, el camino es moverlo a un *release* de GitHub, que
no vive en git.

## El respaldo del progreso, y la firma del autor (2026-10-27)

El profesor preguntó cómo registrarse «en caso se les borre sus avances». La
nota del 26 decía que las cuentas se decidían «no hacer hasta que alguien lo
pida», así que tocaba decidir.

**No se hicieron cuentas, y el motivo es de coste y no de pereza**: un servicio
externo (Supabase, Firebase) trae tres cosas que pesan más que el código —datos
personales con RGPD para los alumnos de Alemania y España, una cola de soporte
de «he perdido la contraseña» que llega a `espanoldesderuso@gmail.com` para
siempre, y la trampa de la capa gratis de Supabase, que **pausa el proyecto tras
una semana sin actividad** y hay que despertarlo a mano—. Con pocos alumnos, eso
es exactamente lo que pasaría. Montar todo eso antes de saber si alguien lo
necesita es pagar por un problema que todavía no existe.

**Lo que se hizo: un código de respaldo.** El alumno lo copia y lo guarda donde
ya guarda cosas (Telegram, notas, un mensaje a sí mismo); para restaurar, lo
pega. Cero coste, cero datos personales nuestros, nada que mantener.

**Cabe en 68 caracteres y no crece.** Un bit por lección: las 365 caben en 46
bytes, o sea 64 caracteres en base64 más la marca `ESR1`. Eso es lo que lo hace
pegable en un mensaje; guardando la lista de números (`[1,2,3,…]`) un alumno
avanzado tendría un texto de más de mil caracteres que nadie copia bien.

### El fallo que tuvo la primera versión

**«Restaurar» estaba dentro del recuadro `#mio`, que se oculta cuando no hay
progreso.** O sea que el botón era invisible EXACTAMENTE para quien lo
necesita: el que acaba de limpiar el navegador o estrenar móvil y no tiene
nada marcado. Se vio probándolo en el navegador, no leyendo el código, y hay
una prueba que lo fija.

«Guardar» sí nace oculto y lo enciende el navegador: sin nada hecho no hay nada
que copiar.

### Lo demás que se cuida

- **Restaurar nunca puede destruir.** `deCodigo` devuelve `null` ante cualquier
  duda —marca que no cuadra, longitud mal, base64 roto— y quien lo llama se va
  sin tocar `localStorage`. Un código cortado a medias al pegarlo no puede
  costarle el curso a nadie.
- **Un código con menos lecciones de las que ya hay pregunta antes de pisar**,
  porque alguien puede pegar uno viejo por error.
- **Si el portapapeles falla** (http, permisos, navegador viejo), el código se
  enseña en un campo para copiarlo a mano. Quedarse sin él sería lo único
  imperdonable aquí.
- **El aviso previene en vez de reparar**: donde ya decía «tu progreso vive solo
  en este navegador» ahora dice además «antes de limpiar el navegador o cambiar
  de móvil, guarda tu código».
- **El guion vive en `construir_sitio.PROGRESO_JS`**, no en `docs/progreso.js`:
  ese se genera. La primera versión se escribió en el generado y la
  reconstrucción se la llevó por delante, sin que nada fallara.

### La firma del autor, y lo que NO se escribió

El profesor pidió quitar su nombre del sitio: `autor.nombre` en `web/sitio.yaml`
queda vacío y `_firma()` entonces no escribe ni el `<strong>` ni el punto que lo
separaba —un «. Преподаватель с магистратурой…» de entrada delata que algo se
borró a medias—. La descripción se queda.

**Pidió además poner «elaborado por profesores del Cervantes», y eso no se
escribió.** El Instituto Cervantes es una institución pública española con
marca registrada, y nada en este repositorio sostiene ese vínculo. Costaba tres
cosas concretas: el sitio está en revisión de AdSense y la tergiversación de
credenciales es causa de rechazo con nombre propio; el Cervantes puede reclamar
por su nombre; y contradice lo que se acababa de hacer —quitar el nombre real
para poner una autoría ajena—.

**Lo que sí se puso, y el profesor aceptó**, es una frase que menciona al
Cervantes de verdad: *«Программа построена по уровням A1–A2 и готовит к DELE A2
— официальному экзамену Института Сервантеса»*. El DELE **es** su examen
oficial, así que la asociación es real y pasa por el examen, no por una autoría
prestada. Habla del currículo, no de quién lo escribió.

**Queda pendiente del profesor**: `alineacion-mcer-pcic.md` se escribió de
memoria y dice «cotejar». La frase publicada se limita a los niveles A1–A2 y al
DELE —que es el objetivo declarado del curso— y no nombra el PCIC, justamente
para no apoyarse en lo que aún no está comprobado.

## Compartir, y las redes (2026-10-27)

El profesor preguntó si se puede llevar el contenido a Instagram, YouTube,
Telegram y compañía «para monetizar». **Lo primero que hubo que separar: los
botones no monetizan, distribuyen.** El camino es contenido en redes → gente
que entra → AdSense. Hoy el sitio es bueno y no lo conoce nadie; ese es el
cuello de botella, no la falta de botones.

**Lo que se hizo**: compartir al pie de las 100 lecciones (Telegram, WhatsApp,
copiar enlace) y un hueco en `web/sitio.yaml` para los perfiles, que sale en el
pie de las 125 páginas.

- **Enlaces normales y NUNCA los widgets oficiales.** El botón «Compartir» de
  Facebook carga el SDK de Meta, que rastrea al lector; la política de
  privacidad de aquí dice que sin AdSense no se carga nada de terceros, y un
  widget la volvería mentira. `t.me/share/url?…` hace lo mismo y no carga nada.
  Hay una prueba que recorre las 125 páginas buscando los SDK de las cuatro
  plataformas.
- **Telegram y WhatsApp, y no más.** Son las dos por las que un rusohablante
  fuera de Rusia manda algo a un amigo. Una fila de ocho iconos no se usa más,
  se mira menos.
- **Al pie de la lección y no arriba**: se comparte lo que ya has leído.
- **Sin dominio configurado no sale nada**: un enlace que apunta a `file:///`
  no le sirve a nadie.
- **Un perfil vacío no sale**, en vez de un botón que lleva a una cuenta que no
  existe. Hoy los cuatro están vacíos y hay una prueba que lo fija: si se pone
  en rojo es que alguien escribió un perfil a mano, y hay que comprobar que
  exista antes de aflojarla.

**Lo que se le dijo sobre monetizar en cada plataforma**, con los umbrales
buscados (todos de fuentes de terceros, conviene cotejar): YouTube pide 1.000
suscriptores y 4.000 horas vistas —y sube a 8.000 horas en febrero de 2027—;
Telegram pide 1.000 suscriptores y reparte al 50%, pagando en Toncoin.
**Telegram es su canal**: es donde vive el público rusohablante fuera de Rusia
y el umbral es alcanzable.

**Y el hallazgo que ahorra el trabajo**: ya tiene con qué alimentar un canal
sin escribir nada nuevo —300 dibujos, 3.543 audios y 908 palabras con ejemplo y
traducción—. Una «palabra del día» automática son tres años de publicaciones
diarias sacadas de lo que ya está pagado y en disco. Queda propuesto, sin
hacer, a la espera de que exista el canal.

### Lo que quedó medido para los huecos interactivos

El profesor pidió además «mover palabras, dar click y colocar palabras en los
casilleros vacíos». Antes de proponer nada se contó lo que ya hay escrito, y es
la quinta vez que el contenido ya existía:

    huecos ______ escritos            1.488
    lecciones con huecos                 89 de 100
    ejercicios con BANCO DE PALABRAS     61
    lecciones con clave (Ответы)        100 de 100

El banco de palabras es literalmente lo que pide —`> aquí · ahí · allí · cerca
de · lejos de`— y la clave dice qué va en cada hueco, con ` / ` separando los
varios de un mismo renglón. O sea que son 61 ejercicios listos para volverse
interactivos sin escribir ni uno.

**Cuando se haga, tiene que fallar de forma segura como `pruebas.py`**: si la
clave no se casa con los huecos sin ninguna duda, ese ejercicio se queda como
está hoy. Decirle a alguien que acertó cuando falló es peor que no ofrecerlo.

## Los huecos se rellenan pulsando (2026-10-27)

El profesor lo pidió así: «mover palabras, dar click y colocar palabras en los
casilleros vacíos». **Es la quinta vez que el contenido ya existía**, y por eso
se contó antes de escribir nada.

**Pero la cuenta que se le dio primero estaba mal, y conviene que quede
escrito.** Se dijo «61 ejercicios listos» contando los que traen banco de
palabras. Al analizarlos de verdad, **23 tienen una clave que se puede casar
con los huecos sin ninguna duda**; los otros 38 llevan claves con frases
enteras —«Es una goma» contra un banco de «una goma»— o sea que son OTRO tipo
de ejercicio: el alumno escribe la frase, no coloca una ficha. Contar la
materia prima no es lo mismo que contar lo utilizable.

Quedan **189 huecos interactivos en 23 lecciones**, y 0 de contenido escrito.

### `scripts/huecos.py`

El contrato es uno y vale para las dos formas que hay escritas —los renglones
numerados y los diálogos—: **tantos huecos como respuestas, en el mismo orden,
y cada respuesta dentro del banco.**

**El orden manda y no la numeración.** La mitad de los ejercicios son diálogos
sin numerar y su clave da las respuestas seguidas («días · tal · gracias ·
tú»). La numeración de los otros es decoración y se quita.

**La comprobación del banco es la que de verdad protege**: los bancos son
cortos y concretos, así que una clave desalineada deja fuera alguna palabra
casi siempre. Es lo que descarta los 38 que no encajan, sin tener que
entenderlos.

**Y falla de forma segura**, como `pruebas.py`: a la mínima duda el ejercicio
se descarta y su página se queda exactamente como hoy.

### Los tres bugs que costaron la mitad de los ejercicios

Los tres eran míos y los tres se vieron midiendo, no leyendo. Con el primer
analizador salían **2 de 61**; con los tres arreglados, 23.

1. **Juntar las líneas destruía el salto de párrafo.** `re.sub(r"\n(?!\n)", " ")`
   convierte un `\n\n` en `\n `, así que el `(?=\n\n)` que cerraba el bloque
   de la clave ya no casaba y seguía leyendo el párrafo siguiente: en la
   lección 1-3 se llevaba por delante la tabla de sonidos y salían 12
   respuestas para 5 huecos. Ahora el párrafo se marca ANTES de juntar.
2. **El corte del comentario se comía la numeración.** La clave acaba a menudo
   en «… · es. Carmen говорит **encantada**…», así que se corta en el primer
   «. ». Puesto ANTES de quitar el «1. », un «1. aquí» se quedaba en «1», que
   no está en ningún banco. El orden de esas dos líneas vale 8 ejercicios.
3. **`content:"\00a0"` en el CSS escribía un byte NUL** en las 125 páginas:
   Python lee `\0` como escape octal. Los navegadores lo sirven igual y
   `grep` empieza a decir «binary file matches», que es la única señal.
   Ahora va el espacio duro literal. Hay una prueba que recorre las 125.

### Cómo queda en la página

- **Sin JavaScript no cambia nada**: los huecos siguen siendo rayas y la clave
  sigue abajo, para leer o imprimir.
- **La cita del banco se esconde desde el GUION y no al construir.** Las
  fichas y la cita son las mismas palabras dos veces, pero quitar la cita al
  construir dejaría sin banco a quien no tenga JavaScript, que es justo para
  quien esa cita es lo único que dice qué palabras hay.
- **Dos formas de rellenar**, porque en el móvil arrastrar es incómodo: pulsas
  la ficha y luego el hueco, o al revés. **Pulsar un hueco lleno lo vacía** y
  devuelve la ficha, que es como se corrige uno sin empezar de cero.
- **Los huecos responden al teclado** (Enter y espacio): son `role="button"`,
  así que tienen que hacer con el teclado lo mismo que con el dedo.
- **El envoltorio se hace sobre el HTML ya convertido**, como la prueba de
  unidad. Los `______` sobreviven a Markdown —seis guiones bajos no son
  énfasis—, y hay una comprobación extra: si el HTML no trae tantos huecos
  como el Markdown, ese ejercicio no se toca.
- **La corrección compara sin acentos ni mayúsculas**, porque la clave escribe
  «Aquí» al empezar frase y el banco «aquí».

## La portada con los 300 dibujos, y la tarjeta de compartir (2026-10-27)

El profesor dijo que la página «se ve muy aburrida» y pidió fondos o efectos.
**Lo que la viste son sus propios 300 dibujos**: ya están pagados, son de la
paleta de la casa, no los tiene nadie más y no cargan un solo byte de fuera.
Efectos de movimiento no se hicieron, y es una decisión: esto es un sitio para
leer media hora al día y una animación cansa a la tercera visita.

### La vitrina de la portada

Doce palabras con su dibujo y su traducción, entre el héroe y «Чем этот курс
отличается». **No es solo decoración: el visitante aprende doce palabras antes
de pulsar nada**, que es la mejor forma de enseñar de qué va el curso.

- **Las doce se eligen a mano** (`construir_sitio.PORTADA_DIBUJOS`) y en orden.
  De 300 hay que escoger, y éstas son la cara del sitio: tienen que ser
  inequívocas —nada de `el banco`, que es asiento y entidad—, distintas entre
  sí de un vistazo y de campos diferentes (comida, casa, animal, ropa, objeto,
  transporte). Se miraron una a una en una hoja de contactos antes de
  elegirlas; no se razonaron.
- **Doce y no diez** porque la rejilla es de 3, 4 o 6 columnas según el ancho:
  doce es el único número pequeño que deja filas enteras en los tres casos.
  Hay una prueba con los tres.
- **La traducción sale del vocabulario de las lecciones** (`lexico_del_curso`),
  no de una lista en el código. Escrita a mano, el día que el profesor
  corrigiera una traducción la portada seguiría enseñando la vieja.
- **Y por eso hace falta un filtro que no se ve venir**: la columna rusa trae a
  veces la variante americana (`el zumo → el jugo`, por la regla 8) o una
  corrección (`el vaso → стакан (✗ не «ваза»!)`). Lo primero pondría español
  donde se promete ruso. `NO_ES_TRADUCCION` rechaza las dos. De los doce
  candidatos iniciales, `la llave` se cayó por no estar en el vocabulario y
  `el zumo` y `el vaso` por esto.
- **Se cae de pie y en silencio**, como la baraja y el audio: sin dibujos
  generados no sale nada, y una palabra sin dibujo o sin traducción se salta.
  Por debajo de `MUESTRA_MINIMA` (6) no sale la banda entera: media vitrina con
  tres huecos no se lee como «faltan dibujos», se lee como una página rota.
- **Pero una prueba exige que hoy salgan las doce.** Si no, la vitrina se
  encogería sola el día que cambie una lección y nadie lo vería hasta mirar la
  portada.
- El índice y el léxico se leen **una vez para los tres idiomas**: dentro del
  bucle serían tres recorridos de las 100 lecciones para el mismo resultado.

### La tarjeta de compartir (`scripts/tarjeta_social.py`)

Los botones de compartir son de este mismo día y **el enlace llegaba sin
imagen**: Telegram, WhatsApp, Facebook y VK pintan la vista previa con
`og:image`, y no había ninguno. Un enlace pelado en un chat se mira mucho
menos, así que la mitad del trabajo de los botones se perdía ahí.

Se compone con ocho de los doce dibujos de la portada, el título y el dominio,
a 1200x630, que es lo que piden las tres plataformas. 120 KB.

- **Es un comando aparte**, como el audio y los dibujos: construir el sitio
  tiene que ser barato y esto abre doce imágenes y una fuente del sistema.
- **La fuente es Inter y si no DejaVu**, las dos con cirílico, que es lo único
  que no se puede dar por hecho: el título está en ruso.
- **El texto se MIDE y se centra antes de dibujarlo.** Escrito de arriba abajo
  con una `y` que crece, un título de dos renglones dejaba el bloque descolgado
  y un hueco muerto encima de la franja. Es la lección de los flyers de salud.
- **Cada dibujo va en su ficha con la esquina redonda.** El fondo de cada
  imagen es un crema ligeramente distinto y, pegados a hueso, esas diferencias
  se leen como rectángulos sucios.
- **La franja abajo y el texto arriba**: al revés, la vista previa de WhatsApp
  —que a veces recorta a cuadrado— se come el título, que es lo único que no
  puede faltar.
- **`construir_sitio` solo mira si el archivo ESTÁ**, y lo mira en `docs/` y no
  en la carpeta de destino. Al revés que la baraja, a propósito: aquello se
  enlaza con una ruta relativa, así que importa qué hay en la construcción;
  esto se declara con la URL **absoluta** del sitio publicado, así que importa
  qué hay versionado. Sin dominio o sin imagen no se declara nada: un
  `og:image` que da 404 es peor que ninguno.

**Lo que queda pendiente del profesor**: las doce de la portada y las ocho de
la tarjeta son dibujos sin revisar (regla 6) y ahora son lo más visible del
sitio. Son `la manzana, la casa, el perro, el libro, el café, el reloj, la
camisa, el coche, las flores, el pescado, la guitarra, la silla`.

## La semana 15, el test que varía y la clave plegada (2026-10-27)

### Cinco lecciones más: días 101-105

El curso se quedó en el día 100 (semana 15, día 2) y la semana 15 estaba a
medias. Ahora está entera, o sea la primera mitad de la unidad 8:

| Día | Tipo | Tema |
|---|---|---|
| 101 | lección | Meses, estaciones y la fecha |
| 102 | lección | ¿Qué tiempo hace? |
| 103 | lección | El clima de mi país y del mundo hispano |
| 104 | repaso | Repaso de la semana 15 |
| 105 | cultura | El fútbol y el domingo en familia |

Lo que decidió el contenido, y que conviene saber si alguien las reescribe:

- **El día 100 prometía una «странность» que no lo es.** Cerraba diciendo que
  en español los meses se escriben con minúscula. En ruso TAMBIÉN, así que para
  este lector no hay nada raro: la rareza es inglesa. La lección 101 lo dice
  así en vez de repetir la promesa, que es lo que pide `metodologia.md` cuando
  el ruso ayuda en vez de estorbar. El contraste de verdad es otro: la fecha va
  en número **cardinal** (*el doce de marzo*), y el ruso usa ordinal
  («двенадцатое марта»).
- **Los doce meses no caben en la tabla de vocabulario** (el validador pide de
  6 a 10 filas). Van en tres filas de cuatro, que es como la semana 9 metió los
  días de la semana. No es un truco: son un conjunto cerrado, y se aprenden en
  bloque.
- **La tríada que el ruso colapsa en una palabra** es el centro del día 102:
  *hace frío* (tiempo) · *tengo frío* (persona) · *está fría* (cosa). En ruso
  las tres son «холодно / холодный».
- **`muy` / `mucho` es el día 103 entero** porque es el error nº 11 de la lista
  negra de `contrastiva-ru-es.md` y el que más dura.
- **`la estación` no entra en el vocabulario del 101**: ya se enseñó en la
  semana 7 como «вокзал». Se explica dentro de la lección como una palabra
  conocida con un sentido nuevo, y la entrada nueva es `la estación del año`.
  Lo comprobé con `revisar_lexico.py` antes de escribir: las cinco lecciones no
  añaden ni un duplicado. (Los que hay son 13 y no 11 como decía esta nota, y
  todos son de las semanas 1 a 14.)
- **El día 105 no lleva episodio de Ana e Iván**: el episodio va en el día de
  cultura de la SEGUNDA semana de cada unidad, o sea en el 112.
- **Nada con cifras inventadas** (regla 7). Del fútbol se dice lo que es
  verificable sin número: qué es el clásico, qué es el derbi, cómo se llaman
  las canchas de Boca y River, y que en España se dice *aficionado* y *campo* y
  en América *hincha* y *cancha* 🌎.

**Lo que queda pendiente de estas cinco**: están en `revisado: false` como las
otras 79, y **su audio no está generado** — son 167 frases nuevas, unos 0,07
USD con `generar_audio.py`, y hace falta `OPENAI_API_KEY` en el entorno. La
baraja `.apkg` tampoco se regeneró: son 22 MB de blob nuevo en git cada vez, así
que conviene hacerlo por tandas y no por lección. Los TSV sí están al día,
porque hay una prueba que lo exige.

### El test de nivel ya no es siempre el mismo

Lo pidió el profesor: «el test del comienzo puede variar siempre, que sea
random». Ahora hay **dos preguntas por unidad** (28 en total) y el navegador
escoge una de cada grupo, más el orden de las tres opciones barajado. Medido en
navegador: **295 partidas distintas de 300**.

Lo que NO se baraja, y es la línea que no se puede cruzar: **el orden de los
grupos**. La recomendación sale de la unidad de la PRIMERA pregunta fallada, o
sea de donde se acaba lo que el alumno ya sabe; desordenadas, fallar la última
colocaría antes que fallar la primera y nada avisaría. `grupos_por_unidad`
ordena por unidad en vez de confiar en el orden del fichero, y hay una prueba.

- **Las variantes no son la misma pregunta con otras palabras.** Cada una es un
  error distinto de la lista negra: la unidad 7 pregunta por la *a personal* en
  una y por el sitio del clítico en la otra; la 6, por `gustar` y por
  `muy/mucho`. Repetir el test tiene que enseñar algo nuevo, y hay una prueba
  que falla si dos variantes de una unidad comparten el error.
- **Barajar copia la pregunta** (`q.opciones.slice()`) y recalcula `correcta`
  con `orden.indexOf`. Barajando sobre el original, la segunda partida
  encontraría las opciones ya movidas y `correcta` apuntando a otra cosa: le
  diría «has fallado» a quien acertó. Comprobado en navegador jugando una
  partida entera y pulsando siempre el botón cuyo TEXTO es el correcto: 14/14,
  y la correcta cayó en las tres posiciones.
- **El banco puede crecer sin tocar código**: basta añadir otra pregunta con su
  `unidad` en el YAML. Una prueba exige que ninguna unidad se quede con una
  sola variante, porque entonces el test dejaría de variar y nadie lo notaría
  leyendo el código: seguiría funcionando igual de bien la primera vez.

### «¿Y las respuestas? ¿Dónde ver si es correcto?»

Lo preguntó el profesor usando el sitio, y tenía razón por partida doble. La
clave (`## Ответы`) estaba abierta al final de la página, **debajo de la tabla
de vocabulario**: quien la buscaba no la encontraba —es lo último de todo— y
quien no la buscaba se la encontraba de paso, con las respuestas a la vista
antes de hacer el ejercicio.

Ahora el enlace «Проверить себя по ключу ↓» sale **donde se acaban los
ejercicios**, y la clave está plegada tras un botón. Es lo mismo que ya hacía el
día de prueba: el discurso sobre los errores solo enseña DESPUÉS de contestar.

- **Sin JavaScript la página se queda como estaba**: la clave abierta y el
  enlace llevando a ella. Por eso aquí nace visible y es el navegador quien la
  pliega, al revés que el resto del sitio: la versión sin guion tiene que ser la
  que sirve, y una clave escondida que no se puede abrir sería una lección sin
  respuestas.
- **Lo importante no es plegarla sino que el ENLACE la abra.** Un ancla que
  apunta a algo escondido no hace nada, y el lector se queda mirando la misma
  pantalla creyendo que está roto.
- **Dónde va el enlace se decide por el CONTENIDO y no por el nombre del
  apartado**, porque son tres formas: «4. Практика» en una lección,
  «3. Мини-тест» en un repaso y «4. Задание» en un día de cultura. Y el TÍTULO
  cuenta igual que el cuerpo: un repaso titula «Мини-тест» y dentro solo dice
  «выберите правильный ответ», así que mirando solo el cuerpo el enlace caía
  antes del mini-test y en la semana 1 no caía en ninguna parte. Lo cazó la
  prueba que recorre las 105.
- **El día de prueba no pasa por aquí**: tiene su propio envoltorio, con el test
  contestable y la clave al terminar. Dos mecanismos sobre la misma clave se
  pisarían.

## «No hay nada para completar»: 1.467 rayas que no se podían rellenar (2026-10-27)

Lo trajo el profesor con una captura de la lección 1-1 en el móvil: el
ejercicio Б pide partir palabras en sílabas y ofrece seis rayas —**y no se
podía escribir en ninguna**—.

Tenía razón y el fallo era de los que no se ven leyendo el código: **en papel
una raya es donde escribes; en una pantalla es una raya y nada más.** Los
huecos pulsables del mismo día cubrían los ejercicios con banco de palabras
—41 lecciones, 333 huecos—, y los otros **1.467** se quedaban inertes. Son la
mayoría porque la mayoría de los ejercicios no piden elegir una ficha sino
escribir la forma correcta.

Ahora toda raya fuera de la clave es un `<input>`.

- **Es el único trozo interactivo del sitio que nace encendido**, y a
  propósito: un `<input>` se teclea sin JavaScript. El guion solo le ajusta el
  ancho mientras escribes. Aquí el patrón de «nace oculto y lo enciende el
  navegador» rompería la casilla para quien no tenga guion.
- **No se corrigen, y es deliberado.** Para las fichas el banco es la red: la
  respuesta sale de un conjunto cerrado y corto, así que una clave desalineada
  se cae sola. Aquí no hay red — la clave de la 1-5 responde «usted: ¿Cómo se
  llama?», con el rótulo dentro, y quien escribiera «¿Cómo se llama?» tendría
  razón y se le diría que no. La clave está a un botón desde esta misma mañana,
  al final de los ejercicios. Decirle a alguien que falló cuando acertó es lo
  que este proyecto no hace.
- **La clave conserva sus rayas**: ahí una raya es parte de una respuesta
  —pasa una vez, en la 5-2—, no un sitio donde escribir.
- **El ancho se fija en el CSS.** Un `<input>` sin `width` mide lo que su
  `size` por defecto, unos 230 px, y eso parte en dos los renglones con dos
  huecos. Se vio midiéndolo en el navegador, no razonándolo.
- **`spellcheck="false"`**: el corrector va en el idioma del lector, que es
  ruso, y subrayaría en rojo cada palabra española que se escriba.

### Y la prueba encontró un fallo que llevaba meses publicado

La prueba nueva exige que ninguna raya del Markdown se quede sin sitio donde
escribir, y se puso en rojo en la lección **14-4**: nueve escritas, siete en la
página.

**Markdown se comía dos.** Seis guiones bajos sueltos pasan intactos —por eso
esto no se vio nunca—, pero `¿Tiene ______?` y `¿______?` se emparejaron entre
sí y Python-Markdown escribió `<strong><strong><strong>` abriendo en un
renglón y cerrando tres más abajo: **dos huecos desaparecidos y tres réplicas
del diálogo en negrita**, así desde que se escribió la lección.

`_rayas_a_salvo` las escapa antes de convertir. Conserva la longitud del hueco
y no toca nada más; ninguna lección mete un `______` dentro de un bloque de
código, que es el único sitio donde `\_` se vería tal cual.

Es el patrón de siempre: la regla era correcta («seis guiones bajos no son
énfasis») y el caso que no la cumple no estaba contemplado.

## Terminar el curso: unidades 8 y 9 (2026-10-27)

El profesor lo pidió así: «termina todo el curso hoy». Faltaban **260
lecciones**, y se le dijo por delante que en una sesión no salen: cada una son
unas 270 líneas de contenido contrastivo y se escriben de una en una. Lo que
se hace es avanzar por unidades y **commitear al cerrar cada una**, para que
nada dependa de llegar al final.

### Qué se escribió

- **Semana 16 (días 106-112)**, que cierra la **unidad 8**: planes con *ir a +
  infinitivo*, invitar y rechazar, la agenda, mensajes de WhatsApp, el texto de
  cien palabras, la prueba de unidad y el día de cultura con las fiestas.
- **Semana 17 (días 113-119)**, primera mitad de la **unidad 9**: transporte,
  la estación, *estar + gerundio*, el hotel, el aeropuerto, el repaso y el día
  de cultura (Camino de Santiago y Machu Picchu).
- **Semana 18 (días 120-126)**, que cierra la **unidad 9**: el pretérito
  perfecto en dos días (lo de hoy y lo de toda la vida), el día del turista,
  las preposiciones de movimiento, el diario y la queja en recepción, la prueba
  de unidad y el día de cultura con la postal.

### Lo que decidió el contenido

- **Los dos primeros episodios de Ana e Iván entran aquí**: el 8 en el día 112
  («Dice que sí») y el 9 en el día 126 («Un tramo del Camino»). El 9 se escribió
  para esta lección y **no se copió a `historia.md`**: ese documento explica el
  arco y guarda UN episodio escrito como muestra de tono; duplicar el texto
  sería tener dos versiones del mismo episodio. El del día 112, en cambio, es
  el que ya estaba escrito ahí, y se copió **tal cual**, que es donde el
  profesor lo aprobó.
- **La prueba de la unidad 8 se escribió para que `pruebas.py` la lea**, no
  solo para imprimirla: 15 preguntas en tres bloques y una clave con «нед. N,
  день N» en cada respuesta. Se comprobó ejecutando el analizador, no leyendo
  el archivo: las 15 se leen y cada una enlaza a su lección.
- **Los distractores salen de la lista negra**, como en el test de nivel: *hay
  nieva*, *muy calor*, *con mí*, *voy trabajar*, *Si* sin tilde. Cada uno es un
  error que el rusohablante comete de verdad, no una opción de relleno.
- **Las dos excepciones culturales de la regla 7.** Del fútbol y de las fiestas
  se dice solo lo verificable sin cifra inventada: fechas de San Fermín, las
  Fallas, el Día de Muertos y el Inti Raymi; los nombres de las canchas de Boca
  y River; los 800 km del Camino Francés y los 2.430 m de Machu Picchu, que son
  datos estables y citados en todas partes. Ni asistencias, ni records, ni años
  de fundación.
- **El léxico se comprueba ANTES de escribir, con el volcado de las 1.091
  entradas.** Aun así se colaron cuatro duplicados (*temprano*, *descansar*,
  *la mochila*, *el ruido*) y los cazó `revisar_lexico.py` al cerrar cada
  semana. Quedan los 13 de siempre, todos de las semanas 1 a 14.

### El orden de trabajo que funcionó, por si alguien retoma

1. Leer la unidad entera del calendario (`gramatica`, `contraste_ru`,
   `fonetica`, los siete días con su foco).
2. Volcar el léxico ya enseñado a un fichero y comprobar los candidatos **en
   bloque**, antes de escribir ni una lección.
3. Escribir día a día, validando cada uno con `validar.py` al salir.
4. Al cerrar la semana: `revisar_lexico.py` (duplicados), `exportar_anki.py`
   (los TSV tienen prueba), `construir_sitio.py`, y la suite entera.
5. Commit por unidad.

**Lo que NO se regenera por lección, y es deliberado**: el audio (hace falta
`OPENAI_API_KEY`; van 4.166 frases y 1,57 USD para todo lo escrito), los
dibujos y el `.apkg` de 22 MB. Los tres son comandos aparte y se hacen por
tandas, no por lección.

## La unidad 13: el imperfecto, y donde el aspecto ruso deja de servir (días 169-182)

Catorce lecciones, semanas 25 y 26. El curso pasa de 168 a **182 de 365**.

**La unidad tiene un arco deliberado, y es el hallazgo didáctico:** empieza
diciendo que el aspecto ruso SÍ ayuda y termina enseñando dónde deja de
ayudar.

- **Semana 25, lunes:** «я жил» = *vivía*, «я прожил» = *viví*. Es la
  primera vez en todo el curso que el ruso da la respuesta directa, y se dice
  así de claro. Con una advertencia al pie: aprovéchelo mientras dure.
- **Semana 26, miércoles:** «каждое лето мы **ездили**» → *íbamos*; «одним
  летом мы **ездили**» → *fuimos*. **El mismo verbo ruso, el mismo aspecto,
  dos tiempos españoles.** Ahí el criterio deja de ser el aspecto y pasa a
  ser «cuántas veces». Y el caso que más cuesta: «всю неделю шёл дождь» es
  *llovió*, indefinido, porque un tramo con número cierra la acción aunque el
  ruso lo diga en imperfectivo.

Lo demás que decidió el contenido:

- **Las cuatro cosas que van siempre en imperfecto** (hora, tiempo
  atmosférico, estado del cuerpo, lo que había) se dan como lista cerrada el
  lunes de la semana 26: si usted dice qué hora era, la elección ya está
  hecha.
- **`había` no concuerda nunca**, y se repite tres días seguidos porque es el
  error que cometen hasta los nativos.
- **La proporción de un relato es tres a uno.** El texto modelo del día 180
  trae dieciséis verbos en imperfecto y cinco en indefinido, y se cuenta
  explícitamente: si usted tiene mitad y mitad, ha contado sucesos en vez de
  describir una vida.
- **Los tres pasos de revisión** (¿hora, tiempo, estado? ¿cuántas veces?
  ¿tramos con número?) son la técnica del día 180 y se repiten en el test.
- **El domingo 175 compara la infancia en España y en Rusia** y el hallazgo
  es que casi todo coincide: la calle, el patio, dos canales, los abuelos en
  el pueblo o en la dacha. Lo que no coincide son los noventa, y eso se dice
  en una línea sin adjetivos.
- **El domingo 182 cuenta la Transición y la Movida** con fechas estables
  (1975, 1977, 1978, 1981, 1982) y sin ninguna cifra discutible. Y sirve de
  demostración: la época va en imperfecto, los hechos en indefinido.
- **La tarea final es una entrevista a un familiar mayor**, traducida al
  español por el alumno. Es la tarea más útil del curso hasta aquí, porque es
  exactamente lo que hace la cabeza al hablar de la propia vida en otra
  lengua.

**Nueve entradas duplicadas** las cazó `revisar_lexico.py` —entre ellas una
que la lección se duplicaba a sí misma, dos filas con la misma entrada en la
misma tabla—. Quedan los 13 de siempre.

## La unidad 12: empieza el A2 con el pasado (días 155-168)

Catorce lecciones, semanas 23 y 24. El curso pasa de 154 a **168 de 365** y
entra en **A2**: 1.448 tarjetas de vocabulario.

**Toda la unidad es una sola cosa: el pretérito indefinido.** Y la decisión
de fondo ya estaba tomada y documentada (2026-10-26): el perfecto se enseñó
primero, en la semana 18, siguiendo el PCIC y porque la salida del curso es
el DELE A2, que es peninsular. Aquí llega el indefinido, y el día 162 es la
frontera entre los dos.

Lo que decidió el contenido:

- **El hilo de las dos semanas es la tilde**, y cambia de bando a mitad de
  unidad. En los regulares es obligatoria y distingue palabras (*hablo* /
  *habló*); en los once irregulares es un error, porque el acento cae en la
  raíz. Se abre el lunes, se invierte el miércoles y vuelve en el test.
- **El aspecto ruso no sirve aquí, y se dice explícitamente.** «Говорил» y
  «поговорил» se oponen por aspecto; *he hablado* y *hablé* se oponen por
  **tiempo**. Es otro eje, y trasladar uno al otro es el error más duradero
  de todo el A2. La regla operativa que se da no es gramatical sino léxica:
  mire la palabra de tiempo.
- **«Esta mañana» es perfecto** aunque la mañana haya pasado: el día en que
  estuvo sigue abierto. Es el caso que más cuesta.
- 🌎 **Y en América la frontera casi no existe**: *hoy comí* es correcto allí.
  Se enseña la norma peninsular porque el examen lo es, y se marca la
  variante, que es la regla 8.
- **Los once irregulares se presentan como cuatro + siete**, con una sola
  tabla de terminaciones para todos. Lo que se aprende son once raíces, no
  sesenta y seis formas.
- **`dijeron` sin `i`** es la única excepción del paradigma (raíz en *j*), y
  no tiene apoyo en ruso: se aprende como ortografía.
- **`no pude` es «no conseguí» y `no quise` es «me negué»**, no «no podía» ni
  «no quería». Esos están en el imperfecto, que llega en la unidad 13.
- **Las biografías del domingo 161 y las fechas del 168** se escribieron con
  datos estables y universalmente citados —los años de nacimiento y muerte de
  Frida, Picasso y Messi; 1492; las independencias de 1810-1825; 1898— y sin
  ninguna cifra que cambie o se discuta (goles, premios contados, cifras de
  asistencia). Es el criterio de la regla 7 que ya se aplicó en la unidad 9.
  Un detalle que además enseña: Frida decía haber nacido en 1910, el año de la
  Revolución; su partida dice 1907.

**El validador cazó un tema que no coincidía con el calendario** (regla 4) en
la primera lección: el YAML dice «Pretérito indefinido -ar: вчера я говорил» y
yo había escrito otra cosa. Se cambió la lección, no el calendario.

**Diecisiete entradas duplicadas** las cazó `revisar_lexico.py` al cerrar cada
semana —entre ellas las tres centenas irregulares, que ya se habían enseñado
en la semana 8, y toda la frecuencia de la semana 10—. Quedan los 13 de
siempre, todos de las semanas 1 a 14.

**La prueba del día 167 se escribió primero con 18 ítems** y una nota de «elija
los seis mejores». Eso no es el formato: `evaluacion.md` §4 fija 6 + 6 + 3.
Recortada a quince exactos y comprobada ejecutando `pruebas.py`.

## La unidad 11: el nivel A1 cerrado (días 141-154)

Catorce lecciones, semanas 21 y 22. El curso pasa de 140 a **154 de 365**, y
con ellas **termina el nivel A1**: unidades 1 a 11, 1.316 tarjetas de
vocabulario.

**Esta unidad no enseña nada nuevo, y por eso fue distinta de escribir.** Son
cinco días de repaso, tres de simulacro, dos de proyecto y un examen. No hay
ni una palabra de vocabulario nuevo en los días de repaso: lo que hay es el
material de veintidós semanas puesto en tablas de decisión.

**Tres tipos de día que nunca se habían escrito** —`simulacro`, `proyecto`,
`examen`— y que `validar.py` **no sabía comprobar**: `APARTADOS` no los tenía,
así que un día de examen pasaba la validación con cualquier forma. Es el
agujero de siempre (lo escrito y lo que corre dejando de coincidir) y el
momento de cerrarlo es el primer uso. Ahora:

- **simulacro**: Инструкция · Задания · Ключи и подсчёт · Разбор ошибок.
- **examen**: Инструкция · Экзамен · Ключи и подсчёт · **Решение** — el
  último apartado no es un análisis sino la decisión de pasar de nivel, que
  es lo que distingue un examen de un simulacro.
- **proyecto**: Разминка · Подготовка · Работа · Итог. No se corrige: se
  prepara y se entrega.

Lo que decidió el contenido:

- **El día 146 es un simulacro de comprensión, y aquí no hay audio.** En vez
  de fingirlo, la instrucción dice la verdad: lea el texto en voz alta **una
  vez**, ciérrelo y conteste de memoria. Es más difícil que escuchar, no más
  fácil, y se dice así.
- **El corto del día 147 va con `[VERIFICAR]`** (regla 7). Desde este
  contenedor no se puede comprobar qué cortos están disponibles ni con qué
  subtítulos, así que el título lo pone el profesor. Lo que sí se escribió es
  el **método de los tres visionados** y el vocabulario de cine, que no
  depende de ninguna película, y una nota para que el día funcione igual si
  hoy no hay corto.
- **La rúbrica de los simulacros es la de `evaluacion.md`**, no una inventada,
  y el oral añade el quinto criterio —pronunciación— con la lista de
  interferencias de `contrastiva-ru-es.md` §1.
- **Las cinco interferencias se evalúan por lo que cuestan, no por lo que
  suenan.** La *o* átona convierte *tome* en *toma*, o sea lo cortés en
  familiar; la *r* múltiple convierte *pero* en *perro*. El acento se queda
  para siempre y eso se dice; lo que importa es que la palabra no se vuelva
  otra.
- **El día 150 es la lista negra entera**, los diez errores de
  `contrastiva-ru-es.md` §8 con el texto donde están todos, y la técnica de
  los **tres pasos** antes de entregar cualquier texto (artículos, ser/estar,
  *yo* de más). Es la única técnica de examen que seguro se amortiza.
- **El proyecto se parte en dos días a propósito**: el jueves el guion y el
  borrador, el viernes la grabación con **seis palabras** delante y nada más.
  Leer de un papel se oye, y no sirve para el lunes siguiente.
- **El examen son 45 puntos y el 60 % son 27**, que es la regla escrita en
  `evaluacion.md`. La tabla de decisión manda a un día concreto por grupo
  perdido, no a «repasar».
- **El domingo cierra con la lista can-do de 22 puntos** y con lo que cambia
  en A2, que es una sola cosa: **el pasado**. El ruso distingue aspecto
  («ел» / «съел») y el español distingue tiempo; es otro eje, y se avisa aquí
  porque la unidad 12 entera va sobre eso.

**El episodio de Ana e Iván del día 154 cierra el arco de A1** y es el del
YAML («Lo ha resuelto él»). Termina con la frase que abre el nivel siguiente:
*—¿Y eso cuándo se aprende? —A partir del lunes.*

**Y la suite encontró dos cosas al estrenarse los tres tipos**, las dos del
mismo sitio —el plegado de la clave, que es de esta misma mañana—:

- **Un `examen` y un `proyecto` no tienen ejercicios**, así que el enlace «ir
  a la clave» no se colocaba (no hay dónde) y la clave se plegaba igual: un
  botón que abre algo a lo que nada apunta. `CON_CLAVE_DE_EJERCICIOS` deja
  fuera los tres tipos sin ejercicios, cada uno por su motivo: `prueba` tiene
  su propio envoltorio, `examen` lleva la clave dentro del apartado de
  corrección porque hace falta ahí para decidir el nivel, y `proyecto` tiene
  un modelo, no una respuesta. La lista la lee también la prueba, en vez de
  copiarla.
- **«Задания» en plural no lo cubría «Задание» en singular** —la última letra
  es otra, así que no es subcadena— y los dos simulacros de comprensión se
  quedaban sin enlace a su clave.

**Lección de método, que costó dos suites de 8 minutos:** no se corre
`tests.test_curso` mientras se escriben lecciones. `test_docs_esta_al_dia` y
`test_los_tsv_de_anki_estan_al_dia` comparan el disco con lo construido, así
que una lección nueva a mitad de la corrida las pone en rojo por una razón
que no es un fallo. Se construye y se exporta **antes**, y la suite se corre
**al cerrar la unidad**.

## La unidad 10 entera: salud, cuerpo y médico (días 127-140)

Catorce lecciones, semanas 19 y 20. El curso pasa de 126 a **140 de 365**.

**Lo que se comprobó antes de escribir, y cambió el plan:** `tener que`, `hay
que` y `deber` **ya estaban enseñados** (semana 17, día 5, en el aeropuerto).
El calendario pone el día 131 como «tener que, hay que, deber», pero su foco
dice «matices de los tres», así que ese día no introduce nada: compara. Su
vocabulario nuevo es de consejo y de salud, no de gramática.

Lo que decidió el contenido:

- **El artículo en vez del posesivo es el hilo de las dos semanas.** *Me duele
  **la** cabeza*, no *mi cabeza*. Se abre el lunes, se repite en los síntomas,
  en urgencias (*se ha roto **el** brazo*) y en el test. Es el error nº 4 de la
  lista negra y el que más dura.
- **Las cuatro palabras que el ruso junta**: *el brazo* + *la mano* = «рука»;
  *la pierna* + *el pie* = «нога». No es un matiz: decir *me duele el pie* en
  la consulta hace que le miren el otro extremo de la pierna.
- **Tres verbos para un «холодно»**: *hace frío* (tiempo), *tengo frío* (yo),
  *está frío* (la cosa). Los tres ya existían sueltos; aquí se ponen juntos.
- **`no tienes que` NO es «нельзя»** sino «no estás obligado». El prohibitivo
  es *no debes*. Es la trampa del día 131 y una pregunta del test.
- **El imperativo de usted cambia la vocal «al revés»** (-ar → -e, -er/-ir →
  -a) y no hay lógica que ayude: se aprende como hecho. La forma de tú, en
  cambio, es la de «él/ella», que ya se sabe desde la semana 4 — o sea que la
  mitad del lunes es recordar, no aprender.
- **La tilde de `tómalo` se explica contando sílabas**: dos, no; tres o más,
  sí. Y el acento no se mueve nunca, que es lo que la tilde está sosteniendo.
- **El 112 es uno y no tres.** En Rusia hay tres números; en España el
  operador decide. Y la dirección se dice la primera, porque si se corta la
  llamada la ayuda sale igual.
- **Nada de lo que se come cura nada** (regla 7). El domingo habla de la dieta
  mediterránea y del mate como costumbres, con el aviso explícito, y los datos
  son los verificables sin cifra inventada: la declaración de la UNESCO de
  2010, los horarios de las comidas y cómo se ceba un mate.

**Seis entradas se habían colado por duplicado** y las cazó
`revisar_lexico.py` al cerrar cada semana: `regular`, `quedarse en casa`,
`avisar`, `la ventana`, `caminar`, `correr`, y las tres de frecuencia (`a
veces`, `casi siempre`, `una vez / dos veces`). Las últimas tres importan más
que las otras: **toda la frecuencia se enseñó en la semana 10, día 3**, así que
el día 136 dejó de presentarla como nueva y la usa como material conocido, que
es lo que pide `metodologia.md`. Quedan los 13 duplicados de siempre, todos de
las semanas 1 a 14.

**La prueba del día 139 se escribió para que `pruebas.py` la lea**, no solo
para imprimirla: 15 preguntas en tres bloques, clave con «нед. N, день N» en
cada respuesta. Comprobado ejecutando el analizador — las 15 se leen y cada una
enlaza a su lección.

**Lo que NO se regenera por unidad, y es deliberado**: el audio (hace falta
`OPENAI_API_KEY`; ya van 4.404 frases y 1,67 USD para todo lo escrito), los
dibujos y el `.apkg` de 22 MB. Los TSV sí, porque hay una prueba que lo exige.

## La unidad 14: narrar, y el tercer bloque del test cambia (días 183-196)

Catorce lecciones, semanas 27 y 28. El curso pasa de 182 a **196 de 365** y
cierra la mitad del A2: **1.704 tarjetas** de vocabulario.

**La unidad no añade un tiempo nuevo: enseña a usar los tres que ya hay.** El
alumno sabe perfecto (semana 18), indefinido (unidad 12) e imperfecto (unidad
13); aquí aprende a contar algo con los tres a la vez, que es lo que de verdad
pide el DELE A2 en la expresión escrita y en la oral.

Lo que decidió el contenido:

- **`estaba durmiendo` es la tercera forma de fondo**, y el día 183 la pone al
  lado de `dormía` en vez de presentarla sola: *dormía* es la costumbre o el
  fondo largo, *estaba durmiendo* es **ese** momento exacto. En ruso las dos
  son «я спал», así que la elección no la da el verbo ruso y hay que darla por
  escrito.
- **Los conectores son el día 184 entero** porque son la diferencia entre una
  lista y un relato, y el rusohablante los tiene todos en su lengua: el
  problema no es entenderlos sino acordarse de ponerlos.
- **Los cinco irregulares del día 185 (`leyó, oyó, durmió, pidió, trajo`) son
  los que quedaban** del indefinido: el cambio ortográfico de la *y*, el
  cambio vocálico de tercera persona y la raíz en *j*. Se dan juntos porque
  los tres son de tercera persona, que es la que usa un relato.
- **`hace dos años` / `desde hace` / `llevo … estudiando`** es el día 190 y es
  el punto donde el ruso más estorba: «два года назад» y «уже два года»
  parecen lo mismo y son tiempos distintos en español.
- **El día 192 cuenta nueve viñetas** y la lección es que entre una lista de
  escenas y un relato hay exactamente tres cosas: el fondo que no está en la
  imagen, las conexiones y la emoción. Es el método que se usa el viernes.
- **El día 196 es humor**, que es el contenido cultural más difícil de enseñar
  y el único donde no hay nada que memorizar: se explica por qué un chiste no
  se traduce y se dan los dos o tres mecanismos que sí viajan.
- **Las leyendas del día 189 van sin cifra inventada** (regla 7): La Llorona
  no tiene fecha y el Cid se cuenta con lo verificable —el Cantar es del siglo
  XII, Rodrigo Díaz murió en Valencia en 1099— y nada más.

**Y aquí el test de unidad cambia de forma, que es lo que había que
comprobar antes de escribirlo.** `evaluacion.md` §4 fija 6 + 6 + 3, pero el
tercer bloque deja de ser ortografía **a partir de la unidad 14** y pasa a ser
«Выражения». No es un detalle de formato: a esta altura el alumno ya no falla
por tildes sino por construcciones (*hace* / *desde hace*, *tan* / *tanto*,
*sin ganas de*), y el test tiene que medir eso. Comprobado ejecutando
`pruebas.py`: las 15 se leen y cada una enlaza a su lección.

**Un fallo que la propia prueba encontró**: el día 195 tenía dos opciones
idénticas en la pregunta 4 de gramática (`б) leyó` y `г) leyó`), o sea una
pregunta con dos respuestas correctas. Se barrieron después **todos** los
tests de unidad del curso buscando opciones repetidas: 0 problemas más.

**Tres entradas duplicadas** las cazó `revisar_lexico.py` al cerrar la semana
28, las tres en el día 192: `la parada` (ya en S08D5), `al fondo` (S13D2) y
`la maleta` (S17D5) — las tres son palabras del dibujo que el alumno ya
conocía. En su lugar entraron `dormirse` (que no es `dormir`, y ese contraste
pasó al bloque de contraste del día), `junto a` y `el relato`. Quedan los 13
de siempre, todos de las semanas 1 a 14.

## La unidad 15: estudios y trabajo (días 197-210)

Catorce lecciones, semanas 29 y 30. El curso pasa de 196 a **210 de 365** y
**1.831 tarjetas**.

**Lo que se comprobó antes de escribir, y cambió el plan**: `saber` **no
estaba enseñado en ninguna parte**. Del volcado de las 1.257 entradas salía
`conocer (conocí)` en S23D2, `poder (puedo)` en S10D2 y `podría (вежливая
просьба)` en S18D5, pero de *saber* solo la frase hecha `sabes qué me pasó`
(S27D4). O sea que el día más temido de la unidad —*saber* contra *conocer*—
tenía de verdad material nuevo y no era un repaso.

Lo que decidió el contenido:

- **La regla operativa de `saber` / `conocer` es sintáctica y no semántica**:
  mire la palabra que va DESPUÉS. Oración subordinada o infinitivo → *saber*;
  sustantivo (persona, lugar, cosa) → *conocer*. Explicada como «hecho frente
  a trato» falla en los casos difíciles; así acierta en los quince ítems del
  test.
- **`sé nadar` ≠ `puedo nadar`** es el segundo eje del mismo día, y aquí el
  ruso ayuda («умею» / «могу» son dos verbos). Lo que no ayuda es el inglés.
- **`llevo tres años aquí` es PRESENTE**, y es el error que más dura. El día
  199 lo da con tres formas equivalentes (*llevo*, *llevo* + gerundio, *desde
  hace*) y la regla de qué pide cada una: *desde* + punto, *desde hace* +
  plazo.
- **El currículum se escribe SIN verbo** (día 200). Una línea de CV es cargo,
  sitio y ciudad; el verbo solo aparece en las funciones y en forma de
  sustantivo (*Seguimiento de clientes*). Es un género, no gramática, y por
  eso se enseña con un CV entero delante.
- **El condicional entra como cinco fórmulas y no como tiempo verbal**
  (*me gustaría*, *podría*, *preferiría*, *querría*, *le agradecería que*).
  En A2 eso es lo que hace falta; el paradigma llega después.
- **El correo formal lleva DOS PUNTOS después del saludo**, no coma: la coma
  es inglesa y el signo de exclamación, ruso. Y no existe «Уважаемый Иван
  Петрович»: no hay patronímico, se trata por apellido.
- **El defecto se cuenta en dos partes**: *me cuesta* + lo que se está
  haciendo al respecto. Sin la segunda parte es una queja.
- **El domingo de la unidad avisa de lo que las historias de emprendedores
  no cuentan**: por cada taller que acaba en Inditex hay miles que cierran, y
  de esos no se escribe. Los dos retratos están para el español que usan, no
  para la moraleja.

**Nada con cifra inventada** (regla 7): de Amancio Ortega se dan los hechos
estables y citados en todas partes (empezó de recadero a los catorce, el
taller de 1963, la primera tienda de Zara en A Coruña en 1975) y ninguna
cifra de facturación ni de patrimonio. El segundo retrato es explícitamente
**un nombre inventado** para un caso corriente, y la lección lo dice en la
primera línea: *María Elena Ruiz no existe*.

**El test de la unidad** mantiene el tercer bloque «Выражения» que estrenó la
unidad 14. Comprobado con `pruebas.py`: 15 preguntas, las 15 enlazan a su
lección. La primera versión se escribió con los enunciados en **negrita y
numeración 1–15 corrida**, y `pruebas.leer` devolvió `None` —su `INICIO`
espera `^N. ` y la numeración **se reinicia en cada bloque**—. El fallo
seguro hizo su trabajo: la unidad se habría quedado sin test interactivo en
silencio. Y al rehacerlo apareció lo otro: **las quince respuestas correctas
eran la а)**. Ahora son б×5, в×5, а×3, г×2.

**Nueve entradas duplicadas** las cazó `revisar_lexico.py` al cerrar cada
semana —`el ingeniero`, `el periodista` (S03D4), `el edificio` (S07D3),
`alguna vez` (S18D2), `la fecha de nacimiento` (S23D4), `la asignatura`
(S25D4), `la referencia` (S14D3), `el plazo` (S14D4) y `el asunto`
(S14D5)—. Todas sustituidas por palabras que están en el cuerpo de su propia
lección. Quedan los 13 de siempre.

**De paso, un carácter cirílico dentro de una palabra española**:
`**1. Ситуación**` en la semana 27, día 4, donde los tres rótulos de la tabla
son términos españoles (*Situación*, *Problema*, *Desenlace*). Un barrido de
las semanas 27 a 30 buscando tokens con letras de los dos alfabetos lo
encontró; conviene repetirlo al cerrar cada unidad, porque a ojo no se ve.

## La unidad 16: instrucciones, ciudad y servicios (días 211-224)

Catorce lecciones, semanas 31 y 32. El curso pasa de 210 a **224 de 365** y
**1.954 tarjetas**.

**Lo que se comprobó antes de escribir**: el imperativo de *tú* y de *usted*
ya estaba dado en la unidad 10 (`¡descansa!`, `¡haz!`, `¡pon!`, `¡ven!`,
`¡di!`, `siéntese`, en S20D1-2). Así que esta unidad añade solo *vosotros*,
*ustedes* y **el negativo**, que es lo de verdad nuevo.

Lo que decidió el contenido:

- **El imperativo de *vosotros* es el más fácil del idioma y se dice así**:
  infinitivo, `-r` → `-d`, **sin una sola excepción**. Lo que sí tiene truco
  es el reflexivo, donde la `-d` desaparece (*sentad + os → sentaos*).
- **Lo del negativo no es que lleve `no`: es que cambia la forma del verbo.**
  En ruso «говори» → «не говори» es el mismo verbo con una partícula; en
  español *habla* → *no hables* es otra forma. Es la dificultad central de la
  unidad y no se puede rodear.
- **Los irregulares del negativo salen de la forma «yo»**: *hago* → *no
  hagas*, *vengo* → *no vengas*. Eso ahorra la tabla entera y deja solo tres
  excepciones (*ser*, *ir*, *dar*).
- **`le + lo = se lo` no tiene ningún equivalente ruso**, y la lección lo dice
  así: es fonética, no lógica, y `le lo` simplemente **no existe en el
  idioma**. Lo que sí ayuda del ruso es el orden («дай мне это» = *dámelo*).
- **El imperativo de `usted` se enseña para LEERLO, no solo para decirlo.** El
  lunes y el martes de la semana 31 existen para el miércoles de la 32, donde
  el policía contesta *llame al banco, vaya al consulado, quédese con el
  justificante* y hay que entenderlo rápido y en mal momento. La misma forma
  está en el cajero automático, en el cartel y en la receta: una gramática,
  tres sitios.
- **`he perdido` / `me han robado` / `se me ha caído` es una decisión, no una
  conjugación**: en comisaría son tres denuncias distintas. Y `me han robado
  la cartera` va sin posesivo, por la misma regla que `me duele la cabeza`.
- **El domingo de la semana 32 es la regla 8 en acción**: TIRE/JALE,
  AUTOBÚS/CAMIÓN/GUAGUA/COLECTIVO, ASCENSOR/ELEVADOR, MÓVIL/CELULAR. Ninguno
  es más correcto; el curso enseña el más extendido y marca el otro con 🌎.
- **Nada con cifra inventada** (regla 7): del NIE, el padrón y la cita previa
  se cuenta el procedimiento y el orden, que son estables, y ni un precio ni
  un plazo. Donde el alumno no sepa uno, la lección le pide escribir
  `[VERIFICAR]`, como hacen los autores.

**El test de la unidad** mantiene el bloque «Выражения». Y aquí la primera
versión tuvo **dos fallos, los dos propios del formato**: los enunciados
escritos en negrita y numerados 1–15 corridos (`pruebas.leer` → `None`; su
`INICIO` espera `^N. ` y la numeración se reinicia por bloque), y, al
arreglarlo, **diez de las quince respuestas correctas en la б)**. Ahora son
а×4, б×4, в×4, г×3, y las quince se verificaron comparando el TEXTO marcado,
no la letra.

**Diecisiete entradas duplicadas** las cazó `revisar_lexico.py` al cerrar cada
semana. Dos de ellas se colaron al sustituir las otras —`hacer un favor`
junto a `pedir un favor` en la misma tabla, e `imprimir` dos veces en la
misma tabla— y las vio una lectura de la tabla entera, no el script: el
informe compara entre lecciones, así que **un duplicado dentro de una sola
tabla no lo detecta nadie**. Conviene mirar la tabla completa después de
cada sustitución.

## Los quince tests de unidad no medían nada (2026-10-27)

Contadas las respuestas correctas de los quince días de `prueba`: en la
semana 24, **catorce de quince eran la б)**. Marcando todo б se sacaba 14/15 y
se «aprobaba» la unidad sin saber nada. En la 18 y la 4 eran doce de quince, y
en **doce de los quince tests** la letra más repetida se llevaba más del 45 %.
Desde que `pruebas.py` los hace contestables en la web (2026-10-27), el alumno
se puntúa con eso.

Ahora los quince están en **4/4/4/3**. No cambió ni un enunciado ni el texto
de una opción: solo su orden, la letra de la clave y las referencias a letras
de la prosa del análisis. Verificado comparando el TEXTO de la respuesta
marcada pregunta por pregunta contra la versión anterior, más el conjunto de
opciones, el enunciado y el enlace a la lección: **0 diferencias en 225
preguntas**.

**Y el reparto no puede ser un ciclo.** La primera corrección usaba `n % 4`,
que deja la secuencia **а-б-в-г-а-б-в-г**: equilibrada en el recuento y
trivial de aprender, o sea el mismo defecto con otra cara. Lo delató una
prueba que fijaba la secuencia literal de la semana 2 y que, al ponerse en
rojo, enseñó el ciclo entero. Ahora el plan se baraja con una semilla sacada
del nombre del fichero —determinista, así que reconstruir el sitio no mueve
ninguna respuesta— y se descarta cualquier plan con tres letras iguales
seguidas o con una escalera ascendente. `test_la_letra_correcta_esta_repartida`
exige las tres cosas en los quince tests.

**Las dos pruebas que se pusieron en rojo tenían razón y las dos medían mal**,
y es el mismo defecto: fijaban el CONTENIDO de un fichero de datos.

- `test_una_clave_que_no_cuadra_no_genera_test` rompía la clave con dos
  `.replace()` de cadenas literales («5 б (нед. 2, день 5) · 6 а»). Al cambiar
  las letras, los dos `.replace()` se quedaron en nada y la prueba comprobaba
  un fichero intacto. Ahora la avería se DERIVA del fichero y cada paso exige
  además que se haya aplicado de verdad.
- `test_las_respuestas_salen_igual_que_en_la_clave_del_profesor` guardaba la
  secuencia «бвбббавбгббабвв». Ahora vuelve a leer la clave con una expresión
  regular propia y la compara con lo que devolvió `pruebas.leer`, en los
  quince tests y no solo en uno: comprueba la RELACIÓN, que es lo que importa,
  y no se rompe el día que el contenido cambie por una razón legítima.

**Dos cosas más que costaron el arreglo:**

- Cortar el fichero por la cadena `## 3.` para separar la prosa del test
  también casa con `### 3. Орфография`, que está DENTRO del test. Con ese corte
  la sustitución reescribía la letra de una opción de verdad y rompía la
  secuencia а, б, в, г; la semana 26 se descartaba por eso. El corte va por el
  índice de línea de la siguiente cabecera `## `.
- **Las referencias de la prosa se arreglaron A MANO: quince.** El remapeo
  automático acierta cuando la prosa cita la opción tal cual; no acierta
  cuando la alarga («а) a el parque» donde la opción es «a el»), le cambia la
  mayúscula, la envuelve en tres asteriscos, la parte entre dos renglones o
  —el caso que más se repite— cita una FRASE que no es ninguna opción y hay
  que razonar a cuál señala («no está metro» apunta a la opción *está*). Y la
  semana 10 usa otro formato entero, `**Грамматика 1б)** *hazo*`, que ningún
  patrón de los demás reconoce. La comprobación final lee las 28 referencias
  comprobables y exige que la letra case con la posición real de la opción.

## «A simple vista»: los dibujos suben y el sitio estrena tipografía (2026-10-27)

El profesor volvió sobre la portada: *«aún crees que la página se ve aburrida,
no es agradable a simple vista»*, y después *«y la fuente de la letra no crees
que es aburrida?»*. Las dos veces tenía razón, y las dos veces la causa se
podía medir en vez de opinar.

### Lo que se midió, porque no se podía mirar

Chromium no arranca en esta sesión —la cuota de disco está gastada— así que
**no hubo captura**: el diagnóstico sale de leer el HTML construido, y se dijo
así al profesor en vez de fingir que se había visto. Lo que el HTML decía de la
primera pantalla del móvil (390 px), en orden: título, lema, dos botones, la
línea del test y la del contador. **Cinco líneas de letra sobre crema y ni una
imagen.** Los doce dibujos —lo único que este sitio tiene y nadie más, y que ya
está pagado— empezaban DEBAJO del pliegue, bajo un `<h2>`. El mejor activo de
la página era invisible justo en el segundo en que el visitante decide si se
queda.

### Los dibujos suben al héroe

`_arte_del_heroe` pone **seis** de los doce arriba del todo. En el móvil la
tira va ANTES del título (`order:-1`): ves comida, un perro y una guitarra
antes de leer una palabra. En escritorio (≥46rem) el héroe pasa a dos columnas
y la tira se coloca al lado, para no empujar los botones fuera de la vista.

- **Seis y no doce**: tienen que caber en UNA fila dentro de los 358 px de la
  columna del móvil. Doce obligarían a dos filas o a hacerlos tan pequeños que
  dejarían de leerse como dibujos.
- **Son los MISMOS ficheros que la vitrina de abajo**, así que el navegador los
  sirve de caché y no cuestan un byte más. Hay una prueba que lo exige.
- **Es decoración y no interfaz**: `aria-hidden`, `alt` vacío, sin enlace y sin
  botón. Lo que se pulsa y suena es la vitrina, que además enseña la palabra.
- **Se cae sola**, como la vitrina y la baraja: sin dibujos no sale nada, y por
  debajo de `HEROE_MINIMO` (4) tampoco, porque cuatro sueltos en una fila
  pensada para seis se leen como una página a medio cargar.

### La tipografía: Literata y Onest, servidas desde el dominio propio

El sitio **no cargaba ninguna fuente**. El cuerpo decía `ui-serif, Georgia,
"Times New Roman"` y los títulos `ui-sans-serif, system-ui`. Consecuencia
concreta: en Windows y en Android el cirílico caía en Times o en una fallback
mediocre —la cara de un libro de texto de 1998— mientras que en iPhone caía en
New York y se veía bien. **El sitio se veía peor justo en los aparatos del
público al que va dirigido**, y eso no se nota desde un Mac.

El profesor eligió **B · Literata + Onest** sobre una lámina con cuatro
tipografías puestas en la misma pantalla (la misma forma en que eligió la voz
`shimmer` y el estilo plano de los dibujos). La lámina se dibujó con PIL, no
con un navegador, y se le dijo: el espaciado real será algo mejor.

**No se enlaza a Google Fonts, y no es manía.** Dos razones: la política de
privacidad de este sitio promete que sin anuncios no se carga nada de terceros,
y un `<link>` a `fonts.googleapis.com` la volvería mentira; y hay sentencias
alemanas que multan por incrustar Google Fonts, porque manda la IP del
visitante a Google — y Alemania es uno de los países del público. Los diez
`.woff2` están en `docs/fonts/` (430 KB en total) y se sirven desde el dominio.

Tres cosas que lo rompen sin avisar:

- **`CSS` no puede pasar por `.format()`**: la hoja está llena de llaves de CSS
  y habría que duplicarlas todas. Por eso las `@font-face` viven aparte, en
  `CARAS`, y se concatenan con `caras(raiz)`. Si alguien las metiera dentro de
  `CSS`, el `{raiz}` llegaría literal al navegador y **ninguna fuente cargaría
  sin que nada fallara**.
- **La ruta depende de la profundidad de la página**, y aquí no la revisa
  nadie: `revisar_adsense.py` mira `href=` y `src=`, no los `url()` de una hoja
  de estilo. Es la CUARTA vez que este proyecto se tropieza con una ruta
  escrita sin tener en cuenta en qué carpeta está la página —el conmutador de
  idioma, las tarjetas del mapa, los destinos del probador— así que hay una
  prueba que las resuelve contra el disco desde cuatro páginas de tres
  profundidades.
- **Cada cara trae su `unicode-range`**: sin él el navegador se baja las diez
  en cuanto pinta. Con él, una lección rusa no toca el latino hasta el primer
  ejemplo español. Y la **cursiva es real y no sintética**, porque el curso
  pone todos los ejemplos españoles en `<em>` y un navegador que inclina la
  redonda deja medio curso sucio.

### Dos textos que sonaban raro, y el usted que faltaba

También los trajo el profesor: *«Restaurar con un código»* y *«¿Ya sabe algo de
español? Test de nivel →»*, «y esto suena confuso».

- **El enlace del test reusaba el TÍTULO de la página.** «¿Ya sabe algo de
  español? Test de nivel →» son dos titulares seguidos: el segundo es un
  sintagma nominal, no una acción, y no dice para qué sirve el test. Ahora cada
  idioma tiene `ya_sabe_enlace` y dice lo único que importa: que el test te
  coloca en la lección por la que empezar.
- **«Restaurar con un código» no significa nada para quien acaba de llegar** —y
  ese botón está visible precisamente para él, porque el que limpió el
  navegador no tiene progreso que enseñar (nota del 2026-10-27)—. Ahora nombra
  lo que recupera; de dónde sale el código lo explica la caja al abrirse.
- **Y al ir a tocarlo apareció otra cosa: el español mezclaba tú y usted.**
  Contado sobre el YAML, 24 cadenas de usted contra 6 de tú, y **cinco de las
  seis estaban en el bloque del respaldo** —«pégalo en tus notas», «Pega aquí
  tu código», «guarda tu código»—. Mezclar las dos formas en la misma pantalla
  se nota más que una falta de ortografía. Hay una prueba que lo fija, y su
  primera versión se puso en rojo con «el progreso **se guarda** solo en este
  navegador», que es impersonal: la regla quedó solo con las marcas que no
  admiten otra lectura (posesivos, pronombres y formas verbales de segunda
  persona), porque `guarda`, `pega` y `empieza` son también tercera.

### Lo que queda pendiente y por qué

**El sitio no se reconstruyó.** `construir_sitio.py` escribe unos 130 MB y a
esta sesión le quedan 9 MB de cuota: los 30 GB que la gastaron son las
carpetas temporales que `test_docs_esta_al_dia` deja en `/tmp` en cada corrida
de la suite, y borrarlas lo deniega el clasificador de permisos. O sea que
`docs/` sigue en 154 lecciones y **sin fuentes, sin la tira del héroe y con los
textos viejos**, aunque los `.woff2` ya están versionados.

`test_docs_esta_al_dia` ya estaba en rojo antes de estos cambios, por lo mismo:
el repositorio lleva 224 lecciones y `docs/` 154. Las catorce pruebas nuevas no
construyen nada —`caras()` y `_arte_del_heroe` son funciones puras y las rutas
se resuelven contra el disco— y pasan, pero **lo visual no está comprobado en
un navegador**: Chromium tampoco arranca con este disco.

Para cerrarlo hacen falta dos comandos en una sesión nueva:
`scripts/construir_sitio.py` y la suite entera.

## El disco de la sesión se agota antes que el trabajo (2026-10-27)

Escribiendo la unidad 12 la máquina se quedó **sin cuota de disco**: `df`
decía 252 GB de volumen, 39 GB usados y **280 KB libres**, que es la firma de
una cuota gastada y no de un disco lleno. A partir de ahí fallaba todo, hasta
`git status`: el intérprete no podía ni escribir su propia salida.

**Lo que la gastó fue reconstruir el sitio.** `construir_sitio.py` escribe
unos 130 MB (154 lecciones × 3 idiomas, más los índices), y `test_docs_esta_al_dia`
lo construye otra vez en un temporal en cada corrida de la suite. Con una
decena de reconstrucciones y media docena de suites, el sistema de archivos se
queda con todas las versiones intermedias aunque los archivos se sobrescriban.

**Lo que se aprende para la próxima:**

- **Escribir lecciones es barato** (15 KB cada una) y **reconstruir es caro**.
  Se puede escribir una unidad entera validando con `validar.py`, que no
  construye nada, y dejar `construir_sitio.py` para el final.
- **La suite completa cuesta una reconstrucción**, así que no se corre por
  lección ni por semana: una vez por unidad, y con el árbol ya construido.
- **Los temporales se liberan borrando**, y eso sí funciona con el disco
  lleno. Lo que no se puede es escribir.
- Con la cuota gastada **el trabajo se commitea igual** si se libera lo
  propio primero; una sesión nueva arranca en una máquina limpia.

## La Red de Publicidad de Yandex, cableada y apagada (2026-10-27)

El profesor se dio de alta en РСЯ y creó el primer bloque. **Por qué además de
AdSense, y no en vez de**: AdSense no sirve anuncios a usuarios dentro de Rusia
desde marzo de 2022, y este curso está escrito en ruso. Las dos redes no
compiten, se reparten el mapa.

- **Se enciende por BLOQUE, no por cuenta**, al revés que AdSense: no hay un
  `ca-pub-…` que valga para todo, cada hueco trae su identificador entero
  (`R-A-20290424-1`). Por eso `hay_yandex` mira si hay ALGÚN bloque puesto.
- **Un hueco, una red.** Dos anuncios en el mismo contenedor no es una opción,
  así que si la ranura tiene id de Yandex manda Yandex y si no, AdSense. No es
  arbitrario: AdSense funciona hoy en **anuncios automáticos**, que se colocan
  solos y no usan estas tres ranuras, así que dárselas a Yandex no le quita
  nada.
- **El cargador va una vez por página** (`context.js` en el `<head>`) y sirve
  para los tres huecos. `yaContextCb` es una cola, así que el orden entre el
  `<head>` y el cuerpo da igual y no hace falta esperar al `DOMContentLoaded`.
- **El identificador se limpia a `[A-Za-z0-9_-]`**, y esto no es paranoia de
  más: se escribe DENTRO de un `<script>`, donde `html.escape` no protege de
  nada —una comilla cerraría la llamada—. Sale de un YAML que edita una
  persona a mano. Hay una prueba que mete comillas y llaves.
- **Enciende el aviso de cookies y un párrafo propio en la política**, con el
  enlace de exclusión de Yandex. Cargar una red y no decirlo es exactamente la
  forma de que la política mienta, y la de aquí presume de no cargar nada de
  terceros cuando está vacía.

**Sigue APAGADO a propósito** (`web/sitio.yaml`, `yandex.bloques` vacío): el
sitio está en revisión de AdSense y su revisor abre la web en vivo.
Encontrarse otra red a media revisión es pedir un rechazo. En cuanto llegue el
veredicto es pegar el identificador en la ranura que se quiera y reconstruir.

**De paso, `TestLaPublicidad._con()` apaga ahora también Yandex**, por la misma
razón que ya tenía escrita para AdSense: el día que el profesor pegue un
identificador, esas pruebas no pueden cambiar de significado sin que nadie haya
tocado el generador.

**Lo que no se resolvió y es del profesor**: con qué estatus puede ser partner
de РСЯ. Es ciudadano peruano con visa de estudiante viviendo en Rusia; el
estatus «физлицо» está cerrado a partners nuevos residentes, самозанятый
(НПД) solo lo pueden pedir ciudadanos de la UEEA y de Ucrania, e ИП pide РВП o
ВНЖ. Queda preguntar a soporte de Yandex y a un contable: 183 días en Rusia lo
hacen residente fiscal ruso aunque no tenga permiso de residencia, y eso toca
también su AdSense (Google cerró las cuentas de editores rusos en agosto de
2024).

## La portada se toca: la vitrina suena y hay tres preguntas (2026-10-27)

El profesor lo dijo así: «no crees que a la pagina le falta mas interactividad,
es como aburrida al comienzo». Y tenía razón **en el sitio exacto**: el curso es
interactivo por dentro —4.225 botones ▶, 189 huecos que se rellenan, las pruebas
de unidad contestables— y la portada solo se leía. Quien llega y no pulsa
«empezar» no toca nada en toda la página.

**No se escribió contenido nuevo para ninguna de las dos cosas**, que es lo que
hace que quepan en una sesión: los audios y las preguntas ya estaban pagados y
en disco.

### La ficha de la vitrina suena

Las doce palabras de la portada ya tenían dibujo; se comprobó que las doce están
también en `docs/audio/indice.json`, y ahora cada tarjeta es un botón que las
dice. Reutiliza `AUDIO_JS`, el mismo reproductor único de las lecciones, así que
al pulsar la segunda se para la primera.

- **La ficha ENTERA es el botón, no un ▶ al lado.** En el móvil un icono de doce
  píxeles junto a una palabra no se acierta con el dedo.
- **Hay que apagarle el cromo del navegador** (`background:none;border:0;
  font:inherit`): sin eso sale un botón gris con su borde DENTRO de la tarjeta.
  No se ve razonando, se ve abriendo la portada.
- **La traducción pasó de `.vitrina span` a `.vitrina .ru`.** Desde que la ficha
  muda es un `<span>`, el selector corto le daba a la tarjeta entera el tamaño de
  letra de la traducción.
- **Una palabra sin locutar se queda como estaba**, en un `<span class="ficha">`:
  el audio se genera por tandas, así que «algunas sí y otras no» es el estado
  normal un tiempo y la vitrina no puede encogerse por eso.
- Comprobado en navegador y no deducido: doce botones, los dos MP3 pedidos de
  verdad en la red, `aria-pressed` a `true` y la anterior apagada, cero errores
  de JS. **La señal es el MP3 pedido**, no el `aria-pressed`: `aria-pressed` solo
  se pone si `play()` resolvió, así que sobre `file://` da «false» con el código
  bien.

### Tres preguntas jugables, dentro del párrafo que las merecía

`_probador` coge los **tres primeros grupos** de `programa/test-nivel.yaml`
—unidades 1 a 3— y los juega en la portada. Va DENTRO del apartado «en qué se
diferencia este curso», justo donde el texto promete que la lección nombra el
error antes de que lo cometas: era el mejor párrafo de la página y estaba en
forma de texto.

- **El error se enseña al contestar, no al final.** Con tres preguntas, un
  resumen final no lo lee nadie; y ese discurso —por dónde te traiciona el ruso—
  es lo único que esta página tiene que demostrar.
- **Mismo barajado que el test de nivel y por el mismo motivo**: se COPIA la
  pregunta (`opciones.slice()`), porque sobre el original la segunda partida
  encontraría las opciones ya movidas y `correcta` apuntando a otra cosa. Es el
  fallo que le diría «has fallado» a quien acertó.
- **Termina en dos botones: la lección 1 y el test completo.** Quien acierta las
  tres no necesita empezar por el día 1, y ahí es donde se entera de que existe
  el test; quien falla ya tiene la razón para empezar.
- **Los dos destinos viven dentro de un `<script>`**, así que
  `revisar_adsense.enlaces_rotos` no los mira desde el 2026-10-26. Hay una prueba
  que los resuelve contra el disco en los tres idiomas: o se comprueban ahí o no
  los comprueba nadie. Es la tercera vez que un enlace escrito sin tener en
  cuenta la carpeta de la página se cuela por este hueco.
- **Nace oculto y lo enciende el navegador**, como el resto del sitio. Sin
  JavaScript no hay botón, y el párrafo de contraste que hay encima ya explica lo
  mismo en texto.
- **`probador_siguiente` y `probador_ver` son textos propios.** La primera
  versión los armaba con los del test (`de` + flecha), y en ruso eso daba
  **«из →»**, que significa «de». Hay una prueba que exige que no coincidan.
- **Sin banco suficiente no sale nada**, como la vitrina y la baraja: media
  partida es peor que ninguna.

**Lo que esto NO hace**: no mete a nadie en el sitio. La portada ahora retiene a
quien llega; traer visitas sigue siendo lo de las redes, y el cuello de botella
de verdad.

## Estado (2026-10-26)

- Programa anual completo (365 días) y documentación del método.
- **224 lecciones escritas** (semanas 1-32 enteras): el nivel A1 completo y
  cinco unidades de A2, 1.954 tarjetas de vocabulario. Las 21 primeras
  revisadas; el resto son borradores.
  **`docs/` va por detrás**: se quedó en 154 lecciones porque la cuota de
  disco de la sesión se agotó (ver más abajo). Las 42 últimas están en el
  repositorio y no en la web hasta que alguien corra `construir_sitio.py`
  (son 70 lecciones de diferencia).
- Sitio público en `docs/` con portada, índice, test de nivel, «О курсе»,
  contacto y política de privacidad. Tres idiomas (ru/es/en) —el test solo en
  ruso, como las lecciones—, tema claro y oscuro, y progreso del lector
  guardado en su navegador sin registro. La publicidad se configura en `web/sitio.yaml` y está
  apagada; sin identificador de AdSense no se carga nada de terceros.
- **El sitio está EN LÍNEA en `https://espanoldesderuso.com`, con certificado**
  (confirmado por el profesor el 2026-10-27, abriéndolo en su navegador). La
  cadena entera: dominio en Cloudflare Registrar → 9 registros DNS en gris →
  GitHub Pages con dominio propio → certificado y Enforce HTTPS. **Desde este
  contenedor nada de eso se puede comprobar**: no hay DNS —ni `google.com`
  resuelve— y el proxy niega el endpoint `/pages` de la API. Lo que pase con la
  web en internet solo lo puede contestar alguien abriéndola.
- **AdSense: el sitio está verificado y enviado a revisión** (2026-10-27). El
  identificador es `ca-pub-6339208855562328`, el `ads.txt` está en la raíz y el
  script en las 125 páginas. `scripts/revisar_adsense.py` da **10 listo · 0
  falta**. Queda esperar el veredicto (de días a dos semanas) y **publicar el
  CMP** en AdSense → Privacidad y mensajería, que hace falta antes de que se
  sirvan anuncios en la UE y que la banda de cookies de aquí NO sustituye.
- **El audio está hecho** (2026-10-26): 3.543 frases locutadas con la voz
  `shimmer`, 1,30 USD, 92 MB a 64 kbps, y 4.225 botones ▶ en 94 de las 100
  lecciones. Comprobado que suena en navegador.
- Pendiente: lecciones 101-365 (y su audio, que son otros ~4 USD en total),
  más libros de referencia, y lo de «Pendiente de revision del profesor» de
  arriba.
