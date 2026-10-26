#!/usr/bin/env python3
"""Las lecciones, en un archivo que WordPress importa de un clic.

    .venv/bin/python scripts/exportar_wordpress.py

Deja `salida/curso-wordpress.xml`. En WordPress: Herramientas → Importar →
WordPress → subir el archivo. El importador crea una entrada por lección, una
categoría por unidad y una página con el índice del curso.

Dos decisiones que no son de forma:

- **Las lecciones sin revisar entran como BORRADOR.** La regla 6 del proyecto
  dice que nada generado con Claude se publica sin revisión del profesor, y esa
  regla tiene que sobrevivir al cambio de plataforma: si entraran publicadas,
  mudarse a WordPress sería la forma de saltársela sin querer.
- **El HTML no depende del CSS del sitio.** El bloque de contraste —la firma
  del curso— lleva estilo en línea, porque es lo único que se perdería del todo
  en un tema de WordPress y lo que hace que la lección se entienda. Para lo
  demás hay una hoja aparte, opcional, en `salida/curso-wordpress.css`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
import unicodedata
import xml.sax.saxutils as sax

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import construir_sitio  # noqa: E402
import plan  # noqa: E402
import validar  # noqa: E402

SALIDA = RAIZ / "salida"

# El contraste con el ruso es lo único que no puede perderse al cambiar de
# plantilla: va con estilo en línea para que se vea igual en cualquier tema.
ESTILO_CONTRASTE = ("background:#fdf1ec;border:1px solid #e8c4b4;border-radius:10px;"
                    "padding:16px 18px;margin:20px 0")

CSS_OPCIONAL = """/* Opcional: Apariencia → Personalizar → CSS adicional.
   El bloque de contraste ya lleva su estilo dentro de cada entrada, así que
   esto solo afina las tablas y el vocabulario. */
