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
import validar  # noqa: E402

DOCS = RAIZ / "docs"
CONFIG = RAIZ / "web" / "sitio.yaml"
TEXTOS = RAIZ / "web" / "textos.yaml"
EXTENSIONES = ["tables", "fenced_code", "sane_lists", "toc", "attr_list"]

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
.idiomas a{padding:.12rem .5rem;border-radius:999px;font-size:.75rem;font-weight:600;
  text-transform:uppercase;letter-spacing:.05em;line-height:1.5}
.idiomas a[aria-current]{background:var(--acento);color:#fff}
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
@media(min-width:40rem){
  header.sitio nav.paginas{order:0;flex:0 1 auto;margin-inline-start:auto}
  header.sitio .marca{flex:0 1 auto}
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
def pagina(cfg, t, idiomas, idioma, titulo, cuerpo, *, descripcion="", pagina_id="", raiz=".", jsonld="") -> str:
    """El armazón de toda página: cabecera con menú y cambio de idioma, cuerpo, pie."""
    dominio = cfg["dominio"]
    actual = next(i for i in idiomas if i["codigo"] == idioma)
    base_actual = f"{dominio}/{actual['carpeta']}".rstrip("/") if dominio else ""
    canonica = f"{base_actual}/{pagina_id}" if base_actual and pagina_id else base_actual

    menu = "".join(
        f'<a href="{raiz}/{destino}"{" aria-current=\"page\"" if destino == pagina_id else ""}>{html.escape(t["menu"][clave])}</a>'
        for clave, destino in (("curso", "kurs.html"), ("sobre", "o-kurse.html"), ("contacto", "kontakt.html"))
    )
    # El cambio de idioma lleva a la MISMA página en el otro idioma.
    conmutador = []
    hreflangs = []
    for i in idiomas:
        prefijo = f"{raiz}/{i['carpeta']}".rstrip("/") if i["carpeta"] else raiz
        destino = f"{prefijo}/{pagina_id or 'index.html'}"
        marca = ' aria-current="true"' if i["codigo"] == idioma else ""
        conmutador.append(f'<a href="{destino}" hreflang="{i["html"]}" lang="{i["html"]}"{marca}>{i["codigo"]}</a>')
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
</div></header>
<main><div class="envoltorio">
{cuerpo}
</div></main>
<footer class="sitio"><div class="envoltorio">
<p><a href="{raiz}/o-kurse.html">{html.escape(t['menu']['sobre'])}</a> · <a href="{raiz}/kontakt.html">{html.escape(t['menu']['contacto'])}</a> · <a href="{raiz}/privacy.html">{html.escape(t['privacidad']['titulo'])}</a></p>
<p>{html.escape(t['pie'])}</p>
</div></footer>
{banda_cookies(cfg, t, raiz)}
{TEMA_SCRIPT}
</body>
</html>"""


def md(texto: str) -> str:
    return markdown.markdown(texto, extensions=EXTENSIONES)


def escritas(cal: dict) -> list[plan.Dia]:
    return [d for d in plan.dias(cal) if d.ruta.exists()]


# ----------------------------------------------------------------------- páginas
def construir_portada(cfg, t, idiomas, idioma, destino, cal, raiz) -> None:
    hechas = escritas(cal)
    total = len(plan.dias(cal))
    primera = hechas[0] if hechas else None
    enlace = f"{raiz}/semana-{primera.semana:02d}/dia-{primera.dia}.html" if primera else f"{raiz}/kurs.html"
    p = t["portada"]
    pct = round(len(hechas) * 100 / total, 1)

    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Course",
        "name": t["titulo_sitio"], "description": p["entrada"],
        "inLanguage": "ru", "teaches": "Spanish", "educationalLevel": "A1-A2",
        "provider": {"@type": "Person", "name": cfg.get("autor", {}).get("nombre", "")},
        "isAccessibleForFree": True,
    }, ensure_ascii=False)

    filas = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>" for a, b in p["dia_filas"])
    tarjetas = "".join(f'<div class="tarjeta"><h3>{html.escape(a)}</h3><p>{b}</p></div>' for a, b in p["ano_tarjetas"])

    cuerpo = f"""
<div class="heroe">
<h1>{html.escape(p['titulo'])}<span class="segunda">{html.escape(p['titulo2'])}</span></h1>
<p class="lema">{html.escape(p['lema'])}</p>
<p>{html.escape(p['entrada'])}</p>
<div class="botones">
<a class="boton" href="{enlace}">{html.escape(p['boton'])}</a>
<a class="boton secundario" href="{raiz}/kurs.html">{html.escape(p['boton2'])}</a>
</div>
<div class="progreso">
<div class="cifras"><span class="n">{len(hechas)}</span><span>/ {total} {html.escape(p['progreso'])}</span></div>
<div class="barra"><i style="width:{max(pct, 1)}%"></i></div>
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
               descripcion=p["entrada"], pagina_id="index.html", raiz=raiz, jsonld=jsonld),
        encoding="utf-8")


