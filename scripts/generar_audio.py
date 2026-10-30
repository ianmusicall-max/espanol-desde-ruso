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
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402

AUDIO = RAIZ / "docs" / "audio"
INDICE = "indice.json"
# Lo que volvió MUDO. Un MP3 de silencio pesa y existe, así que pasaba las dos
# guardas de siempre —no está vacío, no es un `.parcial`— y el sitio le ponía
# su ▶: el lector lo pulsa y no suena nada, que es el peor fallo posible
# porque no se distingue de un botón roto. Pasó con 14 de las 11 378, y al
# volver a pedirlas las 14 volvieron con voz —la «h» y la «y» incluidas—, o
# sea que eran fallos sueltos de la API y no letras sin nada que decir. Por
# eso esto no es una lista de excepciones del idioma: es una red.
#
# Se guarda el TEXTO y no el hash: así se lee qué frase es sin descifrar nada,
# y `faltan()` no vuelve a pagarla en cada corrida.
MUDOS = "mudos.json"
# Medido sobre el curso entero: una frase de verdad pica entre -3 y -10 dB, y
# las dos mudas estaban en -61 y -84. Cualquier corte entre medias vale; -50
# deja fuera el silencio sin tocar una grabación floja.
SILENCIO_DB = -50.0

# Lo que se PUBLICA. OpenAI entrega 128 kbps mono 24 kHz, que para voz es
# tirar bits que el oído no recoge: a 64 el curso entero pasa de 463 MB a 290
# y cabe de sobra en el límite de 1024 MB de GitHub Pages.
#
# Se recodifica ANTES del primer commit, y eso no es manía: git guarda el
# historial para siempre, así que subir los de 128 y encogerlos después deja
# el repositorio cargando con los dos juegos.
BITS = 64_000
# Un archivo ya recodificado mide unos 64 500 bps y no 64 000 exactos, así
# que la comprobación es un umbral y no una igualdad: con `== BITS` se
# recodificaría cada vez, y recodificar dos veces pierde calidad.
BITS_TOPE = 80_000

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


CIRILICO = re.compile(r"[а-яА-ЯёЁ]")


def parte_espanola(texto: str) -> str:
    """El español de una entrada de vocabulario que lleva la glosa rusa dentro.

    `hay que + инф.`, `tomar = и пить, и есть`, `el conductor (✗ не
    «кондуктор»)`: la entrada ES española y lo que la ensucia es la etiqueta en
    ruso que explica cómo se usa. Sin esto el locutor las rechaza enteras —y
    con razón, porque una voz española leyendo «инф.» sería audio inútil y
    pagado— y la tarjeta de Anki se queda muda: eran 103 de 3.001.

    Devuelve "" si lo que queda no es español que alguien quiera oír.
    """
    t = re.sub(r"\([^)]*\)", lambda m: "" if CIRILICO.search(m.group()) else m.group(), texto)
    t = re.sub(r"\s*=.*$", "", t)          # «tomar = и пить, и есть»
    while CIRILICO.search(t):               # colas «+ инф.», «+ прил. + que»
        corto = re.sub(r"\s*\+\s*[^+]*$", "", t)
        if corto == t:
            break
        t = corto
    t = re.sub(r"\s+", " ", t).strip(" ,;·")
    return t if not CIRILICO.search(t) and vale_la_pena(t) else ""


def frases_del_vocabulario(cal: dict) -> list[str]:
    """Las entradas de vocabulario rescatadas con `parte_espanola`.

    Solo las ENTRADAS, no todas las celdas, y eso es la decisión: medido sobre
    el curso entero, limpiar cualquier celda añade 255 frases y buena parte es
    basura —`ca-fe` y `mu-si-ca` son palabras partidas en sílabas de las tablas
    de fonética, `cu + a` y `¿Cómo es` son trozos sin sentido—, y esas saldrían
    además como botones ▶ en la lección, al lado de cosas que no son frases.
    Las entradas de vocabulario están curadas: de ahí salen 67 y todas valen.

    Pasa por `exportar_anki.filas_de`, que es el único sitio que sabe cuál de
    las dos tablas tiene cada día. Una copia aquí es como el informe de léxico
    se quedó sin ver los 50 domingos.
    """
    import exportar_anki

    salida: list[str] = []
    for d in plan.dias(cal):
        if not d.ruta.exists():
            continue
        for fila in exportar_anki.filas_de(d.ruta)[1]:
            if not fila:
                continue
            entrada = exportar_anki.limpiar(fila[0])
            if CIRILICO.search(entrada):
                p = parte_espanola(entrada)
                if p:
                    salida.append(p)
    return salida


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
    for f in frases_del_vocabulario(cal):
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


