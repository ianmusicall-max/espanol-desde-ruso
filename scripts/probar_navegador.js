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
const http = require('http');
const fs = require('fs');
const path = require('path');

// El sitio se sirve por HTTP y no se abre como archivo. No es cosmetico: sobre
// file:// el navegador no resuelve play() —asi que `aria-pressed` se queda en
// false con el codigo bien— y la peticion del MP3 no se observa, o sea que el
// audio no se puede comprobar de ninguna manera. Y ademas es lo que hace un
// lector de verdad.
const TIPOS = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
                '.json': 'application/json', '.mp3': 'audio/mpeg', '.webp': 'image/webp',
                '.png': 'image/png', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };

function servir(raiz) {
  return new Promise(ok => {
    const s = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '');
      const f = path.join(raiz, rel);
      if (!f.startsWith(raiz) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) {
        res.writeHead(404); return res.end('no');
      }
      // Content-Length NO es decorativo aqui: sin el, la comprobacion del audio
      // lee 0 bytes y acusa de muda a toda pagina que suene. Un servidor de
      // verdad lo manda, asi que mandarlo es ademas lo fiel.
      res.writeHead(200, { 'Content-Type': TIPOS[path.extname(f)] || 'application/octet-stream',
                           'Content-Length': fs.statSync(f).size });
      fs.createReadStream(f).pipe(res);
    });
    s.listen(0, '127.0.0.1', () => ok(s));
  });
}

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
  'docs/semana-01/dia-2.html',       // las tarjetas del día: las 8 primeras del curso
  'docs/semana-31/dia-2.html',       // clave en NEGRITA: daba 0 aciertos con todo bien
  // Las cuatro siguientes no tenían un solo ▶ hasta el 2026-10-28: el audio
  // del curso llegaba a la lección 100 y se paraba. Están aquí para que el
  // día que el audio se rompa se entere la suite y no un lector.
  'docs/semana-15/dia-3.html',       // la 101: la primera del tramo que faltaba
  'docs/semana-30/dia-3.html',
  'docs/semana-45/dia-1.html',
  'docs/semana-52/dia-7.html',
  // La tabla de fonética donde el profesor pulsó la «y» y no sonó nada: sus
  // dos letras estaban entre los 14 mudos, y las dos volvieron con voz.
  'docs/semana-01/dia-3.html',
  // El indice, que es donde vive el calendario del ano. Se siembra progreso
  // antes de mirarlo: sin lecciones marcadas no se dibuja, que es su regla.
  'docs/kurs.html',
  // El diccionario, que desde el 2026-10-30 tiene los dos sentidos. El ruso
  // NO viene servido: lo arma el guion con las filas de la pagina, asi que
  // leyendo el HTML no se ve ni una entrada rusa.
  'docs/slovar.html',
];