def construir_indice_curso(cfg, t, idiomas, idioma, destino, cal, raiz) -> None:
    c = t["curso"]
    partes = [f'<h1>{html.escape(c["titulo"])}<span class="segunda">{html.escape(c["subtitulo"])}</span></h1>',
              f'<p>{html.escape(c["entrada"])}</p>', anuncio(cfg, "cabecera")]
    dias = plan.dias(cal)
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
                    f'<div class="unidad-cab"><h2 style="border:0;margin:0;padding:0">{c["tema"]} {u["numero"]}. {html.escape(titulo_u)}</h2>'
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
                partes.append(f'<li>{num}<span><a href="{raiz}/semana-{d.semana:02d}/dia-{d.dia}.html">{html.escape(tema)}</a> {etiqueta}</span></li>')
            else:
                partes.append(f'<li>{num}<span class="falta">{html.escape(tema)} {etiqueta}</span></li>')
        partes.append("</ul>")
    partes.append(anuncio(cfg, "pie"))
    destino.joinpath("kurs.html").write_text(
        pagina(cfg, t, idiomas, idioma, f'{c["titulo"]} — {c["subtitulo"]}', "\n".join(partes),
               descripcion=c["entrada"], pagina_id="kurs.html", raiz=raiz),
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


def construir_leccion(d, cfg, t, idiomas, destino, cal, todos) -> None:
    """Las lecciones solo existen en ruso: son el curso."""
    datos, cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))
    i = todos.index(d)
    anterior = next((x for x in reversed(todos[:i]) if x.ruta.exists()), None)
    siguiente = next((x for x in todos[i + 1:] if x.ruta.exists()), None)
    L = t["leccion"]

    html_cuerpo = _marcar_contraste(_tablas_envueltas(md(cuerpo)))
    dentro = anuncio(cfg, "dentro")
    if dentro:
        marca = re.search(r"<h2[^>]*>4\.\s*(Практика|Задание)", html_cuerpo)
        if marca:
            html_cuerpo = html_cuerpo[:marca.start()] + dentro + html_cuerpo[marca.start():]

    titulo = f"{L['urok']} {d.numero}: {d.tema_ru} — {t['titulo_sitio']}"
    descripcion = f"{L['urok']} {d.numero}: {d.tema_ru}. {d.foco[:110]}"
    aviso = "" if datos.get("revisado") else f'<p class="aviso">{html.escape(L["borrador"])}</p>'

    pasos = []
    pasos.append(f'<a href="../semana-{anterior.semana:02d}/dia-{anterior.dia}.html">← {L["anterior"]} {anterior.numero}</a>' if anterior else "<span></span>")
    pasos.append(f'<a href="../kurs.html">{html.escape(L["todos"])}</a>')
    pasos.append(f'<a href="../semana-{siguiente.semana:02d}/dia-{siguiente.dia}.html">{L["siguiente"]} {siguiente.numero} →</a>' if siguiente else "<span></span>")

    cab = (f'<div class="leccion-cab"><span class="n">{L["urok"]} {d.numero}</span>'
           f'<span>{L["de"]} {len(todos)}</span><span class="tipo">{plan.TIPO_RU[d.tipo]}</span>'
           f'<span>{L["semana"]} {d.semana} · {L["nivel"]} {html.escape(d.nivel)}</span></div>')
    cuerpo_final = cab + anuncio(cfg, "cabecera") + aviso + html_cuerpo + anuncio(cfg, "pie") + f'<nav class="pasos">{"".join(pasos)}</nav>'

    salida = destino / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        pagina(cfg, t, idiomas, "ru", titulo, cuerpo_final, descripcion=descripcion,
               pagina_id=f"semana-{d.semana:02d}/dia-{d.dia}.html", raiz=".."),
        encoding="utf-8")


def construir_programa(cfg, t, idiomas, destino) -> None:
    carpeta = destino / "programa"
    carpeta.mkdir(parents=True, exist_ok=True)
    for origen, prefijo in ((RAIZ / "programa", ""), (RAIZ / "referencias", "ref-")):
        for ruta in sorted(origen.glob("*.md")):
            cuerpo = _tablas_envueltas(md(ruta.read_text(encoding="utf-8")))
            carpeta.joinpath(f"{prefijo}{ruta.stem}.html").write_text(
                pagina(cfg, t, idiomas, "es", f"{ruta.stem} — documentación", cuerpo,
                       descripcion="Documentación del programa del curso.",
                       pagina_id=f"programa/{prefijo}{ruta.stem}.html", raiz=".."),
                encoding="utf-8")


def construir_sitemap(cfg, idiomas, destino, cal) -> None:
    dominio = cfg["dominio"]
    hoy = dt.date.today().isoformat()
    urls: list[tuple[str, str]] = []
    for i in idiomas:
        base = f"{i['carpeta']}/" if i["carpeta"] else ""
        urls += [(f"{base}index.html", "1.0"), (f"{base}kurs.html", "0.9"),
                 (f"{base}o-kurse.html", "0.5"), (f"{base}kontakt.html", "0.3"), (f"{base}privacy.html", "0.3")]
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


def construir(destino: pathlib.Path = DOCS, cfg: dict | None = None, textos: dict | None = None) -> int:
    cal = plan.cargar()
    cfg = cfg or cargar_config()
    textos = textos or cargar_textos()
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

    todos = plan.dias(cal)
    hechas = escritas(cal)
    for d in hechas:
        construir_leccion(d, cfg, textos["ru"], idiomas, destino, cal, todos)
    construir_programa(cfg, textos["es"], idiomas, destino)
    construir_sitemap(cfg, idiomas, destino, cal)
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
    if not cfg.get("autor", {}).get("email"):
        print("  aviso: sin correo de contacto en web/sitio.yaml; AdSense suele pedirlo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
