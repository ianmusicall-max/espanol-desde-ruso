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

    # Las dos tablas no son lo mismo, y meterlas en un número solo convierte
    # un informe en un reproche: `Словарь дня` ENSEÑA diez palabras nuevas y el
    # `3. Слова` de los domingos GLOSA las que usa su texto, nuevas o no. Una
    # palabra glosada el domingo y enseñada el lunes no es un defecto: es
    # exposición previa. Por eso el informe las separa, y lo único que de
    # verdad hay que mirar son las de la tercera lista.
    grupos = {"entre domingos": {}, "domingo y semana": {}, "dos veces como nueva": {}}
    for clave, apariciones in repetidas.items():
        tipos = [d.tipo for d, _ in apariciones]
        if all(x == "cultura" for x in tipos):
            grupos["entre domingos"][clave] = apariciones
        elif any(x == "cultura" for x in tipos):
            grupos["domingo y semana"][clave] = apariciones
        else:
            grupos["dos veces como nueva"][clave] = apariciones

    if repetidas:
        print(f"Entradas que aparecen en más de una tabla: {len(repetidas)}")
        print(f"  {len(grupos['entre domingos']):3} entre dos domingos "
              "— su tabla glosa el texto del día, así que repetir es normal")
        print(f"  {len(grupos['domingo y semana']):3} en un domingo y en una lección de semana "
              "— exposición previa o nueva glosa")
        print(f"  {len(grupos['dos veces como nueva']):3} DOS VECES en «Словарь дня» "
              "— esto es lo que hay que mirar\n")
        for nombre, grupo in grupos.items():
            if not grupo:
                continue
            print(f"== {nombre} ({len(grupo)})")
            for clave, apariciones in sorted(grupo.items(), key=lambda kv: -len(kv[1])):
                sitios = ", ".join(f"S{d.semana:02d}D{d.dia}" for d, _ in apariciones)
                print(f"  {apariciones[0][1]:<34} {len(apariciones)}×  {sitios}")
            print()
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
