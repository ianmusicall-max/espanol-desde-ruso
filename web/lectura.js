(function () {
  'use strict';
  var textos = window.CURSO_LECTURA || {};
  var cabecera = document.querySelector('header.sitio');
  var botonMenu = document.getElementById('menu-movil');
  var menu = document.querySelector('header.sitio nav.paginas');
  var movil = window.matchMedia('(max-width: 39.99rem)');

  function abrirMenu(abierto) {
    cabecera.classList.toggle('menu-abierto', abierto);
    botonMenu.setAttribute('aria-expanded', String(abierto));
    botonMenu.setAttribute('aria-label', abierto ? textos.menu_cerrar : textos.menu);
  }

  if (cabecera && botonMenu && menu) {
    menu.id = 'menu-principal';
    botonMenu.setAttribute('aria-controls', menu.id);
    cabecera.classList.add('menu-interactivo');
    function ajustarMenu() {
      botonMenu.hidden = !movil.matches;
      abrirMenu(false);
    }
    botonMenu.addEventListener('click', function () {
      abrirMenu(botonMenu.getAttribute('aria-expanded') !== 'true');
    });
    menu.addEventListener('click', function (evento) {
      if (evento.target.closest('a')) abrirMenu(false);
    });
    document.addEventListener('keydown', function (evento) {
      if (evento.key === 'Escape' && botonMenu.getAttribute('aria-expanded') === 'true') {
        abrirMenu(false);
        botonMenu.focus();
      }
    });
    document.addEventListener('click', function (evento) {
      if (!cabecera.contains(evento.target)) abrirMenu(false);
    });
    if (movil.addEventListener) movil.addEventListener('change', ajustarMenu);
    ajustarMenu();
  }

  document.querySelectorAll('.tabla-dialogo').forEach(function (bloque, indice) {
    var tabla = bloque.querySelector('table');
    if (!tabla) return;
    tabla.id = tabla.id || 'dialogo-tabla-' + (indice + 1);
    var boton = document.createElement('button');
    boton.type = 'button';
    boton.className = 'dialogo-traduccion boton secundario';
    boton.textContent = textos.traduccion_ocultar;
    boton.setAttribute('aria-controls', tabla.id);
    boton.setAttribute('aria-expanded', 'true');
    boton.addEventListener('click', function () {
      var ocultar = !bloque.classList.contains('traduccion-oculta');
      bloque.classList.toggle('traduccion-oculta', ocultar);
      boton.textContent = ocultar ? textos.traduccion_mostrar : textos.traduccion_ocultar;
      boton.setAttribute('aria-expanded', String(!ocultar));
    });
    bloque.insertBefore(boton, tabla);

    var hablantes = Object.create(null);
    var siguienteHablante = 0;
    var turnoAnonimo = 0;
    tabla.querySelectorAll('tbody tr').forEach(function (fila) {
      var celdas = fila.querySelectorAll('td');
      if (celdas.length !== 2 || !celdas[1].textContent.trim()) return;
      var texto = celdas[0].textContent.replace(/▶/g, '').trim();
      var destacado = celdas[0].querySelector('strong');
      var nombre = destacado ? destacado.textContent.trim() : '';
      if (nombre && /^[A-ZÁÉÍÓÚÜÑ][^:]{0,24}:$/.test(nombre) && texto.indexOf(nombre) === 0) {
        if (!(nombre in hablantes)) hablantes[nombre] = siguienteHablante++;
        fila.setAttribute('data-voz', String(hablantes[nombre] % 2));
      } else if (/^[—–]\s/.test(texto)) {
        fila.setAttribute('data-voz', String(turnoAnonimo++ % 2));
      } else { return; }
      celdas[0].setAttribute('lang', 'es');
      celdas[1].setAttribute('lang', 'ru');
    });
  });
})();
