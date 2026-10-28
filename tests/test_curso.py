"""Pruebas del curso: el calendario, las lecciones y los scripts cuentan lo mismo.

    .venv/bin/python -m unittest tests.test_curso
"""
from __future__ import annotations

import copy
import dataclasses
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from collections import Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import yaml  # noqa: E402

import construir_sitio  # noqa: E402
import generar_audio  # noqa: E402
import generar_imagenes  # noqa: E402
import huecos  # noqa: E402
import exportar_apkg  # noqa: E402
import poner_dominio  # noqa: E402
import revisar_adsense  # noqa: E402
import tarjeta_social  # noqa: E402
import exportar_wordpress  # noqa: E402
import escribir_leccion  # noqa: E402
import exportar_anki  # noqa: E402
import plan  # noqa: E402
import pruebas  # noqa: E402
import validar  # noqa: E402

CAL = plan.cargar()
DIAS = plan.dias(CAL)


class TestElCalendarioEsUnAnoEntero(unittest.TestCase):
    def test_hay_365_dias_sin_repetir(self):
        self.assertEqual(len(DIAS), 365)
        self.assertEqual(len({(d.semana, d.dia) for d in DIAS}), 365)
        self.assertEqual([d.numero for d in DIAS], list(range(1, 366)))

    def test_las_52_semanas_tienen_7_dias_y_el_365_es_de_reserva(self):
        por_semana = Counter(d.semana for d in DIAS)
        for s in range(1, 53):
            self.assertEqual(por_semana[s], 7, f"semana {s}")
        self.assertEqual(DIAS[-1].tipo, "reserva")

    def test_cada_unidad_cubre_sus_dos_semanas_enteras(self):
        for u in CAL["unidades"]:
            a, b = u["semanas"]
            self.assertEqual(b - a, 1, f"unidad {u['numero']} no dura dos semanas")
            self.assertEqual(sorted((f[0], f[1]) for f in u["dias"]), [(s, d) for s in (a, b) for d in range(1, 8)])
        self.assertEqual([u["numero"] for u in CAL["unidades"]], list(range(1, 25)))

    def test_la_semana_tipo_se_respeta_en_las_unidades_de_contenido(self):
        for u in CAL["unidades"]:
            if u["numero"] in (11, 24):
                continue  # las de repaso tienen su propia forma
            a, b = u["semanas"]
            for d in DIAS:
                if d.semana not in (a, b):
                    continue
                if d.dia <= 5:
                    self.assertEqual(d.tipo, "leccion", f"{d.etiqueta}")
                elif d.dia == 7:
                    self.assertEqual(d.tipo, "cultura", f"{d.etiqueta}")
                else:
                    self.assertEqual(d.tipo, "repaso" if d.semana == a else "prueba", f"{d.etiqueta}")

    def test_los_tipos_son_los_conocidos_y_todo_dia_tiene_foco_y_salida(self):
        for d in DIAS:
            self.assertIn(d.tipo, plan.TIPOS, d.etiqueta)
            self.assertTrue(d.foco.strip(), d.etiqueta)
            self.assertTrue(d.salida.strip(), d.etiqueta)
            self.assertTrue(d.tema_es.strip() and d.tema_ru.strip(), d.etiqueta)

    def test_ningun_tema_se_repite(self):
        repetidos = [t for t, n in Counter(d.tema_es for d in DIAS).items() if n > 1]
        self.assertEqual(repetidos, [])

    def test_las_fases_suman_el_ano_y_las_horas(self):
        fases = CAL["meta"]["fases"]
        self.assertEqual(fases[0]["semanas"][0], 1)
        for f1, f2 in zip(fases, fases[1:]):
            self.assertEqual(f1["semanas"][1] + 1, f2["semanas"][0])
        self.assertEqual(fases[-1]["semanas"][1], 52)
        self.assertEqual(len(DIAS) * CAL["meta"]["minutos_por_dia"] / 60, CAL["meta"]["horas_totales"])
        self.assertEqual({d.nivel for d in DIAS if d.unidad and d.unidad <= 11}, {"A1"})
        self.assertEqual({d.nivel for d in DIAS if d.unidad and d.unidad >= 12}, {"A2"})

    def test_la_fase_de_cada_semana_coincide_con_el_nivel_de_su_unidad(self):
        for d in DIAS:
            if d.unidad:
                self.assertEqual(plan.fase_de(CAL, d.semana), d.nivel, d.etiqueta)
            else:
                self.assertEqual(plan.fase_de(CAL, d.semana), "Final", d.etiqueta)

    def test_hay_lecciones_nuevas_de_sobra_para_el_vocabulario_objetivo(self):
        minimo, maximo = CAL["meta"]["palabras_nuevas_por_leccion"]
        lecciones = sum(1 for d in DIAS if d.tipo == "leccion")
        self.assertGreaterEqual(lecciones * maximo, CAL["meta"]["vocabulario_objetivo"]["A2"])
        self.assertGreaterEqual(lecciones * minimo, CAL["meta"]["vocabulario_objetivo"]["A1"])


class TestElPlanAnualEstaAlDia(unittest.TestCase):
    def test_la_tabla_de_plan_anual_coincide_con_el_yaml(self):
        self.assertTrue(plan.plan_anual_al_dia(CAL), "corre scripts/plan.py --actualizar")

    def test_la_tabla_lista_las_24_unidades_y_la_fase_final(self):
        filas = [l for l in plan.tabla_unidades(CAL).splitlines() if l.startswith("| ") and not l.startswith("| Unidad")]
        self.assertEqual(len(filas), 25)


class TestLasLeccionesEscritas(unittest.TestCase):
    def test_las_semanas_1_y_2_estan_completas(self):
        for s in (1, 2):
            for n in range(1, 8):
                self.assertTrue((plan.CURSO / f"semana-{s:02d}" / f"dia-{n}.md").exists(), f"semana {s} día {n}")

    def test_toda_leccion_existente_pasa_el_validador(self):
        for ruta in validar.lecciones():
            with self.subTest(leccion=str(ruta.relative_to(RAIZ))):
                self.assertEqual(validar.problemas(ruta, CAL), [])

    def test_las_lecciones_de_la_unidad_1_estan_revisadas(self):
        for ruta in validar.lecciones():
            datos, _ = validar.frontmatter(ruta.read_text(encoding="utf-8"))
            if datos.get("unidad") == 1:
                self.assertTrue(datos["revisado"], str(ruta))

    def test_la_plantilla_tiene_las_franjas_de_una_leccion_de_30_minutos(self):
        _, cuerpo = validar.frontmatter((RAIZ / "curso" / "plantilla-leccion.md").read_text(encoding="utf-8"))
        tramos = validar.franjas(cuerpo)
        self.assertEqual(validar.problemas_de_franjas(tramos, 30), [])
        self.assertEqual(validar.problemas_de_apartados("leccion", tramos), [])
        self.assertIn(validar.CONTRASTE, cuerpo)


class TestElValidadorSePoneEnRojoCuandoToca(unittest.TestCase):
    def _escribir(self, texto: str) -> pathlib.Path:
        carpeta = pathlib.Path(tempfile.mkdtemp()) / "curso" / "semana-01"
        carpeta.mkdir(parents=True)
        ruta = carpeta / "dia-1.md"
        ruta.write_text(texto, encoding="utf-8")
        return ruta

    def test_una_leccion_de_45_minutos_no_pasa(self):
        texto = (plan.CURSO / "semana-01" / "dia-1.md").read_text(encoding="utf-8").replace("(29–30 мин)", "(29–45 мин)")
        errores = validar.problemas(self._escribir(texto), CAL)
        self.assertTrue(any("termina en 45" in e for e in errores), errores)

    def test_un_tema_que_no_es_el_del_calendario_no_pasa(self):
        texto = (plan.CURSO / "semana-01" / "dia-1.md").read_text(encoding="utf-8").replace('tema_es: "El alfabeto y las cinco vocales"', 'tema_es: "Otro tema"')
        errores = validar.problemas(self._escribir(texto), CAL)
        self.assertTrue(any("no coincide con el calendario" in e for e in errores), errores)

    def test_una_leccion_sin_contraste_con_el_ruso_no_pasa(self):
        texto = (plan.CURSO / "semana-01" / "dia-1.md").read_text(encoding="utf-8").replace(validar.CONTRASTE, "### Nota")
        errores = validar.problemas(self._escribir(texto), CAL)
        self.assertTrue(any("Контраст" in e for e in errores), errores)

    def test_una_leccion_con_hueco_entre_apartados_no_pasa(self):
        texto = (plan.CURSO / "semana-01" / "dia-1.md").read_text(encoding="utf-8").replace("(3–6 мин)", "(4–6 мин)")
        errores = validar.problemas(self._escribir(texto), CAL)
        self.assertTrue(any("hueco" in e for e in errores), errores)

    def test_el_archivo_tiene_que_estar_donde_dice_su_frontmatter(self):
        texto = (plan.CURSO / "semana-01" / "dia-2.md").read_text(encoding="utf-8")
        errores = validar.problemas(self._escribir(texto), CAL)  # se guarda como dia-1.md
        self.assertTrue(any("frontmatter dice" in e for e in errores), errores)


