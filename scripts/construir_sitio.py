#!/usr/bin/env python3
"""Convierte el curso en el sitio público de docs/.

    .venv/bin/python scripts/construir_sitio.py
    .venv/bin/python scripts/construir_sitio.py --destino /tmp/sitio

Produce un sitio estático, sin JavaScript salvo el que pidan los anuncios, que
se puede servir con GitHub Pages desde la carpeta docs/ de la rama main:

    index.html          portada en ruso (lo que ve quien llega de Google)
    kurs.html           índice del curso entero, semana a semana
    o-kurse.html        sobre el curso y el autor
    kontakt.html        contacto
    privacy.html        política de privacidad y cookies
    semana-XX/dia-N.html  cada lección
    programa/*.html     la documentación del programa, para el profesor
    sitemap.xml, robots.txt

Lo que se anuncia, lo que se mide y lo que se avisa sobre cookies sale de
`web/sitio.yaml`. Con los campos vacíos el sitio no carga nada de terceros y no
necesita aviso de cookies; por eso se puede publicar antes de pedir el alta en
AdSense.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import pathlib
import re
import sys

import markdown
import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import validar  # noqa: E402

DOCS = RAIZ / "docs"
CONFIG = RAIZ / "web" / "sitio.yaml"
EXTENSIONES = ["tables", "fenced_code", "sane_lists", "toc", "attr_list"]

CSS = """
:root{--fondo:#fffdf8;--tinta:#1f2328;--tenue:#5c6470;--acento:#b5452b;--suave:#f4efe3;--borde:#ddd5c3;--realce:#fff6d9}
@media(prefers-color-scheme:dark){:root{--fondo:#15171a;--tinta:#e7e3d9;--tenue:#a3a9b3;--acento:#f08a5d;--suave:#21242a;--borde:#383d45;--realce:#2b2a20}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--fondo);color:var(--tinta);font:17px/1.6 Georgia,"Times New Roman",serif}
.envoltorio{max-width:46rem;margin:0 auto;padding:0 16px}
header.sitio{border-bottom:1px solid var(--borde)}
header.sitio .envoltorio{display:flex;flex-wrap:wrap;gap:.4rem 1.1rem;align-items:baseline;padding-top:.7rem;padding-bottom:.7rem}
header.sitio a{font-family:system-ui,-apple-system,sans-serif;font-size:.88rem;color:var(--tenue);text-decoration:none}
header.sitio a:hover{color:var(--acento)}
header.sitio a.marca{font-size:1rem;font-weight:700;color:var(--acento);margin-inline-end:auto}
main{padding-bottom:3rem}
h1{font-size:1.6rem;line-height:1.25;margin:1.4rem 0 .3rem}
h1.ru{font-size:1.15rem;color:var(--acento);margin-top:0;font-weight:400}
h2{font-family:system-ui,-apple-system,sans-serif;font-size:1.08rem;margin:2rem 0 .6rem;padding-top:.7rem;border-top:1px solid var(--borde)}
h3{font-family:system-ui,-apple-system,sans-serif;font-size:.97rem;margin:1.4rem 0 .4rem}
a{color:var(--acento)}
table{border-collapse:collapse;width:100%;font-size:.93rem;margin:.7rem 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--borde);padding:.35rem .5rem;text-align:start;vertical-align:top}
th{background:var(--suave);font-family:system-ui,-apple-system,sans-serif}
blockquote{margin:1.1rem 0;padding:.7rem 1rem;background:var(--suave);border-inline-start:4px solid var(--acento)}
blockquote p:first-child{margin-top:0}blockquote p:last-child{margin-bottom:0}
code{font-size:.9em;background:var(--suave);padding:.1em .3em;border-radius:3px}
ul.dias{list-style:none;padding:0;margin:.4rem 0}
ul.dias li{padding:.3rem 0;border-bottom:1px dotted var(--borde)}
.tipo{font-family:system-ui,-apple-system,sans-serif;font-size:.72rem;color:var(--acento);text-transform:uppercase;letter-spacing:.05em}
.falta{color:var(--tenue)}.falta a{color:var(--tenue)}
details{margin:.5rem 0}summary{cursor:pointer;font-family:system-ui,-apple-system,sans-serif;font-size:.92rem}
input[type=checkbox]{margin-inline-end:.4rem}
nav.pasos{display:flex;justify-content:space-between;gap:1rem;font-family:system-ui,-apple-system,sans-serif;font-size:.85rem;margin:2rem 0 0;padding-top:.8rem;border-top:1px solid var(--borde)}
nav.pasos a{text-decoration:none}
.aviso{background:var(--realce);border:1px solid var(--borde);padding:.6rem .8rem;font-size:.88rem;font-family:system-ui,-apple-system,sans-serif;margin:1rem 0}
.heroe{padding:1.5rem 0 .5rem}
.heroe p.lema{font-size:1.15rem;color:var(--tenue);margin:.3rem 0 1.2rem}
.boton{display:inline-block;background:var(--acento);color:#fff;padding:.65rem 1.3rem;border-radius:6px;text-decoration:none;font-family:system-ui,-apple-system,sans-serif;font-size:1rem}
.boton.secundario{background:transparent;color:var(--acento);border:1px solid var(--acento)}
.botones{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.2rem 0}
.rejilla{display:grid;gap:1rem;grid-template-columns:1fr}
@media(min-width:34rem){.rejilla{grid-template-columns:1fr 1fr}}
.tarjeta{border:1px solid var(--borde);border-radius:8px;padding:.9rem 1rem;background:var(--suave)}
.tarjeta h3{margin-top:0}
.anuncio{margin:1.6rem 0;min-height:1px;text-align:center}
.anuncio::before{content:attr(data-etiqueta);display:block;font-family:system-ui,-apple-system,sans-serif;font-size:.68rem;color:var(--tenue);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.25rem}
footer.sitio{border-top:1px solid var(--borde);padding:1.2rem 0 2.5rem;font-family:system-ui,-apple-system,sans-serif;font-size:.84rem;color:var(--tenue)}
footer.sitio a{color:var(--tenue)}
#cookies{position:fixed;inset-inline:0;bottom:0;background:var(--suave);border-top:1px solid var(--borde);padding:.8rem 16px;font-family:system-ui,-apple-system,sans-serif;font-size:.85rem;display:flex;flex-wrap:wrap;gap:.7rem;align-items:center;justify-content:center;z-index:9}
"""

MENU = [
    ("index.html", "Главная"),
    ("kurs.html", "Все уроки"),
    ("o-kurse.html", "О курсе"),
    ("kontakt.html", "Контакты"),
]


# ---------------------------------------------------------------- configuración
def cargar_config(ruta: pathlib.Path = CONFIG) -> dict:
    with open(ruta, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("dominio", "")
    cfg["dominio"] = (cfg.get("dominio") or "").rstrip("/")
    cfg.setdefault("adsense", {}).setdefault("bloques", {})
    cfg.setdefault("analitica", {})
    cfg.setdefault("autor", {})
    return cfg


def hay_anuncios(cfg: dict) -> bool:
    return bool((cfg.get("adsense") or {}).get("cliente"))


def hay_analitica(cfg: dict) -> bool:
    return bool((cfg.get("analitica") or {}).get("google"))


def necesita_cookies(cfg: dict) -> bool:
    """Solo se avisa de cookies si de verdad las hay."""
    return hay_anuncios(cfg) or hay_analitica(cfg)


# ------------------------------------------------------------------- fragmentos
def anuncio(cfg: dict, ranura: str) -> str:
    """Un bloque de AdSense, o nada si no está configurado.

    Sin cliente no se escribe ni el contenedor: una página sin anuncios no
    tiene por qué llevar huecos vacíos ni pedir scripts a Google.
    """
    cliente = (cfg.get("adsense") or {}).get("cliente")
    bloque = ((cfg.get("adsense") or {}).get("bloques") or {}).get(ranura)
    if not cliente or not bloque:
        return ""
    return (
        f'<div class="anuncio" data-etiqueta="Реклама">'
        f'<ins class="adsbygoogle" style="display:block" data-ad-client="{html.escape(cliente)}" '
        f'data-ad-slot="{html.escape(str(bloque))}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
        f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>'
    )


def cabeza_terceros(cfg: dict) -> str:
    partes = []
    if hay_anuncios(cfg):
        cliente = html.escape(cfg["adsense"]["cliente"])
        partes.append(
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={cliente}" crossorigin="anonymous"></script>'
        )
    if hay_analitica(cfg):
        medidor = html.escape(cfg["analitica"]["google"])
        partes.append(
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={medidor}"></script>'
            f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}"
            f'gtag("js",new Date());gtag("config","{medidor}");</script>'
        )
    return "".join(partes)


def banda_cookies(cfg: dict, raiz: str) -> str:
    if not necesita_cookies(cfg):
        return ""
    return (
        '<div id="cookies"><span>Мы используем файлы cookie для показа рекламы и статистики посещений. '
        f'<a href="{raiz}/privacy.html">Подробнее</a>.</span>'
        '<button class="boton" style="padding:.35rem .9rem;font-size:.85rem" '
        "onclick=\"try{localStorage.setItem('cookies','1')}catch(e){};this.parentNode.remove()\">Понятно</button></div>"
        "<script>try{if(localStorage.getItem('cookies')){var b=document.getElementById('cookies');b&&b.remove()}}catch(e){}</script>"
    )


def pagina(cfg, titulo, cuerpo, *, descripcion="", ruta="", raiz=".", extra_cabeza="", jsonld="") -> str:
    dominio = cfg["dominio"]
    canonica = f"{dominio}/{ruta}" if dominio and ruta else dominio
    menu = " ".join(
        f'<a href="{raiz}/{destino}"{" class=\"marca\"" if i == 0 else ""}>{html.escape(texto)}</a>'
        for i, (destino, texto) in enumerate(MENU)
    )
    meta = f'<meta name="description" content="{html.escape(descripcion)}">' if descripcion else ""
    canon = f'<link rel="canonical" href="{html.escape(canonica)}">' if canonica else ""
    og = (
        f'<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU">'
        f'<meta property="og:title" content="{html.escape(titulo)}">'
        f'<meta property="og:description" content="{html.escape(descripcion)}">'
        + (f'<meta property="og:url" content="{html.escape(canonica)}">' if canonica else "")
    )
    estructura = f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="{cfg.get('idioma', 'ru')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title>
{meta}{canon}{og}{estructura}
<style>{CSS}</style>
{cabeza_terceros(cfg)}{extra_cabeza}
</head>
<body>
<header class="sitio"><div class="envoltorio">{menu}</div></header>
<main><div class="envoltorio">
{cuerpo}
</div></main>
<footer class="sitio"><div class="envoltorio">
<p>{html.escape(cfg['titulo'])} · <a href="{raiz}/o-kurse.html">О курсе</a> · <a href="{raiz}/kontakt.html">Контакты</a> · <a href="{raiz}/privacy.html">Конфиденциальность</a></p>
<p>Материалы курса можно свободно использовать для учёбы.</p>
</div></footer>
{banda_cookies(cfg, raiz)}
</body>
</html>"""


def md(texto: str) -> str:
    return markdown.markdown(texto, extensions=EXTENSIONES)


# ----------------------------------------------------------------------- páginas
def escritas(cal: dict) -> list[plan.Dia]:
    return [d for d in plan.dias(cal) if d.ruta.exists()]


def construir_leccion(d: plan.Dia, cfg: dict, destino: pathlib.Path, cal: dict, todos: list[plan.Dia]) -> None:
    datos, cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))
    i = todos.index(d)
    anterior = next((x for x in reversed(todos[:i]) if x.ruta.exists()), None)
    siguiente = next((x for x in todos[i + 1:] if x.ruta.exists()), None)

    html_cuerpo = md(cuerpo)
    # El anuncio de dentro va antes de los ejercicios, que es donde el lector
    # hace una pausa natural. Si no hay anuncios configurados, no se parte nada.
    dentro = anuncio(cfg, "dentro")
    if dentro:
        # El encabezado lleva un id que pone markdown, así que se busca por
        # patrón y no por texto literal; si el día no tiene ese apartado
        # (un repaso, una prueba), el anuncio simplemente no se inserta.
        marca = re.search(r"<h2[^>]*>4\.\s*(Практика|Задание)", html_cuerpo)
        if marca:
            html_cuerpo = html_cuerpo[:marca.start()] + dentro + html_cuerpo[marca.start():]

    titulo = f"Урок {d.numero}: {d.tema_ru} — испанский с нуля"
    descripcion = f"Урок {d.numero} курса испанского для русскоговорящих: {d.tema_ru}. {d.foco[:110]}"
    aviso = "" if datos.get("revisado") else '<p class="aviso">Черновик: урок написан, но преподаватель его ещё не вычитал.</p>'

    pasos = []
    if anterior:
        pasos.append(f'<a href="../semana-{anterior.semana:02d}/dia-{anterior.dia}.html">← Урок {anterior.numero}</a>')
    else:
        pasos.append("<span></span>")
    pasos.append(f'<a href="../kurs.html">Все уроки</a>')
    if siguiente:
        pasos.append(f'<a href="../semana-{siguiente.semana:02d}/dia-{siguiente.dia}.html">Урок {siguiente.numero} →</a>')
    else:
        pasos.append("<span></span>")

    cuerpo_final = (
        f'<p class="tipo">Урок {d.numero} из 365 · неделя {d.semana} · {html.escape(plan.TIPO_RU[d.tipo])} · уровень {html.escape(d.nivel)}</p>'
        + anuncio(cfg, "cabecera")
        + aviso
        + html_cuerpo
        + anuncio(cfg, "pie")
        + f'<nav class="pasos">{"".join(pasos)}</nav>'
    )
    salida = destino / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        pagina(cfg, titulo, cuerpo_final, descripcion=descripcion,
               ruta=f"semana-{d.semana:02d}/dia-{d.dia}.html", raiz=".."),
        encoding="utf-8",
    )


