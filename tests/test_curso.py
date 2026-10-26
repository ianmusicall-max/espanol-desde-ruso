"""Pruebas del curso: el calendario, las lecciones y los scripts cuentan lo mismo.

    .venv/bin/python -m unittest tests.test_curso
"""
from __future__ import annotations

import copy
import html
import json
import pathlib
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from collections import Counter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import construir_sitio  # noqa: E402
import exportar_wordpress  # noqa: E402
import escribir_leccion  # noqa: E402
import exportar_anki  # noqa: E402
import plan  # noqa: E402
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

    def test_una_unidad_sin_lecciones_toma_un_modelo_del_mismo_tipo_de_la_unidad_1(self):
        """Sin un modelo propio de ese tipo, el prompt presta el de la unidad 1.

        La unidad se busca en el momento, no se fija: a medida que se escriben
        semanas, la primera unidad vacía se mueve, y un número escrito a mano
        dejaría la prueba verde sin comprobar nada."""
        vacia = next(
            u for u in CAL["unidades"]
            if not any(d.ruta.exists() for d in DIAS if d.unidad == u["numero"])
        )
        primera_semana = vacia["semanas"][0]
        for dia_n, modelo in ((6, "curso/semana-01/dia-6.md"), (7, "curso/semana-01/dia-7.md")):
            d = plan.dia(CAL, primera_semana, dia_n)
            sistema, _ = escribir_leccion.armar_prompt(CAL, d)
            self.assertIn(modelo, sistema[1]["text"], f"{d.etiqueta} ({d.tipo})")

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
        destino = pathlib.Path(tempfile.mkdtemp())
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
        cfg = copy.deepcopy(self.cfg)
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


if __name__ == "__main__":
    unittest.main()
