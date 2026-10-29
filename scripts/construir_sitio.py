#!/usr/bin/env python3
"""Convierte el curso en el sitio público de docs/, en tres idiomas.

    .venv/bin/python scripts/construir_sitio.py
    .venv/bin/python scripts/construir_sitio.py --destino /tmp/sitio

Estructura:

    index.html  kurs.html  o-kurse.html  kontakt.html  privacy.html   (ruso)
    es/…  en/…                                   las mismas, traducidas
    semana-XX/dia-N.html                         las lecciones, solo en ruso
    programa/*.html                              documentación, para el profesor
    sitemap.xml  robots.txt

**Las lecciones no se traducen y no es un olvido**: el curso enseña español a
través del ruso, así que la lección en español no tendría sentido. Lo que se
traduce es la web que las rodea, para que alguien que no lee ruso entienda qué
es esto. Los textos están en `web/textos.yaml` y la configuración (dominio,
anuncios, analítica) en `web/sitio.yaml`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import shutil
import urllib.parse
import sys

import markdown
import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import pruebas  # noqa: E402
import huecos  # noqa: E402
import quiz_lexico  # noqa: E402
import validar  # noqa: E402
# Se importa por `limpiar`: la palabra del índice de imágenes está limpia de
# negritas, del 🌎 y de la barra de variantes, así que aquí hay que limpiar la
# celda EXACTAMENTE igual o no casaría ninguna. Dos copias de esa regla es como
# se descubre tarde que una de las dos se quedó vieja.
import generar_imagenes  # noqa: E402
# Y por `tarjetas_de`: la traducción de las doce palabras de la portada sale
# del vocabulario de las lecciones, no de una lista aquí. Si se escribieran a
# mano, el día que el profesor corrigiera una traducción la portada seguiría
# enseñando la vieja.
import exportar_anki  # noqa: E402

DOCS = RAIZ / "docs"
CONFIG = RAIZ / "web" / "sitio.yaml"
TEXTOS = RAIZ / "web" / "textos.yaml"
TEST = RAIZ / "programa" / "test-nivel.yaml"
# El nombre del índice de audio: lo escribe generar_audio.py y lo leen
# tanto el generador como las pruebas, así que vive en un solo sitio.
INDICE_AUDIO = "indice.json"
# Y el de los dibujos del vocabulario, que lo deja scripts/generar_imagenes.py
INDICE_IMG = "indice.json"

# La baraja de tarjetas. El `.apkg` lo escribe scripts/exportar_apkg.py y los
# TSV scripts/exportar_anki.py; aquí solo se copian y se enlazan, igual que con
# el audio: generar es una decisión y construir el sitio no puede gastar.
VOCABULARIO_WEB = "vocabulario"
MANIFIESTO_BARAJA = "baraja.json"

# La tarjeta de la vista previa al compartir. La compone
# scripts/tarjeta_social.py con los dibujos del curso; aquí solo se declara si
# está, porque un `og:image` que da 404 es peor que ninguno.
TARJETA_SOCIAL = "img/tarjeta.png"
EXTENSIONES = ["tables", "fenced_code", "sane_lists", "toc", "attr_list"]


class Tachado(markdown.extensions.Extension):
    """~~así~~ → <del>así</del>.

    Python-Markdown no trae tachado y las lecciones lo usan para la letra muda
    (~~h~~otel) y para la forma incorrecta (~~Yo gusto~~), que es justo donde el
    sentido depende de que se vea tachado: sin esto salían las tildes a la vista
    y la forma mala parecía la buena."""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            markdown.inlinepatterns.SimpleTagInlineProcessor(r"(~~)(.+?)~~", "del"),
            "tachado", 65)

# Las diez caras de Literata (cuerpo) y Onest (títulos y botones), servidas
# desde ESTE dominio y no desde Google.
#
# El profesor preguntó si la fuente no era aburrida, y lo era por una razón
# concreta: el sitio no cargaba ninguna. El cuerpo decía `ui-serif, Georgia,
# "Times New Roman"` y los títulos `ui-sans-serif, system-ui`, o sea que en
# Windows y en Android el cirílico caía en Times o en una fallback mediocre
# —la cara de un libro de texto de 1998— mientras que en iPhone caía en New
# York y se veía bien. El sitio se veía PEOR justo en los aparatos del
# público al que va dirigido.
#
# **No se enlaza a Google Fonts, y eso no es manía.** Dos razones: la política
# de privacidad de este sitio promete que sin anuncios no se carga nada de
# terceros, y un <link> a fonts.googleapis.com la volvería mentira; y hay
# sentencias alemanas que multan por incrustar Google Fonts, porque manda la
# IP del visitante a Google. Alemania es uno de los países del público. Los
# .woff2 están en docs/fonts/ y se sirven desde el dominio propio.
#
# Cada cara trae su `unicode-range`, así que el navegador descarga SOLO lo que
# la página usa: una lección rusa no se baja el latino hasta que encuentra el
# primer ejemplo español. Y `font-display:swap` enseña el texto con la fuente
# del sistema mientras llega la buena, que es lo contrario de una página en
# blanco esperando.
#
# La cursiva es real y no sintética: el curso pone TODOS los ejemplos
# españoles en <em>, y un navegador que inclina la redonda deja un texto
# sucio en la mitad de cada lección.
CARAS = """@font-face{font-family:'Literata';font-style:normal;font-weight:400;font-display:swap;src:url({raiz}/fonts/literata-cyrillic-400.woff2) format('woff2');unicode-range:U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116}
@font-face{font-family:'Literata';font-style:italic;font-weight:400;font-display:swap;src:url({raiz}/fonts/literata-cyrillic-400i.woff2) format('woff2');unicode-range:U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116}
@font-face{font-family:'Literata';font-style:normal;font-weight:700;font-display:swap;src:url({raiz}/fonts/literata-cyrillic-700.woff2) format('woff2');unicode-range:U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116}
@font-face{font-family:'Literata';font-style:normal;font-weight:400;font-display:swap;src:url({raiz}/fonts/literata-latin-400.woff2) format('woff2');unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}
@font-face{font-family:'Literata';font-style:italic;font-weight:400;font-display:swap;src:url({raiz}/fonts/literata-latin-400i.woff2) format('woff2');unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}
@font-face{font-family:'Literata';font-style:normal;font-weight:700;font-display:swap;src:url({raiz}/fonts/literata-latin-700.woff2) format('woff2');unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}
@font-face{font-family:'Onest';font-style:normal;font-weight:400;font-display:swap;src:url({raiz}/fonts/onest-cyrillic-400.woff2) format('woff2');unicode-range:U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116}
@font-face{font-family:'Onest';font-style:normal;font-weight:700;font-display:swap;src:url({raiz}/fonts/onest-cyrillic-700.woff2) format('woff2');unicode-range:U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116}
@font-face{font-family:'Onest';font-style:normal;font-weight:400;font-display:swap;src:url({raiz}/fonts/onest-latin-400.woff2) format('woff2');unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}
@font-face{font-family:'Onest';font-style:normal;font-weight:700;font-display:swap;src:url({raiz}/fonts/onest-latin-700.woff2) format('woff2');unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}"""



def caras(raiz: str) -> str:
    """Las @font-face con la ruta resuelta para la profundidad de la página.

    No se puede meter en `CSS` y pasarlo por `.format()`: la hoja entera está
    llena de llaves de CSS y cada una habría que duplicarla. Se concatena."""
    return CARAS.replace("{raiz}", raiz)


CSS = """
/* Tres estados: lo que diga el sistema, o lo que el lector elija con el botón
   de la luna. El atributo data-tema del <html> gana siempre sobre el sistema;
   lo escribe un script de dos líneas en <head> para que no haya parpadeo. */
:root{
  color-scheme:light;
  /* Blanco con un solo acento, elegido por el profesor sobre una lámina con
     cuatro paletas aplicadas a su propia portada (2026-10-29). El acento es
     el MISMO terracota de antes, y eso no es inercia: es el color del logo
     que eligió el 29 por la mañana, así que la eñe de la pestaña, los
     botones y la caja de consentimiento siguen hablando el mismo idioma.
     Lo que se fue es el crema. */
  --papel:#ffffff; --tinta:#101113; --tenue:#6b7076; --linea:#dcdde0;
  --acento:#b03f26; --acento-suave:#fbeee9; --celeste:#55585e; --celeste-suave:#f1f2f3;
  --realce:#fdeee9; --tarjeta:#f4f4f5; --sombra:0 1px 2px rgba(16,17,19,.06);
  --ancho:44rem;
}
@media(prefers-color-scheme:dark){:root:not([data-tema="light"]){
  color-scheme:dark;
  /* La noche se neutraliza con el día: la tinta era crema (#e8e4da) para ir
     con el papel crema, y sobre un sitio blanco y gris eso se lee amarillo. */
  --papel:#121316; --tinta:#e7e8ea; --tenue:#9b9fa6; --linea:#303337;
  --acento:#f0896a; --acento-suave:#2a1d19; --celeste:#a8adb5; --celeste-suave:#1c1e22;
  --realce:#2a2718; --tarjeta:#1c1e21; --sombra:none;
}}
:root[data-tema="dark"]{
  color-scheme:dark;
  /* La noche se neutraliza con el día: la tinta era crema (#e8e4da) para ir
     con el papel crema, y sobre un sitio blanco y gris eso se lee amarillo. */
  --papel:#121316; --tinta:#e7e8ea; --tenue:#9b9fa6; --linea:#303337;
  --acento:#f0896a; --acento-suave:#2a1d19; --celeste:#a8adb5; --celeste-suave:#1c1e22;
  --realce:#2a2718; --tarjeta:#1c1e21; --sombra:none;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--papel);color:var(--tinta);
  font:400 17px/1.65 Literata,ui-serif,Georgia,"Times New Roman",serif;
  -webkit-font-smoothing:antialiased;overflow-wrap:break-word}
