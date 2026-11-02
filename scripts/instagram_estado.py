#!/usr/bin/env python3
"""¿La página ya tiene una cuenta de Instagram conectada?

Instagram Graph API publica a través del `instagram_business_account` de la
PÁGINA de Facebook, no de la cuenta de Instagram por su cuenta. Esa conexión
se hace en Meta Business Suite (Configuración → Cuentas conectadas) y es un
enlace entre dos productos, no un permiso del token: **no se puede hacer
desde aquí**, ni con el mejor token del mundo.

Este script SOLO LEE: pregunta si la conexión existe y, si existe, el
nombre de usuario. No publica nada y no cambia nada.

Uso (lee FB_TOKEN y FB_PAGE_ID del entorno, igual que facebook_palabra.py):

    FB_TOKEN=... FB_PAGE_ID=... python3 scripts/instagram_estado.py
"""
from __future__ import annotations

import os
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import fb_token  # noqa: E402


def cuenta_instagram(pagina: str, token: str, graph=None) -> dict | None:
    """`None` si no hay ninguna conectada; si no, id, usuario y página."""
    graph = graph or fb_token.graph
    d = graph(pagina, fields="instagram_business_account,name",
              access_token=token)
    cuenta = d.get("instagram_business_account")
    if not cuenta:
        return None
    ig = graph(cuenta["id"], fields="username", access_token=token)
    return {"id": cuenta["id"], "usuario": ig.get("username", "?"),
            "pagina": d.get("name", "?")}


def main(argv=None) -> int:
    token = os.environ.get("FB_TOKEN", "").strip()
    pagina = os.environ.get("FB_PAGE_ID", "").strip()
    if not (token and pagina):
        print("faltan FB_TOKEN y/o FB_PAGE_ID en el entorno.")
        return 1

    c = cuenta_instagram(pagina, token)
    if c is None:
        print("Esta página NO tiene ninguna cuenta de Instagram conectada.")
        print("Se conecta en Meta Business Suite -> Configuración -> "
              "Cuentas conectadas, vinculando una cuenta de Instagram "
              "profesional (empresa o creador) a esta página.")
        return 1

    print("Página:    %s" % c["pagina"])
    print("Instagram: @%s" % c["usuario"])
    print("id de IG:  %s" % c["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
