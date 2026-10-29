#!/usr/bin/env python3
"""Cinco preguntas de opción múltiple con el vocabulario de la propia lección.

Es el test que el profesor echaba en falta al final de cada día. Se le dijo
que rematar las 365 lecciones con cinco preguntas serían unas 1.100 preguntas
nuevas de trabajo de contenido, y **eso era falso**: las palabras ya están
escritas y traducidas en la tabla `Словарь дня` de cada lección, así que las
preguntas se arman de lo que hay. Cero contenido nuevo.

Lo que esto NO hace, y es deliberado:

- **No inventa el enunciado ni la traducción.** Las dos columnas salen de la
  tabla que el profesor escribió y revisó. Si una entrada no se puede usar sin
  dudas, se descarta ella sola; si quedan menos de `MINIMO`, esa lección se
  queda exactamente como está hoy. Es el contrato de `pruebas.py` y de
  `huecos.py`, y por la misma razón: decirle a alguien que falló cuando acertó
  es lo que este proyecto no hace.
- **No saca distractores de otras lecciones.** Son las otras palabras del
  MISMO día, así que el ejercicio es «reconozca las palabras de hoy» y no una
  mezcla con material de hace seis meses. De paso no hace falta leer el curso
  entero para construir una lección.

El sentido de la pregunta es **ruso → español**: se enseña la traducción y se
elige la palabra española. Es la dirección que cuesta —producir— y la que el
examen pide; al revés sería reconocer, que ya hacen las tarjetas.
"""
from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import exportar_anki  # noqa: E402

PREGUNTAS = 5
MINIMO = 4
OPCIONES = 3

# Los días que YA traen un test contestable no llevan éste: dos tests en la
# misma página son ruido, y además un `repaso` no tiene `Словарь дня`.
SIN_QUIZ = ("prueba", "repaso", "examen", "simulacro", "proyecto", "reserva")

# Lo que descalifica una entrada. No es una lista de gustos: cada marca
# significa que la celda no es una traducción limpia de una palabra.
#   ✗ ↔ 🌎   avisos y variantes      «el conductor (✗ не «кондуктор»)»
#   + =      la entrada es una construcción  «hay que + инф.»
#   ( )      una glosa dentro         «la estación (del año)»
#   /        dos palabras en una      «sí / no»
SUCIA = re.compile(r"[✗↔🌎+=()/]")
# Una letra latina en la columna rusa quiere decir que ahí hay otra cosa: la
# variante americana («el zumo → el jugo») o una corrección. Es el mismo
# filtro que `construir_sitio.NO_ES_TRADUCCION` y por el mismo motivo.
LATINA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")
CIRILICA = re.compile(r"[А-Яа-яЁё]")


def limpiar(celda: str) -> str:
    """Quita las negritas con que el curso marca la sílaba tónica.

    `la **ca**sa` es la entrada y `la casa` la palabra. Sin esto el alumno
    leería los asteriscos."""
    return re.sub(r"\*+", "", str(celda or "")).strip()


def usables(filas: list) -> list[tuple[str, str]]:
    """Las entradas de las que se puede hacer una pregunta sin dudas."""
    vistas_es: dict[str, int] = {}
    vistas_ru: dict[str, int] = {}
    limpias = []
    for fila in filas or []:
        if len(fila) < 2:
            continue
        es, ru = limpiar(fila[0]), limpiar(fila[1])
        if not es or not ru:
            continue
        if SUCIA.search(es) or SUCIA.search(ru):
            continue
        if CIRILICA.search(es) or LATINA.search(ru):
            continue
        limpias.append((es, ru))
        vistas_es[es.lower()] = vistas_es.get(es.lower(), 0) + 1
        vistas_ru[ru.lower()] = vistas_ru.get(ru.lower(), 0) + 1
    # Una traducción repetida haría una pregunta con DOS respuestas correctas,
    # y una palabra española repetida, dos opciones iguales. Las dos salen de
    # la tabla, así que se descartan aquí y no se arreglan.
    return [(es, ru) for es, ru in limpias
            if vistas_es[es.lower()] == 1 and vistas_ru[ru.lower()] == 1]


def _permutacion(semilla: int, largo: int) -> list[int]:
    """Fisher-Yates con el MINSTD, el mismo que reparte los mensajes de ánimo.

    Determinista a propósito: reconstruir el sitio no puede mover ninguna
    respuesta, o cada publicación cambiaría el test de 256 lecciones."""
    s = ((semilla + 1) * 48271) % 2147483647
    p = list(range(largo))
    for k in range(largo - 1, 0, -1):
        s = (s * 48271) % 2147483647
        j = (s >> 8) % (k + 1)
        p[k], p[j] = p[j], p[k]
    return p