class TestElVocabulario(unittest.TestCase):
    def test_cada_leccion_nueva_tiene_entre_6_y_10_palabras(self):
        minimo, maximo = CAL["meta"]["palabras_nuevas_por_leccion"]
        for ruta in validar.lecciones():
            datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
            if datos["tipo"] == "leccion":
                n = len(validar.filas_de_vocabulario(cuerpo))
                self.assertTrue(minimo <= n <= maximo, f"{ruta}: {n}")

    def test_los_tsv_de_anki_estan_al_dia(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        exportar_anki.exportar(destino)
        for generado in sorted(destino.glob("*.tsv")):
            versionado = RAIZ / "vocabulario" / generado.name
            self.assertTrue(versionado.exists(), f"falta vocabulario/{generado.name}: corre scripts/exportar_anki.py")
            self.assertEqual(versionado.read_text(encoding="utf-8"), generado.read_text(encoding="utf-8"), f"vocabulario/{generado.name} desactualizado")

    def test_ninguna_palabra_genera_dos_tarjetas(self):
        """Once entradas se enseñan dos veces (lo lista revisar_lexico.py). Eso
        lo decide el profesor; lo que el mazo no puede tener es la misma palabra
        dos veces."""
        import revisar_lexico
        claves = [revisar_lexico.normalizar(l.split("\t")[0])
                  for l in (RAIZ / "vocabulario" / "todo.tsv").read_text(encoding="utf-8").splitlines()[1:]]
        repetidas = {k for k in claves if claves.count(k) > 1}
        self.assertEqual(repetidas, set())

    def test_el_informe_de_lexico_ve_las_dos_tablas(self):
        """Hay DOS tablas de vocabulario y los 50 domingos usan la otra.

        `validar.filas_de_vocabulario` solo lee «Словарь дня»; los días de
        cultura usan «3. Слова», con dos pares de columnas por fila.
        `exportar_anki` leía las dos y `revisar_lexico` solo la primera, así
        que el informe de repeticiones no veía unas mil entradas y pasaba de
        135 repetidas a 13 sin que nada fallara —y el docstring de
        `exportar_anki.exportar` prometía justamente que las lista—. Quien
        decide qué tabla tiene un día es `exportar_anki.filas_de`, una sola
        vez, y este test exige que el informe pase por ahí."""
        import revisar_lexico
        ix = revisar_lexico.lexico()
        domingos = [d for d in plan.dias(CAL)
                    if d.tipo == "cultura" and d.ruta.exists()]
        self.assertGreaterEqual(len(domingos), 30)
        for d in domingos[:5] + domingos[-5:]:
            datos, filas = exportar_anki.filas_de(d.ruta)
            self.assertTrue(filas, f"{d.ruta}: sin filas de vocabulario")
            for fila in filas:
                clave = revisar_lexico.normalizar(fila[0])
                if not clave:
                    continue
                self.assertIn(clave, ix,
                              f"{d.ruta}: «{fila[0]}» no llega al informe de léxico")

    def test_las_tarjetas_no_llevan_negritas_ni_estan_vacias(self):
        for linea in (RAIZ / "vocabulario" / "todo.tsv").read_text(encoding="utf-8").splitlines()[1:]:
            es, ru, _, etiquetas = linea.split("\t")
            self.assertNotIn("**", es)
            self.assertTrue(es and ru and etiquetas.startswith("S"))


class TestElGeneradorCuidaLaCache(unittest.TestCase):
    """El prompt va en tres bloques: estable, unidad, día. Lo volátil va último."""

    def test_el_dia_no_esta_en_los_bloques_cacheados(self):
        d = plan.dia(CAL, 3, 2)
        sistema, usuario = escribir_leccion.armar_prompt(CAL, d)
        self.assertIn(d.tema_es, usuario)
        self.assertIn(d.salida, usuario)
        self.assertNotIn(d.salida, sistema[0]["text"])
        self.assertNotIn("EL DÍA QUE HAY QUE ESCRIBIR", sistema[0]["text"] + sistema[1]["text"])

    def test_el_bloque_estable_es_identico_para_dos_dias_de_unidades_distintas(self):
        a, _ = escribir_leccion.armar_prompt(CAL, plan.dia(CAL, 3, 1))
        b, _ = escribir_leccion.armar_prompt(CAL, plan.dia(CAL, 30, 4))
        self.assertEqual(a[0]["text"], b[0]["text"])
        self.assertEqual(a[0]["cache_control"], {"type": "ephemeral"})
        self.assertEqual(a[1]["cache_control"], {"type": "ephemeral"})

    def test_el_bloque_de_la_unidad_es_identico_para_dos_dias_de_la_misma_unidad(self):
        a, _ = escribir_leccion.armar_prompt(CAL, plan.dia(CAL, 5, 1))
        b, _ = escribir_leccion.armar_prompt(CAL, plan.dia(CAL, 6, 4))
        self.assertEqual(a[1]["text"], b[1]["text"])
        self.assertIn("La familia y las personas", a[1]["text"])

    def test_un_tipo_sin_modelo_en_su_unidad_toma_el_de_la_unidad_1(self):
        """Sin un modelo propio de ese tipo, el prompt presta el de la unidad 1.

        Hasta el 2026-10-28 esto se comprobaba buscando la primera unidad
        **sin ninguna lección escrita**, y con las 24 escritas eso dejó de
        existir: la prueba se caía con un StopIteration en vez de comprobar
        nada. El caso sigue existiendo por otro lado, y es estable porque es
        una propiedad del calendario: **la unidad 24 es de repaso y no tiene
        ni un día de tipo `leccion`**, así que un día de ese tipo en su semana
        tiene que prestar el modelo de la unidad 1."""
        # Se llama a `bloque_unidad`, que es exactamente lo que `armar_prompt`
        # pone en `sistema[1]`, y no a `armar_prompt`: ése arma además el
        # mensaje del día, que busca el día en la lista del calendario y con
        # un día inventado se cae.
        d = dataclasses.replace(plan.dia(CAL, 47, 1), tipo="leccion")
        self.assertIn("curso/semana-01/dia-1.md", escribir_leccion.bloque_unidad(CAL, d))
        # Y la otra mitad: lo que sí tiene modelo propio no presta nada.
        propio, _ = escribir_leccion.armar_prompt(CAL, plan.dia(CAL, 47, 1))
        self.assertNotIn("curso/semana-01/dia-1.md", propio[1]["text"])

    def test_el_dia_que_se_reescribe_sigue_en_el_bloque_cacheado(self):
        """Excluirlo haría que el bloque cambiara de un día a otro de la misma
        unidad, que es justo lo que la caché no puede permitirse."""
        d = plan.dia(CAL, 1, 1)
        sistema, _ = escribir_leccion.armar_prompt(CAL, d)
        self.assertIn("curso/semana-01/dia-1.md", sistema[1]["text"])

    def test_lo_guardado_lleva_revisado_false_aunque_el_modelo_diga_otra_cosa(self):
        texto = (plan.CURSO / "semana-01" / "dia-1.md").read_text(encoding="utf-8")
        limpio = escribir_leccion.limpiar("```markdown\n" + texto + "\n```")
        datos, cuerpo = validar.frontmatter(limpio)
        self.assertIs(datos["revisado"], False)
        self.assertIn("## 1. Разминка (0–3 мин)", cuerpo)
        with self.assertRaises(ValueError):
            escribir_leccion.limpiar("Aquí va la lección:\n---\n")

    def test_la_etapa_del_ruso_se_retira_con_las_unidades(self):
        self.assertIn("по-русски", escribir_leccion.etapa_del_ruso(1))
        self.assertIn("Единицы 19-24", escribir_leccion.etapa_del_ruso(22))
        self.assertIn("Единицы 19-24", escribir_leccion.etapa_del_ruso(None))

    def test_el_modelo_y_el_esfuerzo_son_los_previstos(self):
        self.assertEqual(escribir_leccion.MODELO, "claude-opus-5-5")
        self.assertIn(escribir_leccion.ESFUERZO, ("medium", "high", "xhigh"))
        self.assertIn(escribir_leccion.MODELO, escribir_leccion.PRECIOS)


class TestElSitio(unittest.TestCase):
    """El sitio público: tres idiomas, el diseño y las páginas que pide AdSense."""

    def setUp(self):
        self.cfg = construir_sitio.cargar_config()
        self.textos = construir_sitio.cargar_textos()
        self.idiomas = [i["codigo"] for i in self.textos["idiomas"]]

    def _construir(self, cfg=None):
        """Construye en una carpeta temporal, con el MISMO índice de audio.

        Sin copiarlo, `indice_de_audio` no encuentra nada en la carpeta nueva y
        el sitio sale sin un solo ▶, así que `test_docs_esta_al_dia` compararía
        un sitio con audio contra uno sin audio y acusaría a `docs/` de estar
        desactualizado. Se copia solo el índice y no los 3.543 MP3: los botones
        dependen de él, no de que los archivos estén."""
        destino = pathlib.Path(tempfile.mkdtemp())
        # Lo mismo para los dibujos del vocabulario, y por lo mismo: se copia
        # solo el índice y no las 300 imágenes, porque los <img> dependen de él
        # y no de que los archivos estén.
        # El manifiesto de la baraja va con ellos y NO el .apkg de 22 MB: para
        # eso existe el manifiesto. El .apkg se finge con un archivo vacío,
        # porque el bloque solo mira que esté.
        apkg = RAIZ / "docs" / "vocabulario" / "espanol-desde-ruso.apkg"
        if apkg.exists():
            (destino / "vocabulario").mkdir(parents=True, exist_ok=True)
            (destino / "vocabulario" / apkg.name).touch()
        for carpeta, nombre in (("audio", construir_sitio.INDICE_AUDIO),
                                ("img", construir_sitio.INDICE_IMG),
                                ("vocabulario", construir_sitio.MANIFIESTO_BARAJA)):
            indice = RAIZ / "docs" / carpeta / nombre
            if indice.exists():
                (destino / carpeta).mkdir(parents=True, exist_ok=True)
                shutil.copy2(indice, destino / carpeta / nombre)
        construir_sitio.construir(destino, cfg or self.cfg, self.textos)
        return destino

    def test_los_tres_idiomas_tienen_sus_cinco_paginas(self):
        destino = self._construir()
        for i in self.textos["idiomas"]:
            carpeta = destino / i["carpeta"] if i["carpeta"] else destino
            for nombre in ("index.html", "kurs.html", "o-kurse.html", "kontakt.html", "privacy.html"):
                ruta = carpeta / nombre
                self.assertTrue(ruta.exists(), f"{i['codigo']}/{nombre}")
                self.assertIn(f'<html lang="{i["html"]}"', ruta.read_text(encoding="utf-8"))

    def test_cada_pagina_ofrece_la_misma_pagina_en_los_otros_idiomas(self):
        """El conmutador no manda a la portada: manda a la MISMA página."""
        destino = self._construir()
        pagina = (destino / "es" / "kurs.html").read_text(encoding="utf-8")
        self.assertIn('href="../kurs.html" hreflang="ru"', pagina)
        self.assertIn('href="../en/kurs.html" hreflang="en"', pagina)
        self.assertIn('href="../es/kurs.html" hreflang="es"', pagina)
        self.assertIn('aria-current="true"', pagina)
        raiz = (destino / "privacy.html").read_text(encoding="utf-8")
        self.assertIn('href="./es/privacy.html"', raiz)

    def test_hay_hreflang_para_los_buscadores(self):
        destino = self._construir()
        portada = (destino / "index.html").read_text(encoding="utf-8")
        for i in self.textos["idiomas"]:
            self.assertIn(f'rel="alternate" hreflang="{i["html"]}"', portada)

    def test_las_lecciones_existen_solo_en_ruso(self):
        """No es un olvido: el curso enseña español A TRAVÉS del ruso, así que
        una lección en español no tendría sentido."""
        destino = self._construir()
        for i in self.textos["idiomas"]:
            if not i["carpeta"]:
                continue
            self.assertFalse((destino / i["carpeta"] / "semana-01").exists(), i["codigo"])
        leccion = destino / "semana-01" / "dia-1.html"
        self.assertTrue(leccion.exists())
        self.assertIn('<html lang="ru"', leccion.read_text(encoding="utf-8"))

    def test_el_indice_de_cada_idioma_enlaza_todas_las_lecciones_escritas(self):
        destino = self._construir()
        for i in self.textos["idiomas"]:
            carpeta = destino / i["carpeta"] if i["carpeta"] else destino
            raiz = ".." if i["carpeta"] else "."
            indice = (carpeta / "kurs.html").read_text(encoding="utf-8")
            for ruta in validar.lecciones():
                datos, _ = validar.frontmatter(ruta.read_text(encoding="utf-8"))
                enlace = f'{raiz}/semana-{int(datos["semana"]):02d}/dia-{datos["dia"]}.html'
                self.assertIn(enlace, indice, f"{i['codigo']} → {enlace}")

    def test_la_portada_dice_cuantas_lecciones_hay_de_verdad(self):
        destino = self._construir()
        n = len(validar.lecciones())
        for i in self.textos["idiomas"]:
            carpeta = destino / i["carpeta"] if i["carpeta"] else destino
            portada = (carpeta / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'<span class="n">{n}</span>', portada)
            self.assertIn(f"/ {len(DIAS)} ", portada)

    def test_cada_leccion_enlaza_con_la_anterior_y_la_siguiente(self):
        destino = self._construir()
        pagina = (destino / "semana-01" / "dia-2.html").read_text(encoding="utf-8")
        self.assertIn("dia-1.html", pagina)
        self.assertIn("dia-3.html", pagina)
        self.assertIn("Урок 2", pagina)

    def test_el_contraste_con_el_ruso_se_marca_para_poder_destacarlo(self):
        """Es la firma del curso, así que en la lección se ve distinto."""
        destino = self._construir()
        pagina = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn('<section class="contraste">', pagina)
        self.assertIn("Контраст с русским", pagina)

    def test_las_tablas_van_en_su_propia_caja_con_scroll(self):
        """Una tabla de diálogo no cabe en un móvil; si no se encierra, empuja
        la página entera y el texto se sale."""
        destino = self._construir()
        pagina = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertEqual(pagina.count("<table>"), pagina.count('<div class="tabla-env">'))

    def test_el_boton_de_dia_y_noche_esta_en_todas_las_paginas(self):
        destino = self._construir()
        paginas = ["index.html", "kurs.html", "privacy.html", "es/index.html",
                   "en/kurs.html", "semana-01/dia-1.html"]
        for nombre in paginas:
            pagina = (destino / nombre).read_text(encoding="utf-8")
            self.assertIn('id="tema"', pagina, nombre)
            self.assertIn('class="luna"', pagina, nombre)
            self.assertIn('class="sol"', pagina, nombre)
        # La etiqueta sale en el idioma de la página.
        for i in self.idiomas:
            carpeta = destino / i if i != "ru" else destino
            self.assertIn(self.textos[i]["tema"], (carpeta / "index.html").read_text(encoding="utf-8"), i)

    def test_la_eleccion_del_lector_gana_sobre_el_sistema(self):
        """Sin las tres piezas, el botón pinta pero no manda: el selector de
        `prefers-color-scheme` tiene que ceder ante data-tema."""
        destino = self._construir()
        pagina = (destino / "index.html").read_text(encoding="utf-8")
        self.assertIn(':root:not([data-tema="light"])', pagina)
        self.assertIn(':root[data-tema="dark"]', pagina)
        self.assertIn("localStorage.getItem('tema')", pagina)

    def test_el_tema_se_aplica_antes_de_pintar(self):
        """Si el script fuera al final, quien eligió noche vería un fogonazo
        blanco en cada carga."""
        destino = self._construir()
        pagina = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertLess(pagina.index("localStorage.getItem('tema')"), pagina.index("</head>"))

    def test_sin_anuncios_configurados_no_se_carga_nada_de_terceros(self):
        cfg = construir_sitio.cargar_config()
        cfg["adsense"]["cliente"] = ""
        cfg["analitica"]["google"] = ""
        destino = self._construir(cfg)
        for nombre in ("index.html", "es/index.html", "en/kurs.html", "semana-01/dia-1.html"):
            pagina = (destino / nombre).read_text(encoding="utf-8")
            for rastro in ("adsbygoogle", "googlesyndication", "googletagmanager", 'id="cookies"'):
                self.assertNotIn(rastro, pagina, f"{nombre}: {rastro}")
        for i in self.idiomas:
            carpeta = destino / i if i != "ru" else destino
            self.assertIn(self.textos[i]["privacidad"]["sin_cookies_texto"][:40],
                          (carpeta / "privacy.html").read_text(encoding="utf-8"))

    def test_con_anuncios_configurados_aparecen_y_el_aviso_de_cookies_tambien(self):
        cfg = construir_sitio.cargar_config()
        cfg["adsense"]["cliente"] = "ca-pub-0000000000000000"
        cfg["adsense"]["bloques"] = {"cabecera": "111", "dentro": "222", "pie": "333"}
        destino = self._construir(cfg)
        leccion = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn("ca-pub-0000000000000000", leccion)
        self.assertEqual(leccion.count('class="adsbygoogle"'), 3, "cabecera, dentro y pie")
        self.assertIn('id="cookies"', leccion)
        self.assertLess(leccion.index('data-ad-slot="222"'), leccion.index("4. Практика"))
        # El aviso de cookies sale en el idioma de la página.
        for i in self.idiomas:
            carpeta = destino / i if i != "ru" else destino
            portada = (carpeta / "index.html").read_text(encoding="utf-8")
            self.assertIn(self.textos[i]["cookies_ok"], portada, i)
            privacidad = (carpeta / "privacy.html").read_text(encoding="utf-8")
            self.assertIn("AdSense", privacidad)
            self.assertNotIn(self.textos[i]["privacidad"]["sin_cookies_texto"][:40], privacidad)

    def test_un_bloque_sin_identificador_no_deja_hueco(self):
        cfg = construir_sitio.cargar_config()
        cfg["adsense"]["cliente"] = "ca-pub-0000000000000000"
        cfg["adsense"]["bloques"] = {"cabecera": "111", "dentro": "", "pie": ""}
        destino = self._construir(cfg)
        leccion = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertEqual(leccion.count('class="adsbygoogle"'), 1)

    def test_el_sitemap_lista_los_tres_idiomas_y_las_lecciones(self):
        destino = self._construir()
        mapa = (destino / "sitemap.xml").read_text(encoding="utf-8")
        for i in self.textos["idiomas"]:
            base = f"{i['carpeta']}/" if i["carpeta"] else ""
            self.assertIn(f"/{base}index.html", mapa, i["codigo"])
            self.assertIn(f"/{base}kurs.html", mapa, i["codigo"])
        for ruta in validar.lecciones():
            datos, _ = validar.frontmatter(ruta.read_text(encoding="utf-8"))
            self.assertIn(f"semana-{int(datos['semana']):02d}/dia-{datos['dia']}.html", mapa)
        self.assertIn("sitemap.xml", (destino / "robots.txt").read_text(encoding="utf-8"))

    def test_un_borrador_se_anuncia_como_borrador(self):
        destino = self._construir()
        for ruta in validar.lecciones():
            datos, _ = validar.frontmatter(ruta.read_text(encoding="utf-8"))
            pagina = (destino / f"semana-{int(datos['semana']):02d}" / f"dia-{datos['dia']}.html").read_text(encoding="utf-8")
            aviso = self.textos["ru"]["leccion"]["borrador"][:30]
            if datos["revisado"]:
                self.assertNotIn(aviso, pagina, str(ruta))
            else:
                self.assertIn(aviso, pagina, str(ruta))

    def test_los_textos_estan_completos_en_los_tres_idiomas(self):
        """Una clave que falte en un idioma revienta la construcción de esa
        página, y es el tipo de fallo que solo se ve mirando esa página."""
        def claves(d, prefijo=""):
            salida = set()
            for k, v in d.items():
                salida.add(prefijo + k)
                if isinstance(v, dict):
                    salida |= claves(v, f"{prefijo}{k}.")
            return salida
        referencia = claves(self.textos["ru"])
        for i in ("es", "en"):
            self.assertEqual(referencia - claves(self.textos[i]), set(), f"faltan claves en {i}")

    def test_docs_esta_al_dia(self):
        destino = self._construir()
        for generado in destino.rglob("*"):
            if not generado.is_file():
                continue
            rel = generado.relative_to(destino)
            versionado = RAIZ / "docs" / rel
            self.assertTrue(versionado.exists(), f"falta docs/{rel}: corre scripts/construir_sitio.py")
            # El .apkg no lo escribe el generador del sitio sino
            # `exportar_apkg.py`, y aquí es un archivo vacío que solo está para
            # que el bloque de descarga se pinte. Compararlo acusaría a `docs/`
            # de algo que esta prueba no mira, y además son 22 MB de binario
            # que `read_text` ni siquiera puede abrir.
            if generado.suffix == ".apkg":
                continue
            self.assertEqual(versionado.read_text(encoding="utf-8"), generado.read_text(encoding="utf-8"), f"docs/{rel} desactualizado")


class TestElProgresoDelLector(unittest.TestCase):
    """Sin registro y sin servidor: el navegador recuerda por dónde iba.

    Lo que se fija aquí es el contrato entre el HTML que genera el sitio y
    progreso.js, que es lo único que los ata: un atributo que cambie de nombre
    no rompe ninguna página, deja de funcionar el progreso y nadie se entera."""

    def setUp(self):
        self.cfg = construir_sitio.cargar_config()
        self.textos = construir_sitio.cargar_textos()
        self.destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(self.destino, self.cfg, self.textos)
        self.cal = plan.cargar()

    def _leer(self, *partes):
        return self.destino.joinpath(*partes).read_text(encoding="utf-8")

    def test_el_guion_se_publica_y_lo_cargan_las_paginas(self):
        self.assertTrue((self.destino / "progreso.js").exists())
        for ruta in (("index.html",), ("kurs.html",), ("es", "index.html"),
                     ("semana-01", "dia-1.html")):
            html_ = self._leer(*ruta)
            self.assertIn("progreso.js", html_, "/".join(ruta))
            self.assertIn("CURSO_DIAS=", html_, "/".join(ruta))

    def test_la_leccion_se_marca_con_article_y_no_con_el_li_del_indice(self):
        """progreso.js busca article[data-leccion] para saber en qué lección está.

        Si buscara [data-leccion] a secas, el primero del índice es un <li> de
        la lección 1: abrir «todas las lecciones» movería «la última leída» al
        principio del curso y «continuar» mandaría al día 1."""
        guion = self._leer("progreso.js")
        self.assertIn("querySelector('article[data-leccion]')", guion)
        leccion = self._leer("semana-01", "dia-1.html")
        self.assertIn('<article data-leccion="1">', leccion)
        self.assertIn('id="marcar-caja"', leccion)
        self.assertIn('id="enlace-siguiente"', leccion)
        indice = self._leer("kurs.html")
        self.assertIn('<li data-leccion="1">', indice)
        self.assertNotIn("<article data-leccion", indice)

    def test_solo_las_escritas_estan_en_el_mapa(self):
        """«Continuar» no puede mandar a una lección que no existe."""
        mapa = json.loads(construir_sitio.mapa_de_dias(self.cal))
        escritas = {d.numero for d in construir_sitio.escritas(self.cal)}
        self.assertEqual(set(int(k) for k in mapa), escritas)
        for n, ruta in mapa.items():
            self.assertTrue((self.destino / ruta).exists(), f"{n} → {ruta}")

    def test_lo_que_depende_del_navegador_nace_oculto(self):
        """La primera visita no sabe nada del lector: sin esto se vería un botón
        «continuar» vacío y un contador en cero, que desaniman."""
        portada = self._leer("index.html")
        for trozo in ('id="continuar"', 'id="mio"', 'id="borrar-progreso"'):
            i = portada.index(trozo)
            self.assertIn("hidden", portada[i:portada.index(">", i)], trozo)
        self.assertIn("[hidden]{display:none!important}", construir_sitio.CSS,
                      "el [hidden] del navegador pierde contra .boton{display:inline-block}")

    def test_el_aviso_de_que_el_progreso_no_viaja_esta_en_los_tres_idiomas(self):
        """Es lo único que el lector tiene que saber: no hay cuenta, y si cambia
        de teléfono o borra los datos del navegador, las marcas no van con él."""
        for i in self.textos["idiomas"]:
            aviso = self.textos[i["codigo"]]["progreso"]["aviso"]
            carpeta = self.destino / i["carpeta"] if i["carpeta"] else self.destino
            for pagina in ("index.html", "kurs.html"):
                self.assertIn(html.escape(aviso), carpeta.joinpath(pagina).read_text(encoding="utf-8"),
                              f"{i['codigo']}/{pagina}")


class TestElTachado(unittest.TestCase):
    """~~h~~otel y ~~Yo gusto~~: sin tachado, la forma mala parece la buena."""

    def test_las_dobles_tildes_se_vuelven_del(self):
        self.assertEqual(construir_sitio.md("~~h~~otel"), "<p><del>h</del>otel</p>")
        self.assertEqual(construir_sitio.md("una ~~forma mala~~ aquí"),
                         "<p>una <del>forma mala</del> aquí</p>")

    def test_una_tilde_suelta_no_tacha_nada(self):
        self.assertIn("~", construir_sitio.md("a ~~ b"))

    def test_ninguna_leccion_publicada_deja_tildes_a_la_vista(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        for ruta in destino.glob("semana-*/dia-*.html"):
            self.assertNotIn("~~", ruta.read_text(encoding="utf-8"), ruta.name)


class TestLaPublicidad(unittest.TestCase):
    """Lo que AdSense pide y el generador tiene que poner solo."""

    def setUp(self):
        self.textos = construir_sitio.cargar_textos()
        self.cfg = construir_sitio.cargar_config()

    def _con(self, **cambios):
        """Construye con la publicidad APAGADA salvo que la prueba la encienda.

        Antes partía del `web/sitio.yaml` real tal cual, y eso funcionó solo
        mientras ese fichero estuvo vacío: `_con()` significaba «sin anuncios»
        por casualidad, no por decisión. El día que el profesor puso su
        identificador de AdSense, las dos pruebas del caso «sin anuncios»
        se pusieron en rojo sin que nadie hubiera tocado el generador.

        Una prueba no puede depender de un valor de producción: aquí se apagan
        a mano, y la que quiera anuncios los pide con `adsense=...`."""
        cfg = copy.deepcopy(self.cfg)
        cfg["adsense"] = {"cliente": "", "bloques": {}}
        cfg["analitica"] = {"google": ""}
        # Y Yandex, por el mismo motivo: el día que el profesor pegue un
        # identificador en `web/sitio.yaml`, estas pruebas no pueden cambiar de
        # significado sin que nadie haya tocado el generador.
        cfg["yandex"] = {"bloques": {}}
        cfg.update(cambios)
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, cfg, self.textos)
        return destino

    def test_sin_cliente_no_se_carga_nada_de_terceros(self):
        """El sitio se publica hoy sin anuncios y sin aviso de cookies: eso es lo
        que deja que la política de privacidad diga la verdad."""
        destino = self._con()
        portada = (destino / "index.html").read_text(encoding="utf-8")
        for rastro in ("googlesyndication", "adsbygoogle", "googletagmanager", 'id="cookies"'):
            self.assertNotIn(rastro, portada, rastro)
        self.assertFalse((destino / "ads.txt").exists(), "un ads.txt sin cliente es peor que ninguno")

    def test_con_cliente_salen_los_bloques_el_aviso_y_el_ads_txt(self):
        destino = self._con(adsense={"cliente": "ca-pub-1234567890123456",
                                     "bloques": {"cabecera": "111", "dentro": "222", "pie": "333"}})
        leccion = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertEqual(leccion.count('class="adsbygoogle"'), 3, "cabecera, dentro y pie")
        self.assertIn("googlesyndication.com", leccion)
        self.assertIn('id="cookies"', leccion, "con anuncios hace falta el aviso")
        self.assertIn("google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0",
                      (destino / "ads.txt").read_text(encoding="utf-8"))

    def test_la_politica_de_privacidad_cuenta_los_anuncios_solo_si_los_hay(self):
        """Decir que hay anuncios cuando no los hay, o callarlos cuando los hay,
        son las dos formas de que la política mienta."""
        sin = (self._con() / "es" / "privacy.html").read_text(encoding="utf-8")
        con = (self._con(adsense={"cliente": "ca-pub-1", "bloques": {"pie": "9"}})
               / "es" / "privacy.html").read_text(encoding="utf-8")
        self.assertNotIn("google.com/settings/ads", sin)
        self.assertIn("google.com/settings/ads", con)

    def test_el_ads_txt_y_el_cname_solo_con_dominio_propio(self):
        """ads.txt tiene que estar en la RAÍZ del dominio. En
        usuario.github.io/proyecto/ cae en /proyecto/ads.txt, donde AdSense no
        mira: por eso el dominio propio no es un lujo, es el requisito."""
        anuncios = {"cliente": "ca-pub-1234567890123456", "bloques": {"pie": "333"}}
        en_github = self._con(adsense=anuncios, dominio="https://ianmusicall-max.github.io/espanol-desde-ruso")
        self.assertFalse((en_github / "CNAME").exists(), "un CNAME de github.io deja el sitio sin servir")

        propio = self._con(adsense=anuncios, dominio="https://espanoldesderuso.com")
        self.assertEqual((propio / "CNAME").read_text(encoding="utf-8").strip(), "espanoldesderuso.com")
        self.assertTrue((propio / "ads.txt").exists())


class TestLaExportacionAWordPress(unittest.TestCase):
    """El XML que importa WordPress de un clic."""

    def setUp(self):
        self.cal = plan.cargar()
        self.destino = pathlib.Path(tempfile.mkdtemp())
        self.resumen = exportar_wordpress.exportar(
            self.cal, construir_sitio.cargar_config(), self.destino)
        self.arbol = ET.parse(self.destino / "curso-wordpress.xml").getroot()
        self.ns = {"wp": "http://wordpress.org/export/1.2/",
                   "content": "http://purl.org/rss/1.0/modules/content/"}

    def _items(self, tipo):
        return [i for i in self.arbol.findall(".//item")
                if i.find("wp:post_type", self.ns).text == tipo]

    def test_estan_todas_las_lecciones_escritas_y_el_indice(self):
        self.assertEqual(len(self._items("post")), len(construir_sitio.escritas(self.cal)))
        self.assertEqual(len(self._items("page")), 1, "la página del índice")

    def test_las_lecciones_sin_revisar_entran_como_borrador(self):
        """La regla 6 del proyecto tiene que sobrevivir al cambio de plataforma:
        si entraran publicadas, mudarse a WordPress sería la forma de saltársela
        sin querer."""
        estados = {}
        for d, item in zip(construir_sitio.escritas(self.cal), self._items("post")):
            datos, _ = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))
            estados[item.find("wp:status", self.ns).text] = True
            self.assertEqual(item.find("wp:status", self.ns).text,
                             "publish" if datos.get("revisado") else "draft",
                             f"lección {d.numero}")
        self.assertEqual(set(estados), {"publish", "draft"}, "hay de las dos")

    def test_el_contraste_con_el_ruso_no_depende_del_css_del_sitio(self):
        """Es la firma del curso y lo único que un tema ajeno se llevaría por
        delante del todo, así que va con el estilo dentro."""
        for item in self._items("post")[:5]:
            cuerpo = item.find("content:encoded", self.ns).text
            if "contraste" in cuerpo:
                self.assertIn('class="contraste" style=', cuerpo)
                break
        else:
            self.fail("ninguna de las cinco primeras lecciones trae el bloque de contraste")

    def test_cada_leccion_lleva_su_unidad_como_categoria(self):
        for d, item in zip(construir_sitio.escritas(self.cal), self._items("post")):
            cats = [c.text for c in item.findall("category") if c.get("domain") == "category"]
            self.assertEqual(cats, [exportar_wordpress.categoria_de(self.cal, d)[0]], f"lección {d.numero}")

    def test_las_direcciones_son_legibles_fuera_del_cirilico(self):
        """WordPress acepta un slug en cirílico, pero la URL viaja codificada
        como %D0%A3… y se vuelve ilegible al compartirla por WhatsApp."""
        for item in self._items("post"):
            nombre = item.find("wp:post_name", self.ns).text
            self.assertRegex(nombre, r"^urok-\d+$")

    def test_el_orden_del_curso_y_el_del_blog_coinciden(self):
        """Un blog ordena por fecha descendente y un curso se lee del 1 al 100:
        la lección 1 tiene que ser la MÁS ANTIGUA o la portada abre por la 100."""
        fechas = [i.find("wp:post_date", self.ns).text for i in self._items("post")]
        self.assertEqual(fechas, sorted(fechas))

    def test_ningun_cdata_se_corta_a_la_mitad(self):
        """Un «]]>» dentro del contenido cierra la sección antes de tiempo y el
        importador rechaza el archivo entero. El XML parsea, que es la prueba."""
        bruto = (self.destino / "curso-wordpress.xml").read_text(encoding="utf-8")
        self.assertNotIn("]]>]]>", bruto)
        ET.fromstring(bruto)


class TestElDespliegueEnNetlify(unittest.TestCase):
    """netlify.toml no se usa hoy, y por eso es justo el que se queda viejo.

    Un archivo de despliegue que nombra un script que ya no existe no rompe
    nada aquí: rompe el día que alguien conecta el repositorio y el sitio sale
    vacío. Estas pruebas leen el archivo y comprueban contra el repo real."""

    def setUp(self):
        import tomllib
        self.cfg = tomllib.loads((RAIZ / "netlify.toml").read_text(encoding="utf-8"))

    def test_el_comando_de_construccion_es_el_generador_de_verdad(self):
        comando = self.cfg["build"]["command"]
        self.assertIn("requirements.txt", comando, "sin dependencias el build falla")
        guion = re.search(r"python\s+(\S+\.py)", comando)
        self.assertIsNotNone(guion, f"no se reconoce el guion en: {comando}")
        self.assertTrue((RAIZ / guion.group(1)).exists(), guion.group(1))

    def test_publica_la_carpeta_que_el_generador_escribe(self):
        """Si no coinciden, Netlify sirve un directorio vacío y el error que se
        ve es «Page not found», que no apunta a este archivo."""
        self.assertEqual(RAIZ / self.cfg["build"]["publish"], construir_sitio.DOCS)

    def test_el_ads_txt_no_se_cachea_mucho(self):
        """AdSense lo consulta solo; una copia vieja le hace creer que el sitio
        no declara su editor y deja de pagar el inventario."""
        cabeceras = {h["for"]: h["values"] for h in self.cfg.get("headers", [])}
        self.assertIn("/ads.txt", cabeceras)
        edad = re.search(r"max-age=(\d+)", cabeceras["/ads.txt"]["Cache-Control"])
        self.assertLessEqual(int(edad.group(1)), 3600)


