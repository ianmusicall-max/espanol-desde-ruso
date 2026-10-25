#!/usr/bin/env python3
"""Modelo del calendario anual.

Carga ``programa/calendario.yaml`` -la unica fuente de verdad del programa- y
lo expone como objetos para los demas scripts (validar, construir el sitio,
escribir lecciones). Tambien imprime el plan en Markdown:

    .venv/bin/python scripts/plan.py                 # tabla de las 24 unidades
    .venv/bin/python scripts/plan.py --semana 3      # los 7 dias de la semana 3
    .venv/bin/python scripts/plan.py --dia 120       # un dia por su numero (1-365)
    .venv/bin/python scripts/plan.py --actualizar    # reescribe la tabla de programa/plan-anual.md
"""
from __future__ import annotations

import argparse
import pathlib
import re
from dataclasses import dataclass

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CALENDARIO = RAIZ / "programa" / "calendario.yaml"
PLAN_ANUAL = RAIZ / "programa" / "plan-anual.md"
CURSO = RAIZ / "curso"

TIPOS = ("leccion", "repaso", "cultura", "prueba", "simulacro", "proyecto", "examen", "reserva")
TIPO_RU = {
    "leccion": "урок", "repaso": "повторение", "cultura": "культура", "prueba": "тест",
    "simulacro": "пробный экзамен", "proyecto": "проект", "examen": "экзамен", "reserva": "резерв",
}
DIAS_RU = {1: "понедельник", 2: "вторник", 3: "среда", 4: "четверг", 5: "пятница", 6: "суббота", 7: "воскресенье"}
MARCA_INICIO = "<!-- tabla generada: no editar a mano, correr scripts/plan.py --actualizar -->"
MARCA_FIN = "<!-- fin de la tabla generada -->"


@dataclass(frozen=True)
class Dia:
    semana: int
    dia: int
    tipo: str
    tema_es: str
    tema_ru: str
    foco: str
    salida: str
    unidad: int | None
    nivel: str

    @property
    def numero(self) -> int:
        """Numero del dia dentro del año (1-365)."""
        return (self.semana - 1) * 7 + self.dia

    @property
    def carpeta(self) -> pathlib.Path:
        return CURSO / f"semana-{self.semana:02d}"

    @property
    def ruta(self) -> pathlib.Path:
        return self.carpeta / f"dia-{self.dia}.md"

    @property
    def etiqueta(self) -> str:
        return f"Semana {self.semana} · Día {self.dia}"


def cargar(ruta: pathlib.Path = CALENDARIO) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _dia(fila: list, unidad: int | None, nivel: str) -> Dia:
    if len(fila) != 7:
        raise ValueError(f"fila de dia con {len(fila)} campos (se esperan 7): {fila!r}")
    semana, dia, tipo, tema_es, tema_ru, foco, salida = fila
    return Dia(int(semana), int(dia), str(tipo), str(tema_es), str(tema_ru), str(foco), str(salida), unidad, nivel)


def dias(cal: dict) -> list[Dia]:
    """Los 365 dias en orden."""
    todos: list[Dia] = []
    for u in cal["unidades"]:
        for fila in u["dias"]:
            todos.append(_dia(fila, u["numero"], u["nivel"]))
    for fila in cal["fase_final"]["dias"]:
        todos.append(_dia(fila, None, "A2"))
    for fila in cal["dia_365"]:
        todos.append(_dia(fila, None, "A2"))
    todos.sort(key=lambda d: d.numero)
    return todos


def dia(cal: dict, semana: int, numero_dia: int) -> Dia:
    for d in dias(cal):
        if d.semana == semana and d.dia == numero_dia:
            return d
    raise KeyError(f"no hay dia {numero_dia} en la semana {semana}")


def por_numero(cal: dict, n: int) -> Dia:
    for d in dias(cal):
        if d.numero == n:
            return d
    raise KeyError(f"no hay dia numero {n}")


