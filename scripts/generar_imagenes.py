#!/usr/bin/env python3
"""Dibuja los sustantivos del vocabulario. Cuesta unos pocos dólares.

    .venv/bin/python scripts/generar_imagenes.py --ver            # qué haría y qué costaría
    .venv/bin/python scripts/generar_imagenes.py --muestra 6      # 6 palabras, para ver el estilo
    .venv/bin/python scripts/generar_imagenes.py                  # lo hace (pide OPENAI_API_KEY)

Deja una imagen por palabra en `docs/img/` y un índice en `docs/img/indice.json`.
Es el hermano de `generar_audio.py` y comparte sus tres decisiones: el hash del
pedido entero como nombre, el `.parcial` que se renombra al final, y el índice
reconstruido de lo que hay en disco y no de lo que esta corrida generó.

Lo propio de las imágenes, que es donde esto se rompería:

- **Solo sustantivos.** De las 976 entradas del vocabulario, 471 llevan
  artículo. Las otras —`hola`, `muy`, `mi/mis`, `mayor`— no tienen dibujo
  posible, y ponerles uno sería decoración que roba sitio en una lección de
  30 minutos. Y de los sustantivos se quitan a mano los abstractos
  (`ABSTRACTOS`): «el acento» o «el alquiler» no se dibujan sin mentir.
- **Ni una letra en la imagen.** Los modelos escriben texto con faltas, y un
  dibujo de «la mesa» con «MEZA» encima le enseña al alumno la falta. El
  estilo lo prohíbe explícitamente y hay una prueba que lo exige.
- **Un solo estilo para las 422.** Generadas sueltas saldrían 422 estilos
  distintos y el curso parecería un vertedero de clipart. El estilo entra en
  el hash, así que probar otro no pisa al primero y se pueden comparar.
- **Se guardan a 512 px, no a los 1024 que vienen.** Se ven a ~200 px en la
  tabla, y git guarda el historial para siempre: subir los grandes y
  encogerlos después deja el repositorio cargando con los dos juegos. Es la
  lección del audio, que se recodificó a 64 kbps ANTES del primer commit.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import hashlib
import io
import json
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import exportar_anki  # noqa: E402
import plan  # noqa: E402

IMG = RAIZ / "docs" / "img"
INDICE = "indice.json"

MODELO = "gpt-image-1-mini"
CALIDAD = "low"
MEDIDA = "1024x1024"
# A lo que se guardan. Se ven a ~200 px en la tabla del vocabulario, así que
# 512 da de sobra para pantallas de retina y pesa una cuarta parte.
LADO = 512

# Los estilos candidatos. El primero es el que se usa salvo que --estilo diga
# otro; los demás están para poder VERLOS con --muestra antes de pagar las 422,
# porque cambiar de estilo después es otro hash y se paga entero. Es lo que se
# hizo con la voz del audio el 2026-10-26.
#
# Los tres dicen lo mismo en lo que no se negocia: fondo liso, un solo objeto,
# centrado y SIN TEXTO. Lo que cambia es la piel.
SIN_TEXTO = ("Absolutely no text, no letters, no numbers, no labels and no "
             "watermark anywhere in the image.")
ESTILOS = {
    "plano": ("Flat vector illustration, bold clean outlines, simple shapes, "
              "limited warm palette, plain soft cream background (#f4f1ea), "
              "the object centered and filling most of the frame. " + SIN_TEXTO),
    "acuarela": ("Soft watercolor illustration with gentle washes and visible "
                 "paper texture, muted warm palette, plain cream background, "
                 "the object centered and filling most of the frame. " + SIN_TEXTO),
    "foto": ("Clean studio photograph, soft diffused light, shallow depth of "
             "field, plain uniform cream background, the subject centered and "
             "filling most of the frame, no props. " + SIN_TEXTO),
}
ESTILO = "plano"

# Dólares por imagen. Se mide, no se adivina: si OpenAI cambia la tarifa se
# cambia aquí y el --ver vuelve a decir la verdad.
PRECIOS = {
    ("gpt-image-1-mini", "low"): 0.005,
    ("gpt-image-1-mini", "medium"): 0.011,
    ("gpt-image-1", "low"): 0.011,
    ("gpt-image-1", "medium"): 0.042,
}
PRECIO_SI_NO_SE_SABE = 0.011

# Sustantivos que llevan artículo y aun así no se pueden dibujar sin inventar.
# Es una lista a mano y no una regla, igual que `NO_SON_FRASES` en el audio:
# lo que separa «la mesa» de «el alquiler» no lo dice ninguna marca del texto.
ABSTRACTOS = {
    # Conceptos: no hay dibujo que los enseñe, y uno bonito al lado sería
    # decoración que roba sitio en una lección de 30 minutos.
    "acento", "afición", "alquiler", "asunto", "ayuda", "cambio", "comunidad",
    "consejo", "correspondencia", "cosa", "costumbre", "cuenta", "cultura",
    "derecha", "descuento", "devolución", "diferencia", "dirección", "duda",
    "edad", "ejemplo", "entrega", "envío", "error", "espacio", "experiencia",
    "fecha", "final", "forma", "función", "futuro", "gana", "gusto", "idea",
    "información", "intención", "interés", "longitud", "lugar", "lujo", "manera",
    "marca", "medio", "mismo", "mito", "momento", "motivo", "nivel", "nombre",
    "oferta", "opinión", "orden", "palabra", "parentela", "parte", "pasado",
    "paso", "pausa", "pedido", "pena", "permiso", "plan", "plazo", "precio",
    "presente", "problema", "pronóstico", "pregunta", "punto", "razón",
    "respuesta", "resultado", "ruido", "rutina", "sabor", "sección", "sentido",
    "ser", "servicio", "servicios", "significado", "sitio", "sobremesa",
    "sonido", "suerte", "tipo", "trozo", "turno", "vez", "vida",
    # Gramática y lengua: dibujarlos es dibujar una explicación, y para eso
    # están el texto y el bloque de contraste.
    "abreviatura", "diminutivo", "patronímico", "patrón", "porteño", "regla",
    "tilde",
    # Trámites y dinero: no tienen forma. «La fianza» dibujada es un fajo de
    # billetes, que es «el dinero» otra vez.
    "código postal", "fianza", "garantía", "gastos de envío", "gastos incluidos",
    "iva", "número de teléfono", "paga extra",
    # Tiempo: un reloj o un calendario valen para todos, así que el dibujo no
    # distingue uno de otro y deja de enseñar.
    "día", "día normal", "fin de semana", "fines de semana", "hora",
    "huso horario", "jornada continua", "jornada partida", "lunes",
    "medianoche", "mes", "minuto", "pausa del mediodía", "segundo", "semana",
    "tiempo", "tiempo libre", "veinticuatro horas", "año",
    # Sitios y fiestas reales: una imagen generada de la Península o del Día
    # del Padre es un invento con pinta de dato, que es la regla 7.
    "península", "día del padre", "santo",
    # Y lo que no es un sustantivo pero lleva artículo delante.
    "primera calle", "saludo",
}


# Un sustantivo del vocabulario empieza por artículo. Es la señal más limpia
# que hay en esa tabla y no hace falta analizar nada más.
ARTICULO = re.compile(r"^(el|la|los|las|un|una)\s+", re.I)


def limpiar(celda: str) -> str:
    """La palabra, sin el marcado del acento tónico ni las variantes.

    Tres cosas se tiran y las tres por el mismo motivo —para dibujar hace falta
    UNA palabra—, pero el ORDEN importa:

    1. el 🌎, que separa la forma de España de la de América: «la carta 🌎 el
       menú». Se parte por ahí y se toma la PRIMERA, que por la regla 8 es la
       más extendida y la que el curso enseña. Quitando el 🌎 sin partir salía
       «la carta el menú», que no es nada.
    2. la barra de las dos formas: «el sobrino / la sobrina».
    3. la negrita del acento tónico: «el ma**ri**do»."""
    texto = re.sub(r"[*_`]", "", celda).strip()
    texto = texto.split("🌎")[0]
    texto = texto.split("/")[0].strip()
    return re.sub(r"\s+", " ", texto)


def es_dibujable(palabra: str) -> bool:
    """Si tiene sentido pedirle un dibujo a un modelo.

    Pide artículo —o sea, que sea un sustantivo— y que no esté entre los
    abstractos. Lo que no lleva artículo son saludos, adjetivos y palabras
    funcionales: `hola`, `muy`, `mayor`, `mi/mis`. Un dibujo ahí no enseña
    nada."""
    if not ARTICULO.match(palabra):
        return False
    nucleo = ARTICULO.sub("", palabra).strip().lower()
    if not nucleo or " " in nucleo and len(nucleo.split()) > 3:
        return False
    if not re.fullmatch(r"[a-záéíóúñü ]+", nucleo):
        return False
    return nucleo not in ABSTRACTOS


def todas_las_palabras(cal: dict) -> list[str]:
    """Los sustantivos del vocabulario, sin repetir y en el orden del curso.

    En el orden del curso para que, si la corrida se corta, lo generado sea lo
    de las primeras lecciones, que es lo que más gente ve."""
    vistas: dict[str, None] = {}
    for d in plan.dias(cal):
        if not d.ruta.exists():
            continue
        for tarjeta in exportar_anki.tarjetas_de(d.ruta):
            palabra = limpiar(tarjeta[0])
            if es_dibujable(palabra):
                vistas.setdefault(palabra, None)
    return list(vistas)


def pedido_de(palabra: str, estilo: str = ESTILO) -> str:
    """Lo que se le pide al modelo. El artículo se queda a propósito: «la
    naranja» y «el naranja» son la fruta y el color."""
    return f"An educational illustration for a Spanish vocabulary card: {palabra}. {ESTILOS[estilo]}"


def nombre_de(palabra: str, estilo: str = ESTILO, modelo: str = MODELO,
              calidad: str = CALIDAD) -> str:
    """El pedido ENTERO es la llave: cambiar el estilo o el modelo es otra imagen."""
    crudo = json.dumps([pedido_de(palabra, estilo), modelo, calidad, MEDIDA, LADO],
                       ensure_ascii=False)
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()[:20] + ".webp"


def precio_por_imagen(modelo: str = MODELO, calidad: str = CALIDAD) -> float:
    return PRECIOS.get((modelo, calidad), PRECIO_SI_NO_SE_SABE)


def coste(palabras: list[str], modelo: str = MODELO, calidad: str = CALIDAD) -> float:
    return len(palabras) * precio_por_imagen(modelo, calidad)


def muestra_de(palabras: list[str], n: int) -> list[str]:
    """Las N repartidas a lo largo del curso, no las N primeras.

    Dos cosas, y las dos para que la muestra conteste lo que se le pregunta:

    - **Repartidas.** Las primeras son todas de la unidad 1 —casa, mesa,
      libro— y de un estilo solo se puede juzgar si aguanta cosas distintas:
      una fruta, una persona, una prenda, un sitio.
    - **De una sola palabra.** «El compadre» o «el centro comercial» salen mal
      por el modelo y no por el estilo, así que una muestra con ellas haría
      confundir «no entendió la palabra» con «no me gusta el dibujo», que es
      justo lo que se está decidiendo. Si no hay suficientes, se completa con
      las demás."""
    if n >= len(palabras):
        return list(palabras)
    simples = [p for p in palabras if len(ARTICULO.sub("", p).split()) == 1]
    fuente = simples if len(simples) >= n else palabras
    paso = len(fuente) / n
    elegidas = [fuente[int(i * paso)] for i in range(n)]
    return elegidas


def faltan(palabras: list[str], carpeta: pathlib.Path, estilo: str = ESTILO,
           modelo: str = MODELO, calidad: str = CALIDAD) -> list[str]:
    """Lo que ya está en disco no se vuelve a pagar. Un archivo vacío no cuenta:
    es una descarga que se cortó."""
    pendientes = []
    for p in palabras:
        f = carpeta / nombre_de(p, estilo, modelo, calidad)
        if not f.exists() or f.stat().st_size == 0:
            pendientes.append(p)
    return pendientes


def escribir_indice(palabras: list[str], carpeta: pathlib.Path, estilo: str = ESTILO,
                    modelo: str = MODELO, calidad: str = CALIDAD) -> int:
    """Palabra → archivo, pero solo de lo que de verdad se puede ver."""
    indice = {}
    for p in palabras:
        f = carpeta / nombre_de(p, estilo, modelo, calidad)
        if f.exists() and f.stat().st_size:
            indice[p] = f.name
    carpeta.mkdir(parents=True, exist_ok=True)
    carpeta.joinpath(INDICE).write_text(
        json.dumps(indice, ensure_ascii=False, sort_keys=True, indent=0), encoding="utf-8")
    return len(indice)


# Seis a la vez, por lo mismo que el audio: casi todo es esperar a que OpenAI
# conteste, y el límite de peticiones de la cuenta es lo siguiente que se
# rompería. Un 429 se paga en reintentos.
HILOS = 6


def _encoger(datos: bytes, lado: int = LADO) -> bytes:
    """A `lado` px y a webp. Antes de guardar, no después: git guarda el
    historial para siempre."""
    from PIL import Image
    im = Image.open(io.BytesIO(datos)).convert("RGB")
    im = im.resize((lado, lado), Image.LANCZOS)
    salida = io.BytesIO()
    im.save(salida, format="WEBP", quality=82, method=6)
    return salida.getvalue()


def _una(palabra: str, carpeta: pathlib.Path, cliente, estilo: str,
         modelo: str, calidad: str) -> str | None:
    """Dibuja una palabra. Devuelve el error si lo hubo, o None si salió."""
    destino = carpeta / nombre_de(palabra, estilo, modelo, calidad)
    parcial = destino.with_suffix(".parcial")
    try:
        r = cliente.images.generate(model=modelo, prompt=pedido_de(palabra, estilo),
                                    size=MEDIDA, quality=calidad, n=1)
        crudo = base64.b64decode(r.data[0].b64_json)
        parcial.write_bytes(_encoger(crudo))
        parcial.replace(destino)
        return None
    except Exception as e:  # una palabra que falla no puede tumbar la tanda
        parcial.unlink(missing_ok=True)
        return str(e)


def generar(palabras: list[str], carpeta: pathlib.Path, cliente, estilo: str = ESTILO,
            modelo: str = MODELO, calidad: str = CALIDAD, hilos: int = HILOS) -> int:
    carpeta.mkdir(parents=True, exist_ok=True)
    hechas = 0
    with cf.ThreadPoolExecutor(max_workers=hilos) as pool:
        pedidos = {pool.submit(_una, p, carpeta, cliente, estilo, modelo, calidad): p
                   for p in palabras}
        for i, fut in enumerate(cf.as_completed(pedidos), 1):
            fallo = fut.result()
            if fallo:
                print(f"  [{i}/{len(palabras)}] falló «{pedidos[fut]}»: {fallo[:120]}")
            else:
                hechas += 1
            if i % 50 == 0:
                print(f"  {i}/{len(palabras)}", flush=True)
    return hechas


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ver", action="store_true", help="dice qué haría y qué costaría, sin gastar")
    p.add_argument("--muestra", type=int, metavar="N",
                   help="dibuja solo N palabras, para ver el estilo antes de pagarlas todas")
    p.add_argument("--estilo", default=ESTILO, choices=sorted(ESTILOS),
                   help=f"el estilo del dibujo (por defecto {ESTILO})")
    p.add_argument("--modelo", default=MODELO, help=f"el modelo de OpenAI (por defecto {MODELO})")
    p.add_argument("--calidad", default=CALIDAD, choices=("low", "medium", "high"))
    p.add_argument("--modelos", action="store_true",
                   help="lista los modelos de imagen que la cuenta tiene de verdad")
    p.add_argument("--carpeta", type=pathlib.Path, default=IMG)
    a = p.parse_args(argv)

    if a.modelos:
        if not os.environ.get("OPENAI_API_KEY"):
            print("falta OPENAI_API_KEY en el entorno.")
            return 1
        from openai import OpenAI
        nombres = sorted(m.id for m in OpenAI().models.list() if "image" in m.id)
        print("\n".join(nombres) or "la cuenta no lista ningún modelo de imagen")
        return 0

    palabras = todas_las_palabras(plan.cargar())
    pendientes = faltan(palabras, a.carpeta, a.estilo, a.modelo, a.calidad)
    print(f"{len(palabras)} sustantivos dibujables del vocabulario")
    print(f"ya dibujados: {len(palabras) - len(pendientes)} · faltan: {len(pendientes)}")
    print(f"coste de lo que falta: {coste(pendientes, a.modelo, a.calidad):.2f} USD "
          f"(a {precio_por_imagen(a.modelo, a.calidad):.3f} por imagen, "
          f"{a.modelo} {a.calidad})")

    if a.ver:
        for w in pendientes[:8]:
            print(f"    {nombre_de(w, a.estilo, a.modelo, a.calidad)}  «{w}»")
        if len(pendientes) > 8:
            print(f"    … y {len(pendientes) - 8} más")
        return 0

    if not pendientes:
        total = escribir_indice(palabras, a.carpeta, a.estilo, a.modelo, a.calidad)
        print(f"nada que hacer · índice con {total} palabras")
        return 0

    if a.muestra:
        pendientes = muestra_de(pendientes, a.muestra)
        print(f"\nmuestra de {len(pendientes)} ({a.estilo}) · "
              f"{coste(pendientes, a.modelo, a.calidad):.3f} USD: "
              + ", ".join(pendientes))

    if not os.environ.get("OPENAI_API_KEY"):
        print("\nfalta OPENAI_API_KEY en el entorno (o en .env).")
        return 1
    try:
        from openai import OpenAI
    except ImportError:
        print("\nfalta el paquete: .venv/bin/pip install openai")
        return 1

    hechas = generar(pendientes, a.carpeta, OpenAI(), a.estilo, a.modelo, a.calidad)
    total = escribir_indice(palabras, a.carpeta, a.estilo, a.modelo, a.calidad)
    print(f"\n{hechas} imágenes nuevas · índice con {total} palabras")
    if a.muestra:
        print(f"Míralas en {a.carpeta} y, si el estilo te vale, córrelo sin --muestra.")
    else:
        print("Ahora: .venv/bin/python scripts/construir_sitio.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