.urok table{border-collapse:collapse;width:100%;font-size:.94rem}
.urok th,.urok td{padding:.45rem .65rem;text-align:start;vertical-align:top;
  border-bottom:1px solid #e2dacb}
.urok th{background:#f6f1e7;font-weight:600}
.urok del{text-decoration-color:#c0533b;text-decoration-thickness:2px;opacity:.75}
.urok blockquote{margin:1.2rem 0;padding:.85rem 1.1rem;background:#f6f1e7;
  border-inline-start:3px solid #3f7f93;border-radius:0 8px 8px 0}
"""


def babosa(texto: str) -> str:
    """Un slug latino para una URL: WordPress acepta cirílico, pero una URL en
    cirílico viaja codificada como %D0%90… y se vuelve ilegible al compartirla."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "urok"


def cdata(texto: str) -> str:
    """CDATA no puede contener «]]>»: hay que partirlo en dos secciones."""
    return "<![CDATA[" + texto.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def _contraste_en_linea(html_: str) -> str:
    """El <section class="contraste"> del sitio, con el estilo dentro."""
    return html_.replace('<section class="contraste">',
                         f'<section class="contraste" style="{ESTILO_CONTRASTE}">')


def cuerpo_de(d: plan.Dia) -> tuple[dict, str]:
    datos, texto = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))
    html_ = construir_sitio.md(texto)
    html_ = _contraste_en_linea(construir_sitio._marcar_contraste(html_))
    return datos, f'<div class="urok">{html_}</div>'


def titulo_de(d: plan.Dia) -> str:
    return f"Урок {d.numero}. {d.tema_ru}"


def categoria_de(cal: dict, d: plan.Dia) -> tuple[str, str]:
    u = plan.unidad_de(cal, d.semana)
    if u:
        return f"Тема {u['numero']}. {u['titulo_ru']}", f"tema-{u['numero']}"
    return "Подготовка к DELE", "dele"


def _item(*, titulo, nombre, contenido, post_id, fecha, tipo, estado, orden=0,
          autor="", categorias=(), etiquetas=()) -> str:
    g = fecha.strftime("%Y-%m-%d %H:%M:%S")
    terminos = "".join(
        f'\n    <category domain="category" nicename="{sax.quoteattr(c[1])[1:-1]}">{cdata(c[0])}</category>'
        for c in categorias)
    terminos += "".join(
        f'\n    <category domain="post_tag" nicename="{sax.quoteattr(babosa(e))[1:-1]}">{cdata(e)}</category>'
        for e in etiquetas)
    return f"""  <item>
    <title>{cdata(titulo)}</title>
    <dc:creator>{cdata(autor)}</dc:creator>
    <guid isPermaLink="false">espanol-desde-ruso-{tipo}-{post_id}</guid>
    <description></description>
    <content:encoded>{cdata(contenido)}</content:encoded>
    <excerpt:encoded>{cdata("")}</excerpt:encoded>
    <wp:post_id>{post_id}</wp:post_id>
    <wp:post_date>{cdata(g)}</wp:post_date>
    <wp:post_date_gmt>{cdata(g)}</wp:post_date_gmt>
    <wp:comment_status>{cdata("open")}</wp:comment_status>
    <wp:ping_status>{cdata("closed")}</wp:ping_status>
    <wp:post_name>{cdata(nombre)}</wp:post_name>
    <wp:status>{cdata(estado)}</wp:status>
    <wp:post_parent>0</wp:post_parent>
    <wp:menu_order>{orden}</wp:menu_order>
    <wp:post_type>{cdata(tipo)}</wp:post_type>
    <wp:post_password>{cdata("")}</wp:post_password>
    <wp:is_sticky>0</wp:is_sticky>{terminos}
  </item>
"""


def indice_html(cal: dict, escritas: list[plan.Dia]) -> str:
    """La página del índice.

    Hace falta porque un blog ordena por fecha descendente y un curso se lee del
    uno al cien: sin esta página, la portada de WordPress abre por la lección
    más nueva."""
    partes = ['<div class="urok"><p>Курс из 365 уроков по 30 минут. '
              'Уроки выходят по порядку — начните с первого.</p>']
    unidad = None
    for d in escritas:
        nombre, _ = categoria_de(cal, d)
        if nombre != unidad:
            partes.append(f"</ul>" if unidad else "")
            partes.append(f"<h2>{sax.escape(nombre)}</h2><ul>")
            unidad = nombre
        partes.append(f'<li><a href="/{babosa_de(d)}/">{sax.escape(titulo_de(d))}</a></li>')
    partes.append("</ul></div>")
    return "".join(partes)


def babosa_de(d: plan.Dia) -> str:
    return f"urok-{d.numero}"


def exportar(cal: dict, cfg: dict, destino: pathlib.Path, desde: dt.date | None = None) -> dict:
    escritas = construir_sitio.escritas(cal)
    autor = cfg.get("autor", {}).get("nombre", "") or "autor"
    dominio = cfg.get("dominio", "")
    # Una lección por día hacia atrás: la 1 es la más antigua, así el archivo
    # del blog y el orden del curso coinciden.
    desde = desde or dt.date.today() - dt.timedelta(days=len(escritas))

    categorias: dict[str, str] = {}
    for d in escritas:
        nombre, babosa_cat = categoria_de(cal, d)
        categorias[babosa_cat] = nombre

    cabecera_cats = "".join(
        f"  <wp:category><wp:term_id>{i + 2}</wp:term_id>"
        f"<wp:category_nicename>{cdata(b)}</wp:category_nicename>"
        f"<wp:category_parent>{cdata('')}</wp:category_parent>"
        f"<wp:cat_name>{cdata(n)}</wp:cat_name></wp:category>\n"
        for i, (b, n) in enumerate(categorias.items()))

    items = []
    publicadas = borradores = 0
    for i, d in enumerate(escritas):
        datos, contenido = cuerpo_de(d)
        revisada = bool(datos.get("revisado"))
        publicadas, borradores = (publicadas + 1, borradores) if revisada else (publicadas, borradores + 1)
        items.append(_item(
            titulo=titulo_de(d), nombre=babosa_de(d), contenido=contenido,
            post_id=100 + i, fecha=dt.datetime.combine(desde + dt.timedelta(days=i), dt.time(9, 0)),
            tipo="post", estado="publish" if revisada else "draft", autor=autor,
            categorias=[categoria_de(cal, d)],
            etiquetas=[d.nivel, plan.TIPO_RU[d.tipo], f"Неделя {d.semana}"]))

    items.append(_item(
        titulo="Все уроки", nombre="kurs", contenido=indice_html(cal, escritas),
        post_id=10, fecha=dt.datetime.now(), tipo="page", estado="publish", autor=autor))

    xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<!-- Generado por scripts/exportar_wordpress.py. WordPress: Herramientas → Importar → WordPress. -->
<rss version="2.0"
  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:wfw="http://wellformedweb.org/CommentAPI/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
  <title>{sax.escape(cfg.get('titulo', ''))}</title>
  <link>{sax.escape(dominio)}</link>
  <description>{sax.escape(cfg.get('lema', ''))}</description>
  <pubDate>{dt.datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
  <language>ru</language>
  <wp:wxr_version>1.2</wp:wxr_version>
  <wp:base_site_url>{sax.escape(dominio)}</wp:base_site_url>
  <wp:base_blog_url>{sax.escape(dominio)}</wp:base_blog_url>
  <wp:author><wp:author_id>1</wp:author_id>
    <wp:author_login>{cdata(babosa(autor))}</wp:author_login>
    <wp:author_email>{cdata(cfg.get('autor', {}).get('email', ''))}</wp:author_email>
    <wp:author_display_name>{cdata(autor)}</wp:author_display_name>
    <wp:author_first_name>{cdata('')}</wp:author_first_name>
    <wp:author_last_name>{cdata('')}</wp:author_last_name></wp:author>
{cabecera_cats}{''.join(items)}</channel>
</rss>
"""
    destino.mkdir(parents=True, exist_ok=True)
    destino.joinpath("curso-wordpress.xml").write_text(xml, encoding="utf-8")
    destino.joinpath("curso-wordpress.css").write_text(CSS_OPCIONAL, encoding="utf-8")
    return {"lecciones": len(escritas), "publicadas": publicadas,
            "borradores": borradores, "categorias": len(categorias)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--destino", type=pathlib.Path, default=SALIDA)
    a = p.parse_args(argv)
    r = exportar(plan.cargar(), construir_sitio.cargar_config(), a.destino)
    print(f"{r['lecciones']} lecciones en {a.destino / 'curso-wordpress.xml'}")
    print(f"  {r['publicadas']} se publican (revisadas) · {r['borradores']} entran como BORRADOR (sin revisar)")
    print(f"  {r['categorias']} categorías (una por unidad) · una página «Все уроки» con el índice")
    print("  WordPress: Herramientas → Importar → WordPress → subir el archivo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
