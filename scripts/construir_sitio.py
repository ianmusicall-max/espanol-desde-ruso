#!/usr/bin/env python3
"""Convierte el curso en un sitio estático en docs/ (se lee en el móvil).

    .venv/bin/python scripts/construir_sitio.py            # escribe docs/
    .venv/bin/python scripts/construir_sitio.py --destino /tmp/sitio

Genera: docs/index.html (el año entero, semana a semana, con enlace a cada
lección que ya existe), docs/semana-XX/dia-N.html (cada lección, con
anterior / siguiente) y docs/programa/*.html (los documentos del programa).
Si el repositorio es público, GitHub Pages puede servir docs/ tal cual.
"""
from __future__ import annotations

import argparse
import html
import pathlib
import sys

import markdown

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import validar  # noqa: E402

DOCS = RAIZ / "docs"
EXTENSIONES = ["tables", "fenced_code", "sane_lists", "toc"]
CSS = """
:root{--fondo:#fffdf8;--tinta:#1f2328;--acento:#b5452b;--suave:#f1ebdd;--borde:#d9d2c0}
@media(prefers-color-scheme:dark){:root{--fondo:#15171a;--tinta:#e6e2d8;--acento:#f08a5d;--suave:#23262b;--borde:#3a3e45}}
*{box-sizing:border-box}body{margin:0;background:var(--fondo);color:var(--tinta);font:17px/1.55 Georgia,"Times New Roman",serif}
main{max-width:46rem;margin:0 auto;padding:1rem 1rem 4rem}nav.barra{display:flex;justify-content:space-between;gap:1rem;font-family:system-ui,sans-serif;font-size:.9rem;padding:.6rem 0;border-bottom:1px solid var(--borde)}
nav.barra a{color:var(--acento);text-decoration:none}h1{font-size:1.5rem;line-height:1.25;margin:1.2rem 0 .2rem}h1+h1{font-size:1.15rem;color:var(--acento);margin-top:0}
h2{font-family:system-ui,sans-serif;font-size:1.05rem;margin-top:2rem;padding-top:.6rem;border-top:1px solid var(--borde)}h3{font-family:system-ui,sans-serif;font-size:.95rem;margin-top:1.3rem}
table{border-collapse:collapse;width:100%;font-size:.93rem;margin:.6rem 0;display:block;overflow-x:auto}th,td{border:1px solid var(--borde);padding:.3rem .5rem;text-align:left;vertical-align:top}th{background:var(--suave);font-family:system-ui,sans-serif}
blockquote{margin:1rem 0;padding:.6rem 1rem;background:var(--suave);border-left:4px solid var(--acento)}code{font-size:.9em}ul.dias{list-style:none;padding:0}ul.dias li{padding:.25rem 0;border-bottom:1px dotted var(--borde)}
.tipo{font-family:system-ui,sans-serif;font-size:.75rem;color:var(--acento);text-transform:uppercase;letter-spacing:.04em}.falta{opacity:.55}details{margin:.4rem 0}summary{cursor:pointer;font-family:system-ui,sans-serif}
input[type=checkbox]{margin-right:.4rem}
"""


