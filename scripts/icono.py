#!/usr/bin/env python3
"""El icono del sitio: la eñe, crema sobre terracota.

    .venv/bin/python scripts/icono.py --ver   # qué haría, sin escribir
    .venv/bin/python scripts/icono.py         # escribe docs/img/icono*.png

El sitio **no tenía ninguna marca**. Al quitar el nombre del autor el
2026-10-27 se quedó sin firma, y en la pestaña del navegador salía el globo
gris de «sin favicon». El 2026-10-29 el editor del CMP de AdSense pidió un
logotipo y hubo que dibujar uno; el profesor eligió la eñe sobre tres
candidatos probados **a 72 px**, que es como se ven en esa caja.

Por qué la eñe y no un monograma: a 32 px —el tamaño real de una pestaña— una
sigla de dos letras no se lee, y la eñe es la única marca que dice «español»
sin explicarse. (La tercera candidata era `A` + `Я`, y se desaconsejó: una `Я`
suelta junto a letras latinas es también el truco del «falso cirílico», que a
un lector ruso puede sonarle a burla.)

**El glifo se MIDE y se centra antes de dibujarlo.** Es la lección de la
tarjeta social y de los flyers del proyecto hermano: escrito desde una línea
base, el dibujo queda descolgado y con un hueco muerto abajo. A 512 px casi no
se nota; a 32 es lo único que se ve. Por lo mismo ocupa el 72 % del cuadrado:
más pequeño, en la pestaña no es una letra sino una mancha.

Es un comando aparte y deliberado, como el audio, los dibujos y la tarjeta:
construir el sitio tiene que ser barato, y esto abre una fuente del sistema
para un resultado que se versiona una vez y no cambia. `construir_sitio` solo
mira si los archivos ESTÁN.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import construir_sitio  # noqa: E402

DOCS = RAIZ / "docs"

# La paleta del sitio, la misma del CSS claro y la misma que copia
# `tarjeta_social.py`. PIL no lee variables CSS; si cambia allí, cambia aquí y
# el icono se vuelve a generar a mano.
ACENTO, CREMA = (176, 63, 38), (253, 251, 246)

# El cuadrado grande es el que se sube a AdSense y el que ve un navegador
# moderno; los otros dos son los tamaños que todavía se piden por su nombre.
# 180 es el de iOS («añadir a la pantalla de inicio») y 32 el de la pestaña.
TAMANOS = {"icono.png": 512, "icono-180.png": 180, "icono-32.png": 32}

# Los tres salen del MISMO dibujo grande, achicado. Dibujar directamente a 32
# da un icono peor y conviene saber por qué: el cuerpo de letra es un entero,
# así que a ese lado el ajuste cae un par de puntos por debajo del que toca y
# **la tilde se aplana hasta ser un guión**. Que es, justamente, lo único que
# distingue una eñe de una ene.
MAESTRO = 512

# La proporción del cuadrado que ocupa el lado mayor de la letra. Medida
# mirando el resultado a 32 px, no razonada: por debajo de 0,6 la eñe deja de
# leerse como letra y la tilde se come el poco borde que queda.
PARTE = 0.72

INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _fuente(tam: int):
    """Inter si está, y si no DejaVu. Las dos traen la eñe; es la misma
    elección que ya hizo la tarjeta social, para que las dos imágenes del
    sitio no salgan de dos tipografías distintas."""
    from PIL import ImageFont
    for ruta in (INTER, DEJAVU):
        try:
            return ImageFont.truetype(ruta, tam)
        except OSError:
            continue
    raise SystemExit("no hay ninguna fuente con eñe en este sistema")


def dibujar(lado: int):
    """El cuadrado con la eñe centrada por su TINTA, no por su caja de texto.

    La diferencia no es sutil y costó una vuelta: `textbbox` devuelve la caja
    de la LÍNEA —del ascendente al descendente—, no la del dibujo, así que
    ajustando a ella la letra sale al 49 % del cuadrado cuando se pidió el
    72 %. Aquí el glifo se dibuja suelto, se recorta a sus píxeles encendidos
    y se pega escalado: así el porcentaje es el de verdad y el centrado sale
    exacto (medido: 71 px arriba y 72 abajo, 135 a cada lado).

    Es la misma lección que la tarjeta social y los flyers del proyecto
    hermano: se mide antes de dibujar, y se mide lo que de verdad importa."""
    from PIL import Image, ImageDraw

    # Se dibuja en grande y suelto, sobre transparente, para poder recortar a
    # la tinta. El cuerpo es generoso a propósito: lo que manda es el recorte.
    cuerpo = max(64, lado * 2)
    capa = Image.new("L", (cuerpo * 2, cuerpo * 2), 0)
    ImageDraw.Draw(capa).text((cuerpo // 2, cuerpo // 2), "ñ",
                              font=_fuente(cuerpo), fill=255, anchor="la")
    glifo = capa.crop(capa.getbbox())

    objetivo = max(1, round(lado * PARTE))
    escala = objetivo / max(glifo.size)
    medida = (max(1, round(glifo.width * escala)), max(1, round(glifo.height * escala)))
    glifo = glifo.resize(medida, Image.LANCZOS)

    lienzo = Image.new("RGB", (lado, lado), ACENTO)
    lienzo.paste(Image.new("RGB", medida, CREMA),
                 ((lado - medida[0]) // 2, (lado - medida[1]) // 2), glifo)
    return lienzo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ver", action="store_true", help="dice qué haría, sin escribir")
    args = ap.parse_args()

    maestro = None if args.ver else dibujar(MAESTRO)
    for nombre, lado in TAMANOS.items():
        destino = DOCS / "img" / nombre
        if args.ver:
            print(f"{destino.relative_to(RAIZ)}  {lado}x{lado}"
                  f"{'  (ya está)' if destino.exists() else ''}")
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        from PIL import Image
        imagen = maestro if lado == MAESTRO else maestro.resize((lado, lado), Image.LANCZOS)
        imagen.save(destino, "PNG", optimize=True)
        print(f"{destino.relative_to(RAIZ)}  {lado}x{lado}  "
              f"{destino.stat().st_size // 1024 or 1} KB")
    if not args.ver:
        print("\nAhora: .venv/bin/python scripts/construir_sitio.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