def construir_portada(cfg: dict, destino: pathlib.Path, cal: dict) -> None:
    hechas = escritas(cal)
    primera = hechas[0] if hechas else None
    enlace_primera = f"semana-{primera.semana:02d}/dia-{primera.dia}.html" if primera else "kurs.html"
    jsonld = (
        '{"@context":"https://schema.org","@type":"Course",'
        f'"name":{yaml.dump(cfg["titulo"], allow_unicode=True, default_flow_style=True).strip()[:-1] if False else __import__("json").dumps(cfg["titulo"], ensure_ascii=False)},'
        f'"description":{__import__("json").dumps(cfg["descripcion"], ensure_ascii=False)},'
        '"inLanguage":"ru","teaches":"Spanish","educationalLevel":"A1-A2",'
        f'"provider":{{"@type":"Person","name":{__import__("json").dumps(cfg.get("autor", {}).get("nombre", ""), ensure_ascii=False)}}},'
        '"isAccessibleForFree":true}'
    )
    cuerpo = f"""
<div class="heroe">
<h1>Испанский с нуля для русскоговорящих</h1>
<p class="lema">{html.escape(cfg['lema'])}</p>
<p>Бесплатный курс из 365 уроков по 30 минут: от алфавита до уровня <strong>A2</strong> и экзамена
<strong>DELE A2</strong>. Без регистрации, без оплаты, прямо в браузере.</p>
<div class="botones">
<a class="boton" href="{enlace_primera}">Начать с первого урока</a>
<a class="boton secundario" href="kurs.html">Посмотреть программу</a>
</div>
</div>
{anuncio(cfg, "cabecera")}

<h2>Чем этот курс отличается</h2>
<p>Обычный учебник объясняет испанское правило. Этот объясняет ещё и то, <strong>где вас подводит
родной язык</strong>. В каждом уроке есть раздел «Контраст с русским», который называет ошибку
до того, как вы её сделаете:</p>
<blockquote>
<p><strong>Вы захотите сказать:</strong> ✗ <em>Tengo hermano.</em><br>
<strong>Правильно:</strong> ✅ <em>Tengo <strong>un</strong> hermano.</em></p>
<p>В русском артикля нет совсем, поэтому вы не «забываете» его — вы не слышите, что чего-то
не хватает. Первые три месяца курса артикль разбирается в каждом ключе к каждому упражнению.</p>
</blockquote>
<p>И наоборот: там, где русский <em>помогает</em>, курс говорит об этом прямо. <em>Me gusta el
café</em> — это буквально «мне нравится кофе», та же конструкция. Возвратные глаголы — это <em>-ся</em>.
Прошедшее время строится на том же виде, который у вас уже есть.</p>

<h2>Как устроен день</h2>
<table>
<tr><th>Минуты</th><th>Что происходит</th></tr>
<tr><td>0–3</td><td>Разминка: карточки вчерашних слов</td></tr>
<tr><td>3–6</td><td>Фонетика или аудирование</td></tr>
<tr><td>6–16</td><td>Новое: пример, правило и контраст с русским</td></tr>
<tr><td>16–26</td><td>Три упражнения с ключами</td></tr>
<tr><td>26–29</td><td>Выход: вы что-то пишете или записываете вслух</td></tr>
<tr><td>29–30</td><td>Итог и новые карточки</td></tr>
</table>
<p>Ровно 30 минут. Не 45 и не «сколько получится»: день, который не помещается в полчаса,
разбивается на два дня.</p>

{anuncio(cfg, "dentro")}

<h2>Что будет через год</h2>
<div class="rejilla">
<div class="tarjeta"><h3>Через 2 недели</h3><p>Читаете вслух любое испанское слово, здороваетесь,
представляетесь и считаете до двадцати.</p></div>
<div class="tarjeta"><h3>Через 3 месяца</h3><p>Рассказываете о семье, доме и своём дне,
заказываете еду и покупаете одежду.</p></div>
<div class="tarjeta"><h3>Через полгода (A1)</h3><p>Путешествуете, идёте к врачу, даёте советы.
Сдали бы экзамен уровня A1.</p></div>
<div class="tarjeta"><h3>Через год (A2)</h3><p>Говорите о прошлом и будущем, спорите, пишете письма.
Готовы к <strong>DELE A2</strong> — тому самому, который нужен для гражданства Испании.</p></div>
</div>

<h2>Сколько готово сейчас</h2>
<p><strong>{len(hechas)} уроков из 365</strong> уже написаны и открыты.
Остальные выходят по мере готовности — программа всех 365 дней составлена целиком, её можно
посмотреть на странице <a href="kurs.html">«Все уроки»</a>.</p>
<div class="botones"><a class="boton" href="{enlace_primera}">Начать сейчас</a></div>
{anuncio(cfg, "pie")}
"""
    destino.joinpath("index.html").write_text(
        pagina(cfg, f"{cfg['titulo']} — {cfg['lema']}", cuerpo,
               descripcion=cfg["descripcion"], ruta="index.html", jsonld=jsonld),
        encoding="utf-8",
    )


