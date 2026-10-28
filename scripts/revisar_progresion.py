#!/usr/bin/env python3
"""Formas verbales usadas antes de la leccion que las ensena.

El curso introduce los tiempos en un orden que vive en `calendario.yaml`, y de
ahi los lee este guion: la semana de cada tiempo es la del primer dia cuyo
`tema_es` lo nombra. Escritas aqui a mano se quedarian viejas el dia que el
profesor mueva una unidad, y el sintoma seria un informe que acusa a lecciones
correctas.

Un texto modelo que usa una forma antes de su leccion ensena lo contrario de
lo que dice, y nada se pone en rojo: `validar.py` comprueba la FORMA de la
leccion y no su gramatica. Este guion es ese barrido, y SOLO LEE.

No toda aparicion temprana es un defecto, y por eso el informe las separa:

  lexico      la forma tiene su propia entrada en el vocabulario de esa
              leccion O DE UNA ANTERIOR, o sea que se ensena como PALABRA y no
              como tiempo. Es la convencion del curso para las cinco formulas
              de cortesia (*me gustaría*, *podría*, *quería*…), declarada en la
              unidad 15. Mirando solo la leccion misma, el informe acusaba a
              cada reaparicion de una palabra ya ensenada: `quería` sale en
              S17D4 con su entrada y vuelve cuatro veces despues, y las cuatro
              salian como defecto.
  declarada   la leccion nombra la unidad donde se ensena de verdad, o dice
              que la forma se aprende entera («Откуда эта форма — в 13-й
              единице; пока просто берите», S17D4).
  distractor  la forma esta marcada con ✗ o en «Вы захотите сказать»: esta
              ahi justamente por incorrecta.
  sin declarar  lo que hay que mirar.

Las listas de formas son explicitas y no un patron de terminaciones, porque
las terminaciones mienten: *panadería* casa con el condicional, *vino* con el
indefinido y *queremos* con el futuro.

    .venv/bin/python scripts/revisar_progresion.py          # el resumen
    .venv/bin/python scripts/revisar_progresion.py --todo   # cada aparicion
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exportar_anki
import plan
import revisar_lexico
import validar

# El dia que ensena cada tiempo se busca por su tema en el calendario.
TEMAS = {
    "perfecto": r"pretérito perfecto",
    "indefinido": r"\bindefinido\b",
    "imperfecto": r"\bimperfecto\b",
    "futuro": r"futuro simple",
    "condicional": r"\bcondicional\b",
}

# El pluscuamperfecto NO lo ensena ninguna leccion: es B1. Asi que su semana no
# sale del calendario -no esta- y toda aparicion es temprana. Se mira igual que
# los demas, de modo que un «pluscuamperfecto» declarado (S28D5 lo nombra en su
# clave) sigue contando como declarado.
NUNCA = 10 ** 9

# El condicional entra DOS veces y por eso son dos tiempos y no uno: la unidad
# 15 ensena cinco formulas de cortesia como vocabulario y la 20 el paradigma.
# Contadas juntas, el informe acusaria de «temprana» cada `me gustaría` de las
# semanas 29 a 38, que son material enseñado.
CORTESIA = re.compile(r"\b(gustaría|podría|preferiría|querría|agradecería)\b", re.I)
TEMA_CORTESIA = r"condicional de cortesía"

FORMAS = {
    "perfecto": r"\b(he|has|ha|hemos|habéis|han)\s+(?:[a-záéíóúñ]+\s+)?"
    r"(hablado|comido|vivido|hecho|dicho|visto|escrito|puesto|vuelto|abierto|"
    r"roto|muerto|ido|sido|estado|tenido|podido|querido|sabido|llegado|salido|"
    r"terminado|quedado|empezado|cambiado|pasado|perdido|leído|oído|traído)\b",
    "indefinido": r"\b(hablé|habló|hablaron|comió|comieron|vivió|vivieron|fui|fue|"
    r"fuimos|fueron|tuve|tuvo|tuvieron|estuve|estuvo|estuvieron|hice|hizo|"
    r"hicieron|pude|pudo|puse|puso|quise|quiso|vine|vinieron|dije|dijo|dijeron|"
    r"leyó|oyó|durmió|pidió|trajo|empecé|empezó|llegué|llegó|llegaron|salí|"
    r"salió|volví|volvió|compré|compró|nació|murió|escribió|abrió)\b",
    "imperfecto": r"\b(hablaba|hablaban|comía|comían|vivía|vivían|era|eran|éramos|"
    r"iba|iban|íbamos|veía|veían|tenía|tenían|teníamos|estaba|estaban|había|"
    r"habían|hacía|hacían|quería|querían|podía|podían|sabía|sabían|dormía|"
    r"solía)\b",
    "condicional": r"\b(sería|serían|estaría|estarían|tendría|tendrían|habría|haría|"
    r"harían|podría|podrían|saldría|pondría|vendría|diría|querría|sabría|"
    r"valdría|gustaría|encantaría|preferiría|iría|irían|compraría|hablaría|"
    r"comería|viviría|daría|pagaría|llevaría|dejaría|cambiaría|recomendaría|"
    r"diríamos|deberías|debería|podrías|gustaríamos)\b",
    # habia + participio. La lista de participios es explicita a proposito: con
    # «\w+ado» el existencial se cuela —`no había supermercado`, `había nada
    # roto`— y el informe acusaria a la leccion que de verdad ensena `había`.
    "pluscuamperfecto": r"\b(hab[ií]a|hab[ií]as|hab[ií]amos|hab[ií]ais|hab[ií]an)\s+"
    r"(?:(?:ya|no|todav[ií]a|nunca|casi|siempre)\s+)?(hablado|comido|vivido|hecho|dicho|visto|escrito|puesto|vuelto|abierto|roto|muerto|ido|sido|estado|tenido|podido|querido|sabido|llegado|salido|terminado|quedado|empezado|cambiado|pasado|perdido|leído|oído|traído|olvidado|cerrado|firmado|decidido|estudiado|traducido|venido|dado|puesto|entendido|aprendido|trabajado|comprado|encontrado)\b",
    "futuro": r"\b(seré|será|serán|seremos|estaré|estará|estarás|estarán|tendré|"
    r"tendrá|tendrán|habrá|habrán|haré|hará|harán|podré|podrá|podrán|saldré|"
    r"saldrá|pondré|pondrá|vendré|vendrá|vendrán|diré|dirá|querré|sabré|sabrá|"
    r"valdrá|hablaré|hablará|comeré|comerá|viviré|vivirá|iré|irá|irán|iremos|"
    r"llegaré|llegará|empezaré|empezará|afectará|cerrará|dejarán|decidirá|"
    r"funcionará|gustará|pasará|volveré|volverá|veré|verá|daré|dará|llamaré|"
    r"llamará)\b",
}

# Como el curso declara una forma que llega mas tarde. Se mira en la leccion
# entera -S17D4 declara `quería` una vez y la usa quince- y sobre el texto con
# los espacios juntados y SIN las comillas de bloque, porque el renglon parte
# las frases: en S10D7 el aviso dice «будет через несколько\n> месяцев» y con
# el salto y el `>` en medio no casa ningun patron.
DECLARA = (
    re.compile(r"через несколько (?:единиц|месяцев|недель)"),
    re.compile(r"на следующей неделе придёт"),
    re.compile(r"которой вы ещё"),
    re.compile(r"Это не ошибка"),
    re.compile(r"учат целиком"),
    re.compile(r"пока просто"),
    # Nombrar el tiempo es declararlo: S28D5 lo hace en su clave.
    re.compile(r"pluscuamperfecto", re.I),
)

# Una referencia a una unidad SI declara la forma -«(это единица 12)», «придёт
# в единице 13», «в этом курсе его нет, он идёт на уровне B1»- pero la
# declaracion vale para LA FORMA QUE NOMBRA, no para la leccion entera: un
# domingo cualquiera nombra un numero de unidad por su tarea final o por lo que
# viene la semana que entra, y mirado asi tapaba doce lecciones con defectos de
# verdad. Asi que se buscan los PARRAFOS que declaran y se mira si el parrafo
# nombra esta forma; con una ventana de renglones no alcanzaba, porque el aviso
# del 2026-10-28 va al final del apartado y las formas estan en el texto.
UNIDAD = re.compile(
    r"\d+-(?:й|я|е|ой|м|го)\s+единиц|единиц\w*\s+\d+|уровне B1|pluscuamperfecto",
    re.I,
)

# Un renglon donde la forma esta por incorrecta: marcada con ✗, en la lista de
# «Вы захотите сказать», o entre las opciones de un test —ahi una forma que el
# alumno no conoce es justamente un distractor, y no lleva ✗ porque la clave
# dice aparte cual era la buena—.
DISTRACTOR = ("✗", "Вы захотите сказать")
OPCIONES = re.compile(r"(?:^|[·→|]\s*)[абвгд]\)")

SIN_DECLARAR = "sin declarar"
ESTADOS = ("lexico", "declarada", "distractor", SIN_DECLARAR)


def semanas(cal) -> dict[str, int]:
    """La semana que ensena cada tiempo, leida del calendario."""
    fuera = {}
    for tiempo, patron in TEMAS.items():
        for d in plan.dias(cal):
            if d.tema_es and re.search(patron, d.tema_es, re.I):
                fuera[tiempo] = d.semana
                break
    for u in cal["unidades"]:
        if any(re.search(TEMA_CORTESIA, g, re.I) for g in u["gramatica"]):
            fuera["cortesía"] = min(u["semanas"])
            break
    fuera["pluscuamperfecto"] = NUNCA
    return fuera


def renglon(cuerpo: str, pos: int) -> str:
    ini = cuerpo.rfind("\n", 0, pos) + 1
    fin = cuerpo.find("\n", pos)
    return cuerpo[ini : fin if fin > 0 else None].strip()


def _entradas(ruta: Path) -> str:
    """El vocabulario de un dia, normalizado y en una sola cadena."""
    try:
        _, filas = exportar_anki.filas_de(ruta)
    except Exception:
        return ""
    return " | ".join(revisar_lexico.normalizar(f[0]) for f in filas if f)


def _formas_declaradas(cuerpo: str) -> str:
    """Los parrafos de la leccion que declaran algo, en una sola cadena.

    Un parrafo declara si nombra la unidad donde se ensena la forma o dice que
    no esta en el curso. Lo que vale es lo que ESE parrafo nombra: asi el aviso
    del final del apartado declara sus formas y no las demas."""
    parrafos = [p for p in re.split(r"\n\s*\n", cuerpo) if UNIDAD.search(p)]
    return " ".join(parrafos).lower()


def hallazgos(cal=None):
    """Cada aparicion temprana, como (dia, tiempo, forma, estado, renglon)."""
    cal = cal or plan.cargar()
    desde = semanas(cal)
    fuera = []
    # El vocabulario se acumula: una palabra ensenada el lunes sigue ensenada
    # el martes. Los dias se recorren en orden, que es el de `plan.dias`.
    vocabulario = ""
    for d in plan.dias(cal):
        if not d.ruta.exists():
            continue
        cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))[1]
        # El markdown parte palabras con las negritas: **fue**ra casa con `fue`.
        cuerpo = cuerpo.replace("*", "")
        seguido = re.sub(r"\s+", " ", re.sub(r"^\s*>\s?", "", cuerpo, flags=re.M))
        esta_declarado = any(p.search(seguido) for p in DECLARA)
        vocabulario += " | " + _entradas(d.ruta)
        declarado_en = _formas_declaradas(cuerpo)
        for tiempo, patron in FORMAS.items():
            if tiempo not in desde or d.semana >= desde[tiempo]:
                continue
            for m in re.finditer(patron, cuerpo, re.I):
                forma = m.group(0)
                # Las tablas de fonetica parten las palabras en silabas, y
                # `fue-ra` casa con `fue` porque el guion es frontera.
                if cuerpo[m.start() - 1 : m.start()] == "-" or cuerpo[m.end() : m.end() + 1] == "-":
                    continue
                if tiempo == "condicional" and CORTESIA.fullmatch(forma):
                    # Es una de las cinco formulas: su semana es otra.
                    if d.semana >= desde.get("cortesía", 10 ** 9):
                        continue
                    tiempo = "cortesía"
                linea = renglon(cuerpo, m.start())
                plana = revisar_lexico.normalizar(forma)
                if any(marca in linea for marca in DISTRACTOR) or OPCIONES.search(linea):
                    estado = "distractor"
                elif plana and re.search(rf"\b{re.escape(plana)}\b", vocabulario):
                    estado = "lexico"
                elif forma.lower() in declarado_en:
                    estado = "declarada"
                elif esta_declarado:
                    estado = "declarada"
                else:
                    estado = SIN_DECLARAR
                fuera.append((d, tiempo, forma, estado, linea))
    return fuera


def main() -> int:
    todo = "--todo" in sys.argv
    cal = plan.cargar()
    desde = semanas(cal)
    hs = hallazgos(cal)
    sin = [h for h in hs if h[3] == SIN_DECLARAR]

    print("Cada tiempo se ensena en la semana que dice el calendario:")
    for tiempo, s in sorted(desde.items(), key=lambda kv: kv[1]):
        print(f"  {tiempo:12} semana {s}")

    print(f"\nFormas usadas antes de esa semana: {len(hs)}")
    for estado in ESTADOS:
        print(f"  {estado:12} {sum(1 for h in hs if h[3] == estado)}")

    print("\n== Sin declarar, por tiempo")
    for tiempo in sorted(desde, key=lambda t: desde[t]):
        de_ese = [h for h in sin if h[1] == tiempo]
        if not de_ese:
            continue
        dias = sorted({h[0].etiqueta for h in de_ese}, key=lambda e: (len(e), e))
        print(f"  {tiempo:12} {len(de_ese):3} en {len(dias)} lecciones: {', '.join(dias)}")

    if todo:
        print("\n== Cada aparicion sin declarar")
        for d, tiempo, forma, _, linea in sin:
            print(f"  {d.etiqueta} {tiempo:12} [{forma}] {linea[:88]}")
    else:
        print("\n== Las lecciones con mas (--todo las lista todas)")
        for et, n in collections.Counter(h[0].etiqueta for h in sin).most_common(12):
            formas = sorted({h[2].lower() for h in sin if h[0].etiqueta == et})
            print(f"  {et}  {n:3}  {', '.join(formas[:6])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
