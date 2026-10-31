#!/usr/bin/env python3
"""La tarjeta de la palabra del día, para el canal de Telegram.

Dibuja una imagen con la palabra española, su traducción rusa, la frase de
ejemplo y —cuando la palabra lo tiene— su dibujo. Es PIL: **cero API y cero
céntimos**, como las réplicas del proyecto hermano.

Existe porque el canal se leía como texto. De las 2.984 palabras, 2.883
tienen voz y el mensaje sale como reproductor de audio; el dibujo, que solo
tienen 263, iba de carátula de 320 px y no se veía. O sea que de los 300
dibujos pagados el canal no enseñaba ninguno en grande, y la rama que manda
una foto (`sendPhoto`) **no corría nunca**: es el defecto que este proyecto
documenta una y otra vez, código escrito al que nadie llega.

La tarjeta se dibuja al vuelo, una por día, y NO se versiona: son 2.984
imágenes que nadie va a mirar dos veces, y el repositorio ya carga con los
audios y los dibujos.

Uso:
    tarjeta_palabra.py --ver salida.png    dibuja la de hoy y la deja ahí
"""
import argparse
import datetime as dt
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ))

import construir_sitio  # noqa: E402
import tarjeta_social  # noqa: E402

# El ANCHO es fijo y el ALTO se calcula, y eso no es un detalle: solo 263 de
# las 2.984 palabras tienen dibujo, asi que una tarjeta cuadrada dejaria al
# 88 % del canal con medio lienzo en blanco —peor que el mensaje de texto que
# esto viene a reemplazar—. Telegram respeta la proporcion y la pinta al
# ancho del mensaje, de modo que una tarjeta baja se ve igual de grande y sin
# hueco muerto. Es la misma idea que el ancho de la foto en `beneficios` del
# proyecto hermano: una cuenta y no un numero.
ANCHO = 1080
MARGEN = 84
# Los topes: por debajo del minimo la tarjeta se lee como una banderita y por
# encima del maximo Telegram la recorta en la vista del canal.
ALTO_MINIMO, ALTO_MAXIMO = 480, 1080

# La paleta sale de la tarjeta social, que ya la copió del CSS claro: una
# sola copia, y si algún día cambia allí cambia en las dos.
BLANCO = tarjeta_social.CREMA
TINTA = tarjeta_social.TINTA
TENUE = tarjeta_social.TENUE
ACENTO = tarjeta_social.ACENTO
LINEA = tarjeta_social.LINEA
FICHA = tarjeta_social.TARJETA

# El dibujo, cuando la palabra lo tiene. 263 de 2.984.
DIBUJO = 430
DIBUJO_AIRE = 44

# Las escaleras. Se elige el escalón MÁS GRANDE con el que el texto entra,
# midiéndolo antes de dibujar: un bucle que achica «hasta que entre» y al
# llegar al piso dibuja igual deja el texto saliéndose, y eso se ve en
# Telegram y no aquí.
ESCALERA_ES = (108, 96, 84, 72, 62, 54, 46, 40)
ESCALERA_RU = (64, 58, 52, 46, 40, 36, 32)
ESCALERA_EJ = (42, 38, 34, 30, 27, 24)
EJEMPLO_RENGLONES = 2

PIE = 30
# El aire entre el cuerpo y el pie. Menos que esto y el pie se lee como un
# renglon mas del ejemplo.
AIRE_DEL_PIE = 54
REGLA = 180


def _entra(d, texto: str, fuente, ancho: int) -> bool:
    return d.textlength(texto, font=fuente) <= ancho


def _escalon(d, texto: str, escalera, ancho: int, grosor="Bold"):
    """El cuerpo más grande de la escalera con el que `texto` entra en UNA
    línea. Si no entra con ninguno, devuelve el más chico: es el suelo, y el
    que llama tiene que saber que ahí puede sobresalir."""
    fuente = None
    for tam in escalera:
        fuente = tarjeta_social._fuente(grosor, tam)
        if _entra(d, texto, fuente, ancho):
            return fuente
    return fuente


def _ejemplo_que_entra(d, texto: str, ancho: int):
    """El cuerpo más grande con el que el ejemplo entra en dos renglones.

    Devuelve `(fuente, renglones)`. Al revés que la palabra, aquí sí se
    puede partir: es una frase."""
    fuente = renglones = None
    for tam in ESCALERA_EJ:
        fuente = tarjeta_social._fuente("Regular", tam)
        renglones = tarjeta_social._partir(d, texto, fuente, ancho)
        if len(renglones) <= EJEMPLO_RENGLONES:
            return fuente, renglones
    return fuente, renglones[:EJEMPLO_RENGLONES]


