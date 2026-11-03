#!/usr/bin/env python3
"""La palabra del día en Instagram.

Es el MISMO contenido que Facebook y Telegram, publicado en un tercer
sitio. Nada se escribe dos veces: la palabra, la traducción y el ejemplo
salen de `palabra_del_dia.py`, el texto del post de `facebook_palabra.texto`
—Instagram lee caption plano igual que Facebook— y la tarjeta de
`tarjeta_palabra.componer`, la misma que dibuja el canal.

Dos cosas que Instagram pide y las otras dos redes no:

1. **Una URL pública, nunca un archivo subido.** `/photos` de Facebook
   admite `source` con el archivo; el `/media` de Instagram solo admite
   `image_url`, y va a buscarla él mismo. Por eso esto se divide en dos
   pasos —dibujar y publicar— con un paso de workflow en el medio que sube
   la tarjeta a una *release* del propio repositorio (`gh release upload`,
   la misma receta que ya usa la baraja de Anki) y le da su URL.

2. **La proporción.** Instagram rechaza una imagen más ancha que 1,91:1, y
   la tarjeta más corta del canal (480 px de alto sobre 1080 de ancho) es
   2,25:1 —son ocho de cada nueve días, los que no llevan dibujo—. Se le
   añade aire del MISMO crema del fondo, arriba y abajo, hasta llegar al
   límite: el contenido no cambia de tamaño, solo el lienzo que lo rodea.

Lo que hace falta, y mientras no esté no publica nada:

    FB_TOKEN     el mismo token de página que usa Facebook.
    FB_PAGE_ID   la misma página: Instagram se publica a través de la
                 cuenta de Instagram CONECTADA a esa página, no aparte.

Uso:
    instagram_palabra.py --numero-de-hoy          solo el número, nada más
    instagram_palabra.py --dibujar card.jpg        dibuja la tarjeta apta
    instagram_palabra.py --publicar URL            publica de verdad
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ))

import construir_sitio  # noqa: E402
import facebook_palabra  # noqa: E402
import instagram_estado  # noqa: E402
import palabra_del_dia  # noqa: E402
import tarjeta_palabra  # noqa: E402

GRAPH = facebook_palabra.GRAPH
VAR_TOKEN = facebook_palabra.VAR_TOKEN
VAR_PAGINA = facebook_palabra.VAR_PAGINA

# Instagram no publica una imagen MÁS ANCHA que esto (ancho:alto). Es el
# único límite que de verdad golpea a esta tarjeta: por abajo (4:5, más
# alta que ancha) nunca se llega, porque el ancho está fijo en 1080 y el
# alto nunca baja de 480.
RATIO_MAXIMA = 1.91


class InstagramDijoQueNo(RuntimeError):
    pass


def _numero(cfg: dict, numero: int | None, dia: str) -> int:
    if numero:
        return numero
    desde = (cfg.get("telegram") or {}).get("desde")
    if not desde:
        return 1
    fecha = dt.date.fromisoformat(dia) if dia else dt.date.today()
    return palabra_del_dia.numero_del_dia(
        fecha, dt.date.fromisoformat(str(desde)))


def tarjeta_apta(p: dict, dominio: str, urok: str):
    """La MISMA tarjeta del canal, con aire si hace falta para Instagram.

    `componer` mide el contenido y nunca se sale por abajo de 1:1, pero
    tampoco sabe de Instagram: una palabra sin ejemplo ni dibujo da un
    lienzo de 480 px de alto, 2,25:1, por encima del tope de Instagram. El
    aire se reparte arriba y abajo y es del color del FONDO de la tarjeta,
    no un borde: a simple vista no se nota que se añadió nada.
    """
    from PIL import Image

    imagen = tarjeta_palabra.componer(p, dominio, urok)
    ancho, alto = imagen.size
    minimo = math.ceil(ancho / RATIO_MAXIMA)
    if alto >= minimo:
        return imagen
    fondo = Image.new("RGB", (ancho, minimo), tarjeta_palabra.BLANCO)
    fondo.paste(imagen, (0, (minimo - alto) // 2))
    return fondo


def dibujar(p: dict, destino: pathlib.Path, dominio: str, urok: str):
    """Escribe la tarjeta en JPEG. Devuelve el camino, o None si no se pudo.

    JPEG y no PNG: Instagram la va a comprimir de todos modos, y así el
    archivo que sube la *release* pesa una fracción. **Falla seguro**, como
    `tarjeta_palabra.dibujar`: sin fuentes con cirílico o sin PIL, no hay
    tarjeta y ese día Instagram se saltea solo —el canal y Facebook, que no
    dependen de esto, publican igual.
    """
    try:
        imagen = tarjeta_apta(p, dominio, urok).convert("RGB")
        destino.parent.mkdir(parents=True, exist_ok=True)
        imagen.save(destino, "JPEG", quality=90, optimize=True)
    except (OSError, SystemExit, ImportError, ValueError):
        return None
    return destino


def _post(camino: str, token: str, **params) -> dict:
    """POST a la Graph API, con los parámetros en la URL y el cuerpo vacío.

    Es el mismo estilo que `fb_token.graph` —que ya está probado contra
    Meta de verdad— y evita depender de un `Content-Type` por defecto que
    `urllib` no pone solo. Nunca se imprime la URL ni los parámetros:
    llevan el token dentro, y es el mismo cuidado que
    `facebook_palabra._enviar`.
    """
    url = "%s/%s?%s" % (GRAPH, camino,
                        urllib.parse.urlencode(dict(params,
                                                     access_token=token)))
    pet = urllib.request.Request(url, data=b"", method="POST")
    try:
        with urllib.request.urlopen(pet, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode("utf-8", "replace")
        try:
            motivo = json.loads(cuerpo)["error"].get("message", cuerpo)
        except (ValueError, KeyError):
            motivo = cuerpo
        raise InstagramDijoQueNo("Meta respondió %s: %s"
                                 % (e.code, motivo[:300])) from None


def publicar(ig_id: str, cuerpo: str, imagen_url: str, token: str,
             post=None) -> dict:
    """Los dos pasos que Meta exige: crear el contenedor y publicarlo.

    `post` existe para probar la FORMA del pedido sin red —lo único
    comprobable desde el contenedor donde se escribió esto—, igual que el
    `enviar=` de `facebook_palabra.publicar`.
    """
    post = post or (lambda camino, **p: _post(camino, token, **p))
    contenedor = post("%s/media" % ig_id, image_url=imagen_url,
                      caption=cuerpo)
    creation_id = contenedor.get("id")
    if not creation_id:
        raise InstagramDijoQueNo("Meta no devolvió un id de contenedor: %s"
                                 % contenedor)
    return post("%s/media_publish" % ig_id, creation_id=creation_id)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--numero-de-hoy", action="store_true",
                    help="imprime SOLO el número que toca, nada más")
    ap.add_argument("--dibujar", metavar="RUTA",
                    help="dibuja la tarjeta apta para Instagram ahí")
    ap.add_argument("--publicar", metavar="URL",
                    help="publica de verdad, con esta imagen ya alojada")
    ap.add_argument("--numero", type=int, help="salta la fecha y pide la N")
    ap.add_argument("--dia", default="", help="AAAA-MM-DD, por defecto hoy")
    a = ap.parse_args(argv)

    cfg = construir_sitio.cargar_config()
    t = construir_sitio.cargar_textos()["canal"]
    lista = palabra_del_dia.palabras(cfg)
    n = _numero(cfg, a.numero, a.dia)
    p = palabra_del_dia.del_dia(lista, n)
    if p is None:
        print("la publicación %d no existe: el canal tiene %d."
              % (n, len(lista)))
        return 1

    if a.numero_de_hoy:
        print(n)
        return 0

    dominio = (cfg.get("dominio") or "").rstrip("/")

    if a.dibujar:
        hecho = dibujar(p, pathlib.Path(a.dibujar), dominio, t["urok"])
        if hecho is None:
            print("no se pudo dibujar (¿faltan fuentes con cirílico?)")
            return 1
        print("publicación %d · %s -> %s (%d KB)"
              % (n, p["es"], hecho, hecho.stat().st_size // 1024))
        return 0

    if a.publicar:
        token = os.environ.get(VAR_TOKEN, "").strip()
        pagina = os.environ.get(VAR_PAGINA, "").strip()
        if not (token and pagina):
            print("faltan %s y/o %s: no se publica nada."
                  % (VAR_TOKEN, VAR_PAGINA))
            return 1
        cuenta = instagram_estado.cuenta_instagram(pagina, token)
        if cuenta is None:
            print("esta página no tiene ninguna cuenta de Instagram "
                  "conectada todavía.")
            return 1
        cuerpo = facebook_palabra.texto(p, t, dominio)
        try:
            r = publicar(cuenta["id"], cuerpo, a.publicar, token)
        except InstagramDijoQueNo as e:
            print("\n%s" % e)
            quien = facebook_palabra.de_quien_es(token)
            if quien:
                print("  el token guardado es de %s" % quien)
            return 1
        print("publicado en @%s: %s" % (cuenta["usuario"], r.get("id", r)))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
