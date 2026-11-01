#!/usr/bin/env python3
"""La palabra del día en la página de Facebook del curso.

Es el mismo contenido que el canal de Telegram —la misma palabra, la misma
tarjeta, el mismo vídeo— publicado en otro sitio. Nada se escribe dos veces:
el texto, la tarjeta y el mp4 los arman `palabra_del_dia.py` y
`tarjeta_palabra.py`, y aquí solo se habla con Meta.

**El mismo día sale lo mismo en las dos redes.** La alternancia la decide
`palabra_del_dia.toca_video(n)`, una sola función: si cada red eligiera por
su cuenta, un día Telegram enseñaría el vídeo y Facebook la foto y nadie
sabría por qué.

Lo que hace falta, y mientras no esté no publica nada:

    FB_TOKEN     el token de la PÁGINA (no el de usuario). Va en los
                 secretos de GitHub, nunca en el repositorio.
    FB_PAGE_ID   el id de la página, que es público.

Uso:
    facebook_palabra.py            enseña lo que publicaría, sin publicar
    facebook_palabra.py --publicar publica de verdad
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
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
import palabra_del_dia  # noqa: E402

GRAPH = "https://graph.facebook.com/v21.0"
# Las subidas de vídeo van a OTRO host, que es el que Meta documenta para
# esto. Con el de siempre contesta «(#100) No permission to publish the
# video», que es un mensaje de permisos para algo que no lo es: el token
# tenía `publish_video` y `pages_manage_posts`, comprobados con
# `debug_token`. Pasó el 2026-11-01, el día que se encendió la página.
GRAPH_VIDEO = "https://graph-video.facebook.com/v21.0"
VAR_TOKEN = "FB_TOKEN"
VAR_PAGINA = "FB_PAGE_ID"


class FacebookDijoQueNo(RuntimeError):
    pass


def texto(p: dict, t: dict, dominio: str) -> str:
    """El cuerpo del post, en texto pelado.

    No es el de Telegram con las etiquetas quitadas: Facebook no entiende
    HTML y un `<b>` saldría literal. Lo que sí conserva es el orden —palabra,
    traducción, ejemplo, enlace, etiquetas— para que las dos redes se lean
    igual.

    El enlace va DESNUDO y no detrás de una palabra: Facebook lo vuelve
    pulsable solo, y además así se ve a dónde lleva antes de tocarlo.
    """
    lineas = ["%s — %s" % (p["es"], p["ru"])]
    if p.get("ejemplo"):
        lineas += ["", p["ejemplo"]]
    d = p["dia"]
    if dominio:
        url = "%s/semana-%02d/dia-%d.html" % (dominio, d.semana, d.dia)
        lineas += ["", "%s %d — %s" % (t["urok"], d.numero, url)]
    else:
        lineas += ["", "%s %d" % (t["urok"], d.numero)]
    lineas += ["", " ".join(t["etiquetas"])]
    return "\n".join(lineas)


def _pedido(p: dict, cuerpo: str, pagina: str, n: int,
            taller: pathlib.Path) -> tuple[str, dict, dict]:
    """Qué endpoint toca y con qué. `(camino, campos, archivos)`.

    La tarjeta manda, como en Telegram. Si no se pudo dibujar, el post sale
    igual con el texto solo: una página muda ese día es peor que una sin
    foto, y es la misma red que el canal.
    """
    tarjeta = palabra_del_dia._tarjeta(p, taller)
    if tarjeta is None:
        return "%s/feed" % pagina, {"message": cuerpo}, {}

    if p.get("mp3") and palabra_del_dia.toca_video(n):
        import tarjeta_palabra

        voz = construir_sitio.DOCS / "audio" / ("%s.mp3" % p["mp3"])
        clip = tarjeta_palabra.video(tarjeta, voz, taller / "palabra.mp4")
        if clip is not None:
            # `description` y no `caption`: en /videos el texto del post se
            # llama así. Con el nombre de /photos, Facebook lo acepta y lo
            # TIRA, y el vídeo sale sin una palabra.
            return ("%s/videos" % pagina,
                    {"description": cuerpo, "title": p["es"]},
                    {"source": clip})

    return "%s/photos" % pagina, {"caption": cuerpo}, {"source": tarjeta}


def _enviar(camino: str, campos: dict, archivos: dict, token: str) -> dict:
    datos, tipo = palabra_del_dia._multipart(
        dict(campos, access_token=token), archivos)
    base = GRAPH_VIDEO if camino.endswith("/videos") else GRAPH
    pet = urllib.request.Request("%s/%s" % (base, camino), data=datos,
                                 headers={"Content-Type": tipo})
    try:
        with urllib.request.urlopen(pet, timeout=180) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # El cuerpo trae el motivo de Meta, que es lo único que sirve; el
        # código solo dice que algo salió mal. Y NUNCA se imprime la URL ni
        # los campos, que llevan el token dentro.
        cuerpo = e.read().decode("utf-8", "replace")
        try:
            motivo = json.loads(cuerpo)["error"].get("message", cuerpo)
        except (ValueError, KeyError):
            motivo = cuerpo
        raise FacebookDijoQueNo("Meta respondió %s: %s"
                                % (e.code, motivo[:300])) from None


def de_quien_es(token: str) -> str:
    """A quién pertenece el token, preguntado a Meta: `id (nombre)`.

    Solo se pregunta cuando algo YA falló, y existe por un motivo concreto:
    un token de USUARIO y un token de página al que le falta un permiso
    contestan errores que se parecen —«No permission to publish the video»,
    «publish_actions has been deprecated»— y desde fuera se ven iguales.
    Con `/me`, un token de página ES la página y devuelve su id; uno de
    usuario devuelve a la persona. Eso lo separa de una vez.

    Pasó el 2026-11-01: los dos tokens empiezan por las mismas quince
    letras y el guardado en los secretos era el de usuario.
    """
    try:
        url = ("%s/me?fields=id,name&access_token=%s"
               % (GRAPH, urllib.parse.quote(token)))
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
        return "%s (%s)" % (d.get("id", "?"), d.get("name", "?"))
    except Exception:
        # Es un diagnóstico, no un paso del trabajo: si tampoco se puede
        # preguntar esto, lo que importa sigue siendo el error de arriba.
        return ""


def publicar(p: dict, cuerpo: str, token: str, pagina: str, n: int = 1,
             enviar=None) -> dict:
    """Publica y devuelve lo que contestó Meta.

    `enviar` existe para probar la FORMA del pedido sin red, que es lo único
    comprobable desde el contenedor donde se escribió esto:
    `graph.facebook.com` no se alcanza —lo deniega la política de red— y por
    eso esto corre en GitHub Actions, como el canal.
    """
    import tempfile

    def manda(camino, campos, archivos):
        for nombre, ruta in archivos.items():
            if not ruta.exists():
                raise FileNotFoundError("falta %s (%s)" % (ruta, nombre))
        if enviar is not None:
            return enviar(camino, campos, archivos)
        return _enviar(camino, campos, archivos, token)

    with tempfile.TemporaryDirectory() as tmp:
        taller = pathlib.Path(tmp)
        camino, campos, archivos = _pedido(p, cuerpo, pagina, n, taller)
        try:
            return manda(camino, campos, archivos)
        except FacebookDijoQueNo as e:
            if not camino.endswith("/videos"):
                raise
            # El vídeo es el adorno; la palabra del día es el post. Si Meta
            # no lo quiere, sale la MISMA tarjeta como foto antes que no
            # salir nada, y el motivo queda escrito en el registro. Un día
            # sin publicar no se recupera; uno sin voz, sí.
            tarjeta = palabra_del_dia._tarjeta(p, taller)
            if tarjeta is None:
                raise
            print("el vídeo no se pudo (%s)\n  -> va la tarjeta como foto"
                  % e)
            return manda("%s/photos" % pagina, {"caption": cuerpo},
                         {"source": tarjeta})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--publicar", action="store_true",
                    help="publica de verdad")
    ap.add_argument("--dia", help="la fecha a publicar (AAAA-MM-DD)")
    ap.add_argument("--numero", type=int, help="salta la fecha y pide la N")
    a = ap.parse_args(argv)

    cfg = construir_sitio.cargar_config()
    t = construir_sitio.cargar_textos()["canal"]
    lista = palabra_del_dia.palabras(cfg)

    if a.numero:
        n = a.numero
    else:
        desde = (cfg.get("telegram") or {}).get("desde")
        if not desde:
            print("falta `telegram.desde` en web/sitio.yaml: enseño la 1.")
            n = 1
        else:
            fecha = (dt.date.fromisoformat(a.dia) if a.dia
                     else dt.date.today())
            n = palabra_del_dia.numero_del_dia(
                fecha, dt.date.fromisoformat(str(desde)))

    p = palabra_del_dia.del_dia(lista, n)
    if p is None:
        print("la publicación %d no existe: el canal tiene %d."
              % (n, len(lista)))
        return 1

    cuerpo = texto(p, t, (cfg.get("dominio") or "").rstrip("/"))
    token = os.environ.get(VAR_TOKEN)
    pagina = os.environ.get(VAR_PAGINA)

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        camino, campos, archivos = _pedido(
            p, cuerpo, pagina or "{PAGINA}", n, pathlib.Path(tmp))
        print("publicación %d de %d · %s" % (n, len(lista), camino))
        print("-" * 60)
        print(cuerpo)
        print("-" * 60)
        for k, ruta in archivos.items():
            print("  %-8s %s (%d KB)"
                  % (k, "✓" if ruta.exists() else "FALTA",
                     ruta.stat().st_size // 1024 if ruta.exists() else 0))
        if not archivos:
            print("  (sin tarjeta: sale como texto)")

    if not a.publicar:
        return 0
    if not token or not pagina:
        print("\nfaltan %s y/o %s: no se publica nada."
              % (VAR_TOKEN, VAR_PAGINA))
        return 1

    try:
        r = publicar(p, cuerpo, token, pagina, n)
    except (FacebookDijoQueNo, FileNotFoundError) as e:
        print("\n%s" % e)
        if isinstance(e, FacebookDijoQueNo):
            quien = de_quien_es(token)
            if quien:
                print("  el token guardado es de %s" % quien)
                if not quien.startswith(pagina + " "):
                    print("  ...y la página es %s: eso es un token de "
                          "USUARIO, no el de la página." % pagina)
        return 1
    ident = r.get("post_id") or r.get("id") or str(r)[:120]
    print("\npublicado en la página: %s" % ident)
    return 0


if __name__ == "__main__":
    sys.exit(main())