.sans{font-family:Onest,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.envoltorio{max-width:var(--ancho);margin:0 auto;padding:0 20px}

/* ---- cabecera ---- */
/* En el móvil la cabecera NO se queda pegada: ocupa dos filas y una lección es
   una lectura larga, así que robaría una sexta parte de la pantalla todo el
   rato. A partir de 40rem cabe en una fila y ahí sí se queda. */
header.sitio{background:var(--papel);border-bottom:1px solid var(--linea)}
@media(min-width:40rem){header.sitio{position:sticky;top:0;z-index:20;
  background:color-mix(in srgb,var(--papel) 92%,transparent);backdrop-filter:saturate(1.6) blur(8px)}
  html{scroll-padding-top:4rem}}
header.sitio .envoltorio{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem .9rem;padding-block:.5rem;
  font-family:Onest,ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:.86rem}
header.sitio a{color:var(--tenue);text-decoration:none;white-space:nowrap}
header.sitio a:hover,header.sitio nav.paginas a[aria-current]{color:var(--acento)}
/* El título cede espacio antes que el selector de idioma: en un móvil
   estrecho se recorta con puntos suspensivos, pero el selector no se sale. */
header.sitio .marca{font-weight:650;color:var(--tinta);font-size:.95rem;letter-spacing:-.01em;
  flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis}
header.sitio nav.paginas{display:flex;gap:.9rem;order:3;flex:1 0 100%;overflow-x:auto;
  scrollbar-width:none;padding-bottom:.1rem}
header.sitio nav.paginas::-webkit-scrollbar{display:none}
.idiomas{display:flex;gap:.2rem;flex:0 0 auto;border:1px solid var(--linea);border-radius:999px;padding:2px}
.idiomas a,.idiomas span{padding:.12rem .5rem;border-radius:999px;font-size:.75rem;font-weight:600;
  text-transform:uppercase;letter-spacing:.05em;line-height:1.5}
.idiomas [aria-current]{background:var(--acento);color:#fff}
/* Los idiomas en los que esta página no existe: se ven apagados, se pulsan y
   lo que abren es el aviso de abajo. Enlazarlos movía al lector de sitio. */
.idiomas .apagado{color:var(--tenue);opacity:.6;cursor:pointer;background:none;border:0;
  font:inherit;font-size:.75rem;font-weight:600}
.idiomas .apagado:hover{opacity:1}
/* El aviso de «aquí no hay versión en ese idioma»: ocupa toda la fila de la
   cabecera para que se lea, y nace oculto porque sin JavaScript los botones no
   hacen nada y un aviso suelto no diría nada de nada. */
.sin-idioma{flex:1 0 100%;order:4;margin:.3rem 0 0;font-size:.82rem;color:var(--tenue);
  font-family:Onest,ui-sans-serif,system-ui,sans-serif}
.sin-idioma a{color:var(--acento);font-weight:600}
.tema{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;
  width:30px;height:30px;padding:0;border:1px solid var(--linea);border-radius:999px;
  background:transparent;color:var(--tenue);cursor:pointer;-webkit-tap-highlight-color:transparent}
.tema:hover{color:var(--acento);border-color:var(--acento)}
.tema svg{display:block}
/* De día se ve la luna (pulsa y se hace de noche); de noche, el sol. */
.tema .sol{display:none}
@media(prefers-color-scheme:dark){
  :root:not([data-tema="light"]) .tema .luna{display:none}
  :root:not([data-tema="light"]) .tema .sol{display:block}}
:root[data-tema="dark"] .tema .luna{display:none}
:root[data-tema="dark"] .tema .sol{display:block}
:root[data-tema="light"] .tema .luna{display:block}
:root[data-tema="light"] .tema .sol{display:none}

/* el marco del curso: los niveles y el examen al que lleva. Discreto a
   propósito —es un respaldo, no un reclamo— y con el acento solo en el nombre
   del examen. */
.marco{font-size:.9rem;color:var(--tenue);border-inline-start:3px solid var(--celeste);
  padding-inline-start:.8rem;margin:1rem 0}
/* los huecos que se rellenan pulsando una ficha. Las fichas arriba y los
   huecos debajo, que es el orden en que se usa: eliges la palabra y luego
   dónde va. */
.fichas{display:flex;flex-wrap:wrap;gap:.45rem;margin:.9rem 0}
.ficha{padding:.35rem .8rem;border:1px solid var(--linea);border-radius:999px;
  background:var(--tarjeta);color:inherit;cursor:pointer;font:inherit;font-size:.9rem}
.ficha:hover{border-color:var(--acento)}
.ficha[aria-pressed="true"]{background:var(--acento);color:#fff;border-color:var(--acento)}
.ficha.gastada{opacity:.35;pointer-events:none}
/* El hueco vacío es una raya; lleno, una pastilla. Con un ancho mínimo para
   que la frase no baile al rellenarse. */
.hueco{display:inline-block;min-width:5.5rem;padding:0 .35rem;cursor:pointer;
  border-bottom:2px solid var(--acento);text-align:center;font-weight:600}
.hueco:empty::before{content:" "}
.hueco.bien{border-color:#2e7d4f;color:#2e7d4f}
.hueco.mal{border-color:#b3332b;color:#b3332b}
/* Y el hueco que se ESCRIBE, que son casi todos: 1.398 de los 1.587. No
   lleva ficha que pulsar porque su ejercicio no trae banco de palabras, así
   que se teclea. Sigue pareciendo la raya que sustituye —sin caja, solo el
   subrayado— para que la frase se lea igual que en papel. */
/* El ancho se fija y no se deja al navegador: un `<input>` sin ancho mide
   lo que su `size` por defecto —unos 230 px— y partía en dos los renglones
   que llevan dos huecos. El guion lo hace crecer al teclear. */
.hueco-escribir{display:inline-block;width:5.5rem;max-width:100%;
  padding:0 .3rem;border:0;border-bottom:2px solid var(--acento);
  background:transparent;color:var(--tinta);font:inherit;font-weight:600;
  text-align:center;border-radius:0}
.hueco-escribir:focus{outline:none;background:var(--acento-suave)}
.huecos-pie{display:flex;align-items:center;gap:.8rem;margin:.9rem 0}
.marcador{font-size:.9rem;color:var(--tenue)}
/* compartir: tres botones iguales al pie de la lección. Discretos —son una
   oferta y no el siguiente paso, que es la lección de al lado— y del mismo
   tamaño entre sí, para que ninguno parezca el principal. */
.compartir{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:1.8rem 0 0;
  padding-top:1.1rem;border-top:1px solid var(--linea)}
.compartir .de-que{font-size:.85rem;color:var(--tenue);margin-inline-end:.2rem}
.red{display:inline-block;padding:.4rem .85rem;border:1px solid var(--linea);
  border-radius:999px;background:transparent;color:var(--acento);cursor:pointer;
  font:inherit;font-size:.85rem;text-decoration:none}
.red:hover{border-color:var(--acento)}
.seguir{margin:.5rem 0 0;font-size:.85rem}
/* el respaldo del progreso: un código que el alumno se lleva. Los dos campos
   a ancho completo porque el código son 64 caracteres y en el móvil, en un
   campo corto, no se ve si está entero. */
.respaldo{margin:.9rem 0 0}
.respaldo input{display:block;width:100%;margin:.6rem 0;padding:.55rem .7rem;
  border:1px solid var(--linea);border-radius:8px;background:var(--fondo);
  color:inherit;font-family:ui-monospace,monospace;font-size:.85rem}
.respaldo .enlace{background:none;border:0;padding:0;margin-inline-start:.6rem;
  color:var(--acento);text-decoration:underline;cursor:pointer;font:inherit}
.aviso-chico{margin:.4rem 0 0;font-size:.82rem;color:var(--tenue)}
/* Las listas de «qué hace falta» y del DELE: cada punto es un párrafo corto
   con su negrita, no una palabra, así que necesitan aire entre ellos. */
.lista-larga{margin:.6rem 0 1rem;padding-inline-start:1.2rem}
.lista-larga li{margin:0 0 .7rem}
.lista-larga li:last-child{margin-bottom:0}
/* El saludo al marcar la lección, la racha y el campo del nombre. El campo
   se envuelve en varias líneas a propósito: en el móvil, una etiqueta, una
   casilla y un botón en la misma fila dejan la casilla en cuarenta píxeles. */
.saludo{margin:.6rem 0 0;font-family:Onest,ui-sans-serif,system-ui,sans-serif;
  font-weight:600;color:var(--acento)}
.racha{margin:.5rem 0 0;font-family:Onest,ui-sans-serif,system-ui,sans-serif;
  font-size:.92rem;color:var(--tinta)}
.pide-nombre{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:.7rem 0 0;
  font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.92rem}
.pide-nombre input{flex:1 1 9rem;min-width:7rem;padding:.35rem .5rem;
  border:1px solid var(--linea);border-radius:8px;background:var(--papel);color:var(--tinta);
  font:inherit}
.pide-nombre .aviso-chico{flex:1 0 100%;margin:0}
/* Grabarse y oírse. Mismo marco que el quiz: los dos son lo que se hace
   DESPUÉS de la lección, no un apartado más de ella. */
.grabar-bloque{margin:2rem 0 0;padding:1.1rem 1.2rem;border:1px solid var(--linea);
  border-radius:12px;background:var(--tarjeta)}
.grabar-bloque h2{margin:0 0 .3rem;border:0;padding:0;font-size:1.05rem}
.grabar-bloque>p{margin:0 0 .6rem;font-size:.92rem;color:var(--tenue)}
.grabar-bloque .botones{margin:0}
/* El test de las palabras del día. Usa las cajas del test de nivel —son el
   mismo trasto— y lo único propio es el marco, que lo separa de los
   ejercicios de la lección sin parecer otro apartado. */
.quiz-bloque{margin:2rem 0 0;padding:1.1rem 1.2rem;border:1px solid var(--linea);
  border-radius:12px;background:var(--tarjeta)}
.quiz-bloque h2{margin:0 0 .3rem;border:0;padding:0;font-size:1.05rem}
.quiz-bloque p{margin:0 0 .6rem;font-size:.92rem;color:var(--tenue)}
/* El calendario del año: una casilla por día y las columnas son semanas.
   La racha ya se contaba desde el 2026-10-29 pero era un número («7 дней»);
   la rejilla dice lo mismo y además enseña los huecos, que es lo que hace
   volver al día siguiente. No mide nada nuevo: hace visible `curso.fechas`.
   En el móvil 52 columnas no caben, así que desborda y se desplaza sola
   hasta hoy, que es el extremo derecho. */
.calendario{margin:.9rem 0 0;font-family:Onest,ui-sans-serif,system-ui,sans-serif}
.cal-cab{display:flex;flex-wrap:wrap;gap:.5rem;align-items:baseline;margin:0 0 .45rem;
  font-size:.88rem}
.cal-cab strong{font-weight:650}
.cal-cab span{color:var(--tenue)}
.cal-rejilla{display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,11px);
  gap:3px;overflow-x:auto;padding:2px 3px 4px}
.cal-dia{width:11px;height:11px;border-radius:3px;background:var(--linea)}
.cal-dia.hecho{background:var(--acento)}
.cal-dia.futuro{background:transparent}
.cal-dia.es-hoy{outline:2px solid var(--tinta);outline-offset:1px}
/* El certificado. Sale solo cuando un nivel está cerrado, así que la mayoría
   no lo verá nunca y por eso no puede ocupar sitio de más. */
.diploma-caja{margin:.9rem 0 0;font-family:Onest,ui-sans-serif,system-ui,sans-serif;
  font-size:.92rem}
.diploma-caja p{margin:0 0 .4rem}
/* la baraja de tarjetas: dos descargas, la de Anki primero. En tarjeta y no
   en una lista suelta porque es una oferta, no un apartado del curso. */
.baraja{margin:2rem 0;padding:1.1rem 1.2rem;border:1px solid var(--linea);
  border-radius:12px;background:var(--tarjeta)}
.baraja h2{margin:0 0 .4rem;font-size:1.05rem}
.baraja>p{margin:0 0 .9rem}
.baraja .bajar{display:flex;flex-wrap:wrap;gap:.6rem}
.baraja .bajar a{flex:1 1 15rem}
.baraja .nota{margin:.35rem 0 0;font-size:.82rem;color:var(--tenue)}
/* vocabulario: el dibujo del sustantivo, ENCIMA de la palabra. Pequeño a
   propósito —la palabra manda y el dibujo acompaña— y legible a 56 px porque
   el estilo es plano y de contorno grueso; una foto a ese tamaño no se vería.
   Crece al pasar por encima en escritorio, que sale gratis y no estorba.

   En bloque y no en línea: a 420 px la columna española mide unos 110, así que
   con el dibujo al lado le quedaban 50 a la palabra y «el marido» se partía
   por la mitad. Encima, la palabra se lleva la columna entera. Se vio en una
   captura del móvil, no razonándolo. */
.dibujo{display:block;width:56px;height:56px;border-radius:8px;
  margin:0 0 .3rem;background:var(--tarjeta);transition:transform .12s}
@media(hover:hover){.dibujo:hover{transform:scale(2.2);position:relative;z-index:5}}
/* La clave: el enlace donde se acaban los ejercicios y la caja plegada al
   final. El enlace se ve como un paso más y no como un botón: lo que manda en
   la lección es hacer el ejercicio, no mirar la respuesta. */
.a-la-clave{margin:1.2rem 0 0;font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.92rem}
.a-la-clave a{text-decoration:none;border-bottom:1px solid var(--linea);padding-bottom:1px}
.a-la-clave a:hover{border-color:var(--acento)}
#clave-boton{margin:2rem 0 .5rem}
#clave{border-top:1px solid var(--linea);padding-top:.2rem}
/* audio: un ▶ al lado de cada frase española que esté locutada */
.suena{background:none;border:0;padding:0 .35rem 0 0;margin:0;cursor:pointer;color:var(--celeste);
  font:inherit;font-size:.82em;line-height:1;vertical-align:baseline;opacity:.65;transition:opacity .12s}
.suena:hover,.suena:focus-visible{opacity:1}
.suena[aria-pressed="true"]{opacity:1;color:var(--acento)}
@media(hover:none){.suena{opacity:.9}}

/* Test de nivel */
.test-caja{background:var(--tarjeta);border:1px solid var(--linea);border-radius:12px;
  padding:1.2rem 1.3rem;margin:1.4rem 0;font-family:Onest,ui-sans-serif,system-ui,sans-serif}
.test-cuenta{font-size:.78rem;color:var(--tenue);letter-spacing:.04em;margin-bottom:.5rem}
.test-pregunta{font-size:1.08rem;font-weight:600;color:var(--tinta);margin:0 0 1rem;line-height:1.45}
.test-ops{display:flex;flex-direction:column;gap:.5rem}
.test-ops button{text-align:start;font:inherit;font-size:.98rem;color:var(--tinta);
  background:var(--papel);border:1.5px solid var(--linea);border-radius:9px;
  padding:.6rem .8rem;cursor:pointer;transition:border-color .12s,background .12s}
.test-ops button:hover{border-color:var(--acento)}
.test-ops button[disabled]{cursor:default;opacity:.75}
.test-ops button.bien{border-color:#1d7a4f;opacity:1;font-weight:600}
.test-ops button.mal{border-color:var(--acento);opacity:1}
.test-seg{float:inline-end;font-variant-numeric:tabular-nums;color:var(--tenue);font-weight:600}
.test-reloj{height:3px;border-radius:999px;background:var(--linea);overflow:hidden;margin:0 0 .9rem}
.test-reloj i{display:block;height:100%;background:var(--acento);opacity:.55}
.test-tarde{display:block;color:var(--acento);font-weight:600;font-size:.84rem}
.test-barra{height:4px;border-radius:999px;background:var(--linea);overflow:hidden;margin-top:1rem}
.test-barra i{display:block;height:100%;background:var(--acento);transition:width .2s}
.test-fallo{border-inline-start:3px solid var(--acento);padding:.1rem 0 .1rem .8rem;margin:.7rem 0}
.test-fallo b{display:block;color:var(--tinta);font-size:.94rem}
.test-fallo span{font-size:.88rem;color:var(--tenue)}

/* El mapa de unidades: 24 tarjetas en vez de 365 filas.
   El indice crudo medía 21.482 px de alto, o sea 24 pantallas de scroll, y
   nadie navega eso. Las tarjetas dan una vista de todo el ano en una o dos. */
.mapa{display:grid;gap:.85rem;margin:1.4rem 0 2.2rem;
  grid-template-columns:repeat(auto-fill,minmax(13rem,1fr));
  /* Se sale de la columna de prosa, como la cabecera y por lo mismo: un mapa
     no se lee renglon a renglon. Encerrado en los 44rem del texto solo caben
     dos columnas y el mapa medía 1.806 px, que es tan ilegible como la lista
     que viene a sustituir. Centrado sobre la ventana y no sobre el padre, que
     asi no hace falta saber cuanto mide el padre. */
  width:min(60rem,calc(100vw - 2.5rem));position:relative;left:50%;translate:-50%}
/* Columna y no bloque: la rejilla estira las tarjetas de una fila a la misma
   altura, pero el pie quedaba pegado al texto, asi que las barras de dos
   tarjetas vecinas salian a distinta altura segun si el titulo ocupaba una
   linea o dos. Con margin-top:auto en el pie, todas se alinean abajo. */
.u-tarjeta{display:flex;flex-direction:column;text-decoration:none;color:inherit;background:var(--tarjeta);
  border:1px solid var(--linea);border-radius:12px;padding:.85rem .95rem;
  font-family:Onest,ui-sans-serif,system-ui,sans-serif;transition:border-color .12s,transform .12s}
.u-tarjeta:hover{border-color:var(--acento);transform:translateY(-2px)}
.u-tarjeta .alto{display:flex;align-items:baseline;gap:.5rem;margin-bottom:.3rem}
.u-tarjeta .num{font-size:1.45rem;font-weight:700;color:var(--acento);
  font-feature-settings:"tnum";line-height:1}
/* `align-self` porque la fila alinea por la línea base y una imagen no tiene:
   sin esto el dibujo cuelga del número. Mismo tratamiento que `.dibujo` de
   las tablas de vocabulario —fondo de ficha y esquina redonda— para que las
   dos formas de enseñar un dibujo se parezcan. */
.u-tarjeta .u-dibujo{width:40px;height:40px;border-radius:8px;align-self:center;
  background:var(--tarjeta);transition:transform .14s}
/* El dibujo crece al pasar por encima, como ya hace el de las tablas de
   vocabulario. Solo donde hay raton de verdad: en una pantalla tactil
   `:hover` se queda pegado despues de tocar. */
@media(hover:hover){.u-tarjeta:hover .u-dibujo{transform:scale(1.45)}}
/* Las tarjetas aparecen subiendo al llegar a ellas.
   `.anima` lo pone el GUION y no el servidor, y esa es la linea que no se
   puede cruzar: si el navegador no trae IntersectionObserver —o el sistema
   pide menos movimiento— la clase no se anade y las tarjetas nacen visibles.
   Al reves, un `opacity:0` servido en el HTML deja la pagina en blanco para
   quien no tenga JavaScript, que es justo lo que este sitio no hace. */
.mapa.anima .u-tarjeta{opacity:0;translate:0 12px;
  transition:opacity .4s ease,translate .4s ease,border-color .12s,transform .12s}
.mapa.anima .u-tarjeta.dentro{opacity:1;translate:0 0}
@media(prefers-reduced-motion:reduce){
  .mapa.anima .u-tarjeta{opacity:1;translate:0 0;transition:none}
  .u-tarjeta:hover .u-dibujo{transform:none}}
.u-tarjeta .nivel{margin-inline-start:auto;font-size:.68rem;font-weight:700;letter-spacing:.06em;
  color:var(--celeste);border:1px solid var(--celeste);border-radius:999px;padding:.05rem .4rem}
.u-tarjeta .tit{font-weight:600;font-size:.94rem;color:var(--tinta);line-height:1.3;
  display:block;margin-bottom:.4rem}
.u-tarjeta .serie{font-size:.78rem;color:var(--tenue);font-style:italic;
  display:block;margin-bottom:.5rem}
.u-tarjeta .pie{display:flex;align-items:center;gap:.5rem;font-size:.74rem;color:var(--tenue);
  margin-top:auto;padding-top:.15rem}
.u-tarjeta .mini{flex:1;height:4px;border-radius:999px;background:var(--linea);overflow:hidden}
.u-tarjeta .mini i{display:block;height:100%;background:var(--acento);border-radius:999px}
.u-tarjeta.vacia{opacity:.62}
.u-tarjeta.vacia:hover{border-color:var(--linea);transform:none}

/* progreso del lector */
/* El [hidden] del navegador pierde contra .boton{display:inline-block}, así que
   «continuar» se vería como un botón naranja vacío en la primera visita. */
[hidden]{display:none!important}
.boton.marcar{margin:1.6rem 0 0}
.boton.destacado{box-shadow:0 0 0 3px var(--acento-suave)}
ul.dias li.hecha .num::after{content:"✓";color:var(--acento);font-weight:700;margin-inline-start:.25rem}
ul.dias li.hecha a{color:var(--tenue)}
#mio{margin-top:.9rem;padding-top:.9rem;border-top:1px dashed var(--linea)}
/* El margen negativo era de la PORTADA, donde `.puerta` va pegada a los dos
   botones del héroe y hacía falta recogerla. En `kurs.html` va detrás del
   botón de restaurar el progreso, y ahí lo que hacía era METERSE ENCIMA: el
   enlace y la frase se tocaban. Lo vio el profesor en una captura. Ahora el
   recorte vive donde se escribió, colgado del hermano anterior. */
.puerta{font-size:.9rem;color:var(--tenue);margin:1.2rem 0 0}
.botones+.puerta{margin-top:-.6rem}
.puerta a{color:var(--acento);font-weight:600}
.progreso-nota{font-size:.84rem;color:var(--tenue);font-family:Onest,ui-sans-serif,system-ui,sans-serif;margin-top:.5rem}
#borrar-progreso{background:none;border:0;padding:0;color:var(--tenue);text-decoration:underline;
  cursor:pointer;font:inherit;font-size:.84rem}
@media(min-width:40rem){
  header.sitio nav.paginas{order:0;flex:0 1 auto;margin-inline-start:auto}
  /* En escritorio el titulo NO crece: con flex:1 1 auto se comia el hueco que
     la nav reclama con su margen automatico. */
  header.sitio .marca{flex:0 1 auto}
  /* Y la barra usa mas ancho que el texto. Una columna de lectura tiene que
     ser estrecha; una barra de navegacion no. Metida en los mismos 704 px, el
     titulo + los tres enlaces + los tres idiomas + la luna sumaban 708 y el
     boton del tema caia a una segunda fila con 700 px de pantalla libres al
     lado. Se vio midiendo los hijos, no mirando: fallaba por cuatro pixeles. */
  header.sitio .envoltorio{max-width:60rem}
}

main{padding-bottom:3.5rem}

/* ---- tipografía ---- */
h1{font-size:clamp(1.65rem,5.2vw,2.3rem);line-height:1.15;letter-spacing:-.022em;margin:1.6rem 0 .25rem;font-weight:650}
h1 .segunda{display:block;color:var(--acento);font-weight:400}
h2{font-size:clamp(1.08rem,3.2vw,1.22rem);margin:2.6rem 0 .7rem;padding-top:.9rem;
  border-top:1px solid var(--linea);font-weight:650;letter-spacing:-.012em}
h3{font-size:1rem;margin:1.6rem 0 .45rem;font-weight:650}
h1,h2,h3{font-family:Onest,ui-sans-serif,system-ui,-apple-system,sans-serif}
p{margin:.75rem 0}
a{color:var(--acento);text-underline-offset:2px}
strong{font-weight:650}

/* ---- portada ---- */
.heroe{padding:2rem 0 .5rem}
.heroe .lema{font-size:clamp(1.02rem,3.4vw,1.2rem);color:var(--tenue);margin:.5rem 0 1.1rem;font-style:italic}

/* El arte del heroe: seis de los dibujos del curso, ARRIBA DEL TODO.
   El profesor dijo que la pagina no es agradable a simple vista, y medida la
   primera pantalla del movil tenia cinco lineas de letra sobre crema y ni una
   imagen: los doce dibujos —lo unico que este sitio tiene y nadie mas, y que
   ya esta pagado— empezaban DEBAJO del pliegue, bajo un <h2>. O sea que el
   mejor activo de la pagina era invisible justo en el segundo en que el
   visitante decide si se queda.
   En el movil la tira va ANTES del titulo (order:-1): ves comida, un perro y
   una guitarra antes de leer una palabra. En escritorio se pone al lado, para
   no empujar los botones fuera de la vista.
   No son los mismos bytes dos veces: el navegador ya tiene el fichero en
   cache cuando llega a la vitrina de abajo, que es la que ensena la palabra.
   Y es DECORACION: aria-hidden, alt vacio y sin enlace. Lo que se puede
   pulsar y oir es la vitrina; esto solo mira. */
.heroe{display:flex;flex-direction:column}
.heroe-arte{order:-1;display:flex;gap:.5rem;margin:0 0 1.3rem;justify-content:center}
.heroe-arte img{flex:1 1 0;min-width:0;max-width:72px;height:auto;aspect-ratio:1;
  border-radius:10px;background:var(--tarjeta);border:1px solid var(--linea);
  box-shadow:var(--sombra)}
/* En escritorio la tira es LA MISMA: una fila encima del titulo, solo que con
   los dibujos un poco mayores. La primera version la metia en una segunda
   columna del heroe, y alli los seis caian en una rejilla de 2x3 de 88px: ni
   fila ni columna, descolgada del titulo, con un hueco muerto encima y con el
   recuadro de cada ficha bien visible a ese tamano. El profesor lo dijo mirando
   las dos pantallas —«en el movil salen imagenes y en la web no sale igual»— y
   tenia razon: eran dos disenos distintos para la misma portada.

   Se vio comparando las dos capturas, no razonandolo. */
@media(min-width:46rem){
  .heroe-arte{gap:.75rem;margin-bottom:1.8rem}
  .heroe-arte img{max-width:96px}
}
.botones{display:flex;flex-wrap:wrap;gap:.65rem;margin:1.4rem 0}
.boton{display:inline-block;background:var(--acento);color:#fff;padding:.7rem 1.35rem;border-radius:8px;
  text-decoration:none;font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.97rem;font-weight:550;
  box-shadow:var(--sombra);transition:transform .12s ease}
.boton:hover{transform:translateY(-1px)}
.boton.secundario{background:transparent;color:var(--acento);border:1.5px solid var(--acento);box-shadow:none}

/* La vitrina de la portada: doce palabras con su dibujo. La rejilla es de 3,
   4 o 6 columnas según el ancho, y por eso son doce: en los tres casos quedan
   filas enteras. El dibujo manda aquí —al revés que en la tabla de la
   lección— porque lo que hace es enseñar de qué va el curso de un vistazo. */
.muestra{margin:2.2rem 0}
.muestra h2{margin-bottom:.3rem}
.muestra>p{margin:0 0 1rem;color:var(--tenue);font-size:.92rem}
.vitrina{list-style:none;padding:0;margin:0;display:grid;gap:.6rem;
  grid-template-columns:repeat(3,1fr)}
@media(min-width:30rem){.vitrina{grid-template-columns:repeat(4,1fr)}}
@media(min-width:52rem){.vitrina{grid-template-columns:repeat(6,1fr)}}
.vitrina li{background:var(--tarjeta);border:1px solid var(--linea);border-radius:11px;
  padding:.6rem .3rem .55rem;text-align:center;box-shadow:var(--sombra);
  font-family:Onest,ui-sans-serif,system-ui,sans-serif;transition:transform .12s ease}
@media(hover:hover){.vitrina li:hover{transform:translateY(-2px)}}
/* La ficha ENTERA es el boton que suena, asi que hay que quitarle el cromo
   del navegador: sin esto sale un boton gris con su borde dentro de la
   tarjeta. El <span> es la misma ficha cuando esa palabra no esta locutada. */
.vitrina .ficha{display:block;width:100%;background:none;border:0;padding:0;
  margin:0;color:inherit;font:inherit;text-align:center}
.vitrina button.ficha{cursor:pointer}
.vitrina button.ficha[aria-pressed="true"] b{color:var(--acento)}
.vitrina img{display:block;width:72px;height:72px;margin:0 auto .4rem;border-radius:8px}
.vitrina b{display:block;font-size:.84rem;font-weight:600}
.vitrina .ru{display:block;font-size:.78rem;color:var(--tenue);margin-top:.1rem}

.progreso{margin:1.5rem 0;font-family:Onest,ui-sans-serif,system-ui,sans-serif}
.progreso .cifras{display:flex;align-items:baseline;gap:.45rem;font-size:.88rem;color:var(--tenue)}
.progreso .n{font-size:1.5rem;font-weight:700;color:var(--tinta);font-feature-settings:"tnum"}
.barra{height:7px;border-radius:999px;background:var(--linea);overflow:hidden;margin-top:.45rem}
.barra i{display:block;height:100%;background:linear-gradient(90deg,var(--acento),var(--celeste));border-radius:999px}

/* ---- bloque de contraste: la firma del curso ---- */
.contraste{background:var(--acento-suave);border:1px solid color-mix(in srgb,var(--acento) 22%,transparent);
  border-radius:10px;padding:1rem 1.1rem;margin:1.3rem 0}
.contraste>h3:first-child{margin-top:0;color:var(--acento)}
.contraste p:last-child{margin-bottom:0}
del{text-decoration-line:line-through;text-decoration-color:var(--acento);
  text-decoration-thickness:2px;opacity:.75}
.mal{color:var(--acento)}
.bien{color:#1d7a4f}
@media(prefers-color-scheme:dark){:root:not([data-tema="light"]) .bien{color:#5fc48f}}
/* Los 300 dibujos llevan el fondo DENTRO del archivo —`igualar_dibujos.py`
   los iguala a `--tarjeta`— así que en la noche son cuadrados casi blancos
   sobre tarjetas oscuras, y con la paleta del 2026-10-29 eso empeoró: el
   crema (#f7f2e6) pasó a un gris casi blanco (#f4f4f5).

   Atenuarlos es la única salida barata: el fondo transparente lo descartó la
   nota del 2026-10-28 —en estos dibujos el color es la mitad de lo que
   enseñan, así que no pueden ser siluetas— y recortar el fondo de 300 webp
   con el objeto dentro es arriesgar 300 activos por un cuadrito.

   0,80 está medido sobre las tarjetas, comparado con 1,0 y con una versión
   con aro: por encima deslumbra y por debajo el dibujo deja de leerse. El
   aro no aportaba nada a 40 px. Solo de noche: de día el fondo del dibujo y
   el de su ficha son el MISMO color y no hay nada que atenuar. */
@media(prefers-color-scheme:dark){:root:not([data-tema="light"]) .dibujo,
  :root:not([data-tema="light"]) .u-dibujo,
  :root:not([data-tema="light"]) .heroe-arte img,
  :root:not([data-tema="light"]) .vitrina img{filter:brightness(.8) saturate(.95)}}
:root[data-tema="dark"] .dibujo,:root[data-tema="dark"] .u-dibujo,
:root[data-tema="dark"] .heroe-arte img,
:root[data-tema="dark"] .vitrina img{filter:brightness(.8) saturate(.95)}
:root[data-tema="dark"] .bien{color:#5fc48f}

blockquote{margin:1.2rem 0;padding:.85rem 1.1rem;background:var(--tarjeta);
  border-inline-start:3px solid var(--celeste);border-radius:0 8px 8px 0}
blockquote p:first-child{margin-top:0}blockquote p:last-child{margin-bottom:0}

/* ---- tablas ---- */
.tabla-env{overflow-x:auto;margin:.9rem 0;border:1px solid var(--linea);border-radius:9px;background:var(--papel)}
table{border-collapse:collapse;width:100%;font-size:.92rem;font-family:Onest,ui-sans-serif,system-ui,sans-serif}
th,td{padding:.45rem .65rem;text-align:start;vertical-align:top;border-bottom:1px solid var(--linea)}
tr:last-child td{border-bottom:none}
th{background:var(--tarjeta);font-weight:600;position:sticky;top:0}
code{font-size:.88em;background:var(--tarjeta);padding:.1em .32em;border-radius:4px;
  font-family:ui-monospace,"SF Mono",Menlo,monospace}

/* ---- tarjetas y listas ---- */
.rejilla{display:grid;gap:.85rem;grid-template-columns:1fr;margin:1rem 0}
@media(min-width:36rem){.rejilla{grid-template-columns:1fr 1fr}}
.tarjeta{border:1px solid var(--linea);border-radius:10px;padding:.95rem 1.1rem;background:var(--tarjeta);box-shadow:var(--sombra)}
.tarjeta h3{margin:0 0 .3rem;font-size:.88rem;text-transform:uppercase;letter-spacing:.05em;color:var(--acento)}
.tarjeta p{margin:0;font-size:.95rem}

ul.dias{list-style:none;padding:0;margin:.5rem 0}
ul.dias li{display:flex;gap:.6rem;align-items:baseline;padding:.4rem .2rem;border-bottom:1px solid var(--linea)}
ul.dias li:last-child{border-bottom:none}
ul.dias .num{font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.78rem;color:var(--tenue);
  min-width:2.6rem;font-feature-settings:"tnum"}
ul.dias a{text-decoration:none}ul.dias a:hover{text-decoration:underline}
ul.dias .falta{color:var(--tenue)}
.tipo{font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.67rem;color:var(--celeste);
  text-transform:uppercase;letter-spacing:.07em;border:1px solid var(--linea);border-radius:999px;
  padding:.05rem .4rem;white-space:nowrap}
.unidad-cab{display:flex;flex-wrap:wrap;gap:.5rem;align-items:baseline;margin-top:2.4rem}
details{margin:.5rem 0;font-size:.93rem}
summary{cursor:pointer;font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.86rem;color:var(--tenue)}
details ul{margin:.5rem 0}

/* ---- lección ---- */
.leccion-cab{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center;margin:1.3rem 0 .2rem;
  font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.78rem;color:var(--tenue)}
.leccion-cab .n{background:var(--acento);color:#fff;border-radius:999px;padding:.12rem .6rem;font-weight:600}
/* ---- la guia de los seis pasos ----
   Pegada bajo la cabecera, que es pegajosa a partir de 40rem: el tope lo mide
   el guion y lo deja en --alto-cabecera, porque escrito a mano se quedaria
   viejo el dia que cambie el menu y la guia saldria tapada. z-index por debajo
   de la cabecera (20) a proposito. */
.guia{position:sticky;top:var(--alto-cabecera,0px);z-index:15;display:flex;align-items:center;
  gap:.6rem;flex-wrap:wrap;margin:.6rem 0 1.2rem;padding:.5rem .7rem;background:var(--tarjeta);
  border:1px solid var(--linea);border-radius:10px;box-shadow:var(--sombra);
  font-family:Onest,ui-sans-serif,system-ui,sans-serif}
.guia-barra{display:flex;gap:.3rem}
.guia-punto{width:1.6rem;height:1.6rem;border-radius:50%;border:1px solid var(--linea);
  background:var(--papel);color:var(--tenue);font:inherit;font-size:.74rem;line-height:1;
  cursor:pointer;padding:0}
.guia-punto:hover{border-color:var(--acento)}
.guia-punto.hecho{background:var(--linea);color:var(--tinta)}
.guia-punto.aqui{background:var(--acento);border-color:var(--acento);color:#fff;font-weight:600}
.guia-ahora{flex:1 1 7rem;min-width:0;display:flex;flex-direction:column;line-height:1.25}
.guia-ahora b{font-size:.86rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.guia-ahora span{font-size:.72rem;color:var(--tenue)}
.guia-ir{border:1px solid var(--acento);background:transparent;color:var(--acento);
  border-radius:7px;padding:.33rem .7rem;font:inherit;font-size:.8rem;cursor:pointer;white-space:nowrap}
.guia-ir:hover{background:var(--acento);color:#fff}
/* En el movil los seis numeros no caben en la misma fila que el nombre del
   paso y el boton, y la barra se partia en dos: noventa pixeles pegados arriba
   en una pantalla de 844. Puntos sin numero: cual es se lee en el nombre, que
   esta al lado y dice mas. Medido en el navegador a 390 px. */
@media(max-width:28rem){
  .guia{gap:.45rem;padding:.45rem .55rem}
  .guia-punto{width:.62rem;height:.62rem;font-size:0;border-width:1px}
  .guia-ir{padding:.33rem .55rem}
}
@media print{.guia{display:none}}
.aviso{background:var(--realce);border:1px solid var(--linea);border-radius:8px;padding:.6rem .85rem;
  font-size:.88rem;font-family:Onest,ui-sans-serif,system-ui,sans-serif;margin:1rem 0}
nav.pasos{display:flex;justify-content:space-between;gap:.8rem;margin:2.5rem 0 0;padding-top:1rem;
  border-top:1px solid var(--linea);font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.86rem}
nav.pasos a{text-decoration:none;padding:.4rem .7rem;border:1px solid var(--linea);border-radius:7px}
nav.pasos a:hover{border-color:var(--acento)}
input[type=checkbox]{margin-inline-end:.45rem}

/* ---- anuncios, pie, cookies ---- */
.anuncio{margin:2rem 0;text-align:center;min-height:1px}
.anuncio::before{content:attr(data-etiqueta);display:block;font-family:Onest,ui-sans-serif,system-ui,sans-serif;
  font-size:.64rem;color:var(--tenue);text-transform:uppercase;letter-spacing:.09em;margin-bottom:.3rem}
footer.sitio{border-top:1px solid var(--linea);padding:1.6rem 0 3rem;
  font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.83rem;color:var(--tenue)}
footer.sitio a{color:var(--tenue)}
footer.sitio p{margin:.35rem 0}
#cookies{position:fixed;inset-inline:0;bottom:0;background:var(--tarjeta);border-top:1px solid var(--linea);
  padding:.85rem 20px;font-family:Onest,ui-sans-serif,system-ui,sans-serif;font-size:.85rem;display:flex;
  flex-wrap:wrap;gap:.75rem;align-items:center;justify-content:center;z-index:30}
"""


# El tema se aplica ANTES de pintar: si esto fuera al final de la página, el
# lector que eligió noche vería un fogonazo blanco en cada carga.
TEMA_CABEZA = (
    "<script>try{var t=localStorage.getItem('tema');"
    "if(t)document.documentElement.dataset.tema=t}catch(e){}</script>"
)

LUNA = ('<svg class="luna" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')
SOL = ('<svg class="sol" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" '
       'stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/>'
       '<path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.5 1.5M17.9 17.9l1.5 1.5M2.5 12h2M19.5 12h2'
       'M4.6 19.4l1.5-1.5M17.9 6.1l1.5-1.5"/></svg>')

# Sin data-tema manda el sistema, así que el estado real se consulta con
# matchMedia y no se supone.
TEMA_SCRIPT = (
    "<script>(function(){var b=document.getElementById('tema');if(!b)return;"
    "function actual(){var r=document.documentElement;return r.dataset.tema||"
    "(window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');}"
    "b.addEventListener('click',function(){var n=actual()==='dark'?'light':'dark';"
    "document.documentElement.dataset.tema=n;try{localStorage.setItem('tema',n)}catch(e){}});})();</script>"
)


# El progreso del lector. Vive en SU navegador y en ninguna otra parte: sin
# registro, sin servidor, sin datos personales. Un sitio estático no puede
# guardar nada en un servidor, pero resulta que para «cerré la página, ¿dónde
# iba?» tampoco hace falta.
PROGRESO_JS = r"""(function(){
  var CLAVE_HECHAS='curso.hechas', CLAVE_ULTIMA='curso.ultima';
  var CLAVE_FECHAS='curso.fechas', CLAVE_NOMBRE='curso.nombre';
  var T=window.CURSO_TEXTOS||{}, RAIZ=window.CURSO_RAIZ||'.';

  function leer(clave,porDefecto){
    try{var v=localStorage.getItem(clave);return v?JSON.parse(v):porDefecto}catch(e){return porDefecto}
  }
  function guardar(clave,valor){
    try{localStorage.setItem(clave,JSON.stringify(valor))}catch(e){}
  }
  function hechas(){var v=leer(CLAVE_HECHAS,[]);return Array.isArray(v)?v:[]}
  function url(n){
    var d=window.CURSO_DIAS&&window.CURSO_DIAS[n];
    return d?RAIZ+'/'+d:null;
  }

  function hoy(){
    // La fecha LOCAL y no toISOString(), que da UTC: quien estudia a las
    // once de la noche en Moscú vería la racha contada como del día
    // siguiente, y quien estudia de madrugada en México la perdería.
    var f=new Date(), m=f.getMonth()+1, d=f.getDate();
    return f.getFullYear()+'-'+(m<10?'0':'')+m+'-'+(d<10?'0':'')+d;
  }
  function fechas(){var v=leer(CLAVE_FECHAS,[]);return Array.isArray(v)?v:[]}
  function anotarHoy(){
    var f=fechas(), h=hoy();
    if(f.indexOf(h)<0){f.push(h);guardar(CLAVE_FECHAS,f)}
  }
  function dia(cadena){var p=String(cadena).split('-');return Date.UTC(+p[0],+p[1]-1,+p[2])}
  function rachas(){
    // Devuelve {actual, mejor}. La actual cuenta hacia atrás desde HOY, y si
    // hoy todavía no hay nada, desde ayer: una racha no se rompe por que
    // sean las diez de la mañana y aún no hayas estudiado.
    var f=fechas().slice().sort(), DIA=86400000;
    if(!f.length)return {actual:0,mejor:0,hoy:false};
    var h=dia(hoy()), ultima=dia(f[f.length-1]);
    var actual=0, mejor=0, seguidas=0, previa=null;
    for(var i=0;i<f.length;i++){
      var d=dia(f[i]);
      seguidas = (previa!==null && d-previa===DIA) ? seguidas+1 : 1;
      if(seguidas>mejor)mejor=seguidas;
      previa=d;
    }
    if(ultima===h||ultima===h-DIA){
      actual=1;
      for(var j=f.length-2;j>=0;j--){
        if(dia(f[j+1])-dia(f[j])===DIA)actual++;else break;
      }
    }
    return {actual:actual,mejor:mejor,hoy:ultima===h};
  }
  function plural(n,formas){
    // Tres formas porque el ruso las pide (1 день, 2-4 дня, 5+ дней). En
    // español y en inglés las dos últimas son la misma y no estorba.
    if(!formas||!formas.length)return '';
    var d=n%10, c=n%100;
    if(d===1&&c!==11)return formas[0];
    if(d>=2&&d<=4&&!(c>=12&&c<=14))return formas[1]||formas[0];
    return formas[2]||formas[1]||formas[0];
  }
  function permutacion(bloque,largo){
    // Fisher-Yates con una semilla que sale del BLOQUE, así que da lo mismo
    // en cada visita: el mensaje de una lección no cambia al recargarla.
    // El multiplicador es el de MINSTD y no el del LCG de libro: con éste
    // todos los productos se quedan por debajo de 2^53, que es hasta donde
    // JavaScript cuenta exacto. Con 1103515245 el producto se sale y la
    // mezcla deja de ser la que se midió.
    var s=((bloque+1)*48271)%2147483647, p=[];
    for(var i=0;i<largo;i++)p.push(i);
    for(var k=largo-1;k>0;k--){
      s=(s*48271)%2147483647;
      var j=(s>>8)%(k+1), t=p[k];p[k]=p[j];p[j]=t;
    }
    return p;
  }
  function variante(n,lista){
    // Dentro de cada bloque de `largo` lecciones salen todas las frases una
    // vez, en un orden que depende del bloque. Hace dos cosas a la vez que
    // ninguna solución simple hace: no repite nunca la frase de la lección
    // anterior Y no deja un ciclo visible —con n%largo la frase de hoy es la
    // de hace nueve lecciones, y en una racha de dos semanas eso se nota, que
    // es justo de lo que el profesor se quejó—. Es el mismo reparto por
    // bloques que la letra correcta de los tests, y por el mismo motivo.
    if(!lista)return '';
    if(!lista.length||typeof lista==='string')return String(lista);
    var largo=lista.length, bloque=Math.floor((n-1)/largo), p=permutacion(bloque,largo);
    if(bloque>0&&p[0]===permutacion(bloque-1,largo)[largo-1]){var t=p[0];p[0]=p[1];p[1]=t}
    return lista[p[(n-1)%largo]];
  }
  function conPlantilla(txt,datos){
    return String(txt||'').replace(/\{(\w+)\}/g,function(_,k){
      return datos[k]!==undefined?datos[k]:'';
    });
  }
  function nombre(){try{return localStorage.getItem(CLAVE_NOMBRE)||''}catch(e){return ''}}


  // --- el certificado, dibujado en el navegador ---
  function partirTexto(g,texto,ancho){
    var palabras=String(texto||'').split(/\s+/), lineas=[], linea='';
    for(var i=0;i<palabras.length;i++){
      var prueba=linea?linea+' '+palabras[i]:palabras[i];
      if(g.measureText(prueba).width>ancho&&linea){lineas.push(linea);linea=palabras[i]}
      else{linea=prueba}
    }
    if(linea)lineas.push(linea);
    return lineas;
  }
  function descargarDiploma(nv,quien){
    var A=1200, B=850, lienzo=document.createElement('canvas');
    lienzo.width=A;lienzo.height=B;
    var g=lienzo.getContext('2d');
    if(!g)return;
    // La paleta va escrita aquí y NO leída de las variables del CSS, a
    // propósito: un certificado se imprime, así que es siempre la versión
    // clara. Leyéndola, quien tenga puesto el tema oscuro se descargaría un
    // papel negro. Es el mismo precio que ya paga `tarjeta_social.py`.
    var PAPEL='#ffffff', TINTA='#101113', ACENTO='#b03f26', TENUE='#6b7076';
    var SANS='Onest,ui-sans-serif,system-ui,sans-serif';
    var SERIF='Literata,ui-serif,Georgia,serif';
    g.fillStyle=PAPEL;g.fillRect(0,0,A,B);
    g.strokeStyle=ACENTO;g.lineWidth=6;g.strokeRect(26,26,A-52,B-52);
    g.strokeStyle='#dcdde0';g.lineWidth=1;g.strokeRect(44,44,A-88,B-88);
    // La marca del sitio: la misma eñe del icono, para que el papel y la
    // pestaña hablen el mismo idioma.
    g.fillStyle=ACENTO;
    var lado=84, mx=(A-lado)/2;
    if(g.roundRect){g.beginPath();g.roundRect(mx,88,lado,lado,20);g.fill()}
    else{g.fillRect(mx,88,lado,lado)}
    g.fillStyle=PAPEL;g.textAlign='center';g.textBaseline='alphabetic';
    g.font='700 56px '+SANS;g.fillText('ñ',A/2,88+lado-20);
    g.fillStyle=TINTA;
    g.font='700 46px '+SANS;g.fillText(T.diploma_titulo||'',A/2,250);
    g.fillStyle=TENUE;
    g.font='400 22px '+SANS;g.fillText(T.diploma_sub||'',A/2,288);
    g.strokeStyle='#dcdde0';g.lineWidth=1;
    g.beginPath();g.moveTo(A/2-180,318);g.lineTo(A/2+180,318);g.stroke();
    g.fillStyle=TENUE;
    g.font='400 20px '+SANS;g.fillText(T.diploma_quien||'',A/2,368);
    g.fillStyle=ACENTO;
    g.font='400 56px '+SERIF;g.fillText(quien,A/2,432);
    g.fillStyle=TINTA;
    g.font='400 26px '+SANS;
    g.fillText(conPlantilla(T.diploma_que,{nivel:nv.nivel,n:nv.hasta}),A/2,492);
    g.fillStyle=TENUE;
    g.font='400 22px '+SANS;
    g.fillText(window.CURSO_SITIO||'',A/2,548);
    g.font='400 19px '+SANS;
    g.fillText((T.diploma_fecha||'')+': '+hoy(),A/2,592);
    // El aviso es la línea que hace honrado el papel, así que va en el
    // certificado y no solo en la página.
    g.fillStyle=TENUE;g.font='400 16px '+SANS;
    var lineas=partirTexto(g,T.diploma_aviso,A-280), y=B-150;
    for(var i=0;i<lineas.length;i++){g.fillText(lineas[i],A/2,y+i*23)}
    var dominio=window.CURSO_DOMINIO||'';
    if(dominio){g.fillStyle=TINTA;g.font='700 18px '+SANS;g.fillText(dominio,A/2,B-78)}
    var archivo='certificado-'+String(nv.nivel).replace(/[^A-Za-z0-9]/g,'')+'.png';
    function bajar(url){
      var a=document.createElement('a');
      a.href=url;a.download=archivo;
      document.body.appendChild(a);a.click();document.body.removeChild(a);
    }
    if(lienzo.toBlob){
      lienzo.toBlob(function(b){
        if(!b){bajar(lienzo.toDataURL('image/png'));return}
        var url=URL.createObjectURL(b);bajar(url);
        setTimeout(function(){URL.revokeObjectURL(url)},10000);
      },'image/png');
    }else{bajar(lienzo.toDataURL('image/png'))}
  }

  // --- en una lección: recordar que se pasó por aquí y poder marcarla ---
  // article[data-leccion] y no [data-leccion] a secas: en el índice el primero
  // que aparece es un <li data-leccion>, así que abrir el índice movía «la
  // última leída» a la lección 1 y «continuar» mandaba al principio.
  var cuerpoLeccion=document.querySelector('article[data-leccion]');
  if(cuerpoLeccion){
    var n=parseInt(cuerpoLeccion.getAttribute('data-leccion'),10);
    if(n){guardar(CLAVE_ULTIMA,n);}
    var caja=document.getElementById('marcar-caja');
    if(caja&&n){
      var boton=document.createElement('button');
      boton.type='button';boton.className='boton marcar';
      var siguiente=document.getElementById('enlace-siguiente');
      function pintar(){
        var yaEsta=hechas().indexOf(n)>=0;
        boton.textContent=(yaEsta?'✓ ':'')+(yaEsta?T.hecho:T.marcar);
        boton.classList.toggle('secundario',yaEsta);
      }
      // El saludo al terminar: por su nombre, cuánto lleva y cuántos días
      // seguidos. Lo pidió el profesor —«que la página le envíe un mensaje
      // con su nombre»— y esto es lo que un sitio estático puede hacer de
      // verdad: saludar aquí. Mandar un correo o una notificación necesita
      // servidor y una dirección, que es lo que se decidió no tener.
      var saludo=document.createElement('p');
      saludo.className='saludo';saludo.hidden=true;
      var pedirNombre=document.createElement('p');
      pedirNombre.className='pide-nombre';pedirNombre.hidden=true;
      function felicitar(){
        var r=rachas(), total=window.CURSO_PUBLICADAS||0, hechasAhora=hechas().length;
        var quien=nombre();
        // La PRIMERA lección lleva su propio mensaje: es donde más gente se
        // va, y una frase de rotación no dice nada de lo que acaba de pasar.
        // De ahí en adelante, una de las nueve, elegida por el NÚMERO DE
        // LECCIÓN y no al azar: al azar, marcar y desmarcar la misma lección
        // daría tres frases distintas para el mismo acto, y eso se lee como
        // que el sitio está probando textos en vez de hablarte.
        var trozos=[hechasAhora===1
          ? conPlantilla(quien?T.primera_con:T.primera,{nombre:quien})
          : conPlantilla(variante(n,quien?T.bravo_con:T.bravo),{nombre:quien})];
        if(total)trozos.push(conPlantilla(T.cuantas,{n:hechasAhora,total:total}));
        if(r.actual>1)trozos.push(conPlantilla(T.racha,
          {n:r.actual,dias:plural(r.actual,T.racha_dias)}));
        if(total&&total>hechasAhora)trozos.push(conPlantilla(T.faltan,{n:total-hechasAhora}));
        saludo.textContent=trozos.join(' · ');
        saludo.hidden=false;
        // El nombre se pide DESPUÉS de la primera lección marcada y no antes:
        // preguntárselo a quien acaba de llegar es un formulario en la puerta.
        pedirNombre.hidden=!!quien;
      }
      boton.addEventListener('click',function(){
        var lista=hechas(), i=lista.indexOf(n);
        if(i>=0){lista.splice(i,1)}else{lista.push(n)}
        guardar(CLAVE_HECHAS,lista);pintar();
        if(i<0){
          anotarHoy();felicitar();
          if(siguiente){siguiente.classList.add('destacado')}
        }else{saludo.hidden=true;pedirNombre.hidden=true}
      });
      pintar();caja.appendChild(boton);caja.appendChild(saludo);

      // El campo del nombre, montado aquí y no servido en el HTML: sin
      // JavaScript no habría dónde guardarlo y sería un formulario que no
      // hace nada.
      var etiqueta=document.createElement('label');
      etiqueta.textContent=T.nombre_label||'';
      var campo=document.createElement('input');
      campo.type='text';campo.autocomplete='given-name';campo.maxLength=40;
      var guardarNombre=document.createElement('button');
      guardarNombre.type='button';guardarNombre.className='boton secundario';
      guardarNombre.textContent=T.nombre_boton||'';
      var notaNombre=document.createElement('span');
      notaNombre.className='aviso-chico';notaNombre.textContent=T.nombre_nota||'';
      guardarNombre.addEventListener('click',function(){
        var v=campo.value.trim().slice(0,40);
        if(!v)return;
        try{localStorage.setItem(CLAVE_NOMBRE,v)}catch(e){}
        pedirNombre.hidden=true;felicitar();
      });
      pedirNombre.appendChild(etiqueta);pedirNombre.appendChild(campo);
      pedirNombre.appendChild(guardarNombre);pedirNombre.appendChild(notaNombre);
      caja.appendChild(pedirNombre);
    }
  }

  // --- en la portada: continuar donde se dejó ---
  var seguir=document.getElementById('continuar');
  if(seguir){
    var ultima=leer(CLAVE_ULTIMA,null), destino=ultima?url(ultima):null;
    if(destino){
      seguir.href=destino;
      seguir.textContent=T.continuar+' '+ultima;
      seguir.hidden=false;
      var empezar=document.getElementById('empezar');
      if(empezar){empezar.textContent=T.empezar;empezar.classList.add('secundario')}
    }
  }

  // --- el nombre, en la portada y desde la primera visita ---
  //
  // Vive FUERA de `#mio` a propósito. `#mio` se enciende solo cuando ya hay
  // lecciones marcadas, así que el campo metido ahí era invisible justo para
  // quien acaba de llegar, que es a quien el profesor quería preguntarle.
  // Lo que no se hace es una ventana al entrar: un formulario que tapa la
  // página antes de que el visitante haya visto nada es la forma más fiable
  // de perderlo.
  var hueco=document.getElementById('nombre-portada');
  if(hueco){
    var ponerNombre=function(){
      hueco.innerHTML='';
      var quien=nombre();
      if(quien){
        // Ya lo dio: se le saluda y se le deja cambiarlo, sin un campo
        // abierto ocupando sitio.
        var hola=document.createElement('span');
        hola.textContent=conPlantilla(T.vuelta,{nombre:quien});
        var otro=document.createElement('button');
        otro.type='button';otro.className='boton secundario';
        otro.textContent=T.nombre_cambiar||T.nombre_boton||'';
        otro.addEventListener('click',function(){
          try{localStorage.removeItem(CLAVE_NOMBRE)}catch(e){}
          ponerNombre();
        });
        hueco.appendChild(hola);hueco.appendChild(otro);
      }else{
        var et=document.createElement('label');et.textContent=T.nombre_label||'';
        var ca=document.createElement('input');
        ca.type='text';ca.autocomplete='given-name';ca.maxLength=40;
        var bo=document.createElement('button');
        bo.type='button';bo.className='boton secundario';bo.textContent=T.nombre_boton||'';
        var no=document.createElement('span');
        no.className='aviso-chico';no.textContent=T.nombre_nota||'';
        var guardarlo=function(){
          var v=ca.value.trim().slice(0,40);
          if(!v)return;
          try{localStorage.setItem(CLAVE_NOMBRE,v)}catch(e){}
          ponerNombre();
        };
        bo.addEventListener('click',guardarlo);
        // Enter guarda: en el móvil el teclado tapa el botón.
        ca.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();guardarlo()}});
        hueco.appendChild(et);hueco.appendChild(ca);hueco.appendChild(bo);hueco.appendChild(no);
      }
      hueco.hidden=false;
    };
    ponerNombre();
  }

  // --- el contador personal, donde lo haya ---
  var hechasAhora=hechas(), publicadas=window.CURSO_PUBLICADAS||0;
  var contador=document.getElementById('mio');
  if(contador&&hechasAhora.length){
    contador.hidden=false;
    var cifra=contador.querySelector('.n'), texto=contador.querySelector('.texto');
    if(cifra)cifra.textContent=hechasAhora.length;
    if(texto)texto.textContent='/ '+publicadas+' '+T.tuyo;
    var barra=contador.querySelector('.barra i');
    if(barra&&publicadas)barra.style.width=Math.max(hechasAhora.length*100/publicadas,1)+'%';

    // La racha y el nombre, en el recuadro de progreso.
    //
    // Aquí y NO en una ventana al entrar: un formulario en la puerta, antes
    // de que el visitante haya visto nada, es la forma más fiable de
    // perderlo. El sitio pide el nombre donde ya hay una relación —después
    // de la primera lección marcada— y aquí lo deja cambiar.
    var r=rachas(), quien=nombre();
    var linea=document.createElement('p');
    linea.className='racha';
    var partes=[];
    if(r.actual)partes.push(conPlantilla(T.racha,{n:r.actual,dias:plural(r.actual,T.racha_dias)}));
    if(r.mejor>r.actual)partes.push(conPlantilla(T.racha_mejor,
      {n:r.mejor,dias:plural(r.mejor,T.racha_dias)}));
    if(partes.length){
      linea.textContent=(quien?conPlantilla(T.vuelta,{nombre:quien})+' ':'')+partes.join(' · ');
      var antesDe=document.getElementById('calendario');
      if(antesDe&&antesDe.parentNode===contador)contador.insertBefore(linea,antesDe);
      else contador.appendChild(linea);
    }
    if(!quien){
      var pide=document.createElement('p');
      pide.className='pide-nombre';
      var et=document.createElement('label');et.textContent=T.nombre_label||'';
      var ca=document.createElement('input');
      ca.type='text';ca.autocomplete='given-name';ca.maxLength=40;
      var bo=document.createElement('button');
      bo.type='button';bo.className='boton secundario';bo.textContent=T.nombre_boton||'';
      var no=document.createElement('span');
      no.className='aviso-chico';no.textContent=T.nombre_nota||'';
      bo.addEventListener('click',function(){
        var v=ca.value.trim().slice(0,40);
        if(!v)return;
        try{localStorage.setItem(CLAVE_NOMBRE,v)}catch(e){}
        pide.hidden=true;
        linea.textContent=conPlantilla(T.vuelta,{nombre:v})+' '+partes.join(' · ');
        if(!linea.parentNode){
          var ant=document.getElementById('calendario');
          if(ant&&ant.parentNode===contador)contador.insertBefore(linea,ant);
          else contador.appendChild(linea);
        }
      });
      pide.appendChild(et);pide.appendChild(ca);pide.appendChild(bo);pide.appendChild(no);
      contador.appendChild(pide);
    }
  }


  // --- el calendario del año: una casilla por día ---
  //
  // Lo mismo que `#mio` y las barras del mapa, y por la razón escrita allí:
  // solo si ya hay progreso. Trescientas sesenta y cuatro casillas vacías en
  // la primera visita no se leen como «empieza», se leen como un hueco.
  var cal=document.getElementById('calendario');
  if(cal&&hechasAhora.length){
    var DIA2=86400000, hoyCad=hoy(), hoyMs=dia(hoyCad);
    var puestas={};fechas().forEach(function(f){puestas[f]=1});
    // Se arranca en el lunes de hace 51 semanas, así que las 52 columnas son
    // semanas enteras y la última es la de hoy. Los días de esta semana que
    // aún no han llegado se dibujan vacíos y sin fondo: dejarlos fuera
    // cambiaría el alto de la última columna y la rejilla saldría mellada.
    var lunes=hoyMs-((new Date(hoyMs).getUTCDay()+6)%7)*DIA2;
    var ini=lunes-51*7*DIA2, cuenta=0;
    var rejilla=document.createElement('div');
    rejilla.className='cal-rejilla';
    for(var q=0;q<364;q++){
      var ms=ini+q*DIA2, f=new Date(ms);
      var mm=f.getUTCMonth()+1, dd=f.getUTCDate();
      var clave=f.getUTCFullYear()+'-'+(mm<10?'0':'')+mm+'-'+(dd<10?'0':'')+dd;
      var c=document.createElement('span');
      var clases='cal-dia';
      if(ms>hoyMs){clases+=' futuro'}
      else if(puestas[clave]){clases+=' hecho';cuenta++}
      if(clave===hoyCad)clases+=' es-hoy';
      c.className=clases;
      c.title=clave+(clave===hoyCad&&T.calendario_hoy?' · '+T.calendario_hoy:'');
      rejilla.appendChild(c);
    }
    // Una sola etiqueta para la rejilla entera y las casillas calladas: un
    // lector de pantalla leyendo 364 celdas sería inservible, y el dato que
    // de verdad se quiere oír es cuántos días son.
    var nota=conPlantilla(T.calendario_nota,
      {n:cuenta,dias:plural(cuenta,T.racha_dias)});
    rejilla.setAttribute('role','img');
    rejilla.setAttribute('aria-label',nota);
    var cabc=document.createElement('p');
    cabc.className='cal-cab';
    var fuerte=document.createElement('strong');
    fuerte.textContent=T.calendario||'';
    var suave=document.createElement('span');
    suave.textContent=nota;
    cabc.appendChild(fuerte);cabc.appendChild(suave);
    cal.appendChild(cabc);cal.appendChild(rejilla);
    cal.hidden=false;
    // Desplazada hasta hoy. En el móvil la rejilla desborda y lo que importa
    // es el extremo derecho, no enero.
    rejilla.scrollLeft=rejilla.scrollWidth;
  }

  // --- el certificado, al cerrar un nivel ---
  //
  // Es un sitio estático, así que esto se dibuja en el navegador y no lo
  // firma nadie: el propio papel lo dice —«no es un documento oficial»—. No
  // nombra al Instituto Cervantes, que es la decisión del 2026-10-27: el
  // sitio habla del EXAMEN, que es un hecho, no de una autoría prestada.
  var dip=document.getElementById('diploma');
  if(dip&&hechasAhora.length){
    var niveles=window.CURSO_NIVELES||[];
    var dentroN={};hechasAhora.forEach(function(x){dentroN[x]=1});
    // El nivel más alto que esté ENTERO. A2 pide las 365 y no solo las de
    // A2: terminar A2 incluye haber hecho A1, y un certificado de A2 con el
    // A1 a medias no diría la verdad.
    var logrado=null;
    for(var z=0;z<niveles.length;z++){
      var nv=niveles[z], todo=nv.hasta>0;
      for(var w=1;w<=nv.hasta;w++){if(!dentroN[w]){todo=false;break}}
      if(todo)logrado=nv;
    }
    if(logrado){
      var quienD=nombre();
      if(!quienD){
        // Sin nombre no hay certificado que valga: se señala el campo que ya
        // existe arriba en vez de abrir otro aquí.
        var pideD=document.createElement('p');
        pideD.textContent=T.diploma_pide_nombre||'';
        dip.appendChild(pideD);
      }else{
        var botonD=document.createElement('button');
        botonD.type='button';botonD.className='boton secundario';
        botonD.textContent=conPlantilla(T.diploma_boton,{nivel:logrado.nivel});
        botonD.addEventListener('click',function(){
          // Se esperan las fuentes: sin esto el lienzo dibuja con la letra de
          // reserva del navegador y el certificado sale con otra tipografía
          // que el sitio.
          // `fonts.ready` NO basta, y esto se vio mirando el PNG y no
          // razonándolo: cada cara lleva `unicode-range`, así que el
          // navegador no se baja la cirílica hasta que algo la usa, y
          // dibujar en un lienzo no cuenta como usarla. Sin pedirlas por su
          // nombre Y con el texto que se va a escribir, el certificado sale
          // con la letra de reserva del sistema mientras la página de al
          // lado está en Literata y Onest.
          var pintar=function(){descargarDiploma(logrado,quienD)};
          if(document.fonts&&document.fonts.load){
            var muestra=quienD+(T.diploma_titulo||'')+(T.diploma_sub||'')+(T.diploma_quien||'');
            Promise.all([
              document.fonts.load('700 46px Onest',muestra),
              document.fonts.load('400 22px Onest',muestra),
              document.fonts.load('400 56px Literata',quienD)
            ]).then(pintar,pintar);
          }
          else{pintar()}
        });
        dip.appendChild(botonD);
      }
      dip.hidden=false;
    }
  }

  // --- en el índice: una marca en cada lección hecha ---
  var filas=document.querySelectorAll('li[data-leccion]');
  if(filas.length){
    var mapa={};hechasAhora.forEach(function(x){mapa[x]=1});
    for(var i=0;i<filas.length;i++){
      if(mapa[parseInt(filas[i].getAttribute('data-leccion'),10)]){
        filas[i].classList.add('hecha');
      }
    }
  }

  // --- en el mapa de unidades: TU progreso, no el del curso ---
  //
  // La barra de cada tarjeta medía cuántas lecciones de esa unidad están
  // ESCRITAS, y desde que el curso está entero eso son las catorce en las
  // veinticuatro: una barra llena que no dice nada. El navegador sí sabe
  // cuáles has hecho tú, así que la misma barra pasa a medir eso.
  //
  // Solo si ya hay progreso, igual que `#mio` y por la misma razón: en la
  // primera visita, veinticuatro barras en cero desaniman. Sin nada hecho la
  // página se queda exactamente como la sirve el servidor.
  var tarjetas=document.querySelectorAll('.u-tarjeta[data-desde]');
  if(tarjetas.length&&hechasAhora.length){
    var dentro={};hechasAhora.forEach(function(x){dentro[x]=1});
    for(var k=0;k<tarjetas.length;k++){
      var tj=tarjetas[k],
          desde=parseInt(tj.getAttribute('data-desde'),10),
          hasta=parseInt(tj.getAttribute('data-hasta'),10);
      if(!(desde>0)||!(hasta>=desde))continue;
      var total=hasta-desde+1, mias=0;
      for(var d=desde;d<=hasta;d++){if(dentro[d])mias++}
      var cuenta=tj.querySelector('.hechas');
      if(cuenta){
        var palabra=cuenta.getAttribute('data-palabra')||'';
        cuenta.textContent=mias+'/'+total+(palabra?' '+palabra:'');
      }
      var barra=tj.querySelector('.mini');
      if(barra){
        barra.hidden=false;
        var raya=barra.querySelector('i');
        if(raya)raya.style.width=(mias?Math.max(mias*100/total,3):0)+'%';
      }
      if(mias===total)tj.classList.add('completa');
    }
  }

  // --- el código de respaldo ---
  //
  // El progreso vive en localStorage, que se va con «limpiar datos del
  // navegador» y no viaja a otro teléfono. Cuentas de verdad costarían un
  // servicio, datos personales y soporte; un código que el alumno guarda
  // DONDE QUIERA no cuesta nada y no deja nada nuestro en ningún sitio.
  //
  // Un bit por lección: las 365 caben en 46 bytes, o sea 64 caracteres en
  // base64, y el código NO crece según se avanza. Eso es lo que lo hace
  // pegable en un mensaje de Telegram, que es donde lo va a guardar la gente.
  var BYTES = 46;                       // 365 lecciones / 8, redondeado
  var MARCA = 'ESR1';                   // para reconocer un código nuestro

  function aCodigo(lista, ultima){
    var b = new Uint8Array(2 + BYTES);
    b[0] = (ultima >> 8) & 255; b[1] = ultima & 255;
    for(var i=0;i<lista.length;i++){
      var n = lista[i] - 1;
      if(n >= 0 && n < BYTES*8) b[2 + (n>>3)] |= 1 << (n & 7);
    }
    var cad=''; for(var j=0;j<b.length;j++) cad += String.fromCharCode(b[j]);
    return MARCA + btoa(cad).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  }

  function deCodigo(texto){
    // Devuelve null ante CUALQUIER duda. Restaurar nunca puede destruir lo
    // que el alumno ya tiene por un código mal pegado o cortado a medias.
    try{
      texto = String(texto||'').replace(/\s+/g,'');
      if(texto.slice(0,4) !== MARCA) return null;
      var cad = atob(texto.slice(4).replace(/-/g,'+').replace(/_/g,'/'));
      if(cad.length !== 2 + BYTES) return null;
      var ultima = (cad.charCodeAt(0) << 8) | cad.charCodeAt(1);
      var lista = [];
      for(var i=0;i<BYTES;i++){
        var v = cad.charCodeAt(2+i);
        for(var bit=0;bit<8;bit++) if(v & (1<<bit)) lista.push(i*8 + bit + 1);
      }
      if(ultima < 0 || ultima > BYTES*8) return null;
      return {hechas: lista, ultima: ultima};
    }catch(e){ return null; }
  }

  var copiar = document.getElementById('copiar-progreso');
  if(copiar){
    copiar.hidden = !hechasAhora.length;
    copiar.addEventListener('click', function(){
      var codigo = aCodigo(hechasAhora, leer(CLAVE_ULTIMA,0)||0);
      var aviso = document.getElementById('codigo-aviso');
      function mostrarAviso(){
        if(aviso){ aviso.textContent = T.copiado; aviso.hidden = false; }
      }
      // El portapapeles puede no estar (http, permisos, navegador viejo). Si
      // falla, el código se enseña en un campo para copiarlo a mano: quedarse
      // sin él sería lo único imperdonable aquí.
      function aMano(c){
        var campo = document.getElementById('codigo-mio');
        if(campo){ campo.hidden=false; campo.value=c; campo.select(); }
        mostrarAviso();
      }
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(codigo).then(mostrarAviso, function(){ aMano(codigo); });
      } else { aMano(codigo); }
    });
  }

  var restaurar = document.getElementById('restaurar-progreso');
  var cajaRest = document.getElementById('restaurar-caja');
  if(restaurar && cajaRest){
    restaurar.addEventListener('click', function(){ cajaRest.hidden = !cajaRest.hidden; });
    var aplicar = document.getElementById('restaurar-aplicar');
    if(aplicar) aplicar.addEventListener('click', function(){
      var campo = document.getElementById('restaurar-codigo');
      var aviso = document.getElementById('restaurar-aviso');
      var datos = deCodigo(campo && campo.value);
      function di(t){ if(aviso){ aviso.textContent=t; aviso.hidden=false; } }
      if(!datos){ di(T.malo); return; }
      // Un código viejo trae menos lecciones: se pregunta antes de pisar.
      if(datos.hechas.length < hechasAhora.length){
        // Los huecos que rellena el navegador van con %…% y no con {…}: así
        // se distinguen de un vistazo de los que rellena Python, y la prueba
        // que caza un «{n}» sin sustituir en la página sigue cazándolo.
        var q = (T.menos||'').replace('%a%', datos.hechas.length).replace('%b%', hechasAhora.length);
        if(!window.confirm(q)) return;
      }
      guardar(CLAVE_HECHAS, datos.hechas);
      if(datos.ultima) guardar(CLAVE_ULTIMA, datos.ultima);
      di((T.hecho_restaurar||'').replace('%n%', datos.hechas.length));
      location.reload();
    });
  }

  // --- copiar el enlace de la lección ---
  // Sin widget y sin librería: el navegador ya sabe copiar. Si el portapapeles
  // no está disponible, el botón no miente: se queda como estaba.
  var copiarEnlace = document.getElementById('copiar-enlace');
  if(copiarEnlace && navigator.clipboard && navigator.clipboard.writeText){
    copiarEnlace.addEventListener('click', function(){
      navigator.clipboard.writeText(copiarEnlace.dataset.url).then(function(){
        copiarEnlace.textContent = copiarEnlace.dataset.ok;
      });
    });
  }

  // --- borrar el progreso ---
  var borrar=document.getElementById('borrar-progreso');
  if(borrar){
    borrar.hidden=!hechasAhora.length&&!leer(CLAVE_ULTIMA,null);
    borrar.addEventListener('click',function(){
      if(!window.confirm(T.confirmar))return;
      try{localStorage.removeItem(CLAVE_HECHAS);localStorage.removeItem(CLAVE_ULTIMA)}catch(e){}
      location.reload();
    });
  }
})();"""


# Un solo <audio> para toda la página: con uno por frase, el navegador abre
# 2.600 conexiones y en móvil se nota. Y al empezar una se para la anterior,
# que es lo que se quiere al ir comparando frases.
AUDIO_JS = r"""(function(){
  var sonando=null, reproductor=new Audio();
  reproductor.addEventListener('ended',function(){if(sonando){sonando.setAttribute('aria-pressed','false');sonando=null}});
  document.addEventListener('click',function(e){
    var b=e.target.closest('.suena');
    if(!b)return;
    e.preventDefault();
    if(sonando===b){reproductor.pause();b.setAttribute('aria-pressed','false');sonando=null;return}
    if(sonando)sonando.setAttribute('aria-pressed','false');
    reproductor.src=b.getAttribute('data-audio');
    reproductor.currentTime=0;
    // Si el archivo no está, no se avisa con una alerta: el botón vuelve a su
    // sitio y la lección se sigue leyendo igual.
    reproductor.play().then(function(){b.setAttribute('aria-pressed','true');sonando=b})
                      .catch(function(){b.setAttribute('aria-pressed','false');sonando=null});
  });
})();"""


TEST_JS = r"""(function(){
  var D=window.CURSO_TEST; if(!D)return;
  var caja=document.getElementById('test'); if(!caja)return;
  var i=0, fallos=[], aciertos=0, reloj=null, queda=0, preguntas=[];

  // El test cambia en cada partida: de cada unidad se escoge UNA pregunta de
  // las que hay en el banco, y las tres opciones se barajan. Asi repetirlo no
  // premia la memoria de la pantalla anterior.
  //
  // Lo que NO se baraja es el orden de los grupos: vienen ordenados por unidad
  // y asi se quedan, porque la recomendacion sale de la unidad de la PRIMERA
  // fallada. Desordenadas, fallar la ultima colocaria antes que fallar la
  // primera y nada avisaria.
  function barajar(q){
    // Se copia la pregunta: barajando sobre el original, la segunda partida
    // encontraria las opciones ya movidas de la primera y `correcta` apuntando
    // a otra cosa. Es el fallo que diria «has fallado» a quien acerto.
    var ops=q.opciones.slice(), orden=[], n;
    for(n=0;n<ops.length;n++)orden.push(n);
    for(n=orden.length-1;n>0;n--){
      var j=Math.floor(Math.random()*(n+1)), t=orden[n]; orden[n]=orden[j]; orden[j]=t;
    }
    return {pregunta:q.pregunta, unidad:q.unidad, error:q.error,
            opciones:orden.map(function(k){return ops[k]}),
            correcta:orden.indexOf(q.correcta)};
  }

  function repartir(){
    preguntas=(D.grupos||[]).map(function(g){
      return barajar(g[Math.floor(Math.random()*g.length)]);
    });
  }

  function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML}

  // Un cronometro POR PREGUNTA, no para todo el test. Al agotarse cuenta como
  // fallada y pasa, que es lo que significa para colocar a alguien: lo que no
  // sabes en treinta segundos no lo sabes. `D.segundos` a 0 lo apaga.
  function parar(){if(reloj){clearInterval(reloj);reloj=null}}

  function arrancar(){
    parar();
    if(!D.segundos)return;
    queda=D.segundos;
    pinta();
    reloj=setInterval(function(){
      queda-=0.1;
      if(queda<=0){parar();responder(-1);return}
      pinta();
    },100);
  }

  function pinta(){
    var n=caja.querySelector('.test-reloj i'), s=caja.querySelector('.test-seg');
    if(n)n.style.width=(queda*100/D.segundos)+'%';
    if(s)s.textContent=Math.ceil(queda)+' '+D.t.segundos;
  }

  function pregunta(){
    var q=preguntas[i];
    caja.innerHTML='<div class="test-caja">'
      +'<div class="test-cuenta">'+(i+1)+' '+esc(D.t.de)+' '+preguntas.length
      +' · '+esc(D.t.instruccion)
      +(D.segundos?'<b class="test-seg"></b>':'')+'</div>'
      +(D.segundos?'<div class="test-reloj"><i></i></div>':'')
      +'<p class="test-pregunta">'+esc(q.pregunta)+'</p>'
      +'<div class="test-ops">'+q.opciones.map(function(o,n){
          return '<button type="button" data-n="'+n+'">'+esc(o)+'</button>'}).join('')+'</div>'
      +'<div class="test-barra"><i style="width:'+(i*100/preguntas.length)+'%"></i></div></div>';
    caja.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){responder(parseInt(b.dataset.n,10))});
    });
    arrancar();
  }

  // n === -1 es «se acabó el tiempo». Se anota aparte para poder decirlo en el
  // resultado: no es lo mismo equivocarse que no llegar.
  function responder(n){
    parar();
    var q=preguntas[i];
    if(n===q.correcta){aciertos++}
    else{fallos.push(n===-1?Object.assign({},q,{tarde:true}):q)}
    i++;
    if(i<preguntas.length){pregunta()}else{resultado()}
  }

  function resultado(){
    parar();
    // Se empieza donde se acaba lo que ya se sabe: la unidad de la PRIMERA
    // fallada. Y si esa unidad aun no esta escrita -el curso tiene 100
    // lecciones de 365-, la ultima escrita, que no es un parche: si ya sabe
    // todo lo que el curso cubre, ahi es exactamente donde empieza. Acertarlo
    // todo lleva al mismo sitio. Sin ese `|| D.ultima` la pantalla de
    // resultado se quedaba sin su boton.
    var u=fallos.length?fallos[0].unidad:null;
    var dest=(u&&D.inicios[u])||D.ultima;
    var h='<div class="test-caja"><div class="test-cuenta">'+esc(D.t.resultado)+'</div>'
      +'<p class="test-pregunta">'+aciertos+' / '+preguntas.length+' '+esc(D.t.aciertos)+'</p>';
    if(dest){
      h+='<p>'+esc(D.t.empieza_en)+' <b>'+dest.n+'</b>.</p>'
        +'<p><a class="boton" href="'+dest.url+'">'+esc(D.t.ir)+'</a></p>';
    }
    if(!fallos.length){h+='<p>'+esc(D.t.todo_bien)+'</p>'}
    else{
      h+='<p class="test-cuenta" style="margin-top:1.2rem">'+esc(D.t.errores)+'</p>';
      fallos.forEach(function(q){
        h+='<div class="test-fallo"><b>'+esc(q.opciones[q.correcta])+'</b>'
          +(q.tarde?'<span class="test-tarde">'+esc(D.t.tiempo_fuera)+'</span>':'')
          +'<span>'+esc(q.error)+'</span></div>';
      });
    }
    h+='<p style="margin-top:1.2rem"><button type="button" class="boton secundario" id="otra-vez">'
      +esc(D.t.repetir)+'</button></p></div>';
    caja.innerHTML=h;
    var r=document.getElementById('otra-vez');
    if(r)r.addEventListener('click',function(){i=0;fallos=[];aciertos=0;repartir();pregunta()});
  }

  // El boton nace oculto y lo enciende el navegador, como el resto del sitio:
  // sin JavaScript seria un boton que no hace nada, y para ese caso esta el
  // <noscript>, que manda a la leccion 1. Al empezar desaparece: volver a
  // pulsarlo reiniciaria el test a mitad, y al lado del resultado no dice nada
  // que «Пройти заново» no diga mejor.
  var arranque=document.getElementById('test-arranque');
  var boton=document.getElementById('test-empezar');
  if(arranque&&boton){
    arranque.hidden=false;
    boton.addEventListener('click',function(){arranque.hidden=true;repartir();pregunta()});
  }
})();"""


# Los idiomas apagados: explican en vez de no hacer nada. Va en línea y no en
# un fichero aparte porque son ocho líneas y solo está en las páginas que lo
# necesitan.
IDIOMA_SCRIPT = """<script>(function(){
  var aviso=document.getElementById('sin-idioma'); if(!aviso)return;
  document.querySelectorAll('.idiomas .apagado').forEach(function(b){
    b.addEventListener('click',function(){
      var a=aviso.querySelector('a');
      a.href=b.dataset.portada;
      a.textContent=a.dataset.ir+' ('+b.dataset.idioma+') \u2192';
      aviso.hidden=false;
    });
  });
})();</script>"""


HUECOS_JS = r"""(function(){
  var D=window.CURSO_HUECOS; if(!D)return;
  var T=D.t||{};

  // Dos formas de rellenar, porque en el móvil arrastrar es incómodo:
  //   - pulsas una ficha y luego el hueco;
  //   - o pulsas un hueco vacío y la ficha elegida cae ahí.
  // Y pulsar un hueco lleno lo vacía y devuelve la ficha, que es como se
  // corrige uno sin tener que empezar de cero.
  var elegida = null;

  // La cita del banco sobra en cuanto hay fichas: las mismas palabras dos
  // veces seguidas. Se esconde desde aquí y no al construir, para que sin
  // JavaScript la cita siga estando —ahí es lo único que dice qué palabras
  // hay—.
  document.querySelectorAll('.banco-escrito').forEach(function(q){ q.hidden = true; });

  function fichasDe(ej){ return document.querySelectorAll('.ficha[data-ej="'+ej+'"]'); }
  function huecosDe(ej){ return document.querySelectorAll('.hueco[data-ej="'+ej+'"]'); }

  function repintarFichas(ej){
    var usadas = {};
    huecosDe(ej).forEach(function(h){ if(h.textContent) usadas[h.textContent] = (usadas[h.textContent]||0)+1; });
    var vistas = {};
    fichasDe(ej).forEach(function(f){
      var n = f.textContent;
      vistas[n] = (vistas[n]||0)+1;
      // Una palabra puede repetirse en el banco y usarse varias veces: se
      // apaga la ficha solo cuando ya no quedan copias libres.
      f.classList.toggle('gastada', (usadas[n]||0) >= vistas[n] && (usadas[n]||0) > 0
                                     && fichasDe(ej).length === Object.keys(vistas).length);
    });
  }

  function soltar(h){
    if(!h.textContent) return;
    h.textContent = '';
    h.classList.remove('bien','mal');
    repintarFichas(h.dataset.ej);
  }

  document.addEventListener('click', function(e){
    var f = e.target.closest('.ficha');
    if(f){
      if(elegida === f){ elegida = null; f.setAttribute('aria-pressed','false'); return; }
      if(elegida) elegida.setAttribute('aria-pressed','false');
      elegida = f; f.setAttribute('aria-pressed','true');
      return;
    }
    var h = e.target.closest('.hueco');
    if(h){
      if(h.textContent){ soltar(h); return; }
      if(!elegida || elegida.dataset.ej !== h.dataset.ej) return;
      h.textContent = elegida.textContent;
      h.classList.remove('bien','mal');
      elegida.setAttribute('aria-pressed','false');
      elegida = null;
      repintarFichas(h.dataset.ej);
      return;
    }
    var c = e.target.closest('.comprobar');
    if(c) comprobar(c.dataset.ej);
  });

  // El teclado: un hueco es un botón, así que Enter y espacio tienen que
  // hacer lo mismo que el dedo.
  document.addEventListener('keydown', function(e){
    if(e.key !== 'Enter' && e.key !== ' ') return;
    var h = e.target.closest && e.target.closest('.hueco');
    if(!h) return;
    e.preventDefault();
    h.click();
  });

  function plano(x){
    return (x||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim();
  }

  function comprobar(ej){
    var datos = D.ejercicios[ej]; if(!datos) return;
    var huecos = huecosDe(ej), bien = 0;
    huecos.forEach(function(h, i){
      var ok = plano(h.textContent) === plano(datos.respuestas[i]);
      h.classList.toggle('bien', ok);
      h.classList.toggle('mal', !ok);
      if(ok) bien++;
    });
    var m = document.querySelector('.marcador[data-ej="'+ej+'"]');
    if(m) m.textContent = (T.resultado||'').replace('%a%', bien).replace('%b%', huecos.length);
  }
})();"""


GRABAR_JS = r"""(function(){
  var D=window.CURSO_GRABAR; if(!D)return;
  var caja=document.getElementById('grabar'); if(!caja)return;
  // Sin micrófono o sin MediaRecorder el bloque NO sale. Es la regla del
  // sitio: un botón que no puede hacer nada es peor que ningún botón, y aquí
  // además pediría un permiso para nada.
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia)return;
  if(typeof MediaRecorder==='undefined')return;

  var T=D.t, grabadora=null, trozos=[], url=null, sonido=null;

  function boton(texto,secundario){
    // El tercer estado no existe: o es el botón principal o es secundario.
    // La primera versión recibía la clase como cadena y `''` caía en el
    // `||`, así que «Записать» salía perfilado como los demás cuando es la
    // única acción de este bloque.
    var b=document.createElement('button');
    b.type='button';b.className=secundario?'boton secundario':'boton';
    b.textContent=texto;
    return b;
  }
  var bGrabar=boton(T.grabar,false), bParar=boton(T.parar,true), bOir=boton(T.oir,true);
  var aviso=document.createElement('p');
  aviso.className='aviso-chico';aviso.hidden=true;
  bParar.hidden=true;bOir.hidden=true;

  function soltar(){
    // La grabación anterior se tira en cuanto hay otra: no se acumulan blobs
    // en memoria y no queda nada al salir de la página.
    if(url){URL.revokeObjectURL(url);url=null}
    if(sonido){sonido.pause();sonido=null}
  }

  bGrabar.addEventListener('click',function(){
    aviso.hidden=true;
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(flujo){
      soltar();
      trozos=[];
      // Sin `mimeType`: cada navegador graba en lo suyo —Safari en mp4, el
      // resto en webm— y fijarlo aquí dejaría a uno de los dos fuera.
      grabadora=new MediaRecorder(flujo);
      grabadora.addEventListener('dataavailable',function(e){if(e.data.size)trozos.push(e.data)});
      grabadora.addEventListener('stop',function(){
        // El micrófono se apaga de verdad: sin esto la pestaña se queda con
        // el punto rojo encendido hasta que se cierra.
        flujo.getTracks().forEach(function(p){p.stop()});
        if(!trozos.length)return;
        url=URL.createObjectURL(new Blob(trozos,{type:grabadora.mimeType||'audio/webm'}));
        bOir.hidden=false;bGrabar.textContent=T.otra;
      });
      grabadora.start();
      bGrabar.hidden=true;bParar.hidden=false;bOir.hidden=true;
      aviso.textContent=T.grabando;aviso.hidden=false;
    }).catch(function(){
      // Permiso denegado, o no hay micrófono. Se dice, y se dice que la
      // lección se puede hacer igual: el ejercicio es decirlo en voz alta.
      aviso.textContent=T.sin_permiso;aviso.hidden=false;
    });
  });

  bParar.addEventListener('click',function(){
    if(grabadora&&grabadora.state!=='inactive')grabadora.stop();
    bParar.hidden=true;bGrabar.hidden=false;aviso.hidden=true;
  });

  bOir.addEventListener('click',function(){
    if(!url)return;
    if(!sonido)sonido=new Audio();
    sonido.src=url;sonido.currentTime=0;sonido.play().catch(function(){});
  });

  // Al salir de la página no queda nada. No hace falta para que sea cierto
  // —un blob en memoria muere con la pestaña— pero sí para que el punto rojo
  // del micrófono no se quede encendido si se navega a mitad de una toma.
  window.addEventListener('pagehide',function(){
    if(grabadora&&grabadora.state!=='inactive')grabadora.stop();
    soltar();
  });

  var fila=document.createElement('div');
  fila.className='botones';
  fila.appendChild(bGrabar);fila.appendChild(bParar);fila.appendChild(bOir);
  caja.appendChild(fila);caja.appendChild(aviso);
  caja.hidden=false;
})();"""


QUIZ_JS = r"""(function(){
  var D=window.CURSO_QUIZ; if(!D||!D.preguntas||!D.preguntas.length)return;
  var caja=document.getElementById('quiz'); if(!caja)return;
  var arranque=document.getElementById('quiz-arranque');
  var boton=document.getElementById('quiz-empezar');
  if(!arranque||!boton)return;
  var P=D.preguntas, T=D.t, i=0, aciertos=0, fallos=[];

  function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML}

  // Nace oculto y lo enciende el navegador, como todo lo de este sitio: sin
  // JavaScript un botón que no hace nada es peor que ningún botón, y el
  // vocabulario del día ya está en su tabla ahí arriba, con su traducción.
  arranque.hidden=false;

  function pregunta(){
    var q=P[i];
    caja.innerHTML='<div class="test-caja">'
      +'<div class="test-cuenta">'+(i+1)+' '+esc(T.de)+' '+P.length+'</div>'
      +'<p class="test-cuenta">'+esc(T.instruccion)+'</p>'
      +'<p class="test-pregunta">'+esc(q.ru)+'</p>'
      +'<div class="test-ops">'+q.opciones.map(function(o,n){
          return '<button type="button" data-n="'+n+'">'+esc(o)+'</button>'}).join('')+'</div>'
      +'<div class="test-barra"><i style="width:'+(i*100/P.length)+'%"></i></div></div>';
    caja.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){responder(parseInt(b.dataset.n,10))});
    });
  }

  function responder(n){
    var q=P[i];
    if(n===q.correcta){aciertos++}else{fallos.push(q)}
    i++;
    if(i<P.length){pregunta()}else{resultado()}
  }

  function resultado(){
    var h='<div class="test-caja"><div class="test-cuenta">'+esc(T.resultado)+'</div>'
      +'<p class="test-pregunta">'+aciertos+' / '+P.length+' '+esc(T.aciertos)+'</p>';
    if(!fallos.length){h+='<p>'+esc(T.sin_fallos)+'</p>'}
    else{
      h+='<p class="test-cuenta" style="margin-top:1.2rem">'+esc(T.errores)+'</p>';
      fallos.forEach(function(q){
        var oir=q.mp3?'<button type="button" class="suena" aria-pressed="false"'
          +' data-audio="'+esc(q.mp3)+'" aria-label="'+esc(q.opciones[q.correcta])+'">▶</button>':'';
        h+='<div class="test-fallo"><b>'+oir+esc(q.opciones[q.correcta])+'</b>'
          +'<span>'+esc(q.ru)+'</span></div>';
      });
    }
    h+='<p style="margin-top:1.2rem">'
      +'<button type="button" class="boton secundario" id="quiz-otra">'+esc(T.repetir)+'</button></p></div>';
    caja.innerHTML=h;
    var r=document.getElementById('quiz-otra');
    // Las mismas cinco y en el mismo orden: las elige el generador, así que
    // repetir es repasar lo que se acaba de fallar y no una tirada nueva.
    if(r)r.addEventListener('click',function(){i=0;aciertos=0;fallos=[];pregunta()});
  }

  boton.addEventListener('click',function(){arranque.hidden=true;pregunta()});
})();"""


PRUEBA_JS = r"""(function(){
  var D=window.CURSO_PRUEBA; if(!D)return;
  var caja=document.getElementById('prueba'); if(!caja)return;
  var papel=document.getElementById('prueba-papel');
  var clave=document.getElementById('prueba-clave');
  // En un repaso la clave no se envuelve: ya esta plegada tras su boton, y
  // lleva ademas las claves del dictado y del calentamiento. Asi que alli el
  // boton de «ver la clave» abre ESE plegado, pulsando su boton de verdad para
  // que la etiqueta («ver» / «ocultar») no se quede mintiendo.
  var plegada=document.getElementById('clave');
  // Las preguntas vienen del JSON que deja el generador, y NO se barajan: la
  // clave impresa debajo las nombra por su letra («1 в»), asi que moverlas
  // haria que la clave del profesor dejara de corresponder.
  //
  // Esta linea faltaba. Sin ella `pregunta()` referenciaba una variable que no
  // existia, y el test entero moria con «preguntas is not defined» en cuanto se
  // pulsaba empezar: el papel ya estaba escondido y no salia nada en su lugar.
  // Llevaba asi desde que se publico, porque se comprobo el lector en Python y
  // nadie llego a pulsar el boton en un navegador.
  var preguntas=D.preguntas||[];
  var i=0, fallos=[], aciertos=0;

  function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML}

  // Sin JavaScript la pagina se queda EXACTAMENTE como estaba: las quince
  // preguntas y su clave, para leer o imprimir. El guion solo las esconde
  // cuando de verdad puede ofrecer algo mejor.
  if(papel)papel.hidden=true;
  if(clave)clave.hidden=true;

  function pregunta(){
    var q=preguntas[i];
    caja.innerHTML='<div class="test-caja">'
      +'<div class="test-cuenta">'+(i+1)+' '+esc(D.t.de)+' '+preguntas.length
      +' · '+esc(q.bloque)+'</div>'
      +'<p class="test-pregunta">'+esc(q.enunciado)+'</p>'
      +'<div class="test-ops">'+q.opciones.map(function(o,n){
          return '<button type="button" data-n="'+n+'">'+esc(o)+'</button>'}).join('')+'</div>'
      +'<div class="test-barra"><i style="width:'+(i*100/preguntas.length)+'%"></i></div></div>';
    caja.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){responder(parseInt(b.dataset.n,10))});
    });
  }

  function responder(n){
    var q=preguntas[i];
    if(n===q.correcta){aciertos++}else{fallos.push(q)}
    i++;
    if(i<preguntas.length){pregunta()}else{resultado()}
  }

  function resultado(){
    var h='<div class="test-caja"><div class="test-cuenta">'+esc(D.t.resultado)+'</div>'
      +'<p class="test-pregunta">'+aciertos+' / '+preguntas.length+' '+esc(D.t.aciertos)+'</p>';
    if(!fallos.length){h+='<p>'+esc(D.t.sin_fallos)+'</p>'}
    else{
      h+='<p class="test-cuenta" style="margin-top:1.2rem">'+esc(D.t.errores)+'</p>';
      fallos.forEach(function(q){
        // La clave del profesor dice de que leccion sale cada respuesta, asi
        // que el fallo no solo se corrige: se puede ir a releerlo.
        h+='<div class="test-fallo"><b>'+esc(q.opciones[q.correcta])+'</b>'
          +'<span>'+esc(q.enunciado)+'</span>'
          +(q.url?'<span><a href="'+q.url+'">'+esc(D.t.donde)+' '+q.n+' →</a></span>':'')
          +'</div>';
      });
    }
    h+='<p style="margin-top:1.2rem">'
      +'<button type="button" class="boton secundario" id="otra-vez">'+esc(D.t.repetir)+'</button> '
      +'<button type="button" class="boton secundario" id="ver-clave">'+esc(D.t.clave)+'</button></p></div>';
    caja.innerHTML=h;
    var r=document.getElementById('otra-vez');
    // Sin `repartir()`: eso es del test de nivel, que escoge una variante de
    // cada grupo. Aqui las quince preguntas son siempre las mismas.
    if(r)r.addEventListener('click',function(){i=0;fallos=[];aciertos=0;pregunta()});
    var v=document.getElementById('ver-clave');
    // El discurso sobre los distractores que cierra la clave es lo mejor del
    // dia, y solo ensena DESPUES de contestar: antes seria la respuesta.
    if(v)v.addEventListener('click',function(){
      if(clave){clave.hidden=false;clave.scrollIntoView({behavior:'smooth'})}
      else if(plegada){
        var z=document.getElementById('clave-boton');
        var bb=z&&z.querySelector('button');
        if(bb&&plegada.hidden)bb.click();
        plegada.scrollIntoView({behavior:'smooth'});
      }
      v.hidden=true;
    });
  }

  var arranque=document.getElementById('prueba-arranque');
  var boton=document.getElementById('prueba-empezar');
  if(arranque&&boton){
    arranque.hidden=false;
    boton.addEventListener('click',function(){arranque.hidden=true;pregunta()});
  }
})();"""


# ---------------------------------------------------------------- configuración
def cargar_config(ruta: pathlib.Path = CONFIG) -> dict:
    with open(ruta, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg["dominio"] = (cfg.get("dominio") or "").rstrip("/")
    cfg.setdefault("adsense", {}).setdefault("bloques", {})
    cfg.setdefault("analitica", {})
    cfg.setdefault("autor", {})
    return cfg


def cargar_textos(ruta: pathlib.Path = TEXTOS) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cargar_test(ruta: pathlib.Path = TEST) -> dict:
    """Las preguntas del test de nivel. Si el fichero no está, no hay test.

    Devolver {} y no reventar es deliberado: el test es una puerta de más, no
    el curso. Un sitio sin test se construye igual; un sitio que no se
    construye por una puerta de más sería mucho peor."""
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def hay_anuncios(cfg): return bool((cfg.get("adsense") or {}).get("cliente"))
def hay_analitica(cfg): return bool((cfg.get("analitica") or {}).get("google"))


def hay_yandex(cfg):
    """La Red de Publicidad de Yandex (РСЯ), que es la otra mitad del público.

    AdSense **no sirve anuncios a usuarios dentro de Rusia** desde marzo de
    2022, y este curso está escrito en ruso: una parte grande de los lectores
    cae justo en ese hueco. РСЯ lo cubre.

    Se enciende por BLOQUE y no por cuenta, al revés que AdSense: aquí no hay
    un identificador de editor que valga para todo, cada hueco tiene el suyo
    (`R-A-…-1`). Así que basta con que uno esté puesto para que haga falta el
    cargador y el aviso de cookies."""
    return any((cfg.get("yandex") or {}).get("bloques", {}).values())


def necesita_cookies(cfg):
    return hay_anuncios(cfg) or hay_analitica(cfg) or hay_yandex(cfg)


# ------------------------------------------------------------------- fragmentos
def _anuncio_yandex(bloque: str) -> str:
    """Un bloque de РСЯ. El identificador ya trae dentro la cuenta y el sitio.

    El contenedor y la llamada van juntos, como los pide Yandex: un `<div>` con
    un id derivado del bloque y un `render` que apunta a ese id. El cargador
    (`context.js`) va una sola vez en el `<head>`, en `cabeza_terceros`.

    `yaContextCb` es una cola: el guion se carga `async`, así que la llamada se
    encola y Yandex la ejecuta cuando el cargador llega. Por eso el orden entre
    el `<head>` y el cuerpo no importa y no hace falta `defer` ni esperar al
    `DOMContentLoaded`."""
    seguro = re.sub(r"[^A-Za-z0-9_-]", "", bloque)
    destino = f"yandex_rtb_{seguro}"
    return (f'<div class="anuncio" data-etiqueta="Ads">'
            f'<div id="{destino}"></div>'
            f"<script>window.yaContextCb.push(()=>{{"
            f'Ya.Context.AdvManager.render({{"blockId":"{seguro}","renderTo":"{destino}"}})'
            f"}})</script></div>")


def anuncio(cfg: dict, ranura: str) -> str:
    """Un bloque de publicidad en ese hueco, o nada.

    **Un hueco, una red.** Dos anuncios en el mismo contenedor no es una
    opción, así que si el hueco tiene identificador de Yandex manda Yandex, y
    si no, AdSense. No es un orden arbitrario: AdSense funciona hoy en
    **anuncios automáticos**, que se colocan solos y no usan estos tres huecos,
    mientras que un bloque de РСЯ solo existe donde se le pone. Dárselos a
    Yandex no le quita nada a AdSense.

    Sin identificador no se escribe ni el contenedor: un `<div>` vacío
    reservando alto dejaría un agujero en mitad de la lección."""
    yan = ((cfg.get("yandex") or {}).get("bloques") or {}).get(ranura)
    if yan:
        return _anuncio_yandex(str(yan))
    cliente = (cfg.get("adsense") or {}).get("cliente")
    bloque = ((cfg.get("adsense") or {}).get("bloques") or {}).get(ranura)
    if not cliente or not bloque:
        return ""
    return (f'<div class="anuncio" data-etiqueta="Ads">'
            f'<ins class="adsbygoogle" style="display:block" data-ad-client="{html.escape(cliente)}" '
            f'data-ad-slot="{html.escape(str(bloque))}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>')


def cabeza_terceros(cfg: dict) -> str:
    partes = []
    if hay_anuncios(cfg):
        c = html.escape(cfg["adsense"]["cliente"])
        partes.append(f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={c}" crossorigin="anonymous"></script>')
    if hay_yandex(cfg):
        # Una sola vez por página, y sirve para los tres huecos.
        partes.append('<script>window.yaContextCb=window.yaContextCb||[]</script>'
                      '<script src="https://yandex.ru/ads/system/context.js" async></script>')
    if hay_analitica(cfg):
        m = html.escape(cfg["analitica"]["google"])
        partes.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={m}"></script>'
                      f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
                      f'gtag("js",new Date());gtag("config","{m}");</script>')
    return "".join(partes)


def banda_cookies(cfg: dict, t: dict, raiz: str) -> str:
    if not necesita_cookies(cfg):
        return ""
    return (f'<div id="cookies"><span>{html.escape(t["cookies"])} '
            f'<a href="{raiz}/privacy.html">{html.escape(t["cookies_mas"])}</a>.</span>'
            f'<button class="boton" style="padding:.4rem 1rem;font-size:.85rem" '
            f"onclick=\"try{{localStorage.setItem('cookies','1')}}catch(e){{}};this.parentNode.remove()\">"
            f'{html.escape(t["cookies_ok"])}</button></div>'
            "<script>try{if(localStorage.getItem('cookies')){var b=document.getElementById('cookies');b&&b.remove()}}catch(e){}</script>")


def _tablas_envueltas(cuerpo: str) -> str:
    """Las tablas largas se desbordan en el móvil; cada una va en su caja con
    scroll propio en vez de empujar la página entera."""
    return re.sub(r"<table>(.*?)</table>", r'<div class="tabla-env"><table>\1</table></div>', cuerpo, flags=re.S)


def _marcar_contraste(cuerpo: str) -> str:
    """Envuelve «⚠️ Контраст с русским» en su propia caja.

    Es el apartado que distingue al curso, así que se ve distinto. Va desde su
    h3 hasta el siguiente encabezado del mismo nivel o superior."""
    patron = re.compile(r'(<h3[^>]*>⚠️[^<]*</h3>)(.*?)(?=<h[123][\s>]|$)', re.S)
    return patron.sub(lambda m: f'<section class="contraste">{m.group(1)}{m.group(2)}</section>', cuerpo)


# ------------------------------------------------------------------------ shell
def _tarjeta_social(cfg, titulo: str) -> str:
    """La imagen de la vista previa al compartir, si existe y si hay dominio.

    Sin ella el enlace llega pelado a Telegram y a WhatsApp —que es por donde
    se comparte este curso desde el 2026-10-27— y un enlace sin imagen se mira
    mucho menos.

    **Las dos condiciones son necesarias y no son lo mismo.** La imagen la
    escribe `scripts/tarjeta_social.py`, que es un comando aparte: si no se ha
    corrido, prometer un `og:image` que da 404 es peor que no declarar
    ninguno. Y `og:image` tiene que ser una URL ABSOLUTA —la plataforma la
    descarga desde su propio servidor, no desde la página—, así que sin
    dominio configurado tampoco sirve.

    Se mira en `docs/` y NO en la carpeta de destino, al revés que la baraja o
    el índice de dibujos, y es a propósito: aquello se enlaza con una ruta
    relativa, así que lo que importa es qué hay en la construcción; esto se
    declara con la URL absoluta del sitio publicado, así que lo que importa es
    qué hay versionado en `docs/`. Construir en otra carpeta no cambia lo que
    la plataforma va a descargar.

    `summary_large_image` es lo que hace que la tarjeta salga grande y no como
    una miniatura cuadrada al lado del texto."""
    dominio = (cfg.get("dominio") or "").rstrip("/")
    if not dominio or not (DOCS / TARJETA_SOCIAL).exists():
        return ""
    url = f"{dominio}/{TARJETA_SOCIAL}"
    return (f'<meta property="og:image" content="{html.escape(url)}">'
            f'<meta property="og:image:width" content="1200">'
            f'<meta property="og:image:height" content="630">'
            f'<meta property="og:image:alt" content="{html.escape(titulo)}">'
            f'<meta name="twitter:card" content="summary_large_image">'
            f'<meta name="twitter:image" content="{html.escape(url)}">')


# El icono de la pestaña, en `img/` como la tarjeta y los dibujos. Lo escribe
# `scripts/icono.py`, que es un comando aparte; aquí solo se mira si está.
ICONOS = (("icono-32.png", "32x32"), ("icono.png", "512x512"))
ICONO_IOS = "icono-180.png"


def _iconos(raiz: str) -> str:
    """Los <link> del icono, con la ruta RELATIVA a la profundidad de la página.

    Por eso llevan `{raiz}` y no una ruta escrita a mano: una lección vive en
    `semana-07/` y la portada en español en `es/`, así que `img/icono.png` a
    secas da 404 en 364 de las 391 páginas. Es el mismo fallo que esta suite ya
    cazó cuatro veces —el conmutador de idioma, las tarjetas del mapa, los
    destinos del probador y las fuentes— y la quinta tiene prueba antes de
    existir.

    Sin los archivos no se escribe nada: un icono que da 404 deja la pestaña
    igual de gris y de paso mete una petición fallida en cada página."""
    salida = []
    for nombre, medida in ICONOS:
        if (DOCS / "img" / nombre).exists():
            salida.append(f'<link rel="icon" type="image/png" sizes="{medida}" href="{raiz}/img/{nombre}">')
    if (DOCS / "img" / ICONO_IOS).exists():
        salida.append(f'<link rel="apple-touch-icon" href="{raiz}/img/{ICONO_IOS}">')
    return "".join(salida)


def canonica_de(cfg, idiomas, idioma, pagina_id: str) -> str:
    """La URL absoluta de una página, o cadena vacía sin dominio configurado.

    Vive aquí y no dentro de `pagina()` porque la necesitan además los bloques
    de compartir, que van en el CUERPO: la lección se la rearmaba a mano y con
    la portada habría tres copias de la misma cuenta. Dos copias de la misma
    pregunta es como se descubre tarde que una de las dos miente —pasó con
    `facebook.permisos` en el proyecto hermano y con `replica.CARPETA`—.

    `idioma=None` es la RAÍZ del sitio, que es donde viven las 365 lecciones:
    existen solo en ruso y por eso no cuelgan de ninguna carpeta de idioma.
    Pedirlo así y no pasar un `"ru"` a ciegas es lo que deja la cuenta escrita
    una sola vez sin dar por supuesto cuál es el idioma de la raíz."""
    dominio = cfg.get("dominio")
    if not dominio:
        return ""
    carpeta = ""
    if idioma is not None:
        carpeta = next(i for i in idiomas if i["codigo"] == idioma)["carpeta"]
    base = f"{dominio}/{carpeta}".rstrip("/")
    return f"{base}/{pagina_id}" if pagina_id else base


def pagina(cfg, t, idiomas, idioma, titulo, cuerpo, *, descripcion="", pagina_id="", raiz=".",
           jsonld="", publicadas=0, mapa_dias="{}", traducida=True, con_audio=False, test=None,
           huecos=None,
           niveles="[]",
           quiz=None,
           grabar=None,
           prueba=None) -> str:
    """El armazón de toda página: cabecera con menú y cambio de idioma, cuerpo, pie."""
    dominio = cfg["dominio"]
    actual = next(i for i in idiomas if i["codigo"] == idioma)
    base_actual = f"{dominio}/{actual['carpeta']}".rstrip("/") if dominio else ""
    canonica = canonica_de(cfg, idiomas, idioma, pagina_id)

    menu = "".join(
        f'<a href="{raiz}/{destino}"{" aria-current=\"page\"" if destino == pagina_id else ""}>{html.escape(t["menu"][clave])}</a>'
        for clave, destino in (("curso", "kurs.html"), ("sobre", "o-kurse.html"), ("contacto", "kontakt.html"))
    )
    # El cambio de idioma lleva a la MISMA página en el otro idioma, pero solo
    # cuando esa página existe de verdad en los tres. Las lecciones están solo
    # en ruso —son el curso—, los documentos del programa solo en español y el
    # test de nivel solo en ruso, así que ahí no hay gemela a la que ir.
    #
    # La PRIMERA versión apuntaba a la gemela igual y daba 404 (215 enlaces
    # rotos). La SEGUNDA mandaba a la portada de ese idioma, y eso tampoco
    # servía: el lector pulsa «ES» esperando esta página en español y se
    # encuentra en la portada, habiendo perdido la lección que estaba leyendo.
    # Lo dijo el profesor en cuanto lo usó.
    #
    # Ahora, en esas 108 páginas, los otros idiomas NO son enlaces: se enseñan
    # apagados y al pulsarlos sale un aviso visible que dice que esta página solo
    # existe en este idioma y ofrece la portada del otro como una elección. Así
    # nadie se mueve sin quererlo y nadie se queda sin saber por qué. Apagados y
    # no escondidos, porque el conmutador es la señal de que hay tres idiomas.
    #
    # Y el hreflang desaparece, no se redirige: hreflang declara que dos URL son
    # la MISMA página traducida. Apuntarlo a la portada es decirle a Google algo
    # falso, que es peor que no decirle nada.
    conmutador = []
    hreflangs = []
    for i in idiomas:
        prefijo = f"{raiz}/{i['carpeta']}".rstrip("/") if i["carpeta"] else raiz
        actual_este = i["codigo"] == idioma
        if not traducida:
            # Tercera y cuarta versión de esto. Resumen, porque cada una arregló
            # la queja de la anterior:
            #   1.ª  llevaba a la gemela  -> 404 (215 enlaces rotos)
            #   2.ª  llevaba a la portada -> «se regresa a la página del inicio»
            #   3.ª  no hacía nada        -> «no cambian los idiomas»
            # Las tres fallaban en lo mismo: la página nunca DECÍA que aquí no
            # hay versión en ese idioma. El aviso estaba en un `title`, que en
            # el móvil no existe, así que el botón parecía roto.
            #
            # Ahora se pulsan y abren un aviso visible que lo explica y ofrece
            # la portada de ese idioma COMO UNA ELECCIÓN. Nadie se mueve de
            # sitio sin quererlo, y nadie se queda sin saber por qué.
            if actual_este:
                conmutador.append(f'<span lang="{i["html"]}" aria-current="true">{i["codigo"]}</span>')
            else:
                conmutador.append(
                    f'<button type="button" class="apagado" lang="{i["html"]}" '
                    f'data-portada="{prefijo}/index.html" data-idioma="{i["nombre"]}">'
                    f'{i["codigo"]}</button>')
            continue
        # De aquí abajo `traducida` es siempre cierto: el caso contrario se fue
        # por el `continue`.
        hoja = pagina_id or "index.html"
        marca = ' aria-current="true"' if actual_este else ""
        conmutador.append(f'<a href="{prefijo}/{hoja}" hreflang="{i["html"]}" lang="{i["html"]}"{marca}>{i["codigo"]}</a>')
        if dominio:
            d = f"{dominio}/{i['carpeta']}".rstrip("/")
            hreflangs.append(f'<link rel="alternate" hreflang="{i["html"]}" href="{d}/{pagina_id or "index.html"}">')

    meta = f'<meta name="description" content="{html.escape(descripcion)}">' if descripcion else ""
    canon = f'<link rel="canonical" href="{html.escape(canonica)}">' if canonica else ""
    og = (f'<meta property="og:type" content="website"><meta property="og:locale" content="{actual["html"]}">'
          f'<meta property="og:title" content="{html.escape(titulo)}">'
          f'<meta property="og:description" content="{html.escape(descripcion)}">'
          + (f'<meta property="og:url" content="{html.escape(canonica)}">' if canonica else "")
          + _tarjeta_social(cfg, titulo))
    estructura = f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""

    return f"""<!doctype html>