def construir_indice_curso(cfg: dict, destino: pathlib.Path, cal: dict) -> None:
    partes = ["<h1>Все уроки</h1><h1 class='ru'>365 дней, 52 недели, 24 темы</h1>",
              anuncio(cfg, "cabecera"),
              "<p>Ссылками открываются уроки, которые уже написаны. У остальных показана тема дня: "
              "программа составлена на весь год вперёд.</p>"]
    dias = plan.dias(cal)
    por_semana: dict[int, list[plan.Dia]] = {}
    for d in dias:
        por_semana.setdefault(d.semana, []).append(d)
    unidad_actual = None
    for semana, lista in por_semana.items():
        u = plan.unidad_de(cal, semana)
        if u:
            titulo_u = f"Тема {u['numero']}: {u['titulo_ru']} · {u['titulo_es']}"
        elif semana <= 52:
            titulo_u = f"{cal['fase_final']['titulo_ru']} · {cal['fase_final']['titulo_es']}"
        else:
            titulo_u = "День 365"
        if titulo_u != unidad_actual:
            partes.append(f"<h2>{html.escape(titulo_u)}</h2>")
            if u:
                objetivos = "".join(f"<li>{html.escape(o)}</li>" for o in u["objetivos"])
                partes.append(
                    f"<details><summary>Чему вы научитесь · уровень {html.escape(u['nivel'])} · недели {u['semanas'][0]}–{u['semanas'][1]}</summary><ul>{objetivos}</ul></details>"
                )
            unidad_actual = titulo_u
        partes.append(f"<h3>Неделя {semana}</h3><ul class='dias'>")
        for d in lista:
            etiqueta = f"<span class='tipo'>{plan.TIPO_RU[d.tipo]}</span> "
            texto = f"Урок {d.numero}. {html.escape(d.tema_ru)}"
            if d.ruta.exists():
                partes.append(f"<li>{etiqueta}<a href='semana-{d.semana:02d}/dia-{d.dia}.html'>{texto}</a></li>")
            else:
                partes.append(f"<li class='falta'>{etiqueta}{texto}<br><small>{html.escape(d.foco)}</small></li>")
        partes.append("</ul>")
    partes.append(anuncio(cfg, "pie"))
    destino.joinpath("kurs.html").write_text(
        pagina(cfg, "Все уроки курса испанского — 365 дней",
               "\n".join(partes),
               descripcion="Программа курса испанского языка для русскоговорящих: 365 уроков по 30 минут, от алфавита до уровня A2.",
               ruta="kurs.html"),
        encoding="utf-8",
    )


