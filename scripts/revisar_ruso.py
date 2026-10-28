#!/usr/bin/env python3
"""Cuanto ruso y cuanto espanol hay en cada unidad, y SOLO LEE.

`metodologia.md` §6 promete una retirada progresiva del ruso en cuatro bandas
(unidades 1-6, 7-11, 12-18, 19-24) y en tres columnas: las instrucciones, la
explicacion gramatical y los titulos de ejercicio. Medido el 2026-10-28, **esa
retirada no ocurre**: la proporcion es plana de la unidad 1 a la 23, y el
rotulo del ejercicio es «Упражнение А» en las 220 lecciones.

El curso tomo otra decision, coherente y distinta: el andamio en ruso de
principio a fin, y el espanol en todo lo que el alumno lee y produce. Este
guion existe para que la decision se pueda cambiar con numeros delante, no de
memoria: si el profesor decide implementar §6, aqui se ve por donde va.

Se cuenta por RENGLONES de los apartados 4 (Практика) y 5 (Выход), que es
donde vive la instruccion. Las tablas, las citas y los titulos quedan fuera: la
tabla de vocabulario es espanol por definicion y contarla subiria el porcentaje
sin que nadie hubiera retirado nada.

    .venv/bin/python scripts/revisar_ruso.py
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan
import validar

# Lo que §6 promete para cada banda de unidades, en la columna «Instrucciones».
PROMETIDO = {
    (1, 6): "ruso",
    (7, 11): "ruso",
    (12, 18): "español + glosa en ruso",
    (19, 24): "español",
}
# Un renglon con menos letras que esto no dice nada de en que idioma esta.
MINIMO = 20


def banda(unidad: int) -> str:
    for (a, b), que in PROMETIDO.items():
        if a <= unidad <= b:
            return que
    return "?"


def reparto(cal=None) -> dict[int, tuple[int, int]]:
    """{unidad: (renglones en ruso, renglones en espanol)}."""
    cal = cal or plan.cargar()
    fuera: dict[int, list[int]] = collections.defaultdict(lambda: [0, 0])
    for d in plan.dias(cal):
        if not d.ruta.exists() or d.unidad is None or d.tipo != "leccion":
            continue
        cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))[1]
        m = re.search(r"^## 4\..*?(?=^## 6\.)", cuerpo, re.S | re.M)
        if not m:
            continue
        for linea in m.group(0).split("\n"):
            linea = linea.strip()
            if not linea or linea.startswith(("|", ">", "#")):
                continue
            cirilico = len(re.findall(r"[Ѐ-ӿ]", linea))
            latino = len(re.findall(r"[A-Za-záéíóúüñÁÉÍÓÚÑ]", linea))
            if cirilico + latino < MINIMO:
                continue
            fuera[d.unidad][0 if cirilico > latino else 1] += 1
    return {u: tuple(v) for u, v in sorted(fuera.items())}


def rotulos(cal=None) -> collections.Counter:
    """Como empieza el titulo de los ejercicios, contado."""
    cal = cal or plan.cargar()
    cuenta: collections.Counter = collections.Counter()
    for d in plan.dias(cal):
        if not d.ruta.exists():
            continue
        cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))[1]
        for m in re.finditer(r"^### +(\S+)", cuerpo, re.M):
            palabra = m.group(1).rstrip(".:")
            if palabra in ("Упражнение", "Ejercicio", "Задание", "Tarea"):
                cuenta[palabra] += 1
    return cuenta


def main() -> int:
    cal = plan.cargar()
    print("Instrucciones de los apartados 4 y 5, por unidad\n")
    print("  u   ruso  español   %es   §6 promete")
    for unidad, (ru, es) in reparto(cal).items():
        pct = 100 * es // max(1, ru + es)
        print(f"  {unidad:2}  {ru:5}  {es:7}  {pct:4}   {banda(unidad)}")

    print("\nRótulo de los ejercicios en las 365 lecciones:")
    for palabra, n in rotulos(cal).most_common():
        print(f"  {n:4}  {palabra}")
    print(
        "\n§6 pide «español + ruso» desde la unidad 7 y «español» desde la 12.\n"
        "Lo que hay es Упражнение en casi todas: la columna de los títulos no se\n"
        "implementó nunca. Cambiarla toca 660 encabezados y sus claves, porque la\n"
        "clave llama al ejercicio por su letra (А, Б, В)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