class TestNingunEnlaceLlevaANingunaParte(unittest.TestCase):
    """215 enlaces rotos vivieron meses en el sitio sin que nadie los viera.

    Eran el conmutador de idioma en las páginas que existen en UNO solo: las
    100 lecciones (en ruso, que son el curso) y los 7 documentos del programa
    (en español). El lector pulsaba «ES» en una lección y le salía un 404, y
    los hreflang apuntaban a páginas que no existen. No se vio antes porque
    ninguna prueba recorría los enlaces: se miraba que el conmutador llevara a
    la misma página, no que esa página estuviera."""

    def setUp(self):
        self.destino = pathlib.Path(tempfile.mkdtemp())
        self.textos = construir_sitio.cargar_textos()
        construir_sitio.construir(self.destino, construir_sitio.cargar_config(), self.textos)

    def test_no_hay_un_solo_enlace_interno_roto(self):
        rotos = revisar_adsense.enlaces_rotos(self.destino)
        self.assertEqual(rotos, [], f"{len(rotos)} rotos, p.ej. {rotos[:3]}")

    def test_en_una_leccion_el_conmutador_no_mueve_al_lector(self):
        """Cuarta versión de esto, y las tres anteriores estaban mal.

        La 1.ª apuntaba a la gemela y daba 404 (215 enlaces rotos). La 2.ª
        mandaba a la portada de ese idioma, y el profesor lo reportó en cuanto
        lo usó: pulsas «ES» esperando esta página en español y apareces en la
        portada, habiendo perdido la lección que leías. La 3.ª dejó los tres
        inertes, y el profesor volvió: «no cambian los idiomas». Las tres
        fallaban en lo mismo —la página nunca DECÍA que aquí no hay versión en
        ese idioma; el motivo estaba en un `title`, que en el móvil no existe—.

        El contrato de ahora: ningún `<a>` en el conmutador, los otros dos
        idiomas son botones con la portada que van a OFRECER, y el propio es un
        span inerte (era enlace a la portada, así que pulsar «ru» desde una
        lección en ruso también te sacaba de ella)."""
        leccion = (self.destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        conmutador = re.search(r'<div class="idiomas".*?</div>', leccion, re.S).group(0)
        self.assertNotIn("<a ", conmutador, "el conmutador no puede llevar a ninguna parte")
        self.assertEqual(2, conmutador.count('class="apagado"'), conmutador)
        self.assertIn('<span lang="ru" aria-current="true">', conmutador)
        self.assertNotIn("../es/semana-01", leccion)

    def test_el_aviso_explica_por_que_y_nace_oculto(self):
        """El defecto de las tres versiones anteriores era este: nada decía al
        lector por qué el otro idioma no hacía lo que esperaba. El aviso lo
        dice, y nace oculto porque sin JavaScript los botones no abren nada y
        un aviso suelto en la cabecera no explicaría nada de nada."""
        leccion = (self.destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        aviso = re.search(r'<p class="sin-idioma".*?</p>', leccion, re.S).group(0)
        self.assertIn("hidden", aviso)
        self.assertIn(self.textos["ru"]["solo_este_idioma"], aviso)
        self.assertIn(self.textos["ru"]["ir_a_portada"], aviso)
        # Y el guion que los enciende tiene que estar en esa página: sin él los
        # botones son adorno y volvemos a la tercera versión.
        self.assertIn("sin-idioma", construir_sitio.IDIOMA_SCRIPT)
        self.assertIn(construir_sitio.IDIOMA_SCRIPT, leccion)

    def test_la_portada_que_ofrece_el_aviso_existe(self):
        """Nadie más comprueba esto: `revisar_adsense.enlaces_rotos` se salta el
        `href=""` vacío (lo rellena el navegador) y los `<script>`. O sea que el
        destino viaja en un `data-portada` que ningún revisor mira.

        Y es justo el fallo que esta suite ya ha cazado dos veces por el mismo
        motivo —el conmutador y las tarjetas del mapa de unidades—: una ruta
        relativa escrita sin tener en cuenta en qué carpeta está la página."""
        for relativa in ("semana-01/dia-1.html", "semana-14/dia-7.html",
                         "programa/metodologia.html", "test.html"):
            pagina = self.destino / relativa
            marcas = re.findall(r'data-portada="([^"]+)"', pagina.read_text(encoding="utf-8"))
            self.assertEqual(2, len(marcas), relativa)
            for destino in marcas:
                self.assertTrue((pagina.parent / destino).resolve().exists(),
                                f"{relativa} ofrece {destino}, que no existe")

    def test_pero_donde_la_pagina_sí_esta_traducida_el_conmutador_funciona(self):
        """El arreglo no podía apagar el conmutador en todo el sitio: en las
        cinco páginas que sí están en tres idiomas tiene que llevar a la
        gemela, no a la portada."""
        for nombre in ("index.html", "kurs.html", "o-kurse.html", "kontakt.html", "privacy.html"):
            pagina = (self.destino / nombre).read_text(encoding="utf-8")
            conmutador = re.search(r'<div class="idiomas".*?</div>', pagina, re.S).group(0)
            self.assertNotIn("apagado", conmutador, nombre)
            self.assertIn(f'href="./es/{nombre}"', conmutador, nombre)
            self.assertIn(f'href="./en/{nombre}"', conmutador, nombre)

    def test_el_idioma_activo_se_resalta_tambien_cuando_es_un_span(self):
        """El resaltado colgaba de `.idiomas a[aria-current]`. Al dejar de ser
        un enlace, en 108 páginas no se veía cuál era el idioma activo."""
        self.assertIn(".idiomas [aria-current]{background:var(--acento)", construir_sitio.CSS)

    def test_una_pagina_sin_traducir_no_declara_hreflang(self):
        """hreflang dice «esta URL es la MISMA página traducida». Apuntarlo a la
        portada le cuenta a Google algo falso, que es peor que no decir nada."""
        leccion = (self.destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertNotIn('rel="alternate"', leccion)
        programa = next((self.destino / "programa").glob("*.html")).read_text(encoding="utf-8")
        self.assertNotIn('rel="alternate"', programa)

    def test_las_paginas_que_sí_estan_en_tres_idiomas_los_siguen_declarando(self):
        """El arreglo no puede llevarse por delante el hreflang de las que sí
        están traducidas: son las que el buscador tiene que emparejar."""
        for nombre in ("index.html", "kurs.html", "o-kurse.html", "privacy.html"):
            pagina = (self.destino / nombre).read_text(encoding="utf-8")
            self.assertEqual(pagina.count('rel="alternate"'), 3, nombre)


class TestElRevisorDeAdsense(unittest.TestCase):
    """Solo lee, y separa lo que se puede comprobar de lo que no."""

    def test_no_escribe_nada(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        antes = {p: p.stat().st_mtime_ns for p in destino.rglob("*") if p.is_file()}
        revisar_adsense.revisar(destino, construir_sitio.cargar_config(), plan.cargar())
        despues = {p: p.stat().st_mtime_ns for p in destino.rglob("*") if p.is_file()}
        self.assertEqual(antes, despues)

    def test_un_dominio_gratis_se_marca_como_que_falta(self):
        """github.io, netlify.app, vercel.app y wordpress.com son todos el mismo
        caso: el dominio no es tuyo. Si uno se escapara, el revisor diría que
        está listo y la solicitud se rechazaría un mes después."""
        destino = pathlib.Path(tempfile.mkdtemp())
        cfg = copy.deepcopy(construir_sitio.cargar_config())
        for host in ("usuario.github.io", "curso.netlify.app", "curso.vercel.app",
                     "curso.wordpress.com"):
            cfg["dominio"] = f"https://{host}"
            construir_sitio.construir(destino, cfg, construir_sitio.cargar_textos())
            filas = revisar_adsense.revisar(destino, cfg, plan.cargar())
            falta = [t for e, t, _ in filas if e == "FALTA" and "no es tuyo" in t]
            self.assertTrue(falta, f"{host} tendría que marcarse como dominio ajeno")

        cfg["dominio"] = "https://espanoldesderuso.com"
        construir_sitio.construir(destino, cfg, construir_sitio.cargar_textos())
        filas = revisar_adsense.revisar(destino, cfg, plan.cargar())
        self.assertFalse([t for e, t, _ in filas if e == "FALTA" and "no es tuyo" in t])


    def test_un_href_dentro_de_un_script_no_es_un_enlace(self):
        """El guion del test de nivel arma el enlace del resultado
        concatenando `href="'+dest.url+'"`. Leido como marca, eso es un enlace
        a un fichero que no existe, y el revisor cantaba un roto que ningun
        lector puede pulsar."""
        destino = pathlib.Path(tempfile.mkdtemp())
        (destino / "p.html").write_text(
            '<a href="existe.html">ok</a>'
            '<script>var h=\'<a href="\'+x.url+\'">\'</script>',
            encoding="utf-8")
        (destino / "existe.html").write_text("ok", encoding="utf-8")
        self.assertEqual(revisar_adsense.enlaces_rotos(destino), [])

    def test_y_un_enlace_roto_de_verdad_sigue_saliendo(self):
        """El arreglo no puede dejar ciego al revisor: es la prueba que ya cazo
        215 rotos del conmutador de idioma y los enlaces del mapa."""
        destino = pathlib.Path(tempfile.mkdtemp())
        (destino / "p.html").write_text('<a href="no-existe.html">x</a>', encoding="utf-8")
        self.assertEqual(revisar_adsense.enlaces_rotos(destino),
                         [("p.html", "no-existe.html")])


class TestPonerElDominio(unittest.TestCase):
    """El guion del día de la compra. Lo que se prueba es lo que se rompe."""

    def test_acepta_el_dominio_escrito_de_las_formas_normales(self):
        """Nadie teclea el dominio dos veces igual."""
        for entrada in ("espanoldesderuso.com", "ESPANOLDESDERUSO.COM",
                        "https://espanoldesderuso.com", "https://espanoldesderuso.com/",
                        "  espanoldesderuso.com  "):
            self.assertEqual(poner_dominio.comprobar(entrada), "espanoldesderuso.com", entrada)

    def test_rechaza_lo_que_dejaria_el_sitio_sin_servir(self):
        """Un CNAME con «https://» o con «www» dentro no sirve nada, y GitHub
        Pages no dice por qué: la página simplemente no carga."""
        for malo in ("www.midominio.com", "no es un dominio", "", "midominio",
                     "curso.github.io", "curso.netlify.app", "curso.wordpress.com"):
            with self.assertRaises(SystemExit, msg=malo):
                poner_dominio.comprobar(malo)

    def test_escribe_el_dominio_sin_llevarse_los_comentarios(self):
        """web/sitio.yaml es medio archivo de comentarios que explican cada
        ajuste. Un yaml.dump los borraría todos y nadie lo notaría hasta
        necesitarlos."""
        copia = pathlib.Path(tempfile.mkdtemp()) / "sitio.yaml"
        original = construir_sitio.CONFIG.read_text(encoding="utf-8")
        copia.write_text(original, encoding="utf-8")

        poner_dominio.escribir("espanoldesderuso.com", copia)
        nuevo = copia.read_text(encoding="utf-8")

        self.assertIn('dominio: "https://espanoldesderuso.com"', nuevo)
        self.assertEqual(nuevo.count("#"), original.count("#"), "se perdieron comentarios")
        self.assertEqual(len(nuevo.splitlines()), len(original.splitlines()))
        self.assertEqual(yaml.safe_load(nuevo)["dominio"], "https://espanoldesderuso.com")

    def test_con_dominio_propio_aparecen_el_cname_y_la_url_canonica(self):
        """Es lo que de verdad desbloquea AdSense, y se comprueba construyendo."""
        cfg = copy.deepcopy(construir_sitio.cargar_config())
        cfg["dominio"] = "https://espanoldesderuso.com"
        cfg["adsense"] = {"cliente": "ca-pub-1234567890123456", "bloques": {"pie": "333"}}
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, cfg, construir_sitio.cargar_textos())

        self.assertEqual((destino / "CNAME").read_text(encoding="utf-8").strip(),
                         "espanoldesderuso.com")
        self.assertTrue((destino / "ads.txt").exists())
        leccion = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="https://espanoldesderuso.com/semana-01/dia-1.html"',
                      leccion)
        self.assertNotIn("github.io", (destino / "sitemap.xml").read_text(encoding="utf-8"))

    def test_las_direcciones_de_github_pages_son_cuatro_y_cuatro(self):
        """Si alguien recorta la lista, el dominio resuelve a veces sí y a veces
        no, según a qué IP caiga: el fallo más difícil de leer que hay."""
        self.assertEqual(len(poner_dominio.A_GITHUB), 4)
        self.assertEqual(len(poner_dominio.AAAA_GITHUB), 4)
        for ip in poner_dominio.A_GITHUB:
            self.assertRegex(ip, r"^185\.199\.10[89]\.153$|^185\.199\.11[01]\.153$")
        texto = poner_dominio.instrucciones("ejemplo.com")
        for ip in poner_dominio.A_GITHUB + poner_dominio.AAAA_GITHUB:
            self.assertIn(ip, texto)
        self.assertIn("DNS only", texto, "el proxy de Cloudflare impide el certificado")


class TestLaFormaDeContacto(unittest.TestCase):
    """AdSense pide una forma de contactar, y el sitio la publica de verdad."""

    def setUp(self):
        self.cfg = construir_sitio.cargar_config()
        self.textos = construir_sitio.cargar_textos()

    def _construir(self, cfg):
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, cfg, self.textos)
        return destino

    def test_el_correo_sale_en_los_tres_idiomas(self):
        correo = self.cfg["autor"]["email"]
        self.assertTrue(correo, "sin correo, AdSense marca la página de contacto")
        destino = self._construir(self.cfg)
        for i in self.textos["idiomas"]:
            carpeta = destino / i["carpeta"] if i["carpeta"] else destino
            pagina = carpeta.joinpath("kontakt.html").read_text(encoding="utf-8")
            self.assertIn(f"mailto:{correo}", pagina, i["codigo"])

    def test_el_correo_publicado_es_el_de_la_configuracion_y_no_otro(self):
        """Un correo escrito a mano en una plantilla se queda viejo el día que
        se cambia el de verdad, y nadie se entera hasta que alguien escribe a
        una dirección muerta."""
        cfg = copy.deepcopy(self.cfg)
        cfg["autor"] = dict(cfg["autor"], email="otro@ejemplo.com")
        destino = self._construir(cfg)
        pagina = (destino / "kontakt.html").read_text(encoding="utf-8")
        self.assertIn("mailto:otro@ejemplo.com", pagina)
        self.assertNotIn(self.cfg["autor"]["email"], pagina)

    def test_sin_correo_la_pagina_lo_dice_en_vez_de_quedarse_muda(self):
        """Una página de contacto sin nada es peor que no tenerla: el lector no
        sabe si falta un dato o si es que no quieres que te escriban."""
        cfg = copy.deepcopy(self.cfg)
        cfg["autor"] = dict(cfg["autor"], email="")
        pagina = (self._construir(cfg) / "kontakt.html").read_text(encoding="utf-8")
        self.assertNotIn("mailto:", pagina)
        self.assertIn(html.escape(self.textos["ru"]["contacto"]["sin_correo"]), pagina)

    def test_las_paginas_del_sitio_no_publican_ningun_otro_correo(self):
        """El sitio es público: de lo que escribe el generador, el único correo
        que sale es el que el profesor puso a propósito para el curso.

        Las lecciones quedan fuera a propósito y no es una excusa: la 3-5
        enseña a dictar una dirección en español («arroba», «punto») y lleva
        cinco inventadas (ivan.petrov@gmail.com y compañía). Son material
        didáctico, no una fuga. Lo que esta prueba cuida es la otra cosa: que
        una dirección personal no se cuele por la cabecera, el pie, la página
        de contacto o los datos estructurados."""
        destino = self._construir(self.cfg)
        permitido = self.cfg["autor"]["email"]
        revisadas = 0
        for pagina in destino.rglob("*.html"):
            if pagina.parent.name.startswith("semana-"):
                continue
            revisadas += 1
            for correo in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", pagina.read_text(encoding="utf-8")):
                self.assertEqual(correo, permitido, f"{pagina.relative_to(destino)}: {correo}")
        self.assertGreater(revisadas, 20, "se saltearon casi todas: el filtro está mal")

    def test_la_cabecera_y_el_pie_de_una_leccion_tampoco_traen_correos(self):
        """La excepción de arriba vale para el CUERPO de la lección, que lo
        escribe el profesor. Lo que el generador pone alrededor no."""
        destino = self._construir(self.cfg)
        leccion = (destino / "semana-03" / "dia-5.html").read_text(encoding="utf-8")
        marco = leccion[:leccion.index("<main")] + leccion[leccion.index("</main>"):]
        self.assertNotIn("@gmail", marco)
        self.assertNotIn("@correo", marco)


class TestElAudioDeLasLecciones(unittest.TestCase):
    """Las frases españolas se pueden oír. Cuesta ~1,30 USD una sola vez."""

    def setUp(self):
        self.cal = plan.cargar()

    def test_no_se_locuta_la_columna_rusa(self):
        """Es el fallo que haría el audio inútil y costaría el doble: una voz
        española leyendo «Спокойной ночи»."""
        for f in generar_audio.todas_las_frases(self.cal):
            self.assertNotRegex(f, r"[а-яА-ЯёЁ]", f"se colaría ruso: {f!r}")

    def test_ni_las_cabeceras_ni_la_transcripcion_fonetica(self):
        """«Español» encabeza casi todas las tablas (199 veces) y «[a]» es un
        símbolo para leer con los ojos: una voz diría «corchete a corchete»."""
        self.assertFalse(generar_audio.vale_la_pena("Español"))
        self.assertFalse(generar_audio.vale_la_pena("[a]"))
        self.assertFalse(generar_audio.vale_la_pena("/kasa/"))
        self.assertFalse(generar_audio.vale_la_pena("— Спокойной ночи."))
        self.assertFalse(generar_audio.vale_la_pena("123"))
        for buena in ("casa", "— ¡Hola! ¿Qué tal?", "a", "Me llamo Ana"):
            self.assertTrue(generar_audio.vale_la_pena(buena), buena)

    def test_se_locuta_la_palabra_de_ejemplo_y_no_solo_la_letra(self):
        """En las tablas de fonética la letra está en la 1ª columna y la
        palabra («casa») en la 4ª, que es la que hay que oír. Mirar solo la
        primera columna dejaba fuera justo lo útil."""
        frases = generar_audio.frases_de(plan.dias(self.cal)[0].ruta)
        for palabra in ("casa", "mesa", "moto", "uno"):
            self.assertIn(palabra, frases)

    def test_la_misma_frase_se_locuta_y_se_paga_una_vez(self):
        """«Buenos días» sale en varias lecciones. El nombre es un hash del
        pedido entero, así que es el mismo archivo."""
        self.assertEqual(generar_audio.nombre_de("Buenos días"),
                         generar_audio.nombre_de("Buenos días"))
        self.assertNotEqual(generar_audio.nombre_de("Buenos días"),
                            generar_audio.nombre_de("Buenas noches"))
        self.assertNotEqual(generar_audio.nombre_de("Buenos días"),
                            generar_audio.nombre_de("Buenos días", voz="alloy"))
        self.assertEqual(len(generar_audio.todas_las_frases(self.cal)),
                         len(set(generar_audio.todas_las_frases(self.cal))))

    def test_un_archivo_vacio_no_cuenta_como_locutado(self):
        """Una descarga cortada dejaría un MP3 de cero bytes que el sitio
        serviría como bueno: el lector pulsa ▶ y no suena nada."""
        carpeta = pathlib.Path(tempfile.mkdtemp())
        (carpeta / generar_audio.nombre_de("casa")).write_bytes(b"")
        (carpeta / generar_audio.nombre_de("mesa")).write_bytes(b"ID3datos")
        pendientes = generar_audio.faltan(["casa", "mesa"], carpeta)
        self.assertEqual(pendientes, ["casa"])
        self.assertEqual(generar_audio.escribir_indice(["casa", "mesa"], carpeta), 1)

    def test_sin_audio_el_sitio_se_construye_igual_y_sin_botones(self):
        """El audio se genera por tandas: el estado normal durante un tiempo es
        «algunas frases sí y otras no», y ninguna página puede romperse."""
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        leccion = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertNotIn('class="suena"', leccion)
        self.assertNotIn("sonando", leccion, "ni se carga el reproductor")

    def test_con_audio_salen_los_botones_y_el_reproductor(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        carpeta = destino / "audio"
        carpeta.mkdir(parents=True)
        for frase in ("casa", "— ¡Hola!"):
            (carpeta / generar_audio.nombre_de(frase)).write_bytes(b"ID3datos")
        generar_audio.escribir_indice(["casa", "— ¡Hola!"], carpeta)
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())

        leccion = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn('class="suena"', leccion)
        self.assertIn(f'data-audio="../audio/{generar_audio.nombre_de("casa")}"', leccion)
        self.assertIn("sonando", leccion, "el reproductor tiene que ir en la página")
        # y una lección sin ninguna de esas dos frases no carga el reproductor
        otra = (destino / "semana-09" / "dia-3.html").read_text(encoding="utf-8")
        self.assertNotIn("sonando", otra)


    def test_otra_voz_es_otro_archivo_y_no_pisa_la_primera(self):
        """Cambiar de voz cuesta los 1,30 USD otra vez, asi que hay que poder
        comparar dos sin que la segunda borre la primera. Y sobre todo: el
        indice no puede acabar mezclando dos voces en la misma pagina."""
        carpeta = pathlib.Path(tempfile.mkdtemp())
        frase = "Buenos dias"
        uno = generar_audio.nombre_de(frase, "nova")
        otro = generar_audio.nombre_de(frase, "sage")
        self.assertNotEqual(uno, otro)
        (carpeta / uno).write_bytes(b"x")
        self.assertEqual(generar_audio.faltan([frase], carpeta, "nova"), [])
        self.assertEqual(generar_audio.faltan([frase], carpeta, "sage"), [frase])
        generar_audio.escribir_indice([frase], carpeta, "nova")
        indice = json.loads((carpeta / generar_audio.INDICE).read_text(encoding="utf-8"))
        self.assertEqual(indice, {frase: uno})

    def test_la_muestra_coge_las_frases_mas_largas(self):
        """Una voz se juzga en una frase entera. Por orden de leccion la
        primera seria la letra «a», que no dice nada de como suena."""
        frases = ["a", "Buenos dias", "Me llamo Ana y vivo en Madrid", "casa"]
        self.assertEqual(generar_audio.muestra_de(frases, 2),
                         ["Me llamo Ana y vivo en Madrid", "Buenos dias"])
        self.assertEqual(len(generar_audio.muestra_de(frases, 99)), 4)

        # Y sobre las de verdad: ninguna de las tres primeras puede ser una letra
        reales = generar_audio.muestra_de(
            generar_audio.todas_las_frases(plan.cargar()), 3)
        self.assertTrue(all(len(f) > 10 for f in reales), reales)

    def test_sin_clave_no_se_inventa_nada(self):
        """Sin OPENAI_API_KEY devuelve 1 y no escribe un solo archivo: un MP3
        falso donde el lector espera una voz es peor que no tener audio."""
        carpeta = pathlib.Path(tempfile.mkdtemp())
        self.assertEqual(generar_audio.main(["--carpeta", str(carpeta)]), 1)
        self.assertEqual(list(carpeta.glob("*.mp3")), [])


class TestLaHistoria(unittest.TestCase):
    """Ana e Iván: un episodio por unidad, en el día `cultura` de la 2.ª semana.

    Lo que se vigila aquí es que el arco y el calendario no se separen. Es el
    fallo que más se repite en este proyecto: lo escrito en un .md y lo que de
    verdad corre dejan de coincidir, y nadie se entera porque nada se pone en
    rojo."""

    def setUp(self):
        self.cal = plan.cargar()
        self.unidades = self.cal["unidades"]
        self.arco = (RAIZ / "programa" / "historia.md").read_text(encoding="utf-8")

    def test_cada_unidad_tiene_su_episodio(self):
        for u in self.unidades:
            ep = u.get("episodio")
            self.assertIsNotNone(ep, f"unidad {u['numero']} sin episodio")
            self.assertTrue(ep.get("titulo"), u["numero"])
            self.assertTrue(ep.get("sinopsis"), u["numero"])

    def test_ningun_episodio_repite_titulo(self):
        titulos = [u["episodio"]["titulo"] for u in self.unidades]
        self.assertEqual(len(titulos), len(set(titulos)))

    def test_el_arco_escrito_nombra_los_mismos_episodios_que_el_calendario(self):
        """Si alguien renombra un episodio en el YAML y no en historia.md, el
        documento pasa a describir una historia que el curso no cuenta."""
        for u in self.unidades:
            self.assertIn(u["episodio"]["titulo"].split(":")[0][:18], self.arco,
                          f"unidad {u['numero']}: el arco no menciona «{u['episodio']['titulo']}»")

    def test_hay_un_dia_cultura_donde_cabe_el_episodio(self):
        """El episodio no añade un día ni un minuto: vive en un día que ya
        existe y que ya no es de gramática nueva."""
        dias = plan.dias(self.cal)
        for u in self.unidades:
            segunda = u["semanas"][1]
            culturales = [d for d in dias if d.semana == segunda and d.tipo == "cultura"]
            self.assertEqual(len(culturales), 1,
                             f"unidad {u['numero']}: la semana {segunda} no tiene un día de cultura")

    def test_el_arco_llega_hasta_el_examen(self):
        """El final del curso es el DELE A2, y la historia tiene que terminar
        ahí: es lo que convierte el examen en el desenlace y no en un trámite."""
        self.assertIn("DELE A2", self.arco)
        ultimo = self.unidades[-1]["episodio"]["sinopsis"]
        self.assertIn("DELE", ultimo, "el último episodio tiene que dejar a Iván en el examen")


class TestLaEntrada(unittest.TestCase):
    """Lo que ve quien llega por primera vez.

    «100 / 365 уроков открыто» es cierto y es lo tercero que se ve, pero se lee
    como «el curso está a medias». El mismo dato en meses contesta la pregunta
    que el visitante sí se hace: ¿me voy a quedar sin curso?"""

    def setUp(self):
        self.cfg = construir_sitio.cargar_config()
        self.textos = construir_sitio.cargar_textos()

    def test_el_ruso_declina_los_meses(self):
        """2-4 piden «месяца» y 5+ «месяцев», con la excepción de 12-14. Un
        «3 месяцев» en la portada delata que el sitio no lo escribió nadie."""
        formas = self.textos["ru"]["portada"]["meses"]
        casos = {100: (3, "месяца"), 120: (4, "месяца"), 150: (5, "месяцев"),
                 365: (12, "месяцев"), 390: (13, "месяцев"), 660: (22, "месяца")}
        for lecciones, espera in casos.items():
            self.assertEqual(construir_sitio.meses_de(lecciones, formas), espera, lecciones)

    def test_el_numero_de_meses_se_calcula_y_no_se_escribe(self):
        """«Más de tres meses» envejecería el día que se escriba la 101."""
        formas = self.textos["es"]["portada"]["meses"]
        self.assertEqual(construir_sitio.meses_de(100, formas)[0], 3)
        self.assertEqual(construir_sitio.meses_de(200, formas)[0], 6)

    def test_con_poco_curso_el_aviso_no_sale(self):
        """Por debajo de 60 lecciones la respuesta honrada a «¿me quedaré sin
        curso?» es que sí, así que no se dice lo contrario."""
        formas = self.textos["ru"]["portada"]["meses"]
        self.assertEqual(construir_sitio.meses_de(30, formas)[0], 2, "nunca baja de 2")

    def test_la_portada_lo_enseña_en_los_tres_idiomas(self):
        """El hueco {n} tiene que quedar relleno EN LA PROSA.

        Los `<script>` se quitan antes de mirar, igual que hace el revisor de
        enlaces rotos desde el 2026-10-26 y por el mismo motivo: el JSON de
        `window.CURSO_TEXTOS` lleva plantillas sin rellenar a propósito —«Шаг
        {n} из {total}», que el navegador rellena al pintar la guía— y un
        buscador de texto las acusaba de ser el hueco de los meses."""
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, self.cfg, self.textos)
        for i in self.textos["idiomas"]:
            carpeta = destino / i["carpeta"] if i["carpeta"] else destino
            bruto = carpeta.joinpath("index.html").read_text(encoding="utf-8")
            portada = re.sub(r"<script\b.*?</script>", "", bruto, flags=re.S)
            self.assertIn('class="progreso-nota"', portada, i["codigo"])
            self.assertNotIn("{n}", portada, f'{i["codigo"]}: quedó el hueco sin rellenar')
            self.assertNotIn("{meses}", portada, i["codigo"])
            # Y la guarda de la guarda: que quitar los <script> no haya dejado
            # la comprobación ciega.
            self.assertIn("{n}", bruto, "la plantilla de la guía tiene que estar en el JSON")

    def test_el_boton_principal_lleva_a_la_primera_leccion(self):
        """La entrada tiene UN camino obvio, y no puede llevar a un 404."""
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, self.cfg, self.textos)
        portada = (destino / "index.html").read_text(encoding="utf-8")
        destino_boton = re.search(r'id="empezar" href="([^"]+)"', portada).group(1)
        self.assertTrue((destino / destino_boton.lstrip("./")).exists(), destino_boton)