def construir_estaticas(cfg: dict, destino: pathlib.Path, cal: dict) -> None:
    autor = cfg.get("autor", {})
    hechas = len(escritas(cal))

    # --- О курсе
    cuerpo = f"""
<h1>О курсе</h1>
{anuncio(cfg, "cabecera")}
<h2>Кто это написал</h2>
<p>{html.escape(autor.get('descripcion', ''))}</p>
<h2>Почему «с русского», а не просто «испанский»</h2>
<p>Курсы испанского пишут для всех сразу. Но ошибки у всех разные. Русскоговорящий пропускает
артикль не потому, что невнимателен, а потому что в его языке этой категории нет вообще.
Он ставит прилагательное перед существительным, потому что так устроен русский. Он говорит
<em>«мне тридцать»</em> вместо <em>tengo treinta años</em>, потому что в русском возраст — в
дательном падеже.</p>
<p>Курс построен вокруг этих двадцати типичных ошибок. Они перечислены заранее, разбираются
по одной и возвращаются в ключах к упражнениям и в вариантах ответов тестов: неправильный
вариант — это всегда то, что сказал бы русскоговорящий.</p>
<h2>Как заниматься</h2>
<p>Один урок в день, по порядку, 30 минут. Не больше: курс рассчитан на год, и пропущенная
неделя вредит меньше, чем три урока подряд за один вечер. В конце каждого урока есть «Выход» —
то, что нужно написать или записать вслух. Без этого урок не считается сделанным.</p>
<h2>Сколько это стоит</h2>
<p>Нисколько. Курс открыт целиком, без регистрации. Сайт существует за счёт рекламы.</p>
<p>Сейчас открыто <strong>{hechas} уроков из 365</strong>.</p>
{anuncio(cfg, "pie")}
"""
    destino.joinpath("o-kurse.html").write_text(
        pagina(cfg, "О курсе и авторе — испанский с нуля",
               cuerpo, descripcion="Кто написал курс испанского для русскоговорящих и почему он построен на контрасте с русским языком.",
               ruta="o-kurse.html"),
        encoding="utf-8",
    )

    # --- Контакты
    if autor.get("email"):
        contacto = (f'<p>Пишите на <a href="mailto:{html.escape(autor["email"])}">'
                    f'{html.escape(autor["email"])}</a>: об ошибке в уроке, о том, что непонятно, '
                    f'или о занятиях с преподавателем.</p>')
    else:
        contacto = ('<p class="aviso">Адрес для связи пока не указан. Чтобы он появился здесь, '
                    'впишите его в поле <code>autor.email</code> в файле <code>web/sitio.yaml</code> '
                    'и соберите сайт заново.</p>')
    cuerpo = f"""
<h1>Контакты</h1>
{contacto}
<p>Нашли ошибку в уроке? Это самое полезное письмо, которое можно прислать: курс пишется
последовательно, и опечатка в ключе портит упражнение всем.</p>
<h2>Об авторе</h2>
<p>{html.escape(autor.get('nombre', ''))}. {html.escape(autor.get('descripcion', ''))}</p>
"""
    destino.joinpath("kontakt.html").write_text(
        pagina(cfg, "Контакты — испанский с нуля", cuerpo,
               descripcion="Как связаться с автором курса испанского языка для русскоговорящих.",
               ruta="kontakt.html"),
        encoding="utf-8",
    )

    # --- Политика конфиденциальности (refleja lo que el sitio HACE de verdad)
    bloques = ["<h1>Политика конфиденциальности</h1>",
               f"<p>Обновлено: {dt.date.today().isoformat()}.</p>",
               "<h2>Что собирает сам сайт</h2>",
               "<p>Ничего. На сайте нет регистрации, форм, комментариев и личных кабинетов. "
               "Мы не просим и не храним ваше имя, адрес или электронную почту.</p>"]
    if hay_anuncios(cfg):
        bloques += [
            "<h2>Реклама</h2>",
            "<p>Сайт показывает рекламу через Google AdSense. Google и его партнёры используют "
            "файлы cookie, чтобы показывать объявления с учётом ваших прежних посещений этого "
            "и других сайтов. Персонализированную рекламу можно отключить в "
            '<a href="https://www.google.com/settings/ads" rel="nofollow noopener">настройках рекламы Google</a>, '
            'а сторонние поставщики — на <a href="https://www.aboutads.info/choices/" rel="nofollow noopener">aboutads.info</a>.</p>',
            '<p>Как Google использует данные: <a href="https://policies.google.com/technologies/partner-sites" rel="nofollow noopener">policies.google.com</a>.</p>',
        ]
    if hay_analitica(cfg):
        bloques += [
            "<h2>Статистика</h2>",
            "<p>Мы считаем посещения через Google Analytics, чтобы понимать, какие уроки читают. "
            "Это обезличенная статистика: мы не видим, кто вы.</p>",
        ]
    if not necesita_cookies(cfg):
        bloques += [
            "<h2>Файлы cookie</h2>",
            "<p>Сейчас сайт не использует ни рекламные, ни аналитические cookie и не загружает "
            "скрипты сторонних сервисов. Единственное, что может сохраняться в браузере, — "
            "ваши собственные настройки чтения. Если это изменится, страница будет обновлена, "
            "и вы увидите уведомление.</p>",
        ]
    bloques += [
        "<h2>Ваши права</h2>",
        "<p>Если вы в Европейском союзе, у вас есть право на доступ к своим данным, их исправление "
        "и удаление. Поскольку сайт сам никаких данных о вас не хранит, обращаться с такими "
        'запросами нужно напрямую к Google. Вопросы о сайте — через страницу <a href="kontakt.html">контактов</a>.</p>',
        "<h2>Дети</h2>",
        "<p>Сайт не предназначен для детей младше 13 лет и не собирает их данные сознательно.</p>",
    ]
    destino.joinpath("privacy.html").write_text(
        pagina(cfg, "Политика конфиденциальности", "\n".join(bloques),
               descripcion="Какие данные собирает сайт курса испанского языка и как используются файлы cookie.",
               ruta="privacy.html"),
        encoding="utf-8",
    )


