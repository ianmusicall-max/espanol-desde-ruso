#!/usr/bin/env python3
"""Las preguntas de un día de tipo `prueba`, leídas de la propia lección.

    .venv/bin/python scripts/pruebas.py          # qué unidades se pueden hacer interactivas

El calendario tiene 23 días `prueba`, uno al cerrar cada unidad, y cada uno
trae 15 preguntas de opción múltiple en tres bloques y su clave de respuestas.
Eso ya lo escribió y lo revisó el profesor: aquí no se inventa ni una pregunta.
Lo único que falta es que en la web se puedan contestar en vez de leerse con la
clave a un scroll de distancia, que es como nadie se autoevalúa.

**La lección es la única fuente de verdad.** Si las preguntas vivieran además
en un YAML, el día que el profesor corrigiera una en el Markdown la web
seguiría con la vieja. Este proyecto ya se ha tropezado varias veces con lo
escrito y lo que corre dejando de coincidir.

**Y falla de forma segura.** `leer` devuelve `None` en cuanto algo no cuadra
—una clave con más respuestas que preguntas, una letra que no está entre las
opciones, un bloque descolgado— y entonces esa unidad simplemente no tiene test
interactivo y su página se queda como está hoy. Decirle a alguien que acertó
cuando falló es mucho peor que no ofrecerle el test.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import validar  # noqa: E402

# Las letras de las opciones, en el orden en que tienen que aparecer. Son
# cirílicas porque las lecciones están en ruso.
LETRAS = ("а", "б", "в", "г", "д")

# Cada pregunta empieza por «N. » al principio de línea y se acaba en el primer
# renglón en blanco. Lo que hay en medio es el enunciado y sus opciones.
INICIO = re.compile(r"^(\d+)\.[ \t]+", re.M)

# El marcador de una opción: «а) » con un espacio delante o al principio.
#
# Se corta por el MARCADOR y no por el «·» que separa las opciones, y eso no es
# un detalle: en la unidad 4 una opción es una transcripción fonética que lleva
# su propio «·» dentro —«а) [дос · а-би-та-сьо-нес]»— y cortando por el punto
# se partía en dos. Y en la unidad 5 las opciones se parten entre dos renglones,
# así que antes de mirar hay que juntar las líneas. Las dos fallaban con la
# primera versión, y el fallo seguro las dejó fuera en vez de inventarse una
# respuesta: por eso existe.
MARCADOR = re.compile(r"(?:^|\s)([абвгд])\)\s")

# En la clave la letra va suelta («1 б») o en negrita («1 **б**»), y detrás
# suele venir de qué lección sale la respuesta: «(нед. 2, день 5)». Eso último
# es un regalo del profesor: permite que el resultado enlace a la lección donde
# se enseña lo que acabas de fallar.
RESPUESTA = re.compile(r"\b(\d+)\s+\*{0,2}([абвгд])\*{0,2}(?!\w)")
DE_DONDE = re.compile(r"нед\.\s*(\d+),\s*д(?:ень|ня)\s*(\d+)")


@dataclasses.dataclass
class Pregunta:
    bloque: str
    enunciado: str
    opciones: list[str]
    correcta: int
    semana: int | None = None   # de qué lección sale la respuesta
    dia: int | None = None


def _bloques_de_preguntas(texto: str) -> list[tuple[str, str]]:
    """(título, cuerpo) de cada `### …` que esté dentro de `## 2. Тест`."""
    partes = re.split(r"^## .+$", texto, flags=re.M)
    cabeceras = re.findall(r"^## (.+)$", texto, flags=re.M)
    for cabecera, cuerpo in zip(cabeceras, partes[1:]):
        if cabecera.strip().startswith("2."):
            trozos = re.split(r"^### (.+)$", cuerpo, flags=re.M)
            return list(zip(trozos[1::2], trozos[2::2]))
    return []


def _bloques_de_clave(texto: str) -> list[str]:
    """El cuerpo de cada bloque de la sección `## Ответы`.

    Las líneas se juntan antes de mirar: en la clave una respuesta puede partirse
    en dos renglones («3 б (нед. 2,\\nдень 1)») y leída línea a línea se pierde."""
    if "## Ответы" not in texto:
        return []
    clave = texto.split("## Ответы", 1)[1]
    clave = re.sub(r"\n(?!\n)", " ", clave)
    trozos = re.split(r"\*\*\d+\.\s*[^*]+?:\*\*", clave)
    return trozos[1:]


def _preguntas_del_bloque(cuerpo: str) -> list[tuple[str, str, list[tuple[str, str]]]] | None:
    """(número, enunciado, [(letra, texto)…]) de cada pregunta de un bloque."""
    trozos = INICIO.split(cuerpo)
    salida = []
    for numero, texto in zip(trozos[1::2], trozos[2::2]):
        # Hasta el primer renglón en blanco: lo que viene después es el recuento
        # de puntos, no una opción.
        texto = " ".join(texto.split("\n\n")[0].split())
        marcas = list(MARCADOR.finditer(texto))
        if not marcas:
            return None
        opciones = []
        for j, m in enumerate(marcas):
            fin = marcas[j + 1].start() if j + 1 < len(marcas) else len(texto)
            opciones.append((m.group(1), texto[m.end():fin].strip().rstrip("·").strip()))
        salida.append((numero, texto[:marcas[0].start()].strip(), opciones))
    return salida


def leer(texto: str) -> list[Pregunta] | None:
    """Las preguntas con su respuesta, o None si no se puede estar seguro."""
    preguntas = _bloques_de_preguntas(texto)
    claves = _bloques_de_clave(texto)
    if not preguntas or len(preguntas) != len(claves):
        return None

    salida: list[Pregunta] = []
    for (titulo, cuerpo), clave in zip(preguntas, claves):
        encontradas = _preguntas_del_bloque(cuerpo)
        respuestas = RESPUESTA.findall(clave)
        # Mismo número de preguntas que de respuestas, y numeradas 1..n en orden
        if encontradas is None or len(encontradas) != len(respuestas):
            return None
        if [n for n, _, _ in encontradas] != [str(i) for i in range(1, len(encontradas) + 1)]:
            return None
        if [n for n, _ in respuestas] != [str(i) for i in range(1, len(respuestas) + 1)]:
            return None

        # De qué lección sale cada respuesta, si la clave lo dice. Se corta la
        # clave por respuestas para que cada «(нед. X, день Y)» quede con la suya.
        cortes = [m.start() for m in RESPUESTA.finditer(clave)] + [len(clave)]

        for i, ((_, enunciado, opciones), (_, letra)) in enumerate(zip(encontradas, respuestas)):
            letras = [x for x, _ in opciones]
            if letras != list(LETRAS[:len(letras)]):   # а, б, в… sin saltos
                return None
            if letra not in letras:
                return None
            donde = DE_DONDE.search(clave[cortes[i]:cortes[i + 1]])
            salida.append(Pregunta(
                bloque=titulo.strip(),
                enunciado=enunciado.strip(),
                opciones=[t for _, t in opciones],
                correcta=letras.index(letra),
                semana=int(donde.group(1)) if donde else None,
                dia=int(donde.group(2)) if donde else None,
            ))
    return salida or None


def de_la_leccion(ruta: pathlib.Path) -> list[Pregunta] | None:
    _, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
    return leer(cuerpo)


def main(argv=None) -> int:
    cal = plan.cargar()
    dias = [d for d in plan.dias(cal) if d.tipo == "prueba"]
    hechos = [d for d in dias if d.ruta.exists()]
    print(f"{len(dias)} días de prueba en el calendario · {len(hechos)} escritos\n")
    bien = 0
    for d in hechos:
        preguntas = de_la_leccion(d.ruta)
        if preguntas:
            bien += 1
            con_origen = sum(1 for p in preguntas if p.semana)
            print(f"  ✓ unidad {d.unidad:2} (día {d.numero:3}): {len(preguntas)} preguntas · "
                  f"{con_origen} enlazan a su lección")
        else:
            print(f"  ✗ unidad {d.unidad:2} (día {d.numero:3}): no se puede leer con seguridad, "
                  f"se queda como está")
    print(f"\n{bien} de {len(hechos)} se pueden hacer interactivas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
