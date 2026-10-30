#!/usr/bin/env python3
"""Las tarjetas que la propia lección pide, sacadas de los días anteriores.

Lo trajo el profesor mirando la lección 2 en el móvil: el apartado «Разминка»
dice **«Карточки: 8 слов вчерашнего дня. Скажите перевод вслух, прежде чем
перевернуть»** —«tarjetas: 8 palabras de ayer; diga la traducción en voz alta
antes de dar la vuelta»— y preguntó dónde están. No están. Contado:

    lecciones que piden tarjetas .............. 285 de 365
    con palabras anteriores suficientes ....... 285

O sea que **285 lecciones le piden al alumno girar unas fichas que la página
no le enseña**. Hasta hoy solo existían como descarga de Anki, que necesita
instalar una aplicación; quien estudia en el móvil leía «dé la vuelta» y no
tenía nada que girar.

Y las 285 se arman **sin escribir una palabra**: las que pide cada día son las
de los días anteriores, que ya están en el repositorio con su traducción y su
voz.

Lo que decide el contenido, y conviene saberlo si alguien lo toca:

- **Cuántas las dice la propia lección**, no una constante de aquí. Unas piden
  8, otras 10 y las de repaso 20 («20 слов всей недели»). Un número fijo
  contradiría al texto que el alumno está leyendo tres renglones más arriba.
- **De dónde salen: de los días ANTERIORES, caminando hacia atrás.** Eso es lo
  que significan las dos formas que el curso usa —«вчерашнего дня» y «всей
  недели»— sin tener que entender cuál es cuál: con 8 se queda en ayer y con
  20 llega a la semana.
- **Falla de forma segura**, como `pruebas.py` y `huecos.py`: sin la línea
  «Карточки:» no hay bloque. La lección 1 dice «hoy es el primer día, todavía
  no hay tarjetas» y ofrece otra cosa — está bien escrita, y el hueco empieza
  en la 2.
"""
from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import exportar_anki  # noqa: E402
import quiz_lexico  # noqa: E402

# «Карточки: 8 слов…», «Карточки: 20 слов — вся неделя», «Карточки: 10 слов.»
PIDE = re.compile(r"Карточки:\s*(\d+)\s*слов")
MINIMO = 4          # menos de cuatro no es un repaso, es un adorno
TOPE = 24           # ni la lección más pedigüeña pasa de 20


def cuantas_pide(texto: str) -> int | None:
    """Cuántas tarjetas pide esta lección, o `None` si no pide ninguna."""
    m = PIDE.search(texto)
    if not m:
        return None
    n = int(m.group(1))
    return n if MINIMO <= n <= TOPE else None


def vocabulario_del_curso(dias) -> dict[int, list[tuple[str, str]]]:
    """El vocabulario de cada lección, leído UNA vez.

    Se pasa hecho a `del_dia` porque si no habría que releer las 365 lecciones
    una vez por lección, o sea 133.225 lecturas para el mismo resultado."""
    salida: dict[int, list[tuple[str, str]]] = {}
    for d in dias:
        if not d.ruta.exists():
            continue
        _, filas = exportar_anki.filas_de(d.ruta)
        buenas = []
        for fila in filas or []:
            if len(fila) < 2:
                continue
            es, ru = quiz_lexico.limpiar(fila[0]), quiz_lexico.limpiar(fila[1])
            # La columna rusa tiene que traer ruso: a veces es la variante
            # americana («el zumo → el jugo», regla 8) y una tarjeta que
            # promete la traducción enseñaría español en los dos lados.
            if es and ru and quiz_lexico.CIRILICA.search(ru):
                buenas.append((es, ru))
        salida[d.numero] = buenas
    return salida


def del_dia(numero: int, cuantas: int, vocabulario: dict,
            audio: dict | None = None) -> list[dict]:
    """Las tarjetas de la lección `numero`, de los días anteriores.

    En orden del curso —la más antigua primero— y no en el del paseo hacia
    atrás: el alumno las vio en ese orden y las recuerda en ese orden."""
    audio = audio or {}
    elegidas: list[tuple[str, str]] = []
    n = numero - 1
    while n >= 1 and len(elegidas) < cuantas:
        # Del día más reciente hacia atrás, pero dentro de un día en el orden
        # de su tabla. Del día más viejo se cogen las ÚLTIMAS que hagan falta
        # y no las primeras: así las tarjetas son exactamente «las N últimas
        # palabras que aprendiste», seguidas y sin un hueco en medio.
        falta = cuantas - len(elegidas)
        elegidas = vocabulario.get(n, [])[-falta:] + elegidas
        n -= 1
    if len(elegidas) < MINIMO:
        return []
    return [{"es": es, "ru": ru,
             "mp3": (audio.get(es) or "").removesuffix(".mp3")}
            for es, ru in elegidas]


def de_la_leccion(d, vocabulario: dict, audio: dict | None = None) -> list[dict]:
    """Las tarjetas de un día, o `[]` si su lección no pide ninguna."""
    if not d.ruta.exists():
        return []
    cuantas = cuantas_pide(d.ruta.read_text(encoding="utf-8"))
    if not cuantas:
        return []
    return del_dia(d.numero, cuantas, vocabulario, audio)


def main(argv=None) -> int:
    import argparse
    import json

    import plan

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("leccion", nargs="?", type=int, help="el número de un día")
    a = ap.parse_args(argv)

    cal = plan.cargar()
    dias = plan.dias(cal)
    vocab = vocabulario_del_curso(dias)
    indice = RAIZ / "docs" / "audio" / "indice.json"
    audio = json.loads(indice.read_text(encoding="utf-8")) if indice.exists() else {}

    if a.leccion:
        d = next(x for x in dias if x.numero == a.leccion)
        fichas = de_la_leccion(d, vocab, audio)
        print(f"lección {d.numero}: {len(fichas)} tarjetas")
        for f in fichas:
            print(f"   {f['es']:<28} {f['ru']}{'  ▶' if f['mp3'] else ''}")
        return 0

    piden = con = sin = 0
    for d in dias:
        if not d.ruta.exists():
            continue
        if cuantas_pide(d.ruta.read_text(encoding="utf-8")):
            piden += 1
            if de_la_leccion(d, vocab, audio):
                con += 1
            else:
                sin += 1
    print(f"lecciones que piden tarjetas : {piden}")
    print(f"  con tarjetas que enseñar   : {con}")
    print(f"  sin material suficiente    : {sin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
