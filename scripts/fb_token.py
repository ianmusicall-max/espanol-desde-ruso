#!/usr/bin/env python3
"""Convierte un token de usuario corto en un token de PÁGINA permanente.

Los tres pasos, que Facebook no hace solo:

  1. token de usuario corto (dura 1-2 h)  ->  token de usuario largo (60 días)
  2. token de usuario largo               ->  las páginas que administras
  3. el token de página derivado de uno largo **NO caduca**

Y un cuarto que no es opcional: **lo comprueba**. `debug_token` tiene que
contestar `expires_at: 0`; sin esa comprobación lo único que se sabe es que
Facebook devolvió algo, y un token de dos horas se ve igual que uno eterno
hasta que un día el canal deja de publicar.

Todo se lee del ENTORNO y nada se imprime: ni el token corto, ni el largo,
ni la clave de la app, ni el permanente. Lo único que sale por pantalla es
el id de cada página, su nombre, sus permisos y si caduca o no. El token se
escribe en el archivo que se le diga, para copiarlo de ahí a los secretos de
GitHub sin que pase por la pantalla ni por el historial de la shell.

Uso (en tu ordenador, que sí alcanza Meta):

    FB_APP_ID=... FB_APP_SECRET=... FB_TOKEN_CORTO=... \\
        python3 scripts/fb_token.py --guardar token.txt

El token corto se saca del Explorador de la API de Meta
(developers.facebook.com/tools/explorer) pidiendo los permisos
`pages_show_list` y `pages_manage_posts`.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com/v21.0"
# Lo que hace falta para publicar la palabra del día. `pages_show_list` es el
# que deja ver la lista de páginas, así que sin él el paso 2 vuelve vacío y
# parece que no administras ninguna.
PERMISOS = ("pages_show_list", "pages_manage_posts")


def graph(camino: str, **params) -> dict:
    url = "%s/%s?%s" % (GRAPH, camino, urllib.parse.urlencode(params))
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            cuerpo = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        texto = e.read().decode("utf-8", "replace")
        try:
            motivo = json.loads(texto)["error"].get("message", texto)
        except (ValueError, KeyError):
            motivo = texto
        # NUNCA se imprime la url: lleva el token y la clave dentro.
        raise SystemExit("Meta respondió %s: %s" % (e.code, motivo[:300]))
    except urllib.error.URLError as e:
        raise SystemExit("no se alcanza graph.facebook.com (%s).\n"
                         "Córrelo en tu ordenador: desde el contenedor de "
                         "Claude la política de red lo deniega." % e.reason)
    if "error" in cuerpo:
        raise SystemExit("Meta dijo que no: %s"
                         % str(cuerpo["error"].get("message", ""))[:300])
    return cuerpo


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--guardar", default="",
                    help="archivo donde dejar el token de la página")
    ap.add_argument("--pagina", default="",
                    help="id de la página, si administras varias")
    a = ap.parse_args(argv)

    app_id = os.environ.get("FB_APP_ID", "").strip()
    secreto = os.environ.get("FB_APP_SECRET", "").strip()
    corto = os.environ.get("FB_TOKEN_CORTO", "").strip()
    if not (app_id and secreto and corto):
        print("faltan FB_APP_ID, FB_APP_SECRET y/o FB_TOKEN_CORTO "
              "en el entorno.")
        return 1

    print("1. el token corto de usuario -> largo (60 días)")
    largo = graph("oauth/access_token", grant_type="fb_exchange_token",
                  client_id=app_id, client_secret=secreto,
                  fb_exchange_token=corto)["access_token"]

    print("2. las páginas que administras")
    paginas = graph("me/accounts", access_token=largo).get("data") or []
    if not paginas:
        print("   ninguna. ¿Pediste el permiso pages_show_list?")
        return 1

    elegida = None
    for pg in paginas:
        marca = " <-" if (a.pagina and pg.get("id") == a.pagina) else ""
        print("   %s  %s%s" % (pg.get("id"), pg.get("name", ""), marca))
        if a.pagina and pg.get("id") == a.pagina:
            elegida = pg
    if elegida is None:
        if a.pagina:
            print("   esa página no está en la lista.")
            return 1
        if len(paginas) > 1:
            print("\nadministras varias: repite con --pagina <id>.")
            return 1
        elegida = paginas[0]

    ficha = elegida["access_token"]
    print("\n3. comprobando que el de la página NO caduque")
    # Con `debug_token`, que es la única forma de preguntarlo: `/me/permissions`
    # con un token de PÁGINA devuelve «(#100) nonexisting field», porque `/me`
    # con un token de página ES la página y una página no tiene ese campo.
    datos = graph("debug_token", input_token=ficha,
                  access_token="%s|%s" % (app_id, secreto)).get("data", {})
    caduca = datos.get("expires_at")
    scopes = datos.get("scopes") or []
    print("   página   %s" % datos.get("profile_id", elegida.get("id")))
    print("   caduca   %s" % ("NO (expires_at: 0)" if caduca == 0
                              else "SÍ, en %s" % caduca))
    print("   permisos %s" % ", ".join(sorted(scopes)) or "(ninguno)")

    faltan = [x for x in PERMISOS if x not in scopes]
    if faltan:
        print("\n   FALTAN para publicar: %s" % ", ".join(faltan))
        print("   Vuelve al Explorador, tilda esos permisos y repite.")
    if caduca != 0:
        print("\n   El token NO es permanente. Suele ser que el paso 1 no "
              "se aplicó:\n   comprueba que el token corto sea de USUARIO y "
              "no de página.")
        return 1

    if a.guardar:
        destino = pathlib.Path(a.guardar)
        destino.write_text(ficha + "\n", encoding="utf-8")
        destino.chmod(0o600)
        print("\n   token guardado en %s (no se imprime)." % destino)
        print("   Cópialo de ahí a FB_TOKEN en los secretos de GitHub y "
              "borra el archivo.")
    else:
        print("\n   Repite con --guardar token.txt para tenerlo en un "
              "archivo:\n   así no pasa por la pantalla ni por el historial.")
    return 0 if not faltan else 1


if __name__ == "__main__":
    sys.exit(main())