<html lang="{actual['html']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title>
{meta}{canon}{"".join(hreflangs)}{og}{estructura}{_iconos(raiz)}
<style>{caras(raiz)}{CSS}</style>
{TEMA_CABEZA}
{cabeza_terceros(cfg)}
</head>
<body>
<header class="sitio"><div class="envoltorio">
<a class="marca" href="{raiz}/index.html">{html.escape(t['titulo_sitio'])}</a>
<nav class="paginas">{menu}</nav>
<div class="idiomas" title="{html.escape(t['idioma'])}">{"".join(conmutador)}</div>
<button class="tema" id="tema" type="button" title="{html.escape(t['tema'])}" aria-label="{html.escape(t['tema'])}">{LUNA}{SOL}</button>
{f'<p class="sin-idioma" id="sin-idioma" hidden>{html.escape(t["solo_este_idioma"])}. <a href="" data-ir="{html.escape(t["ir_a_portada"])}"></a></p>' if not traducida else ""}
</div></header>
<main><div class="envoltorio">
{cuerpo}
</div></main>
<footer class="sitio"><div class="envoltorio">
<p><a href="{raiz}/test.html">{html.escape(t['test']['titulo'])}</a> · <a href="{raiz}/o-kurse.html">{html.escape(t['menu']['sobre'])}</a> · <a href="{raiz}/kontakt.html">{html.escape(t['menu']['contacto'])}</a> · <a href="{raiz}/privacy.html">{html.escape(t['privacidad']['titulo'])}</a></p>
<p>{html.escape(t['pie'])}</p>
{_seguir(t, cfg, raiz)}
</div></footer>
{banda_cookies(cfg, t, raiz)}
{TEMA_SCRIPT}
{IDIOMA_SCRIPT if not traducida else ""}
<script>window.CURSO_TEXTOS={json.dumps(t['progreso'], ensure_ascii=False)};window.CURSO_RAIZ="{raiz}";window.CURSO_PUBLICADAS={publicadas};window.CURSO_DIAS={mapa_dias};window.CURSO_NIVELES={niveles};window.CURSO_SITIO={json.dumps(t["titulo_sitio"], ensure_ascii=False)};window.CURSO_DOMINIO={json.dumps((cfg.get("dominio") or "").replace("https://", "").replace("http://", ""), ensure_ascii=False)};</script>
<script src="{raiz}/progreso.js" defer></script>
{f'<script>{AUDIO_JS}</script>' if con_audio else ""}
{f'<script>window.CURSO_TEST={json.dumps(test, ensure_ascii=False)};{TEST_JS}</script>' if test else ""}
{f'<script>window.CURSO_PRUEBA={json.dumps(prueba, ensure_ascii=False)};{PRUEBA_JS}</script>' if prueba else ""}
{f'<script>window.CURSO_GRABAR={json.dumps(grabar, ensure_ascii=False)};{GRABAR_JS}</script>' if grabar else ""}
{f'<script>window.CURSO_QUIZ={json.dumps(quiz, ensure_ascii=False)};{QUIZ_JS}</script>' if quiz else ""}
{f'<script>window.CURSO_HUECOS={json.dumps({"ejercicios": huecos, "t": t["huecos"]}, ensure_ascii=False)};{HUECOS_JS}</script>' if huecos else ""}
{f'<script>{CASILLA_JS}</script>' if 'hueco-escribir' in cuerpo else ""}
</body>
</html>"""


def md(texto: str) -> str:
    return markdown.markdown(texto, extensions=EXTENSIONES + [Tachado()])


def escritas(cal: dict) -> list[plan.Dia]:
    return [d for d in plan.dias(cal) if d.ruta.exists()]


def meses_de(hechas: int, formas: list) -> tuple[int, str]:
    """Cuántos meses de estudio diario son las lecciones publicadas.

    Se calcula, no se escribe a mano: «más de tres meses» envejecería el día
    que se escriba la lección 101 y nadie volvería a mirarlo.

    El ruso pide tres formas según el número (1 месяц, 2-4 месяца, 5+ месяцев)
    y aquí hacen falta las dos últimas, porque por debajo de 60 lecciones este
    aviso no se enseña: decir «más de un mes» no tranquiliza a nadie."""
    n = max(hechas // 30, 2)
    ultimos_dos = n % 100
    pocos = 2 <= n % 10 <= 4 and not 12 <= ultimos_dos <= 14
    return n, formas[0] if pocos else formas[1]


def mapa_de_dias(cal: dict) -> str:
    """{número de lección: ruta}, para que «continuar» sepa adónde ir.

    Solo las escritas: mandar a una lección que no existe sería peor que no
    tener el botón."""
    return json.dumps({d.numero: f"semana-{d.semana:02d}/dia-{d.dia}.html" for d in escritas(cal)},
                      ensure_ascii=False, separators=(",", ":"))


def inicios_de_unidad(cal: dict, raiz: str = ".") -> dict:
    """{unidad: {n, url}} de la PRIMERA lección escrita de cada unidad.

    Es a lo que apunta el resultado del test de nivel. Se calcula al construir
    y no en el navegador: el guion no puede saber qué lecciones existen, y
    mandar a una que no está es el fallo que ya cazó dos veces la prueba de
    enlaces rotos.

    Solo las unidades con alguna lección escrita. Las demás no se rellenan a
    propósito: el test cae entonces en la última escrita de una unidad, que es
    la respuesta honrada —si ya sabe todo lo que el curso cubre, ahí empieza—.

    **Y los días SIN unidad no entran.** Las semanas 49-52 son la fase final y
    la 53 es el día de reserva: su `unidad` está vacía, así que agruparlas por
    unidad metía una clave `null` en los datos que viajan al navegador. No
    rompía nada —las preguntas del test se mapean a las unidades 1-24 y nadie
    busca `null`— pero era un dato falso publicado en todas las visitas."""
    inicios: dict[int, dict] = {}
    for d in escritas(cal):
        if d.unidad is None:
            continue
        inicios.setdefault(d.unidad, {"n": d.numero,
                                      "url": f"{raiz}/semana-{d.semana:02d}/dia-{d.dia}.html"})
    return inicios


GUIA_JS = r"""(function(){
  // La guia de la leccion: los seis pasos de los 30 minutos, con el que toca
  // marcado y un boton que lleva al siguiente.
  //
  // Por que. Una leccion es una pagina larga con seis apartados y sus franjas
  // de minutos escritas en los titulos («## 3. Новое (6–16 мин)»), y hasta hoy
  // el alumno tenia que ir encontrandolos solo entre el texto. El profesor lo
  // pidio asi: «que sea un aprendizaje intuitivo, colocar algo mas guiado».
  // Esto no anade materia: hace visible la que ya estaba.
  //
  // Los pasos salen de los PROPIOS titulos de la leccion y no de una lista en
  // el codigo. Una lista se queda vieja el dia que un tipo de dia use otros
  // apartados —los de examen, simulacro y proyecto ya lo hacen— y el sintoma
  // seria una guia que señala donde no es.
  var art=document.querySelector('article[data-leccion]');
  var caja=document.getElementById('guia');
  var T=window.CURSO_TEXTOS||{};
  if(!art||!caja)return;

  var FRANJA=/^\s*(\d+)\.\s*(.+?)\s*\((\d+)\s*[–—-]\s*(\d+)\s*мин\)\s*$/;
  var pasos=[];
  Array.prototype.forEach.call(art.querySelectorAll('h2'),function(h){
    var m=(h.textContent||'').match(FRANJA);
    if(m)pasos.push({el:h,nombre:m[2],a:+m[3],b:+m[4]});
  });
  // Menos de tres no es una leccion con sus franjas (la clave, por ejemplo, no
  // es un paso: no se hace, se consulta). Sin guia, la pagina se queda igual.
  if(pasos.length<3)return;

  // La cabecera del sitio es pegajosa a partir de 40rem, asi que la guia tiene
  // que pegarse DEBAJO de ella. Se mide, no se escribe: cambiar el menu movia
  // el numero y nadie se enteraria hasta ver la guia tapada.
  function altoCabecera(){
    var h=document.querySelector('header.sitio');
    if(!h)return 0;
    return getComputedStyle(h).position==='sticky'?Math.round(h.getBoundingClientRect().height):0;
  }
  function ajustarTope(){
    document.documentElement.style.setProperty('--alto-cabecera',altoCabecera()+'px');
  }
  ajustarTope();
  window.addEventListener('resize',ajustarTope);

  var barra=document.createElement('div');barra.className='guia-barra';
  var puntos=pasos.map(function(p,i){
    var b=document.createElement('button');
    b.type='button';b.className='guia-punto';b.textContent=String(i+1);
    b.setAttribute('data-i',String(i));
    b.title=p.nombre;b.setAttribute('aria-label',p.nombre);
    b.addEventListener('click',function(){irA(i)});
    barra.appendChild(b);return b;
  });
  var ahora=document.createElement('div');ahora.className='guia-ahora';
  var cual=document.createElement('b'), franja=document.createElement('span');
  ahora.appendChild(cual);ahora.appendChild(franja);
  var ir=document.createElement('button');
  ir.type='button';ir.className='guia-ir';
  ir.addEventListener('click',function(){
    if(actual+1<pasos.length){irA(actual+1)}
    else{
      // En el ultimo paso la guia deja de guiar la leccion y lleva al boton de
      // marcarla: es lo unico que queda por hacer, y es lo que encadena con el
      // dia siguiente.
      var m=document.getElementById('marcar-caja');
      if(m)m.scrollIntoView({behavior:'smooth',block:'center'});
    }
  });
  caja.appendChild(barra);caja.appendChild(ahora);caja.appendChild(ir);
  caja.hidden=false;

  var actual=-1, hasta=0;
  function irA(i){
    var tope=caja.getBoundingClientRect().height+altoCabecera()+10;
    var y=pasos[i].el.getBoundingClientRect().top+window.pageYOffset-tope;
    // Se pinta el paso YA y se bloquea al vigilante un momento. Sin esto, el
    // desplazamiento suave todavia no ha terminado cuando `mirar()` vuelve a
    // calcular, el titulo aun cae un pixel por debajo del corte y el paso se
    // queda en el anterior: el siguiente clic repetia el mismo apartado. Se
    // vio recorriendo la leccion en el navegador, no leyendo el codigo.
    pintar(i); hasta=Date.now()+700;
    window.scrollTo({top:Math.max(y,0),behavior:'smooth'});
  }
  function pintar(i){
    if(i===actual)return;
    actual=i;
    for(var k=0;k<puntos.length;k++){
      puntos[k].classList.toggle('aqui',k===i);
      puntos[k].classList.toggle('hecho',k<i);
    }
    var p=pasos[i];
    cual.textContent=p.nombre;
    franja.textContent=p.a+'–'+p.b+' '+(T.guia_min||'мин');
    ir.textContent=(i+1<pasos.length?(T.guia_siguiente||'Дальше'):(T.guia_final||''))+' ↓';
    caja.setAttribute('aria-label',(T.guia_paso||'{n}/{total}')
      .replace('{n}',i+1).replace('{total}',pasos.length));
  }
  function mirar(){
    if(Date.now()<hasta)return;
    var corte=altoCabecera()+caja.getBoundingClientRect().height+16;
    var i=0;
    for(var k=0;k<pasos.length;k++){
      if(pasos[k].el.getBoundingClientRect().top<=corte)i=k;
    }
    pintar(i);
  }
  var esperando=false;
  window.addEventListener('scroll',function(){
    if(esperando)return;esperando=true;
    requestAnimationFrame(function(){esperando=false;mirar()});
  },{passive:true});
  mirar();
})();"""


EFECTOS_JS = r"""(function(){
  // Las tarjetas del mapa aparecen subiendo al llegar a ellas.
  //
  // La clase que las esconde la pone ESTE guion y no el servidor, y es la
  // linea que no se puede cruzar: si el navegador no trae
  // IntersectionObserver, o el sistema pide menos movimiento, no se anade
  // nada y las tarjetas nacen visibles. Al reves —un `opacity:0` servido en
  // el HTML— deja la pagina en blanco para quien no tenga JavaScript, que es
  // justo lo que este sitio no hace en ninguna otra parte.
  //
  // Se desconecta cada tarjeta en cuanto entra: si no, el observador sigue
  // trabajando en cada scroll durante toda la visita para nada.
  var mapa=document.querySelector('.mapa');
  if(!mapa||!window.IntersectionObserver)return;
  try{
    if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  }catch(e){}
  var tarjetas=mapa.querySelectorAll('.u-tarjeta');
  if(!tarjetas.length)return;
  mapa.classList.add('anima');
  var ojo=new IntersectionObserver(function(entradas){
    entradas.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('dentro');ojo.unobserve(e.target)}
    });
  },{rootMargin:'0px 0px -40px 0px'});
  for(var i=0;i<tarjetas.length;i++)ojo.observe(tarjetas[i]);
  // Red: si algo impidiera que el observador disparara, a los dos segundos
  // se encienden igual. Una tarjeta invisible para siempre seria peor que
  // no tener efecto.
  setTimeout(function(){
    for(var j=0;j<tarjetas.length;j++)tarjetas[j].classList.add('dentro');
  },2000);
})();"""





def _bloque_de_grabar(t: dict, con_audio: bool) -> str:
    """El botón de grabarse, al cerrar la lección.

    El curso pide grabarse en 77 lecciones —«запишите себя»— y el sitio no
    ofrecía dónde. Nada sale del navegador: la grabación vive en memoria y se
    tira al salir de la página, y eso está dicho en el propio bloque y en la
    política de privacidad.

    Solo donde hay audio que comparar. Sin un ▶ en la página el ejercicio es
    grabarse contra nada, y el micrófono se pediría para eso.
    """
    if not con_audio:
        return ""
    g = t["grabar"]
    return (f'<div class="grabar-bloque" id="grabar" hidden>'
            f'<h2>{html.escape(g["titulo"])}</h2>'
            f'<p>{html.escape(g["entrada"])}</p></div>')


def _bloque_del_quiz(t: dict, preguntas: list) -> str:
    """El test de las palabras del día, al cerrar la lección.

    Nace con el botón OCULTO y lo enciende el guion, como el resto del sitio:
    sin JavaScript sería un botón muerto, y el vocabulario ya está en su tabla
    más arriba con su traducción al lado, que es la versión que vale.

    Va DESPUÉS de los ejercicios y antes de marcar la lección: primero se
    hace el día, después se comprueban las palabras, y lo último es marcarlo.
    """
    if not preguntas:
        return ""
    q = t["quiz"]
    return (f'<div class="quiz-bloque">'
            f'<h2>{html.escape(q["titulo"])}</h2>'
            f'<p>{html.escape(q["entrada"])}</p>'
            f'<div class="botones" id="quiz-arranque" hidden>'
            f'<button type="button" class="boton" id="quiz-empezar">'
            f'{html.escape(q["empezar"])}</button></div>'
            f'<div id="quiz"></div></div>')


def _calendario_y_diploma() -> str:
    """Los dos huecos que llena el navegador dentro de `#mio`.

    Nacen vacíos y ocultos, como todo lo que depende del progreso: una
    rejilla de 364 casillas en blanco y un botón de certificado que nadie ha
    ganado desaniman en la primera visita, que es la regla de `#mio`.

    En UNA función y no copiados en la portada y en el índice: dos copias de
    lo mismo es como se descubre tarde que una de las dos se quedó vieja.
    """
    return ('<div class="calendario" id="calendario" hidden></div>'
            '<div class="diploma-caja" id="diploma" hidden></div>')


def niveles_del_curso(cal: dict) -> list[dict]:
    """Los niveles del curso con la última lección de cada uno.

    `hasta` es el número de esa última lección y el certificado pide TODAS
    las de 1 a `hasta`: terminar A2 incluye haber hecho A1, así que un
    certificado de A2 con el A1 a medias no diría la verdad.

    Sale del calendario y no de dos números escritos a mano: el día que el
    profesor mueva una unidad de nivel, esto lo sigue solo.
    """
    topes: dict[str, int] = {}
    for d in plan.dias(cal):
        topes[d.nivel] = max(topes.get(d.nivel, 0), d.numero)
    return [{"nivel": n, "hasta": h} for n, h in sorted(topes.items(), key=lambda x: x[1])]


def escribir_progreso_js(destino: pathlib.Path) -> None:
    destino.joinpath("progreso.js").write_text(
        PROGRESO_JS + "\n" + GUIA_JS + "\n" + EFECTOS_JS, encoding="utf-8")


# Las doce palabras que se enseñan en la portada, elegidas A MANO y en este
# orden. De los 300 dibujos hay que escoger, y los de la portada son la cara
# del sitio: tienen que ser inequívocos (nada de «el banco», que es asiento y
# entidad), distintos entre sí de un vistazo, y de campos diferentes —comida,
# casa, animal, ropa, objeto, transporte— para que se vea de qué va el curso.
#
# Doce y no más porque la rejilla es de 3, 4 o 6 columnas según el ancho: con
# doce quedan filas enteras en los tres casos y ninguna huérfana.
PORTADA_DIBUJOS = ("la manzana", "la casa", "el perro", "el libro",
                   "el café", "el reloj", "la camisa", "el coche",
                   "las flores", "el pescado", "la guitarra", "la silla")

# Por debajo de esto la banda no sale. Media vitrina con tres huecos no se lee
# como «todavía no están todos los dibujos»: se lee como una página rota.
MUESTRA_MINIMA = 6

# Una traducción tiene que estar en ruso. Suena obvio y no lo es: la columna
# rusa del vocabulario trae a veces la variante americana («el zumo → el
# jugo», por la regla 8) o una corrección («el vaso → стакан (✗ не ваза!)»).
# Lo primero pondría español donde se promete ruso; lo segundo es una nota
# para el alumno, no una traducción.
NO_ES_TRADUCCION = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]|✗")


def lexico_del_curso(cal) -> dict:
    """Palabra española → su traducción rusa, leída de las lecciones.

    De las lecciones y no de una lista en el código, por lo mismo que el
    índice de dibujos se lee de `docs/img/`: la fuente es el curso. Si dos
    lecciones enseñan la misma entrada se queda la primera, que es la que la
    presenta como nueva."""
    palabras: dict[str, str] = {}
    for d in plan.dias(cal):
        if d.ruta.exists():
            for es, ru, _ej, _et in exportar_anki.tarjetas_de(d.ruta):
                palabras.setdefault(es, ru)
    return palabras


# Cuántos dibujos lleva el héroe. Seis y no doce: en el móvil tienen que caber
# en UNA fila dentro de los 358 px de la columna, y doce obligarían a dos filas
# —o a hacerlos tan pequeños que dejarían de leerse como dibujos—.
HEROE_DIBUJOS = 6

# Por debajo de esto no sale la tira. Cuatro dibujos sueltos en una fila
# pensada para seis se leen como una página a medio cargar, que es peor que
# no tener tira: el mismo criterio que MUESTRA_MINIMA en la vitrina.
HEROE_MINIMO = 4


def _arte_del_heroe(dibujos: dict, raiz: str) -> str:
    """Los primeros dibujos de la portada, como banda del héroe.

    Decoración y nada más: `aria-hidden`, `alt` vacío y sin enlace. Lo que se
    puede pulsar y oír es la vitrina de abajo, que además enseña la palabra y
    su traducción; esta tira solo pone color en la primera pantalla.

    **No carga assets nuevos**: son los mismos ficheros de `docs/img/` que la
    vitrina, así que el navegador los sirve de caché cuando llega abajo.

    Se cae sola, como la vitrina y la baraja: sin dibujos generados devuelve
    cadena vacía y el héroe sale como antes."""
    if not dibujos:
        return ""
    fuera = []
    for palabra in PORTADA_DIBUJOS:
        archivo = dibujos.get(generar_imagenes.limpiar(palabra))
        if not archivo:
            continue
        fuera.append(f'<img src="{raiz}/img/{html.escape(archivo)}" alt="" '
                     f'width="88" height="88" decoding="async">')
        if len(fuera) == HEROE_DIBUJOS:
            break
    if len(fuera) < HEROE_MINIMO:
        return ""
    return f'<div class="heroe-arte" aria-hidden="true">{"".join(fuera)}</div>'


def _muestra_de_dibujos(t, dibujos: dict, lexico: dict, raiz: str, audio: dict | None = None) -> str:
    """Doce palabras con su dibujo, en la portada.

    El profesor dijo que la página «se ve muy aburrida», y lo que la viste son
    los dibujos que ya están pagados y en disco: son de la paleta de la casa,
    no los tiene nadie más y no cargan ni un byte de fuera. Lo que NO se hizo
    son efectos de movimiento: esto es un sitio para leer media hora al día y
    una animación cansa a la tercera visita.

    Y no es solo decoración: el visitante aprende doce palabras antes de
    pulsar nada, que es la mejor forma de enseñar de qué va el curso.

    **Se cae sola y en silencio.** Sin dibujos generados no sale nada —igual
    que la baraja y el audio, el sitio se construye con todo y sin nada— y una
    palabra sin dibujo o sin traducción rusa en el curso se salta. Si quedan
    menos de `MUESTRA_MINIMA`, no sale la banda entera: una vitrina a medias
    parece un fallo, no una obra en marcha."""
    if not dibujos:
        return ""
    p = t["portada"]
    fichas = []
    for palabra in PORTADA_DIBUJOS:
        archivo = dibujos.get(generar_imagenes.limpiar(palabra))
        ruso = lexico.get(palabra, "")
        if not archivo or not ruso or NO_ES_TRADUCCION.search(ruso):
            continue
        # El dibujo SUENA si esa palabra está locutada. En una web de idiomas
        # es lo primero que el visitante quiere hacer —oír cómo suena— y aquí
        # no cuesta nada: los 3.543 audios ya están pagados y en disco.
        # La ficha entera es el botón, no un ▶ al lado: en el móvil un icono
        # de doce píxeles al lado de una palabra no se acierta con el dedo.
        mp3 = (audio or {}).get(palabra)
        etiqueta = f'{html.escape(t["portada"]["oir"])}: {html.escape(palabra)}'
        abre = (f'<button type="button" class="suena ficha" aria-pressed="false" '
                f'data-audio="{raiz}/audio/{html.escape(mp3)}" aria-label="{etiqueta}">'
                if mp3 else '<span class="ficha">')
        cierra = "</button>" if mp3 else "</span>"
        fichas.append(
            f'<li>{abre}<img src="{raiz}/img/{html.escape(archivo)}" alt="" '
            f'width="72" height="72" loading="lazy" decoding="async">'
            f'<b>{html.escape(palabra)}</b>'
            f'<span class="ru">{html.escape(ruso)}</span>{cierra}</li>')
    if len(fichas) < MUESTRA_MINIMA:
        return ""
    nota = html.escape(p["muestra_nota"]).format(n=len(dibujos), k=len(fichas))
    return (f'<section class="muestra"><h2>{html.escape(p["muestra"])}</h2>'
            f'<p>{nota}</p><ul class="vitrina">{"".join(fichas)}</ul></section>')


PROBADOR_JS = r"""(function(){
  var D=window.CURSO_PROBADOR; if(!D)return;
  var caja=document.getElementById('probador'); if(!caja)return;
  var i=0, fallos=[], aciertos=0, preguntas=[];

  function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML}

  // Mismo barajado que el test de nivel y por el mismo motivo: se COPIA la
  // pregunta, porque sobre el original la segunda partida encontraria las
  // opciones ya movidas y `correcta` apuntando a otra cosa.
  function barajar(q){
    var ops=q.opciones.slice(), orden=[], n;
    for(n=0;n<ops.length;n++)orden.push(n);
    for(n=orden.length-1;n>0;n--){
      var j=Math.floor(Math.random()*(n+1)), t=orden[n]; orden[n]=orden[j]; orden[j]=t;
    }
    return {pregunta:q.pregunta, error:q.error,
            opciones:orden.map(function(k){return ops[k]}),
            correcta:orden.indexOf(q.correcta)};
  }

  function pregunta(){
    var q=preguntas[i];
    caja.innerHTML='<div class="test-caja"><div class="test-cuenta">'
      +(i+1)+' '+esc(D.t.de)+' '+preguntas.length+' · '+esc(D.t.instruccion)+'</div>'
      +'<p class="test-pregunta">'+esc(q.pregunta)+'</p>'
      +'<div class="test-ops">'+q.opciones.map(function(o,n){
          return '<button type="button" data-n="'+n+'">'+esc(o)+'</button>'}).join('')+'</div></div>';
    caja.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){responder(parseInt(b.dataset.n,10),b)});
    });
  }

  // Se contesta y se ENSEÑA el error ahi mismo, sin esperar al final: el
  // discurso sobre por que el ruso te traiciona es lo unico que esta pagina
  // tiene que demostrar, y al final de tres preguntas ya nadie lo lee.
  function responder(n,boton){
    var q=preguntas[i], bien=(n===q.correcta);
    if(bien){aciertos++}else{fallos.push(q)}
    caja.querySelectorAll('.test-ops button').forEach(function(b,k){
      b.disabled=true;
      if(k===q.correcta)b.classList.add('bien');
      else if(b===boton)b.classList.add('mal');
    });
    var p=document.createElement('div');
    p.className='test-fallo';
    p.innerHTML='<b>'+esc(bien?D.t.bien:D.t.mal)+'</b><span>'+esc(q.error)+'</span>';
    caja.querySelector('.test-caja').appendChild(p);
    var sig=document.createElement('button');
    sig.type='button'; sig.className='boton';
    sig.textContent=(i+1<preguntas.length)?D.t.siguiente:D.t.ver;
    sig.style.marginTop='1rem';
    sig.addEventListener('click',function(){i++;if(i<preguntas.length){pregunta()}else{resultado()}});
    caja.querySelector('.test-caja').appendChild(sig);
  }

  function resultado(){
    caja.innerHTML='<div class="test-caja"><div class="test-cuenta">'+esc(D.t.resultado)+'</div>'
      +'<p class="test-pregunta">'+aciertos+' / '+preguntas.length+' '+esc(D.t.aciertos)+'</p>'
      +'<p>'+esc(D.t.final)+'</p>'
      +'<div class="botones"><a class="boton" href="'+D.leccion+'">'+esc(D.t.empezar)+'</a>'
      +'<a class="boton secundario" href="'+D.test+'">'+esc(D.t.test)+'</a></div></div>';
  }

  // Nace oculto y lo enciende el navegador, como el resto del sitio: sin
  // JavaScript seria un boton que no hace nada, y el parrafo de contraste que
  // hay encima ya explica lo mismo en texto.
  var arranque=document.getElementById('probador-arranque');
  var boton=document.getElementById('probador-empezar');
  if(arranque&&boton){
    arranque.hidden=false;
    boton.addEventListener('click',function(){
      arranque.hidden=true;
      preguntas=(D.grupos||[]).map(function(g){return barajar(g[Math.floor(Math.random()*g.length)])});
      pregunta();
    });
  }
})();"""

# Cuántas preguntas se ofrecen en la portada. Tres y no catorce: esto no
# coloca a nadie, solo enseña de qué va el curso antes de pedir un clic. El
# test de verdad está a un botón de distancia al terminar.
PROBADOR_PREGUNTAS = 3


def _probador(t, preguntas: dict, raiz: str, enlace: str) -> str:
    """Tres preguntas jugables en la portada, con las del test de nivel.

    El profesor lo dijo dos veces: la página «se ve muy aburrida» y «le falta
    interactividad al comienzo». Y tenía razón en el sitio exacto: el curso es
    interactivo por dentro —audio, huecos que se rellenan, pruebas de unidad—
    pero la portada solo se lee.

    **No se escribió ni una pregunta nueva.** Son las de
    `programa/test-nivel.yaml`, que ya existen, ya están agrupadas por unidad y
    ya traen la explicación del error en ruso. Aquí se cogen los tres primeros
    grupos, que son las unidades 1 a 3: lo bastante fáciles para que un
    principiante acierte y siga, y lo bastante rápidas para que quien ya sabe
    español llegue al final y pulse «hacer el test completo».

    Va DENTRO del apartado «en qué se diferencia este curso», justo donde el
    texto promete que la lección nombra el error antes de que lo cometas. Era
    el mejor párrafo de la página y estaba en forma de texto: ahora se toca."""
    grupos = grupos_por_unidad(preguntas.get("preguntas") or [])[:PROBADOR_PREGUNTAS]
    if len(grupos) < PROBADOR_PREGUNTAS:
        return ""
    p, k = t["portada"], t["test"]
    datos = {
        "grupos": grupos,
        "leccion": enlace,
        "test": f"{raiz}/test.html",
        "t": {"de": k["de"], "instruccion": k["instruccion"], "resultado": k["resultado"],
              "aciertos": k["aciertos"], "empezar": p["boton"], "test": p["probador_test"],
              "bien": p["probador_bien"], "mal": p["probador_mal"], "final": p["probador_final"],
              "siguiente": p["probador_siguiente"], "ver": p["probador_ver"]},
    }
    return (f'<h3>{html.escape(p["probador_titulo"])}</h3>'
            f'<p>{html.escape(p["probador_entrada"])}</p>'
            f'<div class="botones" id="probador-arranque" hidden>'
            f'<button type="button" class="boton" id="probador-empezar">'
            f'{html.escape(k["empezar"])}</button></div>'
            f'<div id="probador"></div>'
            f'<script>window.CURSO_PROBADOR={json.dumps(datos, ensure_ascii=False)};'
            f'{PROBADOR_JS}</script>')


# ----------------------------------------------------------------------- páginas
def construir_portada(cfg, t, idiomas, idioma, destino, cal, raiz,
                      dibujos=None, lexico=None, audio=None, preguntas=None) -> None:
    hechas = escritas(cal)
    total = len(plan.dias(cal))
    primera = hechas[0] if hechas else None
    enlace = f"{raiz}/semana-{primera.semana:02d}/dia-{primera.dia}.html" if primera else f"{raiz}/kurs.html"
    p = t["portada"]
    pr = t["progreso"]
    pct = round(len(hechas) * 100 / total, 1)

    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Course",
        "name": t["titulo_sitio"], "description": p["entrada"],
        "inLanguage": "ru", "teaches": "Spanish", "educationalLevel": "A1-A2",
        "provider": {"@type": "Person", "name": cfg.get("autor", {}).get("nombre", "")},
        "isAccessibleForFree": True,
    }, ensure_ascii=False)

    # «100 de 365» se lee como «el curso está a medias» y es lo tercero que ve
    # quien llega. El mismo dato dicho en meses contesta la pregunta que de
    # verdad se hace: ¿me voy a quedar sin curso? Por debajo de 60 lecciones no
    # se enseña, porque entonces la respuesta honrada sería que sí.
    nota_meses = ""
    if len(hechas) >= 60 and p.get("progreso_nota"):
        n, forma = meses_de(len(hechas), p["meses"])
        nota_meses = (f'<p class="progreso-nota">'
                      f'{html.escape(p["progreso_nota"].format(n=n, meses=forma))}</p>')

    filas = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>" for a, b in p["dia_filas"])
    tarjetas = "".join(f'<div class="tarjeta"><h3>{html.escape(a)}</h3><p>{b}</p></div>' for a, b in p["ano_tarjetas"])

    cuerpo = f"""
