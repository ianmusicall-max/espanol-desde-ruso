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

- `pagina(..., traducida=False)` para esas dos familias: el conmutador lleva a
  la **portada de ese idioma** —mejor que un 404, y el sitio sí está traducido
  aunque la lección no— y el `hreflang` **desaparece**, no se redirige:
  `hreflang` declara que dos URL son la misma página traducida, y apuntarlo a la
  portada le cuenta a Google algo falso, que es peor que callarse.
- El roto 215 era otro: un documento del programa citaba a otro por su nombre
  `.md`, correcto al leerlo en el repositorio y roto en la web.
  `_enlaces_entre_documentos` lo reescribe a `.html`, con el prefijo `ref-` si
  viene de `referencias/`.
- Cuatro pruebas: ninguna página con un enlace roto, el conmutador de una
  lección va a la portada, una página sin traducir no declara `hreflang`, y las
  que SÍ están en tres idiomas conservan los suyos —el arreglo no podía
  llevárselos por delante—.

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
- **`docs/audio/` está en `.gitignore` por ahora.** Cuando el audio esté hecho
  de verdad hay que quitar esa línea para que se publique. Se probó el
  reproductor con tonos generados con ffmpeg —no hay TTS ni clave en este
  contenedor— y **esos tonos se borraron antes de subir nada**: publicar un
  pitido donde el lector espera una voz es peor que no tener audio.

**Lo que falta**: `OPENAI_API_KEY` y correr el guion. La voz elegida es `nova`
con instrucciones de hablar despacio y en español de España; cambiarla es
cambiar `VOZ` y vuelve a costar 1,30 USD, porque es otro hash.

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
- Para AdSense **solo falta el dominio propio** (y el CMP de Google al
  encender los anuncios). El correo de contacto ya está puesto y el resto de
  la lista la da por buena `scripts/revisar_adsense.py`.
- Pendiente: lecciones 101-365, generar el audio (el camino ya está:
  `scripts/generar_audio.py`, 1,30 USD y una clave de OpenAI), más libros de
  referencia, y lo de «Pendiente de revision del profesor» de arriba.
