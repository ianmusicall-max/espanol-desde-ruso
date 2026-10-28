#!/usr/bin/env python3
"""Revisa el léxico del curso entero: repeticiones y volumen acumulado.

El vocabulario de cada día vive en su tabla de «Словарь дня». Con varias
lecciones escritas por separado, lo que no se ve a simple vista es que la misma
palabra se enseñe dos veces como nueva. Esto lo lista.

    .venv/bin/python scripts/revisar_lexico.py              # informe completo
    .venv/bin/python scripts/revisar_lexico.py --repetidas  # solo las repetidas

No falla ni corrige nada: decide el profesor. Una repetición puede ser
legítima (la palabra vuelve con otro significado o en otra construcción), y
por eso esto es un informe y no una regla del validador.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import exportar_anki  # noqa: E402
import plan  # noqa: E402
import validar  # noqa: E402

# Artículos y marcas que no forman parte de la palabra a efectos de comparar.
DELANTE = re.compile(r"^(el|la|los|las|un|una|unos|unas)\s+", re.I)


def normalizar(entrada: str) -> str:
    """«el **li**bro» y «los libros» no son la misma entrada, pero «El libro»
    y «el  libro » sí. Quita negritas, artículo, acentos y mayúsculas."""
    texto = entrada.replace("**", "").replace("<u>", "").replace("</u>", "")
    texto = re.sub(r"\s+", " ", texto).strip().lower()
    texto = DELANTE.sub("", texto)
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return texto.strip(" .,;:!¡?¿")


def lexico() -> dict[str, list[tuple[plan.Dia, str]]]:
    """{palabra normalizada: [(día, entrada tal cual), …]} en orden de curso."""
    cal = plan.cargar()
    indice: dict[str, list[tuple[plan.Dia, str]]] = {}
    for d in plan.dias(cal):
        if not d.ruta.exists():
            continue
        # Las DOS tablas, y quién decide cuál vive en exportar_anki: los
        # domingos de cultura usan «3. Слова» y no «Словарь дня», así que
        # mirando solo la segunda este informe no veía unas mil entradas.
        datos, filas = exportar_anki.filas_de(d.ruta)
        if not datos:
            continue
        for fila in filas:
            if not fila or not fila[0].strip():
                continue
            clave = normalizar(fila[0])
            if clave:
                indice.setdefault(clave, []).append((d, fila[0].strip()))
    return indice


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repetidas", action="store_true")
    a = p.parse_args(argv)

    indice = lexico()
    repetidas = {k: v for k, v in indice.items() if len(v) > 1}

    if repetidas:
        print(f"Entradas que se enseñan como nuevas más de una vez: {len(repetidas)}\n")
        for clave, apariciones in sorted(repetidas.items(), key=lambda kv: -len(kv[1])):
            sitios = ", ".join(f"S{d.semana:02d}D{d.dia}" for d, _ in apariciones)
            print(f"  {apariciones[0][1]:<34} {len(apariciones)}×  {sitios}")
    else:
        print("Ninguna entrada se repite.")

    if a.repetidas:
        return 0

    cal = plan.cargar()
    escritas = [d for d in plan.dias(cal) if d.ruta.exists()]
    print(f"\nLecciones escritas: {len(escritas)} de {len(plan.dias(cal))}")
    print(f"Entradas de vocabulario: {sum(len(v) for v in indice.values())} ({len(indice)} distintas)")
    objetivo = cal["meta"]["vocabulario_objetivo"]
    ultima = escritas[-1] if escritas else None
    if ultima:
        print(f"Última escrita: {ultima.etiqueta} — {ultima.tema_es}")
    print(f"Objetivo del curso: {objetivo['A1']} palabras en A1, {objetivo['A2']} acumuladas en A2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
