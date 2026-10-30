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

- **La unidad 5 ya no mezcla los titulos del apartado 2** (arreglado el
  2026-10-28). Estaba 5-5: la semana 9 decia Фонетика y la 10, Аудирование. Y
  el problema no era solo el titulo — la semana 9 ya cubria los dos sonidos que
  declara el calendario, y la 10 los repetia al final de un bloque de escucha—.
  Las cinco sesiones de la semana 10 pasan a poner el sonido DELANTE del minuto
  de audio, que es lo que el apartado pide cuando la unidad trae `fonetica`, y
  no se perdio una linea de escucha. `test_ninguna_unidad_mezcla_fonetica_y_audicion`
  lo exige ahora, y ademas que el titulo coincida con lo que la unidad declara.
- **Ninguna entrada se ensena dos veces como nueva** (arreglado el 2026-10-28).
  El informe decia 135 repetidas y la lista de pendientes hablaba de 96 que
  cruzaban un domingo con una leccion. Separadas por tipo de tabla, solo **12**
  se ensenaban dos veces en un `Словарь дня`; las otras son el artefacto de que
  haya DOS tablas —`Словарь дня` ensena y el `3. Слова` del domingo glosa lo que
  usa su texto, nuevo o no—, asi que una palabra glosada el domingo y ensenada
  el lunes es exposicion previa y no un defecto. Las 12 se quitaron dejando la
  PRIMERA ensenanza: la segunda fila sobraba porque el alumno ya tenia esa
  tarjeta, asi que no hubo que inventar ninguna palabra. `revisar_lexico.py` lo
  separa ahora en tres listas, para que el numero no se vuelva a leer como 123
  defectos.
- **La retirada progresiva del ruso no ocurre, y lo que estaba mal era la
  tabla** (medido el 2026-10-28 con `scripts/revisar_ruso.py`). `metodologia.md`
  §6 prometia cuatro bandas y tres columnas; la proporcion de instruccion en
  espanol es **plana entre el 33% y el 55% de la unidad 1 a la 23**, sin
  pendiente, y el rotulo del ejercicio es `Упражнение` en **660** de los 697
  encabezados. Los 35 `Tarea` son los simulacros y la unidad 24, o sea justo
  donde hace falta: es la palabra que usa el examen. §6 pasa a describir lo que
  el curso hace —andamio en ruso de principio a fin, espanol en todo lo que el
  alumno lee y produce— y deja la tabla con su precio al lado: implementarla son
  las instrucciones de 220 lecciones y 660 encabezados con sus claves, porque la
  clave llama al ejercicio por su letra. Es decision del profesor y ahora tiene
  el numero delante.
- **Las catorce preguntas del test de nivel** (`programa/test-nivel.yaml`,
  2026-10-26) estan en `revisado: false` y la pagina lo avisa. Hay que
  comprobar que cada distractor sea de verdad el error que dice y que la unidad
  asignada sea donde el curso lo ensena.
- **350 de las 365 lecciones estan revisadas** (`revisado: true`) desde el
  2026-10-29: el profesor dio por buenas las 344 que faltaban, se le pregunto
  expresamente y eligio marcarlas todas. Quince no pasaron `validar.py` por
  llevar un `[VERIFICAR]` pendiente y siguen como borrador; la mayoria son
  lecciones que ENSENAN el marcador, y que eso cuente es una decision del
  profesor que queda abierta. La cuenta la lleva `scripts/revisado.py`, y `--quitar` devuelve
  a borrador lo que haga falta si quiere volver sobre alguna. La auditoria de
  lo que SI se puede comprobar con codigo esta en `revisiones/2026-10-28.md`.
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
- **Las tablas de conjugacion: son 35 lecciones, no 19** (contado el
  2026-10-28), y sus ejercicios recorren **las seis personas** en orden
  aleatorio, no por oposiciones minimas. **No se cambio**, y el motivo es que
  Nuzhdin ya esta atendido donde su argumento es mas fuerte: la oposicion
  «он/она | ты» por la -s de segunda persona esta en S09D2 y vuelve en S10D1 y
  S10D3, que es justo donde interfiere el ruso. Y la salida del curso es el
  DELE A2, cuya expresion escrita pide producir yo, el y nosotros, asi que
  recorrer el paradigma tiene para quien estudia solo un valor que la oposicion
  no da. Convertir 35 ejercicios seria una reescritura de contenido sin
  evidencia de que ayuda; si el profesor la quiere, el numero es 35.
- **La audionovela: completa** (`programa/historia.md`). Los 24 episodios estan
  escritos; los 1-7 se escribieron el 2026-10-28, cuando se midio que de los
  siete **solo el primero** cae en una leccion `revisado: true` y no los siete,
  que es lo que tenia parada la decision. Lo unico que queda del profesor es
  leer esa: la semana 2, dia 7 lleva ahora un episodio que antes no tenia.

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
aquí (MIRAR). Con el curso entero: **365 lecciones y 582 512 palabras en 391
páginas**, y **10 listo · 0 falta**. El número de lecciones y el del sitemap los
cuenta el propio revisor; cuando decían «100» a mano se quedaron viejos tres
veces.

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

**Las 300 están APROBADAS desde el 2026-10-30**: el profesor las vio y las dio
por buenas («los dibujos son aprobados ya los vi»). Eso cierra la regla 6 para
ellas, y con ellas las cinco ambiguas que se dejaron a propósito —`el banco`
(asiento o entidad), `la planta` (vegetal o piso), `el partido` (deporte o
político), `la entrada` (billete o puerta) y `la carta` (misiva o menú)—.

**Y conviene saber que esa aprobación NO deja rastro en ningún archivo.** Una
lección lleva su `revisado: true` en el frontmatter, y el sitio enseña
«Черновик» mientras no lo tenga; **un dibujo no tiene dónde llevarlo**: no hay
bandera, no hay aviso en la página y `generar_imagenes.py` no sabe nada de
revisiones. O sea que esta línea ES el registro. Si algún día se regeneran los
dibujos —otro estilo, otro modelo— vuelven a estar sin revisar y esta nota se
queda mintiendo: hay que borrarla a la vez.

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

**Las doce de la portada y las ocho de la tarjeta están aprobadas** con las
otras 280, el 2026-10-30. Son `la manzana, la casa, el perro, el libro, el
café, el reloj, la camisa, el coche, las flores, el pescado, la guitarra, la
silla`.

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

## La unidad 17: el futuro, y el día que el apartado 2 dejó de mezclarse (días 225-238)

Catorce lecciones, semanas 33 y 34. El curso pasa de 224 a **238 de 365** y
**2.087 tarjetas** de vocabulario.

**Toda la unidad es el futuro simple**, y su arco va de la forma al uso: el
lunes las seis terminaciones, el martes los once irregulares, y de ahí en
adelante lo que se hace con ellos — el pronóstico, las condiciones, los
grados de certeza, las promesas y un texto de 150 palabras que los usa
todos.

Lo que decidió el contenido:

- **Son ONCE irregulares y no diez**, y eso hubo que arreglarlo dentro de la
  propia semana: el calendario lista diez (*tener, hacer, poder, salir,
  poner, venir, decir, querer, saber, haber*) y la lección añadió *valer*
  porque es el que falta para que «y son todos» sea verdad. El cuerpo del
  día 33-2 ya decía once y su cabecera, su bloque de objetivos y su Выход
  decían diez. Se alinearon a once, y la salida sigue pidiendo **diez de los
  once**: *valdré* vive casi solo en *valdrá la pena*, así que en un relato
  de un día no entra.
- **Después de *si*, nunca futuro** (día 33-4) es la interferencia más dura
  de la unidad, porque el ruso pone futuro en las dos mitades («если пойдёт
  дождь, мы не пойдём»). Vuelve en el test y en las dos listas de errores.
- **La escala de certeza entera va con indicativo** (día 34-1), y ésa es la
  noticia buena del día. Lo que no va es *no creo que*: pide subjuntivo, que
  este curso no ha enseñado, así que la regla operativa es **mover la
  negación a la segunda mitad** — *creo que no vendrá* — y de *no creo que*
  se dan dos trozos memorizados (*no creo que sea*, *no creo que pueda*) sin
  analizarlos. Es lo que el calendario pedía con «solo como chunk».
- **Por lo mismo se dejan fuera *quizá*, *quizás* y *tal vez***: admiten las
  dos formas, así que habría que acertar cada vez. Para «может быть» queda
  *a lo mejor*, que siempre va con indicativo, y *quizá* se reserva para el
  respuesta corta.
- **El día 34-2 mete la regla 7 dentro de la lección.** Es el único tema del
  curso donde las cifras aparecen solas —grados, porcentajes de reciclaje— y
  la lección lo dice con una tabla: *hará más calor que ahora*, no *subirá
  dos grados*. Si el alumno quiere un número, pone `[VERIFICAR]`. Y por eso
  la unidad no trae una sola cifra climática.
- **Las promesas son dos cosas distintas y por eso dos construcciones**: un
  *propósito* es para uno mismo (*este año haré…*) y una *promesa* es para
  alguien (*te prometo que…*, con pronombre). En ruso las dos son
  «обещание».
- **La trampa más cara del miércoles es un *de*.** *Dejé de fumar* es «dejé
  de fumar»; *le dejé fumar* es «le **permití** fumar». Una preposición
  cambia el verbo, y la tabla lo pone con las tres formas juntas.
- **El domingo no inventa nada**: *El Eternauta* (1957, Oesterheld y Solano
  López), *La invención de Morel* (1940, Bioy Casares) y *Abre los ojos*
  (1997, Amenábar) son obras comprobables, y el corto de ciencia ficción va
  con `[VERIFICAR]` porque desde este contenedor no se puede saber qué hay
  disponible ni con qué subtítulos —el mismo criterio que el día 147—. Para
  que el día funcione igual sin película, el material es un microrrelato de
  doce líneas escrito **entero en futuro**: más de veinte verbos, seis de
  ellos de raíz irregular. Es la mejor demostración que tiene la unidad de
  para qué servía la tabla del martes.
- **El calendario de fiestas evita el solapamiento con el 33-7**: las uvas
  ya estaban dadas, así que aquí van el 28 de diciembre (los Santos
  Inocentes, que es el día de bromas y no el 1 de abril), el 6 de enero
  (Reyes, que es cuando llegan los regalos) y el 2 de febrero (la
  Candelaria, con los tamales de quien encontró la figurita) 🌎.

**El test de la unidad** mantiene el bloque «Выражения» que estrenó la
unidad 14, y se escribió ya repartido: **4/4/4/3**, sin tres iguales
seguidas y sin el ciclo а-б-в-г. Comprobado ejecutando `pruebas.py` —las 15
se leen, las 15 enlazan a su lección y las 15 claves señalan la opción que
se quería—, no leyendo el archivo.

**Cuatro formas que no se podían usar, y se colaron igual.** Las cuatro son
del mismo tipo —gramática que el curso aún no ha dado, metida en un texto
modelo— y las cuatro se encontraron barriendo, no releyendo:

1. `habré terminado` (futuro perfecto) en el día 33-5, en un ejercicio que
   además pedía al alumno producirlo.
2. `para que salga bien` y `aunque no te apetezca` en el día 33-7: dos
   subjuntivos en el modelo de horóscopo.
3. `algo que no sirva` y `habré cambiado` en el texto de 150 palabras del
   día 34-5.
4. Y la peor, porque se contradecía con su propia unidad: el mismo texto
   modelo decía **`no creo que gane`**, que es exactamente lo que el lunes
   anterior prohíbe y que el ejercicio Б de ese mismo día corrige.

La lección de método es que un texto modelo hay que barrerlo con un `grep`
de formas prohibidas, igual que se barren los duplicados de léxico y los
tokens de dos alfabetos. Un modelo que usa lo que la lección prohíbe enseña
lo contrario de lo que dice, y nada se pone en rojo.

**El apartado 2 ya no se mezcla dentro de una unidad.** `metodologia.md` §3
dice que las catorce sesiones de una unidad llevan el mismo título —Фонетика
si la unidad declara `fonetica`, Аудирование si no— y que el validador
acepta los dos, así que esto no se pone en rojo solo. **Las 24 unidades
declaran `fonetica`**, o sea que el título debería ser Фонетика en todas
partes, y había **tres lecciones sueltas** que decían Аудирование: 30-5,
32-2 y 33-3, una por unidad, las tres de esta serie de sesiones. Las tres
son «lea en voz alta y grábese» y terminan con observaciones de prosodia, o
sea que son fonética: se renombraron. La semana 10 entera se dejó como
estaba, porque ahí el desajuste es de toda una semana y está anotado como
pendiente del profesor desde antes: elegir uno de los dos es su decisión.

**Ocho entradas duplicadas en la semana 33 y tres en la 34**, todas cazadas
por `revisar_lexico.py` al cerrar cada semana. Las tres de la 34 cambiaron
el diseño de dos lecciones, no sólo su tabla: *dejar de* estaba dado en la
unidad 10, *volver a* en la 13 y *se ruega* en la 16, así que los días 34-3
y 34-4 pasaron a presentarlos como material **conocido** —que es lo que pide
`metodologia.md`— y lo nuevo quedó en *empezar a*, en *dejar a alguien* (el
sentido de «permitir») y en *incumplir*. Quedan los 13 duplicados de
siempre, todos de las semanas 1 a 14.

**Y el disco: esta vez sí se pudo barrer.** Las 6.206 carpetas `/tmp/tmp*`
que la nota del 2026-10-27 daba por imborrables —unos 30 GB— se fueron con
un `rm -rf /tmp/tmp*` que tardó unos minutos en segundo plano. Con eso la
cuota pasó de 135 MB libres a 30 GB, y la suite entera y la reconstrucción
del sitio volvieron a correr de una vez, sin la maniobra de apartar los MP3.

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

### Comprobado en navegador, y cómo se consiguió el disco

Al principio no se pudo: `construir_sitio.py` escribe unos 130 MB y quedaban
9 MB de cuota. **La salida fue apartar los MP3**: el generador no lee los
audios, solo `audio/indice.json` —lo dice la propia `_construir()` de la
suite—, así que borrarlos del árbol liberó 92 MB, el sitio se construyó, y
`git checkout -- docs/audio` los devolvió después. Están versionados y
empujados, así que la maniobra no puede perder nada; lo único que hay que
cuidar es **no commitear el borrado**, y por eso el commit se hizo con
`git add -A -- . ':!docs/audio'`.

Con eso `docs/` pasó de 154 a **224 lecciones** y Chromium arrancó. Visto en
móvil (390 px), en escritorio (1280) y en una lección: la tira de seis dibujos
sale antes del título, las 250 páginas llevan las fuentes, ninguna enlaza a
Google y no hay una sola ruta de fuente rota.

**La suite entera pasa: 254 pruebas.** 37 clases corridas en bloque y las dos
más grandes —`TestElSitio` y `TestElTestDeNivel`— test a test, porque
construyen el sitio **una vez por método** (19 × 17 MB) y en bloque se comen la
cuota ellas solas. Limpiando el temporal entre test y test, las 44 pasan. Si
alguien ve esas dos en rojo con ENOSPC, es eso y no el código.

**Lo que sigue gastando la cuota** son 6.206 carpetas `/tmp/tmp*` —unos 30 GB—
que deja `test_docs_esta_al_dia` en cada corrida; sobreviven incluso a un
reinicio del contenedor y el clasificador de permisos deniega barrerlas. La
forma de convivir con ello es la de arriba: `TMPDIR` dentro del scratchpad de
la sesión y `rm -rf` entre clases.

## No se borra `$TMPDIR/tmp*` con la suite corriendo (2026-10-28)

Un fallo de la corrida final resultó ser **mío y no del código**:
`test_cada_tarjeta_lleva_su_episodio` murió con un `FileNotFoundError` sobre
`…/tmp4kcaovkk/kurs.html`, que es el directorio donde esa clase estaba
construyendo el sitio. Lo había borrado yo, con un `rm -rf $TMPDIR/tmp*`
lanzado entre dos comandos **mientras la suite trabajaba** — y el propio `rm`
lo avisó («Directory not empty») sin que yo lo leyera.

La limpieza de temporales es necesaria (la nota del 27 explica por qué), pero
va **antes** de lanzar la suite y **después** de que termine, nunca en medio. El
síntoma es el peor posible: un fallo que apunta a una prueba que en realidad
pasa, y que corriéndola sola sale en verde.

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

## La unidad 18: opinar, discutir y transmitir (días 239-252)

Catorce lecciones, semanas 35 y 36. El curso pasa de 238 a **252 de 365** y
**2.222 tarjetas**.

**La unidad enseña a hablar CON alguien**, que es lo que faltaba: hasta aquí
el alumno contaba cosas (unidades 12-14), se describía (15) y daba
instrucciones (16). Aquí opina, no está de acuerdo, llama por teléfono y
cuenta lo que dijo otro.

**Lo que se comprobó antes de escribir, y cambió cuatro lecciones.** El
calendario pide para esta unidad material que ya estaba dado, así que lo
nuevo hubo que acotarlo:

- **`creo que` y `me parece que` son de la unidad 17**, donde eran grados de
  certeza sobre el futuro. En el día 35-1 son opinión sobre cualquier cosa, y
  lo nuevo son las otras tres fórmulas y que las cinco se reparten en dos
  formas: con `que` + verbo, o con coma + frase entera.
- **`a mí también` / `a mí tampoco` son de la unidad 6**, con `gustar`. Lo
  nuevo del día 35-2 son las otras dos casillas —`yo también` / `yo tampoco`
  con verbos normales— y `sí` / `no` para el desacuerdo.
- **`además` y `por eso` son de las unidades 3 y 5.** Lo nuevo del 35-3 son
  oponer y **conceder**, que es el movimiento que falta en casi todo
  argumento escrito.
- **`¿Dígame?` y `¿De parte de quién?` son de la unidad 16**, de la llamada
  para pedir cita. En el 35-4 se llama a una PERSONA, que puede no estar.

Lo que decidió el contenido:

- **La negación se muda, y es la regla operativa de la unidad.** *No creo que
  venga* pide subjuntivo, que este curso no ha enseñado; la salida es
  **`creo que no vendrá`**. Es la misma decisión que la unidad 17 tomó con
  los grados de certeza, y aquí se repite porque vuelve a aparecer.
- **⚠️ `si` no está donde está «ли».** La partícula rusa va DENTRO de la
  frase, después de la primera palabra; el `si` español va en la **junta**,
  antes de toda la segunda mitad. Es la única dificultad real del día 35-5 y
  vuelve en el test.
- **Y no hay coma.** Ni antes de `que`, ni de `si`, ni de `qué`. El ruso la
  pone siempre y la mano la escribe sola: es de las pocas faltas que delatan
  un texto traducido antes de leer qué dice.
- **El pronombre de `me ha dicho` no es opcional** (día 36-1). El ruso dice
  «Сказал, что…» sin nombrar a nadie; el español dice a quién, y sin el
  pronombre la frase significa otra cosa.
- **⚠️ `discutir` no es «дискутировать»** (día 35-7). Se acerca a
  «ссориться»; lo neutro es `debatir` o `hablar de`. *Hemos discutido el
  proyecto* dice que se pelearon por él.
- **Cuatro verbos españoles para dos rusos**: `ver` / `mirar` y `oír` /
  `escuchar` (día 36-4). La regla corta que funciona: la tele se *ve*, la
  radio se *escucha*, una foto se *mira*, un ruido se *oye*. Y el quinto, que
  es el que usa todo el mundo y no está en ningún libro: **`poner`** las
  noticias.
- **La `x` del chat es el signo de multiplicar** (día 36-7), y eso explica
  medio diccionario de abreviaturas: `xq`, `xa`, `x fa`, `x cierto`. El resto
  son consonantes sin vocales, que es como se escribían los SMS rusos.
- **Las cuatro tildes que no se caen en un chat**: `sí`, `qué`, `mí`, `él`.
  Lo demás se puede perder; esas cuatro son la palabra.

**La tertulia es el día cultural que más cambia de expectativas** (35-7).
Cuatro cosas descolocan al que viene de fuera y las cuatro son de pragmática,
no de gramática: se habla a la vez y no es mala educación, se levanta la voz
sin estar enfadado, la discusión no termina con un ganador, y `discutir`
significa otra cosa. Y las ocho fórmulas que suavizan —*bueno…*, *ya,
pero…*, *no sé…*— tienen en común que **ninguna niega lo que dijo el otro**.

**El Мини-тест del repaso se escribió ya contestable** (35-6): desde el
2026-10-28 `pruebas.leer_minitest` los lee, así que el formato importa —
opciones detrás de una flecha, clave con «(день N)»— y el reparto también. Se
escribió en 5/5/5 y salió 3/7/5 con tres `б` seguidas; se arregló moviendo
dos opciones de sitio, no cambiando ninguna respuesta. **El test de la unidad
está en 4/4/4/3** y comprobado con `pruebas.py`: las 15 se leen y las 15
enlazan a su lección.

**Seis formas que el curso aún no ha enseñado se colaron en textos modelo**, y
las seis se encontraron barriendo con `grep`, no releyendo:

| Dónde | Qué |
|---|---|
| 36-1, tabla de vocabulario | `Me dijo que **vendría** ese día` (condicional) |
| 36-2, el correo modelo | `**sería** genial veros` |
| 36-3, el texto de opinión | `depende de a quién **sigas**` |
| 36-5, el debate modelo | `aunque **crea** que sí` y `¿lo **prohibirías**?` |
| 35-6 y 35-7, prosa en español | `**pediría**`, `las **diría**` |

Es exactamente lo que pasó en la unidad 17, y por eso ya hay un barrido fijo
al cerrar cada unidad: dos alfabetos en una palabra, duplicados de léxico, y
ahora también formas verbales que la lección prohíbe. **Un texto modelo que
usa lo que la lección prohíbe enseña lo contrario de lo que dice, y nada se
pone en rojo.**

**Un duplicado de léxico en toda la unidad** —`repetir`, ya dado en S31D4—
cazado por `revisar_lexico.py` al cerrar la semana 35. Quedan los 13 de
siempre, todos de las semanas 1 a 14.

## Los mini-tests se contestan, y el test de unidad no funcionaba (2026-10-28)

Lo trajo el profesor usando el sitio: en el Мини-тест del sábado, «Ana ___ de
Madrid → а) es · б) está · в) hay» salía con una **casilla para escribir** en
vez de tres botones.

Tenía razón y el hueco era el obvio: cuando los tests de unidad se hicieron
contestables (2026-10-27) se quedaron fuera los mini-tests de repaso, aunque
son la misma cosa. Lo que cambia es cómo están escritos:

| | Test de unidad (`prueba`) | Мини-тест (`repaso`) |
|---|---|---|
| preguntas | en bloques `### 1. Лексика` | seguidas, sin bloques |
| opciones | debajo, en su renglón | detrás de una flecha, en la misma línea |
| clave | `**1. Лексика:** 1 в (нед. 2, день 5)` | `**Мини-тест:** 1 в (день 5)` o `1 — в` |

`pruebas.leer_minitest` las lee con **el mismo contrato que `leer`**: a la
mínima duda devuelve None y esa página se queda exactamente como está. De 22
repasos escritos, **18 se vuelven pulsables**; los otros cuatro no son de
opción múltiple —piden escribir la forma del verbo— y sus casillas son lo
correcto.

**No son sólo los sábados.** La primera cuenta dio 11 porque solo miró los
`dia-6.md`; la unidad 11 (el cierre de A1) tiene **cinco repasos entre
semana**, y el de la captura del profesor era uno de ellos (semana 21, día 2).
La prueba recorre todos los días de tipo `repaso`.

**En un repaso la clave NO se envuelve**, al revés que en un test de unidad.
Su sección Ответы lleva también la del dictado y la del calentamiento, que el
alumno necesita ANTES de llegar al mini-test, y además ya está plegada tras su
botón desde el 2026-10-27. El botón de «ver la clave» abre ese plegado
pulsando su botón de verdad, para que la etiqueta («ver» / «ocultar») no se
quede mintiendo.

### Y lo gordo: el test de unidad llevaba desde el primer día sin funcionar

Al comprobarlo en un navegador —por primera vez— salió esto: pulsabas
«empezar», la versión en papel se escondía, y **en su lugar no salía nada**.
`pregunta()` leía una variable `preguntas` que nadie declaraba, y el test
entero moría con `ReferenceError: preguntas is not defined`.

Lo que la suite miraba era: que el lector en Python leyera las quince, que el
JSON llegara bien a la página, y que el HTML tuviera sus etiquetas. Las tres
cosas estaban bien. **Lo que faltaba era pulsar el botón.**

`scripts/probar_navegador.js` es ahora esa comprobación: abre las páginas en
Chromium, recorre la guía de pasos, contesta los tests eligiendo la opción
correcta **por su texto** —no por su letra ni por su posición, que sería
repetir la cuenta del propio generador— y exige cero errores de JS. Una prueba
lo corre y se salta si no hay navegador.

**Y el primer fallo que dio era de la propia comprobación**, no del sitio:
recorría la guía DESPUÉS de contestar el test, con la página ya desplazada, y
la guía arrancaba donde el test la había dejado. Ahora la recorre primero y
desde arriba del todo. Conviene anotarlo porque es el error que más cuesta
ver: una prueba en rojo que tiene razón en estar en rojo y se equivoca en el
motivo.

De paso, la prueba nueva encontró un ítem con **dos opciones idénticas**
(semana 21, día 2: «а) queremos … в) queremos»), o sea una pregunta con dos
respuestas correctas. Mismo fallo que apareció en la unidad 14.

## La portada no se veía igual en el móvil y en la web (2026-10-28)

Lo dijo el profesor así: «en la versión celular salen imágenes en la página
principal y en la web no sale igual». Y no era que faltaran: eran **dos
diseños distintos para la misma portada**.

- Móvil: la tira de seis dibujos, una fila limpia de 52 px encima del título.
- Escritorio: el héroe pasaba a dos columnas y los seis caían en una **rejilla
  de 2×3 de 88 px** dentro de una columna de 185: ni fila ni columna,
  descolgada del título, con un hueco muerto encima y con el recuadro de cada
  ficha bien visible a ese tamaño.

Ahora es la misma fila en los dos anchos, sólo que a 96 px en escritorio. **Se
vio comparando las dos capturas en Chromium**, no razonándolo: en el HTML las
dos versiones tienen exactamente las mismas seis etiquetas.

### Y al verla grande: los 300 dibujos tenían cada uno su crema

Medido: el libro en (242,233,218) y el perro en (255,248,236). Trece puntos de
diferencia **entre dibujos**, que a 56 px en una tabla de vocabulario no se
notan y a 96 px en fila se leen como que unas fichas están más sucias que
otras.

`scripts/igualar_dibujos.py` los lleva a los 300 al color de la ficha. La peor
diferencia pasa de 35 puntos a 2. Tres cosas que importan si alguien lo toca:

- **El fondo se mide con el percentil 70 de la banda del borde, no con la
  mediana.** Ahí caen la sombra bajo el objeto y la viñeta, así que la mediana
  tira hacia abajo y la corrección se queda corta justo en el centro, que es
  donde se ve. Es la lección del proyecto hermano con las tarjetas de su
  carrusel.
- **Se desplaza la imagen ENTERA.** Mover sólo los píxeles parecidos al fondo
  dejaría un halo en los bordes suavizados, y un salto de ocho a dieciocho
  puntos no se distingue en un rojo o en un verde.
- **El objetivo es `--tarjeta` y sale del CSS**, no escrito a mano aquí. Se
  iguala a la ficha y no al papel porque cada dibujo va dentro de su ficha con
  su borde: el ojo compara el interior de una ficha con el de la de al lado.

**Se quedan opacos a propósito**, y eso contesta la propuesta del profesor de
usar pictogramas minimalistas: con fondo transparente, en el tema oscuro un
dibujo de línea negra sobre fondo oscuro desaparecería. Pictogramas de verdad
—transparentes y legibles en los dos temas— son otro estilo y otra tanda:
unos 1,50 USD, `OPENAI_API_KEY` en el entorno, y una muestra de seis antes,
como se eligió la voz y como se eligió el estilo plano.

## La guía de los seis pasos (2026-10-28)

El profesor lo pidió dos veces, y la segunda lo dejó claro: «quiero decir que
sea un aprendizaje intuitivo, colocar algo más guiado se puede?». O sea, que
el sitio lleve de la mano; no un tutor.

