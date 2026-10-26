#!/usr/bin/env python3
"""Cambia el sitio a un dominio propio y dice qué poner en el DNS.

    .venv/bin/python scripts/poner_dominio.py espanoldesderuso.com

Hace tres cosas: escribe el dominio en `web/sitio.yaml`, reconstruye el sitio
—con lo que aparecen `CNAME` y las URL canónicas y el sitemap correctos— e
imprime los registros exactos que hay que crear en el registrador.

Con `--ver` solo enseña lo que haría.

Por qué un guion y no hacerlo a mano: el día de la compra hay que tocar el
YAML, acordarse de reconstruir y buscar las cuatro IP de GitHub Pages en su
documentación. Tres pasos en los que es fácil dejarse uno, y el síntoma de
dejarse el segundo es una web que parece bien y lleva el dominio viejo en las
etiquetas canónicas, el sitemap y el ads.txt.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import construir_sitio  # noqa: E402

# Las cuatro de GitHub Pages para un dominio sin «www» delante. Están en su
# documentación y cambian muy de vez en cuando: si el sitio no sale a las
# pocas horas, lo primero es cotejarlas con docs.github.com.
A_GITHUB = ("185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153")
AAAA_GITHUB = ("2606:50c0:8000::153", "2606:50c0:8001::153",
               "2606:50c0:8002::153", "2606:50c0:8003::153")

# Un dominio no es una URL: si se cuela «https://» o una barra, el CNAME sale
# mal y GitHub Pages no sirve nada, sin decir por qué.
VALIDO = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$")

GRATIS = (".github.io", ".netlify.app", ".vercel.app", ".wordpress.com",
          ".pages.dev", ".web.app", ".firebaseapp.com")


def comprobar(dominio: str) -> str:
    d = dominio.strip().lower()
    d = re.sub(r"^https?://", "", d).strip("/")
    if d.startswith("www."):
        raise SystemExit(f"pon el dominio sin «www.»: {d[4:]}\n"
                         "El «www» se configura aparte y apunta aquí.")
    if not VALIDO.match(d):
        raise SystemExit(f"«{dominio}» no parece un dominio. Ejemplo: espanoldesderuso.com")
    if d.endswith(GRATIS):
        raise SystemExit(f"«{d}» es un subdominio de otro: no es tuyo y AdSense pide uno propio.\n"
                         "Es justo lo que ya tenemos.")
    return d


def escribir(dominio: str, ruta: pathlib.Path = construir_sitio.CONFIG) -> str:
    """Solo la línea del dominio: el resto del YAML son comentarios que explican
    cada ajuste y los perdería una reescritura con yaml.dump."""
    texto = ruta.read_text(encoding="utf-8")
    nuevo, n = re.subn(r'^dominio:.*$', f'dominio: "https://{dominio}"', texto, count=1, flags=re.M)
    if n != 1:
        raise SystemExit(f"no encuentro la línea «dominio:» en {ruta}")
    ruta.write_text(nuevo, encoding="utf-8")
    return nuevo


def instrucciones(dominio: str) -> str:
    filas = "\n".join(f"    A      @      {ip}" for ip in A_GITHUB)
    filas6 = "\n".join(f"    AAAA   @      {ip}" for ip in AAAA_GITHUB)
    return f"""
En el registrador, en la zona DNS de {dominio}, crea:

{filas}
{filas6}
    CNAME  www    ianmusicall-max.github.io.

Después, en GitHub:

  1. Settings → Pages → Custom domain → {dominio} → Save
  2. Espera a que diga «DNS check successful» (de minutos a 24 horas)
  3. Marca «Enforce HTTPS» cuando se deje: el certificado lo saca GitHub solo

Si el registrador es Cloudflare, los registros tienen que ir en gris
(«DNS only») y NO en naranja: con el proxy puesto, GitHub no puede validar el
dominio para emitir el certificado y «Enforce HTTPS» se queda apagado.

Cuando esté, el curso pasa de
  ianmusicall-max.github.io/espanol-desde-ruso/semana-01/dia-1.html
a
  {dominio}/semana-01/dia-1.html

y ads.txt queda en {dominio}/ads.txt, que es donde AdSense lo busca.
"""


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("dominio", help="sin https:// y sin www, p. ej. espanoldesderuso.com")
    p.add_argument("--ver", action="store_true", help="enseña lo que haría y no toca nada")
    a = p.parse_args(argv)

    dominio = comprobar(a.dominio)
    if a.ver:
        print(f"Dejaría en web/sitio.yaml:  dominio: \"https://{dominio}\"")
        print(instrucciones(dominio))
        return 0

    escribir(dominio)
    print(f"web/sitio.yaml → https://{dominio}")
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "construir_sitio.py")], check=True)
    print(instrucciones(dominio))
    print("Falta el último paso: git add -A && git commit && git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