async function unaPagina(b, rel, base) {
  const p = await b.newPage();
  const errores = [];
  const mp3 = [];
  p.on('pageerror', e => errores.push(String(e)));
  p.on('response', res => {
    if (/\.mp3(\?|$)/.test(res.url())) {
      mp3.push({ estado: res.status(), bytes: Number(res.headers()['content-length'] || 0) });
    }
  });
  await p.goto(base + rel.replace(/^docs\//, ''));

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
  // El quiz de las palabras del dia. Se contesta eligiendo por el TEXTO de la
  // opcion, nunca por su letra ni por su posicion: por la letra seria repetir
  // la cuenta del propio generador y la comprobacion no probaria nada.
  const hayQuiz = await p.evaluate(() => !!(window.CURSO_QUIZ && window.CURSO_QUIZ.preguntas));
  if (hayQuiz) {
    const correctas = await p.evaluate(() =>
      window.CURSO_QUIZ.preguntas.map(q => q.opciones[q.correcta]));
    r.quiz = correctas.length;
    await p.locator('#quiz-empezar').click();
    let bien = 0;
    for (const texto of correctas) {
      const bs = p.locator('#quiz .test-ops button');
      const n = await bs.count();
      let pulsado = false;
      for (let k = 0; k < n; k++) {
        if ((await bs.nth(k).textContent()).trim() === texto) { await bs.nth(k).click(); pulsado = true; bien++; break; }
      }
      if (!pulsado) { r.errores.push('quiz: no encontré la opción: ' + texto); break; }
    }
    r.quiz_aciertos = bien;
    const txt = (await p.locator('#quiz').textContent()).replace(/\s+/g, ' ');
    r.quiz_bien = txt.includes(bien + ' / ' + correctas.length);
    if (!r.quiz_bien) r.errores.push('el quiz no da ' + bien + '/' + correctas.length + ': ' + txt.slice(0, 80));
  }

  // Los huecos que se rellenan pulsando. Se comprueban las tres cosas que el
  // profesor vio rotas el 2026-10-30: que al colocar una palabra se APAGUE su
  // ficha —y no solo la ultima del banco—, que el boton de comprobar este
  // DESPUES de las frases y no antes, y que al fallar salga la respuesta
  // correcta pegada al hueco en vez de obligar a bajar hasta la clave.
  const hayHuecos = await p.evaluate(() => !!(window.CURSO_HUECOS && window.CURSO_HUECOS.ejercicios));
  if (hayHuecos) {
    const h = await p.evaluate(() => {
      const plano = x => (x || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
      const e = '0';
      const D = window.CURSO_HUECOS.ejercicios[e];
      const hs = [...document.querySelectorAll('.hueco[data-ej="' + e + '"]')];
      const fs = [...document.querySelectorAll('.ficha[data-ej="' + e + '"]')];
      const pie = document.querySelector('.comprobar[data-ej="' + e + '"]');
      const banco = document.querySelector('.fichas[data-ej="' + e + '"]');
      const sitio = {
        bancoArriba: !!(hs[0].compareDocumentPosition(banco) & Node.DOCUMENT_POSITION_PRECEDING),
        pieAbajo: !!(hs[hs.length - 1].compareDocumentPosition(pie) & Node.DOCUMENT_POSITION_FOLLOWING),
      };
      for (let k = 0; k < hs.length; k++) {
        const f = fs.find(x => plano(x.textContent) === plano(D.respuestas[k]) && !x.classList.contains('gastada'));
        if (!f) return Object.assign(sitio, { fallo: 'sin ficha libre para ' + D.respuestas[k] });
        f.click(); hs[k].click();
      }
      const gastadas = fs.filter(x => x.classList.contains('gastada')).length;
      pie.click();
      const pistasBien = document.querySelectorAll('.correcta').length;
      // Y ahora un fallo a proposito, para ver la respuesta correcta.
      hs[0].click();
      const mala = fs.find(x => plano(x.textContent) !== plano(D.respuestas[0]));
      mala.click(); hs[0].click();
      pie.click();
      const pistas = [...document.querySelectorAll('.correcta')].map(x => x.textContent);
      return Object.assign(sitio, {
        huecos: hs.length, fichas: fs.length, gastadas: gastadas,
        pistasConTodoBien: pistasBien, pistas: pistas, debia: D.respuestas[0],
      });
    });
    r.huecos = h.huecos;
    if (h.fallo) r.errores.push('huecos: ' + h.fallo);
    if (!h.bancoArriba) r.errores.push('huecos: el banco de fichas no esta antes de las frases');
    if (!h.pieAbajo) r.errores.push('huecos: comprobar no esta debajo del ejercicio');
    if (h.gastadas !== h.fichas) r.errores.push('huecos: se apagaron ' + h.gastadas + ' de ' + h.fichas + ' fichas');
    if (h.pistasConTodoBien !== 0) r.errores.push('huecos: sale la respuesta correcta con todo bien');
    if (h.pistas && (h.pistas.length !== 1 || h.pistas[0] !== h.debia)) {
      r.errores.push('huecos: al fallar no sale la correcta: ' + JSON.stringify(h.pistas));
    }
  }

  // Las tarjetas del dia: se dan la vuelta y se pasa a la siguiente.
  const hayFichas = await p.evaluate(() => !!(window.CURSO_TARJETAS && window.CURSO_TARJETAS.fichas));
  if (hayFichas) {
    const caja = p.locator('#tarjetas');
    if (await caja.isHidden()) r.errores.push('tarjetas: el bloque no se encendio');
    const es = (await p.locator('#ficha-cara').textContent()).trim();
    await p.locator('#ficha-girar').click();
    const ru = (await p.locator('#ficha-cara').textContent()).trim();
    if (!ru || ru === es) r.errores.push('tarjetas: no se da la vuelta');
    await p.locator('#ficha-sig').click();
    const dos = (await p.locator('#ficha-cara').textContent()).trim();
    if (dos === ru) r.errores.push('tarjetas: la siguiente no cambia');
    r.tarjetas = await p.evaluate(() => window.CURSO_TARJETAS.fichas.length);
  }

  // El audio: que el boton SUENE, no que este puesto. La señal observable es
  // el MP3 pedido con 200 y con bytes, mas `aria-pressed`, que el reproductor
  // solo pone a true si play() resolvio —usa `new Audio()`, que no inserta
  // nada en el DOM, asi que no hay ningun <audio> que buscar—.
  const botones = p.locator('button:has-text("▶")');
  r.audio_botones = await botones.count();
  if (r.audio_botones) {
    // Se ESPERA a que el boton diga que suena, y se reintenta, en vez de
    // dormir un rato fijo. Los 800 ms que habia aqui bastaban casi siempre y
    // fallaban en UNA pagina al azar de las 25, distinta en cada corrida y
    // con su MP3 ya descargado (200 y bytes): la promesa de `play()` se queda
    // sin resolver cuando el contenedor no tiene salida de audio.
    //
    // Lo que NO se hizo es conformarse con el MP3: `aria-pressed` es la unica
    // señal de que play() resolvio, y era justo lo que esta guarda vino a
    // comprobar el 2026-10-28. Reintentar mantiene la exigencia y quita la
    // casualidad: una pagina de verdad muda falla los tres intentos.
    for (let intento = 0; intento < 3 && !r.audio_suena; intento++) {
      await botones.first().click();
      if (intento === 0) {
        try { await p.waitForResponse(res => /\.mp3/.test(res.url()), { timeout: 8000 }); } catch (e) {}
      }
      try {
        await p.waitForFunction(
          () => document.querySelector('button.suena[aria-pressed="true"]') !== null,
          null, { timeout: 5000 });
      } catch (e) {}
      r.audio_suena = (await botones.first().getAttribute('aria-pressed')) === 'true'
                      && mp3.length > 0 && mp3.every(m => m.estado === 200 && m.bytes > 1000);
      r.audio_intentos = intento + 1;
    }
    if (!r.audio_suena) r.errores.push('el ▶ no suena: ' + JSON.stringify(mp3));
  }
  // La rejilla del curso: no que ESTE, sino que las casillas del lector se
  // VEAN y que su rotulo diga la fecha. El profesor la denuncio dos veces: la
  // primera con la cabecera diciendo «2 dias» y las 364 casillas grises —las
  // marcadas existian y estaban fuera de la parte visible— y la segunda
  // porque marcaba una leccion mas el mismo dia y no cambiaba nada, que es
  // lo que pasa cuando la casilla es un DIA y no una leccion. Leyendo el
  // codigo no se ve ninguna de las dos.
  if (/kurs\.html$/.test(rel)) {
    await p.evaluate(() => {
      const hoy = new Date();
      const k = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0')
                     + '-' + String(d.getDate()).padStart(2, '0');
      // Tres lecciones DEL MISMO DIA: con la rejilla vieja eso era UNA
      // casilla, y es justo la queja.
      localStorage.setItem('curso.hechas', JSON.stringify([1, 2, 3]));
      localStorage.setItem('curso.fechas', JSON.stringify([k(hoy)]));
      localStorage.setItem('curso.cuando', JSON.stringify({ 1: k(hoy), 2: k(hoy) }));
    });
    await p.reload({ waitUntil: 'load' });
    await p.waitForTimeout(600);
    const cal = await p.evaluate(() => {
      const rj = document.querySelector('.cal-rejilla');
      if (!rj) return null;
      const caja = rj.getBoundingClientRect();
      const dentro = c => {
        const b = c.getBoundingClientRect();
        return b.x >= caja.x - 1 && b.right <= caja.right + 1;
      };
      const hechas = [...rj.children].filter(c => c.classList.contains('hecho'));
      const aqui = [...rj.children].find(c => c.classList.contains('aqui'));
      return {
        casillas: rj.children.length,
        hechas: hechas.length,
        hechas_visibles: hechas.filter(dentro).length,
        con_fecha: hechas.filter(c => /\d{4}-\d{2}-\d{2}/.test(c.title)).length,
        aqui: aqui ? aqui.title : null,
        aqui_visible: !!aqui && dentro(aqui),
        desborda: rj.scrollWidth > rj.clientWidth,
        color: hechas.length ? getComputedStyle(hechas[0]).backgroundColor : null,
        vacio: getComputedStyle(rj.children[rj.children.length - 1]).backgroundColor,
      };
    });
    if (!cal) r.errores.push('la rejilla del curso no se dibujo con progreso');
    else {
      r.calendario = cal;
      // Una casilla por leccion: tres del mismo dia son TRES.
      if (cal.hechas !== 3) r.errores.push('la rejilla marco ' + cal.hechas + ' y no 3');
      if (cal.casillas !== 365)
        r.errores.push('la rejilla trae ' + cal.casillas + ' casillas y no 365');
      if (cal.hechas_visibles !== cal.hechas)
        r.errores.push('hay casillas marcadas fuera de la vista: '
                       + cal.hechas_visibles + ' de ' + cal.hechas);
      // Dos tienen fecha guardada y la tercera no: esa no se inventa ninguna.
      if (cal.con_fecha !== 2)
        r.errores.push('rotulos con fecha: ' + cal.con_fecha + ' y no 2');
      if (!cal.aqui_visible) r.errores.push('la casilla de «aqui lo dejo» no se ve');
      if (cal.aqui && !/ 4 /.test(cal.aqui))
        r.errores.push('«aqui lo dejo» no cae en la leccion 4: ' + cal.aqui);
      if (cal.color === cal.vacio) r.errores.push('una casilla marcada es del color de una vacia');
      if (cal.desborda) r.errores.push('las columnas del curso no caben en el escritorio');
    }
    // Y en el movil, que es donde la rejilla SI desborda y lo unico que pone
    // a la vista donde vas es el desplazamiento del guion.
    await p.setViewportSize({ width: 390, height: 780 });
    await p.reload({ waitUntil: 'load' });
    await p.waitForTimeout(600);
    const movil = await p.evaluate(() => {
      const rj = document.querySelector('.cal-rejilla');
      if (!rj) return null;
      const caja = rj.getBoundingClientRect();
      const a = [...rj.children].find(c => c.classList.contains('aqui'));
      const b = a && a.getBoundingClientRect();
      return { desborda: rj.scrollWidth > rj.clientWidth,
               aqui_visible: !!b && b.x >= caja.x - 1 && b.right <= caja.right + 1 };
    });
    r.calendario_movil = movil;
    if (!movil || !movil.aqui_visible)
      r.errores.push('en el movil la casilla de «aqui lo dejo» se queda fuera de la vista');
  }

  // El diccionario en los dos sentidos. Lo que se comprueba es lo que el HTML
  // no puede enseñar: que el boton aparezca —solo si `ruso.json` llego—, que
  // al pulsarlo salgan las entradas RUSAS con todos sus españoles juntos, y
  // que el ▶ de una entrada rusa siga diciendo la palabra ESPAÑOLA, que es la
  // que suena.
  if (/slovar\.html$/.test(rel)) {
    await p.waitForTimeout(800);
    const mando = p.locator('#dicc-sentido');
    if (!(await mando.isVisible())) {
      r.errores.push('el boton de los dos sentidos no aparecio');
    } else {
      const antes = await p.evaluate(() =>
        document.querySelectorAll('#dicc-lista li').length);
      await p.locator('#dicc-sentido button[data-dir="ru"]').click();
      await p.waitForTimeout(400);
      const d = await p.evaluate(() => {
        const ru = document.getElementById('dicc-ruso');
        const es = document.getElementById('dicc-lista');
        const fila = [...ru.querySelectorAll('li')]
          .find(li => li.querySelector('b').textContent.trim() === 'автобус');
        return {
          entradas: ru.querySelectorAll('li').length,
          es_oculta: es.hidden, ru_visible: !ru.hidden,
          cuenta: (document.getElementById('dicc-cuenta') || {}).textContent || '',
          autobus: fila ? fila.querySelector('i').textContent : null,
          cirilico: /^[\u0400-\u04FF]/.test(
            (ru.querySelector('li b') || {}).textContent || ''),
        };
      });
      r.diccionario = { es: antes, ru: d.entradas, autobus: d.autobus };
      if (!d.ru_visible || !d.es_oculta)
        r.errores.push('al cambiar de sentido las dos listas quedaron mal');
      if (d.entradas < 2000)
        r.errores.push('el sentido ruso trae ' + d.entradas + ' entradas');
      if (!d.cirilico)
        r.errores.push('la primera entrada del sentido ruso no empieza por una letra rusa');
      // «автобус» es la entrada que justifica este sentido: cinco formas de
      // decirlo que el sentido español no puede juntar.
      if (!d.autobus || d.autobus.split('·').length < 4)
        r.errores.push('«автобус» no trae sus cinco españoles: ' + d.autobus);
      // El ▶ de una entrada rusa suena en español: su rotulo tiene que ser la
      // palabra española y no la rusa del <b>, o el lector de pantalla miente.
      const voz = await p.evaluate(() => {
        const b = document.querySelector('#dicc-ruso li .suena');
        if (!b) return null;
        return { rotulo: b.getAttribute('aria-label') || '',
                 mp3: b.getAttribute('data-audio') || '',
                 urok: document.querySelectorAll('#dicc-ruso li:first-child .dicc-urok').length };
      });
      r.diccionario.voz = voz;
      if (!voz) r.errores.push('ninguna entrada rusa saco su ▶');
      else {
        if (/[\u0400-\u04FF]/.test(voz.rotulo))
          r.errores.push('el ▶ de una entrada rusa se anuncia en ruso: ' + voz.rotulo);
        if (voz.urok > 1)
          r.errores.push('la entrada rusa repitio el enlace a la leccion');
      }
      // Buscar en ruso filtra el sentido ruso.
      await p.fill('#dicc-buscar', 'автобус');
      await p.waitForTimeout(400);
      const filtradas = await p.evaluate(() =>
        [...document.querySelectorAll('#dicc-ruso li')].filter(li => !li.hidden).length);
      if (filtradas < 1 || filtradas > 30)
        r.errores.push('buscar «автобус» en el sentido ruso dejo ' + filtradas + ' entradas');
      await p.fill('#dicc-buscar', '');
      await p.waitForTimeout(300);
      // Y se vuelve: el sentido de siempre tiene que quedar como estaba.
      await p.locator('#dicc-sentido button[data-dir="es"]').click();
      await p.waitForTimeout(300);
      const vuelta = await p.evaluate(() => ({
        es: !document.getElementById('dicc-lista').hidden,
        ru: !document.getElementById('dicc-ruso').hidden,
      }));
      if (!vuelta.es || vuelta.ru) r.errores.push('no se vuelve al sentido español');
    }
  }

  r.errores = r.errores.concat(errores);
  await p.close();
  return r;
}

(async () => {
  const paginas = process.argv.slice(2).length ? process.argv.slice(2) : POR_DEFECTO;
  const servidor = await servir(path.resolve('docs'));
  const base = 'http://127.0.0.1:' + servidor.address().port + '/';
  // `--mute-audio` no afloja nada: `play()` sigue resolviendo igual y
  // `aria-pressed` sigue siendo la señal exigida. Lo que quita es la
  // dependencia de que el contenedor tenga salida de audio, que no la tiene:
  // sin esto, una página al azar de las 25 se quedaba con la promesa de
  // `play()` sin resolver —con su MP3 descargado, 200 y bytes— y el rojo
  // señalaba cada vez a una página distinta.
  const b = await chromium.launch({
    args: ['--no-sandbox', '--mute-audio', '--autoplay-policy=no-user-gesture-required'] });
  let malas = 0;
  for (const rel of paginas) {
    const r = await unaPagina(b, rel, base);
    const roto = r.errores.length || (r.test && (r.aciertos !== r.test || !r.dice_todo_bien));
    if (roto) malas++;
    console.log(JSON.stringify(r));
  }
  await b.close();
  servidor.close();
  process.exit(malas ? 1 : 0);
})();