def construir_programa(cfg: dict, destino: pathlib.Path) -> None:
    """La documentación del programa, en español, para el profesor."""
    carpeta = destino / "programa"
    carpeta.mkdir(parents=True, exist_ok=True)
    for origen, prefijo in ((RAIZ / "programa", ""), (RAIZ / "referencias", "ref-")):
        for ruta in sorted(origen.glob("*.md")):
            texto = ruta.read_text(encoding="utf-8")
            carpeta.joinpath(f"{prefijo}{ruta.stem}.html").write_text(
                pagina(cfg, f"{ruta.stem} — документация курса", md(texto),
                       descripcion="Документация программы курса (на испанском, для преподавателя).",
                       ruta=f"programa/{prefijo}{ruta.stem}.html", raiz=".."),
                encoding="utf-8",
            )


def construir_sitemap(cfg: dict, destino: pathlib.Path, cal: dict) -> None:
    dominio = cfg["dominio"]
    hoy = dt.date.today().isoformat()
    urls = [("index.html", "1.0"), ("kurs.html", "0.9"), ("o-kurse.html", "0.5"),
            ("kontakt.html", "0.3"), ("privacy.html", "0.3")]
    urls += [(f"semana-{d.semana:02d}/dia-{d.dia}.html", "0.8") for d in escritas(cal)]
    if dominio:
        filas = "".join(
            f"<url><loc>{html.escape(dominio)}/{u}</loc><lastmod>{hoy}</lastmod><priority>{p}</priority></url>"
            for u, p in urls
        )
        cuerpo = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{filas}</urlset>\n'
        destino.joinpath("sitemap.xml").write_text(cuerpo, encoding="utf-8")
    robots = "User-agent: *\nAllow: /\n"
    if dominio:
        robots += f"\nSitemap: {dominio}/sitemap.xml\n"
    destino.joinpath("robots.txt").write_text(robots, encoding="utf-8")


