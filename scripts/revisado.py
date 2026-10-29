#!/usr/bin/env python3
"""Qué lecciones ha vuelto a leer el profesor, y marcar las que sí.

    .venv/bin/python scripts/revisado.py                 # por dónde va
    .venv/bin/python scripts/revisado.py 101 102 103     # marca esas tres
    .venv/bin/python scripts/revisado.py 15-3            # semana 15, día 3
    .venv/bin/python scripts/revisado.py 101-120         # un tramo
    .venv/bin/python scripts/revisado.py --semana 15
    .venv/bin/python scripts/revisado.py --unidad 8
    .venv/bin/python scripts/revisado.py --quitar 101    # deshacer

**Nada de esto mide que alguien haya leído nada, y no puede.** La regla 6 dice
que el generador escribe con `revisado: false` y que lo pone en `true` el
profesor: esa bandera es una FIRMA, no una medición. Lo que este guion hace es
que firmar sea barato —hasta hoy eran 344 archivos y una línea en cada uno, a
mano— y que se vea por dónde va, que es la otra mitad del problema: leyendo de
a poco, lo que se pierde no es la voluntad sino el sitio donde uno se quedó.

Por eso el informe dice **cuál es la siguiente sin revisar** y su dirección en
el sitio: es la única pregunta que hay que contestar para seguir.

Toca UNA línea del frontmatter y nada más. No usa `yaml.dump`, que reordenaría
las claves y se llevaría por delante las comillas de `tema_es`; es la misma
razón por la que `poner_dominio.py` edita `sitio.yaml` con una expresión
regular y no con un volcado.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402

BANDERA = re.compile(r"^revisado:\s*(true|false)\s*$", re.M)
DOMINIO = "https://espanoldesderuso.com"


def _leer(ruta: pathlib.Path) -> bool | None:
    """True / False, o None si la lección no está escrita o no declara nada."""
    if not ruta.exists():
        return None
    m = BANDERA.search(ruta.read_text(encoding="utf-8"))
    return None if not m else m.group(1) == "true"


def marcar(ruta: pathlib.Path, valor: bool) -> bool:
    """Deja la bandera en `valor`. Devuelve si cambió algo."""
    texto = ruta.read_text(encoding="utf-8")
    nuevo = BANDERA.sub(f"revisado: {'true' if valor else 'false'}", texto, count=1)
    if nuevo == texto:
        return False
    ruta.write_text(nuevo, encoding="utf-8")
    return True


def _numeros(objetivos: list[str], cal: dict) -> list[int]:
    """Entiende `105`, `15-3` y `101-120`.

    `15-3` y `101-120` se escriben igual y significan cosas distintas, así que
    hay que decidir: un guion es un TRAMO cuando las dos partes son números de
    día válidos y van en orden; si no, es semana-día. En la práctica no hay
    ambigüedad —`15-3` iría al revés— y el caso dudoso se resuelve mirando que
    `1-7` es la semana 1 día 7 y no el tramo del día 1 al 7, que es lo mismo."""
    salida: list[int] = []
    for bruto in objetivos:
        t = bruto.strip()
        if "-" in t:
            a, b = t.split("-", 1)
            if a.isdigit() and b.isdigit():
                a, b = int(a), int(b)
                if a < b and b <= 365 and (a, b) != (1, 7):
                    salida.extend(range(a, b + 1))
                    continue
                try:
                    salida.append(plan.dia(cal, a, b).numero)
                    continue
                except KeyError:
                    pass
            raise SystemExit(f"no entiendo «{bruto}»")
        if not t.isdigit() or not 1 <= int(t) <= 365:
            raise SystemExit(f"no entiendo «{bruto}»: los días van del 1 al 365")
        salida.append(int(t))
    return sorted(set(salida))


def informe(cal: dict) -> None:
    todos = plan.dias(cal)
    estado = {d.numero: _leer(d.ruta) for d in todos}
    escritas = [d for d in todos if estado[d.numero] is not None]
    hechas = [d for d in escritas if estado[d.numero]]
    print(f"Revisadas {len(hechas)} de {len(escritas)} lecciones escritas "
          f"({len(hechas) * 100 // max(1, len(escritas))} %)\n")

    por_unidad: dict[object, list] = {}
    for d in escritas:
        por_unidad.setdefault(d.unidad, []).append(d)
    for unidad, grupo in por_unidad.items():
        si = sum(1 for d in grupo if estado[d.numero])
        barra = "█" * round(si / len(grupo) * 12) + "·" * (12 - round(si / len(grupo) * 12))
        nombre = f"unidad {unidad:>2}" if unidad else "fase final"
        print(f"  {nombre}  {barra}  {si:>2}/{len(grupo)}")

    pendientes = [d for d in escritas if not estado[d.numero]]
    if not pendientes:
        print("\nNo queda ninguna por revisar.")
        return
    s = pendientes[0]
    print(f"\nLa siguiente sin revisar es la {s.numero}: semana {s.semana}, día {s.dia}"
          f" — {s.tema_es}")
    print(f"  {DOMINIO}/semana-{s.semana:02d}/dia-{s.dia}.html")
    print(f"  {s.ruta.relative_to(RAIZ)}")
    print(f"\nCuando la des por buena:  scripts/revisado.py {s.numero}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dias", nargs="*", help="105, 15-3 o 101-120")
    ap.add_argument("--semana", type=int, help="la semana entera")
    ap.add_argument("--unidad", type=int, help="la unidad entera")
    ap.add_argument("--quitar", action="store_true", help="devolverlas a borrador")
    args = ap.parse_args()

    cal = plan.cargar()
    todos = {d.numero: d for d in plan.dias(cal)}

    objetivo = set(_numeros(args.dias, cal))
    if args.semana:
        objetivo |= {d.numero for d in todos.values() if d.semana == args.semana}
    if args.unidad:
        objetivo |= {d.numero for d in todos.values() if d.unidad == args.unidad}

    if not objetivo:
        informe(cal)
        return 0

    valor = not args.quitar
    cambiadas = 0
    for n in sorted(objetivo):
        d = todos[n]
        if not d.ruta.exists():
            print(f"  {n:>3}  (sin escribir, me la salto)")
            continue
        if marcar(d.ruta, valor):
            cambiadas += 1
            print(f"  {n:>3}  semana {d.semana}, día {d.dia} — {d.tema_es}")
    verbo = "a borrador" if args.quitar else "revisadas"
    print(f"\n{cambiadas} {verbo}; {len(objetivo) - cambiadas} ya lo estaban o no existen.")
    if cambiadas:
        print("Ahora: .venv/bin/python scripts/construir_sitio.py "
              "(el aviso de «Черновик» sale del frontmatter)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # `revisado.py | head` cierra la tubería a mitad del informe. Sin
        # esto el guion muere con un traceback que parece un fallo suyo.
        sys.stdout = None
        raise SystemExit(0)