def _ficha_del_dibujo(ruta: pathlib.Path, lado: int):
    """El dibujo dentro de su ficha redondeada, como en la portada.

    Los 300 dibujos ya están igualados al color de la ficha
    (`igualar_dibujos.py`), así que pegados a hueso se verían como
    rectángulos sucios: la esquina redonda es lo que los hace una pieza.
    """
    from PIL import Image, ImageDraw

    ficha = Image.new("RGB", (lado, lado), FICHA)
    try:
        dib = Image.open(ruta).convert("RGBA")
    except OSError:
        return None
    dib.thumbnail((lado - DIBUJO_AIRE, lado - DIBUJO_AIRE), Image.LANCZOS)
    ficha.paste(dib, ((lado - dib.width) // 2, (lado - dib.height) // 2), dib)

    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        (0, 0, lado - 1, lado - 1), radius=lado // 9, fill=255)
    redonda = Image.new("RGB", (lado, lado), BLANCO)
    redonda.paste(ficha, (0, 0), mascara)
    return redonda


def componer(p: dict, dominio: str, urok: str):
    """La tarjeta de una palabra. Devuelve la imagen de PIL.

    Todo se MIDE antes de dibujar: el alto sale del contenido, asi que una
    palabra sin ejemplo ni dibujo no deja medio lienzo vacio y una con las
    dos cosas no se sale. Escrito al reves —lienzo fijo y texto encima— una
    de las dos siempre queda mal, y eso se ve en Telegram y no aqui.
    """
    from PIL import Image, ImageDraw

    regla = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    ancho = ANCHO - 2 * MARGEN

    dibujo = None
    if p.get("dibujo"):
        dibujo = _ficha_del_dibujo(
            construir_sitio.DOCS / "img" / p["dibujo"], DIBUJO)

    f_es = _escalon(regla, p["es"], ESCALERA_ES, ancho)
    f_ru = _escalon(regla, p["ru"], ESCALERA_RU, ancho, grosor="Regular")
    f_ej = renglones = None
    if p.get("ejemplo"):
        f_ej, renglones = _ejemplo_que_entra(regla, p["ejemplo"], ancho)
    f_pie = tarjeta_social._fuente("Regular", PIE)

    alto_es = f_es.size + 18
    alto_ru = f_ru.size + 26
    alto_regla = 32 if renglones else 0
    alto_ej = (f_ej.size + 12) * len(renglones) if renglones else 0
    cuerpo = alto_es + alto_ru + alto_regla + alto_ej
    if dibujo is not None:
        cuerpo += DIBUJO + 44

    alto = MARGEN + cuerpo + AIRE_DEL_PIE + PIE + MARGEN
    alto = max(ALTO_MINIMO, min(ALTO_MAXIMO, alto))

    lienzo = Image.new("RGB", (ANCHO, alto), BLANCO)
    d = ImageDraw.Draw(lienzo)
    y = MARGEN

    if dibujo is not None:
        # Centrado y no pegado al margen. Se probaron las dos: alineado a la
        # izquierda deja media tarjeta vacia a su derecha, porque el dibujo
        # es cuadrado y el texto de debajo no llega tan abajo. Centrado, el
        # blanco queda repartido en los dos lados y se lee como aire.
        lienzo.paste(dibujo, ((ANCHO - DIBUJO) // 2, y))
        y += DIBUJO + 44

    d.text((MARGEN, y), p["es"], font=f_es, fill=TINTA)
    y += alto_es
    d.text((MARGEN, y), p["ru"], font=f_ru, fill=ACENTO)
    y += alto_ru
    if renglones:
        d.line((MARGEN, y, MARGEN + REGLA, y), fill=LINEA, width=2)
        y += alto_regla
        for renglon in renglones:
            d.text((MARGEN, y), renglon, font=f_ej, fill=TENUE)
            y += f_ej.size + 12

    pie = alto - MARGEN - PIE
    d.text((MARGEN, pie), "%s %d" % (urok, p["dia"].numero),
           font=f_pie, fill=TENUE)
    if dominio:
        marca = dominio.replace("https://", "").replace("http://", "")
        d.text((ANCHO - MARGEN - d.textlength(marca, font=f_pie), pie),
               marca, font=f_pie, fill=TENUE)
    return lienzo


def dibujar(p: dict, destino: pathlib.Path, dominio: str, urok: str):
    """Escribe la tarjeta. Devuelve el camino, o None si no se pudo.

    **Falla seguro**: sin fuentes con cirílico en el sistema, o sin PIL, la
    publicación del día sale como antes en vez de no salir. Un canal mudo
    es mucho peor que un canal sin tarjeta.
    """
    try:
        imagen = componer(p, dominio, urok)
        destino.parent.mkdir(parents=True, exist_ok=True)
        imagen.save(destino, "PNG", optimize=True)
    except (OSError, SystemExit, ImportError, ValueError):
        return None
    return destino


def main(argv=None) -> int:
    import palabra_del_dia

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ver", default="", help="dónde dejar la tarjeta")
    ap.add_argument("--dia", default="", help="AAAA-MM-DD, por defecto hoy")
    ap.add_argument("--numero", type=int, help="salta la fecha y pide la N")
    args = ap.parse_args(argv)

    cfg = construir_sitio.cargar_config()
    t = construir_sitio.cargar_textos()["canal"]
    lista = palabra_del_dia.palabras(cfg)

    if args.numero:
        n = args.numero
    else:
        desde = (cfg.get("telegram") or {}).get("desde")
        if not desde:
            n = 1
        else:
            fecha = (dt.date.fromisoformat(args.dia) if args.dia
                     else dt.date.today())
            n = palabra_del_dia.numero_del_dia(
                fecha, dt.date.fromisoformat(str(desde)))

    p = palabra_del_dia.del_dia(lista, n)
    if p is None:
        print("la publicación %d no existe: el canal tiene %d."
              % (n, len(lista)))
        return 1

    salida = pathlib.Path(args.ver or "tarjeta-palabra.png")
    hecho = dibujar(p, salida, (cfg.get("dominio") or "").rstrip("/"),
                    t["urok"])
    if hecho is None:
        print("no se pudo dibujar (¿faltan fuentes con cirílico?)")
        return 1
    print("publicación %d · %s — %s%s -> %s (%d KB)"
          % (n, p["es"], p["ru"], " +dibujo" if p.get("dibujo") else "",
             hecho, hecho.stat().st_size // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