def construir(destino: pathlib.Path = DOCS, cfg: dict | None = None) -> int:
    cal = plan.cargar()
    cfg = cfg or cargar_config()
    destino.mkdir(parents=True, exist_ok=True)
    todos = plan.dias(cal)
    hechas = escritas(cal)
    for d in hechas:
        construir_leccion(d, cfg, destino, cal, todos)
    construir_portada(cfg, destino, cal)
    construir_indice_curso(cfg, destino, cal)
    construir_estaticas(cfg, destino, cal)
    construir_programa(cfg, destino)
    construir_sitemap(cfg, destino, cal)
    destino.joinpath(".nojekyll").write_text("", encoding="utf-8")
    return len(hechas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--destino", type=pathlib.Path, default=DOCS)
    a = p.parse_args(argv)
    cfg = cargar_config()
    n = construir(a.destino, cfg)
    print(f"{n} lecciones + portada, índice, estáticas, programa y sitemap en {a.destino}")
    print(f"  anuncios: {'sí (' + cfg['adsense']['cliente'] + ')' if hay_anuncios(cfg) else 'no configurados'}")
    print(f"  analítica: {'sí' if hay_analitica(cfg) else 'no configurada'}")
    print(f"  aviso de cookies: {'sí' if necesita_cookies(cfg) else 'no hace falta'}")
    if not cfg.get("autor", {}).get("email"):
        print("  aviso: sin correo de contacto en web/sitio.yaml; AdSense suele pedirlo para aprobar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