class TestLaCabecera(unittest.TestCase):
    """La barra de navegación no cabe en la columna de lectura.

    Con los dos al mismo ancho, en escritorio el título más los tres enlaces
    más los tres idiomas más el botón del tema sumaban ~708 px en una columna
    de 704, y el botón del tema caía a una segunda fila con 700 px de pantalla
    libres al lado. Fallaba por cuatro píxeles, así que solo se vio midiendo
    los hijos en un navegador, no mirando la captura.

    Esto es una comprobación del CSS y no del dibujo: fija la invariante —la
    barra más ancha que el texto— que es lo que impide que vuelva a pasar."""

    def setUp(self):
        self.css = construir_sitio.CSS

    def _rem(self, patron):
        m = re.search(patron, self.css)
        self.assertIsNotNone(m, patron)
        return float(m.group(1))

    def test_la_barra_es_mas_ancha_que_la_columna_de_lectura(self):
        texto = self._rem(r"--ancho:\s*([\d.]+)rem")
        barra = self._rem(r"header\.sitio \.envoltorio\{max-width:([\d.]+)rem\}")
        self.assertGreater(barra, texto,
                           "la cabecera tiene que poder usar más ancho que la prosa")

    def test_la_columna_de_lectura_sigue_siendo_estrecha(self):
        """Ensanchar la barra no puede ensanchar el texto: una línea de prosa
        muy larga se lee peor, y ese era justo el motivo de la columna."""
        texto = self._rem(r"--ancho:\s*([\d.]+)rem")
        self.assertLessEqual(texto, 48, "la prosa no debe pasar de ~48rem")

    def test_el_titulo_solo_crece_en_movil(self):
        """En móvil el título cede espacio y se recorta con puntos suspensivos
        para que el selector de idioma no se salga; en escritorio, si creciera,
        se comería el hueco que la nav reclama con su margen automático."""
        self.assertIn("header.sitio .marca{flex:0 1 auto}", self.css)
        self.assertRegex(self.css, r"header\.sitio \.marca\{[^}]*flex:1 1 auto")


class TestElMapaDeUnidades(unittest.TestCase):
    """24 tarjetas antes de la lista día a día.

    El índice crudo medía 21.482 px de alto —24 pantallas de scroll— y nadie
    navega eso. La idea viene de la referencia que mandó el profesor, que entra
    a cada curso por una tarjeta; lo que se tomó es esa estructura, no su
    aspecto."""

    def setUp(self):
        self.cal = plan.cargar()
        self.textos = construir_sitio.cargar_textos()
        self.destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(self.destino, construir_sitio.cargar_config(), self.textos)

    def _indice(self, carpeta=""):
        return self.destino.joinpath(carpeta, "kurs.html").read_text(encoding="utf-8")

    def test_hay_una_tarjeta_por_unidad(self):
        html_ = self._indice()
        self.assertEqual(html_.count('class="u-tarjeta'), len(self.cal["unidades"]))

    def test_cada_tarjeta_lleva_su_episodio(self):
        """Es donde la historia se ve sin abrir ninguna lección."""
        html_ = self._indice()
        for u in self.cal["unidades"]:
            self.assertIn(html.escape(u["episodio"]["titulo"]), html_, u["numero"])

    def test_una_unidad_escrita_enlaza_a_su_primera_leccion(self):
        """Y una sin escribir no manda a un 404: ancla a su sección de abajo."""
        html_ = self._indice()
        self.assertIn('href="./semana-01/dia-1.html"', html_)
        # Y desde una carpeta de idioma, con el prefijo que toca: las lecciones
        # viven solo en la raíz.
        self.assertIn('href="../semana-01/dia-1.html"', self._indice("es"))
        for destino in re.findall(r'class="u-tarjeta[^"]*" href="([^"]+)"', html_):
            if destino.startswith("#"):
                self.assertIn(f'id="{destino[1:]}"', html_, destino)
            else:
                self.assertTrue((self.destino / destino).exists(), destino)

    def test_las_unidades_sin_lecciones_se_ven_apagadas(self):
        """Prometer una puerta que no abre es peor que enseñarla cerrada.

        Desde que están escritas las 24 unidades (2026-10-28) **el sitio real
        no tiene ni una tarjeta apagada**, así que mirar el índice construido
        dejó de comprobar nada: la prueba pasaba con el mecanismo borrado. Se
        miran las dos cosas por separado, y el mecanismo se mira pasándole al
        generador los días de la unidad 24 apuntando a una semana que no
        existe —o sea, sin lecciones escritas—."""
        self.assertNotIn("u-tarjeta vacia", self._indice(),
                         "las 24 unidades están escritas: no debería quedar ninguna apagada")
        dias = [dataclasses.replace(d, semana=99) if d.unidad == 24 else d
                for d in plan.dias(self.cal)]
        mapa = construir_sitio._mapa_de_unidades(
            self.cal, dias, self.textos["ru"]["curso"], "ru", "")
        self.assertIn("u-tarjeta vacia", mapa)
        self.assertIn('href="#u24"', mapa,
                      "y una unidad sin lecciones ancla a su sección, no a una lección")

    def test_el_mapa_se_sale_de_la_columna_de_prosa(self):
        """Mismo motivo que la cabecera: un mapa no se lee renglón a renglón.
        Encerrado en los 44rem del texto solo caben dos columnas."""
        self.assertRegex(construir_sitio.CSS, r"\.mapa\{[^}]*width:min\(60rem")

    def test_el_pie_de_las_tarjetas_se_alinea_abajo(self):
        """Sin esto, dos tarjetas vecinas enseñan la barra a distinta altura
        según si el título ocupa una línea o dos."""
        self.assertRegex(construir_sitio.CSS, r"\.u-tarjeta \.pie\{[^}]*margin-top:auto")
        self.assertRegex(construir_sitio.CSS, r"\.u-tarjeta\{display:flex;flex-direction:column")

    def test_el_mapa_esta_en_los_tres_idiomas(self):
        for i in self.textos["idiomas"]:
            html_ = self._indice(i["carpeta"])
            self.assertIn('class="mapa"', html_, i["codigo"])
            self.assertIn(html.escape(self.textos[i["codigo"]]["curso"]["mapa"]), html_)


