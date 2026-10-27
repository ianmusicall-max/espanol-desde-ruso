#!/usr/bin/env python3
"""Locuta en español las frases de las lecciones. Cuesta cerca de un dólar.

    .venv/bin/python scripts/generar_audio.py --ver      # qué haría y qué costaría
    .venv/bin/python scripts/generar_audio.py            # lo hace (pide OPENAI_API_KEY)

Deja un MP3 por frase en `docs/audio/` y un índice en `docs/audio/indice.json`.
El sitio los enchufa solo: cada frase española de las tablas sale con un ▶ si
tiene audio, y sin él si no lo tiene.

Tres decisiones que no son de forma:

- **El nombre del archivo es un hash del pedido entero** (texto + voz +
  modelo), no un número de lección. Así una frase que se repite —«Buenos
  días» sale en varias lecciones— se locuta y se paga UNA vez, y volver a
  correr el guion no vuelve a pagar nada de lo que ya está. Es la misma idea
  que la cache de imágenes del proyecto de salud.
- **Se escribe en un archivo aparte y se renombra al final.** Si el proceso se
  corta a mitad de una descarga, lo que queda es un `.parcial` y no un MP3 de
  cero bytes que luego el sitio serviría como bueno.
- **El índice se reconstruye de los archivos que hay en disco**, no de lo que
  esta corrida acaba de generar: así una corrida a medias deja un índice
  coherente con lo que de verdad se puede oír.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402

AUDIO = RAIZ / "docs" / "audio"
INDICE = "indice.json"

MODELO = "gpt-4o-mini-tts"
# La eligió el profesor el 2026-10-26 oyendo las tres con la misma frase
# (`--muestra 3 --voz …`). Cambiarla aquí es otro hash, o sea 1,30 USD otra
# vez: si alguien la toca, que sea después de volver a escucharlas.
VOZ = "shimmer"
INSTRUCCIONES = ("Habla en español de España, claro y despacio, como un profesor "
                 "que dicta para que un principiante repita. Pronuncia cada sílaba.")

# Cabeceras de tabla y rótulos: no son frases que nadie quiera oír, y «Español»
# aparece 199 veces porque encabeza casi todas las tablas.
NO_SON_FRASES = {"español", "espanol", "frase", "ejemplo", "ejemplos", "singular",
                 "plural", "masculino", "femenino", "verbo", "palabra", "forma"}

# Un precio que se mide, no se adivina: si cambia, se cambia aquí y el --ver
# vuelve a decir la verdad. Son dólares por millón de caracteres.
PRECIO_POR_MILLON = 16.0


def vale_la_pena(texto: str) -> bool:
    """Si locutar esto le sirve a alguien.

    Fuera lo que no es español hablado: lo que trae cirílico (es la columna
    rusa), los rótulos de cabecera, lo que no tiene ni una letra, y la
    transcripción fonética entre corchetes —«[a] abierta»—, que es un símbolo
    para leer con los ojos y que una voz leería como «corchete a corchete»."""
    if not texto or re.search(r"[а-яА-ЯёЁ]", texto):
        return False
    if texto.lower() in NO_SON_FRASES:
        return False
    if not re.search(r"[a-záéíóúñü]", texto, re.I):
        return False
    return not re.fullmatch(r"\[.*\]|/.*/", texto.strip())


def frases_de(ruta: pathlib.Path) -> list[str]:
    """El español de las tablas, mirando TODAS las columnas.

    No solo la primera: en las tablas de fonética la primera columna es la
    letra («a») y la palabra de ejemplo («casa») está en la cuarta, que es
    justo la que hay que oír. La columna rusa se cae sola por el cirílico."""
    salida: list[str] = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if not linea.strip().startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 2 or set(celdas[0]) <= set("-: "):
            continue
        for celda in celdas:
            texto = re.sub(r"[*_`]", "", celda)
            texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto).strip()
            if vale_la_pena(texto):
                salida.append(texto)
    return salida


def todas_las_frases(cal: dict) -> list[str]:
    """Sin repetir y en el orden del curso, para que las primeras en generarse
    sean las de las primeras lecciones si la corrida se corta."""
    vistas: dict[str, None] = {}
    for d in plan.dias(cal):
        if d.ruta.exists():
            for f in frases_de(d.ruta):
                vistas.setdefault(f, None)
    return list(vistas)


# Las cinco de OpenAI que valen para dictar despacio. `nova` es la elegida;
# las otras estan aqui para poder oirlas con --muestra antes de pagar las
# 3.543, porque cambiar de voz despues es otro hash y se paga entero.
VOCES = ("nova", "alloy", "shimmer", "coral", "sage")


def nombre_de(texto: str, voz: str = VOZ, modelo: str = MODELO) -> str:
    """El pedido ENTERO es la llave: cambiar la voz o el modelo es otro audio."""
    crudo = json.dumps([texto, voz, modelo, INSTRUCCIONES], ensure_ascii=False)
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()[:20] + ".mp3"


def coste(frases: list[str]) -> float:
    return sum(len(f) for f in frases) * PRECIO_POR_MILLON / 1_000_000


def muestra_de(frases: list[str], n: int) -> list[str]:
    """Las N más largas, para oír la voz antes de pagar las 3.543.

    Las más LARGAS y no las primeras: una voz se juzga en una frase entera, y
    por orden de lección la primera sería la letra «a», que no dice nada de
    cómo suena. Cuesta céntimos y contesta lo único que no se puede contestar
    leyendo: si esa voz sirve para que un principiante repita."""
    return sorted(frases, key=len, reverse=True)[:n]


def faltan(frases: list[str], carpeta: pathlib.Path, voz: str = VOZ) -> list[str]:
    """Lo que ya está en disco no se vuelve a pagar. Un archivo vacío no cuenta:
    es una descarga que se cortó.

    La voz entra en el nombre, así que probar otra no borra ni pisa la primera:
    son dos juegos de archivos y se puede comparar."""
    return [f for f in frases
            if not (carpeta / nombre_de(f, voz)).exists()
            or (carpeta / nombre_de(f, voz)).stat().st_size == 0]


def escribir_indice(frases: list[str], carpeta: pathlib.Path, voz: str = VOZ) -> int:
    """Texto → archivo, pero solo de lo que de verdad se puede oír."""
    indice = {f: nombre_de(f, voz) for f in frases
              if (carpeta / nombre_de(f, voz)).exists()
              and (carpeta / nombre_de(f, voz)).stat().st_size}
    carpeta.mkdir(parents=True, exist_ok=True)
    carpeta.joinpath(INDICE).write_text(
        json.dumps(indice, ensure_ascii=False, sort_keys=True, indent=0), encoding="utf-8")
    return len(indice)


# A una frase por vez, las 3.543 tardan hora y media: casi todo es esperar a
# que OpenAI conteste, no trabajo nuestro. Seis a la vez lo dejan en unos
# quince minutos. No más de seis a propósito: el límite de peticiones de la
# cuenta es lo siguiente que se rompería, y un 429 se paga en reintentos.
HILOS = 6


def _una(texto: str, carpeta: pathlib.Path, cliente, voz: str) -> str | None:
    """Locuta una frase. Devuelve el error si lo hubo, o None si salió.

    Escribe en `.parcial` y renombra: una descarga cortada dejaría un MP3 de
    cero bytes que el sitio serviría como bueno, y el lector pulsaría ▶ sin que
    sonara nada. El `.parcial` lleva el nombre del destino, así que dos hilos
    nunca escriben en el mismo archivo temporal."""
    destino = carpeta / nombre_de(texto, voz)
    parcial = destino.with_suffix(".parcial")
    try:
        with cliente.audio.speech.with_streaming_response.create(
                model=MODELO, voice=voz, input=texto,
                instructions=INSTRUCCIONES, response_format="mp3") as r:
            r.stream_to_file(parcial)
        parcial.replace(destino)
        return None
    except Exception as e:  # una frase que falla no puede tumbar la tanda
        parcial.unlink(missing_ok=True)
        return str(e)


def generar(frases: list[str], carpeta: pathlib.Path, cliente, voz: str = VOZ,
            hilos: int = HILOS) -> int:
    carpeta.mkdir(parents=True, exist_ok=True)
    hechos = 0
    with cf.ThreadPoolExecutor(max_workers=hilos) as pool:
        pedidos = {pool.submit(_una, t, carpeta, cliente, voz): t for t in frases}
        for i, fut in enumerate(cf.as_completed(pedidos), 1):
            fallo = fut.result()
            if fallo:
                print(f"  [{i}/{len(frases)}] falló «{pedidos[fut][:40]}»: {fallo}")
            else:
                hechos += 1
            if i % 250 == 0:
                print(f"  {i}/{len(frases)}", flush=True)
    return hechos


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ver", action="store_true", help="dice qué haría y qué costaría, sin gastar")
    p.add_argument("--muestra", type=int, metavar="N",
                   help="locuta solo N frases, para oír la voz antes de pagarlas todas")
    p.add_argument("--voz", default=VOZ, choices=VOCES,
                   help=f"la voz de OpenAI (por defecto {VOZ})")
    p.add_argument("--carpeta", type=pathlib.Path, default=AUDIO)
    a = p.parse_args(argv)

    frases = todas_las_frases(plan.cargar())
    pendientes = faltan(frases, a.carpeta, a.voz)
    print(f"{len(frases)} frases distintas · {sum(len(f) for f in frases):,} caracteres"
          .replace(",", " "))
    print(f"ya locutadas: {len(frases) - len(pendientes)} · faltan: {len(pendientes)}")
    print(f"coste de lo que falta: {coste(pendientes):.2f} USD "
          f"(a {PRECIO_POR_MILLON:.0f} USD por millón de caracteres)")

    if a.ver:
        for f in pendientes[:5]:
            print(f"    {nombre_de(f)}  «{f[:50]}»")
        if len(pendientes) > 5:
            print(f"    … y {len(pendientes) - 5} más")
        return 0

    if not pendientes:
        print(f"nada que hacer · índice con {escribir_indice(frases, a.carpeta, a.voz)} frases")
        return 0

    if a.muestra:
        pendientes = muestra_de(pendientes, a.muestra)
        print(f"\nmuestra de {len(pendientes)} frases · {coste(pendientes):.4f} USD")

    if not os.environ.get("OPENAI_API_KEY"):
        print("\nfalta OPENAI_API_KEY en el entorno (o en .env).")
        return 1
    try:
        from openai import OpenAI
    except ImportError:
        print("\nfalta el paquete: .venv/bin/pip install openai")
        return 1

    hechos = generar(pendientes, a.carpeta, OpenAI(), a.voz)
    total = escribir_indice(frases, a.carpeta, a.voz)
    print(f"\n{hechos} audios nuevos · índice con {total} frases")
    if a.muestra:
        print(f"Escúchalas en {a.carpeta} y, si la voz te vale, córrelo sin --muestra.")
    else:
        print("Ahora: .venv/bin/python scripts/construir_sitio.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
