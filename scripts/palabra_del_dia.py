#!/usr/bin/env python3
"""La palabra del día para el canal de Telegram, armada de lo que ya hay.

El 2026-10-27 se decidió que **Telegram es el canal**: es donde vive el
público rusohablante fuera de Rusia y su umbral de monetización es
alcanzable. Y se anotó entonces que el curso ya tiene con qué alimentarlo sin
escribir nada nuevo. Contado el 2026-10-30:

    palabras del curso ......... 2 985     o sea 8 años y 65 días
    con voz .................... 2 883
    con frase de ejemplo ....... 2 095
    con dibujo .................   263

Así que una publicación diaria **no cuesta ni un céntimo ni una línea de
contenido**: la palabra, su traducción, su frase, su voz y el enlace a la
lección que la enseña salen de lo que el profesor ya escribió y revisó.

**Van en el ORDEN DEL CURSO y no al azar.** Quien siga el canal está haciendo
una versión lenta del curso, y el enlace de cada día apunta a la lección que
toca; barajadas, el canal sería una lista de palabras sueltas y el enlace no
diría nada.

**Qué día sale cuál se calcula de la FECHA, no de un contador en disco**
(`telegram.desde` en `web/sitio.yaml`). Dos motivos: correrlo dos veces el
mismo día publica lo mismo —un cron que se dispara dos veces no adelanta el
canal— y no hay ningún estado que se pueda perder o desincronizar.

**El envío NO está probado de punta a punta desde este contenedor**:
`api.telegram.org` da `000` aquí, como Google y el Cervantes. Lo que sí está
probado es todo lo demás —qué palabra toca, qué texto sale y qué se adjunta—
y la forma del pedido, con un enviador de mentira. Quien lo prueba de verdad
es GitHub Actions, que sí tiene red.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import html
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import construir_sitio  # noqa: E402
import generar_audio  # noqa: E402
import plan  # noqa: E402

API = "https://api.telegram.org"
# Lo que Telegram admite como carátula de un audio: JPEG, 320 px de lado como
# mucho y menos de 200 kB. Los dibujos del curso son `.webp` de 512, así que
# hay que convertirlos: mandados tal cual, Telegram rechaza el envío ENTERO y
# las 263 publicaciones con dibujo se quedarían mudas sin que nadie supiera
# por qué. Está escrito en su documentación y no se puede comprobar desde
# aquí, porque `api.telegram.org` no se alcanza.
MINIATURA = 320
# `https://t.me/espanoldesderuso` -> `@espanoldesderuso`
ENLACE = re.compile(r"(?:https?://)?t\.me/(?:s/)?@?([A-Za-z0-9_]{4,})/?$")
# El token NUNCA se escribe aquí ni en el repositorio: sale del entorno, que
# en GitHub Actions es un secreto del repositorio.
VAR_TOKEN = "TELEGRAM_TOKEN"
VAR_CANAL = "TELEGRAM_CANAL"


def es_una_pareja(p: dict) -> bool:
    """¿La fila es una palabra y su traducción, o es una nota?

    Una publicación del canal promete «palabra — traducción», así que una
    fila que repite la palabra española DENTRO de la columna rusa no es una
    traducción: es una aclaración. La única del curso es

        tomar = и пить, и есть   ->   tomar = прежде всего пить

    y escrita así sale un «tomar = ... — tomar = ...» que se lee como una
    publicación rota.

    **Una de 2.985, y aun así la regla no es una lista con esa fila dentro**:
    una lista no vuelve a mirar nada el día que el profesor escriba otra
    igual. Y se escribe por la forma del defecto y no por lo que descarta
    hoy, porque las OTRAS doce filas con letras latinas en la columna rusa
    son glosas legítimas —`la palta (Арг., Чили, Перу)`, `(🌎 la alberca)`—
    y descartarlas sería perder material bueno por una de mentira.

    Se compara la PALABRA y no la celda entera: `tomar = и пить, и есть` no
    aparece tal cual dentro de la columna rusa, así que mirando la celda la
    regla no cazaba nada. La palabra la saca `generar_audio.parte_espanola`,
    que es el único sitio que sabe separar la glosa rusa de la española —se
    escribió el 2026-10-28 para rescatar estas mismas 103 filas del
    locutor—. Y se busca con frontera de palabra: sin ella, una entrada corta
    casaría dentro de cualquier paréntesis («(ser)», «(🌎 el básquet)»)."""
    palabra = generar_audio.parte_espanola(p["es"]).strip().lower()
    if not palabra:
        return True
    return re.search(rf"(?<!\w){re.escape(palabra)}(?!\w)", p["ru"].lower()) is None


def palabras(cfg=None, cal=None) -> list[dict]:
    """Las del curso, en el orden en que el curso las enseña."""
    cal = cal or plan.cargar()
    audio = construir_sitio.indice_de_audio(construir_sitio.DOCS)
    dibujos = construir_sitio.indice_de_imagenes(construir_sitio.DOCS)
    salida = [p for p in construir_sitio.palabras_del_curso(cal, audio, orden="curso")
              if es_una_pareja(p)]
    for p in salida:
        p["dibujo"] = dibujos.get(p["es"], "")
    return salida


def miniatura(dibujo: pathlib.Path, destino: pathlib.Path) -> pathlib.Path:
    """El dibujo convertido a lo que Telegram admite de carátula."""
    from PIL import Image

    with Image.open(dibujo) as im:
        im = im.convert("RGB")
        im.thumbnail((MINIATURA, MINIATURA))
        im.save(destino, "JPEG", quality=85)
    return destino


def canal_de(cfg: dict) -> str:
    """A dónde se publica, escrito en UN solo sitio.

    El pie de las 394 páginas enlaza `redes.telegram` y el publicador necesita
    `@handle`: son el mismo canal, así que se deriva del enlace en vez de
    pedirlo dos veces. `telegram.canal` sigue estando para el caso que el
    enlace no cubre —un canal privado, que es un id numérico— y para poder
    publicar antes de enseñarlo en el sitio."""
    tg = cfg.get("telegram") or {}
    if (tg.get("canal") or "").strip():
        return tg["canal"].strip()
    m = ENLACE.match(((cfg.get("redes") or {}).get("telegram") or "").strip())
    return f"@{m.group(1)}" if m else ""


def numero_del_dia(fecha: dt.date, desde: dt.date) -> int:
    """Qué publicación toca: la 1 el día de arranque."""
    return (fecha - desde).days + 1


def del_dia(lista: list[dict], n: int) -> dict | None:
    """La palabra número `n`, o `None` si el canal ya dio la vuelta entera.

    No se repite desde el principio a propósito: ocho años de publicaciones
    diarias son de sobra, y volver a empezar en silencio haría que el canal
    dijera «la palabra de hoy» de algo que ya salió. Si algún día llega, es
    una decisión y no un efecto."""
    return lista[n - 1] if 1 <= n <= len(lista) else None


def texto(p: dict, t: dict, dominio: str) -> str:
    """El cuerpo de la publicación, en HTML de Telegram.

    En ruso y solo en ruso: es el idioma del que lee el canal, igual que el
    test de nivel y por la misma razón."""
    e = html.escape
    lineas = [f"<b>{e(p['es'])}</b> — {e(p['ru'])}"]
    if p.get("ejemplo"):
        lineas += ["", f"<i>{e(p['ejemplo'])}</i>"]
    d = p["dia"]
    if dominio:
        url = f"{dominio}/semana-{d.semana:02d}/dia-{d.dia}.html"
        lineas += ["", f'{e(t["urok"])} {d.numero} · <a href="{e(url)}">{e(t["abrir"])}</a>']
    else:
        lineas += ["", f'{e(t["urok"])} {d.numero}']
    lineas += ["", " ".join(t["etiquetas"])]
    return "\n".join(lineas)


def _pedido(p: dict, cuerpo: str, canal: str) -> tuple[str, dict, dict]:
    """Qué método de la API toca y con qué.

    Devuelve `(metodo, campos, archivos)`. La voz manda sobre el dibujo: el
    96 % de las palabras la tiene y oírla es para lo que existe un canal de
    idiomas; el dibujo, que solo tienen 263, va de carátula cuando hay las
    dos cosas. Sin ninguna de las dos es un mensaje de texto y ya."""
    campos = {"chat_id": canal, "parse_mode": "HTML"}
    archivos: dict[str, pathlib.Path] = {}
    if p.get("mp3"):
        campos["caption"] = cuerpo
        campos["title"] = p["es"]
        archivos["audio"] = construir_sitio.DOCS / "audio" / f"{p['mp3']}.mp3"
        if p.get("dibujo"):
            archivos["thumbnail"] = construir_sitio.DOCS / "img" / p["dibujo"]
        return "sendAudio", campos, archivos

    if p.get("dibujo"):
        campos["caption"] = cuerpo
        archivos["photo"] = construir_sitio.DOCS / "img" / p["dibujo"]
        return "sendPhoto", campos, archivos
    campos["text"] = cuerpo
    campos["disable_web_page_preview"] = "true"
    return "sendMessage", campos, archivos


def _multipart(campos: dict, archivos: dict) -> tuple[bytes, str]:
    """El cuerpo del POST. A mano y sin dependencias: `requests` no está."""
    borde = "----palabradeldia" + os.urandom(8).hex()
    trozos: list[bytes] = []
    for k, v in campos.items():
        trozos.append(
            f'--{borde}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
            .encode("utf-8"))
    for k, ruta in archivos.items():
        trozos.append(
            f'--{borde}\r\nContent-Disposition: form-data; name="{k}"; '
            f'filename="{ruta.name}"\r\nContent-Type: application/octet-stream\r\n\r\n'
            .encode("utf-8"))
        trozos.append(ruta.read_bytes())
        trozos.append(b"\r\n")
    trozos.append(f"--{borde}--\r\n".encode("utf-8"))
    return b"".join(trozos), f"multipart/form-data; boundary={borde}"


def enviar(p: dict, cuerpo: str, token: str, canal: str, pedir=None) -> dict:
    """Publica, y devuelve lo que contestó Telegram.

    `pedir` existe para poder probar la FORMA del pedido sin red, que es lo
    único comprobable desde aquí: `api.telegram.org` no se alcanza."""
    metodo, campos, archivos = _pedido(p, cuerpo, canal)
    for nombre, ruta in archivos.items():
        if not ruta.exists():
            raise FileNotFoundError(f"falta {ruta} ({nombre})")
    if pedir is not None:
        return pedir(metodo, campos, archivos)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        if "thumbnail" in archivos:
            archivos = dict(archivos,
                            thumbnail=miniatura(archivos["thumbnail"],
                                                pathlib.Path(tmp) / "caratula.jpg"))
        return _enviar_ya(metodo, campos, archivos, token)


def _enviar_ya(metodo: str, campos: dict, archivos: dict, token: str) -> dict:
    datos, tipo = _multipart(campos, archivos)
    pet = urllib.request.Request(f"{API}/bot{token}/{metodo}", data=datos,
                                 headers={"Content-Type": tipo})
    try:
        with urllib.request.urlopen(pet, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # El cuerpo del error trae el motivo de Telegram, que es lo único que
        # sirve; el código solo dice que algo salió mal. Y NUNCA se imprime la
        # URL, que lleva el token dentro.
        raise SystemExit(f"Telegram respondió {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ver", action="store_true", help="enseña lo que publicaría, sin publicar")
    ap.add_argument("--dia", help="la fecha a publicar (AAAA-MM-DD); por defecto, hoy")
    ap.add_argument("--numero", type=int, help="salta la fecha y pide la publicación N")
    ap.add_argument("--telegram", action="store_true", help="publica de verdad")
    a = ap.parse_args(argv)

    cfg = construir_sitio.cargar_config()
    t = construir_sitio.cargar_textos()["canal"]
    tg = cfg.get("telegram") or {}
    lista = palabras(cfg)

    if a.numero:
        n = a.numero
    else:
        desde = tg.get("desde")
        if not desde:
            print("falta `telegram.desde` en web/sitio.yaml (el día en que arranca el canal).")
            print("Mientras no esté, --ver enseña la primera publicación.")
            n = 1
        else:
            fecha = dt.date.fromisoformat(a.dia) if a.dia else dt.date.today()
            n = numero_del_dia(fecha, dt.date.fromisoformat(str(desde)))

    p = del_dia(lista, n)
    if p is None:
        print(f"la publicación {n} no existe: el canal tiene {len(lista)} "
              f"({len(lista)//365} años y {len(lista)%365} días).")
        return 1

    cuerpo = texto(p, t, (cfg.get("dominio") or "").rstrip("/"))
    metodo, campos, archivos = _pedido(p, cuerpo, canal_de(cfg) or "@…")

    print(f"publicación {n} de {len(lista)} · {metodo}")
    print("-" * 60)
    print(cuerpo)
    print("-" * 60)
    for k, ruta in archivos.items():
        marca = "✓" if ruta.exists() else "FALTA"
        print(f"  {k:<10} {marca} {ruta.relative_to(RAIZ)}")
    if not archivos:
        print("  (sin voz ni dibujo: sale como mensaje de texto)")

    if not a.telegram:
        return 0

    token, canal = os.environ.get(VAR_TOKEN), os.environ.get(VAR_CANAL) or canal_de(cfg)
    if not token or not canal:
        print(f"\nfaltan {VAR_TOKEN} y/o el canal: no se publica nada.")
        return 1
    r = enviar(p, cuerpo, token, canal)
    if not r.get("ok"):
        print(f"\nTelegram dijo que no: {str(r)[:300]}")
        return 1
    print(f"\npublicado en {canal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
