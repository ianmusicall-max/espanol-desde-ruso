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

# El sentido RUSO → ESPAÑOL. Vive aquí, y no en el diccionario ni en la
# baraja, porque lo necesitan los dos: con una copia en cada sitio, el día que
# alguien afine la clave se arregla uno y el otro agrupa de otra manera, que es
# como el informe de léxico se quedó sin ver los 50 domingos.
_GLOSA = re.compile(r"\([^)]*\)")
# Lo que corta y lo que no, medido sobre las 3.001 entradas y no elegido a
# ojo. Cortan la barra y las flechas, que separan FORMAS de una misma entrada:
# «его / её (уточнение)» se ordena por «его» y se junta con «его / её зовут» y
# «его / её (о вещи)», que es justo lo que este sentido tiene que enseñar.
#
# NO cortan la coma ni el punto volado, aunque lo parezca: ahí la celda trae
# VARIAS entradas —«идти, ходить, ехать», «аккаунт · пароль»— y cortando se
# quedaban en «идти» y «аккаунт», que arrastraban a cualquier otra fila con esa
# palabra. Con la coma salían 2.720 entradas y una tarjeta que preguntaba
# «идти, ходить, ехать» y respondía «ir · quedar bien / mal · tardar · nevar»;
# sin ella son 2.800 y ningún grupo junta cosas distintas.
_ALTERNATIVA = re.compile(r"\s*[/↔=≠]\s*.*$")
CIRILICA_INICIAL = re.compile(r"^[а-яё]", re.I)


def clave_rusa(ru: str) -> str:
    """Bajo qué palabra se ordena y se busca una entrada rusa.

    La columna rusa no está tan limpia como la española: 1.080 de las 2.985
    entradas traen una glosa, y en 7 la glosa va DELANTE —«(космический)
    корабль», «хорошо» (7–8,9)—. Sin quitarla, esas siete se van al principio
    de la lista bajo el paréntesis y nadie las encuentra buscando su palabra.
    Lo encontró una muestra con los datos de verdad, no leyendo el código.

    Se quita la glosa esté donde esté, y se corta en lo que introduce una
    segunda forma («затем, далее» se ordena por «затем»). El acento de la
    tónica —que el curso marca con un combinante— no cuenta, igual que las
    tildes no cuentan del lado español."""
    import unicodedata

    s = unicodedata.normalize("NFD", ru.lower().replace("ё", "е"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = _GLOSA.sub(" ", s).replace("«", "").replace("»", "")
    s = _ALTERNATIVA.sub("", s)
    s = re.sub(r"[!?.;:…]", " ", s)
    return " ".join(s.split())


def agrupar_por_ruso(rusos: list[str]) -> list[list[int]]:
    """Las posiciones de `rusos` agrupadas por entrada y en orden ruso.

    Devuelve posiciones y no textos a propósito: quien llama ya tiene la lista
    entera —la página la lleva escrita en su HTML y la baraja en sus notas— y
    repetir aquí las 2.985 palabras sería pagarlas dos veces.

    171 palabras rusas tienen varios españoles, y eso no es un defecto que
    haya que deshacer: «автобус» devuelve las cinco formas de decirlo, que es
    lo que este sentido puede enseñar y el otro no.

    Lo que SÍ se queda fuera es una entrada cuya clave no empiece por una
    letra rusa: una entrada de un diccionario ruso tiene que empezar por una
    palabra rusa. Hoy es una sola, la fila «tomar = и пить, и есть», que ya
    descarta por su cuenta el canal de Telegram."""
    grupos: dict[str, list[int]] = {}
    for i, ru in enumerate(rusos):
        k = clave_rusa(ru)
        if k and CIRILICA_INICIAL.match(k):
            grupos.setdefault(k, []).append(i)
    return [grupos[k] for k in sorted(grupos)]



def limpiar(celda: str) -> str:
    celda = celda.replace("**", "").replace("<u>", "").replace("</u>", "")
    return re.sub(r"\s+", " ", celda).strip()


def filas_de(ruta: pathlib.Path) -> tuple[dict, list[list[str]]]:
    """({frontmatter}, filas de vocabulario) de un día, de la tabla que tenga.

    Hay DOS tablas y es lo que decide esta función: las lecciones usan
    «Словарь дня» y los domingos de cultura usan «3. Слова», con dos pares de
    columnas por fila. Vive aquí y la usa también `revisar_lexico.py`, porque
    con una copia en cada script el informe de repeticiones se quedó sin ver
    el vocabulario de los 50 domingos —unas 1.000 entradas— sin que nada
    fallara: `exportar_anki` sí las exportaba, así que la palabra llegaba al
    mazo y la repetición no se listaba nunca."""
    datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
    if not datos:
        return {}, []
    filas = validar.filas_de_vocabulario(cuerpo)
    if not filas and datos.get("tipo") == "cultura":
        filas = _filas_de_cultura(cuerpo)
    return datos, filas


def tarjetas_de(ruta: pathlib.Path) -> list[tuple[str, str, str, str]]:
    datos, filas = filas_de(ruta)
    if not datos:
        return []
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