class TestElTestDeNivel(unittest.TestCase):
    """La segunda puerta: por qué lección empezar si ya se sabe algo.

    Hasta ahora el sitio tenía una sola entrada, la lección 1. Quien llega
    sabiendo algo lee «empieza por el alfabeto», decide que esto no es para él
    y se va.

    Lo que estas pruebas vigilan no es el aspecto sino las dos cosas que lo
    romperían en silencio: que la recomendación apunte a una lección que no
    existe —el fallo que esta suite ya cazó dos veces— y que la explicación del
    error le llegue al lector en un idioma que no lee."""

    def setUp(self):
        self.preguntas = construir_sitio.cargar_test()
        self.lista = self.preguntas["preguntas"]
        self.destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(self.destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        self.pagina = (self.destino / "test.html").read_text(encoding="utf-8")

    def _datos(self):
        m = re.search(r"window\.CURSO_TEST=(\{.*?\});\(function", self.pagina, re.S)
        self.assertIsNotNone(m, "la página no lleva los datos del test")
        return json.loads(m.group(1))

    # ---- las preguntas
    def test_cada_pregunta_apunta_a_una_unidad_que_existe(self):
        unidades = {u["numero"] for u in CAL["unidades"]}
        for q in self.lista:
            self.assertIn(q["unidad"], unidades, q["pregunta"])

    def test_van_en_orden_de_unidad(self):
        """De esto depende la recomendación entera: se empieza en la unidad de
        la PRIMERA fallada, o sea donde se acaba lo que ya se sabe. Desordenadas,
        fallar la última pregunta podría colocar a alguien antes que fallar la
        primera."""
        unidades = [q["unidad"] for q in self.lista]
        self.assertEqual(unidades, sorted(unidades), unidades)

    def test_el_navegador_recibe_un_grupo_por_unidad_y_en_orden(self):
        """El test varía porque de cada unidad se escoge una pregunta al azar.
        Lo que NO puede variar es el orden de los grupos: la recomendación sale
        de la unidad de la primera fallada."""
        grupos = self._datos()["grupos"]
        unidades = [g[0]["unidad"] for g in grupos]
        self.assertEqual(unidades, sorted(unidades), unidades)
        self.assertEqual(len(unidades), len(set(unidades)), "una unidad en dos grupos")
        for g in grupos:
            self.assertEqual(len({q["unidad"] for q in g}), 1, "grupo con dos unidades")

    def test_hay_mas_de_una_pregunta_por_unidad(self):
        """Es lo que hace que el test varíe. Con una sola por unidad vuelve a
        ser siempre el mismo test, y nadie se daría cuenta leyendo el código:
        seguiría funcionando igual de bien la primera vez."""
        for g in self._datos()["grupos"]:
            self.assertGreaterEqual(len(g), 2, f"unidad {g[0]['unidad']}: una sola variante")

    def test_las_variantes_de_una_unidad_no_repiten_el_mismo_error(self):
        """Repetir el test tiene que enseñar algo nuevo, no premiar la memoria
        de la pantalla anterior. Dos variantes con el mismo error serían la
        misma pregunta con otras palabras."""
        for g in self._datos()["grupos"]:
            for clave in ("pregunta", "error"):
                vistos = [q[clave] for q in g]
                self.assertEqual(len(vistos), len(set(vistos)),
                                 f"unidad {g[0]['unidad']}: {clave} repetido")

    def test_agrupar_ordena_por_unidad_aunque_el_fichero_no_lo_esté(self):
        grupos = construir_sitio.grupos_por_unidad([
            {"unidad": 5, "pregunta": "b", "opciones": [], "correcta": 0, "error_ru": "x"},
            {"unidad": 2, "pregunta": "a", "opciones": [], "correcta": 0, "error_ru": "y"},
            {"unidad": 5, "pregunta": "c", "opciones": [], "correcta": 0, "error_ru": "z"},
        ])
        self.assertEqual([[q["pregunta"] for q in g] for g in grupos], [["a"], ["b", "c"]])

    def test_barajar_copia_la_pregunta_y_recalcula_la_correcta(self):
        """Barajando sobre el original, la segunda partida encontraría las
        opciones ya movidas y `correcta` apuntando a otra cosa: le diría «has
        fallado» a quien acertó. Comprobado además en navegador, jugando una
        partida entera y pulsando siempre el botón cuyo TEXTO es el correcto."""
        js = construir_sitio.TEST_JS
        self.assertIn("q.opciones.slice()", js)
        self.assertIn("orden.indexOf(q.correcta)", js)
        # Y se reparte de nuevo al empezar y al repetir, que es donde se nota.
        self.assertEqual(js.count("repartir()"), 3)

    def test_la_respuesta_correcta_es_una_de_las_opciones_y_no_se_repite(self):
        for q in self.lista:
            self.assertGreaterEqual(len(q["opciones"]), 3, q["pregunta"])
            self.assertIn(q["correcta"], range(len(q["opciones"])), q["pregunta"])
            self.assertEqual(len(set(q["opciones"])), len(q["opciones"]),
                             f"dos opciones iguales en «{q['pregunta']}»")

    def test_el_error_esta_en_los_dos_idiomas_y_ninguno_vacio(self):
        """`error_ru` lo lee el alumno; `error_es` es la regla que revisa el
        profesor, que es quien aprueba (regla 6) y lee en español."""
        for q in self.lista:
            for clave in ("error_ru", "error_es"):
                self.assertTrue((q.get(clave) or "").strip(), f"{clave} en «{q['pregunta']}»")

    def test_al_navegador_va_el_ruso_y_no_el_espanol(self):
        """La primera versión mandaba la explicación en español, que es justo el
        idioma que el lector viene a aprender: explicarle su error ahí no le
        enseña nada."""
        for q in self.lista:
            self.assertIn(q["error_ru"], self.pagina, q["pregunta"])
            self.assertNotIn(q["error_es"], self.pagina, q["pregunta"])

    # ---- la recomendación
    def test_cada_inicio_de_unidad_es_una_leccion_que_existe(self):
        datos = self._datos()
        for unidad, d in datos["inicios"].items():
            self.assertTrue((self.destino / d["url"]).exists(), f"unidad {unidad}: {d['url']}")
        self.assertTrue((self.destino / datos["ultima"]["url"]).exists())

    def test_solo_se_listan_las_unidades_que_tienen_leccion_escrita(self):
        """Las demás caen en la última escrita de una unidad, que es la
        respuesta honrada: si ya sabe todo lo que el curso cubre, ahí es donde
        empieza.

        Y los días SIN unidad no cuentan: las semanas 49-52 son la fase final y
        la 53 el día de reserva. Esta prueba se puso en rojo al escribirlas
        —`int("null")`— y tenía razón: el generador estaba publicando una clave
        `null` en los datos del test."""
        datos = self._datos()
        escritas = {d.unidad for d in construir_sitio.escritas(CAL)
                    if d.unidad is not None}
        self.assertEqual({int(u) for u in datos["inicios"]}, escritas)
        self.assertNotIn("null", datos["inicios"],
                         "la fase final no es una unidad: no puede salir en los inicios")

    def test_la_ultima_del_test_de_nivel_no_es_el_dia_de_reserva(self):
        """A quien acierta las catorce se le manda a `ultima`, y con el curso
        entero la última lección escrita era el **día 365**, que es el de
        reserva: una página que dice que hoy no hay nada que hacer. El destino
        tiene que ser la última lección de una unidad."""
        datos = self._datos()
        n = datos["ultima"]["n"]
        d = plan.por_numero(CAL, n)
        self.assertIsNotNone(d.unidad, f"el día {n} no pertenece a ninguna unidad")
        self.assertNotEqual(d.tipo, "reserva")
        self.assertTrue((self.destino / datos["ultima"]["url"]).exists())

    def test_el_inicio_es_la_primera_leccion_de_la_unidad_y_no_una_del_medio(self):
        inicios = construir_sitio.inicios_de_unidad(CAL)
        for d in construir_sitio.escritas(CAL):
            self.assertLessEqual(inicios[d.unidad]["n"], d.numero, d.numero)

    def test_el_resultado_cae_en_la_ultima_escrita_cuando_la_unidad_no_existe(self):
        """Sin el `|| D.ultima`, fallar en una unidad aún no escrita dejaba la
        pantalla de resultado sin su botón."""
        self.assertIn("(u&&D.inicios[u])||D.ultima", construir_sitio.TEST_JS)

    # ---- la página
    def test_hay_un_solo_test_y_esta_en_ruso(self):
        """Las catorce preguntas son frases rusas que hay que decir en español:
        un lector que no lee ruso no puede contestarlas. Traducir la interfaz
        alrededor dejaría un test que no se puede hacer."""
        self.assertFalse((self.destino / "es" / "test.html").exists())
        self.assertFalse((self.destino / "en" / "test.html").exists())
        self.assertNotIn('rel="alternate"', self.pagina)

    def test_el_enlace_si_esta_en_los_tres_idiomas(self):
        """Igual que la portada en español manda a una lección en ruso."""
        for carpeta, raiz in (("", "."), ("es", ".."), ("en", "..")):
            for hoja in ("index.html", "kurs.html"):
                p = self.destino.joinpath(carpeta, hoja).read_text(encoding="utf-8")
                self.assertIn(f'<a href="{raiz}/test.html">', p, f"{carpeta}/{hoja}")
                self.assertIn('class="puerta"', p, f"{carpeta}/{hoja}")

    def test_el_pie_de_todas_las_paginas_lleva_al_test(self):
        leccion = (self.destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn('<a href="../test.html">', leccion)

    def test_mientras_no_este_revisado_la_pagina_lo_avisa(self):
        """Regla 6: nada generado se publica como bueno sin el profesor."""
        if not self.preguntas.get("revisado"):
            textos = construir_sitio.cargar_textos()
            self.assertIn(html.escape(textos["ru"]["test"]["borrador"]), self.pagina)

    def test_el_boton_nace_oculto_y_lo_enciende_el_navegador(self):
        """Sin JavaScript sería un botón que no hace nada; para ese caso está el
        <noscript>, que manda a la lección 1."""
        self.assertIn('id="test-arranque" hidden', self.pagina)
        self.assertIn("arranque.hidden=false", construir_sitio.TEST_JS)
        self.assertIn("<noscript>", self.pagina)

    def test_sin_fichero_de_preguntas_el_sitio_se_construye_igual(self):
        """El test es una puerta de más, no el curso. Un sitio que no se
        construye por una puerta de más sería mucho peor."""
        otro = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(otro, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos(), preguntas={})
        pagina = (otro / "test.html").read_text(encoding="utf-8")
        self.assertNotIn("window.CURSO_TEST", pagina)
        self.assertIn("<noscript>", pagina)
        self.assertEqual(revisar_adsense.enlaces_rotos(otro), [])

    # ---- el cronómetro
    def test_el_cronometro_es_por_pregunta_y_viaja_al_navegador(self):
        """Por pregunta y no global: un reloj para todo el test solo mete
        prisa, y lo que hace falta es que no dé tiempo a buscar la respuesta en
        el diccionario. Quien lo busca queda colocado más adelante de lo que
        sabe y se pierde en la primera lección."""
        self.assertEqual(self._datos()["segundos"],
                         self.preguntas["segundos_por_pregunta"])
        self.assertGreater(self.preguntas["segundos_por_pregunta"], 0)

    def test_al_agotarse_cuenta_como_fallada_y_pasa(self):
        """`responder(-1)` es «se acabó el tiempo», y entra en `fallos` como
        cualquier otra: para colocar a alguien, lo que no sabe en treinta
        segundos no lo sabe."""
        self.assertIn("responder(-1)", construir_sitio.TEST_JS)
        self.assertIn("tarde:true", construir_sitio.TEST_JS)

    def test_se_puede_apagar_desde_el_yaml_sin_tocar_codigo(self):
        """El profesor ajusta los segundos —o los pone a 0— sin que nadie
        tenga que abrir el generador."""
        self.assertIn("if(!D.segundos)return", construir_sitio.TEST_JS)
        datos = {"preguntas": self.lista, "segundos_por_pregunta": 0}
        otro = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(otro, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos(), preguntas=datos)
        pagina = (otro / "test.html").read_text(encoding="utf-8")
        m = re.search(r"window\.CURSO_TEST=(\{.*?\});\(function", pagina, re.S)
        self.assertEqual(json.loads(m.group(1))["segundos"], 0)

    def test_el_reloj_se_para_al_contestar_y_al_terminar(self):
        """Sin pararlo, el de la pregunta anterior seguiría corriendo y
        mandaría un `responder(-1)` encima de la siguiente."""
        self.assertIn("function responder(n){\n    parar();", construir_sitio.TEST_JS)
        self.assertIn("function resultado(){\n    parar();", construir_sitio.TEST_JS)

    def test_el_test_esta_en_el_sitemap_una_sola_vez(self):
        cfg = dict(construir_sitio.cargar_config(), dominio="https://ejemplo.com")
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, cfg, construir_sitio.cargar_textos())
        mapa = (destino / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(mapa.count("/test.html</loc>"), 1)


class TestLaGuiaDeLaLeccion(unittest.TestCase):
    """Los seis pasos de los 30 minutos, visibles mientras se lee.

    Lo pidió el profesor: «que sea un aprendizaje intuitivo, colocar algo más
    guiado». Una lección es una página larga con seis apartados y sus franjas
    de minutos escritas en los títulos, y hasta ahora el alumno tenía que ir
    encontrándolos solo. Esto no añade materia: hace visible la que ya estaba.

    Los pasos salen de los PROPIOS títulos y no de una lista en el código. Una
    lista se queda vieja el día que un tipo de día use otros apartados —los de
    examen, simulacro y proyecto ya lo hacen— y el síntoma sería una guía que
    señala donde no es."""

    # La misma expresión que usa el guion, traducida: «## 3. Новое (6–16 мин)».
    FRANJA = re.compile(r"^\s*(\d+)\.\s*(.+?)\s*\((\d+)\s*[–—-]\s*(\d+)\s*мин\)\s*$")

    def test_cada_leccion_lleva_su_hueco_y_nace_oculto(self):
        """Sin JavaScript la página se queda exactamente como estaba: los seis
        títulos con sus franjas, que es la versión que vale."""
        paginas = sorted((RAIZ / "docs").glob("semana-*/dia-*.html"))
        if not paginas:
            self.skipTest("el sitio no está construido")
        for ruta in paginas[:40]:
            with self.subTest(pagina=ruta.parent.name + "/" + ruta.name):
                self.assertIn('<div id="guia" class="guia" hidden>', ruta.read_text(encoding="utf-8"))
        # y en ninguna otra página: la guía es de las lecciones
        for otra in ("index.html", "kurs.html", "test.html"):
            self.assertNotIn('id="guia"', (RAIZ / "docs" / otra).read_text(encoding="utf-8"))

    def test_los_pasos_salen_de_los_titulos_de_cada_tipo_de_dia(self):
        """Cada tipo de día tiene sus propios apartados y todos tienen que dar
        al menos tres pasos; con menos, el guion no dibuja nada y la página se
        queda como está, que es el fallo seguro."""
        vistos = {}
        for ruta in sorted((RAIZ / "curso").glob("semana-*/dia-*.md")):
            datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
            pasos = [m for linea in cuerpo.splitlines()
                     if linea.startswith("## ") and (m := self.FRANJA.match(linea[3:]))]
            vistos.setdefault(datos["tipo"], []).append(len(pasos))
        self.assertGreaterEqual(len(vistos), 5, f"tipos vistos: {sorted(vistos)}")
        for tipo, cuentas in sorted(vistos.items()):
            with self.subTest(tipo=tipo):
                self.assertGreaterEqual(min(cuentas), 3,
                                        f"{tipo}: algún día da menos de tres pasos")

    def test_el_tope_pegajoso_se_mide_y_no_se_escribe(self):
        """La cabecera es pegajosa a partir de 40rem, así que la guía va debajo
        de ella. Su alto lo mide el guion y lo deja en --alto-cabecera: escrito
        a mano se quedaría viejo el día que cambie el menú, y el síntoma sería
        la guía tapada —que es justo lo que ya pasó con la barra en octubre—."""
        self.assertIn("--alto-cabecera", construir_sitio.GUIA_JS)
        self.assertIn("top:var(--alto-cabecera,0px)", construir_sitio.CSS.replace(" ", ""))
        self.assertIn("GUIA_JS", (RAIZ / "scripts" / "construir_sitio.py").read_text(encoding="utf-8"))

    def test_el_guion_llega_al_navegador(self):
        js = (RAIZ / "docs" / "progreso.js").read_text(encoding="utf-8")
        self.assertIn("guia-barra", js)
        self.assertIn("--alto-cabecera", js)


class TestElNavegador(unittest.TestCase):
    """Lo único que caza un ReferenceError.

    Todo lo que este proyecto da por «comprobado en navegador» se comprobó a
    mano, una vez, y nunca más: no había ni una prueba que abriera Chromium.
    Así vivió el fallo del 2026-10-28, que es el peor que había: el test de
    unidad **no funcionaba desde el día que se publicó**. `pregunta()` leía una
    variable `preguntas` que nadie declaraba, así que al pulsar «empezar» el
    papel se escondía y en su lugar no salía nada. El lector en Python estaba
    probado, el JSON llegaba bien a la página y el HTML tenía las etiquetas
    correctas: las tres cosas que la suite miraba. Lo que faltaba era pulsar.

    `scripts/probar_navegador.js` abre las páginas, contesta los tests
    eligiendo la opción correcta **por su texto** y exige cero errores de JS.
    Elegir por posición sería repetir la cuenta del propio generador."""

    GUION = RAIZ / "scripts" / "probar_navegador.js"

    def test_las_paginas_se_usan_sin_un_solo_error_de_js(self):
        if not (RAIZ / "docs" / "index.html").exists():
            self.skipTest("el sitio no está construido")
        try:
            r = subprocess.run(["node", str(self.GUION)], cwd=RAIZ, capture_output=True,
                               text=True, timeout=300)
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.skipTest(f"sin navegador en este entorno: {e}")
        if "Cannot find module" in r.stderr or "Executable doesn" in r.stderr:
            self.skipTest("playwright o Chromium no están disponibles")
        paginas = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        self.assertTrue(paginas, f"el guion no dijo nada:\n{r.stderr[-800:]}")
        for pag in paginas:
            with self.subTest(pagina=pag["pagina"]):
                self.assertEqual(pag["errores"], [], "errores de JavaScript")
                if pag.get("guia"):
                    self.assertTrue(pag["guia_avanza"],
                                    f'la guía no avanza: {pag.get("guia_recorrido")}')
                if pag["test"]:
                    self.assertEqual(pag["aciertos"], pag["test"],
                                     "no se pudieron contestar todas")
                    self.assertTrue(pag["dice_todo_bien"], pag.get("resultado"))
                    self.assertTrue(pag["papel_escondido"],
                                    "la versión en papel tenía que esconderse")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_el_guion_del_test_declara_lo_que_usa(self):
        """La guarda barata, para cuando no hay navegador: `PRUEBA_JS` no puede
        leer `preguntas` sin declararla, que es exactamente lo que pasó."""
        # Sin los comentarios: el código explica por qué NO llama a `repartir()`,
        # y un buscador de palabras acusaría a la explicación.
        js = re.sub(r"^\s*//.*$", "", construir_sitio.PRUEBA_JS, flags=re.M)
        self.assertIn("var preguntas=", js)
        self.assertLess(js.index("var preguntas="), js.index("preguntas[i]"),
                        "se usa antes de declararse")
        # `repartir()` es del test de nivel, que escoge una variante de cada
        # grupo; aquí las quince preguntas son siempre las mismas y llamarlo
        # volvería a romper el botón de «otra vez».
        self.assertNotIn("repartir()", js)


class TestLaPruebaDeUnidad(unittest.TestCase):
    """Los días `prueba` se pueden contestar, no solo leer.

    El calendario tiene 23, uno al cerrar cada unidad, con 15 preguntas y su
    clave que el profesor ya escribió y revisó. Aquí no se inventa ninguna: se
    leen de la propia lección, que es la única fuente de verdad.

    Lo que estas pruebas vigilan es lo único que haría daño de verdad: que una
    respuesta quede mal mapeada y la web le diga a alguien que acertó cuando
    falló."""

    def setUp(self):
        self.cal = plan.cargar()
        self.dias = [d for d in plan.dias(self.cal) if d.tipo == "prueba" and d.ruta.exists()]

    # ---- el analizador
    def test_las_respuestas_salen_igual_que_en_la_clave_del_profesor(self):
        """Si el analizador leyera otra letra, el test corregiría mal y nadie
        se enteraría.

        La clave se vuelve a leer aquí con una expresión regular propia y se
        compara con lo que devolvió `pruebas.leer`. **No se fija la secuencia
        literal**: la primera versión guardaba «бвбббавбгббабвв» para la
        semana 2, y el día que se repartieron las respuestas correctas de los
        quince tests —porque catorce de quince eran la б y marcar todo б
        aprobaba la unidad— se puso en rojo sin que el analizador tuviera nada
        que ver. Una prueba que fija el CONTENIDO de un fichero de datos se
        rompe cada vez que ese fichero cambia por una razón legítima, y
        entonces se afloja. Esta comprueba la relación, que es lo que importa:
        la letra de la clave y la opción marcada tienen que ser la misma
        posición, en los quince tests y no solo en uno."""
        for ruta in sorted((RAIZ / "curso").glob("semana-*/dia-6.md")):
            datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
            if datos.get("tipo") != "prueba":
                continue
            preguntas = pruebas.leer(cuerpo)
            self.assertIsNotNone(preguntas, ruta.parent.name)
            # la clave, leída otra vez y por otro camino
            clave = cuerpo.split("## Ответы", 1)[1]
            bloques = re.split(r"\*\*\d+\.\s*[^*]+?:\*\*", clave)[1:]
            letras = []
            for bloque in bloques:
                bloque = re.sub(r"\n(?!\n)", " ", bloque).split("\n\n")[0]
                letras += [m[1] for m in pruebas.RESPUESTA.findall(bloque)]
            self.assertEqual(len(letras), len(preguntas), ruta.parent.name)
            for i, (letra, q) in enumerate(zip(letras, preguntas), 1):
                self.assertEqual(pruebas.LETRAS[q.correcta], letra,
                                 f"{ruta.parent.name}, pregunta {i}")

    def test_la_letra_correcta_esta_repartida(self):
        """Un test donde 14 de 15 respuestas son la б) no mide nada: marcando
        todo б se saca 14/15 y se «aprueba» la unidad. Y desde que `pruebas.py`
        los hace contestables en la web, el alumno se puntúa con eso.

        Tampoco vale el reparto perfecto а-б-в-г-а-б-в-г, que fue la primera
        corrección: equilibrado en el recuento y trivial de aprender. Por eso
        aquí se exige además que no haya tres iguales seguidos ni una escalera
        ascendente completa.

        Y se recorren los TRES tipos que tienen preguntas con clave, no solo
        los tests de unidad. La corrección de 2026-10-27 arregló los quince
        `prueba` y dejó fuera los mini-tests de repaso —que son contestables en
        la web desde el 28— y los dos exámenes de nivel. Medido entonces: 23 de
        los 23 mini-tests legibles estaban mal, uno con 14 de 15 respuestas en
        la б), y el examen de A1 tenía 27 de 45, que es exactamente el 60 % con
        el que se aprueba el nivel: marcando todo б se pasaba a A2 sin saber
        nada. Los días de la fase final no tienen unidad, así que esto recorre
        el calendario y no un glob de `dia-6.md`."""
        dias = [d for d in plan.dias(plan.cargar())
                if d.tipo in ("prueba", "repaso", "examen") and d.ruta.exists()]
        self.assertGreaterEqual(len(dias), 38)
        mirados = 0
        for d in dias:
            preguntas = pruebas.de_la_leccion(d.ruta)
            if not preguntas:
                continue    # los repasos que piden escribir la forma, no elegir
            mirados += 1
            donde = f"{d.ruta.parent.name}/{d.ruta.stem} ({d.tipo})"
            idx = [q.correcta for q in preguntas]
            veces = Counter(idx)
            self.assertLessEqual(max(veces.values()), len(idx) * 0.45,
                                 f"{donde}: la letra más repetida se lleva "
                                 f"{max(veces.values())} de {len(idx)}")
            self.assertFalse(any(idx[i] == idx[i+1] == idx[i+2] for i in range(len(idx)-2)),
                             f"{donde}: tres respuestas seguidas con la misma letra")
            self.assertFalse(all((idx[i]+1) % 4 == idx[i+1] for i in range(len(idx)-1)),
                             f"{donde}: la secuencia es el ciclo а-б-в-г")
            # Y ninguna escalera de tres —абв o вба seguidas—, que es el
            # reparto que más se cuela porque en la clave, leída número a
            # número, no se ve.
            #
            # Solo donde los ítems tienen TRES opciones, y eso no es para que
            # la prueba pase: con tres, абв son las tres letras en orden, o sea
            # un patrón completo y visible; con cuatro son tres de cuatro y no
            # predicen la г). Medido: trece de los veintitrés tests de unidad
            # —que son de cuatro opciones— tienen una, que es más o menos lo
            # que da el azar en quince ítems, y reordenarlos no ganaría nada.
            if all(len(q.opciones) == 3 for q in preguntas):
                escaleras = [i + 1 for i in range(len(idx) - 2)
                             if idx[i:i+3] in ([0, 1, 2], [2, 1, 0])]
                self.assertFalse(escaleras,
                                 f"{donde}: escalera de tres letras en el ítem "
                                 f"{escaleras[:1]}")
        self.assertGreaterEqual(mirados, 38,
                                "se están mirando menos días de los que tienen clave")

    def test_el_examen_final_repite_los_cuarenta_del_examen_de_a1(self):
        """El examen de A1 (нед. 22, день 6) acaba prometiendo que dentro de un
        año se pasará el MISMO examen otra vez, y que «la diferencia entre las
        dos hojas es la única nota que significa algo». El examen final cumple
        esa promesa: sus ítems 1-40 son los 40 del bloque 1 de aquél, con las
        mismas opciones en el mismo orden y la misma respuesta.

        Hay que fijarlo porque se rompe en silencio: el día que alguien
        reparta las letras de uno de los dos y no del otro, las dos hojas
        dejan de poder compararse y las dos lecciones siguen diciendo que sí.
        Pasó de verdad el 2026-10-28 —el reparto del examen de A1— y por eso
        el final se escribió DESPUÉS y copiando."""
        a1 = validar.frontmatter(
            (RAIZ / "curso" / "semana-22" / "dia-6.md").read_text(encoding="utf-8"))[1]
        fin = validar.frontmatter(
            (RAIZ / "curso" / "semana-52" / "dia-6.md").read_text(encoding="utf-8"))[1]
        qa, qb = pruebas.leer_examen(a1), pruebas.leer_examen(fin)
        self.assertIsNotNone(qa, "el examen de A1 dejó de poder leerse")
        self.assertIsNotNone(qb, "el examen final dejó de poder leerse")
        self.assertGreaterEqual(len(qa), 40)
        self.assertEqual(len(qb), 60, "el examen final son 60 ítems")
        for i in range(40):
            with self.subTest(item=i + 1):
                self.assertEqual(qa[i].enunciado, qb[i].enunciado)
                self.assertEqual(qa[i].opciones, qb[i].opciones)
                self.assertEqual(qa[i].correcta, qb[i].correcta)

    def test_los_minitests_de_repaso_se_leen(self):
        """El Мини-тест del sábado de repaso tiene la MISMA forma que un test de
        unidad —enunciado, tres opciones, clave— y se quedó fuera cuando los
        tests de unidad se hicieron contestables (2026-10-27), porque sus
        opciones van detrás de una flecha en la misma línea y su clave dice
        «(день N)» en vez de «(нед. N, день N)». El resultado era una casilla
        para escribir donde deberían salir tres botones, y así lo vio el
        profesor usando el sitio."""
        # No sólo los sábados: la unidad 11 (el cierre de A1) tiene cinco días
        # de repaso entre semana, y el de la captura del profesor era uno de
        # ellos (semana 21, día 1). Por eso se recorren TODOS los días de tipo
        # repaso y no los `dia-6.md`.
        repasos = [r for r in sorted((RAIZ / "curso").glob("semana-*/dia-*.md"))
                   if validar.frontmatter(r.read_text(encoding="utf-8"))[0].get("tipo") == "repaso"]
        self.assertGreaterEqual(len(repasos), 23)
        sin_leer = {r.parent.name + "/" + r.stem for r in repasos
                    if not pruebas.de_la_leccion(r)}
        # No se fija cuántos se leen —ese número sube con cada unidad nueva y
        # la prueba se rompería sola—, sino CUÁLES no. Estos cuatro no son de
        # opción múltiple: piden escribir la forma del verbo, así que sus
        # casillas son lo correcto y `leer_minitest` devuelve None. Si mañana
        # aparece otro en esta lista, es que un mini-test de opción múltiple
        # dejó de leerse, y eso sí hay que mirarlo.
        self.assertEqual(sin_leer, {"semana-09/dia-6", "semana-29/dia-6",
                                    "semana-31/dia-6", "semana-33/dia-6"},
                         "cambió qué mini-tests no se pueden leer")

    def test_un_minitest_de_produccion_no_se_convierte(self):
        """La semana 33 pide escribir las formas del futuro, sin opciones. Ahí
        `leer_minitest` tiene que devolver None: inventarle opciones sería
        corregir lo que nadie eligió."""
        ruta = RAIZ / "curso" / "semana-33" / "dia-6.md"
        self.assertIsNone(pruebas.de_la_leccion(ruta))

    def test_la_clave_del_minitest_casa_con_las_opciones(self):
        """Se vuelve a leer la clave con una expresión propia y se compara con
        lo que devolvió `leer_minitest`: lo que se comprueba es la RELACIÓN, no
        el contenido de ningún fichero, que es la lección del 2026-10-27."""
        letras = "абвгд"
        clave_re = re.compile(r"\*\*Мини-тест:?\*\*(.*?)(?=\n\n|\Z)", re.S)
        suelta = re.compile(r"\b(\d+)\s*[—–-]?\s*\*{0,2}([абвгд])\*{0,2}(?!\w)")
        vistos = 0
        for ruta in sorted((RAIZ / "curso").glob("semana-*/dia-*.md")):
            datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
            if datos.get("tipo") != "repaso":
                continue
            preguntas = pruebas.leer_minitest(cuerpo, semana=datos["semana"])
            if not preguntas:
                continue
            vistos += 1
            bruto = clave_re.search(cuerpo)
            esperado = [letras.index(l) for _, l in suelta.findall(" ".join(bruto.group(1).split()))]
            self.assertEqual([q.correcta for q in preguntas], esperado, ruta.parent.name)
            for q in preguntas:
                self.assertIn(q.correcta, range(len(q.opciones)), q.enunciado)
                self.assertEqual(len(set(q.opciones)), len(q.opciones),
                                 f"dos opciones iguales: {q.enunciado}")
                self.assertTrue(q.enunciado and not q.enunciado.endswith("→"), q.enunciado)
        # Lo que se comprueba es la RELACIÓN entre la clave y las opciones, no
        # cuántos hay: ese número crece con cada unidad.
        self.assertGreaterEqual(vistos, 19)

    def test_una_clave_de_minitest_que_no_cuadra_lo_deja_como_esta(self):
        """Fallo seguro: si sobra una respuesta, esa página se queda con sus
        casillas en vez de corregir mal.

        La avería se DERIVA del fichero y no se escribe a mano: la primera
        versión rompía la clave con un `.replace("**Мини-тест:** 1 б", …)`, y el
        día que se repartieron las letras de los mini-tests —porque veintitrés
        de veintitrés estaban desequilibrados— ese `replace` se quedó en nada y
        la prueba comprobaba un fichero intacto. Es el mismo error que ya se
        corrigió en `test_una_clave_que_no_cuadra_no_genera_test`."""
        ruta = RAIZ / "curso" / "semana-05" / "dia-6.md"
        datos, cuerpo = validar.frontmatter(ruta.read_text(encoding="utf-8"))
        self.assertIsNotNone(pruebas.leer_minitest(cuerpo, semana=5))
        marca = pruebas.CLAVE_MINI.search(cuerpo)
        self.assertIsNotNone(marca, "la clave del mini-test cambió de forma")
        # una respuesta de más delante de la primera: sobra una y no se lee
        primera = pruebas.RESPUESTA_MINI.search(marca.group(1))
        self.assertIsNotNone(primera)
        corte = marca.start(1) + primera.start()
        roto = cuerpo[:corte] + "0 а · " + cuerpo[corte:]
        self.assertNotEqual(roto, cuerpo)
        self.assertIsNone(pruebas.leer_minitest(roto, semana=5))

    def test_las_siete_pruebas_escritas_se_leen(self):
        """Dos no se leían al principio: en la unidad 4 una opción es una
        transcripción fonética con su propio «·» dentro, y en la unidad 5 las
        opciones se parten entre dos renglones. Por eso se corta por el
        marcador «а)» y no por el punto."""
        for d in self.dias:
            with self.subTest(unidad=d.unidad):
                self.assertIsNotNone(pruebas.de_la_leccion(d.ruta),
                                     f"la unidad {d.unidad} dejó de poder leerse")

    def test_la_respuesta_correcta_esta_entre_las_opciones(self):
        for d in self.dias:
            for q in pruebas.de_la_leccion(d.ruta):
                self.assertIn(q.correcta, range(len(q.opciones)), f"unidad {d.unidad}")
                self.assertGreaterEqual(len(q.opciones), 2, q.enunciado)
                self.assertEqual(len(set(q.opciones)), len(q.opciones),
                                 f"dos opciones iguales: {q.enunciado}")

    def test_una_clave_que_no_cuadra_no_genera_test(self):
        """El fallo seguro: antes que corregir mal, no ofrecer el test.

        La avería se DERIVA del fichero, no se escribe a mano. La primera
        versión fijaba las letras de la semana 2 («5 б … · 6 а», «1. Лексика:
        1 б») y el día que se repartieron las respuestas correctas de los
        quince tests esas cadenas dejaron de existir: los dos `.replace()` se
        quedaron en nada y el test comprobaba un fichero intacto. Se puso en
        rojo, que es lo que había que hacer, pero por entonces ya no medía lo
        que dice. Por eso cada paso exige además que la avería se haya
        aplicado de verdad."""
        bueno = (RAIZ / "curso" / "semana-02" / "dia-6.md").read_text(encoding="utf-8")
        _, cuerpo = validar.frontmatter(bueno)
        self.assertIsNotNone(pruebas.leer(cuerpo))

        clave = cuerpo.split("## Ответы", 1)[1]
        respuestas = pruebas.RESPUESTA.findall(clave)
        self.assertGreaterEqual(len(respuestas), 2)

        # una respuesta de menos en el primer bloque
        ultima = pruebas.RESPUESTA.search(clave, clave.index(f"{respuestas[-1][0]} "))
        primeras = list(pruebas.RESPUESTA.finditer(clave))
        quitar = primeras[len(respuestas) // 3 - 1]          # la última del bloque 1
        roto = cuerpo.replace(quitar.group(0), "", 1)
        self.assertNotEqual(roto, cuerpo, "la avería no se aplicó")
        self.assertIsNone(pruebas.leer(roto))

        # una letra que no está entre las opciones
        uno = primeras[0]
        roto = cuerpo.replace(uno.group(0), uno.group(0).replace(uno.group(2), "д", 1), 1)
        self.assertNotEqual(roto, cuerpo, "la avería no se aplicó")
        self.assertIsNone(pruebas.leer(roto))

        # y sin clave no hay test
        self.assertIsNone(pruebas.leer(cuerpo.split("## Ответы")[0]))

    # ---- la página
    def test_la_pagina_esconde_el_papel_y_ofrece_el_test(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        prueba = (destino / "semana-02" / "dia-6.html").read_text(encoding="utf-8")
        for marca in ('id="prueba"', 'id="prueba-papel"', 'id="prueba-clave"',
                      'id="prueba-empezar"', "window.CURSO_PRUEBA"):
            self.assertIn(marca, prueba, marca)
        # Sin JavaScript la página se queda como estaba: las preguntas siguen
        # en el HTML y es el guion el que las esconde.
        self.assertIn("De nada", prueba)
        self.assertIn("papel.hidden=true", construir_sitio.PRUEBA_JS)

        # y una lección normal no lleva nada de esto
        normal = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertNotIn("window.CURSO_PRUEBA", normal)
        self.assertNotIn('id="prueba"', normal)

    def test_los_enlaces_del_resultado_llevan_a_lecciones_que_existen(self):
        """Van dentro del JSON de un <script>, así que el revisor de enlaces
        rotos NO los mira: desde que salta los scripts, hay que comprobarlos
        aquí o no los comprueba nadie."""
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        total = 0
        for d in self.dias:
            pagina = (destino / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html").read_text(encoding="utf-8")
            m = re.search(r"window\.CURSO_PRUEBA=(\{.*?\});\(function", pagina, re.S)
            self.assertIsNotNone(m, f"unidad {d.unidad}")
            for q in json.loads(m.group(1))["preguntas"]:
                if "url" in q:
                    total += 1
                    destino_q = (destino / f"semana-{d.semana:02d}" / q["url"]).resolve()
                    self.assertTrue(destino_q.exists(), f"unidad {d.unidad}: {q['url']}")
        self.assertGreater(total, 50, "la clave dice de qué lección sale cada respuesta")


if __name__ == "__main__":
    unittest.main()


class TestLasImagenesDelVocabulario(unittest.TestCase):
    """`generar_imagenes.py`: dibuja los sustantivos del vocabulario.

    Las 976 entradas no se pueden dibujar: 505 son saludos, adjetivos y
    palabras funcionales —«hola», «muy», «mi/mis», «mayor»— y de las que
    llevan artículo hay que quitar los abstractos. Lo que estas pruebas fijan
    es ese filtro y la llave de la cache, que es donde esto cuesta dinero."""

    def test_la_variante_americana_no_se_pega_a_la_de_espana(self):
        """El 🌎 separa las dos formas: «la carta 🌎 el menú». Quitándolo sin
        partir salía «la carta el menú», que no es ninguna palabra y se habría
        pagado un dibujo de ella. Se queda la PRIMERA, que por la regla 8 es la
        más extendida y la que el curso enseña."""
        self.assertEqual("la carta", generar_imagenes.limpiar("la **car**ta 🌎 el me**nú**"))
        self.assertEqual("el zumo", generar_imagenes.limpiar("el zumo 🌎 el jugo"))
        # Y las otras dos formas de traer variantes siguen funcionando.
        self.assertEqual("el sobrino", generar_imagenes.limpiar("el so**bri**no / la so**bri**na"))
        self.assertEqual("el marido", generar_imagenes.limpiar("el ma**ri**do"))

    def test_solo_se_dibuja_lo_que_tiene_dibujo(self):
        """Sin artículo no es un sustantivo, y un abstracto no se dibuja sin
        mentir. Un dibujo ahí sería decoración que roba sitio en 30 minutos."""
        for si in ("la manzana", "el perro", "la casa", "los zapatos"):
            self.assertTrue(generar_imagenes.es_dibujable(si), si)
        for no in ("hola", "muy", "gracias", "mayor", "¿Y tú?",   # sin artículo
                   "el IVA", "la fianza", "el huso horario",       # trámites
                   "la tilde", "el patronímico", "la regla",       # gramática
                   "la Península", "el Día del Padre"):            # sitios reales
            self.assertFalse(generar_imagenes.es_dibujable(no), no)

    def test_ningun_estilo_deja_escribir_texto_en_la_imagen(self):
        """Los modelos escriben con faltas, y un dibujo de «la mesa» con «MEZA»
        encima le enseña al alumno la falta. No es una preferencia: es lo único
        del estilo que no se puede aflojar."""
        for nombre, estilo in generar_imagenes.ESTILOS.items():
            self.assertIn(generar_imagenes.SIN_TEXTO, estilo, nombre)

    def test_cambiar_de_estilo_es_otro_archivo(self):
        """Si no, probar un estilo pisaría el anterior y no se podrían
        comparar —y el índice mezclaría dos—. Es lo mismo que la voz del audio."""
        nombres = {generar_imagenes.nombre_de("la manzana", e)
                   for e in generar_imagenes.ESTILOS}
        self.assertEqual(len(nombres), len(generar_imagenes.ESTILOS))
        # Y la misma palabra con el mismo estilo es SIEMPRE el mismo archivo:
        # eso es lo que hace que no se pague dos veces.
        self.assertEqual(generar_imagenes.nombre_de("la manzana"),
                         generar_imagenes.nombre_de("la manzana"))

    def test_la_muestra_no_juzga_el_estilo_con_palabras_dificiles(self):
        """«El compadre» o «el centro comercial» salen mal por el modelo y no
        por el estilo. Una muestra con ellas haría confundir «no entendió la
        palabra» con «no me gusta el dibujo», que es lo que se decide."""
        palabras = generar_imagenes.todas_las_palabras(plan.cargar())
        muestra = generar_imagenes.muestra_de(palabras, 6)
        self.assertEqual(6, len(muestra))
        for w in muestra:
            nucleo = generar_imagenes.ARTICULO.sub("", w)
            self.assertEqual(1, len(nucleo.split()), f"«{w}» tiene más de una palabra")

    def test_un_archivo_vacio_no_cuenta_como_dibujado(self):
        """Una descarga cortada dejaría un webp de cero bytes que el sitio
        serviría como bueno. Misma guarda que en el audio."""
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = pathlib.Path(tmp)
            (carpeta / generar_imagenes.nombre_de("la manzana")).write_bytes(b"")

            self.assertEqual(["la manzana"], generar_imagenes.faltan(["la manzana"], carpeta))
            self.assertEqual(0, generar_imagenes.escribir_indice(["la manzana"], carpeta))

            indice = json.loads((carpeta / generar_imagenes.INDICE).read_text(encoding="utf-8"))
            self.assertEqual({}, indice, "una imagen vacía no puede entrar en el índice")


class TestLosDibujosEnLaLeccion(unittest.TestCase):
    """El dibujo del sustantivo, delante de la palabra, en la tabla del día.

    Espeja al audio: el índice se lee de `docs/img/` y no de una lista en el
    código, así que el sitio se construye igual con dibujos y sin ellos."""

    CUERPO = """## Словарь дня

| Español | Русский | Пример |
|---|---|---|
| el ma**ri**do | муж | Su marido es médico. |
| la **car**ta 🌎 el me**nú** | меню | ¿Nos trae la carta? |
| ma**yor** | старший | Mi hermano mayor. |

## Ответы

| Español | Русский |
|---|---|
| el ma**ri**do | aquí no |
"""
    INDICE = {"el marido": "AAA.webp", "la carta": "BBB.webp"}

    def _puesto(self):
        return construir_sitio._dibujos_en_el_vocabulario(
            construir_sitio.md(self.CUERPO), self.INDICE, "..")

    def test_el_dibujo_va_en_la_palabra_que_le_toca(self):
        salida = self._puesto()
        self.assertEqual(2, salida.count('class="dibujo"'))
        # Solo las filas del vocabulario: «el marido» sale también en la tabla
        # de Ответы, y mirando el documento entero esa otra pisaba a esta.
        vocabulario = salida.split("Ответы")[0]
        filas = {re.sub(r"<[^>]+>", "", tr.split("</td>")[0]).strip():
                 'class="dibujo"' in tr
                 for tr in re.findall(r"<tr>(.*?)</tr>", vocabulario, re.S)}
        self.assertTrue(filas["el marido"])
        self.assertFalse(filas["mayor"], "«mayor» no lleva artículo: no se dibuja")

    def test_la_variante_americana_casa_con_su_dibujo(self):
        """«la carta 🌎 el menú» tiene que encontrar la entrada «la carta».

        Es lo que obliga a que el generador y el sitio limpien la celda con la
        MISMA función: con dos copias de esa regla, el día que una cambie los
        dibujos dejarían de aparecer sin que nada falle."""
        self.assertIn("BBB.webp", self._puesto())

    def test_solo_la_tabla_del_vocabulario_y_solo_su_primera_columna(self):
        """En las de fonética la primera columna es una letra y en las de
        conjugación una forma verbal: un dibujo ahí no enseña nada. Y en la
        columna de ejemplo sobraría, porque la palabra ya tiene el suyo."""
        salida = self._puesto()
        self.assertNotIn('class="dibujo"', salida.split("Ответы")[1])
        primera_fila = salida.split("Su marido")[1].split("</tr>")[0]
        self.assertNotIn('class="dibujo"', primera_fila)

    def test_sin_indice_la_leccion_sale_igual_que_siempre(self):
        """Las imágenes se generan por tandas: «algunas sí y otras no» es el
        estado normal, y ninguna página puede romperse por eso."""
        html_ = construir_sitio.md(self.CUERPO)
        self.assertEqual(html_, construir_sitio._dibujos_en_el_vocabulario(html_, {}, ".."))

    def test_el_dibujo_no_se_lee_dos_veces_en_voz_alta(self):
        """El `alt` va vacío a propósito: la palabra está al lado y su
        traducción en la columna siguiente, así que un lector de pantalla que
        leyera el dibujo diría lo mismo dos veces."""
        self.assertIn('alt=""', self._puesto())
        self.assertNotIn('alt="el marido"', self._puesto())

    def test_el_boton_del_audio_en_la_celda_no_tapa_la_palabra(self):
        """El camino REAL: `_botones_de_audio` corre antes y mete un «▶» en la
        celda. Quitando solo las etiquetas, el texto salía «▶el marido» y no
        casaba con nada: las 100 lecciones se construyeron sin un solo dibujo
        mientras la prueba de al lado seguía en verde, porque su HTML no tenía
        botones. Por eso esta prueba los pone."""
        con_audio = construir_sitio._botones_de_audio(
            construir_sitio.md(self.CUERPO), {"el marido": "x.mp3"}, "..")
        self.assertIn("▶", con_audio, "el montaje de la prueba tiene que traer el botón")

        salida = construir_sitio._dibujos_en_el_vocabulario(con_audio, self.INDICE, "..")
        self.assertIn("AAA.webp", salida, "el ▶ del audio tapó la palabra")

    def test_el_indice_se_lee_del_disco_y_aguanta_que_no_esté(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual({}, construir_sitio.indice_de_imagenes(pathlib.Path(tmp)))


class TestLaBarajaDeTarjetas(unittest.TestCase):
    """La baraja de Anki: `exportar_apkg.py` y su bloque de descarga.

    El curso está construido sobre las tarjetas y no era un añadido: 92 de las
    100 lecciones empiezan con «Карточки: 10 слов» y 87 cierran pidiendo que se
    añadan 5 palabras a la baraja. Lo que faltaba era la baraja."""

    def test_el_curso_de_verdad_pide_tarjetas(self):
        """Si un día dejara de pedirlas, la baraja sobraría y habría que
        quitarla en vez de mantenerla. Por eso el número se fija aquí."""
        calienta = pide = 0
        for d in plan.dias(plan.cargar()):
            if not d.ruta.exists():
                continue
            texto = d.ruta.read_text(encoding="utf-8")
            calienta += "арточк" in texto.split("## 2.")[0]
            pide += "колод" in texto
        self.assertGreaterEqual(calienta, 80, "las lecciones ya no empiezan con tarjetas")
        self.assertGreaterEqual(pide, 80, "las lecciones ya no mandan añadir a la baraja")

    def test_los_identificadores_son_fijos(self):
        """Anki reconoce baraja, modelo y nota por su id. Con ids al azar,
        volver a importar no actualiza la baraja del alumno: le crea otra al
        lado y pierde meses de repasos. Es el único fallo de este guion que no
        se vería hasta meses después y en el ordenador de otro."""
        self.assertEqual(exportar_apkg._id("Юнит 03"), exportar_apkg._id("Юнит 03"))
        self.assertNotEqual(exportar_apkg._id("Юнит 03"), exportar_apkg._id("Юнит 04"))

    def test_la_tarjeta_del_dibujo_solo_existe_si_hay_dibujo(self):
        """Va envuelta en {{#Imagen}}…{{/Imagen}}: sin eso, las 600 palabras
        sin dibujo tendrían una tarjeta con el anverso en blanco, imposible de
        contestar."""
        dibujo = next(p for p in exportar_apkg.PLANTILLAS if "рисунок" in p["name"])
        self.assertIn("{{#Imagen}}", dibujo["qfmt"])
        self.assertIn("{{/Imagen}}", dibujo["qfmt"])

    def test_el_bloque_sale_de_lo_que_hay_en_disco(self):
        """Sin manifiesto no hay bloque: un botón de descarga que lleva a un
        404 es peor que no ofrecer la baraja."""
        textos = construir_sitio.cargar_textos()["ru"]
        with tempfile.TemporaryDirectory() as tmp:
            vacio = pathlib.Path(tmp)
            self.assertEqual("", construir_sitio._bloque_de_la_baraja(textos, vacio, "."))

            # Con manifiesto pero sin el archivo, tampoco: el manifiesto puede
            # haber sobrevivido a un borrado del .apkg.
            (vacio / "vocabulario").mkdir()
            (vacio / "vocabulario" / construir_sitio.MANIFIESTO_BARAJA).write_text(
                json.dumps({"archivo": "x.apkg", "bytes": 1_000_000, "palabras": 10,
                            "con_voz": 9, "con_dibujo": 3}), encoding="utf-8")
            self.assertEqual("", construir_sitio._bloque_de_la_baraja(textos, vacio, "."))

            (vacio / "vocabulario" / "x.apkg").touch()
            bloque = construir_sitio._bloque_de_la_baraja(textos, vacio, ".")
            self.assertIn("./vocabulario/x.apkg", bloque)
            self.assertIn("10", bloque)

    def test_los_tres_idiomas_enlazan_la_misma_baraja_en_la_raiz(self):
        """La baraja vive UNA vez en `docs/vocabulario/`, no una por idioma.
        El índice en español se escribe en `docs/es/`, así que mirándola en su
        propia carpeta no la encontraría y el bloque se caería en dos de las
        tres páginas."""
        destino = pathlib.Path(RAIZ / "docs")
        if not (destino / "vocabulario" / construir_sitio.MANIFIESTO_BARAJA).exists():
            self.skipTest("todavía no se ha generado la baraja")
        for pagina, prefijo in (("kurs.html", "."), ("es/kurs.html", ".."),
                                ("en/kurs.html", "..")):
            texto = (destino / pagina).read_text(encoding="utf-8")
            self.assertIn('class="baraja"', texto, pagina)
            self.assertIn(f'href="{prefijo}/vocabulario/', texto, pagina)


class TestElRespaldoDelProgreso(unittest.TestCase):
    """El código que el alumno se lleva, para no perder el avance.

    El progreso vive en `localStorage`, que se va con «limpiar datos del
    navegador» y no viaja a otro teléfono. Cuentas de verdad costarían un
    servicio, datos personales y soporte; un código que el alumno guarda donde
    quiera no cuesta nada y no deja nada nuestro en ningún sitio."""

    def setUp(self):
        self.textos = construir_sitio.cargar_textos()
        self.destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(self.destino, construir_sitio.cargar_config(), self.textos)
        self.indice = (self.destino / "kurs.html").read_text(encoding="utf-8")

    def test_restaurar_se_ve_aunque_no_haya_ningun_progreso(self):
        """Es el fallo que tuvo la primera versión y el más fácil de repetir.

        El recuadro `#mio` se oculta cuando no hay nada hecho. Con el botón de
        restaurar dentro, era invisible EXACTAMENTE para quien lo necesita: el
        que acaba de limpiar el navegador o de estrenar móvil y no tiene nada.
        Se vio probándolo en el navegador, no leyendo el código."""
        mio = re.search(r'<div class="progreso" id="mio".*?(?=<div class="respaldo")',
                        self.indice, re.S)
        self.assertIsNotNone(mio, "ya no hay un bloque .respaldo después de #mio")
        self.assertNotIn("restaurar-progreso", mio.group(0),
                         "«Restaurar» no puede vivir dentro del recuadro que se oculta")
        self.assertIn('class="respaldo"', self.indice)

    def test_guardar_nace_oculto_y_restaurar_no(self):
        """Sin nada hecho no hay nada que copiar, así que «Guardar» lo enciende
        el navegador. «Restaurar» siempre está, por lo de arriba."""
        guardar = re.search(r'<button[^>]*id="copiar-progreso"[^>]*>', self.indice).group(0)
        restaurar = re.search(r'<button[^>]*id="restaurar-progreso"[^>]*>', self.indice).group(0)
        self.assertIn("hidden", guardar)
        self.assertNotIn("hidden", restaurar)

    def test_el_html_y_el_guion_hablan_de_los_mismos_ids(self):
        """El contrato son seis ids. Cambiar uno no rompe ninguna página: deja
        de funcionar el respaldo en silencio, que es el fallo que esta suite ya
        caza para el resto del progreso."""
        for id_ in ("copiar-progreso", "restaurar-progreso", "restaurar-caja",
                    "restaurar-codigo", "restaurar-aplicar", "codigo-mio"):
            self.assertIn(f'id="{id_}"', self.indice, f"falta {id_} en el HTML")
            self.assertIn(f"'{id_}'", construir_sitio.PROGRESO_JS, f"el guion no busca {id_}")

    def test_un_codigo_invalido_no_puede_borrar_nada(self):
        """`deCodigo` devuelve null ante cualquier duda y quien lo llama se va
        sin tocar `localStorage`. Restaurar nunca puede ser destructivo: un
        código cortado a medias al pegarlo no puede costarle el curso a nadie."""
        js = construir_sitio.PROGRESO_JS
        cuerpo = js[js.index("function deCodigo"):js.index("var copiar =")]
        self.assertGreaterEqual(cuerpo.count("return null"), 3)
        self.assertIn("catch(e){ return null; }", cuerpo)
        # Y el que llama se va ANTES de escribir nada.
        self.assertIn("if(!datos){ di(T.malo); return; }", js)

    def test_los_textos_estan_en_los_tres_idiomas(self):
        for clave in ("copiar", "copiado", "restaurar", "pegar", "aplicar",
                      "malo", "menos", "hecho_restaurar", "antes"):
            for idioma in ("ru", "es", "en"):
                valor = self.textos[idioma]["progreso"].get(clave, "")
                self.assertTrue(valor.strip(), f"falta progreso.{clave} en {idioma}")

    def test_el_aviso_dice_que_guarde_el_codigo_antes(self):
        """Previene en vez de reparar: quien lee «tu progreso vive solo aquí»
        tiene que leer en la misma frase qué hacer al respecto."""
        self.assertIn(self.textos["ru"]["progreso"]["antes"], self.indice)


class TestLaFirmaDelAutor(unittest.TestCase):
    """El nombre del autor puede ir vacío, y entonces no se escribe el hueco."""

    def test_sin_nombre_no_queda_un_strong_vacio_ni_un_punto_suelto(self):
        """Un «. Преподаватель с магистратурой…» de entrada delata que algo se
        borró a medias."""
        solo = construir_sitio._firma({"nombre": "", "descripcion": "Профессор."})
        self.assertEqual("Профессор.", solo)
        self.assertNotIn("<strong>", solo)

        con = construir_sitio._firma({"nombre": "Ana", "descripcion": "Профессор."})
        self.assertEqual("<strong>Ana</strong>. Профессор.", con)

    def test_el_sitio_construido_no_trae_un_strong_vacio(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        for pagina in destino.rglob("*.html"):
            self.assertNotIn("<strong></strong>", pagina.read_text(encoding="utf-8"),
                             str(pagina.relative_to(destino)))


class TestCompartir(unittest.TestCase):
    """Los botones de compartir al pie de cada lección, y los perfiles en el pie."""

    def setUp(self):
        self.textos = construir_sitio.cargar_textos()
        self.cfg = construir_sitio.cargar_config()

    def test_son_enlaces_normales_y_no_widgets(self):
        """El botón «Compartir» de Facebook carga el SDK de Meta, que rastrea
        al lector. La política de privacidad de este sitio dice que sin AdSense
        no se carga NADA de terceros, y un widget la volvería mentira."""
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, self.cfg, self.textos)
        for pagina in destino.rglob("*.html"):
            texto = pagina.read_text(encoding="utf-8")
            for sdk in ("connect.facebook.net", "platform.twitter.com",
                        "platform.linkedin.com", "apis.google.com"):
                self.assertNotIn(sdk, texto, f"{pagina.name} carga {sdk}")

    def test_sin_dominio_no_se_ofrece_compartir(self):
        """Un enlace para compartir que apunta a `file:///` no le sirve a
        nadie, así que es mejor no ofrecerlo."""
        sin = dict(self.cfg, dominio="")
        self.assertEqual("", construir_sitio._compartir(self.textos["ru"], sin, ""))

    def test_el_enlace_lleva_a_ESTA_leccion_y_no_a_la_portada(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, self.cfg, self.textos)
        leccion = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn("semana-01%2Fdia-1.html", leccion, "comparte la página equivocada")
        self.assertIn('data-url="https://espanoldesderuso.com/semana-01/dia-1.html"', leccion)

    def test_una_red_sin_rellenar_no_sale(self):
        """Un botón que lleva a una cuenta que no existe es peor que ninguno."""
        vacio = dict(self.cfg, redes={"telegram": "", "instagram": "  "})
        self.assertEqual("", construir_sitio._seguir(self.textos["ru"], vacio, "."))

        con = dict(self.cfg, redes={"telegram": "https://t.me/x", "instagram": ""})
        pie = construir_sitio._seguir(self.textos["ru"], con, ".")
        self.assertIn("https://t.me/x", pie)
        self.assertNotIn("Instagram", pie)

    def test_las_redes_del_repo_estan_vacias(self):
        """Hasta que el profesor dé sus URLs, ninguna sale. Si un día esto se
        pone en rojo es que alguien escribió un perfil a mano: comprobar que
        existe antes de aflojar la prueba."""
        for clave, url in (self.cfg.get("redes") or {}).items():
            self.assertEqual("", (url or "").strip(), f"redes.{clave}")


class TestLasCasillasParaEscribir(unittest.TestCase):
    """Las rayas que no son fichas se vuelven casillas donde se escribe.

    Lo trajo el profesor mirando la lección 1-1 en el móvil: «por ejemplo
    estos espacios vacios, no hay nada para completar». En papel una raya es
    donde escribes; en una pantalla era una raya y nada más.

    Las fichas pulsables cubren los ejercicios que traen banco de palabras Y
    una clave que se casa sin ninguna duda. El resto —la gran mayoría, porque
    la mayoría de los ejercicios piden escribir la forma correcta y no elegir
    una ficha— se quedaba inerte."""

    LECCIONES = sorted((RAIZ / "docs").glob("semana-*/dia-*.html"))

    def setUp(self):
        if not self.LECCIONES:
            self.skipTest("todavía no se ha construido el sitio")

    @staticmethod
    def _sin_guiones(html_: str) -> str:
        """La página sin sus `<script>`: dentro va el propio guion de las
        casillas, que NOMBRA la clase, y contarlo sería contarse a sí mismo."""
        return re.sub(r"<script\b.*?</script>", "", html_, flags=re.S)

    def test_ninguna_raya_se_queda_sin_casilla(self):
        """Si el Markdown escribió un hueco, en la página hay dónde escribir:
        o una ficha que se pulsa o una casilla que se teclea."""
        cal = plan.cargar()
        revisadas = 0
        for d in plan.dias(cal):
            if not d.ruta.exists():
                continue
            cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))[1]
            antes_de_la_clave = cuerpo.split("## Ответы")[0]
            esperados = len(re.findall(r"_{3,}", antes_de_la_clave))
            if not esperados:
                continue
            revisadas += 1
            pagina = self._sin_guiones(
                (RAIZ / "docs" / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html")
                .read_text(encoding="utf-8"))
            # Una raya en crudo NO cuenta: es justo lo que se viene a
            # arreglar. Solo cuentan las dos cosas donde se puede escribir.
            hay = (pagina.count('class="hueco-escribir"')
                   + len(re.findall(r'<span class="hueco" ', pagina)))
            self.assertGreaterEqual(hay, esperados,
                                    f"semana {d.semana} día {d.dia}: faltan huecos")
            self.assertEqual(0, len(re.findall(r"_{3,}", pagina.split(">Ответы<")[0])),
                             f"semana {d.semana} día {d.dia}: una raya sin convertir")
        self.assertGreater(revisadas, 80, "casi todas las lecciones tienen huecos")

    def test_la_clave_conserva_sus_rayas(self):
        """Dentro de `## Ответы` una raya es parte de una respuesta, no un
        sitio donde escribir. Hay una así en la lección 5-2."""
        con_raya = 0
        for p in self.LECCIONES:
            texto = self._sin_guiones(p.read_text(encoding="utf-8"))
            if ">Ответы<" not in texto:
                continue
            clave = texto.split(">Ответы<", 1)[1]
            self.assertNotIn("hueco-escribir", clave, p.name)
            con_raya += len(re.findall(r"_{3,}", clave))
        self.assertEqual(1, con_raya,
                         "la clave de la 5-2 trae una raya: si cambia, revisar por qué")

    def test_se_escribe_sin_javascript(self):
        """Es el único trozo interactivo del sitio que nace encendido, y a
        propósito: un `<input>` se teclea sin guion ninguno. El guion solo le
        ajusta el ancho mientras escribes, que es cosmético.

        Por eso aquí no vale el patrón de «nace oculto»: esconder la casilla
        hasta que arranque el guion la rompería para quien no lo tenga."""
        texto = self._sin_guiones(
            (RAIZ / "docs" / "semana-01" / "dia-1.html").read_text(encoding="utf-8"))
        casillas = re.findall(r"<input[^>]*hueco-escribir[^>]*>", texto)
        self.assertGreaterEqual(len(casillas), 6)
        for c in casillas:
            self.assertIn('type="text"', c)
            self.assertNotIn("disabled", c)
            self.assertNotIn("readonly", c)
            self.assertNotIn("hidden", c)

    def test_el_corrector_del_navegador_esta_apagado(self):
        """El corrector va en el idioma del lector, que es ruso: encendido,
        subraya en rojo cada palabra española que se escriba."""
        texto = (RAIZ / "docs" / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        casillas = re.findall(r"<input[^>]*hueco-escribir[^>]*>", texto)
        self.assertGreaterEqual(len(casillas), 6, "sin casillas la prueba no prueba nada")
        for c in casillas:
            self.assertIn('spellcheck="false"', c)
            self.assertIn('autocapitalize="off"', c)

    def test_el_ancho_no_se_deja_al_navegador(self):
        """Un `<input>` sin ancho mide lo que su `size` por defecto —unos
        230 px— y eso parte en dos los renglones que llevan dos huecos. Se
        vio midiéndolo en el navegador, no leyendo el código."""
        regla = re.search(r"\.hueco-escribir\{([^}]*)\}", construir_sitio.CSS)
        self.assertIsNotNone(regla)
        self.assertRegex(regla.group(1), r"\bwidth:",
                         "sin width, el navegador le pone el suyo")
        self.assertNotRegex(regla.group(1), r"\bmin-width:\s*5\.5rem;(?![^}]*\bwidth:)",
                            "min-width sola no limita el ancho de un input")

    def test_un_ejercicio_de_fichas_no_lleva_casillas(self):
        """Los dos mecanismos no pueden convivir en el mismo ejercicio: la
        conversión va DESPUÉS de las fichas justamente para que aquellas ya se
        hayan llevado sus `______`."""
        cal = plan.cargar()
        comprobadas = 0
        for d in plan.dias(cal):
            if not d.ruta.exists():
                continue
            cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))[1]
            ejercicios = huecos.leer(cuerpo)
            if not ejercicios:
                continue
            texto = (RAIZ / "docs" / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html"
                     ).read_text(encoding="utf-8")
            for e in ejercicios:
                trozo = re.split(rf"<h3[^>]*>\s*{re.escape(e.titulo)}\s*</h3>", texto)
                if len(trozo) < 2:
                    continue
                cuerpo_ej = re.split(r"<h[23][\s>]", trozo[1])[0]
                self.assertNotIn("hueco-escribir", cuerpo_ej,
                                 f"semana {d.semana} día {d.dia}: {e.titulo}")
                comprobadas += 1
        self.assertGreater(comprobadas, 20)


class TestLosHuecosInteractivos(unittest.TestCase):
    """Rellenar los ______ pulsando una ficha del banco de palabras.

    Hay 1.488 huecos escritos en 89 de las 100 lecciones y 61 ejercicios con
    banco. De esos, **23 tienen una clave que se puede casar con los huecos sin
    ninguna duda** y son los que se vuelven interactivos; los otros 38 llevan
    claves con frases enteras («Es una goma» contra un banco de «una goma»), o
    sea que son otro tipo de ejercicio y se quedan como están."""

    EJEMPLO = """### Упражнение Б. Дополните. Банк слов:

> aquí · ahí · cerca de · del

1. Mi móvil está ______, en la mesa.
2. Mi casa está ______ el centro.
3. Está al lado ______ parque, ______.

## Ответы

**Б.** 1. aquí · 2. cerca de · 3. del / ahí.
"""

    def test_lee_el_ejercicio_y_casa_la_clave(self):
        e = huecos.leer(self.EJEMPLO)
        self.assertEqual(1, len(e))
        self.assertEqual(["aquí", "ahí", "cerca de", "del"], e[0].banco)
        self.assertEqual(["aquí", "cerca de", "del", "ahí"], e[0].respuestas)

    def test_el_orden_manda_y_no_la_numeracion(self):
        """La mitad de los ejercicios son diálogos SIN numerar, y su clave da
        las respuestas seguidas: «días · tal · gracias · tú». Lo que ata una
        respuesta a su hueco es el orden en que salen."""
        dialogo = self.EJEMPLO.replace("**Б.** 1. aquí · 2. cerca de · 3. del / ahí.",
                                       "**Б.** aquí · cerca de · del · ahí.")
        self.assertEqual(["aquí", "cerca de", "del", "ahí"],
                         huecos.leer(dialogo)[0].respuestas)

    def test_si_la_cuenta_no_cuadra_el_ejercicio_se_descarta(self):
        """Cuatro huecos y tres respuestas: no hay forma de saber cuál falta,
        así que no se adivina. Decirle a alguien que acertó cuando falló es
        mucho peor que no ofrecerle el ejercicio."""
        corta = self.EJEMPLO.replace("3. del / ahí.", "3. del.")
        self.assertEqual([], huecos.leer(corta))

    def test_una_respuesta_fuera_del_banco_descarta_el_ejercicio(self):
        """Es la comprobación que de verdad protege: los bancos son cortos y
        concretos, así que una clave desalineada deja fuera alguna palabra casi
        siempre. Es lo que descarta los 38 ejercicios cuya clave da frases."""
        otra = self.EJEMPLO.replace("2. cerca de", "2. Es una goma")
        self.assertEqual([], huecos.leer(otra))

    def test_sin_clave_no_hay_ejercicio(self):
        self.assertEqual([], huecos.leer(self.EJEMPLO.split("## Ответы")[0]))

    def test_el_comentario_ruso_no_se_cuela_como_respuesta(self):
        """En la lección 1-3 la clave acaba en «… · es. Carmen говорит
        **encantada**…»: sin cortar ahí, la última respuesta sería esa frase
        entera, no estaría en el banco y el ejercicio se perdía."""
        self.assertEqual("del", huecos._respuestas("1. del. Carmen говорит algo")[0])
        self.assertEqual("del", huecos._respuestas("1. del (у вас)")[0])

    def test_el_bloque_de_la_clave_no_se_come_el_parrafo_siguiente(self):
        """Juntando las líneas primero, un «\n\n» se volvía «\n » y el bloque
        seguía leyendo: en la lección 1-3 salían 12 respuestas para 5 huecos."""
        clave = "## Ответы\n\n**Б.** uno · dos.\n\n**Выход:** tres · cuatro · cinco."
        self.assertEqual(["uno", "dos"], huecos._respuestas(
            huecos._bloque_de_la_clave(clave, "Б")))

    def test_en_el_sitio_salen_las_fichas_y_los_huecos(self):
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        con = [p for p in (destino).rglob("semana-*/dia-*.html")
               if 'class="hueco"' in p.read_text(encoding="utf-8")]
        self.assertGreaterEqual(len(con), 20, "se perdieron ejercicios por el camino")

        uno = (destino / "semana-06" / "dia-2.html").read_text(encoding="utf-8")
        self.assertIn('class="ficha"', uno)
        self.assertIn("CURSO_HUECOS", uno)
        # El banco escrito se marca para que lo esconda el navegador, y NO se
        # borra: sin JavaScript es lo único que dice qué palabras hay.
        self.assertIn('class="banco-escrito"', uno)

    def test_ninguna_pagina_trae_un_byte_nulo(self):
        """El CSS llevaba `content:"\00a0"`, que Python lee como escape octal
        y escribía un NUL en las 125 páginas. Un HTML con un NUL lo sirven los
        navegadores pero `grep` lo trata como binario, y es la clase de cosa
        que no se ve mirando la página."""
        for pagina in (RAIZ / "docs").rglob("*.html"):
            self.assertNotIn(b"\x00", pagina.read_bytes(), str(pagina.name))


class TestLaVitrinaDeLaPortada(unittest.TestCase):
    """Los doce dibujos de la portada.

    El profesor dijo que la página «se ve muy aburrida». Lo que la viste son
    los 300 dibujos que ya están pagados y en disco: son de la paleta de la
    casa, no los tiene nadie más y no cargan un solo byte de fuera. Y no es
    solo decoración: el visitante aprende doce palabras antes de pulsar
    nada."""

    def setUp(self):
        self.t = construir_sitio.cargar_textos()["ru"]
        self.dibujos = construir_sitio.indice_de_imagenes(RAIZ / "docs")
        self.lexico = construir_sitio.lexico_del_curso(CAL)

    def test_las_doce_palabras_salen_todas_hoy(self):
        """La página se cae de pie si falta alguna, pero aquí se exige que no
        falte ninguna: el día que una lección cambie una traducción o alguien
        borre un dibujo, la vitrina se encogería en silencio y nadie lo vería
        hasta mirar la portada."""
        if not self.dibujos:
            self.skipTest("todavía no se han generado los dibujos")
        for palabra in construir_sitio.PORTADA_DIBUJOS:
            with self.subTest(palabra=palabra):
                self.assertIn(generar_imagenes.limpiar(palabra), self.dibujos,
                              "sin dibujo")
                ruso = self.lexico.get(palabra, "")
                self.assertTrue(ruso, "no está en el vocabulario del curso")
                self.assertIsNone(construir_sitio.NO_ES_TRADUCCION.search(ruso),
                                  f"la traducción no es rusa limpia: {ruso!r}")

    def test_son_doce_para_que_no_quede_ninguna_huerfana(self):
        """La rejilla es de 3, 4 o 6 columnas según el ancho. Doce es el único
        número pequeño que deja filas enteras en los tres casos."""
        n = len(construir_sitio.PORTADA_DIBUJOS)
        self.assertEqual(n, len(set(construir_sitio.PORTADA_DIBUJOS)), "hay repetidas")
        for columnas in (3, 4, 6):
            self.assertEqual(0, n % columnas, f"con {columnas} columnas sobra una fila a medias")

    def test_sin_dibujos_generados_no_sale_nada(self):
        """Igual que la baraja y el audio: el sitio se construye con todo y
        sin nada."""
        self.assertEqual("", construir_sitio._muestra_de_dibujos(self.t, {}, {}, "."))

    def test_una_traduccion_que_no_es_rusa_se_salta(self):
        """La columna rusa del vocabulario trae a veces la variante americana
        («el zumo → el jugo», por la regla 8) o una corrección («стакан (✗ не
        ваза!)»). Lo primero pondría español donde se promete ruso."""
        dibujos = {generar_imagenes.limpiar(p): f"{i}.webp"
                   for i, p in enumerate(construir_sitio.PORTADA_DIBUJOS)}
        lexico = dict.fromkeys(construir_sitio.PORTADA_DIBUJOS, "слово")
        malas = {construir_sitio.PORTADA_DIBUJOS[0]: "el jugo",
                 construir_sitio.PORTADA_DIBUJOS[1]: "стакан (✗ не «ваза»!)"}
        lexico.update(malas)
        bloque = construir_sitio._muestra_de_dibujos(self.t, dibujos, lexico, ".")
        self.assertEqual(len(construir_sitio.PORTADA_DIBUJOS) - 2, bloque.count("<li>"))
        for palabra in malas:
            self.assertNotIn(f"<b>{palabra}</b>", bloque)

    def test_media_vitrina_no_sale(self):
        """Con tres huecos no se lee como «todavía faltan dibujos»: se lee como
        una página rota."""
        palabras = construir_sitio.PORTADA_DIBUJOS[:construir_sitio.MUESTRA_MINIMA - 1]
        dibujos = {generar_imagenes.limpiar(p): "x.webp" for p in palabras}
        lexico = dict.fromkeys(palabras, "слово")
        self.assertEqual("", construir_sitio._muestra_de_dibujos(self.t, dibujos, lexico, "."))

    def test_la_portada_de_los_tres_idiomas_la_ensena(self):
        """Las mismas doce en ru, es y en: son el vocabulario del curso, no un
        texto de la interfaz. Y el `src` tiene que llevar el prefijo correcto,
        porque los dibujos viven UNA vez en `docs/img/` y la portada española
        se escribe en `docs/es/`."""
        docs = RAIZ / "docs"
        if not (docs / "img" / construir_sitio.INDICE_IMG).exists():
            self.skipTest("todavía no se han generado los dibujos")
        for pagina, prefijo in (("index.html", "./img/"), ("es/index.html", "../img/"),
                                ("en/index.html", "../img/")):
            texto = (docs / pagina).read_text(encoding="utf-8")
            vitrina = re.search(r'<ul class="vitrina">.*?</ul>', texto, re.S)
            self.assertIsNotNone(vitrina, pagina)
            self.assertEqual(len(construir_sitio.PORTADA_DIBUJOS),
                             vitrina.group(0).count("<li>"), pagina)
            for src in re.findall(r'<img src="([^"]+)"', vitrina.group(0)):
                self.assertTrue(src.startswith(prefijo), f"{pagina}: {src}")
                self.assertTrue((docs / src.split("/", 1)[1].lstrip("./")).exists()
                                or (docs / src.replace("../", "").lstrip("./")).exists(),
                                f"{pagina}: no existe {src}")

    def test_el_lexico_sale_de_las_lecciones(self):
        """De las lecciones y no de una lista en el código: si se escribieran a
        mano, el día que el profesor corrigiera una traducción la portada
        seguiría enseñando la vieja."""
        self.assertGreater(len(self.lexico), 500)
        self.assertEqual("яблоко", self.lexico.get("la manzana"))

    # ---- la ficha suena ----

    def test_las_doce_fichas_son_botones_que_suenan(self):
        """La ficha ENTERA es el botón, no un ▶ al lado de la palabra: en el
        móvil un icono de doce píxeles no se acierta con el dedo.

        Y el `data-audio` tiene que apuntar a un archivo que exista: un botón
        que no suena es peor que ninguno, porque el visitante aprende en el
        primer clic que esta web no funciona."""
        docs = RAIZ / "docs"
        audio = construir_sitio.indice_de_audio(docs)
        if not audio or not construir_sitio.indice_de_imagenes(docs):
            self.skipTest("todavía no se han generado el audio o los dibujos")
        for pagina, prefijo in (("index.html", "./audio/"), ("es/index.html", "../audio/")):
            texto = (docs / pagina).read_text(encoding="utf-8")
            vitrina = re.search(r'<ul class="vitrina">.*?</ul>', texto, re.S).group(0)
            fuentes = re.findall(r'class="suena ficha"[^>]*data-audio="([^"]+)"', vitrina)
            self.assertEqual(len(construir_sitio.PORTADA_DIBUJOS), len(fuentes), pagina)
            for src in fuentes:
                self.assertTrue(src.startswith(prefijo), f"{pagina}: {src}")
                self.assertTrue((docs / "audio" / src.rsplit("/", 1)[1]).exists(),
                                f"{pagina}: no existe {src}")

    def test_sin_audio_la_ficha_sigue_siendo_una_ficha(self):
        """El audio se genera por tandas, así que «algunas palabras sí y otras
        no» es el estado normal durante un tiempo. Una palabra sin locutar no
        puede dejar la tarjeta a medias ni desaparecer de la vitrina: se queda
        igual, sin botón."""
        dibujos = {generar_imagenes.limpiar(p): f"{i}.webp"
                   for i, p in enumerate(construir_sitio.PORTADA_DIBUJOS)}
        lexico = dict.fromkeys(construir_sitio.PORTADA_DIBUJOS, "слово")
        muda = construir_sitio._muestra_de_dibujos(self.t, dibujos, lexico, ".")
        self.assertEqual(len(construir_sitio.PORTADA_DIBUJOS), muda.count("<li>"))
        self.assertNotIn("suena", muda)
        self.assertEqual(len(construir_sitio.PORTADA_DIBUJOS), muda.count('<span class="ficha">'))
        # Y con media tanda locutada, cada una en su estado.
        media = dict(list(zip(construir_sitio.PORTADA_DIBUJOS, ["a.mp3", "b.mp3"])))
        mezcla = construir_sitio._muestra_de_dibujos(self.t, dibujos, lexico, ".", media)
        self.assertEqual(2, mezcla.count('class="suena ficha"'))
        self.assertEqual(len(construir_sitio.PORTADA_DIBUJOS) - 2,
                         mezcla.count('<span class="ficha">'))

    def test_el_boton_no_se_lleva_por_delante_el_estilo_de_la_ficha(self):
        """Un `<button>` trae el cromo del navegador —fondo gris, borde, letra
        de sistema— y la ficha es una tarjeta. Sin estas reglas sale un botón
        dentro de la tarjeta, y eso no se ve hasta abrir la portada.

        Y la traducción rusa cuelga de `.ru` y no de `.vitrina span`: desde que
        la ficha muda ES un `<span>`, el selector corto le daría a la tarjeta
        entera el tamaño de letra de la traducción."""
        css = construir_sitio.CSS
        regla = re.search(r"\.vitrina \.ficha\{([^}]*)\}", css)
        self.assertIsNotNone(regla, "la ficha no tiene regla propia")
        for apagado in ("background:none", "border:0", "font:inherit"):
            self.assertIn(apagado, regla.group(1), f"falta {apagado}")
        self.assertIn(".vitrina .ru{", css)
        self.assertNotIn(".vitrina span{", css)


class TestElProbadorDeLaPortada(unittest.TestCase):
    """Tres preguntas jugables en la portada.

    El profesor lo dijo dos veces: la página «se ve muy aburrida» y «le falta
    interactividad al comienzo». Tenía razón en el sitio exacto: el curso es
    interactivo por dentro —audio, huecos que se rellenan, pruebas de unidad—
    pero la portada solo se leía.

    No se escribió ni una pregunta nueva: son las del test de nivel."""

    def setUp(self):
        self.t = construir_sitio.cargar_textos()["ru"]
        self.preguntas = yaml.safe_load(
            (RAIZ / "programa" / "test-nivel.yaml").read_text(encoding="utf-8"))

    def test_las_tres_salen_del_banco_del_test_de_nivel(self):
        """Del banco y no de una lista aparte: una copia se queda vieja el día
        que el profesor corrija una pregunta, y además esas ya traen la
        explicación del error en ruso, que es lo único que esta página tiene
        que demostrar."""
        bloque = construir_sitio._probador(self.t, self.preguntas, ".", "./x.html")
        datos = json.loads(re.search(r"window\.CURSO_PROBADOR=(\{.*?\});\(function",
                                     bloque, re.S).group(1))
        self.assertEqual(construir_sitio.PROBADOR_PREGUNTAS, len(datos["grupos"]))
        banco = {q["pregunta"] for q in self.preguntas["preguntas"]}
        for grupo in datos["grupos"]:
            self.assertTrue(grupo, "un grupo vacío dejaría la portada sin pregunta")
            for q in grupo:
                self.assertIn(q["pregunta"], banco)
                self.assertTrue(q["error"], "sin explicación no enseña nada")

    def test_son_las_tres_primeras_unidades(self):
        """Lo bastante fáciles para que un principiante acierte y siga, y lo
        bastante rápidas para que quien ya sabe español llegue al final y pulse
        «hacer el test completo»."""
        grupos = construir_sitio.grupos_por_unidad(self.preguntas["preguntas"])
        tomados = grupos[:construir_sitio.PROBADOR_PREGUNTAS]
        self.assertEqual([1, 2, 3], [g[0]["unidad"] for g in tomados])

    def test_sin_banco_suficiente_no_sale_nada(self):
        """Como la vitrina y la baraja: el sitio se construye con todo y sin
        nada. Media partida es peor que ninguna."""
        corto = {"preguntas": self.preguntas["preguntas"][:1]}
        self.assertEqual("", construir_sitio._probador(self.t, corto, ".", "./x.html"))
        self.assertEqual("", construir_sitio._probador(self.t, {}, ".", "./x.html"))

    def test_los_dos_destinos_del_final_existen(self):
        """Termina con dos botones —la lección 1 y el test completo— y los dos
        viven dentro de un `<script>`, así que `revisar_adsense.enlaces_rotos`
        no los mira desde el 2026-10-26: o se comprueban aquí o no los
        comprueba nadie."""
        docs = RAIZ / "docs"
        for pagina in ("index.html", "es/index.html", "en/index.html"):
            carpeta = (docs / pagina).parent
            texto = (docs / pagina).read_text(encoding="utf-8")
            datos = json.loads(re.search(r"window\.CURSO_PROBADOR=(\{.*?\});\(function",
                                         texto, re.S).group(1))
            for clave in ("leccion", "test"):
                destino = (carpeta / datos[clave]).resolve()
                self.assertTrue(destino.exists(), f"{pagina}: {clave} → {datos[clave]}")

    def test_el_boton_nace_oculto_y_lo_enciende_el_navegador(self):
        """Sin JavaScript sería un botón que no hace nada. El párrafo de
        contraste que hay encima ya explica lo mismo en texto, así que quien
        llegue sin guion no se pierde nada."""
        texto = (RAIZ / "docs" / "index.html").read_text(encoding="utf-8")
        arranque = re.search(r'<div class="botones" id="probador-arranque"([^>]*)>', texto)
        self.assertIsNotNone(arranque)
        self.assertIn("hidden", arranque.group(1))
        self.assertIn("arranque.hidden=false", texto)

    def test_el_siguiente_no_sale_de_la_palabra_de(self):
        """Los textos de los dos botones son suyos y no un apaño con los del
        test («de» + flecha daba «из →», que en ruso significa «de»). Hay tres
        idiomas y los tres tienen que decirlo entero."""
        todos = construir_sitio.cargar_textos()
        for idioma in ("ru", "es", "en"):
            p = todos[idioma]["portada"]
            with self.subTest(idioma=idioma):
                for clave in ("probador_siguiente", "probador_ver", "probador_titulo",
                              "probador_entrada", "probador_bien", "probador_mal",
                              "probador_final", "probador_test", "oir"):
                    self.assertTrue(p.get(clave, "").strip(), f"falta {clave}")
                self.assertNotEqual(p["probador_siguiente"].strip(" →"),
                                    todos[idioma]["test"]["de"])


class TestLaTarjetaSocial(unittest.TestCase):
    """La imagen de la vista previa al compartir, hecha con los dibujos.

    Los botones de compartir son del 2026-10-27 y el enlace llegaba sin
    imagen: Telegram, WhatsApp, Facebook y VK pintan la vista previa con
    `og:image`, y no había ninguno."""

    def test_la_medida_es_la_que_piden_las_plataformas(self):
        self.assertEqual((1200, 630), (tarjeta_social.ANCHO, tarjeta_social.ALTO))

    def test_son_las_mismas_palabras_que_la_portada(self):
        """Quien llega por el enlace ve primero la tarjeta y enseguida la
        página: que sean las mismas doce hace que el sitio se reconozca."""
        indice = {generar_imagenes.limpiar(p): "x.webp"
                  for p in construir_sitio.PORTADA_DIBUJOS}
        self.assertEqual(list(construir_sitio.PORTADA_DIBUJOS),
                         tarjeta_social.palabras_con_dibujo(indice))
        self.assertEqual([], tarjeta_social.palabras_con_dibujo({}))

    def test_sin_dominio_no_se_declara(self):
        """`og:image` se descarga desde el servidor de la plataforma, así que
        tiene que ser una URL absoluta: sin dominio no sirve de nada."""
        self.assertEqual("", construir_sitio._tarjeta_social({"dominio": ""}, "x"))

    def test_sin_imagen_no_se_declara(self):
        """Prometer una imagen que da 404 es peor que no declarar ninguna."""
        antes = construir_sitio.TARJETA_SOCIAL
        construir_sitio.TARJETA_SOCIAL = "img/no-existe-esta-tarjeta.png"
        try:
            self.assertEqual("", construir_sitio._tarjeta_social(
                {"dominio": "https://ejemplo.com"}, "x"))
        finally:
            construir_sitio.TARJETA_SOCIAL = antes

    def test_la_imagen_esta_en_las_paginas_y_en_disco(self):
        docs = RAIZ / "docs"
        if not (docs / construir_sitio.TARJETA_SOCIAL).exists():
            self.skipTest("todavía no se ha compuesto la tarjeta")
        dominio = construir_sitio.cargar_config().get("dominio", "")
        if not dominio:
            self.skipTest("sin dominio configurado")
        from PIL import Image
        with Image.open(docs / construir_sitio.TARJETA_SOCIAL) as im:
            self.assertEqual((tarjeta_social.ANCHO, tarjeta_social.ALTO), im.size)
        for pagina in ("index.html", "es/index.html", "kurs.html",
                       "semana-01/dia-1.html"):
            texto = (docs / pagina).read_text(encoding="utf-8")
            self.assertIn(f'property="og:image" content="{dominio}/'
                          f'{construir_sitio.TARJETA_SOCIAL}"', texto, pagina)
            self.assertIn('name="twitter:card" content="summary_large_image"', texto, pagina)


class TestLaClaveDeLosEjercicios(unittest.TestCase):
    """Dónde se ven las respuestas y cuándo.

    Lo preguntó el profesor: «¿y las respuestas a los ejercicios? ¿dónde ver si
    es correcto?». Estaban abiertas al final de la página, DEBAJO de la tabla
    de vocabulario, y eso fallaba por los dos lados: quien las buscaba no las
    encontraba y quien no las buscaba se las encontraba de paso, con las
    respuestas a la vista antes de hacer el ejercicio."""

    @classmethod
    def setUpClass(cls):
        cls.destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(cls.destino, construir_sitio.cargar_config(),
                                  construir_sitio.cargar_textos())
        cls.dias = [d for d in construir_sitio.escritas(CAL)]

    def _pagina(self, d):
        return (self.destino / f"semana-{d.semana:02d}" / f"dia-{d.dia}.html").read_text(encoding="utf-8")

    def test_toda_leccion_con_clave_la_pliega_y_la_enlaza(self):
        """El enlace donde se acaban los ejercicios, la clave plegada al final.
        Y las cuatro formas del curso cuentan: lección, repaso, cultura y
        simulacro.

        Los simulacros de la fase final estrenaron el caso que el generador no
        contemplaba: su apartado de corrección **menciona** un ejercicio
        («Задание 2, номер 11»), así que el corte caía en la clave misma y el
        enlace **no se ponía**, sin que nada fallara. Esta prueba lo cazó en
        tres días; el generador se arregló buscando el último corte que esté de
        verdad antes de la clave."""
        mirados = 0
        for d in self.dias:
            # Los tres tipos sin ejercicios quedan fuera, cada uno por su
            # motivo (ver `CON_CLAVE_DE_EJERCICIOS`). La lista se lee del
            # generador y no se copia aquí: dos copias de la misma regla es
            # como se descubre tarde que una de las dos se quedó vieja.
            if d.tipo not in construir_sitio.CON_CLAVE_DE_EJERCICIOS:
                continue
            cuerpo = validar.frontmatter(d.ruta.read_text(encoding="utf-8"))[1]
            if "## Ответы" not in cuerpo:
                continue
            mirados += 1
            p = self._pagina(d)
            with self.subTest(dia=d.numero):
                self.assertIn('<div id="clave">', p)
                self.assertIn('id="clave-boton"', p)
                self.assertIn('<a href="#clave">', p)
                self.assertLess(p.index('<a href="#clave">'), p.index('<div id="clave">'),
                                "el enlace tiene que ir ANTES de la clave")
        self.assertGreater(mirados, 80, "casi todas las lecciones llevan clave")

    def test_los_dias_sin_ejercicios_no_pliegan_la_clave(self):
        """Un `examen` lleva la clave dentro de su apartado de corrección y un
        `proyecto` no tiene ejercicios: su `## Ответы` es un modelo, no una
        respuesta. Plegarlos dejaría un botón que abre algo a lo que no apunta
        ningún enlace, porque el enlace no se coloca donde no hay ejercicios.

        Lo cazó la suite al estrenarse los tres tipos en la unidad 11, y otra
        vez al estrenarse `reserva` en el día 365 — que es para lo que el
        conjunto está fijado: un tipo nuevo no puede colarse sin que alguien
        decida si su clave se pliega. El día 365 no tiene `## Ответы`, así que
        no hay nada que plegar."""
        vistos = []
        for d in self.dias:
            if d.tipo in construir_sitio.CON_CLAVE_DE_EJERCICIOS:
                continue
            p = self._pagina(d)
            vistos.append(d.tipo)
            with self.subTest(dia=d.numero, tipo=d.tipo):
                if d.tipo != "prueba":
                    self.assertNotIn('<div id="clave">', p)
                self.assertNotIn('<a href="#clave">', p)
        self.assertEqual({"prueba", "examen", "proyecto", "reserva"}, set(vistos))

    def test_el_enlace_cae_donde_se_acaban_los_ejercicios(self):
        """Y no al final del todo. Se busca por el CONTENIDO y no por el nombre
        del apartado, porque son tres: «Практика», «Мини-тест» y «Задание»."""
        casos = [(15, 2, "4. Практика", "5. Выход"),
                 (15, 6, "3. Мини-тест", "4. Разбор ошибок"),
                 (1, 6, "3. Мини-тест", "4. Разбор ошибок"),
                 (13, 7, "4. Задание", "5. Итог")]
        for semana, dia, ejercicios, siguiente in casos:
            p = self._pagina(plan.dia(CAL, semana, dia))
            with self.subTest(dia=f"{semana}/{dia}"):
                i = p.index('<p class="a-la-clave">')
                self.assertLess(p.index(ejercicios), i,
                                f"el enlace tiene que ir DESPUÉS de «{ejercicios}»")
                self.assertLess(i, p.index(siguiente),
                                f"y ANTES de «{siguiente}»")

    def test_el_titulo_del_apartado_cuenta_como_marca(self):
        """Un repaso titula «3. Мини-тест» y dentro solo dice «выберите
        правильный ответ»: mirando solo el cuerpo, el enlace caía antes del
        mini-test, y en la semana 1 no caía en ninguna parte."""
        for d in self.dias:
            if d.tipo != "repaso":
                continue
            p = self._pagina(d)
            with self.subTest(dia=d.numero):
                self.assertIn('<p class="a-la-clave">', p)
                self.assertLess(p.index("Мини-тест"), p.index('<p class="a-la-clave">'))

    def test_el_dia_de_prueba_no_pasa_por_aqui(self):
        """Tiene su propio envoltorio: el test contestable y la clave al
        terminar. Dos mecanismos sobre la misma clave se pisarían."""
        for d in self.dias:
            if d.tipo != "prueba":
                continue
            p = self._pagina(d)
            with self.subTest(dia=d.numero):
                self.assertNotIn('<div id="clave">', p)
                self.assertIn('id="prueba-clave"', p)

    def test_sin_javascript_la_clave_sigue_estando(self):
        """La versión sin guion tiene que ser la que sirve: una clave escondida
        que no se puede abrir sería una lección sin respuestas. Por eso nace
        visible y es el navegador quien la pliega, al revés que el resto del
        sitio."""
        p = self._pagina(plan.dia(CAL, 15, 2))
        self.assertNotIn('<div id="clave" hidden>', p)
        self.assertIn("pon(false); zona.hidden=false;", construir_sitio.CLAVE_SCRIPT)
        # Y el contenido de la clave sigue entero en el HTML.
        self.assertIn("два инфинитива", p)

    def test_el_enlace_abre_la_clave(self):
        """Un ancla que apunta a algo escondido no hace nada, y el lector se
        queda mirando la misma pantalla creyendo que está roto. Comprobado
        además en navegador en las tres formas de día."""
        self.assertIn('a[href="#clave"]', construir_sitio.CLAVE_SCRIPT)
        self.assertIn("location.hash==='#clave'", construir_sitio.CLAVE_SCRIPT)

    def test_una_pagina_sin_clave_no_se_toca(self):
        textos = construir_sitio.cargar_textos()["ru"]
        html_ = "<h2>1. Разминка (0–3 мин)</h2><p>Упражнение</p>"
        self.assertEqual(html_, construir_sitio._envolver_clave(html_, textos))

    def test_el_boton_lleva_los_dos_textos(self):
        """Los dos van en el HTML y no en el guion: traducirlos no toca código,
        y el botón dice la verdad desde el primer pintado."""
        L = construir_sitio.cargar_textos()["ru"]["leccion"]
        p = self._pagina(plan.dia(CAL, 15, 2))
        self.assertIn(f'data-ver="{html.escape(L["clave_ver"])}"', p)
        self.assertIn(f'data-ocultar="{html.escape(L["clave_ocultar"])}"', p)


class TestLaRedDeYandex(unittest.TestCase):
    """РСЯ, la otra mitad del público.

    AdSense no sirve anuncios a usuarios dentro de Rusia desde marzo de 2022 y
    este curso está escrito en ruso, así que una parte grande de los lectores
    cae justo en ese hueco. Lo que estas pruebas vigilan no es el dinero sino
    las dos cosas que se rompen en silencio: que se cargue algo de terceros
    cuando la política de privacidad dice que no, y que dos redes se peleen por
    el mismo hueco."""

    BLOQUE = "R-A-20290424-1"

    def setUp(self):
        self.textos = construir_sitio.cargar_textos()
        self.cfg = construir_sitio.cargar_config()

    def _con(self, yandex=None, adsense=None):
        cfg = copy.deepcopy(self.cfg)
        cfg["adsense"] = adsense or {"cliente": "", "bloques": {}}
        cfg["analitica"] = {"google": ""}
        cfg["yandex"] = {"bloques": yandex or {}}
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, cfg, self.textos)
        return destino

    def test_apagado_no_carga_nada_de_yandex(self):
        """Vacío = cero scripts de terceros, que es lo que deja que la política
        de privacidad diga la verdad."""
        p = (self._con() / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        for rastro in ("context.js", "yaContextCb", "yandex_rtb"):
            self.assertNotIn(rastro, p, rastro)

    def test_el_cargador_va_una_sola_vez_aunque_haya_tres_bloques(self):
        """`context.js` se instala una vez por página y sirve para todos los
        huecos. Tres copias serían tres descargas del mismo guion."""
        p = (self._con({"cabecera": self.BLOQUE, "dentro": self.BLOQUE,
                        "pie": self.BLOQUE}) / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertEqual(p.count("ads/system/context.js"), 1)
        self.assertEqual(p.count('class="anuncio"'), 3)

    def test_el_contenedor_y_el_render_apuntan_al_mismo_id(self):
        """Si el `renderTo` no casa con el id del `<div>`, Yandex no pinta nada
        y la página se queda con un hueco mudo: no falla, no avisa."""
        p = (self._con({"pie": self.BLOQUE}) / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        destino = f"yandex_rtb_{self.BLOQUE}"
        self.assertIn(f'<div id="{destino}"></div>', p)
        self.assertIn(f'"renderTo":"{destino}"', p)
        self.assertIn(f'"blockId":"{self.BLOQUE}"', p)

    def test_un_hueco_una_red(self):
        """Dos anuncios en el mismo contenedor no es una opción. Con los dos
        identificadores puestos manda Yandex, porque AdSense funciona en
        anuncios automáticos y no usa estas tres ranuras."""
        destino = self._con({"pie": self.BLOQUE},
                            adsense={"cliente": "ca-pub-1", "bloques": {"pie": "333"}})
        p = (destino / "semana-01" / "dia-1.html").read_text(encoding="utf-8")
        self.assertIn("yandex_rtb", p)
        self.assertNotIn('data-ad-slot="333"', p)

    def test_enciende_el_aviso_de_cookies_y_la_politica(self):
        """Cargar una red de publicidad y no decirlo es exactamente la forma de
        que la política de privacidad mienta."""
        destino = self._con({"pie": self.BLOQUE})
        self.assertIn('id="cookies"', (destino / "index.html").read_text(encoding="utf-8"))
        priv = (destino / "es" / "privacy.html").read_text(encoding="utf-8")
        self.assertIn(self.textos["es"]["privacidad"]["anuncios_yandex"][:40], priv)
        self.assertIn("yandex.ru/support", priv, "hace falta el enlace para desactivar")
        sin = (self._con() / "es" / "privacy.html").read_text(encoding="utf-8")
        self.assertNotIn("Yandex", sin)

    def test_el_identificador_no_puede_inyectar_codigo(self):
        """El identificador sale de un YAML que edita una persona a mano y se
        escribe DENTRO de un `<script>`, donde `html.escape` no protege de
        nada: una comilla cerraría la llamada. Por eso se limpia a lo que un
        bloque de РСЯ puede ser."""
        sucio = construir_sitio._anuncio_yandex('R-A-1"});alert(1);//<script>')
        # Las letras sobreviven y no pasa nada: lo que no puede sobrevivir es
        # un carácter que cierre la cadena, la llamada o la etiqueta.
        for malo in ('"', "'", "}", ")", ";", "/", "<", ">", " "):
            self.assertNotIn(malo, sucio.split('"blockId":"')[1].split('"')[0],
                             f"el identificador deja pasar {malo!r}")
        self.assertEqual(sucio.count("<script>"), 1, "no se puede abrir un segundo script")

    def test_los_tres_idiomas_tienen_el_texto_de_la_politica(self):
        for i in ("ru", "es", "en"):
            self.assertTrue(self.textos[i]["privacidad"]["anuncios_yandex"].strip(), i)


class TestLaTipografia(unittest.TestCase):
    """Literata y Onest, servidas desde este dominio.

    El profesor preguntó si la fuente no era aburrida, y lo era por una razón
    concreta: el sitio no cargaba NINGUNA. El cuerpo decía `ui-serif, Georgia,
    "Times New Roman"` y los títulos `ui-sans-serif, system-ui`, así que en
    Windows y en Android el cirílico caía en Times o en una fallback mediocre
    —la cara de un libro de texto de 1998— mientras que en iPhone caía en New
    York y se veía bien. El sitio se veía peor justo en los aparatos del
    público al que va dirigido, y eso no se ve desde un Mac.

    Estas pruebas no construyen el sitio: `caras()` es una función pura y las
    rutas se resuelven contra el disco. Así son baratas y se pueden correr sin
    esperar una construcción entera."""

    FUENTES = RAIZ / "docs" / "fonts"

    def test_cada_cara_nombra_un_fichero_que_existe(self):
        nombres = re.findall(r"url\(\{raiz\}/fonts/([^)]+)\)", construir_sitio.CARAS)
        self.assertTrue(nombres, "CARAS no declara ninguna @font-face")
        for n in nombres:
            self.assertTrue((self.FUENTES / n).exists(), f"falta docs/fonts/{n}")

    def test_las_rutas_resuelven_desde_las_tres_profundidades(self):
        """Es el fallo que esta suite ya cazó TRES veces por el mismo motivo:
        una ruta escrita sin tener en cuenta en qué carpeta está la página —el
        conmutador de idioma, las tarjetas del mapa de unidades y los destinos
        del probador—. Y aquí no lo cazaría nadie más: `revisar_adsense.py`
        mira `href=` y `src=`, no los `url()` de una hoja de estilo."""
        for pagina, raiz in (("docs/index.html", "."),
                             ("docs/es/index.html", ".."),
                             ("docs/en/index.html", ".."),
                             ("docs/semana-01/dia-1.html", "..")):
            base = (RAIZ / pagina).parent
            for u in re.findall(r"url\(([^)]+)\)", construir_sitio.caras(raiz)):
                self.assertTrue((base / u).resolve().exists(),
                                f"desde {pagina} la fuente {u} no resuelve")

    def test_cada_cara_trae_su_unicode_range(self):
        """Sin `unicode-range` el navegador se baja las diez caras en cuanto
        pinta la página. Con él, una lección rusa no toca el latino hasta que
        encuentra el primer ejemplo español."""
        for bloque in construir_sitio.CARAS.split("@font-face")[1:]:
            self.assertIn("unicode-range", bloque)
            self.assertIn("font-display:swap", bloque)

    def test_hay_cursiva_de_verdad(self):
        """El curso pone TODOS los ejemplos españoles en <em>. Sin cursiva
        real el navegador inclina la redonda y deja medio curso sucio."""
        self.assertIn("font-style:italic", construir_sitio.CARAS)

    def test_no_se_enlaza_a_google_fonts(self):
        """Dos razones y ninguna es manía: la política de privacidad de este
        sitio promete que sin anuncios no se carga nada de terceros, y un
        enlace a fonts.googleapis.com la volvería mentira; y hay sentencias
        alemanas que multan por incrustar Google Fonts, porque manda la IP del
        visitante a Google. Alemania es uno de los países del público."""
        for dominio in ("fonts.googleapis.com", "fonts.gstatic.com"):
            self.assertNotIn(dominio, construir_sitio.CARAS)
            self.assertNotIn(dominio, construir_sitio.CSS)

    def test_las_pilas_empiezan_por_la_fuente_propia(self):
        self.assertIn("font:400 17px/1.65 Literata,", construir_sitio.CSS)
        self.assertIn("h1,h2,h3{font-family:Onest,", construir_sitio.CSS)

    def test_la_hoja_no_se_queda_con_el_marcador_sin_resolver(self):
        """`CSS` no puede pasar por `.format()` —está llena de llaves de CSS—,
        así que las caras se concatenan con `caras(raiz)`. Si alguien las
        metiera dentro de `CSS`, el `{raiz}` llegaría literal al navegador y
        ninguna fuente cargaría, sin que nada fallara."""
        self.assertNotIn("{raiz}", construir_sitio.CSS)
        self.assertNotIn("{raiz}", construir_sitio.caras(".."))


class TestElFondoDeLosDibujos(unittest.TestCase):
    """Los 300 dibujos tienen que compartir EXACTAMENTE un crema.

    El generador devuelve cada uno sobre un fondo parecido pero nunca igual, y
    —lo que de verdad se ve— distinto entre un dibujo y otro: medido antes de
    corregirlos, el libro estaba en (242,233,218) y el perro en (255,248,236).
    A 56 px en una tabla no se nota; a 96 px y en fila, que es como salen los
    seis de la portada, se lee como que unas fichas están más sucias que otras.
    Lo vio el profesor comparando el móvil con el escritorio.

    La prueba mira los DOCE de la portada, que son los que se ven grandes."""

    def test_los_doce_de_la_portada_comparten_el_crema(self):
        indice = RAIZ / "docs" / "img" / "indice.json"
        if not indice.exists():
            self.skipTest("no hay dibujos generados")
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("sin Pillow")
        sys.path.insert(0, str(RAIZ / "scripts"))
        import igualar_dibujos
        objetivo = igualar_dibujos.crema_de_la_pagina()
        idx = json.loads(indice.read_text(encoding="utf-8"))
        vistos = 0
        for palabra in construir_sitio.PORTADA_DIBUJOS:
            nombre = idx.get(palabra)
            if not nombre:
                continue
            ruta = RAIZ / "docs" / "img" / nombre
            if not ruta.exists():
                continue
            vistos += 1
            fondo = igualar_dibujos.fondo_de(Image.open(ruta).convert("RGB"))
            peor = max(abs(fondo[c] - objetivo[c]) for c in range(3))
            self.assertLessEqual(peor, 3, f"{palabra}: fondo {fondo}, esperado {objetivo}")
        self.assertEqual(vistos, 12)

    def test_el_objetivo_sale_del_css_y_es_el_de_la_ficha(self):
        """Escrito a mano aquí y en el CSS, el día que cambie la paleta se
        arregla uno y el otro se queda viejo."""
        sys.path.insert(0, str(RAIZ / "scripts"))
        import igualar_dibujos
        m = re.search(r"--tarjeta:\s*#([0-9a-fA-F]{6})", construir_sitio.CSS)
        self.assertIsNotNone(m)
        esperado = tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4))
        self.assertEqual(igualar_dibujos.crema_de_la_pagina(), esperado)


class TestElArteDelHeroe(unittest.TestCase):
    """Los dibujos suben a la primera pantalla.

    Medida la portada del móvil, lo que se veía antes de hacer scroll eran
    cinco líneas de letra sobre crema y ni una imagen: los doce dibujos
    —lo único que este sitio tiene y nadie más, y que ya está pagado— empezaban
    DEBAJO del pliegue, bajo un `<h2>`. O sea que el mejor activo de la página
    era invisible justo en el segundo en que el visitante decide si se queda."""

    def setUp(self):
        indice = RAIZ / "docs" / "img" / construir_sitio.INDICE_IMG
        self.dibujos = json.loads(indice.read_text(encoding="utf-8")) if indice.exists() else {}

    def test_salen_los_dibujos_y_los_ficheros_estan(self):
        if not self.dibujos:
            self.skipTest("sin dibujos generados")
        arte = construir_sitio._arte_del_heroe(self.dibujos, "..")
        imgs = re.findall(r'src="\.\./img/([^"]+)"', arte)
        self.assertEqual(len(imgs), construir_sitio.HEROE_DIBUJOS)
        for i in imgs:
            self.assertTrue((RAIZ / "docs" / "img" / i).exists(), f"falta docs/img/{i}")

    def test_es_decoracion_y_no_interfaz(self):
        """Lo que se puede pulsar y oír es la vitrina de abajo, que además
        enseña la palabra y su traducción. Esta tira solo pone color: si un
        lector de pantalla la leyera, diría doce veces lo mismo."""
        if not self.dibujos:
            self.skipTest("sin dibujos generados")
        arte = construir_sitio._arte_del_heroe(self.dibujos, ".")
        self.assertIn('aria-hidden="true"', arte)
        self.assertNotIn("<a ", arte)
        self.assertNotIn("<button", arte)
        self.assertEqual(arte.count('alt=""'), construir_sitio.HEROE_DIBUJOS)

    def test_se_cae_sola_y_en_silencio(self):
        """Igual que la vitrina, la baraja y el audio: el sitio se construye
        con todo y sin nada. Y por debajo del mínimo no sale la tira entera,
        porque cuatro dibujos sueltos en una fila pensada para seis se leen
        como una página a medio cargar."""
        self.assertEqual(construir_sitio._arte_del_heroe({}, "."), "")
        pocos = dict(list(self.dibujos.items())[:construir_sitio.HEROE_MINIMO - 1])
        self.assertEqual(construir_sitio._arte_del_heroe(pocos, "."), "")

    def test_no_son_dibujos_nuevos(self):
        """Son los MISMOS ficheros que la vitrina de abajo, así que el
        navegador los sirve de caché y no cuestan un byte más."""
        if not self.dibujos:
            self.skipTest("sin dibujos generados")
        arte = set(re.findall(r'src="\./img/([^"]+)"',
                              construir_sitio._arte_del_heroe(self.dibujos, ".")))
        de_la_vitrina = {self.dibujos[generar_imagenes.limpiar(p)]
                         for p in construir_sitio.PORTADA_DIBUJOS
                         if generar_imagenes.limpiar(p) in self.dibujos}
        self.assertTrue(arte <= de_la_vitrina)


class TestElEnlaceDelTestDeNivel(unittest.TestCase):
    """«¿Ya sabe algo de español? Test de nivel →» eran dos titulares seguidos.

    Lo trajo el profesor: «y esto suena confuso». Tenía razón y el motivo es
    concreto: el enlace reusaba el TÍTULO de la página del test, que es un
    sintagma nominal, no una acción, y no dice para qué sirve. Ahora cada
    idioma tiene su propia etiqueta y dice lo único que importa: que el test
    te coloca en la lección por la que empezar."""

    def setUp(self):
        self.textos = construir_sitio.cargar_textos()

    def test_los_tres_idiomas_tienen_etiqueta_propia(self):
        for codigo in ("ru", "es", "en"):
            p = self.textos[codigo]["portada"]
            self.assertTrue(p.get("ya_sabe_enlace"), f"{codigo} sin ya_sabe_enlace")
            self.assertNotEqual(p["ya_sabe_enlace"], self.textos[codigo]["test"]["titulo"],
                                f"{codigo}: el enlace vuelve a ser el título de la página")

    def test_el_boton_de_restaurar_dice_que_restaura(self):
        """«Restaurar con un código» no significa nada para quien acaba de
        llegar —y ese botón está visible precisamente para él, porque el que
        limpió el navegador no tiene progreso que enseñar—. Ahora nombra lo que
        recupera; de dónde sale el código lo explica la caja al abrirse."""
        for codigo in ("ru", "es", "en"):
            pr = self.textos[codigo]["progreso"]
            self.assertNotIn("код", pr["restaurar"].lower())
            self.assertNotIn("código", pr["restaurar"].lower())
            self.assertNotIn("code", pr["restaurar"].lower())

    def test_el_espanol_trata_de_usted_en_todo_el_bloque_del_progreso(self):
        """El sitio español trata de usted (24 cadenas contra 6), pero el
        bloque del respaldo se había escrito de tú: «pégalo en tus notas»,
        «Pega aquí tu código», «guarda tu código». Mezclar las dos formas en la
        misma pantalla se nota más que una falta de ortografía."""
        # Solo las marcas que no admiten otra lectura: posesivos, pronombres y
        # formas verbales de segunda persona. `guarda`, `pega` y `empieza` se
        # quedan fuera a propósito —son también tercera persona, y «el progreso
        # SE GUARDA solo en este navegador» no trata de tú—. Con los posesivos
        # basta: cazaban cinco de las seis cadenas que había que cambiar.
        TU = re.compile(r"\b(tus?|tú|ti|te|contigo|tienes|sabes|puedes|quieres)\b", re.I)
        for clave, texto in self.textos["es"]["progreso"].items():
            if isinstance(texto, str):
                self.assertIsNone(TU.search(texto), f"progreso.{clave} trata de tú: {texto!r}")