<div class="heroe">
{_arte_del_heroe(dibujos or {}, raiz)}
<div class="heroe-texto">
<h1>{html.escape(p['titulo'])}<span class="segunda">{html.escape(p['titulo2'])}</span></h1>
<p class="lema">{html.escape(p['lema'])}</p>
<p>{html.escape(p['entrada'])}</p>
<p class="marco">{html.escape(p['marco'])}</p>
<div class="botones">
<a class="boton" id="continuar" href="{enlace}" hidden></a>
<a class="boton" id="empezar" href="{enlace}">{html.escape(p['boton'])}</a>
<a class="boton secundario" href="{raiz}/kurs.html">{html.escape(p['boton2'])}</a>
</div>
<p class="puerta">{html.escape(p['ya_sabe'])} <a href="{raiz}/test.html">{html.escape(p.get('ya_sabe_enlace') or t['test']['titulo'])}\u00a0→</a></p>
<div class="progreso">
<div class="cifras"><span class="n">{len(hechas)}</span><span>/ {total} {html.escape(p['progreso'])}</span></div>
<div class="barra"><i style="width:{max(pct, 1)}%"></i></div>
{nota_meses}
<p class="pide-nombre" id="nombre-portada" hidden></p>
<div id="mio" hidden>
<div class="cifras"><span class="n">0</span><span class="texto"></span></div>
<div class="barra"><i style="width:1%"></i></div>
{_calendario_y_diploma()}
<p class="progreso-nota">{html.escape(pr['aviso'])} <button type="button" id="borrar-progreso" hidden>{html.escape(pr['borrar'])}</button></p>
</div>
</div>
</div>
</div>
{_muestra_de_dibujos(t, dibujos or {}, lexico or {}, raiz, audio or {})}
{anuncio(cfg, "cabecera")}