def mudo(ruta: pathlib.Path) -> bool:
    """¿Este MP3 es silencio?

    Lo contesta ffmpeg y no una cuenta sobre el tamaño: un archivo corto puede
    ser una palabra corta. Si ffmpeg no está, devuelve False —no se inventa un
    silencio—, porque quitarle el ▶ a una frase que sí suena sería peor.
    """
    try:
        salida = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", str(ruta), "-af", "volumedetect",
             "-f", "null", "-"],
            capture_output=True, text=True, timeout=60).stderr
    except (OSError, subprocess.SubprocessError):
        return False
    pico = re.search(r"max_volume:\s*(-?[\d.]+) dB", salida)
    return bool(pico) and float(pico.group(1)) < SILENCIO_DB


def bits_de(ruta: pathlib.Path) -> int | None:
    """Los bits por segundo de un MP3, o None si no se pueden leer."""
    try:
        salida = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=bit_rate",
             "-of", "csv=p=0", str(ruta)],
            capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return int(salida) if salida.isdigit() else None


def recodificar(ruta: pathlib.Path) -> bool:
    """Deja el MP3 a BITS. Devuelve si hizo falta tocarlo.

    Es IDEMPOTENTE: lo que ya está a 64 no se vuelve a tocar, así que una
    corrida cortada a mitad se reanuda sin recodificar dos veces y perder
    calidad.

    Escribe aparte y renombra encima, por lo mismo que el `.parcial` del
    generador: si ffmpeg se corta, lo que queda es el original intacto y no un
    MP3 truncado que el sitio serviría como bueno.

    Y el `-f mp3` NO es de adorno: el temporal se llama `.parcial`, y de esa
    extensión ffmpeg no deduce el formato. Sin él falla con «Unable to choose
    an output format», que es lo que dejó una tanda entera sin recodificar.
    """
    bits = bits_de(ruta)
    if bits is None or bits <= BITS_TOPE:
        return False
    tmp = ruta.with_suffix(ruta.suffix + ".parcial")
    try:
        hecho = subprocess.run(
            ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
             "-i", str(ruta), "-b:a", str(BITS), "-ac", "1", "-f", "mp3", str(tmp)],
            capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError):
        tmp.unlink(missing_ok=True)
        return False
    if hecho.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        return False
    tmp.replace(ruta)
    return True


def recodificar_todo(frases: list[str], carpeta: pathlib.Path, voz: str = VOZ,
                     hilos: int = 4) -> list[str]:
    """Las que hacía falta recodificar, de las que están en disco."""
    hay = [f for f in frases if (carpeta / nombre_de(f, voz)).exists()]
    with cf.ThreadPoolExecutor(max_workers=hilos) as pool:
        hechas = list(pool.map(lambda f: recodificar(carpeta / nombre_de(f, voz)), hay))
    return [f for f, h in zip(hay, hechas) if h]


