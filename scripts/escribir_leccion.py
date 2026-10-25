#!/usr/bin/env python3
"""Escribe con Claude el BORRADOR de una lección que todavía no existe.

Toma del calendario qué toca ese día, le da al modelo la metodología, la
plantilla, el análisis contrastivo y las lecciones ya escritas de la misma
unidad (para que los personajes, el léxico y el tono sigan), y guarda el
resultado en `curso/semana-XX/dia-N.md` con `revisado: false`. Después lo pasa
por el validador y, si algo no cuadra, le pide una corrección (una sola vez).

    .venv/bin/python scripts/escribir_leccion.py --semana 3 --dia 1
    .venv/bin/python scripts/escribir_leccion.py --semana 3 --dia 1 --ver      # muestra el prompt, no llama
    .venv/bin/python scripts/escribir_leccion.py --semana 3 --todos             # los 7 días de la semana
    .venv/bin/python scripts/escribir_leccion.py --semana 3 --dia 1 --forzar    # reescribe aunque exista

Necesita ANTHROPIC_API_KEY (en el entorno o en un .env en la raíz). Nada de lo
que escribe se publica sin que el profesor lo lea y ponga `revisado: true`.

El prompt está partido en tres bloques para la caché de la API: el estable
(metodología, plantilla, contraste), el de la unidad (su ficha y sus lecciones
ya escritas) y, al final y sin caché, el día. El orden no se puede cambiar: lo
volátil va último o invalida lo que viene detrás.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import validar  # noqa: E402

MODELO = "claude-opus-5-5"
ESFUERZO = "high"
MAX_TOKENS = 20000
# USD por millón de tokens: entrada, salida, lectura de caché, escritura de caché.
PRECIOS = {"claude-opus-5-5": (4.00, 20.00, 0.20, 5.00)}
TOPE_EJEMPLOS = 40_000  # caracteres de lecciones de ejemplo en el bloque de la unidad

ETAPAS_DEL_RUSO = (
    (6, "Единицы 1-6: инструкции, объяснения и названия упражнений — по-русски."),
    (11, "Единицы 7-11: инструкции и объяснения по-русски; названия упражнений — по-испански с русской пометкой."),
    (18, "Единицы 12-18: инструкции по-испански с краткой русской глоссой; объяснения грамматики по-русски; названия упражнений по-испански."),
    (24, "Единицы 19-24: инструкции и названия по-испански; объяснения по-испански, контраст с русским — по-русски."),
)

INSTRUCCIONES = """Eres el redactor de «Español desde el ruso», un curso de español para rusohablantes
adultos que estudian solos 30 minutos al día durante un año (A0 → A2). Escribes UNA lección completa,
en Markdown, con la forma EXACTA de la plantilla que sigue, en ruso con el español como lengua meta.

Reglas que no se negocian:
1. Un solo punto nuevo por lección y entre 6 y 10 palabras nuevas en «Словарь дня» (tabla de tres
   columnas: Español | Русский | Пример). En A1 la sílaba tónica va en negrita dentro de la palabra.
2. Los apartados llevan número y franja de minutos en el título, contiguos de 0 a 30, con los
   nombres que pide el tipo de día (lección: Разминка, Фонетика o Аудирование, Новое, Практика,
   Выход, Итог; repaso: Разминка, Повторение, Мини-тест, Разбор ошибок, Итог; prueba: Инструкция,
   Тест, Ключи и подсчёт, Разбор ошибок; cultura: Разминка, Материал, Слова, Задание, Итог).
3. Toda lección de tipo `leccion` lleva «### ⚠️ Контраст с русским» con tres pasos: qué hace el
   ruso, qué hace el español, y «**Вы захотите сказать:** ✗ … → **Правильно:** ✅ …». Si el ruso
   AYUDA en ese punto, dilo con la misma claridad.
4. «## Ответы» al final con la clave de TODOS los ejercicios; en la traducción ruso→español la clave
   comenta dónde empuja el ruso al error.
5. El apartado «5. Выход» pide exactamente la producción que dice la columna `salida` del calendario.
6. Ejercicios en escalera: А controlado (formas, con Модель), Б semicontrolado (diálogo o texto con
   huecos y banco de palabras arriba), В traducción ruso→español (desde la unidad 3) o mini-diálogo.
   Fórmulas de instrucción fijas: Прочитайте, Дополните, Соедините, Выберите, Проспрягайте,
   Поставьте в правильном порядке, Исправьте ошибки, Переведите, Ответьте на вопросы, Расскажите,
   Напишите.
7. Español neutro; cuando España y América difieren, una nota con 🌎. Nada de subjuntivo salvo
   fórmulas fijas. Nada de transliteración cirílica de palabras españolas después de la semana 1.
8. No inventes datos (precios, fechas, cifras): si no estás seguro, escribe [VERIFICAR] al lado.
9. Los dos personajes fijos de la unidad siguen siendo los mismos que en las lecciones ya escritas
   de esa unidad (si no hay ninguna, Ana, de Madrid, e Iván, de Moscú, en la unidad 1; para una
   unidad nueva inventa dos y preséntalos en la primera lección).
