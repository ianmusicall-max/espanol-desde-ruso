#!/usr/bin/env python3
"""La baraja de Anki del curso, con el dibujo y la voz dentro.

    .venv/bin/python scripts/exportar_apkg.py --ver   # qué haría, sin escribir
    .venv/bin/python scripts/exportar_apkg.py         # escribe docs/vocabulario/

El curso está construido sobre las tarjetas y no era un añadido: 92 de las 100
lecciones empiezan con «Карточки: 10 слов» y 87 cierran con «añade 5 palabras a
tu baraja». Lo que faltaba era la baraja.

`exportar_anki.py` ya sacaba el vocabulario a TSV y se queda: un TSV lo abre
Excel, Google Sheets, Quizlet y cualquier app de tarjetas, así que el alumno de
iPhone que no quiera pagar AnkiMobile no se queda fuera. Lo que el TSV NO puede
llevar son los medios, y de ahí este `.apkg`: un solo archivo que se abre de un
clic con los 305 dibujos y las 905 voces dentro.

**Dos tipos de tarjeta, y el segundo es el que importa:**

1. `español → русский`, que entrena a traducir.
2. `dibujo → español`, que entrena a PENSAR en español sin pasar por el ruso,
   que es lo que se quiere a la salida de un A2 y lo que el ruso frena. Solo se
   crea cuando hay dibujo, con la plantilla condicional de Anki: un reverso
   vacío sería una tarjeta imposible de contestar.

**Los identificadores son fijos y eso no es un detalle de estilo.** Anki
reconoce una baraja, un modelo y una nota por su id. Si se generaran al azar en
cada corrida, volver a importar no actualizaría la baraja del alumno: le
crearía otra al lado y perdería meses de repasos. Se derivan de un texto fijo,
así que la baraja de mañana es la misma de hoy con las palabras nuevas.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import exportar_anki  # noqa: E402
import generar_audio  # noqa: E402
import generar_imagenes  # noqa: E402
import plan  # noqa: E402

DESTINO = RAIZ / "docs" / "vocabulario"
AUDIO = RAIZ / "docs" / "audio"
IMG = RAIZ / "docs" / "img"
ARCHIVO = "espanol-desde-ruso.apkg"
# El manifiesto: cuatro números y un nombre. El sitio lo lee para pintar el
# bloque de descarga, igual que lee los `indice.json` del audio y los dibujos.
#
# Existe para que construir el sitio NO tenga que abrir un archivo de 22 MB ni
# recontar el vocabulario: el que sabe cuántas tarjetas tiene la baraja es
# quien la acaba de armar. Y de paso la prueba que compara `docs/` puede
# copiarlo entero sin arrastrar los 22 MB.
MANIFIESTO = "baraja.json"

# Lo que ve el alumno. En ruso, como el curso.
BARAJA = "Испанский с нуля"
MODELO = "Испанский с нуля — слово"


def _id(texto: str) -> int:
    """Un identificador FIJO a partir de un texto fijo.

    Anki reconoce baraja, modelo y nota por su id. Con ids al azar, volver a
    importar no actualiza la baraja del alumno: le crea otra al lado y pierde
    sus repasos. Es el único fallo de este guion que no se vería hasta meses
    después y en el ordenador de otro."""
    return int(hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12], 16)


CAMPOS = ["Espanol", "Ruso", "Ejemplo", "Imagen", "Audio", "Leccion",
          "Todos"]

# El estilo: la paleta del sitio, para que la baraja no parezca de otra casa.
ESTILO = """
.card { font-family: -apple-system, system-ui, sans-serif; font-size: 22px;
        text-align: center; color: #2b2b2b; background: #f4f1ea; padding: 18px; }
.nightMode.card { color: #e8e6e1; background: #23211e; }
.es { font-size: 30px; font-weight: 600; }
.ru { font-size: 24px; }
.ej { font-size: 18px; color: #6b665e; margin-top: 10px; font-style: italic; }
.nightMode .ej { color: #a8a299; }
.dib { max-width: 260px; max-height: 260px; border-radius: 10px; }
.de { font-size: 13px; color: #8a847b; margin-top: 14px; }
hr#answer { border: 0; border-top: 1px solid #d8d2c7; margin: 16px 0; }
"""

# La segunda plantilla va envuelta en {{#Imagen}}…{{/Imagen}}: Anki NO crea esa
# tarjeta cuando el campo está vacío. Sin eso, las 603 palabras sin dibujo
# tendrían una tarjeta con el anverso en blanco, imposible de contestar.
PLANTILLAS = [
    {
        "name": "español → русский",
        "qfmt": '<div class="es">{{Espanol}}</div>{{Audio}}',
        "afmt": '{{FrontSide}}<hr id="answer">'
                '<div class="ru">{{Ruso}}</div>'
                '{{#Ejemplo}}<div class="ej">{{Ejemplo}}</div>{{/Ejemplo}}'
                '{{#Leccion}}<div class="de">{{Leccion}}</div>{{/Leccion}}',
    },
    {
        "name": "рисунок → español",
        "qfmt": '{{#Imagen}}{{Imagen}}{{/Imagen}}',
        "afmt": '{{FrontSide}}<hr id="answer">'
                '<div class="es">{{Espanol}}</div>{{Audio}}'
                '<div class="ru">{{Ruso}}</div>'
                '{{#Leccion}}<div class="de">{{Leccion}}</div>{{/Leccion}}',
    },
    # El sentido de vuelta. Va envuelta en {{#Todos}} por el mismo motivo que
    # la de arriba en {{#Imagen}}, y además resuelve lo único que este sentido
    # tiene de difícil: 171 palabras rusas tienen varios españoles, y si cada
    # nota sacara su tarjeta habría 171 anversos repetidos con respuestas
    # distintas, que en repaso espaciado es ruido puro. Solo UNA nota de cada
    # grupo lleva `Todos` —y lleva todas las respuestas—, así que sale una
    # tarjeta por palabra rusa y enseña las cinco formas de decir «автобус».
    {
        "name": "русский → español",
        "qfmt": '{{#Todos}}<div class="ru">{{Ruso}}</div>{{/Todos}}',
        "afmt": '{{FrontSide}}<hr id="answer">'
                '<div class="es">{{Todos}}</div>{{Audio}}'
                '{{#Ejemplo}}<div class="ej">{{Ejemplo}}</div>{{/Ejemplo}}'
                '{{#Leccion}}<div class="de">{{Leccion}}</div>{{/Leccion}}',
    },
]


def reversos(tarjetas: list[tuple]) -> dict[int, str]:
    """Qué nota de cada entrada rusa saca la tarjeta de vuelta, y con qué.

    Devuelve {posición de la nota: todos sus españoles}. Las demás notas del
    grupo se quedan con `Todos` vacío y por tanto sin esa tarjeta. La elegida
    es la primera del curso, que es la que lo enseña antes."""
    salida = {}
    for grupo in exportar_anki.agrupar_por_ruso([t[1] for t in tarjetas]):
        dichos = list(dict.fromkeys(tarjetas[i][0] for i in grupo))
        salida[grupo[0]] = " · ".join(dichos)
    return salida


def tarjetas_del_curso(cal) -> list[tuple]:
    """(español, ruso, ejemplo, etiquetas) sin repetir y en el orden del curso.

    Si dos lecciones enseñan la misma entrada, se queda la primera: es la que
    la presenta como nueva, y la segunda ya la da por sabida."""
    vistas: dict[str, tuple] = {}
    for d in plan.dias(cal):
        if d.ruta.exists():
            for t in exportar_anki.tarjetas_de(d.ruta):
                vistas.setdefault(t[0], t)
    return list(vistas.values())


def _unidad_de(etiquetas: str) -> str:
    """La subbaraja: `Испанский с нуля::Юнит 03`.

    Por unidad y no por semana porque son 24 contra 52, y porque la unidad es
    lo que el curso presenta como un bloque cerrado con su prueba al final."""
    for e in etiquetas.split():
        if e.startswith("U") and e[1:].isdigit():
            return f"{BARAJA}::Юнит {int(e[1:]):02d}"
    return BARAJA


def _clave_de_audio(español: str, audio: dict) -> str:
    """Con qué nombre buscar la voz de esta entrada en el índice.

    Primero la entrada tal cual. Si no está, su parte española: `hay que +
    инф.` se locuta como `hay que`, porque la etiqueta rusa explica cómo se
    usa la palabra y no es algo que nadie quiera oír. Sin esta reserva, 103
    tarjetas de 3.001 salían mudas."""
    limpio = exportar_anki.limpiar(español)
    if limpio in audio:
        return limpio
    return generar_audio.parte_espanola(limpio)


def armar(tarjetas: list[tuple], audio: dict, imagenes: dict):
    """La baraja y la lista de medios que hay que meter en el zip."""
    import genanki

    modelo = genanki.Model(_id(MODELO), MODELO, fields=[{"name": c} for c in CAMPOS],
                           templates=PLANTILLAS, css=ESTILO)

    barajas: dict[str, object] = {}
    medios: set[pathlib.Path] = set()

    vuelta = reversos(tarjetas)

    for puesto, (español, ruso, ejemplo, etiquetas) in enumerate(tarjetas):
        limpio_audio = _clave_de_audio(español, audio)
        limpio_img = generar_imagenes.limpiar(español)

        campo_audio, campo_img = "", ""
        if limpio_audio in audio:
            campo_audio = f"[sound:{audio[limpio_audio]}]"
            medios.add(AUDIO / audio[limpio_audio])
        if limpio_img in imagenes:
            campo_img = f'<img class="dib" src="{imagenes[limpio_img]}">'
            medios.add(IMG / imagenes[limpio_img])

        nombre = _unidad_de(etiquetas)
        if nombre not in barajas:
            barajas[nombre] = genanki.Deck(_id(nombre), nombre)

        barajas[nombre].add_note(genanki.Note(
            model=modelo,
            # El guid sale de la palabra, no del orden: así volver a importar
            # ACTUALIZA la nota en vez de duplicarla, y cambiar el reparto de
            # unidades no le borra los repasos al alumno.
            guid=genanki.guid_for(f"esru::{español}"),
            fields=[español, ruso, ejemplo, campo_img, campo_audio, etiquetas,
                    vuelta.get(puesto, "")],
            tags=etiquetas.split(),
        ))

    return genanki.Package(list(barajas.values())), sorted(medios), barajas


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ver", action="store_true", help="dice qué haría, sin escribir")
    p.add_argument("--destino", type=pathlib.Path, default=DESTINO)
    a = p.parse_args(argv)

    tarjetas = tarjetas_del_curso(plan.cargar())

    def leer(ruta):
        try:
            return json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    audio = leer(AUDIO / "indice.json")
    imagenes = leer(IMG / "indice.json")

    con_a = sum(1 for t in tarjetas if _clave_de_audio(t[0], audio) in audio)
    con_i = sum(1 for t in tarjetas if generar_imagenes.limpiar(t[0]) in imagenes)
    vuelta = len(reversos(tarjetas))
    print(f"{len(tarjetas)} notas · {con_a} con voz · {con_i} con dibujo · "
          f"{vuelta} entradas rusas")

    if a.ver:
        print(f"escribiría {a.destino / ARCHIVO}")
        return 0

    try:
        paquete, medios, barajas = armar(tarjetas, audio, imagenes)
    except ImportError:
        print("falta el paquete: .venv/bin/pip install genanki")
        return 1

    faltan = [m for m in medios if not m.exists()]
    if faltan:
        print(f"faltan {len(faltan)} medios, p.ej. {faltan[0]}")
        return 1

    paquete.media_files = [str(m) for m in medios]
    a.destino.mkdir(parents=True, exist_ok=True)
    salida = a.destino / ARCHIVO
    paquete.write_to_file(salida)

    (a.destino / MANIFIESTO).write_text(json.dumps({
        "archivo": ARCHIVO,
        "bytes": salida.stat().st_size,
        "palabras": len(tarjetas),
        "con_voz": con_a,
        "con_dibujo": con_i,
        "subbarajas": len(barajas),
        "entradas_rusas": vuelta,
    }, ensure_ascii=False, indent=0), encoding="utf-8")

    print(f"{len(barajas)} subbarajas · {len(medios)} medios")
    print(f"{salida}  ·  {salida.stat().st_size / 1e6:.1f} MB")
    print(f"{a.destino / MANIFIESTO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
