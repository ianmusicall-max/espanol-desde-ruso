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
import sys

import markdown
import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import pruebas  # noqa: E402
import validar  # noqa: E402

DOCS = RAIZ / "docs"
CONFIG = RAIZ / "web" / "sitio.yaml"
TEXTOS = RAIZ / "web" / "textos.yaml"
TEST = RAIZ / "programa" / "test-nivel.yaml"
# El nombre del índice de audio: lo escribe generar_audio.py y lo leen
# tanto el generador como las pruebas, así que vive en un solo sitio.
INDICE_AUDIO = "indice.json"
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

CSS = """
/* Tres estados: lo que diga el sistema, o lo que el lector elija con el botón
   de la luna. El atributo data-tema del <html> gana siempre sobre el sistema;
   lo escribe un script de dos líneas en <head> para que no haya parpadeo. */
:root{
  color-scheme:light;
  --papel:#fdfbf6; --tinta:#1b1e23; --tenue:#646c78; --linea:#e2dacb;
  --acento:#b03f26; --acento-suave:#fbeee9; --celeste:#2f6b8f; --celeste-suave:#eaf2f7;
  --realce:#fdf3d8; --tarjeta:#f7f2e6; --sombra:0 1px 2px rgba(27,30,35,.05);
  --ancho:44rem;
}
@media(prefers-color-scheme:dark){:root:not([data-tema="light"]){
  color-scheme:dark;
  --papel:#14161a; --tinta:#e8e4da; --tenue:#9aa2ae; --linea:#333941;
  --acento:#f0896a; --acento-suave:#2a1d19; --celeste:#7fb6d6; --celeste-suave:#162229;
  --realce:#2a2718; --tarjeta:#1d2026; --sombra:none;
}}
:root[data-tema="dark"]{
  color-scheme:dark;
  --papel:#14161a; --tinta:#e8e4da; --tenue:#9aa2ae; --linea:#333941;
  --acento:#f0896a; --acento-suave:#2a1d19; --celeste:#7fb6d6; --celeste-suave:#162229;
  --realce:#2a2718; --tarjeta:#1d2026; --sombra:none;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--papel);color:var(--tinta);
  font:400 17px/1.65 ui-serif,Georgia,"Times New Roman",serif;
  -webkit-font-smoothing:antialiased;overflow-wrap:break-word}
.sans{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
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
  font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:.86rem}
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
  font-family:ui-sans-serif,system-ui,sans-serif}
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

/* audio: un ▶ al lado de cada frase española que esté locutada */
.suena{background:none;border:0;padding:0 .35rem 0 0;margin:0;cursor:pointer;color:var(--celeste);
  font:inherit;font-size:.82em;line-height:1;vertical-align:baseline;opacity:.65;transition:opacity .12s}
.suena:hover,.suena:focus-visible{opacity:1}
.suena[aria-pressed="true"]{opacity:1;color:var(--acento)}
@media(hover:none){.suena{opacity:.9}}

/* Test de nivel */
.test-caja{background:var(--tarjeta);border:1px solid var(--linea);border-radius:12px;
  padding:1.2rem 1.3rem;margin:1.4rem 0;font-family:ui-sans-serif,system-ui,sans-serif}
.test-cuenta{font-size:.78rem;color:var(--tenue);letter-spacing:.04em;margin-bottom:.5rem}
.test-pregunta{font-size:1.08rem;font-weight:600;color:var(--tinta);margin:0 0 1rem;line-height:1.45}
.test-ops{display:flex;flex-direction:column;gap:.5rem}
.test-ops button{text-align:start;font:inherit;font-size:.98rem;color:var(--tinta);
  background:var(--papel);border:1.5px solid var(--linea);border-radius:9px;
  padding:.6rem .8rem;cursor:pointer;transition:border-color .12s,background .12s}
.test-ops button:hover{border-color:var(--acento)}
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
  font-family:ui-sans-serif,system-ui,sans-serif;transition:border-color .12s,transform .12s}
.u-tarjeta:hover{border-color:var(--acento);transform:translateY(-2px)}
.u-tarjeta .alto{display:flex;align-items:baseline;gap:.5rem;margin-bottom:.3rem}
.u-tarjeta .num{font-size:1.45rem;font-weight:700;color:var(--acento);
  font-feature-settings:"tnum";line-height:1}
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
.puerta{font-size:.9rem;color:var(--tenue);margin:-.6rem 0 0}
.puerta a{color:var(--acento);font-weight:600}
.progreso-nota{font-size:.84rem;color:var(--tenue);font-family:ui-sans-serif,system-ui,sans-serif;margin-top:.5rem}
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
h2,h3{font-family:ui-sans-serif,system-ui,-apple-system,sans-serif}
p{margin:.75rem 0}
a{color:var(--acento);text-underline-offset:2px}
strong{font-weight:650}

/* ---- portada ---- */
.heroe{padding:2rem 0 .5rem}
.heroe .lema{font-size:clamp(1.02rem,3.4vw,1.2rem);color:var(--tenue);margin:.5rem 0 1.1rem;font-style:italic}
.botones{display:flex;flex-wrap:wrap;gap:.65rem;margin:1.4rem 0}
.boton{display:inline-block;background:var(--acento);color:#fff;padding:.7rem 1.35rem;border-radius:8px;
  text-decoration:none;font-family:ui-sans-serif,system-ui,sans-serif;font-size:.97rem;font-weight:550;
  box-shadow:var(--sombra);transition:transform .12s ease}
.boton:hover{transform:translateY(-1px)}
.boton.secundario{background:transparent;color:var(--acento);border:1.5px solid var(--acento);box-shadow:none}

.progreso{margin:1.5rem 0;font-family:ui-sans-serif,system-ui,sans-serif}
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
:root[data-tema="dark"] .bien{color:#5fc48f}

blockquote{margin:1.2rem 0;padding:.85rem 1.1rem;background:var(--tarjeta);
  border-inline-start:3px solid var(--celeste);border-radius:0 8px 8px 0}
blockquote p:first-child{margin-top:0}blockquote p:last-child{margin-bottom:0}

/* ---- tablas ---- */
.tabla-env{overflow-x:auto;margin:.9rem 0;border:1px solid var(--linea);border-radius:9px;background:var(--papel)}
table{border-collapse:collapse;width:100%;font-size:.92rem;font-family:ui-sans-serif,system-ui,sans-serif}
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
ul.dias .num{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;color:var(--tenue);
  min-width:2.6rem;font-feature-settings:"tnum"}
ul.dias a{text-decoration:none}ul.dias a:hover{text-decoration:underline}
ul.dias .falta{color:var(--tenue)}
.tipo{font-family:ui-sans-serif,system-ui,sans-serif;font-size:.67rem;color:var(--celeste);
  text-transform:uppercase;letter-spacing:.07em;border:1px solid var(--linea);border-radius:999px;
  padding:.05rem .4rem;white-space:nowrap}
.unidad-cab{display:flex;flex-wrap:wrap;gap:.5rem;align-items:baseline;margin-top:2.4rem}
details{margin:.5rem 0;font-size:.93rem}
summary{cursor:pointer;font-family:ui-sans-serif,system-ui,sans-serif;font-size:.86rem;color:var(--tenue)}
details ul{margin:.5rem 0}

/* ---- lección ---- */
.leccion-cab{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center;margin:1.3rem 0 .2rem;
  font-family:ui-sans-serif,system-ui,sans-serif;font-size:.78rem;color:var(--tenue)}
.leccion-cab .n{background:var(--acento);color:#fff;border-radius:999px;padding:.12rem .6rem;font-weight:600}
.aviso{background:var(--realce);border:1px solid var(--linea);border-radius:8px;padding:.6rem .85rem;
  font-size:.88rem;font-family:ui-sans-serif,system-ui,sans-serif;margin:1rem 0}
nav.pasos{display:flex;justify-content:space-between;gap:.8rem;margin:2.5rem 0 0;padding-top:1rem;
  border-top:1px solid var(--linea);font-family:ui-sans-serif,system-ui,sans-serif;font-size:.86rem}
nav.pasos a{text-decoration:none;padding:.4rem .7rem;border:1px solid var(--linea);border-radius:7px}
nav.pasos a:hover{border-color:var(--acento)}
input[type=checkbox]{margin-inline-end:.45rem}

/* ---- anuncios, pie, cookies ---- */
.anuncio{margin:2rem 0;text-align:center;min-height:1px}
.anuncio::before{content:attr(data-etiqueta);display:block;font-family:ui-sans-serif,system-ui,sans-serif;
  font-size:.64rem;color:var(--tenue);text-transform:uppercase;letter-spacing:.09em;margin-bottom:.3rem}
footer.sitio{border-top:1px solid var(--linea);padding:1.6rem 0 3rem;
  font-family:ui-sans-serif,system-ui,sans-serif;font-size:.83rem;color:var(--tenue)}
footer.sitio a{color:var(--tenue)}
footer.sitio p{margin:.35rem 0}
#cookies{position:fixed;inset-inline:0;bottom:0;background:var(--tarjeta);border-top:1px solid var(--linea);
  padding:.85rem 20px;font-family:ui-sans-serif,system-ui,sans-serif;font-size:.85rem;display:flex;
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
      boton.addEventListener('click',function(){
        var lista=hechas(), i=lista.indexOf(n);
        if(i>=0){lista.splice(i,1)}else{lista.push(n)}
        guardar(CLAVE_HECHAS,lista);pintar();
        if(i<0&&siguiente){siguiente.classList.add('destacado')}
      });
      pintar();caja.appendChild(boton);
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
  var i=0, fallos=[], aciertos=0, reloj=null, queda=0;

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
    var q=D.preguntas[i];
    caja.innerHTML='<div class="test-caja">'
      +'<div class="test-cuenta">'+(i+1)+' '+esc(D.t.de)+' '+D.preguntas.length
      +' · '+esc(D.t.instruccion)
      +(D.segundos?'<b class="test-seg"></b>':'')+'</div>'
      +(D.segundos?'<div class="test-reloj"><i></i></div>':'')
      +'<p class="test-pregunta">'+esc(q.pregunta)+'</p>'
      +'<div class="test-ops">'+q.opciones.map(function(o,n){
          return '<button type="button" data-n="'+n+'">'+esc(o)+'</button>'}).join('')+'</div>'
      +'<div class="test-barra"><i style="width:'+(i*100/D.preguntas.length)+'%"></i></div></div>';
    caja.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){responder(parseInt(b.dataset.n,10))});
    });
    arrancar();
  }

  // n === -1 es «se acabó el tiempo». Se anota aparte para poder decirlo en el
  // resultado: no es lo mismo equivocarse que no llegar.
  function responder(n){
    parar();
    var q=D.preguntas[i];
    if(n===q.correcta){aciertos++}
    else{fallos.push(n===-1?Object.assign({},q,{tarde:true}):q)}
    i++;
    if(i<D.preguntas.length){pregunta()}else{resultado()}
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
      +'<p class="test-pregunta">'+aciertos+' / '+D.preguntas.length+' '+esc(D.t.aciertos)+'</p>';
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
    if(r)r.addEventListener('click',function(){i=0;fallos=[];aciertos=0;pregunta()});
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
    boton.addEventListener('click',function(){arranque.hidden=true;pregunta()});
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


PRUEBA_JS = r"""(function(){
  var D=window.CURSO_PRUEBA; if(!D)return;
  var caja=document.getElementById('prueba'); if(!caja)return;
  var papel=document.getElementById('prueba-papel');
  var clave=document.getElementById('prueba-clave');
  var i=0, fallos=[], aciertos=0;

  function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML}

  // Sin JavaScript la pagina se queda EXACTAMENTE como estaba: las quince
  // preguntas y su clave, para leer o imprimir. El guion solo las esconde
  // cuando de verdad puede ofrecer algo mejor.
  if(papel)papel.hidden=true;
  if(clave)clave.hidden=true;

  function pregunta(){
    var q=D.preguntas[i];
    caja.innerHTML='<div class="test-caja">'
      +'<div class="test-cuenta">'+(i+1)+' '+esc(D.t.de)+' '+D.preguntas.length
      +' · '+esc(q.bloque)+'</div>'
      +'<p class="test-pregunta">'+esc(q.enunciado)+'</p>'
      +'<div class="test-ops">'+q.opciones.map(function(o,n){
          return '<button type="button" data-n="'+n+'">'+esc(o)+'</button>'}).join('')+'</div>'
      +'<div class="test-barra"><i style="width:'+(i*100/D.preguntas.length)+'%"></i></div></div>';
    caja.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){responder(parseInt(b.dataset.n,10))});
    });
  }

  function responder(n){
    var q=D.preguntas[i];
    if(n===q.correcta){aciertos++}else{fallos.push(q)}
    i++;
    if(i<D.preguntas.length){pregunta()}else{resultado()}
  }

  function resultado(){
    var h='<div class="test-caja"><div class="test-cuenta">'+esc(D.t.resultado)+'</div>'
      +'<p class="test-pregunta">'+aciertos+' / '+D.preguntas.length+' '+esc(D.t.aciertos)+'</p>';
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
    if(r)r.addEventListener('click',function(){i=0;fallos=[];aciertos=0;pregunta()});
    var v=document.getElementById('ver-clave');
    // El discurso sobre los distractores que cierra la clave es lo mejor del
    // dia, y solo ensena DESPUES de contestar: antes seria la respuesta.
    if(v)v.addEventListener('click',function(){
      if(clave){clave.hidden=false;clave.scrollIntoView({behavior:'smooth'})}
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
def necesita_cookies(cfg): return hay_anuncios(cfg) or hay_analitica(cfg)


# ------------------------------------------------------------------- fragmentos
def anuncio(cfg: dict, ranura: str) -> str:
    """Un bloque de AdSense, o nada. Sin cliente no se escribe ni el contenedor."""
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
def pagina(cfg, t, idiomas, idioma, titulo, cuerpo, *, descripcion="", pagina_id="", raiz=".",
           jsonld="", publicadas=0, mapa_dias="{}", traducida=True, con_audio=False, test=None,
           prueba=None) -> str:
    """El armazón de toda página: cabecera con menú y cambio de idioma, cuerpo, pie."""
    dominio = cfg["dominio"]
    actual = next(i for i in idiomas if i["codigo"] == idioma)
    base_actual = f"{dominio}/{actual['carpeta']}".rstrip("/") if dominio else ""
    canonica = f"{base_actual}/{pagina_id}" if base_actual and pagina_id else base_actual

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
          + (f'<meta property="og:url" content="{html.escape(canonica)}">' if canonica else ""))
    estructura = f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""

    return f"""<!doctype html>
<html lang="{actual['html']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title>
{meta}{canon}{"".join(hreflangs)}{og}{estructura}
<style>{CSS}</style>
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
</div></footer>
{banda_cookies(cfg, t, raiz)}
{TEMA_SCRIPT}
{IDIOMA_SCRIPT if not traducida else ""}
<script>window.CURSO_TEXTOS={json.dumps(t['progreso'], ensure_ascii=False)};window.CURSO_RAIZ="{raiz}";window.CURSO_PUBLICADAS={publicadas};window.CURSO_DIAS={mapa_dias};</script>
<script src="{raiz}/progreso.js" defer></script>
{f'<script>{AUDIO_JS}</script>' if con_audio else ""}
{f'<script>window.CURSO_TEST={json.dumps(test, ensure_ascii=False)};{TEST_JS}</script>' if test else ""}
{f'<script>window.CURSO_PRUEBA={json.dumps(prueba, ensure_ascii=False)};{PRUEBA_JS}</script>' if prueba else ""}
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
    propósito: el test cae entonces en la última escrita, que es la respuesta
    honrada —si ya sabe todo lo que el curso cubre, ahí empieza—."""
    inicios: dict[int, dict] = {}
    for d in escritas(cal):
        inicios.setdefault(d.unidad, {"n": d.numero,
                                      "url": f"{raiz}/semana-{d.semana:02d}/dia-{d.dia}.html"})
    return inicios


def escribir_progreso_js(destino: pathlib.Path) -> None:
    destino.joinpath("progreso.js").write_text(PROGRESO_JS, encoding="utf-8")


# ----------------------------------------------------------------------- páginas
def construir_portada(cfg, t, idiomas, idioma, destino, cal, raiz) -> None:
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
<h1>{html.escape(p['titulo'])}<span class="segunda">{html.escape(p['titulo2'])}</span></h1>
<p class="lema">{html.escape(p['lema'])}</p>
<p>{html.escape(p['entrada'])}</p>
<div class="botones">
<a class="boton" id="continuar" href="{enlace}" hidden></a>
<a class="boton" id="empezar" href="{enlace}">{html.escape(p['boton'])}</a>
<a class="boton secundario" href="{raiz}/kurs.html">{html.escape(p['boton2'])}</a>
</div>
<p class="puerta">{html.escape(p['ya_sabe'])} <a href="{raiz}/test.html">{html.escape(t['test']['titulo'])} →</a></p>
<div class="progreso">
<div class="cifras"><span class="n">{len(hechas)}</span><span>/ {total} {html.escape(p['progreso'])}</span></div>
<div class="barra"><i style="width:{max(pct, 1)}%"></i></div>
{nota_meses}
<div id="mio" hidden>
<div class="cifras"><span class="n">0</span><span class="texto"></span></div>
<div class="barra"><i style="width:1%"></i></div>
<p class="progreso-nota">{html.escape(pr['aviso'])} <button type="button" id="borrar-progreso" hidden>{html.escape(pr['borrar'])}</button></p>
</div>
</div>
</div>
{anuncio(cfg, "cabecera")}

<h2>{html.escape(p['dif_titulo'])}</h2>
<p>{p['dif_texto']}</p>
<section class="contraste">
<p><strong>{html.escape(p['dif_error'])}</strong> <span class="mal">✗ <em>Tengo hermano.</em></span><br>
<strong>{html.escape(p['dif_bien'])}</strong> <span class="bien">✅ <em>Tengo <strong>un</strong> hermano.</em></span></p>
<p>{html.escape(p['dif_nota'])}</p>
</section>
<p>{p['dif_ayuda']}</p>

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
{anuncio(cfg, "pie")}
"""
    destino.joinpath("index.html").write_text(
        pagina(cfg, t, idiomas, idioma, f"{p['titulo']} {p['titulo2']} — {p['lema']}", cuerpo,
               descripcion=p["entrada"], pagina_id="index.html", raiz=raiz, jsonld=jsonld,
               publicadas=len(hechas), mapa_dias=mapa_de_dias(cal)),
        encoding="utf-8")


def _mapa_de_unidades(cal: dict, dias: list, c: dict, idioma: str, raiz: str) -> str:
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
        hechas = sum(1 for d in suyos if d.ruta.exists())
        primera = next((d for d in suyos if d.ruta.exists()), None)
        # Con `raiz`: las lecciones viven solo en la carpeta de ruso, asi que
        # desde /es/kurs.html y /en/kurs.html un enlace relativo sin prefijo
        # apunta a /es/semana-01/..., que no existe. Lo caza la prueba de
        # enlaces rotos, que es la misma que encontro los 404 del conmutador.
        destino_u = (f"{raiz}/semana-{primera.semana:02d}/dia-{primera.dia}.html" if primera
                     else f"#u{u['numero']}")
        titulo = u["titulo_ru"] if idioma == "ru" else u["titulo_es"]
        ep = (u.get("episodio") or {}).get("titulo", "")
        pct = round(hechas * 100 / len(suyos)) if suyos else 0
        tarjetas.append(
            f'<a class="u-tarjeta{"" if primera else " vacia"}" href="{destino_u}">'
            f'<span class="alto"><span class="num">{u["numero"]}</span>'
            f'<span class="nivel">{html.escape(u["nivel"])}</span></span>'
            f'<span class="tit">{html.escape(titulo)}</span>'
            + (f'<span class="serie">{html.escape(c["episodio"])}: {html.escape(ep)}</span>' if ep else "")
            + f'<span class="pie"><span>{hechas}/{len(suyos)} {html.escape(c["listos"])}</span>'
              f'<span class="mini"><i style="width:{pct}%"></i></span></span></a>')
    return (f'<h2>{html.escape(c["mapa"])}</h2>'
            f'<p>{html.escape(c["mapa_nota"])}</p>'
            f'<div class="mapa">{"".join(tarjetas)}</div>')


def construir_indice_curso(cfg, t, idiomas, idioma, destino, cal, raiz) -> None:
    c, pr = t["curso"], t["progreso"]
    partes = [f'<h1>{html.escape(c["titulo"])}<span class="segunda">{html.escape(c["subtitulo"])}</span></h1>',
              f'<p>{html.escape(c["entrada"])}</p>',
              # Oculto hasta que el navegador diga que hay algo hecho: en blanco
              # no dice nada y un «0 / 100» de bienvenida desanima.
              f'<div class="progreso" id="mio" hidden>'
              f'<div class="cifras"><span class="n">0</span><span class="texto"></span></div>'
              f'<div class="barra"><i style="width:1%"></i></div>'
              f'<p class="progreso-nota">{html.escape(pr["aviso"])} '
              f'<button type="button" id="borrar-progreso" hidden>{html.escape(pr["borrar"])}</button></p></div>',
              f'<p class="puerta">{html.escape(t["portada"]["ya_sabe"])} '
              f'<a href="{raiz}/test.html">{html.escape(t["test"]["titulo"])} →</a></p>',
              anuncio(cfg, "cabecera")]
    dias = plan.dias(cal)
    partes.append(_mapa_de_unidades(cal, dias, c, idioma, raiz))
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
    partes.append(anuncio(cfg, "pie"))
    destino.joinpath("kurs.html").write_text(
        pagina(cfg, t, idiomas, idioma, f'{c["titulo"]} — {c["subtitulo"]}', "\n".join(partes),
               descripcion=c["entrada"], pagina_id="kurs.html", raiz=raiz,
               publicadas=len(escritas(cal)), mapa_dias=mapa_de_dias(cal)),
        encoding="utf-8")


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
        ultima = hechas[-1]
        datos = {
            # Al navegador va `error_ru` y no `error_es`: lo lee un principiante
            # ruso, y explicarle su propio error en el idioma que viene a
            # aprender no le enseña nada. El español se queda en el YAML, que
            # es donde el profesor revisa.
            "preguntas": [{"pregunta": q["pregunta"], "opciones": q["opciones"],
                           "correcta": q["correcta"], "unidad": q["unidad"],
                           "error": q["error_ru"]}
                          for q in lista],
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
<p><strong>{html.escape(autor.get('nombre', ''))}</strong>. {html.escape(autor.get('descripcion', ''))}</p>
<h2>{html.escape(s['porque'])}</h2>
<p>{s['porque_texto']}</p>
<p>{html.escape(s['porque_texto2'])}</p>
<h2>{html.escape(s['como'])}</h2>
<p>{html.escape(s['como_texto'])}</p>
<h2>{html.escape(s['cuanto'])}</h2>
<p>{html.escape(s['cuanto_texto'])}</p>
<p><strong>{html.escape(s['abierto'])}: {hechas} / {len(plan.dias(cal))}.</strong></p>
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
<p><strong>{html.escape(autor.get('nombre', ''))}</strong>. {html.escape(autor.get('descripcion', ''))}</p>
"""
    destino.joinpath("kontakt.html").write_text(
        pagina(cfg, t, idiomas, idioma, f"{k['titulo']} — {t['titulo_sitio']}", cuerpo,
               descripcion=k["texto"], pagina_id="kontakt.html", raiz=raiz), encoding="utf-8")

    pr = t["privacidad"]
    bloques = [f"<h1>{html.escape(pr['titulo'])}</h1>",
               f"<p>{html.escape(pr['actualizado'])}: {dt.date.today().isoformat()}.</p>",
               f"<h2>{html.escape(pr['propio'])}</h2><p>{html.escape(pr['propio_texto'])}</p>"]
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
                f"<h2>{html.escape(pr['ninos'])}</h2><p>{html.escape(pr['ninos_texto'])}</p>"]
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


def _envolver_prueba(html_: str, t: dict) -> str:
    """Marca en el HTML qué parte es el test en papel y cuál la clave.

    Se trabaja sobre el HTML ya convertido y no sobre el Markdown a propósito:
    envolver Markdown en un `<div>` haría que Python-Markdown lo pasara tal cual
    sin convertirlo, y las quince preguntas saldrían en crudo.

    Los tres trozos se marcan de atrás adelante porque cada inserción mueve
    todas las posiciones siguientes."""
    cabeceras = [(m.start(), m.end(), re.sub("<[^>]+>", "", m.group(1)).strip())
                 for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", html_, re.S)]
    inicio_test = fin_test = inicio_clave = None
    for j, (ini, fin, texto) in enumerate(cabeceras):
        if texto.startswith("2.") and inicio_test is None:
            inicio_test, fin_test = fin, (cabeceras[j + 1][0] if j + 1 < len(cabeceras) else len(html_))
        if texto == "Ответы":
            inicio_clave = ini
    if inicio_test is None or inicio_clave is None:
        return html_

    boton = (f'<div class="botones" id="prueba-arranque" hidden>'
             f'<button type="button" class="boton" id="prueba-empezar">'
             f'{html.escape(t["test"]["empezar"])}</button></div><div id="prueba"></div>')
    trozos = [html_[:inicio_test], boton, '<div id="prueba-papel">', html_[inicio_test:fin_test],
              "</div>", html_[fin_test:inicio_clave], '<div id="prueba-clave">',
              html_[inicio_clave:], "</div>"]
    return "".join(trozos)


def construir_leccion(d, cfg, t, idiomas, destino, cal, todos, audio=None) -> None:
    """Las lecciones solo existen en ruso: son el curso."""
    datos, cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))
    i = todos.index(d)
    anterior = next((x for x in reversed(todos[:i]) if x.ruta.exists()), None)
    siguiente = next((x for x in todos[i + 1:] if x.ruta.exists()), None)
    L = t["leccion"]

    html_cuerpo = _botones_de_audio(md(cuerpo), audio or {}, "..")
    html_cuerpo = _anuncios_en_la_leccion(_marcar_contraste(_tablas_envueltas(html_cuerpo)), cfg)

    # Los días de tipo `prueba` traen quince preguntas con su clave, ya escritas
    # y revisadas por el profesor. Si se pueden leer con seguridad, se ofrecen
    # para contestar; si no, la página se queda exactamente como está.
    datos_prueba = None
    if d.tipo == "prueba":
        preguntas = pruebas.leer(cuerpo)
        if preguntas:
            datos_prueba = {
                "preguntas": [_pregunta_al_navegador(q, todos) for q in preguntas],
                "t": t["test"],
            }
            html_cuerpo = _envolver_prueba(html_cuerpo, t)

    titulo = f"{L['urok']} {d.numero}: {d.tema_ru} — {t['titulo_sitio']}"
    descripcion = f"{L['urok']} {d.numero}: {d.tema_ru}. {d.foco[:110]}"
    aviso = "" if datos.get("revisado") else f'<p class="aviso">{html.escape(L["borrador"])}</p>'

    pasos = []
    pasos.append(f'<a href="../semana-{anterior.semana:02d}/dia-{anterior.dia}.html">← {L["anterior"]} {anterior.numero}</a>' if anterior else "<span></span>")
    pasos.append(f'<a href="../kurs.html">{html.escape(L["todos"])}</a>')
    # El id lo usa progreso.js para destacarlo en cuanto marcas esta lección:
    # el paso siguiente es lo único que se quiere hacer después de marcar.
    pasos.append(f'<a id="enlace-siguiente" href="../semana-{siguiente.semana:02d}/dia-{siguiente.dia}.html">{L["siguiente"]} {siguiente.numero} →</a>' if siguiente else "<span></span>")

    cab = (f'<div class="leccion-cab"><span class="n">{L["urok"]} {d.numero}</span>'
           f'<span>{L["de"]} {len(todos)}</span><span class="tipo">{plan.TIPO_RU[d.tipo]}</span>'
           f'<span>{L["semana"]} {d.semana} · {L["nivel"]} {html.escape(d.nivel)}</span></div>')
    # El botón de marcar lo pone el navegador y no el generador: sin JavaScript
    # no haría nada, y un botón muerto es peor que ninguno.
    cuerpo_final = (f'<article data-leccion="{d.numero}">' + cab + aviso
                    + html_cuerpo + anuncio(cfg, "pie") + '<div id="marcar-caja"></div>'
                    + f'<nav class="pasos">{"".join(pasos)}</nav></article>')

    salida = destino / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        pagina(cfg, t, idiomas, "ru", titulo, cuerpo_final, descripcion=descripcion,
               pagina_id=f"semana-{d.semana:02d}/dia-{d.dia}.html", raiz="..",
               publicadas=len(escritas(cal)), mapa_dias=mapa_de_dias(cal), traducida=False,
               con_audio='class="suena"' in cuerpo_final, prueba=datos_prueba),
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

    for i in idiomas:
        t = textos[i["codigo"]]
        carpeta = destino / i["carpeta"] if i["carpeta"] else destino
        carpeta.mkdir(parents=True, exist_ok=True)
        raiz = ".." if i["carpeta"] else "."
        construir_portada(cfg, t, idiomas, i["codigo"], carpeta, cal, raiz)
        construir_indice_curso(cfg, t, idiomas, i["codigo"], carpeta, cal, raiz)
        construir_estaticas(cfg, t, idiomas, i["codigo"], carpeta, cal, raiz)

    construir_test(cfg, textos["ru"], idiomas, destino, cal, preguntas)
    todos = plan.dias(cal)
    hechas = escritas(cal)
    audio = indice_de_audio(destino)
    for d in hechas:
        construir_leccion(d, cfg, textos["ru"], idiomas, destino, cal, todos, audio)
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