def _barajar_sin_ciclo(reparto: list[int], semilla: int) -> list[int]:
    """Baraja el reparto y rechaza las secuencias que se aprenden de memoria.

    Una escalera —а-б-в-а-б— reparte igual de bien en el recuento y se adivina
    en dos lecciones, que es el mismo defecto con otra cara. Se prueban varias
    semillas y se devuelve la primera que no lo sea; si ninguna sirve, se
    devuelve la última, porque un reparto repetitivo es mucho mejor que
    quedarse sin preguntas."""
    for intento in range(8):
        mezcla = _permutacion(semilla * 7 + 1 + intento * 101, len(reparto))
        sitios = [reparto[j] for j in mezcla]
        if len(sitios) < 3:
            return sitios
        paso = (sitios[1] - sitios[0]) % OPCIONES
        escalera = all((sitios[i + 1] - sitios[i]) % OPCIONES == paso
                       for i in range(len(sitios) - 1))
        tres = any(sitios[i] == sitios[i + 1] == sitios[i + 2]
                   for i in range(len(sitios) - 2))
        if not escalera and not tres:
            return sitios
    return sitios


def preguntas_de(ruta: pathlib.Path, numero: int | None = None) -> list[dict]:
    """Las preguntas de una lección, o `[]` si no se puede hacer ninguna."""
    datos, filas = exportar_anki.filas_de(ruta)
    if (datos or {}).get("tipo") in SIN_QUIZ:
        return []
    buenas = usables(filas)
    if len(buenas) < MINIMO:
        return []
    if numero is None:
        numero = int((datos or {}).get("numero") or 0) or _numero_de(ruta)

    # Cuáles de las entradas se preguntan: las `PREGUNTAS` primeras de una
    # mezcla que depende de la lección. Siempre las primeras de la tabla sería
    # no preguntar nunca por las últimas palabras del día.
    orden = _permutacion(numero, len(buenas))
    elegidas = [buenas[i] for i in orden[:min(PREGUNTAS, len(buenas))]]

    # Dónde cae la respuesta correcta. Dos cosas a la vez, y las dos están
    # aprendidas en este proyecto:
    #
    #  - REPARTIDA, porque el 2026-10-27 se midió que catorce de quince
    #    respuestas de un test de unidad eran la б) y marcando todo б se
    #    aprobaba la unidad sin saber nada. Se parte de un reparto ya
    #    equilibrado (2-2-1 con cinco preguntas) y se baraja.
    #  - SIN CICLO. `sitios[i % OPCIONES]` reparte igual de bien y deja la
    #    secuencia а-б-в-а-б, que se aprende de memoria en dos lecciones. Es
    #    exactamente el defecto que ya tuvieron la letra correcta de los tests
    #    y los mensajes de ánimo, con otra cara.
    # El `+ numero` rota cuál es la opción que sale una vez menos. Sin él, con
    # cinco preguntas y tres opciones el reparto de base es siempre 2-2-1 con
    # la MISMA corta, y sobre las 244 lecciones eso daba 488-466-244: la
    # tercera opción valía la mitad que las otras dos en todo el curso.
    reparto = [(i + numero) % OPCIONES for i in range(len(elegidas))]
    sitios = _barajar_sin_ciclo(reparto, numero)

    preguntas = []
    for i, (es, ru) in enumerate(elegidas):
        otras = [o for o in buenas if o[0] != es]
        mezcla = _permutacion(numero * 31 + i, len(otras))
        distractores = [otras[j][0] for j in mezcla[:OPCIONES - 1]]
        if len(distractores) < OPCIONES - 1:
            continue
        correcta = sitios[i]
        opciones = list(distractores)
        opciones.insert(correcta, es)
        preguntas.append({"ru": ru, "opciones": opciones, "correcta": correcta})
    return preguntas if len(preguntas) >= MINIMO else []


def _numero_de(ruta: pathlib.Path) -> int:
    m = re.search(r"semana-(\d+)[/\\]dia-(\d+)", str(ruta))
    return (int(m.group(1)) - 1) * 7 + int(m.group(2)) if m else 1


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ver", action="store_true", help="cuántas lecciones lo tendrían")
    ap.add_argument("leccion", nargs="?", help="curso/semana-01/dia-1.md")
    a = ap.parse_args(argv)

    if a.leccion:
        for q in preguntas_de(pathlib.Path(a.leccion)):
            marca = [" "] * len(q["opciones"])
            marca[q["correcta"]] = "✓"
            print(f'  {q["ru"]}')
            for s, o in zip(marca, q["opciones"]):
                print(f'    {s} {o}')
        return 0

    con = sin = total = 0
    letras: dict[int, int] = {}
    for ruta in sorted((RAIZ / "curso").glob("semana-*/dia-*.md")):
        qs = preguntas_de(ruta)
        if qs:
            con += 1
            total += len(qs)
            for q in qs:
                letras[q["correcta"]] = letras.get(q["correcta"], 0) + 1
        else:
            sin += 1
    print(f"lecciones con quiz : {con}")
    print(f"lecciones sin quiz : {sin}")
    print(f"preguntas en total : {total}")
    print(f"reparto de la correcta: {dict(sorted(letras.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