<h2>{html.escape(p['dif_titulo'])}</h2>
<p>{p['dif_texto']}</p>
<section class="contraste">
<p><strong>{html.escape(p['dif_error'])}</strong> <span class="mal">✗ <em>Tengo hermano.</em></span><br>
<strong>{html.escape(p['dif_bien'])}</strong> <span class="bien">✅ <em>Tengo <strong>un</strong> hermano.</em></span></p>
<p>{html.escape(p['dif_nota'])}</p>
</section>
<p>{p['dif_ayuda']}</p>
{_probador(t, preguntas or {}, raiz, enlace)}

<h2>{html.escape(p['dia_titulo'])}</h2>
<div class="tabla-env"><table>
<tr><th>{html.escape(p['dia_min'])}</th><th>{html.escape(p['dia_que'])}</th></tr>
{filas}
</table></div>
<p>{html.escape(p['dia_nota'])}</p>

{anuncio(cfg, "dentro")}

<h2>{html.escape(p['ano_titulo'])}</h2>
<div class="rejilla">{tarjetas}</div>

<h2>{html.escape(p['final_titulo'])}</h2>
<p>{html.escape(p['final_texto'])}</p>
<div class="botones"><a class="boton" href="{enlace}">{html.escape(p['final_boton'])}</a></div>
{_compartir(t, cfg, canonica_de(cfg, idiomas, idioma, "index.html"), t['compartir']['titulo_curso'])}
{anuncio(cfg, "pie")}
"""
    destino.joinpath("index.html").write_text(
        pagina(cfg, t, idiomas, idioma, f"{p['titulo']} {p['titulo2']} — {p['lema']}", cuerpo,
               descripcion=p["entrada"], pagina_id="index.html", raiz=raiz, jsonld=jsonld,
               publicadas=len(hechas), mapa_dias=mapa_de_dias(cal),
               niveles=json.dumps(niveles_del_curso(cal), ensure_ascii=False),
               con_audio='class="suena ficha"' in cuerpo),
        encoding="utf-8")


# El dibujo de cada una de las 24 tarjetas, elegido a mano y mirando los 300.
#
# A mano y no por una regla, que es lo mismo que decidió `PORTADA_DIBUJOS`: se
# probaron dos automatismos —la primera entrada del vocabulario de la unidad, y
# la palabra con dibujo que más sale en su texto— y los dos aciertan unas seis
# de cada diez. La frecuencia ponía «el móvil» en la unidad de salud y «el
# pelo» en la de la familia. En una tarjeta de unidad el dibujo se lee como
# «de esto va», así que uno equivocado es una pequeña mentira, y eso cuesta
# más que el trabajo de elegir veinticuatro.
#
# Si una palabra deja de tener dibujo, esa unidad no se queda sin él: cae al
# vocabulario de la propia unidad, que es lo que hace `dibujo_por_unidad`.
DIBUJO_DE_UNIDAD = {
    1: "un apretón de manos",   # saludos
    2: "el ingeniero",          # cosas, personas y profesiones
    3: "la familia",
    4: "la casa",
    5: "el reloj",              # el día a día
    6: "la comida",
    7: "el carrito",            # de compras
    8: "la guitarra",           # tiempo libre
    9: "el autobús",            # viajes y transporte
    10: "el médico",            # salud y cuerpo
    11: "el cuestionario",      # repaso y evaluación de A1
    12: "el árbol genealógico", # biografías
    13: "el barrio",            # antes y ahora
    14: "la conversación",      # anécdotas
    15: "la entrevista",        # estudios y trabajo
    16: "el ayuntamiento",      # ciudad y servicios
    17: "el sol",               # el futuro: el pronóstico
    18: "el correo electrónico",# comunicarse
    19: "la ciudad",            # comparar y elegir
    20: "la farmacia",          # salud (ampliación)
    21: "la cocina",            # casa y convivencia
    22: "la fiesta",
    23: "la carta",             # leer y escribir
    24: "la pizarra",           # repaso integral de A2
}


def dibujo_por_unidad(cal, dibujos: dict) -> dict[int, str]:
    """Una imagen por unidad, sacada del vocabulario de esa MISMA unidad.

    Elegida y no escrita a mano, por lo mismo que la vitrina de la portada
    saca sus traducciones de las lecciones: una lista en el código se queda
    vieja el día que alguien reescriba un día, y el síntoma sería una tarjeta
    enseñando algo que esa unidad ya no da.

    **Ninguna se repite.** Un dibujo que ya salió en otra tarjeta se salta y
    se busca el siguiente: veinticuatro puertas con la misma manzana no son
    veinticuatro puertas. Solo si la unidad no tuviera ninguno propio se
    acepta un repetido, que es mejor que dejar el hueco.

    Se calcula UNA vez para los tres idiomas: el mapa es el mismo en ru, es e
    en, y recorrer las 365 lecciones por idioma sería tres veces el mismo
    trabajo. Es la misma razón por la que `lexico_del_curso` vive fuera del
    bucle."""
    if not dibujos:
        return {}
    candidatos: dict[int, list[str]] = {}
    for unidad, palabra in DIBUJO_DE_UNIDAD.items():
        archivo = dibujos.get(generar_imagenes.limpiar(palabra))
        if archivo:
            candidatos[unidad] = [archivo]
    for d in plan.dias(cal):
        if d.unidad is None or not d.ruta.exists():
            continue
        for es, _ru, _ej, _et in exportar_anki.tarjetas_de(d.ruta):
            archivo = dibujos.get(generar_imagenes.limpiar(es))
            if archivo and archivo not in candidatos.setdefault(d.unidad, []):
                candidatos[d.unidad].append(archivo)
    salida: dict[int, str] = {}
    usados: set[str] = set()
    for unidad in sorted(candidatos):
        libres = [a for a in candidatos[unidad] if a not in usados]
        elegido = (libres or candidatos[unidad])[0]
        salida[unidad] = elegido
        usados.add(elegido)
    return salida


def _dibujo_de_tarjeta(dibujos_unidad: dict | None, unidad: int, raiz: str) -> str:
    """El `<img>` de la tarjeta, o nada.

    `alt` vacío a propósito: el título de la unidad está al lado y un lector
    de pantalla diría lo mismo dos veces. Es la misma decisión que en las
    tablas de vocabulario.

    Sin dibujos generados no sale ninguno y el mapa queda como estaba: se cae
    de pie, igual que la vitrina, la tira del héroe y la baraja."""
    archivo = (dibujos_unidad or {}).get(unidad)
    if not archivo:
        return ""
    return (f'<img class="u-dibujo" src="{raiz}/img/{html.escape(archivo)}" alt="" '
            f'width="40" height="40" loading="lazy" decoding="async">')


def _mapa_de_unidades(cal: dict, dias: list, c: dict, idioma: str, raiz: str,
                     dibujos_unidad: dict | None = None) -> str:
    """Las 24 unidades como tarjetas, antes de la lista día a día.

    La idea viene de la referencia que mandó el profesor, que entra a cada
    curso por una tarjeta ilustrada. Lo que se toma es ESO —una puerta por
    sección, en vez de una lista larga— y no su aspecto: la paleta sigue
    siendo la de la casa, porque el azul y naranja de aquel sitio son los de
    cualquier portal de idiomas y esta crema no se parece a nada.

    Cada tarjeta lleva además el título del episodio de esa unidad: es donde
    la historia de Ana e Iván se hace visible sin abrir ninguna lección."""
    tarjetas = []
    for u in cal["unidades"]:
        suyos = [d for d in dias if d.unidad == u["numero"]]
        # Cuántas lecciones TIENE la unidad sale del calendario y no de
        # cuántas están escritas: la tarjeta dice de qué tamaño es la unidad,
        # y eso es verdad aunque algún día falte un archivo. Si no hay
        # ninguna escrita, la tarjeta sale apagada y ancla a su sección.
        primera = next((d for d in suyos if d.ruta.exists()), None)
        # Con `raiz`: las lecciones viven solo en la carpeta de ruso, asi que
        # desde /es/kurs.html y /en/kurs.html un enlace relativo sin prefijo
        # apunta a /es/semana-01/..., que no existe. Lo caza la prueba de
        # enlaces rotos, que es la misma que encontro los 404 del conmutador.
        destino_u = (f"{raiz}/semana-{primera.semana:02d}/dia-{primera.dia}.html" if primera
                     else f"#u{u['numero']}")
        titulo = u["titulo_ru"] if idioma == "ru" else u["titulo_es"]
        ep = (u.get("episodio") or {}).get("titulo", "")
        tarjetas.append(
            f'<a class="u-tarjeta{"" if primera else " vacia"}" href="{destino_u}"'
            f' data-desde="{suyos[0].numero}" data-hasta="{suyos[-1].numero}">'
            f'<span class="alto"><span class="num">{u["numero"]}</span>'
            + _dibujo_de_tarjeta(dibujos_unidad, u["numero"], raiz)
            + f'<span class="nivel">{html.escape(u["nivel"])}</span></span>'
            f'<span class="tit">{html.escape(titulo)}</span>'
            + (f'<span class="serie">{html.escape(c["episodio"])}: {html.escape(ep)}</span>' if ep else "")
            # El pie dice «14 lecciones» mientras el lector no haya marcado
            # nada, y el guion lo cambia por lo SUYO en cuanto hay progreso.
            #
            # Hasta el 2026-10-29 decía «14/14 listas», que contaba las
            # lecciones ESCRITAS: desde que el curso está entero eso son las
            # catorce en las veinticuatro, o sea un contador que no dice nada
            # y que encima parece de progreso. El profesor leyó las 24
            # tarjetas como 24 lecciones y preguntó dónde estaban las demás.
            #
            # La barra nace oculta por lo mismo: llena miente —no has hecho
            # ninguna— y vacía en las veinticuatro desanima en la primera
            # visita, que es la regla que ya tiene escrita `#mio`.
            + f'<span class="pie">'
              f'<span class="hechas" data-palabra="{html.escape(c["listos"])}">'
              f'{len(suyos)} {html.escape(c["lecciones"])}</span>'
              f'<span class="mini" hidden><i style="width:0%"></i></span></span></a>')
    return (f'<h2>{html.escape(c["mapa"])}</h2>'
            f'<p>{html.escape(c["mapa_nota"])}</p>'
            f'<div class="mapa">{"".join(tarjetas)}</div>')


def construir_iconos(destino: pathlib.Path) -> int:
    """Lleva el icono a la carpeta donde se esté construyendo.

    Los `<link rel="icon">` son enlaces RELATIVOS, así que lo que tiene que
    existir es el fichero de la construcción y no el de `docs/`. Es la misma
    distinción que ya separa a la baraja de la tarjeta social: aquella se
    enlaza en relativo y mira el destino; esta se declara con la URL absoluta
    del sitio publicado y mira `docs/`. Mirando el sitio que no es, una
    construcción en otra carpeta —la que hace media suite— sale con tres
    enlaces a ninguna parte, y lo caza el revisor de enlaces rotos.

    Los escribe `scripts/icono.py`, que es un comando aparte; aquí solo se
    copian, como los TSV del vocabulario. Cuando se construye sobre `docs/`
    no hay nada que hacer: el origen y el destino son el mismo fichero."""
    origen = DOCS / "img"
    if destino.resolve() == DOCS.resolve():
        return 0
    nombres = [n for n, _ in ICONOS] + [ICONO_IOS]
    carpeta = destino / "img"
    copiados = 0
    for nombre in nombres:
        if (origen / nombre).exists():
            carpeta.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen / nombre, carpeta / nombre)
            copiados += 1
    return copiados


def construir_vocabulario(destino: pathlib.Path) -> int:
    """Copia los TSV del vocabulario a la web.

    Viven en `vocabulario/`, que es la fuente que una prueba mantiene al día.
    El `.apkg` NO se copia aquí: lo escribe `exportar_apkg.py` directamente en
    `docs/`, como el audio y los dibujos, porque generarlo es una decisión que
    cuesta medio minuto y construir el sitio tiene que ser barato."""
    origen = RAIZ / "vocabulario"
    if not origen.is_dir():
        return 0
    carpeta = destino / VOCABULARIO_WEB
    carpeta.mkdir(parents=True, exist_ok=True)
    tsv = sorted(origen.glob("*.tsv"))
    for f in tsv:
        shutil.copy2(f, carpeta / f.name)
    return len(tsv)


def _bloque_de_la_baraja(t, destino: pathlib.Path, raiz: str) -> str:
    """La descarga de las tarjetas, si la baraja existe.

    Sale de lo que HAY en disco y no de una promesa en el código: sin
    `baraja.json` el bloque no aparece y la página queda como estaba. Es la
    misma regla que el audio y los dibujos —el sitio se construye igual con
    todo y sin nada— y aquí importa el doble, porque un botón de descarga que
    lleva a un 404 es peor que no ofrecer nada.

    Los números salen del manifiesto y no de recontar el vocabulario: el que
    sabe cuántas tarjetas tiene la baraja es quien la armó. Así además esto no
    abre un archivo de 22 MB en cada construcción.

    Se ofrecen los DOS formatos a propósito. El `.apkg` lleva los dibujos y la
    voz dentro y se abre de un clic, pero necesita Anki, que en iPhone es de
    pago. El TSV no lleva medios y lo abre cualquier cosa —Excel, Google
    Sheets, Quizlet—, así que nadie se queda sin tarjetas por el móvil que
    tenga."""
    b = t["baraja"]
    try:
        m = json.loads((destino / VOCABULARIO_WEB / MANIFIESTO_BARAJA)
                       .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    if not (destino / VOCABULARIO_WEB / m["archivo"]).exists():
        return ""

    texto = html.escape(b["texto"]).format(
        n=m["palabras"], v=m["con_voz"], d=m["con_dibujo"])
    enlaces = [
        f'<div><a class="boton" href="{raiz}/{VOCABULARIO_WEB}/{html.escape(m["archivo"])}" '
        f'download>{html.escape(b["anki"])} · {m["bytes"] / 1e6:.0f} MB</a>'
        f'<p class="nota">{html.escape(b["anki_nota"])}</p></div>']
    if (destino / VOCABULARIO_WEB / "todo.tsv").exists():
        enlaces.append(
            f'<div><a class="boton secundario" href="{raiz}/{VOCABULARIO_WEB}/todo.tsv" '
            f'download>{html.escape(b["tsv"])}</a>'
            f'<p class="nota">{html.escape(b["tsv_nota"])}</p></div>')

    return (f'<section class="baraja"><h2>{html.escape(b["titulo"])}</h2>'
            f'<p>{texto}</p><div class="bajar">{"".join(enlaces)}</div></section>')


# Los nombres que se enseñan, en el orden en que salen. El valor vacío en
# `web/sitio.yaml` deja el enlace fuera: un botón a una cuenta que no existe es
# peor que no tener botón.
REDES = (("telegram", "Telegram"), ("instagram", "Instagram"),
         ("youtube", "YouTube"), ("facebook", "Facebook"))


def _compartir(t, cfg, canonica: str, de_que: str = "") -> str:
    """Compartir la lección —o el curso, desde la portada—.

    `de_que` es el rótulo. Hace falta porque el de la lección dice «esta
    lección» y en la portada eso sería falso: lo que se manda desde ahí es el
    curso. Un rótulo equivocado no rompe nada, y por eso se escribe.

    **Enlaces normales y NUNCA los widgets oficiales.** El botón «Compartir»
    de Facebook carga el SDK de Meta, que rastrea al lector; la política de
    privacidad de este sitio dice que sin AdSense no se carga nada de terceros
    y un widget la volvería mentira. `t.me/share/url?…` hace lo mismo y no
    carga nada.

    Telegram y WhatsApp y no más: son las dos por las que un rusohablante
    fuera de Rusia manda algo a un amigo. Una fila de ocho iconos no se usa
    más, se mira menos.

    Sin `canonica` —o sea, sin dominio configurado— no sale nada: un enlace
    para compartir que apunta a `file:///` no le sirve a nadie."""
    if not canonica:
        return ""
    c = t["compartir"]
    u = urllib.parse.quote(canonica, safe="")
    titulo = urllib.parse.quote(t["titulo_sitio"], safe="")
    enlaces = [
        f'<a class="red" href="https://t.me/share/url?url={u}&text={titulo}" '
        f'target="_blank" rel="noopener">{html.escape(c["telegram"])}</a>',
        f'<a class="red" href="https://wa.me/?text={titulo}%20{u}" '
        f'target="_blank" rel="noopener">{html.escape(c["whatsapp"])}</a>',
        f'<button type="button" class="red" id="copiar-enlace" '
        f'data-url="{html.escape(canonica)}" data-ok="{html.escape(c["copiado"])}">'
        f'{html.escape(c["copiar"])}</button>',
    ]
    return (f'<div class="compartir"><span class="de-que">{html.escape(de_que or c["titulo"])}</span>'
            f'{"".join(enlaces)}</div>')


def _seguir(t, cfg, raiz: str) -> str:
    """Los perfiles del curso, en el pie. Solo los que estén rellenos."""
    redes = cfg.get("redes") or {}
    enlaces = [f'<a href="{html.escape(redes[clave])}" target="_blank" rel="noopener">{nombre}</a>'
               for clave, nombre in REDES if (redes.get(clave) or "").strip()]
    if not enlaces:
        return ""
    return (f'<p class="seguir">{html.escape(t["compartir"]["seguir"])}: '
            + " · ".join(enlaces) + "</p>")


def _envolver_huecos(html_: str, ejercicios, t) -> tuple[str, list | None]:
    """Convierte los ______ de un ejercicio en casillas que se rellenan.

    Se hace sobre el HTML YA convertido y no sobre el Markdown, igual que la
    prueba de unidad: envolver Markdown en un `<div>` haría que
    Python-Markdown lo pasara tal cual. Los `______` sobreviven a la
    conversión —seis guiones bajos no son énfasis—, así que aquí solo hay que
    sustituirlos.

    **Sin JavaScript la página no cambia**: los huecos siguen siendo rayas y
    la clave sigue abajo, para leer o imprimir. Es el guion el que las vuelve
    casillas cuando de verdad puede ofrecer algo mejor."""
    if not ejercicios:
        return html_, None

    datos = []
    for i, e in enumerate(ejercicios):
        # El ejercicio empieza en su <h3> y acaba en el siguiente título.
        cabeza = re.search(rf"<h3[^>]*>\s*{re.escape(e.titulo)}\s*</h3>", html_)
        if not cabeza:
            continue
        resto = html_[cabeza.end():]
        corte = re.search(r"<h[23][\s>]", resto)
        cuerpo = resto[: corte.start()] if corte else resto

        n_huecos = len(re.findall(r"_{3,}", cuerpo))
        if n_huecos != len(e.respuestas):
            continue   # el HTML no dice lo mismo que el Markdown: no se toca

        cuenta = [0]

        def casilla(_m):
            k = cuenta[0]
            cuenta[0] += 1
            return (f'<span class="hueco" data-ej="{i}" data-n="{k}" '
                    f'tabindex="0" role="button"></span>')

        nuevo_cuerpo = re.sub(r"_{3,}", casilla, cuerpo)
        # El banco sale dos veces: como fichas pulsables y como la cita
        # original del Markdown. Se marca la cita para que el GUION la
        # esconda; quitarla aquí dejaría sin banco a quien no tenga
        # JavaScript, que es justo para quien la cita sigue siendo útil.
        nuevo_cuerpo = nuevo_cuerpo.replace(
            "<blockquote>", '<blockquote class="banco-escrito">', 1)
        fichas = "".join(f'<button type="button" class="ficha" data-ej="{i}">'
                         f'{html.escape(w)}</button>' for w in e.banco)
        barra = (f'<div class="fichas" data-ej="{i}">{fichas}</div>'
                 f'<div class="huecos-pie">'
                 f'<button type="button" class="boton secundario comprobar" data-ej="{i}">'
                 f'{html.escape(t["huecos"]["comprobar"])}</button>'
                 f'<span class="marcador" data-ej="{i}"></span></div>')

        html_ = (html_[: cabeza.end()] + barra + nuevo_cuerpo
                 + (resto[corte.start():] if corte else ""))
        datos.append({"respuestas": e.respuestas})

    return html_, (datos or None)


def _rayas_a_salvo(cuerpo: str) -> str:
    r"""Escapa los `______` para que Markdown no los lea como cursiva.

    Seis guiones bajos sueltos pasan intactos, y por eso esto no se vio en dos
    años: lo que no pasa es un `______` pegado a un signo. En la lección 14-4,
    `¿Tiene ______?` y `¿______?` se emparejaron entre sí y
    Python-Markdown escribió `<strong><strong><strong>` abriendo en una línea
    y cerrando tres renglones más abajo: **dos huecos desaparecidos y tres
    réplicas del diálogo en negrita**, publicados así desde que se escribió la
    lección.

    El escape conserva la longitud del hueco y no toca nada más. Ninguna
    lección mete un `______` dentro de un bloque de código, que es el único
    sitio donde `\_` se vería tal cual."""
    return re.sub(r"_{3,}", lambda m: "\\_" * len(m.group(0)), cuerpo)


# Un hueco que se escribe. Se deja `type="text"` y nada más: un `<input>`
# funciona SIN JavaScript, así que este es el único trozo interactivo del
# sitio que nace encendido. El guion solo le ajusta el ancho mientras se
# teclea, que es cosmético.
CASILLA_JS = r"""(function(){
  var cajas=document.querySelectorAll('.hueco-escribir');
  if(!cajas.length)return;
  function ancho(c){ c.style.width=Math.max(5.5,(c.value.length+1)*0.62)+'rem' }
  cajas.forEach(function(c){ c.addEventListener('input',function(){ancho(c)}) });
})();"""


def _casillas_para_escribir(html_: str) -> str:
    """Las rayas que quedan se vuelven casillas donde se escribe.

    Lo trajo el profesor mirando la lección 1-3 en el móvil: «por ejemplo
    estos espacios vacios, no hay nada para completar». Tenía razón y el
    fallo era de los que no se ven leyendo el código: en papel una raya es
    donde escribes, en una pantalla es una raya y nada más.

    `_envolver_huecos` ya había convertido en fichas pulsables los ejercicios
    que traen banco de palabras Y una clave que se casa con los huecos sin
    ninguna duda: **23 lecciones y 189 huecos**. Los otros **1.398** —el 88%—
    se quedaban inertes, y son la mayoría del curso porque la mayoría de los
    ejercicios no son de elegir una ficha sino de escribir la forma correcta.

    **No se corrigen, y es deliberado.** Para las fichas el banco es la red:
    la respuesta sale de un conjunto cerrado y corto, así que una clave
    desalineada se cae sola. Aquí no hay red —la clave de la 1-5 responde
    «usted: ¿Cómo se llama?», con el rótulo dentro, y quien escribiera
    «¿Cómo se llama?» tendría razón y se le diría que no—. La clave está a un
    botón desde el 2026-10-27, al final de los ejercicios. Decirle a alguien
    que falló cuando acertó es exactamente lo que este proyecto no hace.

    **La clave queda fuera** de la conversión: ahí una raya es parte de una
    respuesta, no un sitio donde escribir."""
    cabecera = next((m for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", html_, re.S)
                     if re.sub("<[^>]+>", "", m.group(1)).strip() == "Ответы"), None)
    fin = cabecera.start() if cabecera else len(html_)
    cuenta = [0]

    def casilla(m):
        cuenta[0] += 1
        return ('<input type="text" class="hueco-escribir" autocomplete="off" '
                # El corrector del navegador está en el idioma del lector, que
                # es ruso: sin esto subraya en rojo cada palabra española.
                # `size` para que el ancho sea razonable aunque el CSS no
                # llegue (correo, modo lectura, una hoja impresa).
                'autocapitalize="off" spellcheck="false" size="8" '
                f'aria-label="{cuenta[0]}">')

    return re.sub(r"_{3,}", casilla, html_[:fin]) + html_[fin:]


def _firma(autor: dict) -> str:
    """El autor del curso: nombre y descripción, o solo la descripción.

    El nombre puede ir vacío a propósito —`web/sitio.yaml`— y entonces no se
    escribe ni el `<strong>` ni el punto que lo separaba: un «. Преподаватель
    с магистратурой…» de entrada delata que algo se borró a medias."""
    nombre = html.escape(autor.get("nombre", "") or "").strip()
    descripcion = html.escape(autor.get("descripcion", "") or "").strip()
    if not nombre:
        return descripcion
    return f"<strong>{nombre}</strong>. {descripcion}".strip()


def construir_indice_curso(cfg, t, idiomas, idioma, destino, cal, raiz,
                           sitio=None, dibujos_unidad=None) -> None:
    """`destino` es la carpeta del idioma y `sitio` la raíz del sitio.

    No son lo mismo y por eso se pasan las dos: el índice en español se
    escribe en `docs/es/`, pero la baraja vive en `docs/vocabulario/` una sola
    vez para los tres idiomas. Mirándola en `destino` no se encontraría nunca
    y el bloque se caería en dos de las tres páginas."""
    c, pr = t["curso"], t["progreso"]
    partes = [f'<h1>{html.escape(c["titulo"])}<span class="segunda">{html.escape(c["subtitulo"])}</span></h1>',
              f'<p>{html.escape(c["entrada"])}</p>',
              f'<p class="marco">{html.escape(t["portada"]["marco"])}</p>',
              # Oculto hasta que el navegador diga que hay algo hecho: en blanco
              # no dice nada y un «0 / 100» de bienvenida desanima.
              f'<div class="progreso" id="mio" hidden>'
              f'<div class="cifras"><span class="n">0</span><span class="texto"></span></div>'
              f'<div class="barra"><i style="width:1%"></i></div>'
              + _calendario_y_diploma()
              + f'<p class="progreso-nota">{html.escape(pr["aviso"])} '
              f'<strong>{html.escape(pr["antes"])}</strong> '
              f'<button type="button" id="borrar-progreso" hidden>{html.escape(pr["borrar"])}</button></p></div>'
              # El respaldo va FUERA del recuadro de progreso, y eso no es
              # colocación: ese recuadro se oculta cuando no hay nada hecho, y
              # quien más necesita «Restaurar» es justo el que no tiene nada
              # —acaba de limpiar el navegador o de estrenar móvil—. Dentro,
              # el botón era invisible exactamente cuando hacía falta. Se vio
              # probándolo en el navegador, no leyendo el código.
              #
              # «Guardar» sí nace oculto y lo enciende el navegador cuando hay
              # progreso: sin nada hecho no hay nada que copiar.
              f'<div class="respaldo">'
              f'<button type="button" class="boton secundario" id="copiar-progreso" hidden>'
              f'{html.escape(pr["copiar"])}</button>'
              f'<button type="button" class="enlace" id="restaurar-progreso">'
              f'{html.escape(pr["restaurar"])}</button>'
              f'<input type="text" id="codigo-mio" readonly hidden>'
              f'<p class="aviso-chico" id="codigo-aviso" hidden></p>'
              f'<div id="restaurar-caja" hidden>'
              f'<input type="text" id="restaurar-codigo" placeholder="{html.escape(pr["pegar"])}" '
              f'autocomplete="off" spellcheck="false">'
              f'<button type="button" class="boton" id="restaurar-aplicar">'
              f'{html.escape(pr["aplicar"])}</button>'
              f'<p class="aviso-chico" id="restaurar-aviso" hidden></p></div></div>',
              f'<p class="puerta">{html.escape(t["portada"]["ya_sabe"])} '
              f'<a href="{raiz}/test.html">'
              f'{html.escape(t["portada"].get("ya_sabe_enlace") or t["test"]["titulo"])}\u00a0→</a></p>',
              anuncio(cfg, "cabecera")]
    dias = plan.dias(cal)
    partes.append(_mapa_de_unidades(cal, dias, c, idioma, raiz, dibujos_unidad))
    por_semana: dict[int, list[plan.Dia]] = {}
    for d in dias:
        por_semana.setdefault(d.semana, []).append(d)
    unidad_vista = None
    for semana, lista in por_semana.items():
        u = plan.unidad_de(cal, semana)
        clave = u["numero"] if u else ("final" if semana <= 52 else "extra")
        if clave != unidad_vista:
            if u:
                titulo_u = u["titulo_ru"] if idioma == "ru" else u["titulo_es"]
                hechas_u = sum(1 for d in dias if d.unidad == u["numero"] and d.ruta.exists())
                partes.append(
                    f'<div class="unidad-cab" id="u{u["numero"]}"><h2 style="border:0;margin:0;padding:0">{c["tema"]} {u["numero"]}. {html.escape(titulo_u)}</h2>'
                    f'<span class="tipo">{html.escape(u["nivel"])} · {hechas_u}/14</span></div>')
                objetivos = "".join(f"<li>{html.escape(o)}</li>" for o in u["objetivos"])
                partes.append(f'<details><summary>{html.escape(c["objetivos"])} · {html.escape(c["semanas"])} {u["semanas"][0]}–{u["semanas"][1]}</summary><ul>{objetivos}</ul></details>')
            else:
                ff = cal["fase_final"]
                partes.append(f'<div class="unidad-cab"><h2 style="border:0;margin:0;padding:0">{html.escape(ff["titulo_ru"] if idioma == "ru" else ff["titulo_es"])}</h2></div>')
            unidad_vista = clave
        partes.append(f'<h3>{html.escape(c["semana"])} {semana}</h3><ul class="dias">')
        for d in lista:
            tema = d.tema_ru if idioma == "ru" else d.tema_es
            etiqueta = f'<span class="tipo">{plan.TIPO_RU[d.tipo] if idioma == "ru" else d.tipo}</span>'
            num = f'<span class="num">{d.numero}</span>'
            if d.ruta.exists():
                partes.append(f'<li data-leccion="{d.numero}">{num}<span><a href="{raiz}/semana-{d.semana:02d}/dia-{d.dia}.html">{html.escape(tema)}</a> {etiqueta}</span></li>')
            else:
                partes.append(f'<li>{num}<span class="falta">{html.escape(tema)} {etiqueta}</span></li>')
        partes.append("</ul>")
    # La baraja va AL FINAL y no debajo del mapa, donde estuvo hasta el
    # 2026-10-29. Lo pidió el profesor usando el sitio y tiene razón: esta
    # página es un camino —el mapa de las 24 unidades y después los 365 días—
    # y la baraja es un recurso de al lado, así que en medio cortaba el camino
    # justo antes de la lista, que es el contenido. Al final queda como lo que
    # es: lo que te llevas cuando ya miraste el curso.
    partes.append(_bloque_de_la_baraja(t, sitio or destino, raiz))
    partes.append(anuncio(cfg, "pie"))
    destino.joinpath("kurs.html").write_text(
        # El nombre del sitio en el <title>, como en «О курсе», el test y el
        # contacto. Antes decía «Все уроки — 365 дней, 52 недели, 24 темы» y
        # **no contenía la palabra «испанский» en ninguna parte**: es la
        # segunda página del sitio y un buscador no podía saber qué idioma
        # enseña. El «365 дней…» no se pierde: pasa a la descripción.
        pagina(cfg, t, idiomas, idioma, f'{c["titulo"]} — {t["titulo_sitio"]}', "\n".join(partes),
               descripcion=c["entrada"], pagina_id="kurs.html", raiz=raiz,
               publicadas=len(escritas(cal)), mapa_dias=mapa_de_dias(cal),
               niveles=json.dumps(niveles_del_curso(cal), ensure_ascii=False)),
        encoding="utf-8")


def grupos_por_unidad(lista: list) -> list[list[dict]]:
    """Las preguntas del test agrupadas por unidad, en orden ascendente.

    De cada grupo el navegador escoge una al azar, así que el banco puede
    crecer sin tocar ni el generador ni el guion: basta con añadir otra
    pregunta con su `unidad` en `programa/test-nivel.yaml`.

    **El orden de los GRUPOS no se baraja nunca**, y esa es la diferencia que
    importa. La recomendación sale de la unidad de la PRIMERA pregunta fallada,
    o sea de donde se acaba lo que el alumno ya sabe; desordenadas, fallar la
    última colocaría antes que fallar la primera y nada avisaría. Por eso aquí
    se ordena por unidad en vez de confiar en el orden del fichero.

    Al navegador va `error_ru` y no `error_es`: lo lee un principiante ruso, y
    explicarle su propio error en el idioma que viene a aprender no le enseña
    nada. El español se queda en el YAML, que es donde el profesor revisa."""
    grupos: dict[int, list[dict]] = {}
    for q in lista:
        grupos.setdefault(q["unidad"], []).append(
            {"pregunta": q["pregunta"], "opciones": q["opciones"],
             "correcta": q["correcta"], "unidad": q["unidad"],
             "error": q["error_ru"]})
    return [grupos[u] for u in sorted(grupos)]


def construir_test(cfg, t, idiomas, destino, cal, preguntas) -> None:
    """La segunda puerta del sitio: por qué lección empezar si ya sabe algo.

    Hasta ahora la web tenía una sola entrada, la lección 1. Quien llega
    sabiendo algo de español lee «empieza por el alfabeto», decide que esto no
    es para él y se va. El test lo deja en la semana que le toca.

    La idea de tener una segunda puerta viene de la referencia que mandó el
    profesor; las preguntas no: cada distractor es un error predecible del
    rusohablante, sacado de `programa/contrastiva-ru-es.md`. Por eso el
    resultado puede decir POR QUÉ se falló, y por eso el test enseña aunque se
    suspenda.

    La respuesta correcta viaja al navegador, y no hay forma de evitarlo en un
    sitio estático. No importa: esto coloca a quien quiere estudiar, no
    certifica nada. Quien mire el código fuente para hacer trampas se está
    engañando sobre por dónde empezar un curso gratis.

    **Hay UNA página y está en ruso**, igual que las lecciones y por la misma
    razón: las catorce preguntas son frases rusas que hay que decir en español,
    así que un lector que no lee ruso no puede contestarlas. Traducir la
    interfaz alrededor dejaría un test que no se puede hacer, que es peor que
    no ofrecerlo. Lo que sí se traduce es el ENLACE —en el pie y en la puerta de
    la portada—, igual que la portada en español manda a una lección en ruso.
    Por eso la página va con `traducida=False`: el conmutador de idioma lleva a
    la portada de ese idioma y no declara un `hreflang` que sería falso."""
    k = t["test"]
    raiz = "."
    hechas = escritas(cal)
    primera = hechas[0] if hechas else None
    enlace = f"{raiz}/semana-{primera.semana:02d}/dia-{primera.dia}.html" if primera else f"{raiz}/kurs.html"

    aviso = (f'<p class="aviso">{html.escape(k["borrador"])}</p>'
             if preguntas and not preguntas.get("revisado") else "")
    lista = preguntas.get("preguntas") or []

    cuerpo = f"""