def unidad_de(cal: dict, semana: int) -> dict | None:
    for u in cal["unidades"]:
        a, b = u["semanas"]
        if a <= semana <= b:
            return u
    return None


def fase_de(cal: dict, semana: int) -> str:
    for f in cal["meta"]["fases"]:
        a, b = f["semanas"]
        if a <= semana <= b:
            return f["nombre"]
    if semana == 53:
        return "Final"
    raise KeyError(f"la semana {semana} no esta en ninguna fase")


def tabla_unidades(cal: dict) -> str:
    """Tabla Markdown de las 24 unidades mas la fase final."""
    filas = ["| Unidad | Semanas | Nivel | Título | Gramática central |", "|---|---|---|---|---|"]
    for u in cal["unidades"]:
        a, b = u["semanas"]
        gram = "; ".join(u["gramatica"][:3])
        filas.append(f"| {u['numero']} | {a}-{b} | {u['nivel']} | {u['titulo_es']} · {u['titulo_ru']} | {gram} |")
    ff = cal["fase_final"]
    a, b = ff["semanas"]
    filas.append(f"| — | {a}-{b} | A2 | {ff['titulo_es']} · {ff['titulo_ru']} | simulacros DELE A2, proyecto, examen final |")
    return "\n".join(filas)


def tabla_semana(cal: dict, semana: int) -> str:
    filas = [f"| Día | Tipo | Tema | Foco | Salida |", "|---|---|---|---|---|"]
    for d in dias(cal):
        if d.semana == semana:
            filas.append(f"| {d.dia} ({DIAS_RU[d.dia]}) | {d.tipo} | {d.tema_es} · {d.tema_ru} | {d.foco} | {d.salida} |")
    return "\n".join(filas)


def actualizar_plan_anual(cal: dict, ruta: pathlib.Path = PLAN_ANUAL) -> bool:
    """Reescribe la tabla entre las marcas de plan-anual.md. Devuelve True si cambio."""
    texto = ruta.read_text(encoding="utf-8")
    patron = re.compile(re.escape(MARCA_INICIO) + r".*?" + re.escape(MARCA_FIN), re.S)
    nuevo = f"{MARCA_INICIO}\n{tabla_unidades(cal)}\n{MARCA_FIN}"
    if not patron.search(texto):
        raise ValueError(f"{ruta} no tiene las marcas de la tabla generada")
    reemplazado = patron.sub(lambda _: nuevo, texto)
    if reemplazado != texto:
        ruta.write_text(reemplazado, encoding="utf-8")
        return True
    return False


def plan_anual_al_dia(cal: dict, ruta: pathlib.Path = PLAN_ANUAL) -> bool:
    texto = ruta.read_text(encoding="utf-8")
    return f"{MARCA_INICIO}\n{tabla_unidades(cal)}\n{MARCA_FIN}" in texto


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--semana", type=int)
    p.add_argument("--dia", type=int, help="numero del dia en el año (1-365)")
    p.add_argument("--actualizar", action="store_true", help="reescribe la tabla de programa/plan-anual.md")
    a = p.parse_args(argv)
    cal = cargar()
    if a.actualizar:
        print("plan-anual.md actualizado" if actualizar_plan_anual(cal) else "plan-anual.md ya estaba al dia")
        return 0
    if a.semana:
        print(tabla_semana(cal, a.semana))
        return 0
    if a.dia:
        d = por_numero(cal, a.dia)
        u = unidad_de(cal, d.semana)
        print(f"{d.etiqueta} (día {d.numero}, {fase_de(cal, d.semana)}, {TIPO_RU[d.tipo]})")
        print(f"  {d.tema_es} · {d.tema_ru}")
        print(f"  foco:   {d.foco}")
        print(f"  salida: {d.salida}")
        if u:
            print(f"  unidad {u['numero']}: {u['titulo_es']}")
        return 0
    print(tabla_unidades(cal))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
