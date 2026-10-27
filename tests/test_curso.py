"""Pruebas del curso: el calendario, las lecciones y los scripts cuentan lo mismo.

    .venv/bin/python -m unittest tests.test_curso
"""
from __future__ import annotations

import copy
import html
import json
import pathlib
import re
import shutil
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
import exportar_apkg  # noqa: E402
import poner_dominio  # noqa: E402
import revisar_adsense  # noqa: E402
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
        destino = pathlib.Path(tempfile.mkdtemp())
        construir_sitio.construir(destino, self.cfg, self.textos)
        for i in self.textos["idiomas"]:
            carpeta = destino / i["carpeta"] if i["carpeta"] else destino
            portada = carpeta.joinpath("index.html").read_text(encoding="utf-8")
            self.assertIn('class="progreso-nota"', portada, i["codigo"])
            self.assertNotIn("{n}", portada, f'{i["codigo"]}: quedó el hueco sin rellenar')
            self.assertNotIn("{meses}", portada, i["codigo"])

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
        """Prometer una puerta que no abre es peor que enseñarla cerrada."""
        html_ = self._indice()
        self.assertIn("u-tarjeta vacia", html_)

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
        """Las demás caen en la última escrita, que es la respuesta honrada: si
        ya sabe todo lo que el curso cubre, ahí es donde empieza."""
        datos = self._datos()
        escritas = {d.unidad for d in construir_sitio.escritas(CAL)}
        self.assertEqual({int(u) for u in datos["inicios"]}, escritas)

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
        """La unidad 1 está revisada y su clave dice: Léxico б в б б б а,
        Gramática в б г б б а, Ortografía б в в. Si el analizador leyera otra
        cosa, el test corregiría mal y nadie se enteraría."""
        ruta = RAIZ / "curso" / "semana-02" / "dia-6.md"
        preguntas = pruebas.de_la_leccion(ruta)
        self.assertIsNotNone(preguntas)
        letras = "".join(pruebas.LETRAS[q.correcta] for q in preguntas)
        self.assertEqual(letras, "бвбббавбгббабвв")

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
        """El fallo seguro: antes que corregir mal, no ofrecer el test."""
        bueno = (RAIZ / "curso" / "semana-02" / "dia-6.md").read_text(encoding="utf-8")
        _, cuerpo = validar.frontmatter(bueno)
        self.assertIsNotNone(pruebas.leer(cuerpo))
        # una respuesta de menos en el primer bloque
        roto = cuerpo.replace("5 б (нед. 2, день 5) · 6 а", "6 а", 1)
        self.assertIsNone(pruebas.leer(roto))
        # una letra que no existe entre las opciones
        roto = cuerpo.replace("**1. Лексика:** 1 б", "**1. Лексика:** 1 д", 1)
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
