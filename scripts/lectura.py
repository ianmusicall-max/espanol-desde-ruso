"""Presentación de vocabulario, conversaciones y ejercicios sin reescribirlos."""
from __future__ import annotations

import html
from html.parser import HTMLParser
import re


VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
EJERCICIO = re.compile(r"^(?:Упражнение\s+[А-ЯA-Z]|Tarea\s+\d+)\b")


def _texto(celda: str) -> str:
    sin_audio = re.sub(r'<button\b[^>]*>.*?</button>', '', celda, flags=re.S)
    return html.unescape(re.sub(r'<[^>]*>', '', sin_audio)).strip()


def _turno(celda: str) -> bool:
    sin_audio = re.sub(r'<button\b[^>]*>.*?</button>', '', celda, flags=re.S).strip()
    if re.match(r'^[—–]\s', _texto(sin_audio)):
        return True
    nombre = re.match(r'^<strong>([^<]{1,26}):</strong>', sin_audio)
    return bool(nombre and re.fullmatch(r'[A-ZÁÉÍÓÚÜÑ][\wÁÉÍÓÚÜÑáéíóúüñ ]{0,24}', nombre[1]))


def _tabla(m: re.Match) -> str:
    tabla = m[1]
    cabecera = re.search(r'<thead>(.*?)</thead>', tabla, re.S)
    if not cabecera:
        return m[0]
    columnas = [_texto(c) for c in re.findall(r'<th\b[^>]*>(.*?)</th>', cabecera[1], re.S)]
    clase = 'tabla-env'
    if columnas == ['Español', 'Русский', 'Пример']:
        clase += ' tabla-vocabulario'
        # CSS presenta filas como fichas. Los roles mantienen la navegación tabular.
        roles = {'table': 'table', 'thead': 'rowgroup', 'tbody': 'rowgroup', 'tr': 'row', 'th': 'columnheader', 'td': 'cell'}
        tabla = re.sub(r'<(table|thead|tbody|tr|th|td)(\s[^>]*)?>',
                       lambda t: f'<{t[1]}{t[2] or ""} role="{roles[t[1]]}">', tabla)
    elif columnas == ['Español', 'Русский', 'Español', 'Русский']:
        clase += ' tabla-glosario'
    elif columnas == ['Español', 'Русский']:
        cuerpo = re.search(r'<tbody>(.*?)</tbody>', tabla, re.S)
        turnos = 0
        for fila in re.findall(r'<tr\b[^>]*>(.*?)</tr>', cuerpo[1] if cuerpo else '', re.S):
            celdas = re.findall(r'<td\b[^>]*>(.*?)</td>', fila, re.S)
            if len(celdas) == 2 and _texto(celdas[1]) and _turno(celdas[0]):
                turnos += 1
        if turnos >= 2:
            clase += ' tabla-dialogo'
    return f'<div class="{clase}">{tabla}</div>'


class _Limites(HTMLParser):
    """Localiza límites de ejercicios que están al nivel principal de la lección."""

    def __init__(self, cuerpo: str):
        super().__init__(convert_charrefs=False)
        self.cuerpo = cuerpo
        self.lineas = [0]
        self.lineas.extend(m.end() for m in re.finditer(r'\n', cuerpo))
        self.pila = []
        self.limites = []

    def handle_starttag(self, etiqueta, atributos):
        posicion = self.lineas[self.getpos()[0] - 1] + self.getpos()[1]
        atributos = dict(atributos)
        if not self.pila:
            if etiqueta in ('h1', 'h2', 'h3'):
                fin = self.cuerpo.find(f'</{etiqueta}>', posicion)
                titulo = _texto(self.cuerpo[posicion:fin]) if fin >= 0 else ''
                es_ejercicio = etiqueta == 'h3' and bool(EJERCICIO.match(titulo))
                self.limites.append((posicion, es_ejercicio, atributos.get('id')))
            elif etiqueta == 'div' and (atributos.get('id') in ('clave', 'clave-boton', 'prueba-clave')
                                       or 'anuncio' in atributos.get('class', '').split()):
                self.limites.append((posicion, False, None))
            elif etiqueta == 'section' and 'contraste' in atributos.get('class', '').split():
                self.limites.append((posicion, False, None))
        if etiqueta not in VACIOS:
            self.pila.append(etiqueta)

    def handle_endtag(self, etiqueta):
        if etiqueta in self.pila:
            ultimo = len(self.pila) - 1 - self.pila[::-1].index(etiqueta)
            del self.pila[ultimo:]

    def handle_startendtag(self, etiqueta, atributos):
        pass


def presentar(cuerpo: str) -> str:
    cuerpo = re.sub(r'<div class="tabla-env(?: tabla-dialogo)?">(<table\b.*?</table>)</div>', _tabla, cuerpo, flags=re.S)
    estructura = _Limites(cuerpo)
    estructura.feed(cuerpo)
    limites = estructura.limites + [(len(cuerpo), False, None)]
    for indice in range(len(limites) - 2, -1, -1):
        inicio, ejercicio, identificador = limites[indice]
        if not ejercicio:
            continue
        fin = limites[indice + 1][0]
        etiqueta = f' aria-labelledby="{html.escape(identificador)}"' if identificador else ''
        cuerpo = (cuerpo[:inicio] + f'<section class="ejercicio-bloque"{etiqueta}>'
                  + cuerpo[inicio:fin] + '</section>' + cuerpo[fin:])
    return cuerpo