def pagina(titulo: str, cuerpo: str, arriba: str = "", raiz: str = ".") -> str:
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title><style>{CSS}</style></head><body><main>
<nav class="barra"><a href="{raiz}/index.html">← Español desde el ruso</a>{arriba}</nav>
{cuerpo}</main></body></html>"""


def md(texto: str) -> str:
    return markdown.markdown(texto, extensions=EXTENSIONES)


def construir_leccion(ruta: pathlib.Path, destino: pathlib.Path, cal: dict) -> None:
    datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
    d = plan.dia(cal, int(datos["semana"]), int(datos["dia"]))
    dias = plan.dias(cal)
    i = dias.index(d)
    enlaces = []
    for vecino, flecha in ((dias[i - 1] if i > 0 else None, "←"), (dias[i + 1] if i + 1 < len(dias) else None, "→")):
        if vecino and vecino.ruta.exists():
            rel = f"../semana-{vecino.semana:02d}/dia-{vecino.dia}.html"
            enlaces.append(f'<a href="{rel}">{flecha} {html.escape(vecino.etiqueta)}</a>')
    arriba = " · ".join(enlaces)
    aviso = "" if datos.get("revisado") else '<blockquote>Черновик: урок ещё не проверен преподавателем.</blockquote>'
    salida = destino / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(pagina(f"{d.etiqueta} — {d.tema_es}", aviso + md(cuerpo), arriba, raiz=".."), encoding="utf-8")


def construir_indice(destino: pathlib.Path, cal: dict) -> None:
    partes = ["<h1>Español desde el ruso</h1><h1>Испанский с нуля для русскоговорящих · 30 минут в день · год</h1>"]
    partes.append("<p>Программа на 365 дней: уровень A1 → A2 (DELE A2). Каждый день — 30 минут. "
                  "Уроки, которые уже написаны, открываются по ссылке; остальные показывают тему дня.</p>")
    partes.append('<p class="tipo">Programa: <a href="programa/plan-anual.html">plan anual</a> · <a href="programa/metodologia.html">metodología</a> · '
                  '<a href="programa/contrastiva-ru-es.html">contraste ruso-español</a> · <a href="programa/alineacion-mcer-pcic.html">MCER / PCIC / DELE</a> · '
                  '<a href="programa/evaluacion.html">evaluación</a></p>')
    dias = plan.dias(cal)
    por_semana: dict[int, list[plan.Dia]] = {}
    for d in dias:
        por_semana.setdefault(d.semana, []).append(d)
    unidad_actual = None
    for semana, lista in por_semana.items():
        u = plan.unidad_de(cal, semana)
        titulo_u = f"Unidad {u['numero']} · {u['titulo_es']} · {u['titulo_ru']}" if u else cal["fase_final"]["titulo_es"] if semana <= 52 else "Día 365"
        if titulo_u != unidad_actual:
            partes.append(f"<h2>{html.escape(titulo_u)}</h2>")
            if u:
                objetivos = "".join(f"<li>{html.escape(o)}</li>" for o in u["objetivos"])
                partes.append(f"<details><summary>Objetivos · {html.escape(u['nivel'])} · semanas {u['semanas'][0]}-{u['semanas'][1]}</summary><ul>{objetivos}</ul></details>")
            unidad_actual = titulo_u
        fase = plan.fase_de(cal, semana)
        partes.append(f"<h3>Semana {semana} · Неделя {semana} <span class='tipo'>{html.escape(fase)}</span></h3><ul class='dias'>")
        for d in lista:
            etiqueta = f"<span class='tipo'>{plan.TIPO_RU[d.tipo]}</span> "
            texto = f"{d.dia}. {html.escape(d.tema_es)} · {html.escape(d.tema_ru)}"
            if d.ruta.exists():
                partes.append(f"<li>{etiqueta}<a href='semana-{d.semana:02d}/dia-{d.dia}.html'>{texto}</a></li>")
            else:
                partes.append(f"<li class='falta'>{etiqueta}{texto}<br><small>{html.escape(d.foco)}</small></li>")
        partes.append("</ul>")
    (destino / "index.html").write_text(pagina("Español desde el ruso", "\n".join(partes)), encoding="utf-8")


def construir_programa(destino: pathlib.Path) -> None:
    carpeta = destino / "programa"
    carpeta.mkdir(parents=True, exist_ok=True)
    for ruta in sorted((RAIZ / "programa").glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        (carpeta / f"{ruta.stem}.html").write_text(pagina(ruta.stem, md(texto), raiz=".."), encoding="utf-8")
    for ruta in sorted((RAIZ / "referencias").glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        (carpeta / f"ref-{ruta.stem}.html").write_text(pagina(ruta.stem, md(texto), raiz=".."), encoding="utf-8")


def construir(destino: pathlib.Path = DOCS) -> int:
    cal = plan.cargar()
    destino.mkdir(parents=True, exist_ok=True)
    n = 0
    for ruta in validar.lecciones():
        construir_leccion(ruta, destino, cal)
        n += 1
    construir_indice(destino, cal)
    construir_programa(destino)
    (destino / ".nojekyll").write_text("", encoding="utf-8")
    return n


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--destino", type=pathlib.Path, default=DOCS)
    a = p.parse_args(argv)
    n = construir(a.destino)
    print(f"{n} lecciones + índice + programa en {a.destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