<h1>{html.escape(k['titulo'])}<span class="segunda">{html.escape(k['subtitulo'])}</span></h1>
<p>{html.escape(k['entrada'])}</p>
{aviso}
<div class="botones" id="test-arranque" hidden><button type="button" class="boton" id="test-empezar">{html.escape(k['empezar'])}</button></div>
<div id="test"></div>
<noscript><p class="aviso">{html.escape(k['sin_js'])}</p>
<div class="botones"><a class="boton" href="{enlace}">{html.escape(t['portada']['boton'])}</a></div></noscript>
"""
    datos = None
    if lista:
        # La última lección **de una unidad**, y no la última escrita a secas.
        # Con el curso entero eso último era el día 365, que es el de reserva:
        # a quien acierta las catorce preguntas se le mandaba a una página que
        # dice que hoy no hay nada que hacer. El destino honrado es el domingo
        # de la unidad 24, que trata precisamente de qué hay después de A2.
        de_unidad = [d for d in hechas if d.unidad is not None]
        ultima = (de_unidad or hechas)[-1]
        datos = {
            # Al navegador va `error_ru` y no `error_es`: lo lee un principiante
            # ruso, y explicarle su propio error en el idioma que viene a
            # aprender no le enseña nada. El español se queda en el YAML, que
            # es donde el profesor revisa.
            # Agrupadas por unidad y en el orden en que aparecen: el
            # navegador escoge UNA de cada grupo, así que repetir el test no da
            # el mismo test. Lo que no se toca es el orden de los grupos; ver
            # `grupos_por_unidad`.
            "grupos": grupos_por_unidad(lista),
            "inicios": inicios_de_unidad(cal, raiz),
            "ultima": {"n": ultima.numero,
                       "url": f"{raiz}/semana-{ultima.semana:02d}/dia-{ultima.dia}.html"},
            "segundos": preguntas.get("segundos_por_pregunta") or 0,
            "t": k,
        }
    destino.joinpath("test.html").write_text(
        pagina(cfg, t, idiomas, "ru", f"{k['titulo']} — {t['titulo_sitio']}", cuerpo,
               descripcion=k["entrada"][:160], pagina_id="test.html", raiz=raiz,
               traducida=False, test=datos),
        encoding="utf-8")


def construir_estaticas(cfg, t, idiomas, idioma, destino, cal, raiz) -> None:
    autor = cfg.get("autor", {})
    hechas = len(escritas(cal))
    s = t["sobre"]
    cuerpo = f"""
