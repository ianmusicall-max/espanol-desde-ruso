#!/usr/bin/env python3
"""Iguala el fondo de los 300 dibujos al crema de la página.

    .venv/bin/python scripts/igualar_dibujos.py --ver     # sólo mide
    .venv/bin/python scripts/igualar_dibujos.py           # los corrige

El generador devuelve cada dibujo sobre un crema parecido al de la web pero
nunca igual, y —lo que de verdad se ve— **distinto entre un dibujo y otro**:
medido, el libro está en (242,233,218) y el perro en (255,248,236), trece
puntos de diferencia. A 56 px, en la tabla de vocabulario, eso no se nota. A
96 px y en fila, que es como salen los seis de la portada, se lee como que
unas fichas están más sucias que otras. Lo vio el profesor comparando el móvil
con el escritorio.

**Cómo se mide el fondo, que es lo único delicado.** No con la mediana de la
banda del borde: ahí caen la sombra que el generador deja bajo el objeto y la
viñeta —los bordes de la imagen son más oscuros que el centro—, así que la
mediana tira hacia abajo y la corrección se queda corta justo en el centro,
que es donde se ve. Se toma el **percentil 70** de esa banda, o sea su parte
clara. Es la misma lección que el proyecto hermano aprendió con las tarjetas
de su carrusel.

Después se desplaza la imagen ENTERA por la diferencia. Mover sólo los píxeles
parecidos al fondo dejaría un halo en los bordes suavizados del dibujo, y el
desplazamiento global es de ocho a dieciocho puntos: en un rojo o en un verde
eso no se distingue a simple vista.

**Escribe aparte y renombra.** Si algo se corta a la mitad, lo que queda es un
`.parcial` y no un webp truncado que el sitio serviría como bueno. El nombre
NO cambia: es la llave del índice, y además así git guarda una versión más de
cada fichero y no un juego entero nuevo al lado del viejo.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "docs" / "img"
INDICE = CARPETA / "indice.json"

# Cuánto del borde se mira para saber cuál es el fondo, y con qué percentil.
BANDA = 12          # píxeles de cada lado
PERCENTIL = 70      # la parte CLARA de la banda: ver el docstring
MAXIMO = 40         # un desplazamiento mayor que esto no es un fondo: es el dibujo


def crema_de_la_pagina() -> tuple[int, int, int]:
    """El color de la FICHA, leído del CSS y no escrito a mano aquí.

    Se iguala a `--tarjeta` y no a `--papel` porque cada dibujo va dentro de su
    ficha, con su borde: el ojo compara el interior de una ficha con el de la
    de al lado. Igualándolos a la tarjeta, el dibujo y su ficha son el mismo
    color y el recuadro deja de encerrar una mancha.

    Se lee del CSS y no se escribe aquí: si algún día se cambia la paleta, los
    dibujos la siguen solos. Escrito dos veces, el día del cambio se arregla
    uno y el otro se queda viejo, que es la forma de fallo que más se repite en
    este proyecto. La PRIMERA aparición es la del tema claro; la segunda es la
    del oscuro, y los dibujos son opacos y claros en los dos temas."""
    sys.path.insert(0, str(RAIZ / "scripts"))
    import construir_sitio  # noqa: PLC0415
    m = re.search(r"--tarjeta:\s*#([0-9a-fA-F]{6})", construir_sitio.CSS)
    if not m:
        raise SystemExit("no encuentro --tarjeta en el CSS")
    h = m.group(1)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def fondo_de(im: Image.Image) -> tuple[int, int, int]:
    """El color del fondo: el percentil 70 de la banda del borde, por canal."""
    w, h = im.size
    borde = []
    pix = im.load()
    for x in range(w):
        for y in list(range(BANDA)) + list(range(h - BANDA, h)):
            borde.append(pix[x, y])
    for y in range(BANDA, h - BANDA):
        for x in list(range(BANDA)) + list(range(w - BANDA, w)):
            borde.append(pix[x, y])
    salida = []
    for c in range(3):
        valores = sorted(p[c] for p in borde)
        salida.append(valores[min(len(valores) - 1, len(valores) * PERCENTIL // 100)])
    return tuple(salida)  # type: ignore[return-value]


def igualar(ruta: pathlib.Path, objetivo: tuple[int, int, int], escribir: bool) -> dict:
    im = Image.open(ruta).convert("RGB")
    antes = fondo_de(im)
    salto = tuple(objetivo[c] - antes[c] for c in range(3))
    info = {"fichero": ruta.name, "antes": antes, "salto": salto}
    if max(abs(s) for s in salto) > MAXIMO:
        info["saltado"] = "diferencia demasiado grande: eso no es el fondo"
        return info
    if not any(salto):
        info["saltado"] = "ya estaba"
        return info
    if escribir:
        tabla = []
        for c in range(3):
            tabla += [min(255, max(0, v + salto[c])) for v in range(256)]
        nueva = im.point(tabla)
        parcial = ruta.with_suffix(".parcial")
        nueva.save(parcial, "WEBP", quality=88, method=6)
        parcial.replace(ruta)
        info["despues"] = fondo_de(Image.open(ruta).convert("RGB"))
    return info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ver", action="store_true", help="mide y no escribe")
    args = ap.parse_args(argv)

    if not INDICE.exists():
        print("no hay dibujos generados todavía")
        return 0
    objetivo = crema_de_la_pagina()
    nombres = sorted(set(json.loads(INDICE.read_text(encoding="utf-8")).values()))
    print(f"color de la ficha: {objetivo} · {len(nombres)} dibujos\n")

    peor_antes = peor_despues = 0
    tocados = 0
    for nombre in nombres:
        ruta = CARPETA / nombre
        if not ruta.exists():
            continue
        info = igualar(ruta, objetivo, escribir=not args.ver)
        d_antes = max(abs(s) for s in info["salto"])
        peor_antes = max(peor_antes, d_antes)
        if "despues" in info:
            d = max(abs(objetivo[c] - info["despues"][c]) for c in range(3))
            peor_despues = max(peor_despues, d)
            tocados += 1
        elif "saltado" in info and info["saltado"] != "ya estaba":
            print(f"  ! {nombre}: {info['saltado']} (fondo {info['antes']})")

    print(f"peor diferencia antes: {peor_antes} puntos")
    if args.ver:
        print("(--ver: no se ha escrito nada)")
    else:
        print(f"peor diferencia después: {peor_despues} puntos · {tocados} corregidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
