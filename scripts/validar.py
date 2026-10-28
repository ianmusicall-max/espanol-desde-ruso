#!/usr/bin/env python3
"""Valida la forma de las lecciones de curso/.

Comprueba lo que una lección NO puede dejar de tener y que el calendario
(`programa/calendario.yaml`) y la lección cuenten lo mismo:

- frontmatter completo (semana, dia, tipo, unidad, nivel, tema_es, tema_ru,
  minutos, revisado) y coincidente con el día del calendario;
- apartados numerados con su franja de minutos, contiguos de 0 a 30;
- los apartados que pide cada tipo de día (lección, repaso, prueba, cultura);
- el contraste con el ruso en toda lección de tipo `leccion`;
- el vocabulario del día (6-10 palabras en una lección);
- las claves (Ответы) si hay ejercicios.

    .venv/bin/python scripts/validar.py                 # todas las lecciones
    .venv/bin/python scripts/validar.py curso/semana-01/dia-1.md
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402

CAMPOS = ("semana", "dia", "tipo", "unidad", "nivel", "tema_es", "tema_ru", "minutos", "revisado")
FRANJA = re.compile(r"^## (\d+)\. (.+?) \((\d+)[–-](\d+) мин\)\s*$", re.M)
CONTRASTE = "### ⚠️ Контраст с русским"
VOCABULARIO = "## Словарь дня"
RESPUESTAS = "## Ответы"

# Qué apartados pide cada tipo de día. Se compara por "contiene", en orden.
APARTADOS = {
    "leccion": ["Разминка", ("Фонетика", "Аудирование"), "Новое", "Практика", "Выход", "Итог"],
    "repaso": ["Разминка", "Повторение", "Мини-тест", "Разбор ошибок", "Итог"],
    "prueba": ["Инструкция", "Тест", "Ключи и подсчёт", "Разбор ошибок"],
    "cultura": ["Разминка", "Материал", "Слова", "Задание", "Итог"],
    # Los tres tipos de la unidad 11, que es la primera que los usa. Hasta
    # aquí no estaban definidos, así que un día de examen pasaba la validación
    # con cualquier forma: es el agujero de siempre —lo escrito y lo que corre
    # dejando de coincidir— y el momento de cerrarlo es el primer uso.
    #
    # Un simulacro es una prueba del DELE partida en sesiones de 30 minutos:
    # instrucciones, las tareas, la corrección y el análisis. Un examen es lo
    # mismo pero decide si se pasa de nivel, así que su último apartado no es
    # «разбор», sino la decisión. Un proyecto no se corrige: se prepara y se
    # entrega.
    "simulacro": ["Инструкция", "Задания", "Ключи и подсчёт", "Разбор ошибок"],
    "examen": ["Инструкция", "Экзамен", "Ключи и подсчёт", "Решение"],
    "proyecto": ["Разминка", "Подготовка", "Работа", "Итог"],
    # El día 365, que es el único de su tipo y el último del curso. Mismo
    # criterio que los tres de arriba: los apartados se definen el día que se
    # usan por primera vez, porque mientras `APARTADOS` no conoce un tipo su
    # validación no comprueba NADA y la lección pasa con cualquier forma.
    #
    # Un día de reserva no prepara ni corrige: mira qué quedó pendiente y lo
    # hace. Por eso su segundo apartado no es «Подготовка» sino la lista de lo
    # que falta, que es lo único que ese día tiene que decidir.
    "reserva": ["Разминка", "Что осталось", "Работа", "Итог"],
}


def frontmatter(texto: str) -> tuple[dict, str]:
    """Separa el frontmatter YAML del cuerpo. Devuelve ({}, texto) si no hay."""
    if not texto.startswith("---\n"):
        return {}, texto
    fin = texto.find("\n---\n", 4)
    if fin < 0:
        return {}, texto
    datos = yaml.safe_load(texto[4:fin]) or {}
    return datos, texto[fin + 5:]


def franjas(cuerpo: str) -> list[tuple[int, str, int, int]]:
    return [(int(n), nombre.strip(), int(a), int(b)) for n, nombre, a, b in FRANJA.findall(cuerpo)]


def problemas_de_franjas(tramos: list[tuple[int, str, int, int]], minutos: int) -> list[str]:
    errores = []
    if not tramos:
        return ["no hay apartados con franja de minutos («## 1. Nombre (0–3 мин)»)"]
    for i, (n, nombre, a, b) in enumerate(tramos, start=1):
        if n != i:
            errores.append(f"apartado «{nombre}» numerado {n}, se esperaba {i}")
        if b <= a:
            errores.append(f"apartado «{nombre}»: franja {a}–{b} vacía o invertida")
    if tramos[0][2] != 0:
        errores.append(f"el primer apartado empieza en {tramos[0][2]}, no en 0")
    for (_, nombre_a, _, fin_a), (_, nombre_b, inicio_b, _) in zip(tramos, tramos[1:]):
        if fin_a != inicio_b:
            errores.append(f"hueco o solape entre «{nombre_a}» (termina {fin_a}) y «{nombre_b}» (empieza {inicio_b})")
    if tramos[-1][3] != minutos:
        errores.append(f"el último apartado termina en {tramos[-1][3]}, no en {minutos}")
    return errores


def problemas_de_apartados(tipo: str, tramos: list[tuple[int, str, int, int]]) -> list[str]:
    pedidos = APARTADOS.get(tipo)
    if not pedidos:
        return []
    nombres = [nombre for _, nombre, _, _ in tramos]
    errores = []
    if len(nombres) != len(pedidos):
        errores.append(f"un día de tipo {tipo} tiene {len(pedidos)} apartados, aquí hay {len(nombres)}")
    for esperado, real in zip(pedidos, nombres):
        opciones = esperado if isinstance(esperado, tuple) else (esperado,)
        if not any(o in real for o in opciones):
            errores.append(f"apartado «{real}»: se esperaba «{' / '.join(opciones)}»")
    return errores


def filas_de_vocabulario(cuerpo: str) -> list[list[str]]:
    """Las filas de la tabla de «Словарь дня» (sin cabecera ni separador)."""
    inicio = cuerpo.find(VOCABULARIO)
    if inicio < 0:
        return []
    seccion = cuerpo[inicio + len(VOCABULARIO):]
    siguiente = re.search(r"^## ", seccion, re.M)
    if siguiente:
        seccion = seccion[: siguiente.start()]
    filas = []
    for linea in seccion.splitlines():
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in celdas):
            continue  # separador
        if celdas and celdas[0] in ("Español", "Español / Русский"):
            continue  # cabecera
        filas.append(celdas)
    return filas


def problemas(ruta: pathlib.Path, cal: dict | None = None) -> list[str]:
    cal = cal or plan.cargar()
    texto = ruta.read_text(encoding="utf-8")
    datos, cuerpo = frontmatter(texto)
    errores: list[str] = []
    if not datos:
        return ["sin frontmatter"]
    for campo in CAMPOS:
        if campo not in datos:
            errores.append(f"falta «{campo}» en el frontmatter")
    if errores:
        return errores
    if datos["minutos"] != cal["meta"]["minutos_por_dia"]:
        errores.append(f"minutos: {datos['minutos']} (el curso es de {cal['meta']['minutos_por_dia']})")
    if not isinstance(datos["revisado"], bool):
        errores.append("«revisado» tiene que ser true o false")

    # El archivo tiene que estar donde su frontmatter dice.
    esperado = plan.CURSO / f"semana-{int(datos['semana']):02d}" / f"dia-{int(datos['dia'])}.md"
    if ruta.resolve() != esperado.resolve():
        errores.append(f"el archivo está en {ruta} pero su frontmatter dice {esperado.relative_to(RAIZ)}")

    try:
        dia = plan.dia(cal, int(datos["semana"]), int(datos["dia"]))
    except KeyError as e:
        return errores + [str(e)]
    if datos["tipo"] != dia.tipo:
        errores.append(f"tipo «{datos['tipo']}», pero el calendario dice «{dia.tipo}»")
    if datos["tema_es"] != dia.tema_es:
        errores.append(f"tema_es «{datos['tema_es']}» no coincide con el calendario: «{dia.tema_es}»")
    if datos["tema_ru"] != dia.tema_ru:
        errores.append(f"tema_ru «{datos['tema_ru']}» no coincide con el calendario: «{dia.tema_ru}»")
    if datos["unidad"] != dia.unidad:
        errores.append(f"unidad {datos['unidad']}, pero el calendario dice {dia.unidad}")
    if datos["nivel"] != dia.nivel:
        errores.append(f"nivel {datos['nivel']}, pero el calendario dice {dia.nivel}")

    tramos = franjas(cuerpo)
    errores += problemas_de_franjas(tramos, int(datos["minutos"]))
    errores += problemas_de_apartados(datos["tipo"], tramos)

    if datos["tipo"] == "leccion":
        if CONTRASTE not in cuerpo:
            errores.append(f"falta el apartado «{CONTRASTE}»")
        if "Вы захотите" not in cuerpo:
            errores.append("el contraste con el ruso no da el error predecible («Вы захотите сказать…»)")
        minimo, maximo = cal["meta"]["palabras_nuevas_por_leccion"]
        filas = filas_de_vocabulario(cuerpo)
        if not filas:
            errores.append(f"falta «{VOCABULARIO}» con su tabla")
        elif not minimo <= len(filas) <= maximo:
            errores.append(f"el vocabulario tiene {len(filas)} filas; una lección lleva de {minimo} a {maximo}")
        for fila in filas:
            if len(fila) != 3 or not all(fila):
                errores.append(f"fila de vocabulario incompleta: {' | '.join(fila)}")
                break
    if datos["tipo"] == "cultura" and VOCABULARIO not in cuerpo and "## 3. Слова" not in cuerpo:
        errores.append("un día de cultura lleva su tabla de palabras")

    hay_ejercicios = any(marca in cuerpo for marca in ("Упражнение", "Мини-тест", "### 1. Лексика", "Правда или неправда"))
    if hay_ejercicios and RESPUESTAS not in cuerpo:
        errores.append(f"hay ejercicios pero falta «{RESPUESTAS}»")
    if "[VERIFICAR]" in cuerpo and datos["revisado"]:
        errores.append("marcada como revisada pero tiene un [VERIFICAR] pendiente")
    return errores


def lecciones() -> list[pathlib.Path]:
    return sorted(plan.CURSO.glob("semana-*/dia-*.md"), key=lambda p: (p.parent.name, int(p.stem.split("-")[1])))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    rutas = [pathlib.Path(a) for a in argv] or lecciones()
    cal = plan.cargar()
    total = 0
    for ruta in rutas:
        errs = problemas(ruta, cal)
        rel = ruta.resolve().relative_to(RAIZ) if ruta.resolve().is_relative_to(RAIZ) else ruta
        if errs:
            total += len(errs)
            print(f"✗ {rel}")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"✓ {rel}")
    print(f"{len(rutas)} lecciones, {total} problemas")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