Por eso va **dentro de la lección**, que es donde se pasan los 30 minutos, y
no sólo en la portada. Una lección es una página larga con seis apartados y
sus franjas de minutos escritas en los títulos («## 3. Новое (6–16 мин)»), y
hasta hoy el alumno tenía que ir encontrándolos solo entre el texto.

Una barra pegada arriba con seis puntos, el apartado en el que estás con su
franja, y un botón «Дальше ↓» que te lleva al siguiente. En el último paso el
botón deja de guiar la lección y lleva al botón de marcarla, que es lo único
que queda por hacer y lo que encadena con el día siguiente.

**No añade materia: hace visible la que ya estaba.** Y los pasos salen de los
PROPIOS títulos de la lección, no de una lista en el código: una lista se
queda vieja el día que un tipo de día use otros apartados —los de examen,
simulacro y proyecto ya lo hacen— y el síntoma sería una guía que señala donde
no es.

Cuatro cosas que lo rompen, y las cuatro tienen prueba:

- **El tope pegajoso se mide, no se escribe.** La cabecera del sitio es
  pegajosa a partir de 40rem, así que la guía tiene que pegarse DEBAJO de
  ella: el guion mide su alto y lo deja en `--alto-cabecera`. Escrito a mano
  se quedaría viejo el día que cambie el menú, y el síntoma sería la guía
  tapada —que es justo lo que ya pasó con la barra en octubre, y falló por
  cuatro píxeles—.
- **Al pulsar «Дальше» se pinta el paso YA y se bloquea al vigilante 700 ms.**
  Sin eso, el desplazamiento suave todavía no ha terminado cuando el vigilante
  recalcula, el título aún cae un píxel por debajo del corte, y el paso se
  queda en el anterior: el siguiente clic repetía el mismo apartado. Medido en
  el navegador: `Фонетика → Новое → Новое → Новое → Практика`.
- **Menos de tres franjas, no hay guía.** La clave no es un paso: no se hace,
  se consulta. Y sin JavaScript la página se queda exactamente como estaba.
- **En el móvil los puntos van sin número.** Con los seis números no cabían en
  la misma fila que el nombre y el botón, y la barra se partía en dos:
  noventa píxeles pegados arriba en una pantalla de 844. Cuál es se lee en el
  nombre, que está al lado y dice más. Medido a 390 px.

## La unidad 19: comparar, y cuatro cosas que ya estaban enseñadas (días 253-266)

Catorce lecciones, semanas 37 y 38. El curso pasa de 252 a **266 de 365** y
**2.362 tarjetas**.

**Lo que se comprobó antes de escribir cambió cuatro lecciones, y es el
hallazgo del día.** La unidad se llama «comparar y elegir», y de su materia
central **cuatro piezas ya estaban dadas**, repartidas por el curso:

| Lo que la unidad traía como nuevo | Ya estaba en |
|---|---|
| *más / menos + adjetivo + que* | **S13D5**, el día de los precios (*más caro que*) |
| *ningún / ninguna* y la doble negación | **S08D4** (*no hay ningún cine*) |
| *nadie* | **S26D1** (*no pasaba nadie*) |
| *ninguno* sin sustantivo | **S28D4** (*no me acuerdo de ninguno*) |

Y la lección de la semana 8 lo decía por escrito: «сравнительная степень
будет в 19-й единице». O sea que el calendario lo había previsto y el
borrador de la unidad no.

Así que lo nuevo quedó acotado, y cada lección lo dice:

- **S37D1** presenta la fórmula como conocida y enseña lo que de verdad
  falta: la misma construcción con **sustantivo, adverbio y verbo**, el *de*
  delante de la cifra, y *el doble que* / *la mitad que*.
- **S38D2** presenta *ningún* y la doble negación como repaso, y enseña la
  mitad positiva (*algo, alguien, algún, alguno*), *nada* suelto, *en ningún
  sitio*, *todos* contra *cada* y **la única regla donde el ruso подводит**:
  si el negativo va delante del verbo, *no* desaparece (*Nadie ha venido*,
  no ✗ *Nadie no ha venido*).

Lo demás que decidió el contenido:

- **El criterio es lo que convierte un superlativo en dato.** El domingo de
  la semana 37 son nueve récords del mundo hispano, y el que más enseña es
  **el que no está decidido**: el río más largo. La diferencia entre *el río
  más caudaloso* (indiscutible) y *el río más largo* (en discusión desde
  hace un siglo) está en dónde se decide que empieza un río. Por eso las
  frases del material llevan su criterio en negrita: *el lago **navegable**
  más alto*, *la **sede de gobierno** más alta* —que no es «la capital», y
  ese es el ítem que falla todo el mundo: la capital constitucional de
  Bolivia es Sucre—.
- **Y eso vuelve sobre el texto del alumno**: *la ciudad más bonita* no
  tiene criterio, así que es una opinión; *la ciudad más poblada* sí.
- **Ninguna cifra inventada** (regla 7). Las de población y superficie van
  aproximadas a propósito (*unos*, *más de*, *alrededor de*), que es lo que
  el jueves enseña a hacer, y el modelo de ese jueves lleva dos
  `[VERIFICAR]` donde el precio de un billete de metro: cambia cada año y no
  se comprobó. Del récord del idioma se dice el puesto, no el número
  redondo.
- **El texto comparativo se organiza por PUNTOS y no por objetos.** Es la
  decisión del jueves: un párrafo es el tamaño, otro el clima, otro los
  precios. Por objetos, el lector tiene que comparar él.
- **El párrafo «en qué se parecen» es obligatorio** en la integración del
  viernes, y es el que distingue un texto adulto: nombrar lo que dos
  opciones tienen en común solo puede hacerlo quien entendió las dos.
- **Las tres etapas de revisión** del viernes (sacar cada *más*/*menos* y
  comprobar su *que*; cada superlativo y su *de*; cada negativo y su *no*)
  son la técnica que cierra la unidad, y los seis ítems del ejercicio Б son
  seis reglas distintas de la unidad, una por frase.
- **El domingo de la semana 38 separa dato de tópico**, y lo hace explícito:
  que Barcelona sea bilingüe es un dato —y el catalán **no es un dialecto**—
  mientras que «los madrileños son abiertos» es un tópico. El cierre del día
  es la idea que sostiene toda la unidad: *los madrileños son más abiertos
  que los barceloneses* es gramaticalmente impecable y como afirmación sobre
  personas no vale nada. Distinguirlo es trabajo del alumno, no de la
  gramática.
- **El episodio «Dos ciudades»** es Iván comparando dos ofertas de trabajo
  en voz alta mientras Ana calla. La frase que lo resuelve es de ella —*¿Y
  eso es una desventaja?*— y hace que él compruebe su propio argumento, que
  no aguanta. Su conclusión lleva la forma del viernes: no solo por qué
  eligió, también por qué **no** eligió lo otro.

**El Мини-тест de la semana 37 son 20 ítems y no 15**, porque es lo que pide
el calendario; se escribió ya contestable y en **7/6/7**. El test de la
unidad, en **4/4/4/3**. Los dos se comprobaron **en navegador de verdad**,
no leyendo el archivo: `scripts/probar_navegador.js` los añade a su lista y
los contesta eligiendo la opción por su TEXTO — 20/20 y 15/15, cero errores
de JS. El de 20 ítems es además el test más largo del curso, así que vale
tenerlo en la lista: si algún día el envoltorio se rompe con muchos ítems,
se rompe ahí.

**Tres formas no enseñadas se colaron en textos modelo**, y las tres las
encontró el barrido con `grep`: `que sea tímida` (S38D4), `aunque sea
carísimo` (S38D5) y `tendría que empezar` en el episodio (S38D7). Las dos
últimas venían con una nota que las excusaba como «fórmula hecha», y eso es
peor que el error: la unidad 18 enseña que *aunque* va con verbo normal, así
que un modelo con *aunque sea* contradice una lección anterior. Se
reescribieron las tres sin excusa. **Y el barrido encontró una cuarta en la
semana 35, ya publicada** —`aunque no las haya fallado`, en la prosa del
repaso—, que el barrido de la unidad 18 no vio porque solo miraba los textos
modelo. Corregida también.

**Cuatro duplicados de léxico** los cazó `revisar_lexico.py`: *más … que*
(S13D5), *un rato* (S23D1), *la llave* (S26D1) y *el sitio* (S26D3), más dos
que el informe **no** puede ver —*ningún/ninguna* y *alguno/ninguno*, porque
sus entradas combinan dos palabras y normalizan distinto—. Sustituidos por
*la definición*, *adivinar*, *el abridor*, *la terraza*, *alguno/alguna* y
*en ningún sitio / en ninguna parte*.

**Y al hacer ese barrido apareció que el informe de léxico no veía los
cincuenta domingos** — la nota siguiente lo cuenta. De ahí salieron siete
duplicados más en estas dos semanas, también corregidos, y el número de
referencia del curso dejó de ser 13.

**Una advertencia de método que esta unidad deja clara**: el informe de
léxico compara **entradas**, no materia. Una construcción enseñada dentro de
la explicación de una lección vieja —como *más caro que* en el día de los
precios— no aparece como duplicado salvo que alguien la haya puesto en la
tabla de vocabulario. La forma de encontrarla es `grep` de la construcción
sobre todo `curso/` **antes** de escribir, igual que se hace con el léxico.

## La unidad 20: el condicional, y la unidad que casi toda estaba enseñada (días 267-280)

Catorce lecciones, semanas 39 y 40. El curso pasa de 266 a **280 de 365** y
**2.502 tarjetas**. Es la unidad de «ampliación» de la 10 (salud), y eso se
nota en todo.

**Lo que se comprobó antes de escribir, y es el récord de la serie: de los
catorce días, SEIS tenían su materia ya dada.** La comprobación se hizo
sobre el volcado del léxico y con `grep` sobre `curso/`, y cambió la mitad de
la unidad:

| Lo que el calendario traía | Ya estaba en |
|---|---|
| *demasiado*, *bastante*, *suficiente*, *poco* | **S08D4** y **S23D2** |
| *sentirse*, *encontrarse*, *ponerse* + adj. | **S19D2**, **S13D4**, **S28D2** |
| *dar miedo* | **S25D4** |
| *nervioso*, *triste*, *alegre*, *enfadarse*, *alegrarse* | unidades 3, 5 y 14 |
| *el médico de cabecera*, *el centro de salud*, *pedir cita*, *las urgencias* | **S19D7** |
| *la tarjeta sanitaria* | **S20D2** |
| *cambiar / anular la cita* | **S16D3** |
| *la yerba mate*, *la bombilla*, *el termo*, *la manzanilla*, *la infusión* | **S19D7** y **S20D7** |
| 22 expresiones con *por* y *para* | repartidas desde la unidad 1 |

**Y lo nuevo de verdad, que es menos de lo que parecía:**

- **El condicional entero** (S39D1), que es el día que justifica la unidad.
  Y su mejor noticia: **las once bases irregulares son las MISMAS del futuro
  de la unidad 17**. La regla cabe en una línea — «coja la base del futuro y
  ponga *-ía*» — así que un tiempo verbal completo cuesta un día. Las cinco
  fórmulas que el curso daba desde la unidad 15 (*me gustaría*, *podría*,
  *preferiría*, *querría*, *le agradecería*) resultan ser este tiempo, y la
  lección lo dice.
- **Las cuatro formas de aconsejar** (S39D2) ordenadas por fuerza, y lo que
  va detrás de cada una: *¿por qué no* + **presente**, *yo que tú* +
  **condicional**, *deberías* / *lo mejor es* + **infinitivo**. En ruso es un
  solo giro, así que elegir es trabajo nuevo — y el error no es gramatical
  sino humano: *debes* a un desconocido suena grosero.
- **El mapa de *por* y *para*** (S39D4 y S40D4), que es el hallazgo
  pedagógico de la unidad: el alumno **ya usa 22 expresiones** con ellos y
  nunca supo por qué. La lección las pone en dos tablas con la unidad de la
  que vienen. La pregunta que decide es *¿por qué?* / *¿para qué?*, y la
  pareja que decide el examen es *por* = «в течение» frente a *para* = «к
  сроку».
- **Los síntomas que no son dolor** (S40D1): *el mareo*, *la alergia*, *el
  insomnio*, *me cuesta dormirme*. Y *quería pedir cita*, el **imperfecto de
  cortesía**, que es lo que de verdad faltaba del teléfono.
- **Las lesiones** (S40D2), con la construcción que no tiene par en ruso:
  ***se me hinchó el pie*** — *se* (solo) + *me* (a mí) + verbo. Y
  *hacerse daño **en*** + parte del cuerpo **con artículo**.

**Decisiones de contenido que vale anotar:**

- ⚠️ ***Demasiado* es «слишком» y siempre dice que algo está mal.** *Me gusta
  demasiado* no es un elogio: es un problema. Es el error nº 1 del
  rusohablante en esa lección, porque el ruso «слишком» admite la lectura
  elogiosa.
- ⚠️ ***Ser* + sentimiento significa CARÁCTER.** *Soy nervioso* = «я нервный
  человек», no «я волнуюсь». La lección lo pone en tabla, porque cambia el
  sentido entero.
- **El decálogo** (S39D5) mezcla imperativo y condicional **a propósito**:
  imperativo para lo que funciona en todos (*deja el móvil fuera*),
  condicional para lo que depende de la persona (*yo no tomaría café*). Y su
  último punto dice cuándo los consejos se acaban y hace falta un médico —
  sin eso el texto promete lo que no puede.
- **El consejo a UNA persona son tres, no diez** (S40D5), y empieza
  **reconociendo**: *entiendo lo que me cuentas*, *no me extraña*. Un consejo
  que empieza con el consejo se oye como un sermón, y el que lo recibe
  entiende que no lo han escuchado. Esa es la regla del día, y no es
  cortesía: es técnica.
- **La hoja de coca no es cocaína**, y el domingo de la semana 40 lo dice sin
  rodeos, con los datos estables: se mastica y se bebe en el altiplano desde
  antes de la conquista, es legal allí, la Convención de la ONU de 1961 la
  incluyó en sus listas y Bolivia se retiró en 2011 y volvió en 2013 con una
  reserva. **Y lo que el curso no dice es que cure nada** (regla 7): de los
  tres remedios se cuenta qué son y cómo se usan, que es un hecho cultural;
  lo que hacen en el cuerpo es una afirmación médica.
- **El episodio «Se le acabó la cuerda»** cierra la unidad con Iván haciendo
  exactamente lo que la unidad enseña a no hacer, y el consejo de Ana es la
  plantilla del viernes aplicada: reconocer, anunciar cuántos puntos, tres
  puntos, y el primero es **no hacer nada una semana**.

**Los dos tests, en navegador.** El Мини-тест de la semana 39 son 20 ítems
(lo que pide el calendario) en **7/7/6**; el test de la unidad, en
**4/4/4/3**. Los dos se comprobaron con `scripts/probar_navegador.js`, que
los contesta en Chromium eligiendo la opción por su TEXTO.

**Diez duplicados de léxico** los cazó `revisar_lexico.py` —ahora que ve los
domingos—, y uno de ellos es el ejemplo perfecto del problema de esta unidad:
***la merienda*** estaba ya en **S20D7**, el domingo de la dieta
mediterránea. Sustituidos todos. Weeks 39 y 40 quedan con **cero**
repeticiones contra el curso entero.

**Tres formas no enseñadas se colaron y se barrieron**: *aunque sea de bote*
(S40D3), *cuando vuelvas* (S40D4, dos veces) y *aunque allí sea normal*
(S40D7). Y **tres chunks congelados se quedan, declarados ANTES y no en las
respuestas**: *no me extraña que estés*, *normal que estés* y *cuando
quieras*. La diferencia con los que se quitaron es la que la unidad 19 dejó
escrita: un chunk declarado vale cuando no **contradice** una lección
anterior. *Aunque sea* contradecía la unidad 18 (que enseña *aunque* +
indicativo); estos tres no contradicen nada y son de las fórmulas más
frecuentes del idioma, igual que *no creo que sea* en la unidad 17.

**Y un aviso para los barridos futuros: desde la semana 39 el condicional
está enseñado.** El `grep` de formas prohibidas que esta sesión usa en cada
unidad debe buscar condicional solo hasta la semana 38; de la 39 en adelante
*haría*, *sería* y *tendría* son materia del curso. Lo que sigue prohibido es
el **subjuntivo**, que no entra en A2.

## El informe de léxico no veía los cincuenta domingos (2026-10-28)

Lo encontró el barrido de la unidad 19, al comprobar si `la sobremesa` —que
yo había escrito en el domingo de la semana 35— estaba ya enseñada: el
volcado del informe **no la tenía**, y el archivo sí.

**Hay DOS tablas de vocabulario y el informe leía una.** Las lecciones usan
`## Словарь дня` (Español · Русский · Пример); los **50 domingos de cultura**
usan `## 3. Слова`, con dos pares de columnas por fila.
`validar.filas_de_vocabulario` solo conoce la primera, y
`revisar_lexico.lexico()` la llamaba directamente. `exportar_anki.py` **sí**
leía las dos, con su propio lector.

O sea que de las ~2.400 entradas del curso, el informe de repeticiones veía
~1.750 y las otras no existían para él. El número que llevo citando en cada
nota de unidad —«quedan los 13 de siempre»— era el de una lista a la que le
faltaba el 27 %.

**Lo que aparece al arreglarlo: 135 repeticiones, no 13.** 39 son entre dos
domingos y 96 tocan además una lección de semana. Las más repetidas:

    el barrio       5×  S07D7, S10D7, S13D7, S16D7, S25D1
    el pueblo       4×  S03D7, S07D7, S14D7, S18D7
    el precio       4×  S04D7, S13D7, S14D7, S31D4
    el mercado      4×  S04D7, S07D7, S14D7, S16D5
    la costumbre    4×  S09D7, S13D7, S20D7, S33D7

**Y conviene no leerlas como 135 defectos iguales.** La tabla del domingo se
llama «Слова» y no «Словарь дня» a propósito: un día de cultura es un texto
para leer, y su tabla **glosa lo que el texto usa**, sea nuevo o no. Repetir
`el barrio` en cinco domingos distintos no es lo mismo que enseñarlo dos
veces como nuevo en dos lunes. Lo que sí hay que mirar son las 96 que cruzan
un domingo con una lección de semana, porque ahí una de las dos lo presenta
como nuevo cuando no lo es.

**Lo que no cambió: el mazo.** `exportar_anki.exportar` ya deduplicaba, así
que ninguna palabra llegaba dos veces a Anki — el total subió solo por las
siete entradas que yo cambié: 2.362 tarjetas. El defecto estaba en el informe, no en lo que se publica.

Cómo quedó:

- **`exportar_anki.filas_de(ruta)`** es ahora el único sitio que decide qué
  tabla tiene un día, y `revisar_lexico` pasa por ahí. Dos copias de la misma
  pregunta es como se descubre tarde que una de las dos miente, y aquí la
  mentirosa llevaba meses: el propio docstring de `exportar_anki.exportar`
  promete que «`revisar_lexico.py` las lista».
- **La prueba no cuenta repeticiones** —ese número va a cambiar— sino que
  exige que **cada entrada de la tabla de un domingo llegue al informe**.
  Falla con el lector viejo y pasa con el nuevo.
- **Las siete de las semanas 37 y 38 se arreglaron**, que son las mías: *la
  terraza* (ya en tres domingos), *la longitud* (en S09D7, ahí «долгота»),
  *la colección*, *cariñoso*, *el equipo*, *la broma* y *madrugar*.

**Lo que queda para el profesor**: decidir qué hacer con las 96 que cruzan un
domingo con una lección. No se reescribieron 50 domingos ya revisados por una
lista que acaba de aparecer, y la regla del propio script sigue en pie: una
repetición puede ser legítima y decide el profesor.

## La unidad 21: la casa, y la unidad que ya estaba casi toda dada (días 281-294)

Catorce lecciones, semanas 41 y 42. El curso pasa de 280 a **294 de 365** y
**2.642 tarjetas**.

**Es la unidad con más material previo de toda la serie, y de otra manera que
la 20.** Allí eran seis días enteros ya dados; aquí lo que estaba repartido
era el **aparato completo** de la unidad, pieza a pieza, por quince semanas
distintas:

| Lo que el calendario traía | Ya estaba en |
|---|---|
| *se alquila / se alquilan*, la fianza, amueblado, los gastos incluidos | **S08D2-D3** (la unidad de los anuncios de pisos) |
| *no se puede*, *prohibido*, *se ruega*, *se vende*, *se habla español* | **S31D5** (carteles y normas) |
| *hay que* · *tener que* / *deber* comparados | **S17D4** · **S20D1** |
| los **ocho participios irregulares** | **S18D1**, para el perfecto |
| *está roto*, *no funciona*, *la avería*, *el grifo*, *el técnico*, *quejarse* | **S14D4** y **S18D5** (la queja en recepción) |
| *fregar los platos*, *la cerradura*, *el vecino de abajo* | **S28D5** |
| *poner la mesa* · *planchar, barrer, lavar, cocinar* | **S10D1** · **S10D7** |
| el casero, *mudarse*, *independizarse*, *compartir* | **S23D2** · **S23D5** · **S24D7** · **S25D1** |
| el portal, la escalera, el ascensor, el patio, la azotea, la comunidad | **S07D3** y **S07D7** |
| todo el aparato de la carta formal (*Estimado*, *quedo a la espera*, *Atentamente*, *adjuntar*, *en primer lugar*) | **S14D5** · **S30D3** · **S36D5** |

**Y lo nuevo de verdad, que es lo que las catorce lecciones enseñan:**

- **El participio con *estar*, y la agudeza es que contradice la unidad 9.**
  Allí se enseñó —y el test de la unidad 9 lo preguntaba— que *«el participio
  no cambia nunca»*: ✗ *María ha llegada*. Con *estar* **siempre** concuerda:
  *las ventanas están abiert**as***. Dos reglas opuestas, las dos ciertas, y
  lo que decide es el auxiliar. Aquí el ruso **ayuda** —«сломан / сломана /
  сломаны» también concuerda— y la dificultad es la contraria: no llevarse el
  acuerdo a las frases con *haber*. El noveno irregular es *muerto*, y hay
  seis más gratis con prefijo (*devuelto*, *resuelto*, *descubierto*,
  *descrito*, *compuesto*, *deshecho*).
- ***Está roto* (estado) frente a *se ha roto* (suceso)**, que es el
  `contraste_ru` declarado de la unidad: «сломан» / «сломался». S18D5 ya los
  había puesto uno al lado del otro sin explicarlos («*se ha averiado* — или
  *está averiado*», en su clave). Y de ahí sale la frase más útil de la
  semana: ***se me ha roto el móvil***, la construcción de tres piezas que
  S40D2 estrenó para el cuerpo (*se me hinchó el pie*). ⚠️ El verbo concuerda
  con la cosa: *se me **han** perdido las llaves*.
- ***Tocar*** («быть чьей-то очередью»), que funciona como *gustar* y como el
  *molestar* del viernes: *me toca*, *¿a quién le toca?* Tres verbos de esa
  familia en una semana, y el alumno ya tiene la máquina desde la unidad 6.
- ***¿Te importa si…?* y la trampa del ANSWER, no de la pregunta.** «Нет» =
  «можно». El ruso ayuda literalmente («ты не против?» → «нет»); el que se
  pierde es quien piense en inglés. La lección pide contestar con dos
  palabras (*no, no, ponla*) justamente porque la mitad del riesgo está ahí.
- ***Gracias por* + infinitivo** frente al «спасибо, **что**…» ruso, con la
  negación delante (*por no contestar*). Y ⚠️ ***perdón* no es *lo siento***:
  si a alguien se le ha muerto un familiar se dice *lo siento mucho* y nunca
  *perdón*, porque no es culpa suya. El ruso «извините» cubre los dos.
- **El *se* impersonal frente a la pasiva refleja, con UNA prueba
  operativa**: ¿qué hay justo detrás del verbo? Sustantivo sin *a* →
  concuerda (*se alquil**an** pisos*). Nada, o *a* + persona → singular
  siempre (*se dice que…*, *se busca **a** los dueños*). ⚠️ El ruso
  «говорят» en plural es lo que produce el ✗ *se dicen que*. Y ***uno***,
  porque dos *se* no caben: ✗ *se se levanta* → *uno se levanta*.

**El hilo que de verdad recorre la unidad no es gramatical, y conviene no
perderlo si alguien la reescribe: es a quién señala la frase.**

| Día | La misma idea, otra situación |
|---|---|
| 41-5 | ***hay que*** (regla, nadie señalado) frente a ***tienes que*** (señala a él, y es el principio de una discusión) |
| 42-3 | quejarse del **ruido** y no de la persona: ***se oye** mucho la música*, nunca *tú pones* |
| 42-5 | una **regla**, no un reproche: el tercer movimiento de la conversación es *en eso tienes razón* |
| 41-7 | comparar España y Rusia **sin decir dónde se vive mejor** |

Por eso la clave de 42-5 señala cuatro palabras —*tú*, *vosotros*,
*siempre*, *nunca*— como las que convierten un reparto de tareas en una
pelea.

**Decisiones de contenido:**

- **La edad de emancipación va con `[VERIFICAR]` y sin número** (regla 7). El
  fenómeno tiene nombre propio en la prensa española (*la emancipación
  tardía*) y causas estructurales que sí se pueden contar (el alquiler frente
  al primer sueldo, el contrato temporal, el aval); la cifra media cambia cada
  año y no se da ninguna. Lo que sí se dice es lo cultural, que es lo que el
  lector no espera: vivir con los padres a los veintiocho **no se lee como
  fracaso**.
- **Las horas de silencio no se inventan**: las escribe *la comunidad de
  vecinos* y están colgadas en el portal. La lección enseña la pregunta
  (*¿a partir de qué hora no se puede hacer ruido?*) en vez de un horario
  nacional que no existe.
- 🌎 **Dos avisos de la regla 8 que valen un anuncio entero.** *Fregar los
  platos* es peninsular y en parte de América *fregar* significa «надоедать»,
  así que *lavar* es más seguro en todas partes. Y sobre todo: **en media
  América *el piso* es el suelo o la planta**, no la vivienda, así que
  «сдаётся квартира» en México es *se renta departamento*. Toda la unidad va
  de alquilar, y el sustantivo cambia.
- **La casa latinoamericana se cuenta por su planta, no por adjetivos**:
  calle → *zaguán* → *patio* → *corredor* → habitaciones, y de ahí salen
  solas la reja (las ventanas dan al patio), la azotea útil y la hamaca como
  cama en Yucatán y el Caribe.
- **El episodio «Un año de contrato»** cierra pidiendo la persiana **antes**
  de firmar y con Carmen escribiendo a mano que ya estaba rota: es la unidad
  entera (*sigue rota*, *se rompió*, *¿podría?*) puesta a trabajar en el
  único momento donde sirve. Y la última línea es el arco: no firmó para
  quedarse un año, firmó porque ya había decidido quedarse.

**Los dos tests, comprobados en navegador de verdad.** El Мини-тест de la
semana 41 son 15 ítems (lo que pide el calendario) en **5/5/5**; el test de
la unidad, en **4/4/4/3**. `scripts/probar_navegador.js` los añade a su lista
y los contesta en Chromium eligiendo la opción por su TEXTO: 15/15 y 15/15,
cero errores de JS.

**Un subjuntivo entró y se quitó; otro se queda porque está declarado.** Se
colaron *para que las tenga todas juntas* y un *que lo revisen* en el día
42-5 (reescritos: *así las tiene juntas*, *que lo revisaran*). Lo que **sí**
se queda es ***le agradecería que* + imperfecto de subjuntivo**, porque
S30D3 lo enseña como fórmula hecha y con esas mismas formas (*que me
indicara*, *que me enviara*): es la regla de la unidad 20 —un chunk
declarado vale cuando no **contradice** una lección anterior—.

**Los tres barridos, y lo que cazaron:** 0 duplicados de léxico en las dos
semanas contra el curso entero (uno se corrigió: *equivocarse*, ya en
**S35D4**, sustituido por *es culpa mía*); dos tokens de dos alfabetos
(*нóмин* y *бóльшая*, las dos con una vocal **latina** dentro de una palabra
rusa — es el tercer caso de esa forma exacta, y a ojo no se ve nunca); y 0
formas no enseñadas después de los arreglos de arriba.

### Y una advertencia de método que casi costó reenseñar seis palabras

**El volcado del léxico hay que normalizarlo antes de buscar en él.** El
primer barrido de esta unidad dijo que *la fianza*, *los gastos incluidos*,
*amueblado* y *el casero* **no estaban enseñados** — y los cuatro lo están.
El motivo es que las lecciones tempranas marcan la sílaba tónica **dentro**
de la palabra (`la **fian**za`, `los **gas**tos in**clui**dos`), así que un
`grep fianza` sobre el volcado crudo no encuentra nada. Hay que pasar cada
entrada por `revisar_lexico.normalizar` —que quita negritas, artículo,
acentos y mayúsculas— y buscar sobre eso.

Es un falso negativo silencioso y del peor tipo: dice «esto es nuevo» de algo
que el alumno ya sabe, y el resultado habría sido una lección que presenta
como novedad la mitad de la unidad 4. El informe de repeticiones no lo habría
cazado después, porque yo habría cambiado la redacción, no la entrada.

## La unidad 22: fiestas y sentimientos, y el reparto al revés (días 295-308)

Catorce lecciones, semanas 43 y 44. El curso pasa de 294 a **308 de 365** y
**2.774 tarjetas**.

**El reparto es el inverso del de la unidad 21, y eso cambió cómo se
escribió.** Allí el aparato gramatical entero estaba dado y el léxico estaba
libre; aquí es al contrario: **las perífrasis estaban casi todas dadas** y el
léxico —fiestas, música, cine— estaba **libre entero**.

| Lo que el calendario traía | Ya estaba en |
|---|---|
| *empezar a* · *dejar de* · *volver a* | **S34D3** · **S19D5** · **S26D5** |
| ***seguir* + gerundio** | **S27D3** (ver abajo: lo cazó el informe de léxico) |
| *ponerse a* + inf. | **S39D3** |
| *llevar* + gerundio · *ya no* · *todavía* · *tener ganas de* | **S29** · **S20D5** · **S25D3** · **S16D2** |
| *dar miedo* · *dar pena* · *dar vergüenza* · *dar igual* · *estar harto de* | **S25D4** · **S39D3** · **S28D2** · **S39D3** |
| *ponerse* + adjetivo · *sentirse* + adjetivo | **S28D2** y **S39D3** |
| **¡Que aproveche!** · ¡Felicidades! · *felicitar* · *invitar a* · *el brindis* | **S12D1** · **S06D7** · **S34D4** · **S12D7** |
| las cuatro fiestas grandes, *la uva*, *la campanada*, *disfrazarse*, *el desfile* | **S16D7** |
| la Nochevieja · los Reyes Magos · el roscón | **S33D7** · **S34D7** |
| la película · la serie · el personaje · la trama · los subtítulos · *tratar de* · el final | **S21D7** (el domingo de cine) |
| el capítulo · la temporada · el documental · *merecer la pena* | **S36D4** |
| *se celebra* / *se come* / *se regala* | **S08D3**, **S31D5** y **S42D4**, de la semana pasada |

**Lo nuevo de verdad:**

- ***Acabar de* + infinitivo**, que es el `contraste_ru` declarado: «только
  что» en ruso es un **adverbio**, en español es un **verbo**. Y la trampa
  que vale una frase: *acabar de* significa «только что» **solo en
  presente**; para «terminé de hacerlo» se usa *terminar de*.
- **Los siete predlogi de la línea del tiempo en una tabla**: *estar a punto
  de* → *empezar a* / *ponerse a* → *seguir* → *llevar* → *dejar de* →
  *volver a* → *acabar de*. Tres con **a**, cuatro con **de**, y una sola
  —*seguir*— con **gerundio**, que es justo donde el ruso empuja al
  infinitivo («продолжаю учить»).
- ***llevar* / *seguir* + *sin* + infinitivo**: *llevo diez meses **sin**
  fumar*, *sigo **sin** entenderlo*. El ruso pone la negación en el verbo;
  el español, una preposición.
- **Las tres máquinas del sentimiento, y la elección es mecánica**: *me
  **da*** + **sustantivo** (miedo, pena, rabia, asco), *me **pone*** +
  **adjetivo** (nervioso, triste, de buen humor), *me **hace*** +
  **adjetivo o infinitivo** (feliz, reír). ⚠️ Y la bifurcación del día:
  ***me pongo* nervioso** (yo me pongo así) frente a ***me pone*
  nervioso** (el ruido me pone así) — una letra, y cambia quién actúa. La
  primera mitad venía de S39D3; la segunda es nueva.
- **La escala de recomendar, ocho peldaños**, cuatro arriba (*se puede ver <
  te la recomiendo < merece la pena < no te la pierdas*) y cuatro abajo, y
  el más fuerte de los de abajo no es una opinión sino un hecho: ***la dejé
  a la mitad***. Y el pronombre es obligatorio y concuerda (*no te **la**
  pierdas* / *no te **lo** pierdas*).
- ***No soy muy de…*** para los gustos, que no se traduce palabra por
  palabra. Y ⚠️ *me suena* («me resulta conocido») frente a *suena a* («se
  parece a»).

**Los chunks con subjuntivo: el calendario los pide, y la lección pone el
límite.** La unidad declara «fórmulas fijas con subjuntivo como chunks», así
que el día 43-4 enseña seis (*¡Que aproveche!*, *¡Que te mejores!*, *¡Que
tengas suerte!*, *¡Que lo pases bien!*, *¡Que descanses!*, *¡Que te vaya
bien!*) más *ojalá*, **como palabras**, con la instrucción explícita de no
fabricar una séptima. El mejor hallazgo del día: ***¡Que aproveche!* está en
el curso desde la semana 12**, o sea que el alumno lleva dos meses usando un
subjuntivo sin saberlo — y ésa es exactamente la forma en que debe saberlo en
A2.

⚠️ **Y escribí la séptima yo mismo.** El modelo de invitación cerraba con
*¡Que no falte nadie!*, que no está entre las seis declaradas: la lección
decía «no haga nuevas» y su propio ejemplo hacía una. Es el fallo de la
unidad 17 con otra cara (ahí fue *no creo que gane* en un texto modelo).
Reescrito a *¡Os espero!*

**Decisiones de contenido:**

- ⚠️ **El 8 de marzo no es la misma fiesta, y eso es lo más útil de la
  unidad.** En Rusia es día de flores y felicitaciones; en España y América
  es el **Día Internacional de la Mujer**, con manifestaciones y
  reivindicación. Un *«¡Felicidades por el 8 de marzo!»* a una española puede
  caer muy lejos de donde se apuntaba. La lección no prohíbe nada: enseña a
  **describir** (*en mi país se regalan flores a las mujeres*) en vez de a
  felicitar. Es la interculturalidad que `referencias/espana-en-vivo.md`
  echaba en falta —contraste de costumbre, no de gramática—.
- ⚠️ **«El flamenco no es el baile español»: es andaluz.** Decirle a un
  gallego «vosotros los españoles bailáis flamenco» es como decirle a un ruso
  que todos bailan kazachok. Y el domingo tiene una espina dorsal propia: los
  tres bailes **no comparten geografía, comparten origen social** — flamenco
  en las comunidades gitanas del sur, tango en los arrabales del puerto,
  cumbia en la costa caribeña con raíz africana, indígena y europea. Los tres
  nacieron abajo y hoy son lo que cada país enseña al mundo.
- **Las dos únicas cifras de los días de música son las de la UNESCO**
  (tango **2009**, flamenco **2010**), estables y citadas en todas partes —
  el mismo criterio que la dieta mediterránea de S20D7—. Ventas, oyentes,
  años de edición y puestos en listas van con `[VERIFICAR]`, y la tarea final
  lo exige por escrito.
- **El 9 de mayo frente al 8 de mayo**: un día de diferencia por la hora de
  la firma, que es un hecho sobre relojes y no sobre política. La lección
  cuenta **qué se hace** —el desfile, la foto del antepasado, los claveles en
  el monumento— y qué significa para una familia, y **no da ni una cifra**:
  las de pérdidas varían según la fuente y el país, y en A2 no hacen falta.
- ⚠️ **Contar una fiesta invierte la proporción de la unidad 13.** Allí quedó
  escrito que un relato de una vida lleva tres imperfectos por cada
  indefinido. Una fiesta es lo contrario, y está contado sobre el texto
  modelo: **7 imperfectos y 11 indefinidos**. El motivo no es estilístico: en
  una fiesta pasan cosas. La técnica del día es **contar sus propios
  tiempos** y, si ganan los imperfectos, buscar qué describió en vez de
  contar.
- ⚠️ **Una charla de dos minutos necesita MENOS palabras que el texto de
  150, no más.** Leídas, 150 palabras duran un minuto; el resto del tiempo se
  lo comen las pausas, el nombre repetido y mirar a la gente. Así que el oral
  es un **recorte** del texto, no una ampliación — y va con un **esquema de
  cinco palabras** delante, que es el método de la unidad 11 (нед. 22,
  день 5).

**Los dos tests, en Chromium.** El Мини-тест de la semana 43 son 15 ítems en
**5/5/5**; el test de la unidad, en **4/4/4/3**.
`scripts/probar_navegador.js` los añade a su lista y contesta por el TEXTO de
la opción: 15/15 los dos, cero errores de JS.

**Cuatro subjuntivos se colaron en textos modelo y se quitaron**, y dos de
ellos **contradecían la unidad 18**, que enseña *aunque* + indicativo:
*aunque parezca tonto* (44-1) y *aunque haga frío* (44-4) — el arreglo del
segundo es la lección misma, *aunque **hace** frío*—; más *a cualquiera que
quiera empezar* (44-2) y el *¡Que no falte nadie!* de arriba.

### Lo que cazó el informe de léxico, y es un tipo nuevo de hallazgo

Tres entradas repetidas, y una cambió una lección entera:

| Entrada | Ya estaba en |
|---|---|
| ***seguir* + герундий** | **S27D3** |
| *ponerse a* + инф. | **S39D3** |
| *desde entonces* | **S24D5** |

**La de *seguir* + gerundio es la que importa, porque estaba enseñada de
paso.** S27D3 es la lección de los irregulares del indefinido (*leyó, oyó,
durmió, pidió, trajo*), y dentro de ella, en el punto 5, hay una línea:
«*Siguió durmiendo* — «продолжал спать». *Seguir* + герундий». O sea que la
construcción **no es el tema de ninguna lección** y sin embargo está dada, y
además con entrada en el vocabulario, que es lo que permitió cazarla.

Es un caso distinto de los anteriores: no es material que una unidad vieja
enseñó como suyo, es material que se colocó **dentro de otra cosa**.

**Y al buscarle la pareja apareció la segunda, que el informe NO podía
cazar: *a punto de* también estaba dado, en S27D5.** Ahí, en la lección de
comprensión de noticias de la misma semana, hay *un turista que **estaba a
punto de** volver a su país*, con su entrada (*a punto de* + инф.) y su
punto de explicación («**A punto de** — «вот-вот»»). El informe no lo marcó
porque mi entrada decía *estar a punto de* y la vieja *a punto de*: dos
cadenas distintas, la misma construcción. Lo encontré con el volcado del
léxico mientras corría la suite, no con el informe.

**Así que los DOS titulares del día 43-2 estaban enseñados, los dos en la
semana 27 y los dos de paso.** Tiene explicación: la semana 27 es la de
narrar (unidad 14), y narrar necesita «siguió durmiendo» y «estaba a punto
de salir», así que ambas entraron donde hacían falta. El día ahora lo dice
en su punto 7, y lo que queda suyo son tres cosas: **la tabla de las siete
perífrasis en un solo sitio** —la primera vez que se ven como sistema, y lo
que pregunta el test—, las formas con ***sin*** (*llevo diez meses sin
fumar*, *sigo sin entenderlo*), y la diferencia entre *llevo* y *sigo*.

La lección de método es la del informe, afinada: **compara entradas, no
construcciones**, así que una misma forma escrita de dos maneras pasa
inadvertida. Antes de dar por nueva una perífrasis, hay que buscarla con
`grep` sobre `curso/` **en todas sus formas** —*a punto de* y *estar a punto
de*, *seguir* y *sigo*— y no solo en el volcado.

**Y la advertencia de método de la unidad 21 volvió a morder, en otra
forma.** Ayer quedó escrito que el volcado del léxico hay que normalizarlo
antes de buscar. Hoy faltaba la otra mitad: ***normalizar* también quita el
artículo**, así que `grep "la película"` sobre el volcado normalizado no
encuentra nada y `grep "pelicula"` encuentra tres. Buscar siempre **sin
artículo** y sin acentos; con el artículo delante, media docena de palabras
de cine y de música parecían nuevas y no lo eran.

## La unidad 23: leer y escribir, y el día que el informe de léxico no bastó (días 309-322)

Catorce lecciones, semanas 45 y 46. El curso pasa de 308 a **322 de 365** y
**2.912 tarjetas**. Es la última unidad con material nuevo: la 24 es repaso de
todo el A2 y las semanas 49-52 son simulacros.

**Lo que se comprobó antes de escribir, y cambió cinco de las siete lecciones
de la semana 46:**

| Lo que el calendario traía | Ya estaba en |
|---|---|
| los tres bloques del relato (Situación · Problema · Desenlace) y *Resulta que…* | **S27D4** y **S27D2** |
| *solicitar*, *la solicitud*, *Le escribo para* + инф., *le agradecería que* | **S30D3** |
| *el importe* (en el cajero) · *la firma* («подпись», no «фирма») | **S32D1** · **S21D5** |
| *soleado* (con *estar*), *luminoso*, *metros **cuadrados*** | **S15D4** · **S07D3** · **S08D3** |
| *el suelo*, *el techo*, *la persiana*, *acogedor*, *dar al patio* | **S41** · **S42D7** |
| la lista negra entera, con un texto que trae los diez errores | **S22D3** |
| *el recibo*, *el trastero*, *el buzón*, *hecho a mano*, *el impreso* | **S41D1-2** · **S06D7** · **S31D7** |

Cada lección lo dice ahora en su primer punto y enseña solo lo que faltaba.

### La lección de método: el informe de léxico no basta, y hay que grepear

`revisar_lexico.py` compara **entradas de las tablas de vocabulario**. No ve
nada de lo que se enseñó **dentro de una explicación** ni en una tabla de
prosa. Tres casos de esta unidad, los tres encontrados con `grep` sobre
`curso/` y **ninguno** por el informe:

- **los tres bloques del relato** están en S27D4, en una tabla de la
  explicación, con su tiempo verbal y todo;
- **`la firma`** está en S21D5, en la tabla de falsos amigos
  («la firma | фирма | подпись»), que es justamente donde se enseña de verdad;
- **`soleado`** está en S15D4 y S33D3, como ejemplo de otra entrada.

Así que antes de dar una palabra por nueva hay que grepear todo `curso/`, y
el grep tiene **dos trampas** que costaron dos vueltas:

1. **Sin artículo.** `normalizar` quita el artículo, así que `grep "la novela"`
   no encuentra «su novela» de S23D5 y la palabra parece libre. Se busca
   `novela`.
2. **Descartando `tema_es:` y `# Semana`.** Los títulos en español de las
   lecciones vienen del calendario y **no son léxico enseñado**: por ellos
   «sustantivo», «adjetivo» y «artículo» salían como usados cuando el alumno
   nunca los ha leído.

Y una tercera, que es de criterio y no de patrón: los **términos gramaticales**
(*el sustantivo*, *el adjetivo*, *la preposición*, *el artículo*) aparecen en
las explicaciones rusas de todo el curso como etiquetas. Eso no es enseñarlos.
El día 4 los enseña **como palabras**, y lo dice, porque la lista de control
los necesita para funcionar.

### Lo nuevo de verdad, día a día

- **S45D1-2 · leer.** Dos formas de leer (*ojear* / a fondo) y el hábito que
  ahorra la mitad del tiempo en el examen: **primero la pregunta, después el
  texto**. Y los **tres tipos de respuesta incorrecta** —verdadera pero
  pequeña, parecida pero cambiada, razonable pero no está—, que es el aparato
  más reutilizable de la semana: vuelve en el domingo, en el mini-test y en el
  test de la unidad.
- **S45D3-4 · ortografía.** ⚠️ **La tilde no es el acento**: el acento está en
  todas las palabras, la tilde solo donde la regla la pide, y las reglas son
  tres. El día 4 es lo contrario: *b/v*, *h*, *g/j*, *c/z/s*, *ll/y* **no se
  oyen**, así que son reglas cortas y listas. Más los signos que abren y la
  coma que no va delante de *que*.
- **S45D5 · el correo informal (DELE tarea 1).** La única forma segura de
  suspender es no contestar a todas las preguntas: contarlas y tacharlas.
- **S46D1 · el correo formal.** ⚠️ **La petición va PRONTO y es UNA**, en su
  propio párrafo. En el oficio ruso el escrito expone largo y «просит» al
  final; en español un correo que no pide una cosa concreta **no se puede
  atender**. Y el *usted* no se suelta a mitad de camino: es el error que se ve
  en una sola palabra.
- **S46D2 · el texto narrativo (DELE tarea 2).** El reparto de los tres
  tiempos —indefinido la cadena, imperfecto el fondo, perfecto solo el
  desenlace— y **la proporción**, que es el dato nuevo: una anécdota de 75
  palabras queda **casi mitad y mitad** (7 imperfectos y 6 indefinidos en el
  texto modelo), entre los tres a uno de un relato de una vida (единица 13) y
  el predominio del indefinido de una fiesta (единица 22). La técnica es
  **contarlos**.
- **S46D3 · el texto descriptivo.** ⚠️ ***Hay* nunca lleva artículo
  determinado**: ✗ *hay la mesa*. Y la pareja que lo explica: *En el rincón
  **hay una** alfombra* (nueva para el lector) frente a ***La** alfombra
  **está** en el rincón* (ya la conoce). En ruso las dos frases se dicen casi
  igual y **no hay artículo que lo marque**, así que la elección se hace a
  mano cada vez. Más **el olor y el sonido**, los dos sentidos que nadie
  escribe y los que convierten una lista de muebles en un sitio.
- **S46D4 · la lista de control.** ⚠️ **Una pasada por cada tipo de error, no
  una pasada buscando errores.** Leer una vez «buscando fallos» no encuentra
  casi nada, porque la cabeza lee el sentido y rellena sola lo que falta; diez
  pasadas de veinte segundos buscando **una palabra concreta** (los *yo*, los
  *que*, las formas de pasado) encuentran casi todo. Son tres minutos y medio
  y valen un punto entero de *corrección*.
- **S46D5 · los dos textos en 45 minutos.** El reparto por minutos, el
  borrador de **cinco palabras** —el borrador-texto de la escuela rusa no cabe
  en este reloj— y la regla que más cuesta: **un criterio a cero suspende**
  aunque la suma llegue a siete (`evaluacion.md`, §3), y el que se va a cero
  es *adecuación*, por olvido y no por lengua.

**El día 4 estaba previsto desde el principio y no se sabía.**
`contrastiva-ru-es.md` §8 dice literalmente que la lista negra «se entrega en
U1, se repasa en U11 y U24, y **la lista de control de U23 la usa para
corregir textos**», y marca con **U23** justamente sus números 8 (tildes) y 20
(la coma de *que* y *qué/que*). O sea que los dos errores que esta unidad
añade a la lista estaban asignados a ella desde que se escribió el documento.

### El test de la unidad: el tercer bloque es ortografía

`evaluacion.md` §4 fija 6 + 6 + 3 y dice que desde la U14 el tercer bloque es
«Выражения». Aquí es **«Орфография»**, y es la única unidad de A2 donde no es
lo uno ni lo otro: lo pide el calendario (`foco`: «ortografía, conectores,
comprensión de un texto») y además **la ortografía ES el material de la
unidad**. La comprensión no va en un texto compartido sino en **dos ítems
autocontenidos** del primer bloque, y eso no es estilo: `pruebas.leer` descarta
lo que hay antes del ítem 1 de un bloque, así que un texto puesto ahí se vería
en papel y **no** en la versión interactiva — el alumno tendría que contestar
sobre un texto que no está.

### Los derechos de autor, que en esta unidad había que decidir

- **Lorca murió en 1936**, así que su obra es de dominio público en España: las
  dos primeras estrofas de «El lagarto está llorando» se citan enteras.
- **Monterroso (†2003) y Neruda (†1973) no lo son.** De Monterroso se **cita**
  «El dinosaurio» —siete palabras, con autor y obra, como el ejemplo fundador
  del género—; de Neruda **no se copia ni un verso**: se cuenta la idea de las
  *Odas elementales* (odas al tomate, a la cebolla, a los calcetines), que es
  justamente la lección del día. Y se dice en la lección por qué no se copia.
- Los tres microcuentos de A2 y el capítulo de «La habitación de arriba» están
  **escritos para el curso**. El año de las dos ediciones citadas va con
  `[VERIFICAR]`, y las series de lecturas graduadas también: desde este
  contenedor no se puede comprobar qué hay publicado ni qué tiene la biblioteca
  de su ciudad.

**Y el capítulo sirve de demostración**: doscientas palabras cuya gramática es
entera de las единицы 12 a 23 —indefinido, imperfecto, un imperativo negativo,
participios con *estar*, *hay/había*— sin una sola forma que el alumno no haya
dado. Así se escribe una lectura graduada, y es el mejor argumento para que
abra una.

**El episodio «El correo difícil»** cierra la unidad con Iván escribiendo solo
la carta de sus papeles: setenta y ocho palabras, los seis bloques del lunes,
el esqueleto en el margen del viernes. Lo que ha cambiado en un año no es su
español; es que ahora lo escribe él.

### Los barridos

- **Un duplicado de léxico**, `exagerar` (ya en S28D7, el domingo del humor),
  sustituido por `afirmar`, que además es la palabra que el día 2 necesita para
  distinguir hecho de opinión.
- **Cero tokens de dos alfabetos** tras corregir uno en el test de la unidad
  («вейсинос» por «соседи», que es la misma falla de transliteración de las
  unidades 17 y 21 con otra cara).
- **Siete subjuntivos en textos propios**, y **dos de ellos contradecían la
  unidad 18**, que enseña *aunque* + indicativo: *aunque el texto sea
  impecable* y *aunque la suma llegue a siete*. Los otros cinco: *vaya* en el
  enunciado de la tarea del día 45-5, *quieren que abra* y *esté cerrada* en el
  45-2, *que el fondo sea cero* en el 46-2, *de que llegue a la boca* y *que no
  haya dado* en el 46-7. Lo que sí se queda es *le agradecería que* +
  imperfecto de subjuntivo, que es el chunk declarado de S30D3.
- **`quizá` fuera del día 45-3**: la единица 17 lo descartó a propósito —admite
  los dos modos— y la forma del curso es *a lo mejor*. Se había colado tres
  veces.

### Los dos tests, en Chromium

El Мини-тест de la semana 45 son **20 ítems** (lo que pide el calendario) y
todos de ortografía, en **7/7/6**; el test de la unidad, en **4/4/4/3**.
`scripts/probar_navegador.js` los añade a su lista y los contesta eligiendo la
opción por su TEXTO: **20/20 y 15/15, cero errores de JS**.

## La unidad 24: repaso integral de A2, y el nivel cerrado (días 323-336)

Catorce lecciones, semanas 47 y 48. El curso pasa de 322 a **336 de 365** y
**2.952 tarjetas**. **Aquí se acaba el material nuevo**: lo que queda son las
semanas 49-52, que son simulacros, y el día 365.

**Es la unidad más distinta de todas, y por una razón de forma:** de los
catorce días, **once son de tipo `repaso`** y los otros tres son dos de
`cultura` y uno de `prueba`. Un `repaso` no lleva `## Словарь дня`, así que
esta unidad añade **solo 40 entradas de vocabulario** —las dos tablas de los
domingos— contra las ~140 de una unidad normal. Y por lo mismo **no hay
riesgo de duplicados**: el informe de léxico salió limpio sin tocar nada, que
es la primera vez en diez unidades.

### Cómo se reparte el repaso

| Día | Qué consolida |
|---|---|
| **47-1** | presente irregular en cinco grupos · reflexivos · **la máquina del dativo**: los ocho verbos tipo *gustar* en una tabla |
| **47-2** | los tres pasados en **dos preguntas**: ¿sigue abierto el tramo? y ¿suceso o fondo? |
| **47-3** | futuro y condicional son **una sola tabla** (las once bases son las mismas) · las siete perífrasis con su preposición |
| **47-4** | imperativo (cuatro personas × sí/no) · pronombres y *se lo* · **los tres *se*** |
| **47-5** | los **cinco puntos de decisión**: *ser/estar/hay*, *por/para*, comparar, relativos, indefinidos |
| **47-6** | los diez campos léxicos de A2 y **ocho falsos amigos nuevos** |
| **47-7** | una película: tres fragmentos y por qué el español del cine no es el del curso |
| **48-1 a 48-4** | las cuatro pruebas del DELE A2, una por día |
| **48-5** | la lista negra entera, y **la lista personal** |
| **48-6** | prueba integral: **40 ítems** en cuatro bloques |
| **48-7** | qué hay después de A2, el plan de cinco recursos y el episodio «Se apunta» |

### Las cuatro ideas que esta unidad añade, aunque sea repaso

1. ⚠️ **De los veinte errores de la lista negra, los suyos son cinco o
   seis** (48-5). Nadie comete los veinte. Trabajar la lista entera antes del
   examen es repartir el tiempo donde no hay nada que ganar, y **cuáles son
   los suyos se averigua contando en sus propios textos**, no recordando. Y
   se ordenan **por lo que cuestan**, no por frecuencia: cinco de los veinte
   *cambian el sentido* (*ser/estar*, *tener/ser* la edad, imperfecto por
   indefinido, *saber/conocer*, *por/para*) y dos *delatan un texto
   traducido* (el *yo* de más, la coma antes de *que*).
2. ⚠️ **En la prueba de audio, la respuesta correcta casi nunca repite las
   palabras del audio** (48-1), y la equivocada sí. Eso **no es oído**: es la
   misma habilidad del día 2 de la нед. 45, y por eso el mini-test de ese día
   son **transcripciones** —entrena la mitad del problema que se puede
   entrenar sin audio, y lo dice—.
3. ⚠️ **De los cuatro criterios de la rúbrica escrita, tres se suben
   revisando y uno solo se sube ANTES de escribir** (48-4): *alcance*
   consiste en decidir qué va a usar. Tres frases —dos tiempos verbales, un
   conector poco frecuente, una estructura de alguna unidad— lo llevan de 1 a
   3 sin una palabra difícil.
4. ⚠️ **La meseta** (48-7): de A0 a A2 el avance se nota cada semana porque
   se parte de cero; de A2 a B1 el avance es el mismo y **no se nota**,
   porque cada palabra nueva es una entre dos mil. Lo que la rompe no es más
   horas: es **medir otra cosa** —minutos que aguanta escuchando, frases
   seguidas que dice, cuánto entiende de un capítulo la segunda vez—.

**Y lo que B1 añade es UNA cosa: el subjuntivo.** El día 48-7 lo dice con la
tabla de las salidas que este curso usó en su lugar (*creo que no vendrá*,
*a lo mejor viene*, *quiero verte*, *cuando llegas*) y su versión de B1. Es
**el único sitio del curso donde se escriben formas de subjuntivo a
propósito**, y está explicado: son la columna «en B1».

### Lo que hubo que comprobar, y una cosa que cambió el plan

- **Los ocho verbos tipo *gustar* están todos enseñados**, repartidos:
  *gustar* (U6), *encantar* (S11D4), *doler* (S19D2), *quedar bien/grande*
  (S13D4), *interesar* (S15D2), *dar miedo* (S25D4), *poner nervioso*
  (S39D3), *parecer* (S35D1). La unidad los junta por primera vez.
- **Los falsos amigos de A1 ya se dieron** (S21D5: *la carta*, *el mapa*,
  *la firma*, *embarazada*, *sensible*, *el éxito*, *el vaso*, *la
  carpeta*…), y *largo* además en **S04D3**. El calendario pedía «constipado,
  sensible, éxito, largo, vaso…» y tres de esos cinco estaban dados: el día
  47-6 los presenta como repaso y enseña **ocho nuevos** (*constipado*,
  *actualmente*, *realizar*, *asistir a*, *soportar*, *pretender*,
  *educado*, *el disgusto*), de los cuales *soportar* y *asistir* vienen del
  **inglés** y no del ruso: quien sabe inglés los falla más.
- **El método de los tres visionados está en S21D7**, así que el domingo 47-7
  no lo repite: enseña a **elegir tres fragmentos** (principio, conflicto,
  final) con los que se resume la película entera, y la escucha selectiva
  (nombres, números, la palabra que se repite).
- **La estructura de las cuatro pruebas del examen sale de
  `alineacion-mcer-pcic.md` §5**, que la verificó contra fuentes que citan la
  guía oficial de 2020 y pide cotejarla. Las lecciones de la semana 48 la
  citan y repiten el aviso: lo que no depende de eso son las estrategias.

### El test integral: 40 ítems y el reparto de letras, generado

El día 48-6 son **cuatro bloques de diez**, que es lo que `pruebas.leer`
necesita (un `### N.` y un `**N. Título:**` por bloque). Con 40 ítems el
reparto de la letra correcta **ya no se puede hacer a mano**: se generó con
un script que exige **14/13/13**, ningún trío igual seguido y ninguna
escalera (`абв` ni `вба`).

**Y hacerlo así descubrió que cuatro de los mini-tests que yo había repartido
a mano tenían escalera** —S47D1, S47D2, S47D4 (tres) y S48D1, que además
estaba en 6/4/5 y no en 5/5/5—. Se arreglaron **reordenando las opciones**,
sin cambiar ni un enunciado ni una respuesta. La comprobación es ahora un
bucle de ocho líneas sobre los doce tests de la unidad, y conviene correrlo
siempre: **la escalera no se ve leyendo la clave**, porque la clave se lee
número a número y la escalera está entre tres números seguidos.

### Los barridos

- **Cero duplicados de léxico** (los `repaso` no tienen tabla) y **cero
  tokens de dos alfabetos**.
- **Once subjuntivos en prosa propia**, y **uno repetía un error ya corregido
  dos días antes**: *«aunque la suma llegue a 7»*, que es el mismo
  *aunque* + subjuntivo que se quitó de S46D5 y que **contradice la unidad
  18**. Los otros: *haya servido*, *haya visto*, *aunque fuera en ruso*
  (copiado de S21D7), *antes de que empiece*, *como si fuera* (dos veces),
  *que escriba*, *donde haya*, *que estén*, *que ponga*. Todos reescritos sin
  subjuntivo.
- **Lo que SÍ se queda**: las formas de imperativo negativo y de *usted* (*no
  hagas*, *no vayas*, *hable*, *escriba*, *puntúe*), que son material de la
  unidad 16; los distractores marcados como incorrectos (*no venga* frente a
  *no vendrá*); *¡venga!* como muletilla; y la columna «en B1» del día 48-7.

### En navegador

`scripts/probar_navegador.js` añade el Мини-тест de 20 de la semana 47 y el
test integral de 40, que es **el test más largo del curso**: **20/20 y 40/40,
cero errores de JS**. Si algún día el envoltorio se rompe con muchos ítems,
se rompe ahí.

## El reparto de letras no llegaba a los mini-tests ni a los exámenes (2026-10-28)

La corrección del 2026-10-27 repartió la letra correcta de los **quince tests
de unidad**. Al ir a escribir los dos mini-tests de la semana 52 se midieron
los demás días con clave, y el agujero era mayor que el que se había tapado:

| | Estado antes | Lo peor |
|---|---|---|
| 15 `prueba` (test de unidad) | repartidos el 27 | — |
| **23 `repaso`** (Мини-тест) | **los 23 mal** | S27D6: **14 de 15** en la б) |
| **1 `examen`** (final de A1) | **mal** | **27 de 45** en la б) |

**El del examen de A1 es el que duele**: 27 de 45 es exactamente el 60 % con
el que se aprueba el nivel, así que **marcando todo б se pasaba a A2 sin saber
nada**. Y los mini-tests son contestables en la web desde el 2026-10-28, o sea
desde el día anterior: el alumno se puntúa con ellos.

**Por qué la prueba no los veía**, que es lo de siempre: `test_la_letra_correcta_esta_repartida`
hacía `glob("semana-*/dia-6.md")` y se quedaba solo con `tipo == "prueba"`. Los
mini-tests de repaso quedaban fuera por el tipo —y cinco de ellos además por el
nombre, porque la unidad 11 tiene repasos entre semana— y el examen por las dos
cosas y por una tercera: **`pruebas.leer` no sabe leerlo**.

Cómo quedó:

- **`pruebas.leer_examen`**, porque la clave de un examen vive en el apartado 3
  («> **1** а · **2** б …») y su numeración es continua entre sus dos bloques.
  **No lo hace contestable**: `construir_sitio` sigue ofreciendo solo `prueba` y
  `repaso`, y el informe de `pruebas.py` lo dice con otras palabras («se leen
  con seguridad») para no prometer lo que no hay.
- **La prueba recorre el CALENDARIO y los tres tipos**, no un glob: los días de
  la fase final no tienen `unidad` ni caen todos en el día 6.
- **La escalera de tres (абв / вба) se exige solo donde hay TRES opciones**, y
  eso no es para que la prueba pase: con tres, абв son las tres letras en orden,
  o sea un patrón completo; con cuatro son tres de cuatro y no predicen la г).
  Medido: trece de los veintitrés tests de unidad tienen una, que es lo que da
  el azar en quince ítems.
- `pruebas.main()` **ya no revienta con `d.unidad` vacío**: los días de las
  semanas 49-52 no tienen unidad, y formatear `None` es un `TypeError`.

**Lo que se cambió de las lecciones es el ORDEN de las opciones y nada más.**
Ni un enunciado, ni un texto de opción, ni una respuesta. Los dos guiones del
reparto (`repartir_mini.py` y `repartir_examen.py`, en el scratchpad de la
sesión) leen la clave como fuente de verdad, permutan, reescriben **solo la
letra** de la clave —el «(день N)» se conserva: es lo que hace que el resultado
enlace a su lección— y al terminar vuelven a leer el fichero y comprueban ítem a
ítem que el TEXTO de la respuesta marcada es el mismo.

**Y remapean las referencias de la prosa**, que es donde esto se rompe sin
avisar: once renglones del tipo «**7 (а) *mucho tos***» nombran la letra de un
distractor. En la corrección del 27 esas quince referencias se arreglaron **a
mano**; aquí se derivan de la permutación, y una comprobación aparte exige que
cada una siga citando el texto que cita.

**Dos tropiezos del camino que vale anotar:**

1. **El span de un ítem no puede comerse el salto de línea que lo separa del
   siguiente.** Al reescribir el ítem en una línea, dos ítems se pegaron y el
   segundo desapareció — y lo peor es que `leer_minitest` **seguía leyendo
   quince**, con el enunciado del primero y las opciones del segundo. Un fallo
   que no se pone en rojo.
2. **`test_una_clave_de_minitest_que_no_cuadra_lo_deja_como_esta` se puso en
   rojo y tenía razón**: rompía la clave con un `.replace()` de una cadena
   literal, así que al cambiar las letras el `replace` se quedó en nada y la
   prueba comprobaba un fichero intacto. Es **exactamente** el error que el 27
   se corrigió en su hermana, en el fichero de al lado. Ahora la avería se
   deriva del propio fichero.

## La fase final: dos simulacros, el proyecto y el día 365 (días 337-365)

Veintinueve lecciones, semanas 49 a 53. **El curso está escrito entero: 365 de
365.**

No son lecciones: son **cuatro tipos de día que el curso casi no había usado**
—`simulacro` (14 días), `proyecto` (3), `reserva` (1) y los ocho `repaso` de las
semanas 50 y 52—. Aquí no entra ni un punto de gramática nuevo; lo que entra es
el examen.

### Las dos semanas de simulacro, y por qué son dos

| | Semana 49 | Semana 51 |
|---|---|---|
| lectura | T1 correo + T2 anuncios · T3 personas + T4 preguntas | T1 correo + T2 anuncios · T3 personas + **T4 con propuestas** |
| audio | 6 diálogos + 6 avisos · 3 personas + 9 mensajes | igual, otro material |
| escritura | correo 60-70 · **relato** 70-80 | correo 60-70 · **descripción** 70-80 |
| oral | lámina «el tiempo libre» | lámina «un día de trabajo» |

**Dos cosas cambian de forma a propósito, y las dos están explicadas en su
Инструкция:**

- **la tarea 4 de lectura** pasa de preguntas de comprensión a **texto con seis
  propuestas**, que es la forma del DELE real. Y con eso cambia la estrategia:
  «primero las preguntas» no sirve donde no hay preguntas, y lo que sirve es
  leer el texto entero sin pararse, porque media propuesta se resuelve con lo
  que viene **después**.
- **la tarea 2 de escritura** pasa de relato a descripción, y con ella la
  proporción de tiempos: un relato es indefinido con fondo de imperfecto, una
  descripción es presente con un *antes había* / *ahora hay*.

**No hay audio de verdad y se dice así.** Las frases van en **tablas**, que es
lo que `generar_audio.frases_de` recoge, así que cada una sale con su ▶. Y la
Инструкción avisa de lo que eso no es: esa voz **lee** —despacio, sin ruido y
sin solapes— y el examen de verdad es **más difícil**, no menos. Las
grabaciones reales van con `[VERIFICAR]` a los modelos del Cervantes.

### Lo que decidió el contenido

- ⚠️ **El aprobado es por GRUPO y no por suma**, y los cuatro días de
  corrección lo repiten: lectura + escritura = 50 con **30** necesarios, audio
  + oral = 50 con **30**. Sesenta y cinco en uno y veinticinco en el otro son
  noventa de cien y **es un no apto**. Por eso en ninguna tabla de la fase
  final aparece el total de cien: en este examen no existe.
- **La semana 50 son cuatro refuerzos y un juego.** Los refuerzos salen del
  resultado, no de una lista: el día dice a qué volver según qué prueba se
  cayó. Y el sábado es el **quiz de 50 preguntas** en cinco rondas, con una
  lectura que no es el total: **la ronda más baja** es la que dice dónde
  trabajar. Treinta de cincuenta es el 60 %, el mismo aprobado del DELE, para
  que el número de hoy se lea con la vara de mañana.
- ⚠️ **Una sola cifra por grabación.** El domingo de la semana 51 pide elegir
  **el número que salió peor** el viernes anterior y no mirar los otros tres:
  cinco objetivos a la vez son cero objetivos.
- ⚠️ **La película completa es otro ejercicio que el corto** (нед. 50, день 7).
  Cien minutos no se ven tres veces, así que lo que se persigue no son las
  palabras sino **el hilo**, con un número: el **60 %** es un éxito a este
  nivel. Seis reglas, y la segunda es la que cuesta aceptar — **subtítulos en
  español, nunca en ruso**: el ojo lee la lengua materna sin esfuerzo y
  entonces **el oído se apaga solo**.
- **El proyecto son tres días y el texto se decide antes de escribirse**: ocho
  formas elegidas el martes, el texto el miércoles con las diez pasadas de la
  unidad 23, y el jueves la grabación **sin leer**. Y eso último no es una
  regla de estilo: leído, el ejercicio no mide nada, porque lo que hay que
  poder hacer en mayo es hablar tres minutos sin papel.
- ⚠️ **Tres minutos hablando son MENOS palabras de las que uno cree.** El texto
  del proyecto son 174 palabras y leído dura poco más de un minuto: el audio no
  es el texto dicho en voz alta, es el mismo contenido con más aire. Y si se
  acaba a los dos minutos, el único bloque que aguanta crecer es la anécdota.
- **El día 365 existe desde el calendario**, y su mejor uso puede ser **no
  usarlo**: 52 × 7 son 364, y el que sobra se reservó para lo que se quedara
  sin hacer en la última semana, que es donde se acumula. Si no quedó nada,
  dejarlo en blanco es una decisión.

### El examen final reutiliza los 40 del examen de A1, y eso era una promesa

El examen de A1 (нед. 22, день 6) termina diciendo que **dentro de un año se
pasará el mismo examen otra vez** y que «la diferencia entre las dos hojas es
la única nota que significa algo». Así que el examen final son **60 ítems: los
40 de aquel, literalmente los mismos**, más 20 de A2 (pasados, futuro y
condicional, imperativo y pronombres, léxico y construcciones). La tabla de
puntuación tiene por eso **dos columnas**, y el día dice cuál de los dos
números importa: no el total, sino el «Итого A1» contra el de la semana 22.

Y avisa de algo que descoloca: **esos cuarenta pueden salir peor de lo que se
espera**, porque hace un año *ser* y *estar* se estudiaban **esa semana**. Un
bajón ahí no es haber olvidado el idioma: es una tema que no se toca desde
hace meses, y eso es justo lo que hay que saber antes de mayo.

### `validar.py` no sabía comprobar un día de reserva

`APARTADOS` no tenía `reserva`, y mientras no conoce un tipo **su validación no
comprueba nada**: el día 365 habría pasado con cualquier forma. Es el agujero
que ya se cerró en la unidad 11 con `simulacro`, `examen` y `proyecto`, y el
momento de cerrarlo es el primer uso. Un día de reserva no prepara ni corrige,
así que su segundo apartado no es «Подготовка» sino **«Что осталось»**, que es
lo único que ese día decide.

### Los barridos

- **Cero duplicados de léxico** contra el curso entero. La fase final solo
  añade **40 entradas** —las dos tablas de los domingos de las semanas 50 y 52—
  porque un simulacro, un proyecto y un repaso no llevan `Словарь дня`. Total
  del curso: **2 992 tarjetas**. Los 135 duplicados que quedan son los de
  siempre, todos de antes de la semana 49.
- **Dos tokens con los dos alfabetos**, los dos del mismo tipo que ya apareció
  en las unidades 17, 21 y 23: una letra latina dentro de una palabra rusa
  (`proходной`, `nед.`). A ojo no se ven nunca.
- **Veintiséis formas de subjuntivo en prosa propia**, y **cuatro eran
  `aunque` + subjuntivo**, que **contradice la unidad 18**. Es la cuarta
  unidad seguida en la que aparece ese mismo error, así que conviene decirlo
  sin rodeos: *aunque* es el que se escribe solo. Lo que **sí** se queda, porque está enseñado o
  declarado: el **imperativo de usted** (*lea*, *escriba*, *haga*, *ponga*…,
  unidad 16), *o sea* y *fuera de* —los dos usados en quince y doce lecciones
  anteriores—, *cuando quiera* (chunk declarado en la unidad 20) y los
  distractores marcados como incorrectos. Y `lo que sea` se reescribió
  justamente porque **no** aparecía antes en ninguna lección.

### El enlace a la clave se perdía en tres días, y nadie lo habría visto

`_envolver_clave` pone el enlace «ir a la clave» detrás del **último** apartado
que contiene una marca de ejercicio. En un simulacro el apartado de corrección
**menciona** un ejercicio —«Задание 2, номер 11: решает «sin gluten»»—, así que
el último apartado con marca era el de corrección, el corte caía **en la clave
misma** y entonces `corte < inicio_clave` era falso y **el enlace no se
ponía**. Sin error, sin aviso y sin diferencia visible salvo que falta un
enlace.

Arreglado donde estaba el defecto y no en las tres lecciones: ahora se busca el
**último corte que esté de verdad antes de la clave**, que en esos días es
donde acaban los ejercicios. Solo cambia el resultado donde antes no había
enlace. Lo cazó `test_toda_leccion_con_clave_la_pliega_y_la_enlaza`, que ya
existía: lo que faltaba era un tipo de día que lo provocara.

### El test de nivel mandaba al día de reserva a quien lo aprobaba

Dos defectos del mismo sitio, los dos destapados por tener días **sin
unidad** (las semanas 49-52 son la fase final y la 53 el día de reserva):

- **`inicios_de_unidad` agrupaba por `d.unidad` sin mirar si existe**, así que
  publicaba una clave **`"null"`** en los datos que viajan al navegador. No
  rompía nada —las preguntas se mapean a las unidades 1-24 y nadie busca
  `null`— pero era un dato falso servido en cada visita.
- **`ultima` era la última lección escrita a secas**, y con el curso entero eso
  es el **día 365**. O sea que a quien acertaba las catorce preguntas del test
  de nivel se le mandaba a una página que dice que **hoy no hay nada que
  hacer**. Ahora es la última lección **de una unidad**: el domingo de la
  unidad 24, que trata precisamente de qué hay después de A2 — que es la
  respuesta a «ya sé todo lo que el curso cubre».

Las dos las cazó la suite —`int("null")` en una prueba que ya existía— y hay
una nueva que fija el destino: `test_la_ultima_del_test_de_nivel_no_es_el_dia_de_reserva`.

**Y el texto del resultado decía lo que ya no es verdad**: «empiece por la
última lección **escrita**», que con el curso entero es el día 365 y no es a
donde va el botón. Ahora dice «la última lección **del curso**, que trata
precisamente de qué hay después de A2», en los tres idiomas. Comprobado en
navegador contestando las catorce bien: 14/14 y el botón a `semana-48/dia-7`.

### Y una trampa del `grep` que faltaba por escribir

La unidad 21 dejó dicho que **el volcado del léxico hay que normalizarlo antes
de buscar en él** y la 22 que hay que **buscar sin artículo**. Faltaba la otra
mitad, y esta vez dio seis falsos negativos seguidos: **el texto del curso que
se registra también lleva las marcas dentro de las palabras.** `ro**dar**`,
`la car**te**lera`, `el fotogra**ma**`: un `grep rodar` sobre `curso/` no
encuentra nada y la palabra parece libre cuando llevaba una semana enseñada.

Hay que normalizar **las dos partes**: el `grep` va contra una copia del curso
con los asteriscos quitados (`tr -d '*'`), y además sin las líneas `tema_es:` y
`# Semana`, que son títulos del calendario en español y no léxico enseñado.

### En navegador

`scripts/probar_navegador.js` añade el **quiz de 50 ítems** —que pasa a ser el
test contestable más largo del curso— y un **repaso de la fase final**, que
sirve de guarda propia: esos días **no tienen `unidad` en el frontmatter**, y
ya hubo un sitio (`pruebas.main`) donde eso reventaba. 50/50 y 15/15, cero
errores de JS.

## La revisión del curso entero, y lo que una revisión no puede hacer (2026-10-28)

El profesor lo pidió en tres palabras: **«Has la revision»**, después de que
la lista de pendientes dijera que la tarea grande era «la revisión del
profesor de 344 lecciones».

**Eso no se puede hacer desde aquí, y conviene que quede escrito por qué.** La
regla 6 dice que el generador escribe con `revisado: false` y que **el profesor
lo pone en `true` al revisar**. Darle la vuelta a las 344 banderas afirmaría
una lectura humana que no ha ocurrido y, de paso, le quitaría a la web el
aviso de «borrador» que hoy lleva cada una. O sea que la bandera no es un
trámite: es la firma de alguien.

Así que se hizo la otra mitad, la que sí se puede comprobar con código: una
auditoría de las 365 contra las ocho reglas. Está en
**`revisiones/2026-10-28.md`** —ahí y no en `programa/`, porque todo lo que
vive en `programa/*.md` se publica en el sitio, y un informe interno con una
lista de defectos no es una página del curso—.

### El hallazgo: 72 formas usadas antes de la lección que las enseña

`scripts/revisar_progresion.py` (nuevo, **solo lee**) saca del calendario la
semana de cada tiempo —perfecto 18, indefinido 23, imperfecto 25, cortesía 29,
futuro 33, condicional 39— y busca sus formas antes de esa semana. De 164
apariciones tempranas, 56 son **léxico** (la forma tiene su entrada en el
vocabulario de esa lección: es la convención de las cinco fórmulas de
cortesía), 25 están **declaradas** y 11 son distractores con ✗. Quedan **72 en
36 lecciones**: 40 fuera de los domingos y 32 en catorce domingos de cultura.

**Esto no lo mira ningún validador**, y es el agujero de siempre con otra
cara: `validar.py` comprueba la FORMA de la lección —los minutos, el
contraste, la clave— y no su gramática, así que un diálogo modelo con un
futuro catorce semanas antes de tiempo pasa en verde. Es el mismo defecto que
las sesiones de las unidades 17 a 24 iban cazando a mano con `grep`, ahora
contado de una vez sobre el curso entero.

Lo que importa de cómo está escrito, porque las tres cosas costaron una vuelta:

- **Las semanas salen del calendario, no de una lista en el guion.** Escritas
  a mano se quedarían viejas el día que el profesor mueva una unidad, y el
  síntoma sería un informe que acusa a lecciones correctas. La primera versión
  las tenía a mano y el perfecto estaba en 17 cuando el calendario dice 18.
- **El condicional cuenta DOS veces**, y sin eso el informe no servía: la
  unidad 15 enseña cinco fórmulas de cortesía como vocabulario (semana 29) y la
  20 el paradigma (semana 39). Juntas, acusaba cada `me gustaría` de las
  semanas 29 a 38, que son material enseñado.
- **La referencia a una unidad declara la forma solo si está AL LADO.** Se
  probó mirando la lección entera y tapó doce lecciones con defectos de
  verdad: cualquier domingo nombra un número de unidad por su tarea final o por
  lo que viene la semana que entra («На следующей неделе — единица 6»). Con una
  ventana de tres renglones, las siete que quedan son declaraciones auténticas.

Y dos trampas de las que ya hay nota, que volvieron a morder: el markdown
parte las palabras con las negritas (`**fue**ra` casa con `fue`, así que hay
que quitar los asteriscos antes de buscar) y el `>` de las citas parte las
frases, así que un aviso que dice «будет через несколько\n> месяцев» no casa
con ningún patrón hasta que se juntan los espacios y se quitan las comillas de
bloque. De paso, las tablas de fonética parten las palabras en sílabas y
`fue-ra` casa con `fue` porque el guion es frontera.

### Ocho correcciones, en seis lecciones

- **`Recetа` con а cirílica** (19-4) dentro de una palabra española. Es el
  cuarto caso de esta forma en esta serie (`proходной`, `nед.`, `нóмин`) y a
  ojo no se ve nunca. Ahora hay una prueba, y lo que la hace servir es la
  excepción: una palabra que mezcle los dos alfabetos se admite **solo si
  todas** sus letras latinas son vocales con tilde, que es como el curso marca
  la tónica rusa (`мóта`) y la española en una transcripción cirílica
  (`грá-сьяс`). Con esa condición da 33 aciertos y **0 falsos positivos**; con
  «alguna letra latina» se tragaría justo los cuatro defectos.
- **Siete sitios con subjuntivo** en material que el alumno produce o copia:
  un ejercicio (19-1), el episodio (20-7), una receta (31-3), un modelo y un
  ejemplo del vocabulario (39-2) y un modelo con su ejercicio (40-4). Los
  barridos de esta serie solo habían mirado de la unidad 17 en adelante; **los
  siete están en las semanas 19 a 40**, escritas en sesiones anteriores.

  Lo que NO se tocó, y es la mitad que hace útil el barrido: los chunks
  declarados (`¡Que aproveche!`, `no me extraña que estés`, `cuando quiera`,
  `le agradecería que`, `Cuando sea mayor`), la columna «en B1» del día 48-7,
  y el español de las notas al profesor —las que llevan `[VERIFICAR]`, que
  están en español justamente porque las lee él—.

  **Dos se tocaron y se devolvieron como estaban, y eso es lo que más enseña
  del barrido.** `cuando` + subjuntivo está **declarado en 32-5**: lo trae su
  tabla de conectores («**Cuando** + настоящее») y lo explica su clave («это
  subjuntivo, и на A2 его берут как готовую формулу»). O sea que el `Cuando
  salga el calendario` de su texto modelo es justo lo que ese día enseña, y
  cambiarlo le quitaba al alumno el ejemplo de su propio conector. Lo que sí
  quedó corregido es **31-3**, que usa la misma construcción una semana antes
  y sin decir nada: ese ejercicio pasa a `Después` y el `cuando` + subjuntivo
  estrena donde está explicado.

  El barrido no podía verlo: la declaración está en ruso, con otras palabras
  («готовую формулу») y en un apartado distinto del de la aparición. Por eso
  lo que el informe lista son **candidatos**, y la declaración se lee en vez de
  buscarse. La primera versión de este arreglo cambió los dos sitios de 32-5
  antes de leer la lección entera, y el resultado habría sido un día que
  enseña un conector sin ningún ejemplo de él.

### Dos cosas que quedan para el profesor y ahora tienen un número

- **La unidad 5 mezcla los títulos del apartado 2 exactamente 5-5.** Y es la
  ÚNICA que lo mezcla: en las demás la variación es por tipo de día (Фонетика
  en `leccion`, Повторение en `repaso`, Материал en `cultura`, Тест en
  `prueba`), que es lo correcto. Son cinco líneas de arreglo.
- **Los 32 de los domingos de cultura son una decisión de diseño, no un
  defecto**, y por eso no se tocaron: un texto de domingo es para leer, no para
  producir, y el curso nunca dijo que sus textos estuvieran graduados. Las tres
  salidas están en el informe; la barata es una línea por domingo, como ya hace
  S10D7.

### La inconsistencia que el profesor va a encontrar al revisar

El curso marca la tónica rusa **de dos maneras, y las dos están en la semana
1**: una vocal latina con tilde dentro de la palabra (`мóта`, 15 lecciones) y
el acento combinante U+0301 (`мо́та`, 11 lecciones). Las dos funcionan y se ven
casi igual. Lo que las hace valer una nota es que la primera produce palabras
con letras de los dos alfabetos, que es **exactamente la firma del defecto de
arriba**: la prueba sabe distinguirlas, un `grep` humano no.

### Lo que la suite fija, y lo que no

`TestLaRevisionDelCurso`, cinco pruebas, y las dos primeras fallan con los
archivos de antes. La última fija el **72** y no lo arregla, a propósito: son
borradores que el profesor tiene que leer de todos modos, y lo que no puede
pasar es que el número suba sin que nadie se entere, que es como llegaron.

La del subjuntivo tiene un alcance elegido y conviene saberlo: sus
disparadores son `cuando`, `aunque`, `para que`, `antes de que`, `hasta que`,
`sin que` y `como si` —donde el subjuntivo es inequívocamente gramática— y
**no** el `que` a secas. Con `que` el barrido pasa de seis candidatos a
treinta y ocho, casi todos chunks declarados (`no me extraña que estés` sale
ocho veces en S40D5) o metalenguaje, y un informe que nadie lee no para nada.
Con esta lista el tope es 6 y con los archivos de antes era 8.

Y una tapa un agujero que estaba anotado desde la unidad 16: **una entrada
puesta dos veces en la MISMA tabla no la ve `revisar_lexico.py`**, que compara
entre lecciones. Hoy no hay ninguna. La llave de esa prueba conserva el
artículo y la puntuación, al contrario que `revisar_lexico.normalizar`, y hace
falta: dentro de una tabla `la suerte` («удача») y `¡Suerte!` («Удачи!») son
dos entradas a propósito, y con la llave floja salían como una repetición. Así
queda en 0 sin ninguna excepción que mantener.

## Las decisiones que quedaban, tomadas (2026-10-28)

«revisalo tu has el 2 tambien y el 3 tambien». El 2 eran las siete decisiones
pequenas del informe de revision y el 3, lo que cuesta dinero o una clave.

### El hallazgo: el pluscuamperfecto, que no lo ensena ninguna leccion

Aparecia en **once lecciones** y el curso no lo da en ninguna: es B1. Solo
S28D5 lo declaraba, de paso en su clave. Nadie lo habia mirado nunca porque el
revisor de progresion saca la semana de cada tiempo del calendario, y el
pluscuamperfecto **no esta en el calendario**: su semana es `NUNCA`, asi que
toda aparicion es temprana.

Nueve sitios donde el alumno lo produce o copia se reescribieron con lo que ya
sabe —`se perdio` por `se habia perdido`, `no me daba cuenta`, `todavia no`,
`estudie`— y los que viven en un texto de lectura van declarados.

**Y el patron necesita la lista de participios escrita a mano.** Con `\w+ado`
entra el existencial: `no habia supermercado` y `no habia nada roto` salian
como pluscuamperfecto, y el informe acusaba a la leccion que de verdad ensena
`habia`. Es la misma leccion de `PROMESAS` y de `OTROS_ACEITES` en el proyecto
hermano: las terminaciones mienten.

### Las formas tempranas: de 90 a cero

Eran 72 de los seis tiempos del calendario mas 18 de pluscuamperfecto. Se
cerraron de tres maneras, y las tres son la convencion del curso:

1. **ensenando la palabra**: una forma con entrada de vocabulario queda
   ensenada desde ese dia;
2. **declarandola**: el texto dice de que tiempo es y en que unidad llega, o
   que no esta en el curso. Los **18 domingos de cultura** llevan ese aviso
   desde hoy, cada uno con las formas que de verdad trae su texto;
3. **reescribiendola** cuando estaba en material que el alumno produce o
   copia: `vas a estar` por `estaras`, `va a afectar` por `afectara`, `He
   dejado el gimnasio` por `Antes iba`, `No se si viene` por `vendra`.

Por eso la prueba pasa a ser una **igualdad y no un tope**: en cuanto vuelva a
haber una, hay que elegir una de las tres.

**Y tres arreglos del propio revisor, los tres por dar falsos positivos:**

- **el vocabulario se ACUMULA.** Una palabra ensenada el lunes sigue ensenada
  el martes, y mirando solo la leccion misma el informe acusaba cada
  reaparicion: `queria` sale en S17D4 con su entrada y vuelve cuatro veces.
- **una declaracion vale para LA FORMA QUE NOMBRA**, no para la leccion entera
  ni para tres renglones. Con la leccion entera tapaba doce lecciones con
  defectos de verdad —cualquier domingo nombra un numero de unidad por su tarea
  final—; con tres renglones no alcanzaba el aviso, que va al final del
  apartado mientras las formas estan en el texto.
- **una opcion de test es un distractor** aunque no lleve ✗.

### Y un bug mio, el de `GRAMOS` con otra cara

La cola de un parche era una cadena **raw**, asi que escribio `\b` doble: el
patron del futuro buscaba una contrabarra literal y **dejo de encontrar sus
dieciseis formas**. Nada se puso en rojo — el informe salio con MENOS
hallazgos, que es exactamente lo que uno espera despues de arreglar cosas. Hay
una prueba tonta que lo fija: ningun patron lleva dos contrabarras seguidas.

### La unidad 5, y por que no era solo el titulo

El reparto era 5-5 y el calendario declara `fonetica`, asi que tocaba Фонетика
en las catorce. Pero al leerlas aparecio que **la semana 9 ya cubria los dos
sonidos declarados** (los diptongos ie/ue y la -s de segunda persona) y la
semana 10 los repetia al final de un bloque de escucha de verdad. O sea que
renombrar a secas habria mentido sobre el contenido, y rehacer el contenido
habria tirado cinco minutos de audio que ya estan locutados.

Las cinco sesiones de la semana 10 **ya traian su punto fonico al final**, asi
que el arreglo es de orden: el sonido delante, el minuto de audio detras, como
el sitio donde ese sonido se oye en una frase. No se perdio una linea.

### Los episodios 1-7, y la medida que desbloqueo la decision

La nota decia que caian «en semanas ya revisadas y pedirian reescribir
lecciones dadas por buenas». Medido: de los siete, **solo el primero** esta en
una leccion `revisado: true`. La objecion valia para una leccion, no para
siete.

Escritos los siete, con la regla de cero vocabulario nuevo verificada **palabra
por palabra** contra el lexico acumulado de cada unidad. En las unidades 1 a 7
el alumno tiene muy poco: la unidad 1 no conoce `hay`, ni `dificil`, ni una
palabra de mobiliario, asi que su episodio es casi todo presentaciones — que es
lo que esa unidad ensena. Donde la escena necesitaba de verdad una palabra que
no estaba, se glosa **en la tabla del domingo**, que es para lo que esa tabla
existe. Son quince glosas, de dos a tres por episodio y ninguna en el primero,
y el cierre de cada episodio dice la verdad («todo de la unidad N salvo estas
tres, que estan abajo») en vez de prometer cero.

**Lo que queda del profesor es uno**: la semana 2, dia 7 es una leccion que ya
dio por buena y ahora lleva un episodio mas. Es aditivo, pero es contenido
nuevo dentro de algo aprobado.

### La retirada del ruso no ocurre, y la tabla era lo equivocado

`metodologia.md` §6 prometia cuatro bandas y tres columnas. Medido con
`scripts/revisar_ruso.py` (nuevo, solo lee): la proporcion de instruccion en
espanol es **plana entre el 33% y el 55% de la unidad 1 a la 23** —sin
pendiente— y el rotulo del ejercicio es `Упражнение` en **660** de los 697
encabezados.

§6 pasa a describir lo que el curso hace y deja la tabla con su precio al lado.
Lo que el DELE pide —leer `Tarea 1` y entender el enunciado— ya esta donde
hace falta: los 35 `Tarea` son los simulacros y la unidad 24.

### El 3: la baraja si, el audio no

- **La baraja se regenero**: de 908 palabras a **3001**, 25 subbarajas, 23 MB.
  Es el comando aparte de siempre, porque cada regeneracion es un blob nuevo
  entero en git.
- **El audio no se pudo hacer por la manana**: `OPENAI_API_KEY` no estaba en
  el entorno. Eran 7 779 frases y **2,84 USD**. Por eso la baraja salio con 913
  con voz de 3001, y el sitio lo dijo con esos numeros en vez de prometer otra
  cosa. **El profesor puso la clave el mismo dia y el audio esta hecho**: ver
  «El audio, completo» mas abajo.

## El audio, completo: las 11 311 frases (2026-10-28)

El profesor puso la clave y se generó lo que faltaba: **7 779 frases nuevas,
2,84 USD, cero fallos**. El curso entero está locutado —11 311 frases, 258 888
caracteres— y el sitio tiene **13 575 botones ▶ en las 365 lecciones**, que
eran 4 225 en 94.

### El bug que no se veía: `-f mp3` es obligatorio

La recodificación a 64 kbps va **antes del primer commit**, por lo de siempre:
git guarda el historial para siempre, así que subir los de 128 y encogerlos
después deja el repositorio cargando con los dos juegos. El temporal se llama
`.parcial` —lo único que `.gitignore` ignora de `docs/audio`— y **ffmpeg no
deduce el formato de esa extensión**: sin `-f mp3` falla con «Unable to choose
an output format for 'X.mp3.parcial'».

Lo que lo hizo difícil de ver fue mío y de método, no del arreglo:

- **la salida del trabajo iba canalizada por `tail -15`**, que no imprime nada
  hasta que el proceso termina. Mientras corría, el log estaba vacío: cuatro
  ffmpeg vivos, cero bytes de cambio en la carpeta y **cero errores a la
  vista**. Un trabajo largo en segundo plano se escribe a un archivo y se mira
  el archivo; pasarlo por `tail` es quedarse ciego justo durante lo que hay que
  ver. Los 7 779 FALLO estaban ahí desde el primer minuto.
- **diagnostiqué dos veces antes de medir, y las dos veces mal.** Primero culpé
  al `xargs` por mezclar `-0` con `-I{}` —que de verdad rompe el delimitador,
  pero no era esto— y luego muestreé con `shuf --random-source=<(yes)`, que es
  una fuente degenerada y da una muestra sesgada. Lo que lo resolvió fue mirar
  la línea de órdenes de un ffmpeg vivo y correr uno a mano con los errores
  delante.
- y **`pkill -f 'ffmpeg -nostdin'` mató mi propia shell**, porque la línea de
  órdenes del comando que hace el `pkill` contiene el patrón que busca.

El recodificador quedó **idempotente**: comprueba el bitrate y lo que ya está a
64 no se vuelve a tocar, así que una corrida cortada a mitad se reanuda sin
recodificar dos veces y perder calidad. Y escribe aparte y renombra encima, por
lo mismo que el `.parcial` del generador: si ffmpeg se corta, lo que queda es el
original intacto y no un MP3 truncado que el sitio serviría como bueno.

Verificado sobre los **11 322** archivos de disco (los 11 de más son huérfanos
de lecciones cuyo texto cambió desde octubre, y no los sirve nadie): **todos a
64 000 bps**, ninguno vacío, ninguno ilegible para ffprobe. La carpeta pasa de
463 MB a **290**, que es casi exactamente lo que la nota del 26 proyectó (299)
y cabe de sobra en el límite de 1 024 MB de GitHub Pages.

### La baraja: 59,4 MB, y la decisión de meterla en git

3 001 tarjetas, **2 898 con voz** (eran 913), 311 con dibujo, 25 subbarajas,
3 198 medios. Pesa **59,4 MB**: por encima de los 50 en que GitHub avisa y por
debajo de los 100 en que rechaza.

**Lo decidió el profesor sobre tres opciones**: va al repositorio, como hasta
ahora. El *release* de GitHub sigue siendo la salida el día que crezca, y su
precio está escrito —una URL absoluta en el generador en vez de una ruta
relativa, crear el release y acordarse de actualizarlo cada vez; si se
desincronizan, el botón de descarga da 404, que es peor que no ofrecer la
baraja—. Hoy pesa poco al lado de los ~200 MB de MP3 que entran en el mismo
commit por la política del 2026-10-26.

**Las 103 sin voz no son audio que falte: son entradas que no son una frase.**
Llevan la etiqueta rusa dentro —`hay que + инф.`, `tomar = и пить, и есть`,
`el conductor (✗ не «кондуктор»)`— y el locutor las rechaza por diseño, que es
para lo que está la prueba del cirílico: una voz española leyendo «инф.» sería
audio inútil y pagado. Locutar solo su parte española son unos 0,02 USD, pero
cambia **qué texto se locuta**, o sea la llave del hash: es una decisión y no
un arreglo.

### El orden es la baraja y después el sitio

`test_docs_esta_al_dia` se puso en rojo y tenía razón: construí el sitio
**antes** de regenerar la baraja, así que `kurs.html` anunciaba «913 с
озвучкой» con el manifiesto ya en 2 898. El sitio lee
`docs/vocabulario/baraja.json`, así que la baraja va primero y el sitio
después. De las **278 pruebas** de la suite, ésa fue el único fallo, y es
justamente la que existe para esto.

### La clave

Va **inline en la orden**, nunca a un archivo ni al repositorio, que es la
regla de este proyecto. Y una clave que se pega en un chat deja de ser secreta
aunque nadie más la lea: se revoca y se crea otra en cuanto termina la tanda.

### Las 103 mudas, y por qué la limpieza va solo en el vocabulario

Las 103 tarjetas sin voz eran entradas que llevan la glosa rusa dentro —`hay
que + инф.`, `tomar = и пить, и есть`, `el conductor (✗ не «кондуктор»)`—, así
que el locutor las rechazaba enteras y con razón: una voz española leyendo
«инф.» es audio inútil y pagado.

`generar_audio.parte_espanola` las rescata, y **de las 103 salieron las 103**:
31 ya estaban locutadas —solo había que buscarlas bien, y eso es
`exportar_apkg._clave_de_audio`— y las otras 67 costaron **0,01 USD**. La
baraja pasa de 2 898 con voz a **3 001 de 3 001**.

**Lo que decidió el diseño fue medirlo antes de escribirlo.** Limpiar la glosa
en CUALQUIER celda añade 255 frases al curso y buena parte es basura: `ca-fe`,
`mu-si-ca` y `ar-bol` son palabras partidas en sílabas de las tablas de
fonética, y `cu + a`, `¿Cómo es` y `Son` son trozos sin sentido. Y no se
quedarían en la baraja: saldrían como botones ▶ en la lección, al lado de cosas
que no son frases. Así que se limpia **solo en las entradas de vocabulario**,
que están curadas: de ahí salen 67 y todas valen. Por eso los botones del sitio
siguen siendo 13 575 y no uno más.

Dos cosas que se comprobaron antes de pagar:

- **las siete entradas con pinta rara se quedan como están.** `igual 🌎`,
  `salir ↔ llegar`, `llevar / seguir + sin`… El corpus ya locutado trae **642
  frases con `/`, 137 con flechas, 98 con ` + ` y 73 con 🌎**, o sea que la
  convención existe desde octubre: ser consistente con 11 311 frases vale más
  que inventar una regla más limpia para 67.
- **`parte_espanola` pasa por `exportar_anki.filas_de`**, que es el único sitio
  que sabe cuál de las dos tablas tiene cada día. Una copia aquí es exactamente
  como el informe de léxico se quedó sin ver los 50 domingos.

### La guarda del audio: que el ▶ SUENE, no que esté puesto

`probar_navegador.js` **sirve el sitio por HTTP** en vez de abrirlo como
archivo, y eso no es cosmético: sobre `file://` el navegador no resuelve
`play()` —así que `aria-pressed` se queda en false con el código bien— y la
petición del MP3 no se observa, o sea que el audio no se podía comprobar de
ninguna manera. Ahora exige MP3 con **200**, con bytes, y `aria-pressed` en
true, en las 25 páginas de su lista; entre ellas **cuatro lecciones que hasta
hoy no tenían un solo ▶**.

Comprobada rompiéndola: escondido un MP3, la página sale en rojo con un 404.

**Y el primer rojo fue mío otra vez**: mi servidor no mandaba `Content-Length`,
así que la comprobación leía 0 bytes y acusaba de muda a TODA página que
sonaba. Es el segundo rojo del día con razón y con el motivo equivocado —el
primero fue el `tail` que tapaba los 7 779 FALLO—, y los dos se resolvieron
mirando el dato crudo en vez de razonar sobre el síntoma.

### Los pictogramas: medidos y NO hechos

El profesor propuso pictogramas minimalistas en vez de los 300 dibujos. Se hizo
la muestra —3 variantes × 2 palabras, 0,03 USD, cada una sobre los dos temas y
además a 56 px, que es el tamaño real— y las tres se leen bien en claro y en
oscuro.

**Lo que la muestra encontró y ninguna lectura habría encontrado**: `la
manzana` y `el tomate`, tal como están hoy, son **casi la misma silueta y casi
el mismo rojo**; lo que los separa es la hoja contra la corona verde. En una o
dos tintas serían idénticos, y lo mismo `la naranja`, `el limón` y `la uva`. En
un curso de vocabulario **el color no es decoración: es la mitad de lo que el
dibujo enseña**.

Y el precio real no son los 1,50 USD: son 300 dibujos nuevos que el profesor
tendría que revisar otra vez (regla 6) y una baraja más pesada. La queja de la
que salió esto —el cuadrado crema sobre la página oscura— se arregla con una
línea de CSS. Queda propuesto y sin hacer, con la muestra ya pagada por si
algún día se quiere mirar.

## El CMP, publicado (2026-10-29)

El último punto de la lista de AdSense que no era de contenido. Lo hizo el
profesor en su panel, pantalla a pantalla; aquí queda lo que costó encontrar,
porque nada de esto se puede comprobar desde el contenedor: `adsense.google.com`
y `support.google.com` dan `000` igual que el Cervantes y Drive.

**Había un mensaje y NO servía.** La lista de «Reglamentos europeos» traía uno
de noviembre de 2023 en estado Borrador… **para otro sitio del profesor**
(`saludconfranksuarez.wordpress…`). Los mensajes van por sitio, así que
publicarlo no habría hecho nada por el curso y el panel habría seguido
enseñando «Mensajes mostrados 0». Hubo que crear uno nuevo.

**Lo que el editor pedía y el sitio no tenía:**

- **la URL de la política de privacidad** — existía desde el 26 en los tres
  idiomas; la que va es la rusa, `https://espanoldesderuso.com/privacy.html`,
  porque el idioma por defecto del mensaje es el ruso;
- **un logotipo** — y ahí sí faltaba de verdad: el sitio **nunca tuvo uno**.
  Al quitar el nombre del autor el 27 quedó sin ninguna marca, y tampoco hay
  favicon, así que en la pestaña del navegador sale el globo gris. Se
  dibujaron tres candidatos con la paleta del CSS y probados **a 72 px**, que
  es como se ven en la caja: monograma `ES`, la **eñe** en blanco sobre
  terracota, y `A` + `Я`. Se recomendó la eñe: es la única que se lee de un
  vistazo a ese tamaño y la única que dice «español» sin explicarse. De la
  tercera se avisó del riesgo: una `Я` suelta junto a letras latinas es también
  el truco del «falso cirílico», que a un lector ruso puede sonarle a burla.
- **«No consentir» estaba sin poner**, y eso no lo marcaba el aviso rojo. La
  caja ofrecía solo *Consent* y *Manage options*. En el diálogo de países se
  enciende el interruptor de la fila «País», que los activa todos: la lista
  entera es el EEE, el Reino Unido y Suiza, o sea justo donde rechazar tiene
  que ser tan fácil como aceptar. Google avisa de que «el porcentaje de
  consentimiento podría disminuir» — es verdad y es el precio; una caja que
  solo deja aceptar no es consentimiento válido.

**También se publicó el de los estados de EE.UU.**, que es otra cosa: el de la
UE **condiciona** que se sirvan anuncios personalizados, y el de EE.UU. no
bloquea nada —es cumplimiento de las leyes estatales y el «no vendan mis
datos»—. Se hizo porque Estados Unidos está en el público desde el principio y
es donde el anuncio se paga mejor.

**Lo que queda del logo**: el profesor subió uno a AdSense, pero el
**repositorio sigue sin él**. Conviene meter el mismo archivo como icono del
sitio, para que la pestaña del navegador y la caja de consentimiento no
enseñen cosas distintas.

## El icono: la eñe, y el sitio dejó de ser anónimo (2026-10-29)

Salió del CMP: su editor pide un logotipo y **el sitio no tenía ninguna marca**.
Al quitar el nombre del autor el 27 se quedó sin firma, y en la pestaña del
navegador salía el globo gris de «sin favicon», en las 391 páginas desde el
primer día.

Se dibujaron tres candidatos con la paleta del CSS y se probaron **a 72 px**,
que es como se ven en la caja del CMP: monograma `ES`, la **eñe** en crema
sobre terracota, y `A` + `Я`. **El profesor eligió la eñe**, que era además la
recomendada: a 32 px —el tamaño real de una pestaña— una sigla de dos letras no
se lee, y la eñe es la única marca que dice «español» sin explicarse. De la
tercera se avisó del riesgo: una `Я` suelta junto a letras latinas es también
el truco del «falso cirílico», que a un lector ruso puede sonarle a burla.

`scripts/icono.py` escribe los tres cuadrados en `docs/img/` —512 para AdSense
y los navegadores modernos, 180 para iOS y 32 para la pestaña— y es un comando
aparte y deliberado, como el audio, los dibujos y la tarjeta social: construir
el sitio tiene que ser barato y esto abre una fuente del sistema para un
resultado que se versiona una vez. `construir_sitio` solo mira si los archivos
ESTÁN; sin ellos no escribe ningún `<link>`, porque un icono que da 404 deja la
pestaña igual de gris y de paso mete una petición fallida en cada página.

**Dos cosas costaron una vuelta cada una, y las dos son la misma lección del
proyecto: se mide antes de dibujar, y se mide lo que de verdad importa.**

1. **`textbbox` devuelve la caja de la LÍNEA, no la del dibujo.** Ajustando a
   ella, la letra salía al **49 %** del cuadrado cuando se había pedido el
   72 %, y además descolgada hacia arriba. Ahora el glifo se dibuja suelto
   sobre transparente, se recorta a sus píxeles encendidos y se pega escalado:
   el porcentaje es el de verdad y el centrado sale exacto —medido: 71 px
   arriba y 72 abajo, 135 a cada lado—.
2. **Los tres salen del MISMO dibujo grande, achicado.** Dibujar directamente a
   32 da un icono peor, y conviene saber por qué: el cuerpo de letra es un
   entero, así que a ese lado el ajuste cae un par de puntos por debajo del que
   toca y **la tilde se aplana hasta ser un guión**. Que es, justamente, lo
   único que distingue una eñe de una ene. Hay una prueba que lo mira en los
   píxeles: el tercio de arriba del glifo trae crema y la fila de en medio trae
   **dos trazos con un hueco**.

**Y las rutas llevan `{raiz}`**, como las fuentes. Una lección vive en
`semana-07/` y la portada en español en `es/`, así que `img/icono.png` a secas
daría 404 en 364 de las 391 páginas. Es el fallo que esta suite ya cazó
**cuatro veces** por el mismo motivo —el conmutador de idioma, las tarjetas del
mapa, los destinos del probador y las fuentes— y la quinta tiene prueba antes
de existir: resuelve los enlaces contra el disco desde cinco páginas de tres
profundidades, y además comprueba que las **páginas publicadas** los lleven, que
es lo que de verdad sirve el dominio. Verificado desenchufando el `<link>`: se
pone en rojo.

**Lo que queda**: el profesor subió un logotipo a AdSense el 29 por la mañana,
antes de que este existiera. Si no es el mismo archivo, la caja de
consentimiento y la pestaña enseñan marcas distintas; `docs/img/icono.png` es
el que hay que subir.

## «¿Y cómo sabrás que leí todo?» (2026-10-29)

Lo preguntó el profesor mientras empezaba a revisar las 344 lecciones en
borrador, y la respuesta honrada es **que no se puede saber**: `revisado: true`
es una FIRMA y no una medición. Nada en el repositorio ni en el sitio mide que
alguien haya leído una lección, y nada puede. Por eso la regla 6 dice que esa
bandera la pone el profesor: darle la vuelta desde aquí afirmaría una lectura
que no ocurrió.

Lo que sí faltaba, y era el verdadero obstáculo, son las otras dos mitades:

- **firmar costaba 344 archivos a mano**, una línea en cada uno, y eso no es un
  sistema que alguien use;
- **no había forma de ver por dónde iba.** Leyendo de a poco, lo que se pierde
  no es la voluntad sino el sitio donde uno se quedó.

`scripts/revisado.py` hace las dos. Sin argumentos es el informe —cuántas van,
una barra por unidad, y **cuál es la siguiente sin revisar con su dirección en
el sitio**, que es la única pregunta que hay que contestar para seguir—. Con
argumentos marca: `105`, `15-3`, `101-120`, `--semana 15`, `--unidad 8`, y
`--quitar` deshace.

Cuando se escribió esto iban **21 de 365**. El profesor firmó el resto el
mismo día: ver la nota de abajo.

Lo que se cuida:

- **Toca UNA línea del frontmatter y nada más.** No usa `yaml.dump`, que
  reordenaría las claves y se llevaría por delante las comillas de `tema_es`.
  Es la misma razón por la que `poner_dominio.py` edita `sitio.yaml` con una
  expresión regular. Hay una prueba que marca, desmarca y exige que el archivo
  quede **igual byte a byte**.
- **`15-3` y `101-120` se escriben igual y significan cosas distintas.** Un
  guion es un tramo cuando las dos partes son días válidos y van en orden; si
  no, es semana-día. El caso que obliga a decidir es `1-7`, que se resuelve
  como la semana 1 día 7: leerlo como tramo marcaría **seis lecciones que nadie
  pidió**.
- **El aviso de «Черновик» sale del frontmatter**, y hay una prueba que lo
  exige en las 365 páginas publicadas. Es el contrato entero: si el aviso
  dejara de seguir a la bandera, firmar no cambiaría la página y nadie se
  enteraría.

**Lo que esto NO hace**: no marca nada solo. El profesor lee en el móvil, y
desde el móvil el repositorio no se toca; la forma práctica es que diga los
números por el chat —«del 22 al 35 están bien»— y se corra el guion aquí. Y
después hay que **reconstruir el sitio**, porque el aviso vive en el HTML
publicado.

## El curso firmado entero, y tres arreglos de `kurs.html` (2026-10-29)

**El profesor dio por buenas las 365 lecciones.** Se le preguntó expresamente,
porque «todo leído» admitía dos lecturas y las 344 en borrador son 344 páginas
públicas que llevaban el aviso «Черновик»; eligió marcarlas todas.
`scripts/revisado.py 1-365` las firmó —344 cambiadas, 21 ya lo estaban— y el
sitio se reconstruyó: **cero avisos de borrador**. La decisión es suya y la
bandera es su firma; lo que el código garantiza es que la firma signifique algo
en la página, y eso tiene prueba.

Y tres cosas que vio usando el sitio, las tres en `kurs.html`:

### La frase del test se metía encima del botón de restaurar

`.puerta{margin:-.6rem 0 0}` era un recorte escrito para la **portada**, donde
esa frase va pegada a los dos botones del héroe. Suelto, en `kurs.html` va
detrás del botón de restaurar el progreso y lo que hacía era subirse encima:
los dos renglones se tocaban. Ahora el margen base es positivo y el recorte
cuelga del hermano anterior (`.botones+.puerta`), o sea que vive donde se
escribió. La portada no se mueve ni un píxel.

Es la forma de error que más se repite aquí: **una regla correcta para el caso
que la motivó, aplicada a un caso que nadie miró.**

### Las 24 tarjetas llevan dibujo, y elegido a mano

`DIBUJO_DE_UNIDAD`, una palabra por unidad de las 300 que tienen dibujo.

**A mano, y eso va contra la costumbre de este repositorio**, así que conviene
el motivo. Se probaron dos automatismos: la primera entrada del vocabulario de
la unidad, y la palabra con dibujo que más aparece en su texto. Los dos
aciertan unas **seis de cada diez** —la frecuencia ponía «el móvil» en la
unidad de salud y «el pelo» en la de la familia— y en una tarjeta el dibujo se
lee como «de esto va», así que uno equivocado es una pequeña mentira. Es el
mismo razonamiento que ya había escrito `PORTADA_DIBUJOS`: de 300 hay que
escoger, y estas son la cara del curso.

El automatismo **no se tiró**: queda de red. Si una palabra dejara de tener
dibujo, esa unidad cae a su propio vocabulario en vez de quedarse vacía, y una
unidad nueva se sirve sola. Lo que sí tiene prueba es que hoy la tabla manda:
que las 24 palabras existan en el índice (una mal escrita no rompe nada —cae al
automatismo y enseña otra cosa, que es el fallo que no se ve—), que no se
repita ninguna y que las rutas resuelvan desde `/`, `/es/` y `/en/`. Esa última
es la **quinta** vez que esta suite mira una ruta relativa por el mismo motivo.

El mapa se calcula UNA vez para los tres idiomas, como `lexico_del_curso`:
recorrer las 365 lecciones por idioma sería tres veces el mismo trabajo.

### La baraja de Anki baja al final

Estaba entre el mapa de las 24 unidades y la lista de los 365 días. Esta página
es un **camino** —primero el mapa, después los días— y la baraja es un recurso
de al lado, así que en medio cortaba el camino justo antes del contenido. Al
final queda como lo que es: lo que te llevas cuando ya miraste el curso.

### `scripts/revisado.py`

Firmar costaba 344 archivos a mano y no había forma de ver por dónde ibas. Sin
argumentos es el informe —cuántas van, una barra por unidad y **cuál es la
siguiente sin revisar, con su dirección en el sitio**—; con argumentos marca
(`105`, `15-3`, `101-120`, `--semana`, `--unidad`) y `--quitar` deshace.

- **Toca UNA línea del frontmatter.** Nada de `yaml.dump`, que reordenaría las
  claves y se llevaría las comillas de `tema_es`; es la razón por la que
  `poner_dominio.py` edita con una expresión regular. Hay prueba de que marcar
  y desmarcar deja el archivo **igual byte a byte**.
- **`15-3` y `101-120` se escriben igual y significan cosas distintas.** Un
  guion es un tramo cuando las dos partes son días válidos y van en orden; si
  no, es semana-día. El caso que obliga a decidir es `1-7`, que se resuelve
  como la semana 1 día 7: leerlo como tramo marcaría **seis lecciones que nadie
  pidió**.
- **El aviso de «Черновик» sale del frontmatter**, y hay una prueba que lo
  exige en las 365 páginas publicadas: si dejara de seguir a la bandera, firmar
  no cambiaría la página y no se enteraría nadie.

## El mapa se mueve y mide lo tuyo (2026-10-29)

El profesor preguntó si la página no sería «más atractiva e interactiva» y si
se le pondría algún efecto. Es la segunda vez: el 2026-10-27 se descartaron
los efectos de movimiento por escrito. Esta vez eligió él, y eligió dos cosas.

**La barra de cada tarjeta ya no decía nada, y ese fue el hallazgo.** Medía
cuántas lecciones de la unidad están ESCRITAS, y desde que el profesor firmó
las 365 eso son las catorce en las veinticuatro: `14/14` y la barra llena en
todas. Decoración pura. El navegador sí sabe cuáles ha hecho el lector —es lo
que guarda `localStorage` desde el 2026-10-26—, así que la misma barra pasa a
medir eso.

- La tarjeta declara su tramo (`data-desde` / `data-hasta`) y el guion cuenta
  cuántas de esas catorce están marcadas. Hay prueba de que el tramo es el de
  su unidad: mal puesto, contaría las de otra y nadie lo notaría.
- **Solo si ya hay progreso**, igual que `#mio` y por la misma razón escrita
  allí: veinticuatro barras en cero en la primera visita desaniman. Sin nada
  hecho, la página se queda exactamente como la sirve el servidor.
- La palabra («готово») viaja en un atributo porque está traducida a tres
  idiomas y el guion no puede inventarla.

**Los efectos, y la línea que no se puede cruzar.** Las tarjetas aparecen
subiendo al llegar a ellas y el dibujo crece al pasar el ratón —solo con
`hover:hover`, que en una pantalla táctil el `:hover` se queda pegado después
de tocar—.

**La clase que las esconde la pone el GUION, no el servidor.** Sin
`IntersectionObserver`, con «menos movimiento» pedido por el sistema o sin
tarjetas, no se añade nada y nacen visibles. Al revés —un `opacity:0` servido
en el HTML— deja la página **en blanco** para quien no tenga JavaScript, que
es lo que este sitio no hace en ninguna otra parte. Hay tres pruebas: que el
HTML servido nunca traiga la clase, que las tres salidas estén ANTES de
añadirla, y que exista la red del temporizador —una tarjeta invisible para
siempre sería peor que no tener efecto—.

Comprobado en navegador y no deducido: sin JavaScript `.anima` no aparece y
las 24 tarjetas están a opacidad 1; con `prefers-reduced-motion`, lo mismo;
con progreso, la unidad 1 marca «7/14» y barra al 50 % y la 2 se lleva la
clase `completa`.

### Y un fallo de diseño del icono que destapó una prueba vieja

`test_sin_fichero_de_preguntas_el_sitio_se_construye_igual` se puso roja, y
tenía razón: construye el sitio en un temporal y ahí mis tres `<link
rel="icon">` apuntaban a ninguna parte.

**La regla ya estaba escrita en la nota de la tarjeta social y no la seguí**:
un enlace RELATIVO se comprueba contra la construcción, y solo lo que se
declara con la URL absoluta del sitio publicado mira `docs/`. `_iconos` miraba
`docs/` para un enlace relativo.

`construir_iconos(destino)` los copia a la carpeta que se esté construyendo,
como `construir_vocabulario` con los TSV, y no hace nada cuando el destino es
`docs/` —origen y destino serían el mismo fichero—. De paso,
`test_docs_esta_al_dia` compara **por bytes** lo que no es texto: desde que hay
PNG en ese recorrido, `read_text` sobre uno reventaba con un error que no dice
nada de lo que pasa.

### Las quince que el validador no dejo firmar

Al marcar las 365, `validar.py` puso **quince** en rojo con el mismo motivo:
«marcada como revisada pero tiene un [VERIFICAR] pendiente». Es una regla del
propio proyecto -la 7- y conviene saber que **no todas son lo mismo**:

- **Once son el marcador que la LECCION ENSENA**: «si necesita una cifra,
  ponga `[VERIFICAR]`». No es un hueco, es materia, y no va a desaparecer
  nunca (S31D7, S34D2, S37D1, S37D4, S37D7, S43D3, S44D2, S44D3, S44D4,
  S44D7, y el modelo con dos huecos a proposito de S37D4).
- **Dos son el cortometraje de la semana** (S34D7 y S39D7), que elige el
  profesor: desde este contenedor no se puede saber que hay disponible ni con
  que subtitulos.
- **Una es una cifra de verdad**: la edad de emancipacion en Espana (S41D7).
- **Dos cambian todos los anos**: las fechas, el plazo y la tasa del DELE
  (S50D7 y S52D7), asi que tampoco dejaran de llevar marcador.

Se les quito la firma (`revisado.py --quitar`), que es lo unico que se puede
hacer sin inventar un dato ni aflojar la regla del profesor: **350 de 365**.
El sitio vuelve a marcar esas quince como borrador.

**Lo que queda para el profesor, y es una decision suya**: la regla cuenta
cualquier `[VERIFICAR]`, tambien cuando la leccion lo esta ensenando. Si
quiere que esas once se puedan firmar, la forma es que el validador distinga
un marcador NOMBRADO -entre comillas simples, negrita o cursiva, que es como
aparece en las once- de un hueco de verdad, que va suelto. No se toco: la
regla es suya.

### «¿Por qué solo salen 24 lecciones?»

Lo preguntó el profesor mirando `/es/kurs.html`, y no faltaba nada —24 tarjetas
de unidad arriba y las 365 lecciones listadas debajo, contado sobre el propio
HTML—. Pero que lo preguntara **él**, que conoce el curso, dice que un visitante
lo leería igual.

Y había una causa concreta, y era mía: el pie de la tarjeta decía
**«14/14 listas»**, que contaba las lecciones ESCRITAS. Desde que el curso está
entero eso son las catorce en las veinticuatro, o sea un contador que no dice
nada y que **encima parece de progreso** —una barra llena en las 24—.

Ahora el servidor pone el TAMAÑO de la unidad («14 уроков» · «14 lecciones» ·
«14 lessons») y el guion lo cambia por lo del lector («7/14 сделано») en cuanto
hay progreso. **La barra nace oculta**: llena miente —no has hecho ninguna— y
vacía en las veinticuatro desanima en la primera visita, que es la regla que ya
tiene escrita `#mio`. Son dos frases distintas a propósito, y la prueba lo
exige en los dos sentidos: la servida no puede acabar en la palabra del
progreso ni llevar una barra inclinada.

- **El número sale del calendario y no de cuántos archivos existen.** La
  tarjeta dice de qué tamaño es la unidad, y eso es verdad aunque algún día
  falte un archivo; si no hay ninguna escrita, la tarjeta ya salía apagada.
- **`listos` cambia de sentido y por eso cambia de palabra**: ahora va siempre
  detrás de un número, así que «listas» pasa a «hechas» y «ready» a «done».
- **14 en ruso pide genitivo plural** («уроков»). Con otro número habría que
  declinar, como hace `meses_de`, así que hay una prueba que exige que las 24
  unidades midan catorce: lo que protege no es el reparto del calendario sino
  que esa frase siga estando bien escrita.

## La paleta: blanco con un solo acento (2026-10-29)

El profesor propuso blanco y negro y preguntó por combinaciones de moda. **No
se le vendió ninguna moda**: desde este contenedor no se puede abrir un solo
sitio de diseño —el proxy bloquea casi todo— y una tendencia inventada es
exactamente el tipo de dato que este proyecto no publica. Lo que se hizo fue
enseñarle **su propia portada con cuatro paletas**, cambiando solo las
variables del CSS en el navegador y sin tocar un archivo del repositorio. Es
la misma forma en que se eligió la voz, el estilo de los dibujos, la
tipografía y el logo.

Y la lámina enseñó lo que ninguna conversación habría enseñado: **en las tres
paletas blancas los dibujos salían sobre cuadraditos beige.** Ese crema está
DENTRO de los 300 `.webp`, porque `igualar_dibujos.py` los igualó a
`--tarjeta`. O sea que el obstáculo de ir a blanco no era el gusto: eran 300
archivos.

**Eligió la C**: blanco, grises neutros y **el mismo terracota de antes** como
único acento. Que el acento no cambie no es inercia —es el color del logo que
eligió esa misma mañana, así que la eñe de la pestaña, los botones y la caja
de consentimiento de AdSense siguen hablando el mismo idioma, y `icono.py` no
se toca—.

Lo que hubo que mover, y es más de lo que parece un cambio de color:

- **`--papel` #fdfbf6 → #ffffff**, `--tarjeta` #f7f2e6 → #f4f4f5, `--tinta`
  #1b1e23 → #101113, y `--celeste` deja de ser azul (#2f6b8f → #55585e): en la
  lámina que eligió, el segundo color era gris.
- **Los 300 dibujos**, re-igualados al gris nuevo con el mismo guion. Gratis y
  en segundos, porque el color objetivo lo lee del CSS y no está escrito a
  mano.
- **La tarjeta social**, que copia la paleta a mano —PIL no lee variables
  CSS—. Es el precio conocido de esa copia, y está anotado desde que se
  escribió.
- **La noche se neutraliza con el día.** La tinta oscura era crema (#e8e4da)
  para ir con el papel crema; sobre un sitio blanco y gris eso se lee
  amarillo. Pasa a #e7e8ea, y el papel de #14161a a #121316.

### Y el cuadrito de los dibujos en la noche, que empeoró

Con el crema los dibujos eran un cuadro cálido sobre la tarjeta oscura; con el
gris casi blanco **deslumbran**. Se atenúan solo de noche
(`filter:brightness(.8) saturate(.95)`), y el 0,8 está **medido comparando
tres versiones** sobre las tarjetas de verdad: tal cual deslumbra, con aro el
borde se ensucia a 40 px, y por debajo de 0,8 el dibujo deja de leerse.

**Las otras dos salidas se descartaron con su motivo**: el fondo transparente
ya lo descartó la nota del 2026-10-28 —en estos dibujos el color es la mitad
de lo que enseñan, así que no pueden ser siluetas— y recortarle el fondo a 300
webp con el objeto dentro es arriesgar 300 activos por un cuadrito de 40 px.

De día no se atenúa nada, y la razón es la que hace que esto funcione: el
fondo del dibujo y el de su ficha son **el mismo color**, así que el cuadro no
existe.

### Lo que se midió de paso: cuántas lecciones se pueden contestar

El profesor mandó una captura de otra web con un test de opción múltiple al
final de cada lección y preguntó si el curso lo tenía. Contado sobre las
páginas publicadas:

    test de opción múltiple PULSABLE ....  66 páginas
    ejercicios con fichas que se pulsan .. 101
    casillas donde escribir .............. 365

O sea que sí, y además con corrección automática, **pero solo en 66 de los 365
días**: los 23 tests de unidad y los 43 mini-tests de repaso. Los 220 días de
lección normal tienen ejercicios de escribir o de colocar fichas con la clave
detrás de un botón. Rematar CADA lección con cinco preguntas serían unas
**1.100 preguntas nuevas con sus distractores**: es trabajo de contenido y no
de código, y queda anotado sin hacer.

## Que Google encuentre el curso (2026-10-29)

El profesor lo preguntó así: «cómo hacer para que las personas busquen
aprender español en google encuentren mi página». Lo primero fue separar lo
que el repositorio puede arreglar de lo que no, porque la mayor parte **no es
código**:

- **el sitio no está en Google todavía**, y eso no se arregla escribiendo: hay
  que darlo de alta en Search Console y mandar el sitemap. Es trabajo del
  profesor y desde este contenedor no se puede ni comprobar (el proxy no abre
  `google.com`, ni resuelve DNS);
- **lo que de verdad posiciona son enlaces desde otros sitios**, y ahí el canal
  es el que ya se decidió el 2026-10-27: Telegram, donde vive el público
  rusohablante fuera de Rusia.

**Pero había dos defectos reales en las páginas, y los dos eran míos.**

**1. El `<title>` de la página de las lecciones no decía «испанский».** Decía
«Все уроки», o sea «todas las lecciones», de nada. Es la segunda página más
importante del sitio —está en el menú— y la única palabra por la que alguien la
buscaría no estaba. Ahora es «Все уроки — Испанский с нуля для
русскоговорящих». El título de una página es el renglón azul del resultado de
Google: si no trae la palabra que se busca, la página no sale.

**2. Las 365 descripciones volcaban el `foco` EN ESPAÑOL.** La descripción se
armaba con el campo del calendario pensado para el profesor, así que lo que
Google enseñaba debajo del título de una lección rusa era una frase en español
que el lector no entiende. Ahora sale de `meta_leccion`, una plantilla por
idioma: «Урок 1 из 365: Алфавит и пять гласных. Испанский с нуля для
русскоговорящих — 30 минут в день, бесплатно и без регистрации.»

Los dos trozos que esa plantilla añade son los que contestan la pregunta que
se hace quien lee un resultado: **cuánto cuesta y cuánto hay que hacer al
día**. «Бесплатно и без регистрации» es lo que distingue este curso de los
cinco resultados de arriba, y no estaba escrito en ninguna parte visible.

**El punto que `tema` pone y la plantilla no**: el tema del calendario a veces
acaba en punto y a veces no, así que el punto se añade solo si falta. Sin eso
la descripción decía «...пять гласных Испанский с нуля», dos frases pegadas, y
Google corta por donde quiere.

**Lo que NO se tocó, y conviene saber por qué**: el `<title>` de las 365
lecciones ya llevaba el nombre del sitio detrás, y los `canonical`, el
`hreflang`, el sitemap y los datos estructurados ya estaban desde octubre. El
revisor que los mira es `scripts/revisar_adsense.py`, que da 10 listo · 0
falta.

## El saludo por su nombre, la racha y los mensajes variados (2026-10-29)

Tres pedidos del profesor el mismo día, y el primero hubo que acotarlo antes de
hacer nada: *«no hay forma que la persona pongan su nombre y la que la página
le envíe un mensaje con su nombre que ya terminó la lección y felicitarlo»*.

**Un sitio estático no envía nada.** Ni un correo ni una notificación: eso
necesita servidor, una dirección y responsabilidad sobre datos personales, que
es exactamente lo que se decidió no tener el 2026-10-27 al descartar las
cuentas. Lo que sí puede hacer, y es casi todo lo que se pedía, es **saludarle
ahí mismo**, al marcar la lección. Se le dijo con esas palabras.

Así que el nombre vive en `localStorage` —`curso.nombre`, al lado de
`curso.hechas`— y no sale del navegador. Hay una prueba que busca `fetch`,
`XMLHttpRequest`, `sendBeacon` y `new Image(` en el guion: un nombre que se
escapó ya se escapó, y es lo único de este bloque que no se puede arreglar
después.

**Dónde se pide, que es la decisión que más importa.** El profesor preguntó
después: *«¿Entonces habría una ventana para que coloque su nombre en la página
principal?»*. **No**, y es a propósito: un formulario en la puerta, antes de
que el visitante haya visto nada, es la forma más fiable de perderlo. El campo
sale **después de la primera lección marcada**, donde ya hay una relación, y se
puede cambiar en el recuadro de progreso. Es la misma regla que ya tenía
escrita `#mio`: nada que desanime la primera visita.

**La racha** son los días seguidos, de `curso.fechas`. Dos cosas que la rompen:

- **la fecha es LOCAL y no `toISOString()`**, que da UTC: quien estudia a las
  once de la noche en Moscú vería el día contado como el siguiente, y quien
  estudia de madrugada en México perdería la racha. Hay una prueba que exige
  que `toISOString` no aparezca en el guion —y que mira los comentarios
  fuera, porque el código NOMBRA esa función para explicar por qué no la usa—;
- **la racha no se rompe porque hoy aún no hayas estudiado**: se cuenta hacia
  atrás desde hoy o desde ayer. Si no, a las diez de la mañana el sitio te
  diría que perdiste ocho días.

El ruso declina los días (1 день, 2-4 дня, 5+ дней), así que el plural va en
una lista de tres formas, como ya hacía `meses_de` en la portada. Un «5 день» en
la pantalla delata que el texto no lo escribió nadie.

### Los mensajes variados, y por qué no son un `%` ni un azar

Lo pidió a continuación: *«podemos mandar mensajes de aliento cada vez que
acabe una lección con su nombre, los mensajes deben ser variados»*. Son nueve
por idioma, y lo que costó pensar fue **cuál sale cada vez**:

- **al azar, no**: marcar y desmarcar la misma lección daría tres frases
  distintas para el mismo acto, y eso se lee como que el sitio está probando
  textos en vez de hablarte. La frase de una lección es siempre la misma.
- **`n % 9`, tampoco**: deja un ciclo visible. La frase de hoy es la de hace
  nueve lecciones, y en una racha de dos semanas eso se nota, que es justo de
  lo que la variedad venía a salvar.
- **un hash, menos todavía**: medido sobre las 365 lecciones, repite la frase
  de la lección anterior **entre 15 y 40 veces**. O sea dos días seguidos la
  misma, que es la queja entera.

Queda el **reparto por bloques**, que es el mismo que el de la letra correcta
de los tests (2026-10-27) y por el mismo motivo: dentro de cada bloque de nueve
lecciones salen las nueve frases una vez, en un orden que depende del bloque, y
si la primera del bloque coincide con la última del anterior se cambia por la
segunda. Medido sobre las 365: **0 repeticiones seguidas**, las nueve usadas
40-41 veces cada una, y ningún ciclo. La prueba hace esa cuenta con la misma
aritmética que corre en el navegador.

**El multiplicador es el de MINSTD (48271) y no el del LCG de libro
(1103515245)**, y no es cosmético: con el segundo el producto se sale de 2^53,
que es hasta donde JavaScript cuenta exacto, y la mezcla deja de ser la que se
midió aquí. La prueba lo fija.

**Son DOS listas y no una frase con el nombre pegado detrás**, porque el nombre
no siempre va al final: «Иван, ещё один урок позади!» frente a «Отлично,
Иван!». El precio es que se emparejan por índice, así que una lista más larga
que la otra daría la frase de un mensaje con el nombre de otro **y nada
fallaría**: hay una prueba que exige mismo largo, que la versión con nombre lo
nombre y que la otra no —un `{nombre}` suelto se imprime tal cual, y sin él sale
«Отлично, !»—.

**Dos mensajes se salen de la rotación a propósito:**

- **la primera lección** tiene el suyo («Первый урок пройден — самое трудное
  уже позади»). Es el momento en que más gente se va, y una frase de rotación
  no dice nada de lo que acaba de pasar.
- **el recuadro de la portada no felicita**: ahí el lector LLEGA, no acaba de
  terminar nada. Una frase de la rotación diría algo que no ha ocurrido —«una
  lección más» sin haber hecho ninguna— así que ese sitio lleva un saludo de
  vuelta, fijo («С возвращением, Иван!»). Hay una prueba que lo exige en los
  dos sentidos.

**Lo que esto NO hace**: no sincroniza entre aparatos, no sobrevive a un
borrado de datos del navegador y no manda nada a ningún sitio. Para lo primero
está el código de respaldo del 2026-10-27, y conviene saber que **el código no
lleva el nombre ni las fechas**: son 46 bytes de lecciones hechas, y crecer el
formato rompería los códigos que la gente ya tenga guardados.

## Qué hace falta, el DELE A2, y compartir desde la portada (2026-10-29)

Tres pedidos del profesor seguidos, y los tres se contestaron midiendo antes de
escribir.

### «¿Es necesario mencionar que el alumno necesita un cuaderno?»

Sí, y no era una opinión: se contó sobre las 365 lecciones.

    tarjetas (карточк*)   295 lecciones   81 %
    escribir (запиши*)    187             51 %
    grabarse              77              21 %
    cuaderno (тетрад*)    25
    cronómetro             9 · espejo 3 · auriculares 2

O sea que **el curso ya exigía material desde la lección 1 y no se avisaba en
ninguna parte**. Quien llega no sabe qué necesita, y eso se descubre a mitad
del primer ejercicio.

El apartado nuevo de «О курсе» dice tres cosas —cuaderno y bolígrafo, el móvil
para grabarse, y las tarjetas— y **lo que NO hace falta**, que es la mitad de
su valor: ni libro de texto (el curso se sostiene solo), ni diccionario (todas
las palabras vienen traducidas dentro de la lección), ni impresora.

**La tercera es la que convierte un gasto en un enlace**: la baraja ya está
hecha —3001 palabras con voz y dibujo— así que el alumno no tiene que fabricar
nada. Hay una prueba que exige que el texto lo diga.

**Van PROPORCIONES y no los números exactos**, y es deliberado: «187 de 365»
sale de contar las lecciones que contienen «запиши», que no es lo mismo que
las que piden escribir. Lo que el recuento sostiene de verdad es el orden de
magnitud, y además una proporción no envejece el día que se reescriba una
lección. Los números exactos quedan aquí, que es donde se pueden fechar.

### El DELE A2: lo que el profesor trajo coincidía con lo que ya estaba verificado

Trajo la descripción del examen con sus fuentes. Lo primero fue cotejarla con
`programa/alineacion-mcer-pcic.md` §5, verificado el 2026-10-26, y **coincide
hasta el minuto**: 60 de lectura, 40 de audición, 45 de escritura y 12 de oral
más 12 de preparación. Son dos verificaciones independientes del mismo dato, lo
cual lo refuerza — y por eso hay una prueba que compara el apartado público
con esa sección del programa: **si alguien corrige uno, el otro tiene que
seguirlo**. Es la deriva que este proyecto sufre una y otra vez.

**Las cuatro fuentes que trajo no se pudieron abrir** (`delea2.org`, el
Cervantes de Berlín y las otras dan `000` desde este contenedor, como ya pasaba
con el Cervantes en octubre). Lo que se confirmó se confirmó por búsqueda, con
fuentes de terceros: título oficial del Instituto Cervantes en nombre del
Ministerio de Educación de España, validez indefinida, reconocimiento
internacional, y requisito para la nacionalidad por residencia.

**Un matiz que el profesor no mencionó y que cambia la frase**: los nacionales
de veinte países hispanohablantes están EXENTOS del DELE para la nacionalidad.
Su público rusohablante es justo el que no lo está, así que el dato le sirve —
pero escrito sin ese matiz sería falso para media América, y el sitio se lee
también en español.

Tres cosas que el apartado no hace, y las tres tienen prueba:

- **No trae precio ni fechas** (regla 7): la tasa, las convocatorias y los
  centros cambian cada año. Es lo mismo que las lecciones S50D7 y S52D7, que
  llevan `[VERIFICAR]` por esto. Un precio viejo en la página es peor que
  ninguno, porque el lector cuenta con él. El aviso manda a
  `examenes.cervantes.es`, y la prueba exige que ese enlace esté: es lo que
  sostiene el apartado entero.
- **No se atribuye el Cervantes.** Es la decisión del 2026-10-27, cuando se
  rechazó escribir «elaborado por profesores del Cervantes»: el sitio habla del
  EXAMEN, que es un hecho, no de una autoría prestada. La guarda busca
  «profesor/elaborado/creado/авторы» a menos de cuarenta caracteres de
  «Cervantes».
- **No promete aprobar**: dice que el curso prepara, no que inscriba ni
  garantice nada.

### «En la página principal no está el botón para compartir»

Tenía razón, y es el patrón que más se repite aquí: **una regla correcta para
el caso que la motivó, aplicada a un caso que nadie miró**. El 2026-10-27 se
decidió que compartir va al pie de la lección «porque se comparte lo que ya has
leído», y eso dejó fuera la portada — que es justamente la página que alguien
manda para recomendar el curso, y por tanto la que más gente puede traer.

Dos cosas que no son de forma:

- **El rótulo cambia.** El de la lección dice «Поделиться **уроком**», y en la
  portada eso sería falso: lo que se manda desde ahí es el curso. Un rótulo
  equivocado no rompe nada, y por eso hay que escribirlo y probarlo.
- **La canónica pasa a calcularse en UN solo sitio** (`canonica_de`). Estaba
  dentro de `pagina()` y la lección la rearmaba a mano con
  `cfg['dominio'] + "/semana-.."`, que funciona **por una coincidencia**: las
  lecciones existen solo en ruso y el ruso va en la raíz. Con la portada habría
  tres copias de la misma cuenta, y dos copias de la misma pregunta es como se
  descubre tarde que una de las dos miente —pasó con `facebook.permisos` y con
  `replica.CARPETA` en el proyecto hermano—. `idioma=None` significa «la raíz
  del sitio», que es lo que la lección quiere decir, en vez de pasarle un
  `"ru"` a ciegas.
- **El enlace de cada portada apunta a SU portada.** Es la sexta vez que esta
  suite mira una ruta por idioma, después del conmutador de idioma, las
  tarjetas del mapa, los destinos del probador, las fuentes y los iconos. Aquí
  el fallo sería mudo y caro: el botón del curso en inglés mandando a la
  portada rusa. La prueba resuelve las tres contra `canonica_de`.

Y una cosa del ensayo que vale anotar: el parche se probó **sobre copias** de
los dos ficheros antes de tocar el repo, y ahí saltó que `yaml.safe_dump`
**envuelve a 80 columnas**, así que un texto largo salía partido en varias
líneas sin la indentación del bloque y dejaba `textos.yaml` ilegible para el
propio YAML. Se escriben con `json.dumps`, que es un subconjunto válido de YAML
para un escalar entre comillas y no envuelve nada.

### El vídeo por lección: medido, probado y NO aplicado (2026-10-29)

El profesor preguntó si se podía montar un canal de YouTube y poner un vídeo
por lección, y al terminar aclaró que **no va a grabar nada: era una
pregunta**. Así que no se aplicó nada. Queda escrito porque lo que costó
averiguar no es el código.

**Lo que bloquea esto no es técnico, es la política de privacidad.** Un
`<iframe>` de YouTube carga el reproductor de Google al abrir la página, y la
política de este sitio promete por escrito que sin anuncios no se carga nada
de terceros. Es el mismo caso que ya se decidió dos veces: los widgets de
compartir —que por eso son enlaces normales— y Google Fonts, que por eso están
autoalojadas. La miniatura tampoco vale: `i.ytimg.com` también es de Google.

La salida es una **fachada**: un bloque con el botón, y el iframe
(`youtube-nocookie.com`) lo inserta el guion **al pulsar**. Medido en
navegador: antes del clic, **cero peticiones a Google**; después, una. Y sin
JavaScript el bloque es un **enlace** a YouTube y no un botón muerto, que es
la regla del sitio desde el principio —va al revés que el resto, nace como
enlace y el guion lo convierte en botón, porque la versión sin guion tiene que
ser la que sirve—.

**Y aun así hay que escribir una línea en la política**, diciendo que al
pulsar YouTube recibe la IP y los datos del dispositivo. Ésa es la razón de no
dejarlo puesto «por si acaso»: sin vídeos, esa línea afirma algo que no pasa, y
lo único que una política no puede hacer es describir mal lo que el sitio
carga. Más el campo, el guion, el CSS y ocho guardas sin camino, que es lo que
ya pasó con `render_cifra` y `render_tarjetas`.

**Sobre el canal en sí**, por si vuelve la pregunta: la política de
monetización de YouTube pone como ejemplo de contenido «inauténtico» —el que
no se monetiza— las plantillas clonadas, las diapositivas sin aporte y las
lecturas con voz sintética. O sea que generar 365 vídeos del curso con los
11.378 audios y los 300 dibujos que ya hay en disco **pondría en riesgo el
canal entero**, no solo esos vídeos: es la lección del 2026-10-04 en el
proyecto hermano, donde el reglamento de Facebook penaliza con menos alcance
en TODA la cuenta. Lo que sí monetiza es el profesor grabándose, porque cada
vídeo tiene enfoque propio. Los umbrales (1.000 suscriptores, 4.000 horas, y
8.000 desde febrero de 2027) y la fecha de la política vienen de blogs de
terceros que **se contradicen entre sí**: cotejar en la página oficial del
Programa de Socios antes de montar nada. Y YouTube paga por AdSense, o sea el
mismo asunto de residencia fiscal que quedó pendiente de un contable el 27.

### Y el nombre, desde la portada (2026-10-29)

El profesor lo pidió al final del día: poder escribir el nombre en la página
principal. **El campo ya estaba ahí** —se añadió esa misma mañana— pero DENTRO
de `#mio`, el recuadro de progreso, que se enciende solo cuando ya hay
lecciones marcadas. O sea que era invisible **exactamente para quien acaba de
llegar**, que es a quien se le quería preguntar. El mismo patrón que el botón
de restaurar el progreso el 2026-10-27: escondido justo para el que lo
necesita.

Ahora vive fuera, y hay una prueba que exige que el hueco aparezca ANTES que
`#mio` en el HTML: si vuelve a meterse dentro, nadie lo notaría mirando la
página con progreso.

**Lo que sigue sin hacerse es una ventana al entrar**, y eso no cambió: un
formulario que tapa la página antes de que el visitante haya visto nada es la
forma más fiable de perderlo. Es un campo en la columna, debajo del contador.

Dos cosas menores que importan en el móvil: **Enter guarda** —ahí el teclado
tapa el botón— y quien ya dio su nombre ve un saludo con un botón «Изменить»,
no un campo abierto ocupando sitio para siempre.

## El canal de Telegram, alimentado de lo que ya hay (2026-10-30)

«Ok vamos con telegram». El 2026-10-27 se decidió que **Telegram es el canal**
—es donde vive el público rusohablante fuera de Rusia y su umbral de
monetización es alcanzable— y se anotó entonces que el curso ya tiene con qué
alimentarlo sin escribir nada nuevo. Esto lo hace.

    palabras del curso ......... 2 985
    menos la que no es pareja ..     1
    publicaciones .............. 2 984   → 8 años y 64 días
      con voz .................. 2 882
      con frase de ejemplo ..... 2 094
      con dibujo ...............   263

**Cero contenido nuevo y cero céntimos**: la palabra, su traducción, su frase,
su voz y el enlace a la lección que la enseña salen de lo que el profesor ya
escribió y revisó.

### Las cuatro decisiones

- **Van en el ORDEN DEL CURSO y no al azar.** Quien siga el canal está
  haciendo una versión lenta del curso, y el enlace de cada día apunta a la
  lección que toca. Alfabéticas —que es como las quiere el diccionario— el
  primer día sería «los / las», de la lección 87. `palabras_del_curso` toma un
  `orden=` y sigue siendo UNA función: un segundo recorrido de las 365
  lecciones para lo mismo es como se descubre tarde que uno de los dos se
  quedó viejo.
- **Qué día sale cuál se calcula de la FECHA, no de un contador en disco.**
  Correrlo dos veces el mismo día publica lo mismo —un cron que se dispara dos
  veces no adelanta el canal— y no hay ningún estado que se pueda perder.
- **Al acabarse NO vuelve a empezar.** Volver al principio en silencio haría
  que el canal dijera «la palabra de hoy» de algo que ya salió hace ocho años.
- **El canal se escribe en UN solo sitio**: el pie de las 394 páginas enlaza
  `redes.telegram` y el publicador necesita `@handle`, así que se deriva del
  enlace. `telegram.canal` queda para lo que el enlace no cubre —un canal
  privado es un id numérico— y para poder publicar antes de enseñarlo.

### La fila que se descarta, y por qué la regla no es una lista

De las 2.985 hay **una** que no es una pareja de palabra y traducción:

    tomar = и пить, и есть   →   tomar = прежде всего пить

Escrita así sale un «tomar = … — tomar = …» que se lee como una publicación
rota. La regla es «la columna rusa no puede repetir la palabra española», y se
escribe así y no como una lista con esa fila dentro porque **una lista no
vuelve a mirar nada** el día que el profesor escriba otra igual. Y por la forma
del defecto y no por lo que descarta hoy: las **otras doce** filas con letras
latinas en la columna rusa son glosas legítimas —`la palta (Арг., Чили, Перу)`,
`(🌎 la alberca, la pileta)`, `(≠ dormir — спать)`— y descartarlas sería perder
material bueno por una de mentira.

**Y se compara la PALABRA, no la celda**: `tomar = и пить, и есть` no aparece
tal cual dentro de la columna rusa, así que la primera versión no cazaba nada.
La palabra la saca `generar_audio.parte_espanola`, que es el único sitio que
sabe separar la glosa rusa de la española —se escribió el 2026-10-28 para
rescatar estas mismas filas del locutor—. Con frontera de palabra: sin ella una
entrada corta casaría dentro de cualquier paréntesis, «(ser)» incluido.

### Dos cosas que habrían roto el canal y no se ven probándolo aquí

1. **La carátula tiene que ser JPEG de 320 px y menos de 200 kB**, y los
   dibujos son `.webp` de 512. Mandados tal cual, Telegram **rechaza el envío
   entero**: las 263 publicaciones con dibujo se habrían quedado mudas sin
   decir por qué. Se convierten a un temporal que se tira después.
2. **Pillow no estaba en `requirements.txt`**, y GitHub Actions instala SOLO lo
   que ese fichero diga. Estaba aquí por casualidad —lo usan `icono.py` y otros
   tres— y allí no habría existido. Hay una guarda que lo fija.

Las dos salieron de leer la documentación de la API y de mirar qué instala el
trabajo, no de probar: **`api.telegram.org` da `000` desde este contenedor**,
como Google, Drive y el Cervantes. Lo que SÍ está probado es todo lo demás:
qué palabra toca, qué texto sale, qué se adjunta, qué forma tiene el pedido
—con un enviador de mentira— y que la carátula cumple los límites.

### El automatismo

`.github/workflows/palabra-del-dia.yml`, todos los días a las **06:17 UTC**
—media mañana en Alemania y en España, y el minuto no es redondo a propósito:
a las en punto se juntan los crones de medio GitHub—. Corre en GitHub y no en
el ordenador del profesor por una razón simple: **un canal diario que depende
de que alguien encienda el portátil no es diario**.

- **Enseña lo que va a salir SIEMPRE, en su propio paso**, aunque no publique:
  así el registro de la corrida dice qué tocaba aunque el envío falle o aunque
  el canal no exista todavía.
- **Sin `TELEGRAM_TOKEN` no publica y no falla**: mientras el canal no exista,
  una X roja cada mañana sería ruido.
- **Lleva botón manual** (`workflow_dispatch`), y eso no es comodidad: es la
  única forma de probar el envío, porque desde aquí no se puede.
- **El token va de secreto del repositorio**, nunca en el repositorio. Hay una
  guarda que busca por la FORMA de un token —«dígitos:35 caracteres»— en los
  cuatro ficheros que podrían llevarlo. La primera versión buscaba la palabra
  «bot» y la encontró dentro de «botón», que es prosa de un comentario; la
  segunda pedía 35 caracteres exactos y el token de prueba tenía 34, así que
  **dijo que todo estaba bien con un token pegado en el fichero**. Ahora admite
  de 30 a 45: una guarda de seguridad que falla por un carácter no sirve.

### Lo que falta, y es del profesor

1. **Crear el canal** y meter al bot como ADMINISTRADOR (si no, Telegram
   contesta «chat not found» aunque el token sea bueno).
2. Hablar con **@BotFather** para crear el bot y guardar su token en
   **Settings → Secrets and variables → Actions** como `TELEGRAM_TOKEN`.
3. Escribir el enlace en `redes.telegram` y la fecha de arranque en
   `telegram.desde`, en `web/sitio.yaml`.

Mientras falte cualquiera de las tres, el canal no publica, el pie no enseña
el enlace y el trabajo diario no se pone en rojo.

## Los cinco destinos en la barra, y la eñe como marca (2026-10-30)

Lo pidió el profesor: *«Словарь курса · Тест на уровень, deberían estar en la
parte de arriba, ¿no crees?»*. Tenía razón y el motivo es simple: estaban en
el **pie**, o sea abajo del todo de las 394 páginas. Quien no baje, no sabe
que existen.

**Lo que frenaba no era el sitio, era el título.** La barra ya había fallado
una vez por cuatro píxeles (2026-10-26), así que esto se midió en Chromium
antes de tocar una línea. El alto de la cabecera a cada ancho de ventana —46
px es UNA fila— en la portada rusa:

                             360  414  600  640  700  768  834  900 1024
    antes, 3 enlaces         111  111   78   78   82   46   46   46   46
    4, «Словарь курса»       111  111   78   79   79   79   82   46   46
    5, con los dos           111  111   78   79   79   79   82   46   46
    5 + la eñe de marca      107  107   78   80   46   46   46   46   46

O sea que **no fue un apaño para que cupieran dos enlaces más**: cabe en una
fila desde 700 px en los tres idiomas —el ruso necesitaba 768— y en el móvil
la cabecera encoge. Más destinos y menos barra.

**Y no hubo que acortar ningún rótulo.** Lo que ocupaba el sitio era
«Испанский с нуля для русскоговорящих»: **304 px de una barra de 768, más que
los cinco enlaces juntos**. Por debajo de 64rem se cambia por la eñe, que
desde el 2026-10-29 existe y es reconocible.

Lo que hay que cuidar si alguien lo toca:

- **El corte de la eñe tiene que ser el ANCHO de la barra, y por eso hay una
  prueba que compara los dos números.** La primera versión puso el corte en
  56rem dejando la barra en 60: el título volvía a los 896 px y entonces el
  ruso se partía en dos filas **a 1024 y a 1280, con trescientos píxeles
  libres al lado**, que es exactamente el fallo de octubre con otra cara. La
  barra pasa a 64rem y el corte a 63.99: el título vuelve justo cuando cabe.
- **Sin el archivo del icono el título no se esconde nunca.** La clase
  `con-icono` la pone el generador mirando el disco, igual que los `<link>`
  del icono: esconder el título sin nada que poner en su lugar dejaría la
  barra sin marca.
- **El nombre accesible va en el `aria-label` del enlace**, no en el texto:
  el texto se esconde por CSS, el `aria-label` no. Y el icono lleva `alt=""`,
  que es decorativo.
- **En el móvil el menú SE PARTE en dos líneas en vez de desplazarse.** Con
  tres enlaces cabían en una y el desplazamiento no se notaba; con cinco, los
  dos últimos quedaban detrás de un deslizamiento **y sin ninguna señal**
  —`scrollbar-width:none` esconde hasta la barra—, que es la forma más fiable
  de que nadie los encuentre. Partido ocupa 107 px, menos que los 111 que
  ocupaba la cabecera con tres enlaces.
- **Los rótulos no son textos nuevos**: el del diccionario sale de
  `diccionario.enlace` y el del test de `test.titulo`, que es donde ya vivían.
  Cada palabra se escribe en un solo sitio.

**El pie no se tocó.** Repite cuatro de los cinco destinos, y eso en un pie es
lo normal: lo que se pidió fue subirlos, no vaciarlo.

**Y una guarda mía que miró donde no era, por segunda vez en el mismo día**:
la prueba del icono buscaba `con-icono` en la página entera y lo encontraba
**en el CSS**, que es donde está el selector de la regla. Mira la etiqueta de
la marca. Es el mismo error que acababa de cometer la guarda del audio con
`class="suena"` dentro de un `<script>`.

## El diccionario del curso (2026-10-29)

Una página con **las 2.985 palabras** del curso, buscable, con su audio y un
enlace a la lección donde se enseña cada una. `slovar.html`, en los tres
idiomas, enlazada desde el pie de las 394 páginas y en el sitemap.

Sirve al alumno —«¿cómo se dice X?» a mitad de una lección— y es lo único de
esta tanda que además puede traer visitas: la gente busca palabras sueltas en
Google. Y es **UNA página y no 2.985 páginas finas**, que es lo que un revisor
de AdSense rechaza.

### Qué entra, y una trampa de la regla 8

De las 3.155 filas de las dos tablas de vocabulario salen 2.985 palabras: una
que se glosa en un domingo y se enseña el lunes es la misma, y se conserva la
PRIMERA aparición, que es donde el curso la introduce.

**La traducción tiene que traer cirílico**, y eso descarta dieciséis filas en
las que la segunda columna no es una traducción sino la **variante americana**
—«el zumo → el jugo», por la regla 8—. En una lección eso se lee bien; en un
diccionario dice que «zumo» significa «jugo» en ruso. Es el mismo filtro que la
vitrina de la portada, dicho al derecho: aquí se EXIGE cirílico en vez de
rechazar latino, porque una glosa legítima puede traer las dos cosas.

**Se ordena por la palabra y no por el artículo** —un diccionario busca «casa»,
no «la casa»— y hay que pelar **por turnos**: «el / la cantante» pierde el
«el», y entonces hay que quitar la barra para llegar a «la» y el artículo otra
vez para llegar a «cantante». De una pasada se quedaba en «/ la cantante» y
abría la lista entera.

### El peso, que es lo que decidió la forma

La primera versión traía el ▶ y el enlace escritos en cada fila y pesaba
**142 KB comprimidos**, que es lo que un lector se descarga. Medido:

    con los hashes del audio dentro ... 142 KB
    sin ellos ........................   83 KB
    las palabras y sus traducciones ..   84 KB de texto puro

O sea que **los 83 KB de hoy son casi todo contenido** y no se pueden encoger:
son las palabras. Lo que sobraba eran los veinte caracteres al azar del nombre
de cada MP3, que no los comprime nadie y que **solo le sirven a quien tiene
JavaScript**, porque es el único que puede oírlos. Ahora van en
`vocabulario/voces.json`, un array en el mismo orden que la lista —un
diccionario tendría las 2.985 palabras otra vez como claves— que el guion pide
después de pintar. Hay una prueba que fija el tope: si alguien vuelve a meter
los hashes en la página, se pone en rojo.

**Sin JavaScript queda la lista entera**: las palabras y sus traducciones, para
leer y para que Google la indexe. Lo que no sale es la caja de búsqueda, que no
filtraría nada.

### Dos fallos que solo se vieron en el navegador

1. **Los ▶ no sonaban.** `pagina()` decide si carga el reproductor mirando si
   hay un `.suena` en el cuerpo, y aquí los botones los pone el guion al llegar
   las voces: el HTML servido no trae ninguno. Eran botones mudos en las tres
   páginas.
2. **«урок 87 урок 87».** Una fila se viste al entrar en pantalla y otra vez
   cuando llegan las voces, y la primera versión le pegaba el enlace a la
   lección dos veces. Ahora `vestir` es idempotente: cada parte comprueba si ya
   está, en vez de llevar un «ya hecho» para toda la fila.

Las dos salieron mirando la página —la segunda, en una captura— y ninguna
habría salido leyendo el código.

## Grabarse y oírse (2026-10-29)

El curso pide grabarse en **77 lecciones** —«запишите себя»— desde que se
escribió, y el sitio no ofrecía dónde. Ahora hay un botón al cerrar la
lección: se graba, se oye y se compara con el ▶ de la frase.

**Nada sale del navegador.** La grabación vive en memoria, no se sube, no se
guarda en el aparato y muere con la pestaña. Eso lo dice el propio bloque —la
entrada, antes de cualquier botón— y desde hoy también la política de
privacidad, que estrena un apartado «Микрофон». No era obligatorio, porque el
sitio no recoge nada; pero el lector ve una petición de micrófono y merece
saber por qué, que es la misma regla que dejó escrita el vídeo de YouTube que
no se aplicó: lo único que una política no puede hacer es describir mal lo que
el sitio hace.

Lo que hay que cuidar si alguien lo toca:

- **Sin micrófono o sin `MediaRecorder` el bloque NO sale**, y las dos salidas
  van antes de encenderlo. Un botón que no puede hacer nada es peor que ningún
  botón, y aquí además pediría un permiso para nada.
- **Solo donde hay un ▶ con el que compararse.** Diez días —tests y exámenes—
  no tienen una sola frase locutada en su cuerpo; ahí el ejercicio sería
  grabarse contra nada. La prueba mira esa relación y no un número: si mañana
  una lección pierde su audio, el bloque la sigue.
- **El micrófono se apaga de verdad al parar** (`flujo.getTracks()...stop()`).
  Sin eso la pestaña se queda con el punto rojo encendido hasta que se cierra,
  y eso se lee como que el sitio sigue escuchando.
- **No se fija el `mimeType`.** Cada navegador graba en lo suyo —Safari en
  mp4, el resto en webm— y fijarlo dejaría a uno de los dos fuera.
- **La toma anterior se tira** (`revokeObjectURL`) en cuanto hay otra: si no,
  una sesión larga acaba cargando con todos los blobs.
- **Permiso denegado se dice, y se dice que la lección sigue**: el ejercicio
  es decir la frase en voz alta, y eso se puede hacer sin grabar nada.

**Comprobado con un micrófono falso de Chromium**, que es la única forma de
saber si graba: la toma produce **10.720 bytes de `audio/webm;codecs=opus`**,
no sale una sola petición con cuerpo, sin permiso lo explica y sin
`MediaRecorder` el bloque se queda oculto.

**Y un fallo de una línea que solo se ve mirando**: el ayudante que fabrica
los botones recibía la clase como cadena y `''` caía en el `||`, así que
«Записать» —la única acción del bloque— salía perfilado como los otros dos.
Ahora el parámetro es un booleano: o es el botón principal o es secundario.

## Las palabras del día, al cerrar la lección (2026-10-29)

El profesor echaba en falta un test al final de cada lección: el sitio tenía
**66 de 365 días contestables** —los 23 tests de unidad y los 43 mini-tests— y
los 220 días de lección normal acababan en ejercicios de escribir con la clave
detrás de un botón.

**Se le dijo que serían unas 1.100 preguntas nuevas de trabajo de contenido, y
eso era falso.** Las palabras ya están escritas y traducidas en la tabla
`Словарь дня` de cada lección, revisadas por él. Contado:

    entradas de vocabulario del curso ...... 3.155
    con traducción limpia y usable ......... 2.333
    lecciones con quiz (>= 4 limpias) ......   244 de 365
    preguntas publicadas ................... 1.198
    de esas palabras, con voz ya pagada .... las 1.198

O sea **cero contenido nuevo y cero céntimos**: `scripts/quiz_lexico.py` arma
las preguntas de lo que hay.

**El sentido es ruso → español**: se enseña la traducción y se elige la
palabra. Es la dirección que cuesta —producir— y la que pide el examen; al
revés sería reconocer, que ya hacen las tarjetas.

### Lo que NO hace, y es lo que lo sostiene

- **No inventa nada.** Las dos columnas salen de la tabla del profesor. Si una
  entrada no se puede usar sin dudas se descarta ella sola, y si no quedan
  cuatro limpias esa lección **se queda exactamente como está**. Es el contrato
  de `pruebas.py` y de `huecos.py`: decirle a alguien que falló cuando acertó
  es lo que este proyecto no hace.
- **No saca distractores de otras lecciones.** Son las otras palabras del
  mismo día, así que el ejercicio es «reconozca las palabras de hoy» y no una
  mezcla con material de hace seis meses. De paso, construir una lección no
  necesita leer el curso entero.
- **No guarda nada ni sale a la red.** Su propia entrada lo dice —«las
  respuestas no se guardan y no cuentan para nada»— y hay una prueba que busca
  `fetch`, `XMLHttpRequest`, `sendBeacon` y `localStorage` en el guion. El día
  que contara, habría que decirlo antes.
- **No sale en los días que ya tienen su test** (`prueba`, `repaso`, `examen`,
  `simulacro`, `proyecto`, `reserva`): dos tests en la misma página son ruido,
  y un repaso no tiene `Словарь дня` siquiera.

### Qué descalifica una entrada, y por qué

No es una lista de gustos: cada marca significa que la celda no es una
traducción limpia de una palabra. `✗ ↔ 🌎` son avisos y variantes
(«el conductor (✗ не «кондуктор»)»), `+ =` dicen que la entrada es una
construcción (`hay que + инф.`), los paréntesis son una glosa y la barra son
dos palabras en una (`sí / no`). Más dos que se descartan **enteras**: una
traducción repetida haría una pregunta con DOS respuestas correctas, y una
palabra repetida, dos opciones iguales —que es el defecto que esta suite ya
cazó dos veces en los tests escritos a mano—.

### El reparto de la respuesta correcta: dos cosas, no una

1. **Repartida**, porque el 2026-10-27 se midió que catorce de quince
   respuestas de un test de unidad eran la б) y marcando todo б se aprobaba la
   unidad sin saber nada.
2. **Sin ciclo.** La primera versión hacía `sitios[i % 3]`, que reparte igual
   de bien en el recuento y deja la secuencia **а-б-в-а-б**, que se aprende de
   memoria en dos lecciones. Es exactamente el defecto que ya tuvieron la letra
   correcta de los tests y los mensajes de ánimo, con otra cara.

Y una tercera que apareció midiendo: con cinco preguntas y tres opciones el
reparto de base es 2-2-1, y **si la corta es siempre la misma**, sobre las 244
lecciones daba **488-466-244** —la tercera opción valía la mitad que las otras
dos en todo el curso—. Se rota con el número de lección. Hoy: **397-400-401,
cero escaleras y cero tríos**, y la prueba exige las tres cosas.

### La palabra fallada se puede OÍR

Las 1.198 están locutadas desde el 2026-10-28, así que el ▶ del resultado no
cuesta un céntimo. Funciona sin tocar el reproductor porque `AUDIO_JS` escucha
en `document`: un botón que el guion inserta después de cargar la página entra
solo. Lo único que hubo que ampliar es la condición de cargar el reproductor —
una lección sin un solo ▶ en su cuerpo pero con palabras locutadas en el quiz
lo necesita igual.

### Comprobado contestándolo

`scripts/probar_navegador.js` lo contesta en Chromium eligiendo la opción **por
su TEXTO** y no por su letra ni su posición: por la letra sería repetir la
cuenta del propio generador y no probaría nada. 5/5 en las lecciones, y los
días con su propio test siguen sin llevarlo.

**Y la prueba de fondo mira la RELACIÓN, no un número**: para cada pregunta de
cada lección, la opción marcada como correcta tiene que ser la palabra que el
profesor puso al lado de esa traducción en la tabla. Si algún día el lector se
desalinea, se pone en rojo aunque el reparto de letras siga pareciendo sano.

**De paso, dos artefactos de MI comprobación y no del sitio**, los dos del
mismo tipo y conviene anotarlos: el generador **no copia `docs/fonts/` ni
`docs/audio/indice.json` a un destino nuevo** —están versionados en `docs/` y
nada más—, así que una construcción de prueba sale sin tipografía y con cero
palabras locutadas. En el sitio publicado nunca faltaron. Una construcción de
prueba hay que sembrarla con los dos índices y las fuentes, o se diagnostica
un fallo que no existe.

## El año en casillas y el certificado de nivel (2026-10-29)

El profesor preguntó qué más haría el sitio atractivo para el alumno. Las dos
cosas de este bloque **no miden nada nuevo**: hacen visible lo que el navegador
ya guardaba desde el saludo por su nombre, unas horas antes.

### El calendario del año

La racha era un número —«7 дней подряд»—. Ahora es una rejilla de **364
casillas**, una por día, con las columnas como semanas. El mismo dato dicho de
otra forma, y la forma importa: un número no enseña los huecos, y los huecos
son lo que hace volver mañana.

- **364 y no 365**: se arranca en el lunes de hace 51 semanas, así que las 52
  columnas son semanas enteras y la última es la de hoy. Los días de esta
  semana que aún no han llegado se dibujan vacíos en vez de dejarse fuera: sin
  ellos la última columna cambiaría de alto y la rejilla saldría mellada.
- **Solo si ya hay progreso**, igual que `#mio` y las barras del mapa. En la
  primera visita 364 casillas en blanco no se leen como «empieza», se leen como
  un hueco.
- **En el móvil desborda y se desplaza sola hasta hoy**, que es el extremo
  derecho. Cincuenta y dos columnas no caben en 358 px y achicar la casilla
  hasta que quepan la deja en cuatro píxeles.
- **Una etiqueta para la rejilla entera** (`role="img"`) y las casillas calladas:
  un lector de pantalla leyendo 364 celdas sería inservible, y lo que se quiere
  oír es cuántos días son.
- **El aire de los lados no es decorativo**: el recuadro de HOY es un `outline`,
  que se dibuja FUERA de la casilla, y pegado al borde de la rejilla se corta.

**Y el orden del recuadro cambió**: el calendario va ANTES del párrafo que
explica que el progreso vive en este navegador. Puesto detrás quedaba debajo de
cuatro líneas sobre `localStorage`. El recuadro se lee ahora como lo que es:
el número, la barra, el saludo con la racha, el año, el certificado, y la letra
pequeña al final. Se vio en una captura, no leyendo el HTML.

### El certificado

Al cerrar un nivel —A1 en la 154, A2 en la 365— sale un botón que descarga un
PNG con el nombre del alumno. Lo dibuja el navegador en un `<canvas>`: no hay
servidor, no se sube nada y no se guarda nada de nadie.

- **Los niveles salen del calendario** (`niveles_del_curso`) y no de dos números
  escritos a mano: el día que el profesor mueva una unidad de nivel, esto lo
  sigue solo.
- **`hasta` cuenta desde la lección 1**, no desde donde empieza el nivel:
  terminar A2 incluye haber hecho A1, y un certificado de A2 con el A1 a medias
  no diría la verdad. La guarda es el `for(var w=1;w<=nv.hasta;w++)`.
- **Sin nombre no hay certificado**: se señala el campo que ya existe arriba en
  vez de abrir otro. Un papel que dice «Выдан: » no vale nada.
- **El papel dice que no es oficial**, y lo dice el PNG y no solo la página,
  porque el PNG se comparte suelto. Y **no nombra al Instituto Cervantes ni al
  DELE**: es la decisión del 2026-10-27 —el sitio habla del EXAMEN, que es un
  hecho, no de una autoría ni de un aval prestados— y un certificado es justo
  donde eso costaría más caro. Hay una prueba que busca las cuatro palabras.
- **La paleta va escrita en el guion y NO leída de las variables del CSS**: un
  certificado se imprime, así que es siempre la versión clara; leyéndola, quien
  tenga puesto el tema oscuro se descargaría un papel negro. El precio de esa
  copia es que se queda vieja —es lo que ya le pasa a `tarjeta_social.py`— así
  que hay una prueba que la compara con el `:root` del CSS.

**Dos cosas que costaron una vuelta cada una, y las dos se vieron mirando el
PNG y no razonando:**

1. **El lienzo pedía grosor 600 y el sitio solo trae 400 y 700.** El navegador
   no encuentra ninguna cara y engorda la de 400 por su cuenta, que no es la
   letra del sitio. Hay una prueba que compara los grosores que pide el guion
   con los que declara `CARAS`.
2. **`document.fonts.ready` NO basta.** Cada cara lleva `unicode-range`, así que
   el navegador no se baja la cirílica hasta que algo la USA, y dibujar en un
   lienzo no cuenta como usarla. Hay que pedirlas por su nombre y con el texto
   que se va a escribir. Si la carga falla, se dibuja igual con la letra que
   haya: quedarse sin papel sería peor que quedarse sin tipografía.

**Y un fallo de la comprobación, no del sitio**: la primera verificación en
navegador dijo que el certificado salía con la letra de reserva. Era verdad y
la causa era mía: **el generador no copia `docs/fonts/` a un destino nuevo**
—las fuentes están versionadas en `docs/` y nada más— así que la construcción
de prueba no tenía ninguna. En el sitio publicado nunca faltaron.

## Las tarjetas en la página, y cuatro cosas rotas que salieron con ellas (2026-10-30)

El profesor mandó una foto de la lección 1-2 en el móvil: el calentamiento
dice «Карточки: 8 слов» y **no había ninguna tarjeta a la vista**. Preguntó
después si no se podían enseñar en la página, y de ahí salió todo lo demás.

**Es la sexta vez que el contenido ya existía.** Las palabras son las de los
días anteriores —escritas, traducidas, revisadas y locutadas desde octubre—,
así que `scripts/tarjetas.py` no inventa nada: lee cuántas pide la lección
(`Карточки: N слов`) y las saca hacia atrás del vocabulario del curso.
**285 lecciones las piden y las 285 pueden darlas**, con cero contenido nuevo
y cero céntimos.

- **Las palabras son de los días ANTERIORES, nunca del suyo.** El
  calentamiento repasa lo de ayer; enseñar hoy las que la lección va a dar
  dentro de veinte minutos sería regalar el vocabulario del día.
- **Las últimas N, seguidas.** Cuando hace falta tirar de un día más viejo se
  cogen sus ÚLTIMAS palabras y no las primeras: así la baraja es exactamente
  «lo último que aprendiste» y no una lista con un hueco en medio.
- **El día 1 no lleva ninguna**, y su propio texto lo dice: «карточек ещё
  нет». Un bloque ahí contradiría la lección.
- **Nace oculto y lo enciende el navegador**, como el resto del sitio: sin
  JavaScript una tarjeta no se puede dar la vuelta, y ese vocabulario está en
  sus lecciones con la traducción al lado.
- **El ▶ va en la cara española**, que es lo que la lección pide: se oye, se
  dice la traducción en voz alta y se da la vuelta.
- **Dónde va el bloque se decide por el CONTENIDO**, buscando el apartado que
  habla de «Карточки», y no por el nombre del apartado: los días de repaso y
  de cultura llaman al primero de otra manera.

### Y el bloque de grabarse no decía QUÉ grabar

De la misma foto: «no sale la frase que va a grabar». El bloque decía
«escuche la frase (▶), dígala y compárese» **sin ninguna frase delante**, así
que el ejercicio no se podía hacer. Ahora `frase_para_grabar` nombra una,
con su ▶, y **prefiere una frase de EJEMPLO del vocabulario** —la tercera
columna de `Словарь дня`—: una palabra suelta no entrena la pronunciación,
porque lo que cuesta es la cadena y la vocal átona que el ruso reduce. Es
determinista, así que al recargar la lección está la misma y se puede volver
a intentar.

### Los huecos: las fichas no se apagaban y la corrección estaba arriba

También del profesor, usando el sitio: «cuando marcas las palabras no todas
se desactivan», y «las respuestas correctas se van hasta abajo y no se ponen
debajo del ejercicio mismo».

- **Solo se apagaba la ÚLTIMA ficha del banco.** `repintarFichas` exigía
  además que el total de fichas fuera igual a `Object.keys(vistas).length`, y
  esa cuenta se va llenando DENTRO del propio bucle: hasta la última vuelta
  nunca cuadra. Ahora se apagan tantas copias de una palabra como huecos la
  lleven, que es lo que la condición quería decir.
- **El botón de comprobar estaba ARRIBA**, pegado al banco, porque la barra
  entera se insertaba detrás del `<h3>`. El banco sigue arriba —primero
  eliges la palabra— y el botón baja al final de las frases: juntos arriba, el
  resultado salía a una pantalla de distancia de lo que acababas de rellenar.
- **Al fallar sale la respuesta correcta PEGADA al hueco**, en vez de mandar
  a la clave del final de la página. Solo donde se puso algo: regalarle las
  respuestas a quien pulse comprobar con todo en blanco deshace el ejercicio.
  Vaciar el hueco se la lleva, así que se puede volver a intentar.

**Y al comprobarlo en navegador salió lo gordo, que él no había visto: 32
ejercicios no se podían acertar.** `huecos.leer` guardaba como respuesta el
texto de la CLAVE —«**el cartel**» en negrita, «Aquí» con mayúscula— mientras
que la ficha lleva el texto del BANCO —«el cartel»—. El validador ya
comparaba sin marcado (`_plano`), así que el ejercicio pasaba; lo que se
guardaba era el texto crudo y el navegador comparaba eso. **En 30 de los 32
el lector sacaba 0 aciertos con todo bien puesto.** Ahora la respuesta que se
guarda ES la entrada del banco, con lo que negrita, mayúsculas, acentos y
puntuación dejan de importar de una vez.

La guarda que lo encontró no es una prueba de Python: es
`scripts/probar_navegador.js`, que ahora rellena el ejercicio entero
eligiendo la ficha **por su texto** y exige que el marcador diga que están
todas bien. Leyendo el código no se veía.

### 14 audios eran silencio

El profesor pulsó el ▶ de la «y» en la tabla de fonética: «esta letra no
suena». El archivo existía y pesaba 3.501 bytes, así que pasaba las dos
guardas de siempre —no está vacío, no es un `.parcial`— y el sitio le ponía
su botón. **Un ▶ que no suena no se distingue de uno roto**, que es el peor
fallo que puede tener esta página.

Medido con ffmpeg sobre los 11.378: **14 son silencio** (pico por debajo de
−60 dB contra los −3 a −10 de una frase normal), entre ellas «Ana: ¿Conoces a
García Márquez?».

- **`generar_audio.mudo()`** lo contesta con ffmpeg y no con una cuenta sobre
  el tamaño: un archivo corto puede ser una palabra corta. Si ffmpeg no está,
  devuelve `False` —no se inventa un silencio—, porque quitarle el ▶ a una
  frase que sí suena sería peor.
- **`docs/audio/mudos.json`** guarda el TEXTO y no el hash: se lee qué frase
  es sin descifrar nada, `escribir_indice` la deja fuera —así el sitio no le
  pone ▶— y `faltan()` no la vuelve a pagar en cada corrida.
- **`--mudos`** es el barrido de una vez, para lo que ya estaba locutado;
  tarda tres minutos y no gasta un céntimo. **Una tanda nueva se mide sola**
  al terminar, que es el momento de enterarse.
- **`--reintentar`** borra los apartados y la lista para volver a pedirlos:
  un silencio puede ser la letra o un fallo suelto de la API, y desde fuera
  se ven igual. Lo que vuelva mudo otra vez se aparta solo, así que
  reintentar no puede dejar un ▶ que no suena.

El índice pasa de 11.378 a **11.364** frases mientras las catorce están
apartadas, y la «y» y la «h» se quedan sin botón. **Al reintentarlas el mismo
día se arreglaron las catorce: ver la nota de abajo.**

**Y una guarda se puso en rojo por esto, con razón.**
`test_la_palabra_fallada_se_puede_OIR` exigía que las palabras del quiz
estuvieran TODAS locutadas, y dos de ellas —«toma» y «la vela · soplar las
velas»— son de las catorce mudas. No se aflojó a un «casi todas»: ahora admite
sin audio **solo** lo que esté en `mudos.json` y revienta con cualquier otra,
porque eso sería audio perdido y no silencio. Y las nombra, que es lo que
convierte una excepción en una decisión.

### El ▶ se pulsa con el dedo, y medía 17x13 px

«Los botones de play pueden ser un poquito más grandes para poder apretar».
Lo que crece es la **zona** y no el dibujo: agrandar el triángulo dentro de
una tabla de vocabulario lo convertiría en el protagonista de la celda,
cuando lo que enseña es la palabra de al lado.

La zona pasa a unos **34x34** con un `::after` colocado, que no ocupa sitio y
no mueve un píxel de la maqueta —`padding` no servía: un `<button>` es
`inline-block`, así que el relleno vertical SÍ empuja, y son 13.575 ▶ metidos
en frases y celdas—. Los 9 px de arriba y abajo salen **medidos**: dos ▶ de
la misma columna están a 39,6 px, así que dos zonas de 34 no llegan a
tocarse. Si crecieran más, al pulsar una fila se dispararía la de al lado.

### Y por quinta vez, `\00a0` dentro de `CSS = """..."""`

Al escribir el estilo de la respuesta correcta puse `content:"\00a0→\00a0"`,
que Python lee como escape octal: **un byte NUL en las 394 páginas**. Está
documentado desde el 2026-10-27 y lo volví a hacer igual. La única señal es
que `grep` empiece a decir «binary file matches», y
`test_ninguna_pagina_trae_un_byte_nulo` lo caza. El espacio duro va literal.

## Las catorce mudas se arreglaron, y el recodificado dejó de vivir en mi memoria (2026-10-30)

«Corregir los audios que faltan», el mismo día. `--reintentar` borró los
catorce y la corrida siguiente los volvió a pedir por **0,0036 USD**.

**Volvieron con voz las CATORCE, la «h» y la «y» incluidas** —picos de −3,4 a
−10,6 dB, o sea habla normal—, así que la nota de arriba estaba equivocada en
lo que más importaba: no eran dos letras sin nada que decir y doce fallos
sueltos de la API, eran **catorce fallos sueltos**. Corregido también el
comentario de `MUDOS` en el guion, que afirmaba lo mismo. `mudos.json` ya no
existe: lo sano es que esa lista esté **vacía**, y eso es lo que la convierte
en una red y no en una lista de excepciones del idioma.

El índice vuelve a **11.378** frases y el sitio pasa de 13.575 ▶ a **14.080**
en 355 lecciones. Comprobado en Chromium pulsando los dos botones exactos de
la foto del profesor —las filas «y [й] перед гласной» y «h — не читается
никогда» de `semana-01/dia-3`—: MP3 con 200 y bytes, `aria-pressed` en true
mientras suena y cero errores de JS. Esa página entra en la lista de
`probar_navegador.js`.

**Y `aria-pressed` vuelve a false al acabarse el clip**, que es lo correcto
—el reproductor lo apaga en el evento `ended`— pero hace que una
comprobación escrita a ojo mienta: mi primera medida esperaba 1,8 s y los dos
clips duran 1,06 y 1,56, así que los dos dieron «false» con el audio
funcionando. La señal hay que leerla **mientras suena**.

### El recodificado a 64 kbps estaba en mi memoria y ahora está en el guion

Al ir a subir los catorce aparecieron a **128 kbps**: el recodificado que la
nota del 2026-10-28 describe como obligatorio antes del primer commit **no
existía en ningún archivo del repositorio**. Era una orden de ffmpeg en mi
historial de shell, y por eso se olvidó una vez con una tanda entera ya
generada.

Es el agujero que este proyecto documenta una y otra vez —`repartir_temas.py`
sin nadie que lo llamara, `vigilar_disco.py` sin unidad de systemd—: un paso
que hace falta y no vive en ningún sitio.

- **`generar_audio.recodificar(ruta)`** lo hace, y **la tanda nueva pasa por
  él sola**, entre `generar` y el índice. Lo que se indexa es lo que se
  publica, así que ese orden es la invariante y hay una prueba que lo lee del
  propio guion en vez de confiar en que alguien se acuerde.
- **`--recodificar`** es el barrido de una vez, para lo que ya estaba en
  disco. Corrido hoy sobre los 11.378 tocó **exactamente 14**: es idempotente,
  y eso no es un detalle —recodificar dos veces pierde calidad—.
- **El umbral es `BITS_TOPE` y no una igualdad.** Un archivo ya recodificado
  mide unos 64.500 bps y no 64.000 exactos, así que con `== BITS` se
  recodificaría en cada corrida. Lo delató mirar un archivo viejo con
  `ffprobe`, no razonarlo.
- **El `-f mp3` no es de adorno**, y esto ya costó una tanda el 28: el
  temporal se llama `.parcial` y de esa extensión ffmpeg no deduce el
  formato. Hay una prueba que exige que esa bandera siga en la orden.
- **Escribe aparte y renombra encima**, como el `.parcial` del generador: un
  ffmpeg cortado deja el original intacto y no un MP3 truncado que el sitio
  serviría como bueno. Comprobado con un archivo que no es un MP3.

La carpeta queda en **292 MB**, dentro del límite de 1.024 MB de GitHub
Pages.

### Y la guarda del quiz se arregló sola, que era el objetivo

`test_la_palabra_fallada_se_puede_OIR` admite sin audio **solo** lo que esté
en `mudos.json`. Con la lista vacía vuelve a exigir las 1.198 palabras
locutadas, sin que nadie haya tocado la prueba: eso es lo que se buscaba al
no aflojarla a un «casi todas» el día anterior.

Lo que **sí** hubo que reescribir es `test_ningun_mudo_esta_en_el_indice`,
que exigía «al menos uno» en la lista para no quedarse vacío de sentido. Eso
fija el CONTENIDO de un fichero de datos —el defecto que esta suite ya se
corrigió dos veces en las claves de los tests— y se puso en rojo el día que
se arreglaron los catorce. Ahora mira la RELACIÓN, y un segundo test aparta
uno a mano para que la relación no se compruebe sobre un conjunto vacío.

## «Estos cuadrados se actualizan?»: la rejilla del año nunca cupo (2026-10-30)

El profesor mandó su `kurs.html`: **«marqué la primera clase terminada y no
se marcó»**. Y la página se contradecía sola — el contador decía «3 / 365», la
racha «2 días seguidos» y la cabecera del calendario «2 días de estudio en el
último año», con las 364 casillas grises.

**Medido sobre su propia captura y no mirándola**: cero píxeles del color del
acento en la banda de la rejilla, con el resto en (47,51,54), que es el gris
de una casilla vacía. O sea que las dos casillas marcadas existían —la
cabecera las cuenta del mismo bucle que las pinta— y estaban **fuera de la
parte visible**.

**La causa es una cuenta, y llevaba ahí desde que se escribió la rejilla**:

    52 columnas x 11 px + 51 huecos x 3 px + 6 de relleno = 731 px
    columna de prosa (44rem - 40 de margen)               = 664 px

**Se salía por 67 px en TODA pantalla**, no solo en el móvil como decía su
propio comentario. O sea que la rejilla dependía SIEMPRE del
`scrollLeft=scrollWidth` que el guion le pone al nacer, también en un
escritorio de 1800 px. El día que ese desplazamiento no llegó —una página que
aún se está componiendo, una posición restaurada al volver atrás—, lo que
queda es la rejilla anclada en enero: 362 casillas vacías y los días del
lector a cinco columnas de distancia, fuera de la vista.

**Y no se reproduce pidiéndoselo al navegador.** Medido a 390, 700, 1000,
1280, 1400 y 1800 px, el desplazamiento se pone bien en los seis y las dos
casillas se ven. Por eso la comprobación que de verdad valía no era abrir la
página: era **la aritmética**.

Cómo quedó:

- **La casilla pasa a 10 px y el hueco a 2**: 628 px, que caben en los 664 con
  36 de margen. En el escritorio la rejilla **ya no se desplaza**, así que no
  puede quedarse anclada en ninguna parte.
- **`outline-offset` a 0.** El recuadro de HOY se dibuja FUERA de la casilla,
  así que con el hueco en 2 px un trazo de 2 con desplazamiento de 1 se metía
  en la casilla de al lado. Antes sumaba justo 3 y el hueco era 3: estaba en
  el límite sin que nadie lo hubiera escrito.
- **El desplazamiento se vuelve a poner** en el siguiente fotograma y al
  acabar de cargar, para el móvil, que es donde sigue desbordando. Y **solo si
  sigue en cero**: si no, le quitaría la rejilla de las manos a quien la esté
  moviendo con el dedo.

**Y unas horas después la rejilla dejó de ser de días**: ver la nota de abajo.
Lo de aquí sigue valiendo entero —la cuenta, la casilla de 10 px, el
desplazamiento que se repone— porque el defecto era del ancho y no de lo que
cada casilla significa.

**Las guardas, y cuál de las dos sirve.** La de la aritmética lee las medidas
del CSS —no las escribe— y exige que las columnas quepan; falla con el
código de antes. La del navegador siembra progreso en `kurs.html`, recarga y
exige que las casillas marcadas y la de hoy estén DENTRO de la caja, en
escritorio y a 390 px. **Esa segunda pasaba con el código viejo**, porque aquí
el desplazamiento sí llega: sirve de red para el móvil y para que una casilla
marcada no acabe del color de una vacía, no para lo que se rompió hoy. La
tercera fija que la casilla sea cuadrada, que su alto y su ancho se escriben
en dos reglas distintas.

## La rejilla pasa a ser el CURSO: una casilla por lección (2026-10-30)

Arreglado el ancho, el profesor siguió sin ver lo que esperaba: **«¿por qué
cuando marco terminé la lección el cuadradito no se llena?»**. Y después la
pregunta que lo explicaba todo: **«¿se marca por fecha o se marca por
lección?»**.

**Se marcaba por fecha**, al estilo del calendario de contribuciones de
GitHub: una casilla por día, encendida si ese día estudiaste algo. Con tres
lecciones repartidas en dos días, marcar la tercera no cambiaba nada a la
vista —el cuadro de ese día ya estaba pintado— y eso se lee exactamente como
que no funciona. El defecto no era un fallo: era que la rejilla medía
**constancia** y él esperaba **avance**.

Lo pidió claro: *«debería marcarse por lección, lección 1 cuadradito 1, y
cuando pongas el mouse diga la fecha»*. Hecho, y encaja mejor con este sitio:

- **365 casillas, una por lección**, y las columnas son las **semanas del
  curso**. Eso sale gratis: con `grid-auto-flow:column` y siete filas, la
  casilla 8 cae sola en la semana 2 día 1. La rejilla **es** la cuadrícula del
  calendario del curso, y el día 365 queda solo en la columna 53, que es como
  está escrito el año.
- **El rótulo dice la lección, dónde cae y qué día se hizo**: «Урок 2 · нед. 1,
  день 2 · 2026-10-30».
- **El recuadro marca la primera sin hacer** («здесь вы остановились»), que es
  dónde vas. Antes marcaba hoy, que en una rejilla de lecciones no significa
  nada.
- **53 columnas caben**: 640 px contra los 664 de la columna de prosa. La
  cuenta de la nota de arriba sigue siendo la guarda, ahora contando las
  semanas del propio calendario en vez de un 52 escrito a mano.

**Lo que hubo que guardar, que es la parte delicada.** El navegador sabía *qué*
lecciones hiciste y *qué días* estudiaste, pero no cuál en qué día, así que la
fecha del rótulo no se podía deducir: hace falta una clave nueva,
`curso.cuando`, un mapa {lección: fecha} que se escribe al marcar y se borra al
desmarcar.

- **NO entra en el código de respaldo**, y hay una prueba que lo exige. Ese
  código son 46 bytes de lecciones hechas en 68 caracteres pegables; meterle
  las fechas lo haría crecer y **rompería los códigos que la gente ya tiene
  guardados**, que es lo único de este bloque que no se puede arreglar después.
- **Una lección sin fecha no se inventa ninguna.** Las marcadas antes de que
  esto existiera y las que vienen de un código de respaldo no la tienen: el
  rótulo dice la lección y nada más. Una prueba mira que entre el `if(cuando[q])`
  y el `title` no aparezca `hoy()`.
- **Un `curso.cuando` estropeado cae en vacío** en vez de reventar la página,
  como todas las lecturas de este guion.

**`curso.fechas` se queda** y la racha sigue saliendo de ahí: son dos cosas
distintas y ahora cada una está donde se entiende —el avance en la rejilla, la
constancia en la línea de «2 días seguidos»—.

**Una guarda vieja se puso en rojo y tenía razón.**
`test_el_calendario_no_lee_la_lista_de_dias_dos_veces` exigía que la rejilla y
la racha miraran el MISMO `curso.fechas`. Eso describía el contrato de ayer. No
se aflojó: ahora exige que la rejilla y el CONTADOR cuenten lo mismo —las dos
miran `hechasAhora`, la lista que el contador ya tiene leída—, porque con una
lectura propia una lección podría salir contada arriba y no pintada abajo, y
las dos cifras de la misma caja se contradirían sin que nada fallara.

**Comprobado haciendo lo que él hace**, no leyendo el código: abrir la lección 1
sin ningún progreso, pulsar «Отметить урок пройденным», abrir la lección 2 y
marcarla también, e irse al índice. Salen **dos casillas**, cada una con su
fecha en el rótulo, y el recuadro en la lección 3. Con la rejilla de ayer eso
era **una**.

## El sentido de vuelta: ruso → español (2026-10-30)

El profesor preguntó si se puede hacer el curso al revés, para aprender ruso.
**El código sirve casi entero y las 365 lecciones no**, y lo que decide no es
el trabajo: ese curso lo firmaría alguien que no es nativo de ruso —sería el
alumno y no el profesor—, la lista de errores inversa es más dura (seis casos,
aspecto, verbos de movimiento), y la demanda es asimétrica: muchos
rusohablantes se mudan a España y a América, muy pocos hispanohablantes
necesitan ruso. Con 365 lecciones escritas y cero visitas, el cuello de
botella es que nadie sabe que el sitio existe, no que falte un segundo curso.
**No se hizo.**

Lo que sí se hizo es lo que ya estaba pagado: **el mismo vocabulario al
revés**, en el diccionario y en la baraja. Cero contenido nuevo, cero
céntimos. Lo eligió el profesor sobre una muestra con los datos de verdad, que
es como se eligieron la voz, el estilo de los dibujos, la tipografía, el logo
y la paleta.

**La muestra es la que decidió el diseño**, y encontró tres cosas:

- Las 2.985 palabras dan **2.800 entradas rusas**, no 2.985: **171** palabras
  rusas tienen varios españoles. Y eso no es un defecto que haya que deshacer:
  *автобус* devuelve las cinco formas de decirlo y *играть* devuelve *jugar ·
  tocar · interpretar*, que es lo que este sentido puede enseñar y el otro no.
- **1.080** celdas rusas traen una glosa, y en **7** la glosa va DELANTE
  —«(космический) корабль», «хорошо» (7–8,9)—. Sin quitarla, esas siete se van
  al principio de la lista bajo el paréntesis y no las encuentra nadie
  buscando su palabra. El lado español nunca lo tiene, porque esa columna está
  limpia.
- Una fila no es una entrada rusa: «tomar = и пить, и есть», la misma que ya
  descarta por su cuenta el canal de Telegram. La clave tiene que **empezar**
  por una letra rusa.

### Qué corta la clave y qué no, medido y no elegido a ojo

`exportar_anki.clave_rusa` vive ahí y no en el diccionario ni en la baraja
**porque la usan los dos**: con una copia en cada sitio, el día que alguien la
afine se arregla uno y el otro agrupa de otra manera. Es la lección de
`exportar_anki.filas_de`, que se escribió por lo mismo.

- **Cortan la barra y las flechas**: separan FORMAS de una misma entrada, así
  que «его / её (уточнение)» se junta con «его / её зовут» y «его / её (о
  вещи)», que es justo lo que hay que enseñar.
- **NO cortan la coma ni el punto volado**, aunque lo parezca: ahí la celda
  trae VARIAS entradas —«идти, ходить, ехать», «аккаунт · пароль»—. Con la
  coma salían 2.720 entradas y una tarjeta que preguntaba «идти, ходить,
  ехать» y respondía *ir · quedar bien / mal · tardar · nevar*. Sin ella son
  2.800 y ningún grupo junta cosas distintas. Se vio mirando los grupos más
  grandes, no razonándolo.

### El diccionario: el sentido ruso no cuesta un byte de página

La página se quedó en 83 KB sacando los nombres de los MP3 a su propio
fichero, así que servir las 2.800 entradas rusas —las mismas palabras por
segunda vez— habría deshecho eso. **No se sirven**: `vocabulario/ruso.json`
son 19 KB de **números y nada más** —qué filas forman cada entrada y en qué
orden van— y el navegador arma la lista con el texto que ya está en la página.
La página sube 1,2 KB comprimida, que es el CSS del botón.

- **El botón aparece cuando el fichero ha llegado, y no antes.** Si la
  petición falla, el lector se queda con el sentido de siempre en vez de con
  un botón que abre una lista vacía. Comprobado escondiendo el fichero: sin
  botón, la búsqueda sigue, 2.985 filas y cero errores de JS.
- **La lista rusa se arma al pulsar, no al cargar.** El fichero se pide
  siempre (19 KB) porque es lo que decide si el botón existe; los 2.800 nodos
  se crean una sola vez y cuando hacen falta.
- **El ▶ de una entrada rusa se anuncia en español.** Lo que suena es la
  palabra española, así que leerle al lector de pantalla el `<b>` —que ahí es
  el ruso— sería mentirle. Va en un `data-voz` propio.
- **La voz y la lección son las de la PRIMERA** del grupo, que es la que el
  curso enseña antes.

### La baraja: 3.001 notas, 6.112 tarjetas

Ni un archivo nuevo. La tercera plantilla va envuelta en `{{#Todos}}`, igual
que la del dibujo en `{{#Imagen}}`, y eso resuelve lo único difícil de este
sentido: **si cada nota sacara su tarjeta de vuelta habría 171 anversos
repetidos con respuestas distintas**, que en repaso espaciado es ruido puro.
Solo una nota de cada grupo lleva `Todos` —y lleva todas las respuestas—, así
que sale **una tarjeta por palabra rusa** y enseña las cinco formas de decir
«автобус». Lo eligió el profesor: juntarlas o dejar esas 171 sin tarjeta.

- **El campo nuevo va al FINAL de `CAMPOS`.** El modelo tiene un id fijo para
  que volver a importar actualice la baraja del alumno en vez de crearle otra
  al lado; moviendo los campos que ya existen, sus notas se reordenarían
  solas.
- **Lo que no se puede comprobar desde aquí**: Anki tiene que aceptar un
  modelo con el mismo id y un campo más. Las versiones modernas actualizan el
  tipo de nota al importar; una vieja puede quejarse. Hoy el riesgo es cero
  porque la baraja no la ha descargado nadie —el sitio no tiene visitas— pero
  conviene saberlo antes de volver a tocar `CAMPOS`.
- Pesa **64,0 MB** (eran 60,7). Sigue por debajo de los 100 MB que GitHub
  rechaza y por encima de los 50 en que avisa. El camino el día que crezca
  sigue siendo un *release*, con su precio ya escrito.

### Comprobado en navegador, que es donde esto se ve

`probar_navegador.js` añade `slovar.html` y usa el diccionario: pulsa el
botón, exige que las dos listas se intercambien, que «автобус» traiga sus
cinco españoles, que el ▶ de una entrada rusa se anuncie en español, que el
enlace a la lección no salga repetido —«урок 87 урок 87», que ya pasó—, que
buscar en ruso filtre y que al volver el sentido de siempre quede como estaba.
Leyendo el HTML no se ve ni una entrada rusa, así que o se comprueba ahí o no
lo comprueba nadie.

## Siete pruebas llevaban semanas sin ejecutarse (2026-10-30)

Salió al contar las clases para repartir la suite: `TestElMapaDeUnidades`
estaba definida **dos veces** en `tests/test_curso.py`, en la línea 1430 y en
la 3814. **En Python la segunda definición gana**, así que las SIETE de la
primera —una tarjeta por unidad, su episodio, el enlace a su primera lección,
las unidades apagadas, el mapa saliéndose de la columna de prosa, el pie
alineado abajo y los tres idiomas— no corrían desde que se escribió la
segunda, y la suite seguía en verde.

Es exactamente el accidente del formato `receta` en el proyecto hermano
(2026-10-13), y el síntoma es el peor que hay: **nada se pone en rojo**. Allí
lo delató `git status`; aquí, contar las clases con el cargador de unittest y
ver un nombre repetido.

La segunda pasa a llamarse `TestElDibujoYElProgresoDelMapa`, que es lo que de
verdad comprueba (el dibujo por tarjeta, la barra midiendo lo del lector y el
efecto al aparecer, del 2026-10-29). **Las siete resucitadas pasan todas**, o
sea que no tapaban ningún defecto: lo que se había perdido era la guarda.

Y de paso quedan dos cosas de método que ya estaban escritas y volví a
tropezar con las dos el mismo día:

- **`| tail -8` sobre un comando largo deja el log VACÍO hasta que termina**,
  así que una suite que se murió por `timeout` no dice ni por dónde iba. Es lo
  que pasó con los 7.779 FALLO del audio el 2026-10-28. Se escribe a un
  fichero y se mira el fichero.
- **`pkill -f "unittest tests.test_curso"` mata su propia shell**, porque la
  línea de órdenes del comando que hace el `pkill` contiene el patrón que
  busca. Es el mismo caso que `pkill -f 'ffmpeg -nostdin'`, también anotado.

## La baraja sale de git: más de la mitad del repositorio eran copias suyas (2026-10-30)

«Arreglarlo», sobre el aviso de que el `.apkg` pasaba de 50 MB. **Y el número
que le di estaba mal**: no pasó de 60,7 a 64,0 MB — ya pesaba **63,7** antes
de tocarla, y mi cambio sumó 0,3. El 60,7 venía de estas notas y estaba viejo.

Medido antes de arreglar nada, que es lo que cambió la solución:

    .apkg hoy ............... 64,0 MB  (57,5 de MP3 + 4,6 de webp + 1,5 la base)
    versiones en la historia ....... 5
    lo que ocupan ................ 235 MB
    .git entero .................. 442 MB

O sea que **más de la mitad del repositorio son copias viejas de ese archivo**,
y encima sus 2.982 MP3 duplican `docs/audio`, que ya está versionado al lado.
Git no puede comprimirlos ni deltarlos —ya vienen comprimidos; medido dentro
del zip, `compress_size == file_size`— así que cada regeneración es un blob
nuevo **entero**.

**Lo que NO era el arreglo, y conviene que quede escrito**: encoger el audio.
57,5 MB son 2.982 voces a 64 kbps; a 32 la baraja bajaría a unos 34 MB, pero
esto es un curso de PRONUNCIACIÓN y a ese bitrate lo primero que se va son las
sibilantes y la vocal átona, que es justo lo que el alumno tiene que oír. El
tamaño no era el defecto.

### El arreglo: una release de TAG FIJO, armada por GitHub

`.github/workflows/baraja.yml` arma la baraja y la sube como archivo de la
release `baraja`. Una release **no vive en git**, así que el repositorio deja
de crecer 64 MB por regeneración.

- **El tag es fijo y por eso esto funciona.** El precio que este camino tenía
  escrito desde el 2026-10-27 era «una URL absoluta en el generador, crear la
  release y acordarse de actualizarla; si se desincronizan, el botón da 404».
  Con un tag fijo y `gh release upload --clobber`, **la URL no cambia nunca** y
  no hay nada que sincronizar: el archivo se reemplaza debajo.
- **El manifiesto sigue en git** (`docs/vocabulario/baraja.json`, cinco
  números) y lo actualiza el propio trabajo. Es lo que el sitio lee para pintar
  el bloque sin abrir 64 MB, que ya era el diseño.
- **`baraja.release` en `sitio.yaml` es el interruptor.** Vacío = se enlaza el
  archivo de al lado, como antes. **Vaciarlo es el camino de vuelta**, y es lo
  que hay que hacer si algún día se borra la release: un botón de descarga a
  un 404 es peor que no ofrecerla.
- **`baraja.json` NO está entre los caminos que disparan el trabajo**, porque
  lo escribe él mismo y se perseguiría la cola. Hay una prueba.
- **`genanki` no estaba en `requirements.txt`** —lo tenía este contenedor por
  casualidad— y en Actions se instala SOLO lo que ese fichero diga. Es
  exactamente el descuido que ya tuvo Pillow con la palabra del día, y van dos.

**El orden importó y por eso fueron dos commits.** Primero el trabajo, con el
archivo y el enlace intactos; se comprobó que la release existiera y que el
archivo subido pesara **64 009 258 bytes, los mismos que el local**; y solo
entonces se cambió el enlace y se sacó el `.apkg` de git. Al revés, un fallo
del trabajo habría dejado la descarga rota sin nada a lo que volver.
Verificado por la API de GitHub, no descargándolo: desde este contenedor no se
alcanza.

**Lo que esto NO arregla, y es decisión del profesor**: los 235 MB que ya están
en la historia siguen ahí. Sacarlos pide reescribir la historia
(`git filter-repo`) y un `push --force` sobre `main`, que invalida cualquier
copia que alguien tenga del repositorio. No se hizo sin permiso. A partir de
hoy no crece más, que es la mitad que sí se podía cerrar sola.

## Estado (2026-10-29)

**Lo que el alumno puede hacer en el sitio, después de la tanda del 29:**

| | |
|---|---|
| leer las lecciones | 365 días, con 14 080 botones ▶ |
| escribir en los ejercicios | 3 933 casillas, y 730 huecos que se rellenan pulsando en 101 lecciones |
| contestarse | 68 días con test de opción múltiple **+ 244 con el de las palabras del día** |
| **comprobar las palabras del día** | 1 198 preguntas en 244 lecciones, con el ▶ de la que se falla |
| **grabarse y compararse** | en las 355 lecciones que tienen audio |
| **buscar una palabra** | las 2 985 del curso en `slovar.html`, **en los dos sentidos** (2 800 entradas rusas) |
| llevar la cuenta | el contador, la racha, **el año en 364 casillas** y el mapa de las 24 unidades |
| **llevarse un certificado** | al cerrar A1 (154) y A2 (365) |
| llevarse el vocabulario | la baraja de Anki: 3 001 notas y **6 112 tarjetas**, 64,0 MB, **desde una release y ya no desde git** |
| no perderlo | el código de respaldo, 68 caracteres |

Nada de eso sale del navegador: no hay registro, no hay servidor y la
grabación muere con la pestaña.

## Estado (2026-10-28)

- Programa anual completo (365 días) y documentación del método.
- **EL CURSO ESTÁ ESCRITO ENTERO: 365 de 365 lecciones** (semanas 1-53), el A1
  y el A2 completos con sus veinticuatro unidades, la fase final con dos
  simulacros del DELE A2, el proyecto, el examen final y el día de reserva.
  **2 998 tarjetas** de vocabulario y los 24 episodios de Ana e Iván.
  **350 de 365 están revisadas** (`revisado: true`) desde el 2026-10-29,
  cuando el profesor las dio por buenas. Las otras quince las rechazó
  `validar.py` por llevar un `[VERIFICAR]` pendiente —once de ellas porque la
  propia lección ENSEÑA el marcador— y siguen marcadas como borrador en el
  sitio; ver «Las quince que el validador no dejó firmar». La regla 6 sigue en
  pie: la bandera es su firma y la pone él.
  **`docs/` está al día**: las 365 lecciones construidas y publicadas, con la
  tira de dibujos del héroe —la misma fila en el móvil y en el escritorio—,
  la guía de los seis pasos dentro de cada lección y la tipografía propia
  (Literata + Onest, autoalojada). La suite entera pasa: **451 pruebas** en 60
  clases (2026-10-30), una de ellas en navegador de verdad.
- **68 días son contestables o legibles con su clave**: 23 tests de unidad, 43
  mini-tests de repaso (de 47 — los otros cuatro piden escribir la forma, no
  elegir) y los 2 exámenes de nivel. El más largo es el quiz de 50 ítems de la
  semana 50; el examen final son 60, de los cuales **40 son literalmente los
  del examen de A1**, para que la comparación que aquel día prometió se pueda
  hacer de verdad.
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
  falta**. **El CMP está publicado** (2026-10-29, lo confirmó el profesor
  haciéndolo en su panel; desde este contenedor Google no se puede abrir —
  `adsense.google.com` y `support.google.com` dan `000`). Queda solo esperar el
  veredicto. Ver «El CMP, publicado» más abajo. **El sitio ya tiene icono**
  desde el 2026-10-29 (`scripts/icono.py`, la eñe crema sobre terracota en
  `docs/img/`): hasta ese día la pestaña del navegador enseñaba el globo gris.
- **El audio está COMPLETO** (2026-10-28): las **11 378 frases** del curso
  locutadas con la voz `shimmer` —1,30 USD el 26 de octubre y **2,85 hoy**,
  4,15 en total—, 292 MB a 64 kbps, y **14 080 botones ▶ en las 365
  lecciones**, que eran 4.225 en 94. Las **14 que volvieron mudas** se
  repidieron el 2026-10-30 y volvieron las catorce con voz: `mudos.json` ya
  no existe y el índice está completo. Verificado sobre los archivos de disco:
  todos a 64 000 bps, ninguno vacío y ninguno ilegible. Y comprobado **en
  navegador**: el ▶ pide su MP3 y suena, con una guarda en
  `probar_navegador.js` que lo exige en 25 páginas.
- **La revisión mecánica del curso entero está hecha y sus hallazgos
  cerrados** (2026-10-28, `revisiones/2026-10-28.md`): `validar.py` da 365
  lecciones y 0 problemas, y están a **cero** los ítems con dos opciones
  iguales, las palabras con letras de los dos alfabetos, los subjuntivos en lo
  que el alumno produce, las entradas enseñadas dos veces como nuevas y las
  **formas verbales usadas antes de su lección** —que empezaron siendo 90,
  contando el pluscuamperfecto que no enseña ninguna lección—. Las nueve
  guardas viven en `TestLaRevisionDelCurso`.
- **La baraja está al día y con voz**: 3001 palabras, **3 001 con voz** (eran
  913 por la mañana y 2 898 a media tarde), 311 con dibujo, 25 subbarajas,
  3 282 medios, **60,7 MB** como los cuenta GitHub. Ninguna tarjeta queda
  muda.
- Pendiente, y ya no hay nada de contenido en la lista:
  - **las 14 preguntas del test de nivel**, que siguen sin revisar (regla 6).
    Las lecciones ya no —el profesor firmó las 365 el 2026-10-29— y **los 300
    dibujos tampoco: los aprobó el 2026-10-30**. Para volver a mirar una
    lección, `scripts/revisado.py` lleva la cuenta y `--quitar` devuelve a
    borrador lo que haga falta;
  - los **libros de referencia** que quedaron sin analizar y lo de «Pendiente
    de revision del profesor» de arriba.
