(function () {
  'use strict';
  var textos = window.CURSO_TEXTOS || {};
  var preferencia = window.matchMedia('(prefers-reduced-motion: reduce)');
  var cuadroAnimacion = null;
  var avisoRespuesta = null;
  var temporizadorAviso = null;
  var observadorEntrada = null;

  function leer(clave, valorInicial, almacen) {
    try {
      var valor = window[almacen || 'localStorage'].getItem(clave);
      return valor ? JSON.parse(valor) : valorInicial;
    } catch (error) { return valorInicial; }
  }

  function guardar(clave, valor, almacen) {
    try { window[almacen || 'localStorage'].setItem(clave, JSON.stringify(valor)); }
    catch (error) { /* La lectura del curso también funciona con almacenamiento bloqueado. */ }
  }

  function ondas(boton) {
    if (boton.getAttribute('aria-pressed') !== 'true' || boton.querySelector('.audio-ondas')) return;
    var barras = document.createElement('span');
    barras.className = 'audio-ondas';
    barras.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 3; i++) barras.appendChild(document.createElement('i'));
    boton.appendChild(barras);
  }

  function confirmar(elemento) {
    if (!elemento.matches('.test-ops button.bien, .hueco.bien')) return;
    if (elemento.querySelector('.respuesta-check')) return;
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'respuesta-check');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('aria-hidden', 'true');
    var trazo = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    trazo.setAttribute('d', 'M5 12l4 4L19 6');
    svg.appendChild(trazo);
    elemento.appendChild(svg);
  }

  // Las preguntas y las tarjetas insertan botones después de cargar la página.
  var observadorControles = new MutationObserver(function (cambios) {
    cambios.forEach(function (cambio) {
      if (cambio.type === 'attributes') {
        if (cambio.attributeName === 'aria-pressed' && cambio.target.matches('.suena')) ondas(cambio.target);
        if (cambio.attributeName === 'class') confirmar(cambio.target);
      } else {
        cambio.addedNodes.forEach(function (nodo) {
          if (nodo.nodeType !== 1) return;
          confirmar(nodo);
          nodo.querySelectorAll('.test-ops button.bien, .hueco.bien').forEach(confirmar);
          if (nodo.matches('.suena[aria-pressed="true"]')) ondas(nodo);
        });
      }
    });
  });
  observadorControles.observe(document.body, {
    subtree: true, childList: true, attributes: true, attributeFilter: ['class', 'aria-pressed']
  });

  document.addEventListener('curso:respuesta', function (evento) {
    var respuesta = evento.detail;
    if (!avisoRespuesta) {
      avisoRespuesta = document.createElement('div');
      avisoRespuesta.className = 'respuesta-aviso';
      avisoRespuesta.setAttribute('role', 'status');
      document.body.appendChild(avisoRespuesta);
    }
    clearTimeout(temporizadorAviso);
    avisoRespuesta.textContent = (respuesta.bien ? '✓ ' + textos.respuesta_bien : '→ ' + textos.respuesta_correcta)
      + ' · ' + respuesta.correcta;
    avisoRespuesta.classList.toggle('acierto', respuesta.bien);
    avisoRespuesta.hidden = false;
    temporizadorAviso = setTimeout(function () { avisoRespuesta.hidden = true; }, 1800);
  });

  var cajaMarcar = document.getElementById('marcar-caja');
  var totalCurso = window.CURSO_PUBLICADAS || 365;
  var avance = null;
  var cifra = null;
  var barra = null;
  var cantidadVisible = 0;

  function textoCantidad(cantidad) {
    return (textos.cuantas || '{n} / {total}').replace('{n}', cantidad).replace('{total}', totalCurso)
      + (textos.tuyo ? ' · ' + textos.tuyo : '');
  }

  function pintarCantidad(cantidad) {
    cantidadVisible = cantidad;
    if (cifra) cifra.textContent = textoCantidad(cantidad);
  }

  function actualizarAvance(cantidad, animar) {
    if (!avance) return;
    if (cuadroAnimacion !== null) cancelAnimationFrame(cuadroAnimacion);
    cuadroAnimacion = null;
    avance.setAttribute('aria-valuenow', cantidad);
    barra.style.width = (cantidad * 100 / totalCurso) + '%';
    if (!animar || preferencia.matches) { pintarCantidad(cantidad); return; }
    var desde = cantidadVisible;
    var inicio = performance.now();
    function paso(ahora) {
      var progreso = Math.min((ahora - inicio) / 420, 1);
      pintarCantidad(Math.round(desde + (cantidad - desde) * (1 - Math.pow(1 - progreso, 3))));
      cuadroAnimacion = progreso < 1 ? requestAnimationFrame(paso) : null;
    }
    cuadroAnimacion = requestAnimationFrame(paso);
  }

  if (cajaMarcar) {
    var bloque = document.createElement('div');
    bloque.className = 'avance-leccion';
    cifra = document.createElement('p');
    bloque.appendChild(cifra);
    avance = document.createElement('div');
    avance.className = 'barra';
    avance.setAttribute('role', 'progressbar');
    avance.setAttribute('aria-label', textos.titulo || '');
    avance.setAttribute('aria-valuemin', '0');
    avance.setAttribute('aria-valuemax', totalCurso);
    barra = document.createElement('i');
    avance.appendChild(barra);
    bloque.appendChild(avance);
    cajaMarcar.insertBefore(bloque, cajaMarcar.querySelector('.pide-nombre'));
    var guardadas = leer('curso.hechas', []);
    actualizarAvance(Array.isArray(guardadas) ? guardadas.length : 0, false);
  }

  var unidad = null;
  var datosUnidad = document.getElementById('unidad-actual');
  if (datosUnidad) {
    try { unidad = JSON.parse(datosUnidad.textContent); } catch (error) { unidad = null; }
  }
  var celebradas = leer('curso.unidades-celebradas', []);
  if (!Array.isArray(celebradas)) celebradas = [];
  var logro = null;

  function confeti() {
    if (preferencia.matches || document.querySelector('.unidad-confeti')) return;
    var capa = document.createElement('div');
    capa.className = 'unidad-confeti';
    capa.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 30; i++) {
      var pieza = document.createElement('i');
      pieza.style.setProperty('--desvio', ((Math.random() - 0.5) * Math.min(innerWidth, 1000)) + 'px');
      pieza.style.setProperty('--giro', ((Math.random() - 0.5) * 720) + 'deg');
      pieza.style.setProperty('--retraso', (Math.random() * 0.25) + 's');
      capa.appendChild(pieza);
    }
    document.body.appendChild(capa);
    setTimeout(function () { capa.remove(); }, 2200);
  }

  document.addEventListener('curso:leccion-marcada', function (evento) {
    var detalle = evento.detail;
    actualizarAvance(detalle.hechas.length, detalle.marcada);
    guardar('curso.efecto-marca', detalle.marcada ? detalle.numero : 0, 'sessionStorage');
    var completa = unidad && unidad.dias.every(function (dia) { return detalle.hechas.indexOf(dia) >= 0; });
    if (!completa) {
      if (logro) logro.hidden = true;
      return;
    }
    if (!logro) {
      logro = document.createElement('div');
      logro.className = 'unidad-logro';
      logro.setAttribute('role', 'status');
      var titulo = document.createElement('strong');
      titulo.textContent = '✓ ' + textos.unidad_logro;
      var nombre = document.createElement('p');
      nombre.textContent = unidad.nombre;
      logro.appendChild(titulo);
      logro.appendChild(nombre);
      cajaMarcar.insertBefore(logro, cajaMarcar.querySelector('.saludo'));
    }
    logro.hidden = false;
    if (celebradas.indexOf(unidad.numero) < 0) {
      celebradas.push(unidad.numero);
      guardar('curso.unidades-celebradas', celebradas);
      confeti();
    }
  });

  var ultimaMarca = leer('curso.efecto-marca', 0, 'sessionStorage');
  var casillas = document.querySelectorAll('.cal-rejilla .cal-dia');
  if (ultimaMarca > 0 && ultimaMarca <= casillas.length) {
    var casilla = casillas[ultimaMarca - 1];
    if (casilla.classList.contains('hecho')) casilla.classList.add('marca-nueva');
    guardar('curso.efecto-marca', 0, 'sessionStorage');
  }

  function revelarTodo() {
    if (observadorEntrada) observadorEntrada.disconnect();
    document.querySelectorAll('.entrada-pendiente').forEach(function (seccion) {
      seccion.classList.add('entrada-visible');
    });
  }

  if (!preferencia.matches && window.IntersectionObserver) {
    var secciones = document.querySelectorAll('.portada-seccion, .portada .muestra');
    try {
      observadorEntrada = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          entrada.target.classList.add('entrada-visible');
          observadorEntrada.unobserve(entrada.target);
        });
      }, { threshold: 0.06 });
      secciones.forEach(function (seccion) {
        observadorEntrada.observe(seccion);
        seccion.classList.add('entrada-pendiente');
        seccion.querySelectorAll('.tarjeta, .vitrina li').forEach(function (tarjeta, indice) {
          tarjeta.style.setProperty('--entrada-retraso', (Math.min(indice, 5) * 45) + 'ms');
        });
      });
    } catch (error) { revelarTodo(); }
  }

  function cambiarPreferencia() {
    if (!preferencia.matches) return;
    revelarTodo();
    var capa = document.querySelector('.unidad-confeti');
    if (capa) capa.remove();
    document.querySelectorAll('.ficha-cara').forEach(function (cara) {
      if (cara.getAnimations) cara.getAnimations().forEach(function (animacion) { animacion.cancel(); });
    });
    if (avance) actualizarAvance(Number(avance.getAttribute('aria-valuenow')), false);
  }
  if (preferencia.addEventListener) preferencia.addEventListener('change', cambiarPreferencia);
})();
