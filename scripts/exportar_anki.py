#!/usr/bin/env python3
"""Saca el vocabulario de las lecciones a TSV para Anki (u otra app de tarjetas).

El vocabulario vive en cada lección, en la tabla de «Словарь дня» (y en la de
«Слова» de los domingos de cultura). Este script no inventa nada: lo lee de ahí
y lo escribe en `vocabulario/semana-XX.tsv` y `vocabulario/todo.tsv`, con cuatro
columnas: español, ruso, ejemplo, etiquetas.

    .venv/bin/python scripts/exportar_anki.py          # escribe los TSV
    .venv/bin/python scripts/exportar_anki.py --ver    # solo cuenta

En Anki: Importar → separador tabulador → campos 1-3 → la 4.ª columna como
etiquetas. Las negritas del Markdown (la sílaba tónica) se quitan.
"""
from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import revisar_lexico  # noqa: E402
import validar  # noqa: E402

CARPETA = RAIZ / "vocabulario"
CABECERA = "espanol\truso\tejemplo\tetiquetas\n"


def limpiar(celda: str) -> str:
    celda = celda.replace("**", "").replace("<u>", "").replace("</u>", "")
    return re.sub(r"\s+", " ", celda).strip()


def tarjetas_de(ruta: pathlib.Path) -> list[tuple[str, str, str, str]]:
    datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
    if not datos:
        return []
    filas = validar.filas_de_vocabulario(cuerpo)
    if not filas and datos.get("tipo") == "cultura":
        filas = _filas_de_cultura(cuerpo)
    etiquetas = f"S{int(datos['semana']):02d} U{datos.get('unidad') or 0} {datos['nivel']} {datos['tipo']}"
    tarjetas = []
    for fila in filas:
        if len(fila) < 2:
            continue
        es, ru = limpiar(fila[0]), limpiar(fila[1])
        ej = limpiar(fila[2]) if len(fila) > 2 else ""
        if es and ru:
            tarjetas.append((es, ru, ej, etiquetas))
    return tarjetas


def _filas_de_cultura(cuerpo: str) -> list[list[str]]:
    """La tabla de «Слова» de un domingo tiene dos pares de columnas por fila."""
    inicio = cuerpo.find("## 3. Слова")
    if inicio < 0:
        return []
    seccion = cuerpo[inicio:]
    siguiente = re.search(r"^## 4\.", seccion, re.M)
    if siguiente:
        seccion = seccion[: siguiente.start()]
    filas = []
    for linea in seccion.splitlines():
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in celdas) or celdas[0] == "Español":
            continue
        for i in range(0, len(celdas) - 1, 2):
            if celdas[i] and celdas[i + 1]:
                filas.append([celdas[i], celdas[i + 1], ""])
    return filas


def exportar(destino: pathlib.Path = CARPETA, escribir: bool = True) -> dict[str, int]:
    """Una palabra, una tarjeta.

    Si dos lecciones enseñan la misma entrada como nueva, el mazo se queda con
    la PRIMERA: la repetición es una decisión pedagógica que revisa el profesor
    (`scripts/revisar_lexico.py` las lista), pero mandar dos tarjetas idénticas
    a Anki no es una decisión, es un defecto. La palabra sigue en las dos
    lecciones; lo que no se duplica es la tarjeta."""
    vistas: set[str] = set()
    por_semana: dict[str, list[tuple[str, str, str, str]]] = {}
    for ruta in validar.lecciones():
        semana = ruta.parent.name  # semana-01
        nuevas = []
        for tarjeta in tarjetas_de(ruta):
            clave = revisar_lexico.normalizar(tarjeta[0])
            if clave in vistas:
                continue
            vistas.add(clave)
            nuevas.append(tarjeta)
        por_semana.setdefault(semana, []).extend(nuevas)
    cuentas = {}
    todas: list[tuple[str, str, str, str]] = []
    if escribir:
        destino.mkdir(exist_ok=True)
    for semana, tarjetas in sorted(por_semana.items()):
        cuentas[semana] = len(tarjetas)
        todas.extend(tarjetas)
        if escribir:
            (destino / f"{semana}.tsv").write_text(CABECERA + "".join("\t".join(t) + "\n" for t in tarjetas), encoding="utf-8")
    if escribir:
        (destino / "todo.tsv").write_text(CABECERA + "".join("\t".join(t) + "\n" for t in todas), encoding="utf-8")
    cuentas["total"] = len(todas)
    return cuentas


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cuentas = exportar(escribir="--ver" not in argv)
    for k, v in cuentas.items():
        print(f"{k:12} {v:4} tarjetas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
