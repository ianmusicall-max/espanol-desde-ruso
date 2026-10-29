#!/usr/bin/env python3
"""La tarjeta que se ve al compartir el curso, hecha con sus propios dibujos.

    .venv/bin/python scripts/tarjeta_social.py --ver   # qué haría, sin escribir
    .venv/bin/python scripts/tarjeta_social.py         # escribe docs/img/tarjeta.png

El 2026-10-27 se pusieron los botones de compartir al pie de las 100 lecciones
—Telegram y WhatsApp, que son por donde un rusohablante fuera de Rusia manda
algo a un amigo— y el enlace llegaba **sin imagen**: las dos plataformas, y
también Facebook y VK, pintan la vista previa con `og:image`, y aquí no había
ninguna. Un enlace pelado en un chat se mira mucho menos que una tarjeta.

No se encarga fuera ni se dibuja a mano: se compone con los doce dibujos que ya
enseña la portada, que están pagados, son de la paleta de la casa y no los
tiene nadie más. Cero coste y la tarjeta se parece al sitio.

**Es un comando aparte y deliberado, como el audio y los dibujos.** Construir
el sitio tiene que ser barato y esto abre doce imágenes y una fuente del
sistema; además el resultado se versiona una vez y no cambia. `construir_sitio`
solo mira si el archivo ESTÁ: sin él no escribe `og:image`, que es mejor que
prometer una imagen que da 404.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import construir_sitio  # noqa: E402
import generar_imagenes  # noqa: E402

DOCS = RAIZ / "docs"
# En `img/` y no en la raíz porque es un dibujo más del curso, y así la
# política de «docs/img/ se versiona» vale para él sin ninguna excepción.
ARCHIVO = "img/tarjeta.png"

# La medida que piden Facebook, Telegram y WhatsApp: 1200x630 (1,91:1). Más
# chica se ve borrosa en pantallas densas; más grande, algunas no la cargan.
ANCHO, ALTO = 1200, 630

# La paleta del sitio, la misma del CSS claro. Escrita aquí porque PIL no lee
# variables CSS; si algún día cambia allí, cambia aquí, y la tarjeta se vuelve
# a generar a mano como el audio.
CREMA, TINTA, TENUE = (255, 255, 255), (16, 17, 19), (107, 112, 118)
ACENTO, LINEA, TARJETA = (176, 63, 38), (220, 221, 224), (244, 244, 245)

INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf"


def _fuente(grosor: str, tam: int):
    """Inter si está, y si no DejaVu. Las dos traen cirílico, que es lo único
    que no se puede dar por hecho: el título de la tarjeta está en ruso."""
    for ruta in (INTER.format(grosor),
                 DEJAVU.format("-Bold" if grosor != "Regular" else "")):
        try:
            from PIL import ImageFont
            return ImageFont.truetype(ruta, tam)
        except OSError:
            continue
    raise SystemExit("no hay ninguna fuente con cirílico en este sistema")


def _partir(dibujo, texto: str, fuente, ancho: int) -> list[str]:
    """El texto en los renglones que caben, sin partir palabras."""
    renglones, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if dibujo.textlength(prueba, font=fuente) <= ancho or not actual:
            actual = prueba
        else:
            renglones.append(actual)
            actual = palabra
    if actual:
        renglones.append(actual)
    return renglones


def palabras_con_dibujo(indice: dict) -> list[str]:
    """Los doce de la portada que de verdad tienen archivo.

    Los mismos que la portada y no otros: quien llega por el enlace compartido
    ve primero la tarjeta y enseguida la página, y que sean las mismas doce
    palabras hace que el sitio se reconozca."""
    return [p for p in construir_sitio.PORTADA_DIBUJOS
            if generar_imagenes.limpiar(p) in indice]


def componer(cfg, t, indice: dict, carpeta: pathlib.Path):
    from PIL import Image, ImageDraw

    lienzo = Image.new("RGB", (ANCHO, ALTO), CREMA)
    d = ImageDraw.Draw(lienzo)
    p = t["portada"]

    margen = 64
    ancho_util = ANCHO - 2 * margen

    # La franja de dibujos ABAJO y el texto arriba. Al revés, la vista previa
    # de WhatsApp —que a veces recorta a cuadrado— se comía el título, que es
    # lo único que no puede faltar.
    lado, hueco = 112, 16
    palabras = palabras_con_dibujo(indice)[: (ancho_util + hueco) // (lado + hueco)]

    fila_y = ALTO - margen - lado
    corte = fila_y - 40
    d.rectangle([0, corte, ANCHO, ALTO], fill=TARJETA)
    d.line([0, corte, ANCHO, corte], fill=LINEA, width=2)

    # Cada dibujo en su ficha con la esquina redonda, como en la vitrina de la
    # portada. No es adorno: el fondo de cada imagen es un crema ligeramente
    # distinto, y pegados a hueso esas diferencias se leen como rectángulos
    # sucios. Dentro de una ficha con borde se leen como fichas.
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, lado - 1, lado - 1],
                                              radius=14, fill=255)
    total = len(palabras) * lado + (len(palabras) - 1) * hueco
    x = (ANCHO - total) // 2
    for palabra in palabras:
        foto = Image.open(carpeta / indice[generar_imagenes.limpiar(palabra)])
        lienzo.paste(foto.convert("RGB").resize((lado, lado), Image.LANCZOS),
                     (x, fila_y), mascara)
        d.rounded_rectangle([x, fila_y, x + lado - 1, fila_y + lado - 1],
                            radius=14, outline=LINEA, width=2)
        x += lado + hueco

    # El texto se MIDE antes de dibujarlo y se centra en lo que queda. Escrito
    # de arriba abajo con una `y` que va creciendo, un título que ocupara dos
    # renglones dejaría el bloque descolgado y un hueco muerto encima de la
    # franja; así se acomoda solo.
    host = (cfg.get("dominio") or "").split("//")[-1].strip("/")
    bloques = [(_partir(d, p["titulo"], _fuente("Bold", 72), ancho_util),
                _fuente("Bold", 72), 84, TINTA, 0),
               (_partir(d, p["titulo2"], _fuente("SemiBold", 44), ancho_util),
                _fuente("SemiBold", 44), 56, ACENTO, 10),
               (_partir(d, p["lema"], _fuente("Regular", 34), ancho_util),
                _fuente("Regular", 34), 44, TENUE, 14)]
    if host:
        bloques.append(([host], _fuente("SemiBold", 30), 40, ACENTO, 22))

    alto = sum(antes + paso * len(renglones)
               for renglones, _f, paso, _c, antes in bloques)
    y = max(margen, (corte - alto) // 2)
    for renglones, fuente, paso, color, antes in bloques:
        y += antes
        for renglon in renglones:
            d.text((margen, y), renglon, font=fuente, fill=color)
            y += paso

    return lienzo


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ver", action="store_true", help="dice qué haría, sin escribir")
    p.add_argument("--destino", type=pathlib.Path, default=DOCS)
    a = p.parse_args(argv)

    cfg = construir_sitio.cargar_config()
    t = construir_sitio.cargar_textos()["ru"]
    indice = construir_sitio.indice_de_imagenes(a.destino)
    if not indice:
        print(f"no hay dibujos en {a.destino / 'img'}: "
              "primero scripts/generar_imagenes.py")
        return 1

    palabras = palabras_con_dibujo(indice)
    print(f"{len(indice)} dibujos · {len(palabras)} en la tarjeta")
    if a.ver:
        print(f"escribiría {a.destino / ARCHIVO} ({ANCHO}x{ALTO})")
        return 0

    lienzo = componer(cfg, t, indice, a.destino / "img")
    salida = a.destino / ARCHIVO
    salida.parent.mkdir(parents=True, exist_ok=True)
    # Aparte y renombrada, como el `.parcial` del audio y de los dibujos: una
    # escritura cortada a la mitad dejaría una imagen rota que las plataformas
    # cachean durante días.
    temporal = salida.with_suffix(".parcial")
    lienzo.save(temporal, "PNG", optimize=True)
    temporal.replace(salida)
    print(f"{salida}  ·  {salida.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