10. El frontmatter copia tema_es y tema_ru del calendario carácter por carácter y lleva
    `revisado: false`. Devuelve SOLO el Markdown de la lección, sin comentarios ni cercas de código.
"""


def cargar_env() -> None:
    """Lee un .env sencillo (CLAVE=valor) sin pisar lo que ya esté en el entorno."""
    ruta = RAIZ / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip("'\""))


def bloque_estable() -> str:
    partes = [
        INSTRUCCIONES,
        "# PLANTILLA (la forma exacta de una lección)\n\n" + (RAIZ / "curso" / "plantilla-leccion.md").read_text(encoding="utf-8"),
        "# METODOLOGÍA\n\n" + (RAIZ / "programa" / "metodologia.md").read_text(encoding="utf-8"),
        "# ANÁLISIS CONTRASTIVO RUSO → ESPAÑOL\n\n" + (RAIZ / "programa" / "contrastiva-ru-es.md").read_text(encoding="utf-8"),
    ]
    return "\n\n".join(partes)


def _ficha_de_unidad(u: dict) -> str:
    ficha = {k: v for k, v in u.items() if k != "dias"}
    ficha["dias"] = [
        {"semana": f[0], "dia": f[1], "tipo": f[2], "tema_es": f[3], "tema_ru": f[4], "foco": f[5], "salida": f[6]}
        for f in u["dias"]
    ]
    return yaml.safe_dump(ficha, allow_unicode=True, sort_keys=False, width=100)


def _lecciones_de_ejemplo(cal: dict, d: plan.Dia) -> list[pathlib.Path]:
    """Las lecciones ya escritas de la misma unidad (en orden) y, si falta un
    modelo del mismo tipo, una lección de ese tipo de la unidad 1."""
    rutas = [x.ruta for x in plan.dias(cal) if x.unidad == d.unidad and x.ruta.exists() and x.numero != d.numero]
    if not any(validar.frontmatter(r.read_text(encoding="utf-8"))[0].get("tipo") == d.tipo for r in rutas):
        for x in plan.dias(cal):
            if x.unidad == 1 and x.tipo == d.tipo and x.ruta.exists():
                rutas.insert(0, x.ruta)
                break
    return rutas


def bloque_unidad(cal: dict, d: plan.Dia) -> str:
    u = plan.unidad_de(cal, d.semana)
    partes = []
    if u:
        partes.append("# LA UNIDAD\n\n" + _ficha_de_unidad(u))
    else:
        ff = cal["fase_final"]
        partes.append("# LA FASE FINAL\n\n" + yaml.safe_dump({k: v for k, v in ff.items() if k != "dias"}, allow_unicode=True, sort_keys=False))
    usados = 0
    ejemplos = []
    for ruta in _lecciones_de_ejemplo(cal, d):
        texto = ruta.read_text(encoding="utf-8")
        if usados + len(texto) > TOPE_EJEMPLOS:
            break
        usados += len(texto)
        ejemplos.append(f"## {ruta.relative_to(RAIZ)}\n\n{texto}")
    if ejemplos:
        partes.append("# LECCIONES YA ESCRITAS (sigue su forma, sus personajes y su léxico)\n\n" + "\n\n".join(ejemplos))
    return "\n\n".join(partes)


def etapa_del_ruso(unidad: int | None) -> str:
    if unidad is None:
        return ETAPAS_DEL_RUSO[-1][1]
    for tope, texto in ETAPAS_DEL_RUSO:
        if unidad <= tope:
            return texto
    return ETAPAS_DEL_RUSO[-1][1]


def mensaje_del_dia(cal: dict, d: plan.Dia) -> str:
    dias = plan.dias(cal)
    i = dias.index(d)
    ayer = dias[i - 1] if i > 0 else None
    manana = dias[i + 1] if i + 1 < len(dias) else None
    fonetica = "Фонетика" if d.semana <= 8 else "Аудирование"
    lineas = [
        "# EL DÍA QUE HAY QUE ESCRIBIR",
        f"- semana: {d.semana}",
        f"- dia: {d.dia} ({plan.DIAS_RU[d.dia]}), número del año: {d.numero}",
        f"- tipo: {d.tipo}",
        f"- unidad: {d.unidad if d.unidad is not None else 'null'}",
        f"- nivel: {d.nivel}",
        f'- tema_es: "{d.tema_es}"',
        f'- tema_ru: "{d.tema_ru}"',
        f"- foco (lo nuevo del día): {d.foco}",
        f"- salida (lo que el alumno produce en el apartado 5): {d.salida}",
        f"- apartado 2 de una lección: {fonetica}",
        f"- etapa del ruso: {etapa_del_ruso(d.unidad)}",
        f"- ayer: {ayer.tema_es + ' · ' + ayer.tema_ru if ayer else '—'} (la razminka lo recuerda)",
        f"- mañana: {manana.tema_es + ' · ' + manana.tema_ru if manana else '—'} (el Итог lo anuncia en una línea)",
        "",
        "Escribe la lección completa ahora.",
    ]
    return "\n".join(lineas)


def armar_prompt(cal: dict, d: plan.Dia) -> tuple[list[dict], str]:
    sistema = [
        {"type": "text", "text": bloque_estable(), "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": bloque_unidad(cal, d), "cache_control": {"type": "ephemeral"}},
    ]
    return sistema, mensaje_del_dia(cal, d)


def limpiar(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(r"^```(?:markdown|md)?\s*\n", "", texto)
    texto = re.sub(r"\n```\s*$", "", texto)
    if not texto.startswith("---"):
        raise ValueError("la respuesta no empieza por el frontmatter")
    datos, cuerpo = validar.frontmatter(texto + ("\n" if not texto.endswith("\n") else ""))
    datos["revisado"] = False
    fm = yaml.safe_dump(datos, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{fm}\n---\n{cuerpo.lstrip()}".rstrip() + "\n"


def guardar(texto: str, d: plan.Dia) -> pathlib.Path:
    d.carpeta.mkdir(parents=True, exist_ok=True)
    d.ruta.write_text(limpiar(texto), encoding="utf-8")
    return d.ruta


def costo(uso, modelo: str = MODELO) -> float:
    entrada, salida, lectura, escritura = PRECIOS.get(modelo, (0, 0, 0, 0))
    return (
        getattr(uso, "input_tokens", 0) * entrada
        + getattr(uso, "output_tokens", 0) * salida
        + (getattr(uso, "cache_read_input_tokens", 0) or 0) * lectura
        + (getattr(uso, "cache_creation_input_tokens", 0) or 0) * escritura
    ) / 1_000_000


def _texto_de(respuesta) -> str:
    return "".join(b.text for b in respuesta.content if b.type == "text")


def escribir(cal: dict, d: plan.Dia, esfuerzo: str = ESFUERZO, reintentar: bool = True) -> tuple[pathlib.Path, list[str], float]:
    import anthropic

    cargar_env()
    client = anthropic.Anthropic()
    sistema, usuario = armar_prompt(cal, d)
    mensajes: list[dict] = [{"role": "user", "content": usuario}]
    gasto = 0.0
    for intento in (1, 2):
        # Streaming porque la salida es larga; fallbacks por si el clasificador de seguridad
        # declina (la API reintenta sola en otro modelo).
        with client.beta.messages.stream(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=sistema,
            messages=mensajes,
            output_config={"effort": esfuerzo},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            respuesta = stream.get_final_message()
        gasto += costo(respuesta.usage)
        if respuesta.stop_reason == "refusal":
            raise RuntimeError(f"la API declinó la petición ({getattr(respuesta.stop_details, 'category', None)})")
        if respuesta.stop_reason == "max_tokens":
            raise RuntimeError("la lección se cortó por max_tokens; súbelo o acorta los ejemplos")
        ruta = guardar(_texto_de(respuesta), d)
        errores = validar.problemas(ruta, cal)
        if not errores or not reintentar or intento == 2:
            return ruta, errores, gasto
        mensajes.append({"role": "assistant", "content": respuesta.content})
        mensajes.append({"role": "user", "content": "El validador encontró estos problemas; devuelve la lección entera corregida, con la misma forma:\n- " + "\n- ".join(errores)})
    raise AssertionError("inalcanzable")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--semana", type=int, required=True)
    p.add_argument("--dia", type=int)
    p.add_argument("--todos", action="store_true", help="los siete días de la semana")
    p.add_argument("--ver", action="store_true", help="muestra el prompt y no llama a la API")
    p.add_argument("--forzar", action="store_true", help="reescribe una lección que ya existe")
    p.add_argument("--esfuerzo", default=ESFUERZO, choices=["low", "medium", "high", "xhigh", "max"])
    a = p.parse_args(argv)
    if not a.dia and not a.todos:
        p.error("hace falta --dia N o --todos")
    cal = plan.cargar()
    dias = [plan.dia(cal, a.semana, n) for n in (range(1, 8) if a.todos else [a.dia])]
    total = 0.0
    for d in dias:
        if d.ruta.exists() and not a.forzar:
            datos, _ = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))
            estado = "revisada" if datos.get("revisado") else "sin revisar"
            print(f"· {d.etiqueta}: ya existe ({estado}); usa --forzar para reescribirla")
            continue
        if a.ver:
            sistema, usuario = armar_prompt(cal, d)
            print(f"=== {d.etiqueta} · {d.tema_es}")
            print(f"bloque estable: {len(sistema[0]['text']):,} caracteres (cacheado)")
            print(f"bloque unidad:  {len(sistema[1]['text']):,} caracteres (cacheado)")
            print(f"día:            {len(usuario):,} caracteres (sin caché)\n")
            print(usuario)
            continue
        ruta, errores, gasto = escribir(cal, d, a.esfuerzo)
        total += gasto
        estado = "sin problemas" if not errores else f"{len(errores)} problemas del validador:\n    - " + "\n    - ".join(errores)
        print(f"✓ {ruta.relative_to(RAIZ)} escrita (borrador, revisado: false) · ${gasto:.3f} · {estado}")
    if total:
        print(f"gasto total: ${total:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
