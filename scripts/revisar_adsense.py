#!/usr/bin/env python3
"""Qué le falta al sitio para que AdSense lo apruebe. SOLO LEE.

    .venv/bin/python scripts/revisar_adsense.py

Google no publica una lista cerrada de requisitos, así que esto no promete una
aprobación: separa lo que SÍ se puede comprobar desde aquí —contenido, páginas
obligatorias, enlaces rotos, móvil— de lo que depende de una decisión o de un
pago, para no mandar una solicitud con un fallo evitable dentro y esperar un
mes a que lo digan ellos.

Cada renglón dice una de tres cosas:

    LISTO    comprobado contra el sitio construido
    FALTA    lo bloquea de verdad, y se sabe por qué
    MIRAR    no se puede comprobar desde aquí: lo tienes que ver tú
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from urllib.parse import unquote, urldefrag

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import construir_sitio  # noqa: E402
import plan  # noqa: E402

# Por debajo de esto una página parece un esqueleto, que es lo que Google llama
# «contenido de poco valor» y la causa de rechazo más repetida en sitios nuevos.
MINIMO_PALABRAS = 250


def _texto(html_: str) -> str:
    cuerpo = re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", html_)
    cuerpo = re.sub(r"(?s)<header\b.*?</header>|<footer\b.*?</footer>", " ", cuerpo)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", cuerpo)).strip()


def enlaces_rotos(docs: pathlib.Path) -> list[tuple[str, str]]:
    """Un enlace interno que no lleva a ninguna parte.

    Importa más de lo que parece: el revisor de AdSense navega el sitio a mano,
    y una navegación que se rompe es «mala experiencia de usuario», que es una
    de las causas de rechazo con nombre propio."""
    rotos = []
    for pagina in sorted(docs.rglob("*.html")):
        html_ = pagina.read_text(encoding="utf-8")
        for destino in re.findall(r'href="([^"]+)"', html_):
            destino = urldefrag(destino)[0]
            if not destino or destino.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            objetivo = (pagina.parent / unquote(destino)).resolve()
            if not objetivo.exists():
                rotos.append((str(pagina.relative_to(docs)), destino))
    return rotos


def revisar(docs: pathlib.Path, cfg: dict, cal: dict) -> list[tuple[str, str, str]]:
    filas: list[tuple[str, str, str]] = []
    def di(estado, titulo, detalle=""):
        filas.append((estado, titulo, detalle))

    host = (cfg.get("dominio") or "").split("//")[-1].split("/")[0]
    ruta = (cfg.get("dominio") or "").split("//")[-1]
    propio = bool(host) and not host.endswith((".github.io", ".netlify.app", ".vercel.app",
                                               ".wordpress.com", ".pages.dev", ".web.app"))

    # --- lo que sí se puede comprobar ---
    escritas = construir_sitio.escritas(cal)
    paginas = sorted(docs.rglob("*.html"))
    palabras = sum(len(_texto(p.read_text(encoding="utf-8")).split()) for p in paginas)
    di("LISTO", f"{len(escritas)} lecciones originales, {palabras:,} palabras en {len(paginas)} páginas"
       .replace(",", " "),
       "contenido propio y en cantidad: es lo que más pesa y lo tienes")

    flacas = [p.relative_to(docs) for p in paginas
              if len(_texto(p.read_text(encoding="utf-8")).split()) < MINIMO_PALABRAS]
    if flacas:
        di("MIRAR", f"{len(flacas)} páginas con menos de {MINIMO_PALABRAS} palabras",
           ", ".join(str(x) for x in flacas[:4]) + (" …" if len(flacas) > 4 else ""))
    else:
        di("LISTO", f"ninguna página baja de {MINIMO_PALABRAS} palabras",
           "«contenido de poco valor» es el rechazo más común en sitios nuevos")

    for nombre, que in (("privacy.html", "política de privacidad"),
                        ("o-kurse.html", "página «sobre»"),
                        ("kontakt.html", "página de contacto")):
        di("LISTO" if (docs / nombre).exists() else "FALTA", f"{que} ({nombre})")

    correo = (cfg.get("autor") or {}).get("email") or ""
    if correo:
        di("LISTO", "hay una forma de contacto", correo)
    else:
        di("FALTA", "la página de contacto no da ninguna forma de contactar",
           "AdSense pide una. Rellena autor.email en web/sitio.yaml, o pon un formulario")

    rotos = enlaces_rotos(docs)
    if rotos:
        di("FALTA", f"{len(rotos)} enlaces internos rotos",
           "; ".join(f"{a} → {b}" for a, b in rotos[:3]))
    else:
        di("LISTO", "ningún enlace interno roto",
           "el revisor navega el sitio a mano; una navegación rota es causa de rechazo")

    sin_movil = [p.relative_to(docs) for p in paginas
                 if 'name="viewport"' not in p.read_text(encoding="utf-8")]
    di("FALTA" if sin_movil else "LISTO",
       "todas las páginas se adaptan al móvil" if not sin_movil else f"{len(sin_movil)} páginas sin viewport")

    di("LISTO" if (docs / "sitemap.xml").exists() else "MIRAR", "sitemap.xml",
       "ayuda a que Google encuentre las 100 lecciones")

    # --- lo que no depende del código ---
    if propio:
        di("LISTO", f"el dominio es tuyo: {host}")
        di("LISTO" if (docs / "ads.txt").exists() else "FALTA", "ads.txt en la raíz del dominio",
           "" if (docs / "ads.txt").exists() else "se escribe solo al poner adsense.cliente")
    else:
        di("FALTA", f"el dominio no es tuyo: {host or '(sin dominio)'}",
           "es lo único de esta lista que cuesta dinero: unos 10-15 USD al año")
        if "/" in ruta.rstrip("/"):
            di("FALTA", f"el sitio cuelga de una ruta, no de la raíz: /{ruta.split('/', 1)[1]}",
               "ads.txt tiene que estar en la raíz del dominio y ahí no puede estar")

    if construir_sitio.hay_anuncios(cfg):
        di("MIRAR", "el CMP de la UE",
           "la banda de cookies de aquí NO es un CMP certificado; el gratis de Google "
           "está en AdSense → Privacidad y mensajes")

    di("MIRAR", "que la web cargue de verdad en internet",
       f"abre {cfg.get('dominio') or '(sin dominio)'} en el móvil; "
       "desde aquí no se puede comprobar")

    return filas


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--docs", type=pathlib.Path, default=construir_sitio.DOCS)
    a = p.parse_args(argv)
    if not a.docs.is_dir():
        print(f"no existe {a.docs}: corre antes scripts/construir_sitio.py")
        return 1

    filas = revisar(a.docs, construir_sitio.cargar_config(), plan.cargar())
    marca = {"LISTO": "✓", "FALTA": "✗", "MIRAR": "?"}
    for estado, titulo, detalle in filas:
        print(f"  {marca[estado]} {estado:5}  {titulo}")
        if detalle:
            print(f"              {detalle}")
    faltan = sum(1 for e, _, _ in filas if e == "FALTA")
    print()
    print(f"{sum(1 for e, _, _ in filas if e == 'LISTO')} listo · {faltan} falta · "
          f"{sum(1 for e, _, _ in filas if e == 'MIRAR')} para mirar tú")
    if faltan:
        print("Solicitar el alta igual no cuesta nada ni penaliza: se puede volver a pedir.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