<h1>{html.escape(s['titulo'])}</h1>
{anuncio(cfg, "cabecera")}
<h2>{html.escape(s['quien'])}</h2>
<p>{_firma(autor)}</p>
<h2>{html.escape(s['porque'])}</h2>
<p>{s['porque_texto']}</p>
<p>{html.escape(s['porque_texto2'])}</p>
<h2>{html.escape(s['como'])}</h2>
<p>{html.escape(s['como_texto'])}</p>
<h2>{html.escape(s['cuanto'])}</h2>
<p>{html.escape(s['cuanto_texto'])}</p>
<p><strong>{html.escape(s['abierto'])}: {hechas} / {len(plan.dias(cal))}.</strong></p>
<h2>{html.escape(s['falta'])}</h2>
<p>{html.escape(s['falta_texto'])}</p>
<ul class="lista-larga">{"".join(f"<li>{x}</li>" for x in s['falta_lista'])}</ul>
<p>{html.escape(s['falta_no'])}</p>
<h2>{html.escape(s['dele'])}</h2>
<p>{html.escape(s['dele_texto'])}</p>
<ul class="lista-larga">{"".join(f"<li>{x}</li>" for x in s['dele_lista'])}</ul>
<p>{html.escape(s['dele_examen'])}</p>
<p class="aviso-chico">{html.escape(s['dele_aviso'])}</p>
{anuncio(cfg, "pie")}
"""
    destino.joinpath("o-kurse.html").write_text(
        pagina(cfg, t, idiomas, idioma, f"{s['titulo']} — {t['titulo_sitio']}", cuerpo,
               descripcion=s["porque_texto2"][:160], pagina_id="o-kurse.html", raiz=raiz), encoding="utf-8")

    k = t["contacto"]
    if autor.get("email"):
        correo = html.escape(autor["email"])
        contacto = f'<p>{html.escape(k["texto"])}</p><p><a class="boton" href="mailto:{correo}">{correo}</a></p>'
    else:
        contacto = f'<p class="aviso">{html.escape(k["sin_correo"])}</p>'
    cuerpo = f"""
