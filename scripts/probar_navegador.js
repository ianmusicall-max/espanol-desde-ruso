#!/usr/bin/env node
/**
 * Abre páginas del sitio ya construido en Chromium, las USA, y cuenta lo que
 * pasa. Imprime una línea JSON por página.
 *
 *   node scripts/probar_navegador.js docs/semana-21/dia-2.html …
 *   node scripts/probar_navegador.js            # unas cuantas representativas
 *
 * Por qué existe. Todo lo que este proyecto da por «comprobado en navegador»
 * se comprobó a mano, una vez, y nunca más. Así es como el test de unidad
 * estuvo roto desde el día que se publicó: `pregunta()` leía una variable
 * `preguntas` que nadie declaraba, el papel se escondía al pulsar «empezar» y
 * en su lugar no salía nada. El lector en Python estaba comprobado; el botón,
 * no. Un ReferenceError no se ve leyendo el HTML ni contando etiquetas.
 *
 * Lo que mira, en este orden:
 *  - errores de JavaScript en la página (cero, siempre);
 *  - si hay un test contestable, lo CONTESTA ENTERO eligiendo la opción
 *    correcta por su TEXTO —no por su letra ni por su posición— y exige que el
 *    resultado sea todo aciertos. Comparar con la posición sería repetir la
 *    cuenta del propio guion y no probaría nada;
 *  - que la versión en papel quede escondida y el botón de empezar, visible.
 */
const { chromium } = require('playwright');
const path = require('path');

const POR_DEFECTO = [
  'docs/index.html',                 // portada: vitrina, probador de tres preguntas
  'docs/test.html',                  // test de nivel
  'docs/semana-21/dia-2.html',       // repaso con Мини-тест pulsable
  'docs/semana-27/dia-6.html',       // el Мини-тест que tenía 14 de 15 en la б)
  'docs/semana-32/dia-6.html',       // test de unidad
  'docs/semana-33/dia-6.html',       // repaso de producción: NO debe volverse test
  'docs/semana-37/dia-6.html',       // Мини-тест de 20 ítems, el más largo del curso
  'docs/semana-38/dia-6.html',       // test de unidad recién escrito
  'docs/semana-41/dia-6.html',       // repaso de la unidad 21: Мини-тест de 15
  'docs/semana-42/dia-6.html',       // test de la unidad 21
  'docs/semana-43/dia-6.html',       // repaso de la unidad 22: Мини-тест de 15
  'docs/semana-44/dia-6.html',       // test de la unidad 22
  'docs/semana-45/dia-6.html',       // repaso de la unidad 23: Мини-тест de 20 (ortografía)
  'docs/semana-46/dia-6.html',       // test de la unidad 23
  'docs/semana-47/dia-5.html',       // repaso de la unidad 24: Мини-тест de 20
  'docs/semana-48/dia-6.html',       // test de la unidad 24: 40 ítems
  'docs/semana-50/dia-6.html',       // el quiz de 50 ítems: el test más largo del curso
  'docs/semana-52/dia-1.html',       // repaso de la fase final: sin unidad en el frontmatter
  'docs/semana-49/dia-1.html',       // simulacro: el tipo de día que no es un test contestable
  'docs/semana-53/dia-1.html',       // el día 365: `reserva`, único de su tipo en el curso
  'docs/semana-01/dia-1.html',       // lección normal: audio y huecos
];

async function unaPagina(b, rel) {
  const p = await b.newPage();
  const errores = [];
  p.on('pageerror', e => errores.push(String(e)));
  await p.goto('file://' + path.resolve(rel));

  const r = { pagina: rel, test: null, aciertos: null, errores: [] };

  // La guia de los pasos se recorre PRIMERO y desde arriba del todo. Puesta
  // detras del test, arrancaba donde el test habia dejado el scroll y el
  // recorrido salia corrido: el fallo era de esta comprobacion y no de la
  // guia, que es justo el error que mas cuesta ver en una prueba.
  const guia = p.locator('#guia');
  if (await guia.count() && await guia.isVisible()) {
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.waitForTimeout(350);
    const pasos = await p.locator('.guia-punto').count();
    const desde = parseInt(await p.locator('.guia-punto.aqui').first().getAttribute('data-i'), 10);
    const recorrido = [];
    for (let k = 0; k < pasos - 1; k++) {
      await p.locator('.guia-ir').click();
      await p.waitForTimeout(450);
      recorrido.push(parseInt(await p.locator('.guia-punto.aqui').first().getAttribute('data-i'), 10));
    }
    r.guia = pasos;
    r.guia_desde = desde;
    r.guia_recorrido = recorrido;
    // Cada clic avanza uno hasta el ultimo paso; alli «Дальше» ya no avanza,
    // lleva al boton de marcar la leccion, asi que el indice se queda.
    r.guia_avanza = desde === 0 && recorrido.every((v, i) => v === Math.min(i + 1, pasos - 1));
    if (!r.guia_avanza) r.errores.push('la guia no avanza uno por clic: ' + desde + ' -> ' + recorrido.join(','));
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.waitForTimeout(250);
  }

  const hayTest = await p.evaluate(() => !!(window.CURSO_PRUEBA && window.CURSO_PRUEBA.preguntas));
  if (hayTest) {
    const correctas = await p.evaluate(() =>
      window.CURSO_PRUEBA.preguntas.map(q => q.opciones[q.correcta]));
    r.test = correctas.length;
    r.papel_escondido = await p.locator('#prueba-papel').isHidden();
    await p.locator('#prueba-empezar').click();
    let bien = 0;
    for (const texto of correctas) {
      const bs = p.locator('#prueba .test-ops button');
      const n = await bs.count();
      let pulsado = false;
      for (let k = 0; k < n; k++) {
        if ((await bs.nth(k).textContent()).trim() === texto) { await bs.nth(k).click(); pulsado = true; bien++; break; }
      }
      if (!pulsado) { r.errores.push('no encontré la opción: ' + texto); break; }
    }
    r.aciertos = bien;
    const txt = (await p.locator('#prueba').textContent()).replace(/\s+/g, ' ');
    r.resultado = txt.slice(0, 80);
    r.dice_todo_bien = txt.includes(bien + ' / ' + correctas.length);
  }
  r.errores = r.errores.concat(errores);
  await p.close();
  return r;
}

(async () => {
  const paginas = process.argv.slice(2).length ? process.argv.slice(2) : POR_DEFECTO;
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  let malas = 0;
  for (const rel of paginas) {
    const r = await unaPagina(b, rel);
    const roto = r.errores.length || (r.test && (r.aciertos !== r.test || !r.dice_todo_bien));
    if (roto) malas++;
    console.log(JSON.stringify(r));
  }
  await b.close();
  process.exit(malas ? 1 : 0);
})();
