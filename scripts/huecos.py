#!/usr/bin/env python3
"""Los ejercicios de rellenar huecos, leídos de la propia lección.

    .venv/bin/python scripts/huecos.py     # qué ejercicios se pueden contestar

Hay **1.488 huecos escritos en 89 de las 100 lecciones**, y 61 de esos
ejercicios traen su **banco de palabras**:

    ### Упражнение Б. Дополните. Банк слов:
    > aquí · ahí · allí · cerca de · lejos de · al lado de · fuera de · del

    1. — ¿Dónde está mi móvil? — ______, en la mesa, ______ tu libro.

    **Б.** 1. Aquí / al lado de · 2. cerca de · 3. fuera de · …

O sea que el ejercicio, las fichas y las respuestas ya están escritos y
revisados por el profesor. Aquí no se inventa nada: lo único que falta es que
en la web se puedan pulsar en vez de leerse con la clave a un scroll.

**Y falla de forma segura**, igual que `pruebas.py`. `leer` devuelve `None` en
cuanto algo no cuadra —un renglón con dos huecos y una sola respuesta, una
respuesta que no está en el banco, una clave que no se encuentra— y ese
ejercicio se queda exactamente como está hoy. Decirle a alguien que acertó
cuando falló es mucho peor que no ofrecerle el ejercicio.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import plan  # noqa: E402
import validar  # noqa: E402

# La cabecera del ejercicio: «### Упражнение Б. … Банк слов:». La letra es lo
# que lo ata a su bloque de la clave.
CABECERA = re.compile(r"^###\s+Упражнение\s+([А-Я])\.[^\n]*Банк слов:\s*$", re.M)

# El banco es la cita que viene justo debajo.
CITA = re.compile(r"^>\s*(.+)$", re.M)

# Un hueco: tres o más guiones bajos.
HUECO = re.compile(r"_{3,}")

# El cirílico corta la clave: las respuestas son españolas y lo que viene
# detrás en ruso es el comentario del profesor. En la lección 1-2 la clave
# acaba en «…· noches. Последняя реплика — не ошибка:…», y sin este corte esa
# última respuesta sería «noches. Последняя…», que no está en el banco y
# tiraba el ejercicio entero.
CIRILICO = re.compile(r"[А-Яа-яЁё]")

# El separador entre respuestas de un mismo hueco múltiple: « / ».
VARIAS = re.compile(r"\s+/\s+")

# La numeración de la clave («1. ») es decoración: lo que ata una respuesta a
# su hueco es el ORDEN, no el número, porque muchos ejercicios son diálogos
# sin numerar.
NUMERO = re.compile(r"^\d+\.\s*")


@dataclasses.dataclass
class Ejercicio:
    letra: str
    titulo: str
    banco: list[str]
    cuerpo: str              # el texto con sus ______, tal cual
    respuestas: list[str]    # una por hueco, en el orden en que salen


def _plano(texto: str) -> str:
    """Para comparar una respuesta con el banco: sin acentos, sin mayúsculas y
    sin el marcado de Markdown.

    Sin acentos porque la clave escribe «Aquí» con mayúscula al empezar frase y
    el banco «aquí»; y sin marcado porque una respuesta puede venir en negrita."""
    texto = re.sub(r"[*_`]", "", texto).strip().strip(".,;:!¡?¿").strip()
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _bloque_de_la_clave(cuerpo: str, letra: str) -> str | None:
    """El trozo de `## Ответы` que empieza por «**Б.**».

    Las líneas se juntan antes de mirar: en la clave una respuesta se parte a
    menudo entre dos renglones y leída línea a línea se pierde la mitad."""
    if "## Ответы" not in cuerpo:
        return None
    clave = cuerpo.split("## Ответы", 1)[1]
    # El salto de párrafo se marca ANTES de juntar las líneas. Juntándolas
    # primero, un «\n\n» se convertía en «\n » y el bloque seguía leyendo el
    # párrafo siguiente: en la lección 1-3 se llevaba por delante la tabla de
    # sonidos del Выход y salían 12 respuestas para 5 huecos.
    clave = re.sub(r"\n[ \t]*\n", "\x00", clave)
    clave = re.sub(r"\n", " ", clave)
    m = re.search(rf"\*\*{letra}\.\*\*(.+?)(?=\*\*[А-Я]\.\*\*|\x00|\Z)", clave, re.S)
    return m.group(1) if m else None


def _respuestas(bloque: str) -> list[str]:
    """Las respuestas en orden, aplanadas.

    Aplanadas a propósito: lo que ata una respuesta a su hueco es el ORDEN en
    que salen, no la numeración, porque la mitad de los ejercicios son diálogos
    sin numerar. Un «1.» delante se quita, y un « / » separa los dos huecos de
    un mismo renglón."""
    salida = []
    for trozo in bloque.split("·"):
        corte = CIRILICO.search(trozo)
        trozo = trozo[: corte.start()] if corte else trozo
        # El número ANTES del corte por punto, y el orden importa: con el
        # corte primero, un «1. aquí» se quedaba en «1», que no está en ningún
        # banco y tiraba el ejercicio entero.
        trozo = NUMERO.sub("", trozo.strip())
        # Y el comentario que sigue a la última respuesta en la MISMA frase:
        # «… · es. Carmen говорит **encantada**…». Ninguna entrada de un banco
        # lleva un punto y espacio dentro, así que cortar ahí es seguro.
        # Igual con el paréntesis explicativo: «**vuestra** (у вас…)». Ninguna
        # entrada de banco abre paréntesis.
        corta = re.search(r"\.\s|\s*\(", trozo)
        trozo = trozo[: corta.start()] if corta else trozo
        for una in VARIAS.split(trozo):
            una = una.strip().strip(".,;")
            if una:
                salida.append(una)
    return salida


def leer(cuerpo: str) -> list[Ejercicio]:
    """Los ejercicios de huecos que se pueden contestar con seguridad.

    El contrato es simple y vale para las dos formas que hay escritas —los
    renglones numerados y los diálogos—: **tantos huecos como respuestas, en
    el mismo orden, y cada respuesta dentro del banco**. Si algo de eso no
    cuadra, el ejercicio se descarta y su página se queda como está hoy.

    Esa comprobación del banco es la que de verdad protege: los bancos son
    cortos y concretos, así que una clave desalineada deja fuera alguna
    palabra casi siempre."""
    salida: list[Ejercicio] = []
    for cab in CABECERA.finditer(cuerpo):
        letra = cab.group(1)
        resto = cuerpo[cab.end():]
        fin = re.search(r"^#{2,3}\s", resto, re.M)
        seccion = resto[: fin.start()] if fin else resto

        cita = CITA.search(seccion)
        if not cita:
            continue
        banco = [p.strip() for p in cita.group(1).split("·") if p.strip()]
        if len(banco) < 2:
            continue

        # El cuerpo es lo que viene DESPUÉS del banco: el propio banco lleva
        # «·» y ningún hueco, pero contarlo sería contar la cita.
        texto = seccion[cita.end():].strip()
        cuantos = len(HUECO.findall(texto))
        if cuantos < 2:
            continue

        bloque = _bloque_de_la_clave(cuerpo, letra)
        if not bloque:
            continue
        respuestas = _respuestas(bloque)

        if len(respuestas) != cuantos:
            continue
        # La respuesta que se guarda es la ENTRADA DEL BANCO, no el texto de
        # la clave, porque la ficha que el lector pulsa lleva la del banco. La
        # clave escribe «**el cartel**» en negrita y «Aquí» con mayúscula al
        # empezar frase, así que comparando con su texto el ejercicio de la
        # 45-1 daba 0 aciertos con todo bien puesto. Comparado contra el banco,
        # negrita, mayúsculas, acentos y puntuación dejan de importar de una
        # vez, que es lo que `_plano` ya hacía para validar y no para guardar.
        del_banco = {}
        for p in banco:
            del_banco.setdefault(_plano(p), p)
        if any(_plano(r) not in del_banco for r in respuestas):
            continue
        respuestas = [del_banco[_plano(r)] for r in respuestas]

        salida.append(Ejercicio(letra=letra,
                                titulo=cab.group(0).strip().lstrip("# ").strip(),
                                banco=banco, cuerpo=texto, respuestas=respuestas))
    return salida


def de_la_leccion(ruta: pathlib.Path) -> list[Ejercicio]:
    _, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
    return leer(cuerpo)


def main(argv=None) -> int:
    cal = plan.cargar()
    con_banco = bien = huecos = 0
    fallidas = []
    for d in plan.dias(cal):
        if not d.ruta.exists():
            continue
        cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))[1]
        if "Банк слов" not in cuerpo:
            continue
        con_banco += 1
        ejercicios = leer(cuerpo)
        if ejercicios:
            bien += 1
            huecos += sum(len(e.respuestas) for e in ejercicios)
        else:
            fallidas.append(f"semana {d.semana:02d} día {d.dia}")

    print(f"{con_banco} lecciones con banco de palabras")
    print(f"{bien} se pueden contestar · {huecos} huecos interactivos")
    if fallidas:
        print(f"\nse quedan como están ({len(fallidas)}):")
        for f in fallidas[:12]:
            print("   ", f)
        if len(fallidas) > 12:
            print(f"    … y {len(fallidas) - 12} más")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