<h1>{html.escape(k['titulo'])}</h1>
{contacto}
<p>{html.escape(k['error'])}</p>
<h2>{html.escape(k['autor'])}</h2>
<p>{_firma(autor)}</p>
"""
    destino.joinpath("kontakt.html").write_text(
        pagina(cfg, t, idiomas, idioma, f"{k['titulo']} — {t['titulo_sitio']}", cuerpo,
               descripcion=k["texto"], pagina_id="kontakt.html", raiz=raiz), encoding="utf-8")

    pr = t["privacidad"]
    bloques = [f"<h1>{html.escape(pr['titulo'])}</h1>",
               f"<p>{html.escape(pr['actualizado'])}: {dt.date.today().isoformat()}.</p>",
               f"<h2>{html.escape(pr['propio'])}</h2><p>{html.escape(pr['propio_texto'])}</p>"]
    if hay_yandex(cfg):
        # Si carga Yandex hay que decirlo, y con su propio enlace de exclusión:
        # la política no puede hablar solo de Google cuando el lector ruso ve
        # anuncios de otra red.
        bloques += [f"<h2>{html.escape(pr['anuncios'])}</h2><p>{html.escape(pr['anuncios_yandex'])}</p>",
                    f'<p><a href="https://yandex.ru/support/partner2/web/behavioral-advertising.html" '
                    f'rel="nofollow noopener">yandex.ru</a></p>']
    if hay_anuncios(cfg):
        bloques += [f"<h2>{html.escape(pr['anuncios'])}</h2><p>{html.escape(pr['anuncios_texto'])}</p>",
                    f'<p>{html.escape(pr["anuncios_optar"])} '
                    f'<a href="https://www.google.com/settings/ads" rel="nofollow noopener">google.com/settings/ads</a> · '
                    f'<a href="https://www.aboutads.info/choices/" rel="nofollow noopener">aboutads.info</a> · '
                    f'<a href="https://policies.google.com/technologies/partner-sites" rel="nofollow noopener">policies.google.com</a></p>']
    if hay_analitica(cfg):
        bloques += [f"<h2>{html.escape(pr['estadistica'])}</h2><p>{html.escape(pr['estadistica_texto'])}</p>"]
    if not necesita_cookies(cfg):
        bloques += [f"<h2>{html.escape(pr['sin_cookies'])}</h2><p>{html.escape(pr['sin_cookies_texto'])}</p>"]
    bloques += [f"<h2>{html.escape(pr['derechos'])}</h2><p>{html.escape(pr['derechos_texto'])}</p>",
                f"<h2>{html.escape(pr['ninos'])}</h2><p>{html.escape(pr['ninos_texto'])}</p>",
                f"<h2>{html.escape(pr['micro'])}</h2><p>{html.escape(pr['micro_texto'])}</p>"]
    destino.joinpath("privacy.html").write_text(
        pagina(cfg, t, idiomas, idioma, f"{pr['titulo']} — {t['titulo_sitio']}", "\n".join(bloques),
               descripcion=pr["propio_texto"], pagina_id="privacy.html", raiz=raiz), encoding="utf-8")


def _anuncios_en_la_leccion(html_cuerpo: str, cfg: dict) -> str:
    """Los dos bloques de dentro de la lección, en un corte de sección.

    El de cabecera NO va antes del título. Ahí ocupaba la primera pantalla
    entera del móvil y empujaba la lección fuera de la vista, que es
    exactamente lo que las políticas de AdSense llaman un diseño engañoso: el
    lector abre un enlace a una lección y lo primero y único que ve es un
    anuncio. Va después de los títulos y de los objetivos del día, en el primer
    <h2>, donde además ya se vio de qué va la página.

    Si el corte no aparece, el bloque no se dibuja: es mejor perder un hueco
    que meterlo en medio de una frase."""
    for ranura, patron in (("dentro", r"<h2[^>]*>4\.\s*(?:Практика|Задание)"),
                           ("cabecera", r"<h2[^>]*>")):
        trozo = anuncio(cfg, ranura)
        if not trozo:
            continue
        marca = re.search(patron, html_cuerpo)
        if marca:
            html_cuerpo = html_cuerpo[:marca.start()] + trozo + html_cuerpo[marca.start():]
    return html_cuerpo


def _pregunta_al_navegador(q, todos) -> dict:
    """Una pregunta, con el enlace a la lección donde se enseña si la clave lo dice."""
    salida = {"bloque": q.bloque, "enunciado": q.enunciado,
              "opciones": q.opciones, "correcta": q.correcta}
    if q.semana and q.dia:
        leccion = next((x for x in todos
                        if x.semana == q.semana and x.dia == q.dia and x.ruta.exists()), None)
        if leccion:
            salida["url"] = f"../semana-{leccion.semana:02d}/dia-{leccion.dia}.html"
            salida["n"] = leccion.numero
    return salida


# El guion de la clave: diez líneas, y solo en las páginas que la tienen, así
# que va en línea como el de los idiomas. Lo importante no es plegar la clave
# sino que el ENLACE la abra: un ancla que apunta a algo escondido no hace
# nada, y el lector se queda mirando la misma pantalla creyendo que está roto.
# Cómo se reconoce un apartado con ejercicios. Son las mismas marcas que mira
# `validar.problemas` para exigir que haya clave, y por lo mismo: es lo que de
# verdad distingue un ejercicio de una explicación, en las tres formas que
# tienen los días del curso.
# «Задания» en plural es el apartado de los simulacros, y no lo cubre
# «Задание» en singular: la última letra es otra, así que no es subcadena. Sin
# él, los días 146 y 149 se quedaban sin enlace a su clave.
MARCAS_DE_EJERCICIO = ("Упражнение", "Мини-тест", "Правда или неправда",
                       "Задание", "Задания")

# Qué tipos de día tienen ejercicios cuya clave se pliega y se enlaza. Los
# otros tres NO, y cada uno por su motivo:
#
#   `prueba`   tiene su propio envoltorio, con el test contestable y la clave
#              al terminar; dos mecanismos sobre la misma clave se pisarían.
#   `examen`   lleva la clave DENTRO del apartado «Ключи и подсчёт», porque
#              hace falta ahí mismo para decidir si se pasa de nivel. Lo que
#              queda en `## Ответы` es el comentario de los fallos típicos.
#   `proyecto` no tiene ejercicios: se prepara y se entrega. Su `## Ответы` es
#              un modelo para comparar, no una respuesta.
#
# Sin esta lista, el enlace no se colocaba —no hay dónde— y la clave se
# plegaba igual: un botón que abre algo a lo que nada apunta.
CON_CLAVE_DE_EJERCICIOS = ("leccion", "repaso", "cultura", "simulacro")

CLAVE_SCRIPT = """<script>(function(){
  var caja=document.getElementById('clave'), zona=document.getElementById('clave-boton');
  if(!caja||!zona)return;
  var b=zona.querySelector('button');
  function pon(abierta){
    caja.hidden=!abierta;
    b.textContent=abierta?b.dataset.ocultar:b.dataset.ver;
    b.setAttribute('aria-expanded',abierta?'true':'false');
  }
  pon(false); zona.hidden=false;
  b.addEventListener('click',function(){pon(caja.hidden)});
  document.querySelectorAll('a[href="#clave"]').forEach(function(a){
    a.addEventListener('click',function(){pon(true)});
  });
  if(location.hash==='#clave')pon(true);
})();</script>"""


def _envolver_clave(html_: str, t: dict) -> str:
    """La clave (`## Ответы`) detrás de un botón, y un enlace a ella desde los
    ejercicios.

    Antes estaba abierta al final de la página, DEBAJO de la tabla de
    vocabulario, y eso fallaba por los dos lados a la vez: quien la buscaba no
    la encontraba —es lo último de todo, después del diccionario del día— y
    quien no la buscaba se la encontraba de paso, con las respuestas a la vista
    antes de hacer el ejercicio. Lo preguntó el profesor: «¿y las respuestas a
    los ejercicios? ¿dónde ver si es correcto?».

    Ahora el enlace sale **donde se acaban los ejercicios**, que es donde se
    busca, y la clave está plegada hasta que se pulsa. Es lo mismo que ya hacía
    el día de prueba desde el 2026-10-27: el discurso sobre los errores solo
    enseña DESPUÉS de contestar; antes es la respuesta.

    **Sin JavaScript la página se queda exactamente como estaba**: la clave
    abierta y el enlace llevando a ella. Por eso aquí nace visible y es el
    navegador el que la pliega, al revés que el resto del sitio: la versión sin
    guion tiene que ser la que sirve, y una clave escondida que no se puede
    abrir sería una lección sin respuestas.

    Los días de tipo `prueba` no pasan por aquí: tienen su propio envoltorio,
    con el test contestable y la clave al terminar."""
    cabeceras = [(m.start(), m.end(), re.sub("<[^>]+>", "", m.group(1)).strip())
                 for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", html_, re.S)]
    inicio_clave = next((ini for ini, _f, texto in cabeceras if texto == "Ответы"), None)
    if inicio_clave is None:
        return html_
    L = t["leccion"]
    # El enlace va al final de los ejercicios, o sea justo antes del apartado
    # que sigue al ÚLTIMO que los contiene. Se busca por el contenido y no por
    # el nombre del apartado porque son tres formas distintas: «4. Практика» en
    # una lección, «3. Мини-тест» en un repaso y «4. Задание» en un día de
    # cultura. Si no se encuentra ninguno, no se pone enlace: mejor nada que un
    # enlace en mitad de la teoría.
    cortes = []
    for j, (_ini, fin, texto) in enumerate(cabeceras):
        if fin >= inicio_clave:
            break
        siguiente = cabeceras[j + 1][0] if j + 1 < len(cabeceras) else inicio_clave
        # El TÍTULO del apartado cuenta igual que su cuerpo: un repaso titula
        # «3. Мини-тест» y dentro solo dice «выберите правильный ответ», así
        # que mirando solo el cuerpo el enlace caía antes del mini-test, y en
        # la semana 1 no caía en ninguna parte.
        if any(m in texto or m in html_[fin:siguiente] for m in MARCAS_DE_EJERCICIO):
            cortes.append(siguiente)
    # El ÚLTIMO corte que esté de verdad antes de la clave, no el último a
    # secas: cuando el apartado de corrección menciona un ejercicio —«Задание
    # 2, номер 11» en el análisis de un simulacro— el corte caía justo en la
    # clave y entonces **el enlace no se ponía**, sin que nada fallara. En esos
    # días el sitio correcto es donde acaban los ejercicios de verdad, que es
    # el corte anterior.
    corte = next((c for c in reversed(cortes) if c < inicio_clave), None)
    enlace = (f'<p class="a-la-clave"><a href="#clave">'
              f'{html.escape(L["clave_ir"])} ↓</a></p>')
    boton = (f'<div class="botones" id="clave-boton" hidden>'
             f'<button type="button" class="boton secundario" '
             f'data-ver="{html.escape(L["clave_ver"])}" '
             f'data-ocultar="{html.escape(L["clave_ocultar"])}">'
             f'{html.escape(L["clave_ver"])}</button></div>')
    # De atrás adelante, porque cada inserción mueve lo que viene después.
    salida = html_[:inicio_clave] + boton + '<div id="clave">' + html_[inicio_clave:] + "</div>"
    if corte is not None and corte < inicio_clave:
        salida = salida[:corte] + enlace + salida[corte:]
    return salida + CLAVE_SCRIPT


def _envolver_prueba(html_: str, t: dict, es_minitest: bool = False) -> str:
    """Marca en el HTML qué parte es el test en papel y cuál la clave.

    Se trabaja sobre el HTML ya convertido y no sobre el Markdown a propósito:
    envolver Markdown en un `<div>` haría que Python-Markdown lo pasara tal cual
    sin convertirlo, y las quince preguntas saldrían en crudo.

    Los tres trozos se marcan de atrás adelante porque cada inserción mueve
    todas las posiciones siguientes.

    En un día de **repaso** el test es el `## 3. Мини-тест` y NO se envuelve la
    clave: la sección `## Ответы` de un repaso lleva también la del dictado y la
    del ejercicio de calentamiento, que el alumno necesita antes de llegar al
    mini-test, y además ya está plegada por `_envolver_clave`. Envolverla aquí
    escondería tres claves para esconder una."""
    cabeceras = [(m.start(), m.end(), re.sub("<[^>]+>", "", m.group(1)).strip())
                 for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", html_, re.S)]
    inicio_test = fin_test = inicio_clave = None
    for j, (ini, fin, texto) in enumerate(cabeceras):
        suya = "Мини-тест" in texto if es_minitest else texto.startswith("2.")
        if suya and inicio_test is None:
            inicio_test, fin_test = fin, (cabeceras[j + 1][0] if j + 1 < len(cabeceras) else len(html_))
        if texto == "Ответы":
            inicio_clave = ini
    if inicio_test is None:
        return html_

    boton = (f'<div class="botones" id="prueba-arranque" hidden>'
             f'<button type="button" class="boton" id="prueba-empezar">'
             f'{html.escape(t["test"]["empezar"])}</button></div><div id="prueba"></div>')
    if es_minitest:
        return "".join([html_[:inicio_test], boton, '<div id="prueba-papel">',
                        html_[inicio_test:fin_test], "</div>", html_[fin_test:]])
    if inicio_clave is None:
        return html_
    trozos = [html_[:inicio_test], boton, '<div id="prueba-papel">', html_[inicio_test:fin_test],
              "</div>", html_[fin_test:inicio_clave], '<div id="prueba-clave">',
              html_[inicio_clave:], "</div>"]
    return "".join(trozos)


def construir_leccion(d, cfg, t, idiomas, destino, cal, todos, audio=None,
                      dibujos=None) -> None:
    """Las lecciones solo existen en ruso: son el curso."""
    datos, cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))
    i = todos.index(d)
    anterior = next((x for x in reversed(todos[:i]) if x.ruta.exists()), None)
    siguiente = next((x for x in todos[i + 1:] if x.ruta.exists()), None)
    L = t["leccion"]

    html_cuerpo = _botones_de_audio(md(_rayas_a_salvo(cuerpo)), audio or {}, "..")
    html_cuerpo = _dibujos_en_el_vocabulario(html_cuerpo, dibujos or {}, "..")

    # Los ejercicios de rellenar huecos, si su clave se puede casar con los
    # huecos sin ninguna duda. `huecos.leer` descarta los que no, y entonces
    # la página se queda exactamente como está hoy.
    html_cuerpo, datos_huecos = _envolver_huecos(html_cuerpo, huecos.leer(cuerpo), t)
    # Y las rayas que quedan —las de los ejercicios sin banco de palabras, que
    # son el 88%— se vuelven casillas donde se escribe. Va DESPUÉS de las
    # fichas: aquellas ya se han llevado sus `______` y no hay que tocarlas.
    html_cuerpo = _casillas_para_escribir(html_cuerpo)
    html_cuerpo = _anuncios_en_la_leccion(_marcar_contraste(_tablas_envueltas(html_cuerpo)), cfg)

    # Los días de tipo `prueba` traen quince preguntas con su clave, ya escritas
    # y revisadas por el profesor. Si se pueden leer con seguridad, se ofrecen
    # para contestar; si no, la página se queda exactamente como está.
    if d.tipo in CON_CLAVE_DE_EJERCICIOS:
        html_cuerpo = _envolver_clave(html_cuerpo, t)

    # Un día de `prueba` trae el test de unidad; uno de `repaso`, el Мини-тест
    # del sábado, que tiene la misma forma. Los dos se ofrecen para contestar si
    # se pueden leer con seguridad; si no, la página se queda como está.
    datos_prueba = None
    if d.tipo in ("prueba", "repaso"):
        es_mini = d.tipo == "repaso"
        preguntas = (pruebas.leer_minitest(cuerpo, semana=d.semana) if es_mini
                     else pruebas.leer(cuerpo))
        if preguntas:
            datos_prueba = {
                "preguntas": [_pregunta_al_navegador(q, todos) for q in preguntas],
                "t": t["test"],
            }
            html_cuerpo = _envolver_prueba(html_cuerpo, t, es_minitest=es_mini)

    titulo = f"{L['urok']} {d.numero}: {d.tema_ru} — {t['titulo_sitio']}"
    # `foco` es la nota del autor y está EN ESPAÑOL —«dormir 8 horas, hacer
    # ejercicio…»—, así que las 365 páginas salían en Google con medio
    # fragmento en un idioma que el lector ruso no está buscando. La
    # descripción se arma ahora de la plantilla traducida: dice qué lección
    # es, de cuántas, su tema en ruso y lo que un buscador necesita saber
    # —gratis, sin registro, 30 minutos—.
    # El tema se mete con su punto, salvo que ya acabe en signo: hay temas
    # que son una pregunta («Ты ведёшь здоровый образ жизни?») y quedaban
    # con «?.» en el fragmento de Google.
    tema = d.tema_ru if d.tema_ru.rstrip()[-1:] in ".!?…" else d.tema_ru + "."
    descripcion = L["meta_leccion"].format(n=d.numero, tema=tema)
    aviso = "" if datos.get("revisado") else f'<p class="aviso">{html.escape(L["borrador"])}</p>'

    pasos = []
    pasos.append(f'<a href="../semana-{anterior.semana:02d}/dia-{anterior.dia}.html">← {L["anterior"]} {anterior.numero}</a>' if anterior else "<span></span>")
    pasos.append(f'<a href="../kurs.html">{html.escape(L["todos"])}</a>')
    # El id lo usa progreso.js para destacarlo en cuanto marcas esta lección:
    # el paso siguiente es lo único que se quiere hacer después de marcar.
    pasos.append(f'<a id="enlace-siguiente" href="../semana-{siguiente.semana:02d}/dia-{siguiente.dia}.html">{L["siguiente"]} {siguiente.numero} →</a>' if siguiente else "<span></span>")

    # La guia nace vacia y oculta, y la llena el navegador con los apartados de
    # esta leccion. Sin JavaScript la pagina se queda exactamente como estaba:
    # los seis titulos con sus franjas de minutos, que es la version que vale.
    guia = '<div id="guia" class="guia" hidden></div>'
    cab = (f'<div class="leccion-cab"><span class="n">{L["urok"]} {d.numero}</span>'
           f'<span>{L["de"]} {len(todos)}</span><span class="tipo">{plan.TIPO_RU[d.tipo]}</span>'
           f'<span>{L["semana"]} {d.semana} · {L["nivel"]} {html.escape(d.nivel)}</span></div>')
    # El botón de marcar lo pone el navegador y no el generador: sin JavaScript
    # no haría nada, y un botón muerto es peor que ninguno.
    # Compartir va al PIE y no arriba: se comparte lo que ya has leído y te ha
    # gustado, no lo que acabas de abrir.
    # `None` es la raíz del sitio: las lecciones existen solo en ruso.
    canonica = canonica_de(cfg, idiomas, None, f"semana-{d.semana:02d}/dia-{d.dia}.html")
    # Las cinco palabras del día, si se pueden preguntar sin dudas. Un día
    # que ya trae su propio test contestable no lleva éste, y una tabla de
    # la que no salen cuatro preguntas limpias deja la página como está.
    preguntas_quiz = quiz_lexico.preguntas_de(d.ruta, d.numero)
    # Y la palabra que se falló se puede OÍR ahí mismo: las 2.201 del quiz ya
    # están locutadas desde el 2026-10-28, así que no cuesta un céntimo. El
    # reproductor escucha en `document`, de modo que un botón insertado por el
    # guion después de cargar la página funciona sin tocar nada más.
    for q in preguntas_quiz:
        archivo = (audio or {}).get(q["opciones"][q["correcta"]])
        if archivo:
            q["mp3"] = f"../audio/{archivo}"
    datos_quiz = ({"preguntas": preguntas_quiz, "t": t["quiz"]}
                  if preguntas_quiz else None)
    # Grabarse solo donde hay un ▶ con el que compararse.
    hay_audio = 'class="suena"' in html_cuerpo
    datos_grabar = {"t": t["grabar"]} if hay_audio else None
    cuerpo_final = (f'<article data-leccion="{d.numero}">' + cab + guia + aviso
                    + html_cuerpo + anuncio(cfg, "pie")
                    + _bloque_de_grabar(t, hay_audio)
                    + _bloque_del_quiz(t, preguntas_quiz) + '<div id="marcar-caja"></div>'
                    + _compartir(t, cfg, canonica)
                    + f'<nav class="pasos">{"".join(pasos)}</nav></article>')

    salida = destino / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        pagina(cfg, t, idiomas, "ru", titulo, cuerpo_final, descripcion=descripcion,
               pagina_id=f"semana-{d.semana:02d}/dia-{d.dia}.html", raiz="..",
               publicadas=len(escritas(cal)), mapa_dias=mapa_de_dias(cal), traducida=False,
               con_audio=('class="suena"' in cuerpo_final
                          or any(q.get("mp3") for q in preguntas_quiz)),
               prueba=datos_prueba,
               huecos=datos_huecos, quiz=datos_quiz, grabar=datos_grabar),
        encoding="utf-8")


def indice_de_audio(destino: pathlib.Path) -> dict:
    """Texto → archivo. Vacío si todavía no se ha locutado nada.

    Se lee de `docs/audio/`, que es donde lo deja `scripts/generar_audio.py`, y
    no de una lista en el código: así el sitio se construye igual con audio y
    sin él, y encender el audio no es tocar el generador."""
    ruta = destino / "audio" / INDICE_AUDIO
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _botones_de_audio(html_: str, indice: dict, raiz: str) -> str:
    """Un ▶ delante de cada frase española que esté locutada.

    En cualquier celda, no solo la primera: en las tablas de fonética la
    palabra de ejemplo («casa») está en la cuarta columna y es justo la que
    hay que oír. La columna rusa nunca sale marcada porque su texto no está en
    el índice: `generar_audio` descarta todo lo que trae cirílico.

    Una frase sin audio se queda como está, sin botón y sin hueco: el audio se
    genera por tandas, así que el estado normal durante un tiempo es «algunas
    sí y otras no»."""
    if not indice:
        return html_

    def celda(m):
        dentro = m.group(2)
        texto = html.unescape(re.sub(r"<[^>]+>", "", dentro)).strip()
        archivo = indice.get(texto)
        if not archivo:
            return m.group(0)
        boton = (f'<button type="button" class="suena" aria-pressed="false" '
                 f'data-audio="{raiz}/audio/{html.escape(archivo)}" '
                 f'title="Прослушать" aria-label="Прослушать: {html.escape(texto)}">▶</button>')
        return f"{m.group(1)}{boton}{dentro}</td>"

    return re.sub(r"(<td[^>]*>)(.*?)</td>", celda, html_, flags=re.S)


def indice_de_imagenes(destino: pathlib.Path) -> dict:
    """Palabra → archivo. Vacío si todavía no se ha dibujado nada.

    Igual que el del audio y por lo mismo: se lee de `docs/img/`, no de una
    lista en el código, así que el sitio se construye igual con dibujos y sin
    ellos y encenderlos no es tocar el generador."""
    ruta = destino / "img" / INDICE_IMG
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


# Las DOS tablas de vocabulario del curso, y son dos formas distintas:
#
#   `Словарь дня`  (lecciones)  Español | Русский | Пример     -> la columna 0
#   `3. Слова`     (domingos)   Español | Русский | Español | Русский
#                                                              -> las 0 y la 2
#
# Son las únicas que llevan dibujo, y eso no es tacañería: en las de fonética
# la primera columna es una letra y en las de conjugación una forma verbal, así
# que un dibujo ahí no enseñaría nada y rompería la tabla.
#
# El domingo se descubrió tarde: las 50 lecciones de cultura generaban sus
# dibujos y no los enseñaba ninguna, porque el extractor del vocabulario SÍ lee
# esa tabla y el montaje no la miraba.
VOCABULARIO = re.compile(
    r'<h2[^>]*>\s*(?:Словарь дня|3\.\s*Слова[^<]*)\s*</h2>(.*?)(?=<h2|\Z)', re.S)

# En qué columnas de cada tabla hay español. La de los domingos repite el par
# (español, ruso), así que son las pares.
COLUMNAS_ES = {3: (0,), 4: (0, 2)}


def _dibujos_en_el_vocabulario(html_: str, indice: dict, raiz: str) -> str:
    """El dibujo del sustantivo, delante de la palabra, en la tabla del día.

    Solo en la PRIMERA celda de cada fila, que es la columna española. La rusa
    no casaría nunca —el índice no tiene cirílico— pero la de ejemplo sí
    podría: «la manzana» aparece en la frase de ejemplo de otra palabra, y ahí
    el dibujo sobraría.

    Una palabra sin dibujo se queda como está, sin hueco: las imágenes se
    generan por tandas y «algunas sí y otras no» es el estado normal.

    El `alt` va VACÍO a propósito. El dibujo no añade información que no esté
    ya en la fila —la palabra está al lado y su traducción en la columna
    siguiente—, así que un lector de pantalla que lo leyera diría la misma
    palabra dos veces."""
    if not indice:
        return html_

    def con_dibujo(abre, dentro):
        # El <button> del audio se quita ENTERO y no solo sus etiquetas:
        # `_botones_de_audio` corre antes y deja un «▶» dentro de la celda, así
        # que quitando solo las etiquetas el texto salía «▶el marido» y no
        # casaba con el índice —las 100 lecciones salieron sin un dibujo—.
        # Quitar el elemento entero aguanta además que mañana lleve otro signo.
        limpio = re.sub(r"<button\b.*?</button>", "", dentro, flags=re.S)
        texto = html.unescape(re.sub(r"<[^>]+>", "", limpio)).strip()
        archivo = indice.get(generar_imagenes.limpiar(texto))
        if not archivo:
            return None
        img = (f'<img class="dibujo" src="{raiz}/img/{html.escape(archivo)}" '
               f'alt="" width="56" height="56" loading="lazy" decoding="async">')
        return f"{abre}{img}{dentro}</td>"

    def seccion(m):
        salida = []
        for tr in re.split(r"(?=<tr[^>]*>)", m.group(1)):
            celdas = re.findall(r"(<td[^>]*>)(.*?)</td>", tr, flags=re.S)
            cuales = COLUMNAS_ES.get(len(celdas))
            if not cuales:
                salida.append(tr)
                continue
            for i in cuales:
                puesto = con_dibujo(*celdas[i])
                if puesto:
                    viejo_td = f"{celdas[i][0]}{celdas[i][1]}</td>"
                    tr = tr.replace(viejo_td, puesto, 1)
            salida.append(tr)
        return m.group(0).replace(m.group(1), "".join(salida))

    return VOCABULARIO.sub(seccion, html_)


def _enlaces_entre_documentos(html_: str) -> str:
    """Un .md citado desde otro documento se publica como .html.

    Los documentos del programa se enlazan entre sí por su nombre de archivo,
    que es lo correcto al leerlos en el repositorio y un enlace roto en la web.
    Los de `referencias/` llevan además el prefijo `ref-`."""
    def arreglar(m):
        nombre = m.group(1)
        prefijo = "ref-" if (RAIZ / "referencias" / f"{nombre}.md").exists() else ""
        return f'href="{prefijo}{nombre}.html"'
    return re.sub(r'href="(?!https?:)([^"/]+)\.md"', arreglar, html_)


def construir_programa(cfg, t, idiomas, destino) -> None:
    carpeta = destino / "programa"
    carpeta.mkdir(parents=True, exist_ok=True)
    for origen, prefijo in ((RAIZ / "programa", ""), (RAIZ / "referencias", "ref-")):
        for ruta in sorted(origen.glob("*.md")):
            cuerpo = _enlaces_entre_documentos(_tablas_envueltas(md(ruta.read_text(encoding="utf-8"))))
            carpeta.joinpath(f"{prefijo}{ruta.stem}.html").write_text(
                pagina(cfg, t, idiomas, "es", f"{ruta.stem} — documentación", cuerpo,
                       descripcion="Documentación del programa del curso.",
                       pagina_id=f"programa/{prefijo}{ruta.stem}.html", raiz="..",
                       traducida=False),
                encoding="utf-8")


def construir_ads_txt(cfg, destino) -> None:
    """ads.txt, que AdSense exige para pagar el inventario del sitio.

    Tiene que estar en la RAÍZ del dominio: google.com/ads.txt, no
    google.com/algo/ads.txt. Por eso en GitHub Pages solo sirve con dominio
    propio: en ianmusicall-max.github.io/espanol-desde-ruso/ este archivo cae en
    /espanol-desde-ruso/ads.txt, donde AdSense no lo mira nunca. Sin cliente no
    se escribe: un ads.txt vacío es peor que ninguno."""
    cliente = (cfg.get("adsense") or {}).get("cliente") or ""
    numero = cliente.replace("ca-pub-", "").strip()
    if not numero:
        return
    destino.joinpath("ads.txt").write_text(
        f"google.com, pub-{numero}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")


def construir_cname(cfg, destino) -> None:
    """El dominio propio para GitHub Pages, si lo hay.

    GitHub lo lee de este archivo y le saca el certificado de HTTPS solo. Sin
    dominio propio no se escribe, porque un CNAME con el dominio de github.io
    dentro deja el sitio sin servir."""
    dominio = (cfg.get("dominio") or "")
    host = dominio.split("//")[-1].split("/")[0]
    if not host or host.endswith("github.io"):
        return
    destino.joinpath("CNAME").write_text(host + "\n", encoding="utf-8")


def construir_sitemap(cfg, idiomas, destino, cal) -> None:
    dominio = cfg["dominio"]
    hoy = dt.date.today().isoformat()
    urls: list[tuple[str, str]] = []
    for i in idiomas:
        base = f"{i['carpeta']}/" if i["carpeta"] else ""
        urls += [(f"{base}index.html", "1.0"), (f"{base}kurs.html", "0.9"),
                 (f"{base}o-kurse.html", "0.5"), (f"{base}kontakt.html", "0.3"), (f"{base}privacy.html", "0.3")]
    urls.append(("test.html", "0.7"))
    urls += [(f"semana-{d.semana:02d}/dia-{d.dia}.html", "0.8") for d in escritas(cal)]
    if dominio:
        filas = "".join(f"<url><loc>{html.escape(dominio)}/{u}</loc><lastmod>{hoy}</lastmod><priority>{p}</priority></url>"
                        for u, p in urls)
        destino.joinpath("sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{filas}</urlset>\n',
            encoding="utf-8")
    robots = "User-agent: *\nAllow: /\n"
    if dominio:
        robots += f"\nSitemap: {dominio}/sitemap.xml\n"
    destino.joinpath("robots.txt").write_text(robots, encoding="utf-8")


def construir(destino: pathlib.Path = DOCS, cfg: dict | None = None, textos: dict | None = None,
              preguntas: dict | None = None) -> int:
    cal = plan.cargar()
    cfg = cfg or cargar_config()
    textos = textos or cargar_textos()
    preguntas = cargar_test() if preguntas is None else preguntas
    idiomas = textos["idiomas"]
    destino.mkdir(parents=True, exist_ok=True)

    # Antes de las páginas, porque el índice del curso enlaza la baraja y mira
    # si está: copiarlos después dejaría el bloque fuera en la primera corrida.
    construir_vocabulario(destino)
    construir_iconos(destino)

    # Antes del bucle y no dentro: la portada de los tres idiomas enseña los
    # mismos doce dibujos, así que leer el índice y recorrer las lecciones una
    # vez por idioma sería hacer tres veces el mismo trabajo.
    dibujos = indice_de_imagenes(destino)
    lexico = lexico_del_curso(cal) if dibujos else {}
    dibujos_unidad = dibujo_por_unidad(cal, dibujos)
    audio = indice_de_audio(destino)

    for i in idiomas:
        t = textos[i["codigo"]]
        carpeta = destino / i["carpeta"] if i["carpeta"] else destino
        carpeta.mkdir(parents=True, exist_ok=True)
        raiz = ".." if i["carpeta"] else "."
        construir_portada(cfg, t, idiomas, i["codigo"], carpeta, cal, raiz,
                          dibujos, lexico, audio, preguntas)
        construir_indice_curso(cfg, t, idiomas, i["codigo"], carpeta, cal, raiz,
                               destino, dibujos_unidad)
        construir_estaticas(cfg, t, idiomas, i["codigo"], carpeta, cal, raiz)

    construir_test(cfg, textos["ru"], idiomas, destino, cal, preguntas)
    todos = plan.dias(cal)
    hechas = escritas(cal)
    for d in hechas:
        construir_leccion(d, cfg, textos["ru"], idiomas, destino, cal, todos, audio,
                          dibujos)
    construir_programa(cfg, textos["es"], idiomas, destino)
    construir_sitemap(cfg, idiomas, destino, cal)
    construir_ads_txt(cfg, destino)
    construir_cname(cfg, destino)
    escribir_progreso_js(destino)
    destino.joinpath(".nojekyll").write_text("", encoding="utf-8")
    return len(hechas)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--destino", type=pathlib.Path, default=DOCS)
    a = p.parse_args(argv)
    cfg, textos = cargar_config(), cargar_textos()
    n = construir(a.destino, cfg, textos)
    print(f"{n} lecciones · {len(textos['idiomas'])} idiomas ({', '.join(i['codigo'] for i in textos['idiomas'])}) en {a.destino}")
    print(f"  anuncios: {'sí' if hay_anuncios(cfg) else 'no configurados'} · "
          f"analítica: {'sí' if hay_analitica(cfg) else 'no'} · "
          f"cookies: {'sí' if necesita_cookies(cfg) else 'no hacen falta'}")
    host = (cfg.get("dominio") or "").split("//")[-1].split("/")[0]
    pendiente = []
    if not cfg.get("autor", {}).get("email"):
        pendiente.append("sin correo de contacto en web/sitio.yaml; AdSense pide una forma de contacto")
    if host.endswith("github.io"):
        pendiente.append(f"el dominio es {host}, que no es tuyo: AdSense pide un dominio propio "
                         "y ads.txt tiene que estar en su raíz")
    if hay_anuncios(cfg):
        pendiente.append("con anuncios en la UE hace falta un CMP certificado por Google "
                         "(Privacidad y mensajes, dentro de AdSense): la banda de cookies de aquí no lo es")
    for x in pendiente:
        print(f"  aviso: {x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