def leer_mudos(carpeta: pathlib.Path) -> set[str]:
    try:
        return set(json.loads((carpeta / MUDOS).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return set()


def anotar_mudos(carpeta: pathlib.Path, textos) -> set[str]:
    """Suma, nunca reemplaza: una corrida de una tanda no puede borrar lo que
    encontró la anterior."""
    todos = leer_mudos(carpeta) | set(textos)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / MUDOS).write_text(
        json.dumps(sorted(todos), ensure_ascii=False, indent=0), encoding="utf-8")
    return todos


def buscar_mudos(frases: list[str], carpeta: pathlib.Path, voz: str = VOZ,
                 hilos: int = 8) -> list[str]:
    """Mide los que ya están en disco. Es el barrido de una vez, no de cada
    construcción del sitio: son 11.378 llamadas a ffmpeg."""
    hay = [f for f in frases if (carpeta / nombre_de(f, voz)).exists()]
    with cf.ThreadPoolExecutor(max_workers=hilos) as pool:
        juicios = list(pool.map(lambda f: mudo(carpeta / nombre_de(f, voz)), hay))
    return [f for f, m in zip(hay, juicios) if m]


def faltan(frases: list[str], carpeta: pathlib.Path, voz: str = VOZ) -> list[str]:
    """Lo que ya está en disco no se vuelve a pagar. Un archivo vacío no cuenta:
    es una descarga que se cortó.

    La voz entra en el nombre, así que probar otra no borra ni pisa la primera:
    son dos juegos de archivos y se puede comparar."""
    mudas = leer_mudos(carpeta)
    return [f for f in frases
            if f not in mudas
            and (not (carpeta / nombre_de(f, voz)).exists()
                 or (carpeta / nombre_de(f, voz)).stat().st_size == 0)]


def escribir_indice(frases: list[str], carpeta: pathlib.Path, voz: str = VOZ) -> int:
    """Texto → archivo, pero solo de lo que de verdad se puede oír.

    «Se puede oír» son tres cosas y no una: que el archivo esté, que no esté
    vacío y que no sea silencio. Un texto que está en `mudos.json` no entra,
    así que el sitio no le pone ▶ y nadie pulsa un botón que no suena."""
    mudas = leer_mudos(carpeta)
    indice = {f: nombre_de(f, voz) for f in frases
              if f not in mudas
              and (carpeta / nombre_de(f, voz)).exists()
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
            hilos: int = HILOS) -> list[str]:
    """Devuelve las frases que de verdad se escribieron, no cuántas.

    Hacen falta una por una para medirlas justo después: una que vuelva en
    silencio tiene que quedar anotada en la misma corrida, o el ▶ mudo se
    publica y nadie se entera hasta que alguien lo pulsa."""
    carpeta.mkdir(parents=True, exist_ok=True)
    hechas = []
    with cf.ThreadPoolExecutor(max_workers=hilos) as pool:
        pedidos = {pool.submit(_una, t, carpeta, cliente, voz): t for t in frases}
        for i, fut in enumerate(cf.as_completed(pedidos), 1):
            fallo = fut.result()
            if fallo:
                print(f"  [{i}/{len(frases)}] falló «{pedidos[fut][:40]}»: {fallo}")
            else:
                hechas.append(pedidos[fut])
            if i % 250 == 0:
                print(f"  {i}/{len(frases)}", flush=True)
    return hechas


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ver", action="store_true", help="dice qué haría y qué costaría, sin gastar")
    p.add_argument("--muestra", type=int, metavar="N",
                   help="locuta solo N frases, para oír la voz antes de pagarlas todas")
    p.add_argument("--voz", default=VOZ, choices=VOCES,
                   help=f"la voz de OpenAI (por defecto {VOZ})")
    p.add_argument("--carpeta", type=pathlib.Path, default=AUDIO)
    p.add_argument("--mudos", action="store_true",
                   help="mide los audios que ya están en disco y aparta los que son silencio")
    p.add_argument("--reintentar", action="store_true",
                   help="borra los audios apartados por mudos para volver a pedirlos")
    p.add_argument("--recodificar", action="store_true",
                   help=f"baja a {BITS // 1000} kbps lo que esté en disco por encima")
    a = p.parse_args(argv)

    frases = todas_las_frases(plan.cargar())

    if a.reintentar:
        # Un silencio puede ser la letra —la «h» española no se pronuncia— o
        # un fallo suelto de la API en una frase normal, y desde fuera se ven
        # igual. Esto borra los archivos y la lista, y la corrida siguiente
        # los vuelve a pedir; lo que vuelva mudo otra vez se aparta solo, así
        # que reintentar no puede dejar un ▶ que no suena.
        mudas = sorted(leer_mudos(a.carpeta))
        for f in mudas:
            (a.carpeta / nombre_de(f, a.voz)).unlink(missing_ok=True)
        (a.carpeta / MUDOS).unlink(missing_ok=True)
        print(f"{len(mudas)} audios mudos borrados · cuestan "
              f"{coste(mudas):.4f} USD volver a pedirlos")
        print("Ahora: .venv/bin/python scripts/generar_audio.py")
        return 0

    if a.recodificar:
        # El barrido de una vez, para lo que ya estaba en disco antes de que
        # esto fuera automático. No gasta un céntimo y es idempotente.
        tocadas = recodificar_todo(frases, a.carpeta, a.voz)
        print(f"{len(tocadas)} recodificadas a {BITS // 1000} kbps")
        print("Ahora: .venv/bin/python scripts/construir_sitio.py")
        return 0

    if a.mudos:
        # El barrido de una vez, para lo que ya estaba locutado antes de que
        # esta comprobación existiera. No gasta un céntimo: solo mide.
        callados = buscar_mudos(frases, a.carpeta, a.voz)
        for f in callados:
            print(f"  silencio: «{f}»")
        todos = anotar_mudos(a.carpeta, callados)
        print(f"{len(callados)} mudos en esta pasada · {len(todos)} apartados en total")
        print(f"índice con {escribir_indice(frases, a.carpeta, a.voz)} frases")
        print("Ahora: .venv/bin/python scripts/construir_sitio.py")
        return 0
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

    hechas = generar(pendientes, a.carpeta, OpenAI(), a.voz)
    # Se recodifica AQUÍ y no a mano: es el paso que el repositorio exige
    # antes del primer commit, y mientras vivió en la memoria de quien
    # corriera el guion se olvidó una vez.
    bajadas = [f for f in hechas if recodificar(a.carpeta / nombre_de(f, a.voz))]
    if bajadas:
        print(f"\n{len(bajadas)} recodificadas a {BITS // 1000} kbps")
    # Se miden SOLO las de esta tanda: son pocas y es el momento de enterarse.
    # El barrido de todo el disco es `--mudos`.
    callados = [f for f in hechas if mudo(a.carpeta / nombre_de(f, a.voz))]
    if callados:
        anotar_mudos(a.carpeta, callados)
        print(f"\n{len(callados)} volvieron en silencio y se apartan (sin ▶):")
        for f in callados[:10]:
            print(f"  «{f}»")
    total = escribir_indice(frases, a.carpeta, a.voz)
    print(f"\n{len(hechas)} audios nuevos · índice con {total} frases")
    if a.muestra:
        print(f"Escúchalas en {a.carpeta} y, si la voz te vale, córrelo sin --muestra.")
    else:
        print("Ahora: .venv/bin/python scripts/construir_sitio.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
