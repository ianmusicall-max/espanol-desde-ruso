(function(){
  var CLAVE_HECHAS='curso.hechas', CLAVE_ULTIMA='curso.ultima';
  var T=window.CURSO_TEXTOS||{}, RAIZ=window.CURSO_RAIZ||'.';

  function leer(clave,porDefecto){
    try{var v=localStorage.getItem(clave);return v?JSON.parse(v):porDefecto}catch(e){return porDefecto}
  }
  function guardar(clave,valor){
    try{localStorage.setItem(clave,JSON.stringify(valor))}catch(e){}
  }
  function hechas(){var v=leer(CLAVE_HECHAS,[]);return Array.isArray(v)?v:[]}
  function url(n){
    var d=window.CURSO_DIAS&&window.CURSO_DIAS[n];
    return d?RAIZ+'/'+d:null;
  }

  // --- en una lección: recordar que se pasó por aquí y poder marcarla ---
  // article[data-leccion] y no [data-leccion] a secas: en el índice el primero
  // que aparece es un <li data-leccion>, así que abrir el índice movía «la
  // última leída» a la lección 1 y «continuar» mandaba al principio.
  var cuerpoLeccion=document.querySelector('article[data-leccion]');
  if(cuerpoLeccion){
    var n=parseInt(cuerpoLeccion.getAttribute('data-leccion'),10);
    if(n){guardar(CLAVE_ULTIMA,n);}
    var caja=document.getElementById('marcar-caja');
    if(caja&&n){
      var boton=document.createElement('button');
      boton.type='button';boton.className='boton marcar';
      var siguiente=document.getElementById('enlace-siguiente');
      function pintar(){
        var yaEsta=hechas().indexOf(n)>=0;
        boton.textContent=(yaEsta?'✓ ':'')+(yaEsta?T.hecho:T.marcar);
        boton.classList.toggle('secundario',yaEsta);
      }
      boton.addEventListener('click',function(){
        var lista=hechas(), i=lista.indexOf(n);
        if(i>=0){lista.splice(i,1)}else{lista.push(n)}
        guardar(CLAVE_HECHAS,lista);pintar();
        if(i<0&&siguiente){siguiente.classList.add('destacado')}
      });
      pintar();caja.appendChild(boton);
    }
  }

  // --- en la portada: continuar donde se dejó ---
  var seguir=document.getElementById('continuar');
  if(seguir){
    var ultima=leer(CLAVE_ULTIMA,null), destino=ultima?url(ultima):null;
    if(destino){
      seguir.href=destino;
      seguir.textContent=T.continuar+' '+ultima;
      seguir.hidden=false;
      var empezar=document.getElementById('empezar');
      if(empezar){empezar.textContent=T.empezar;empezar.classList.add('secundario')}
    }
  }

  // --- el contador personal, donde lo haya ---
  var hechasAhora=hechas(), publicadas=window.CURSO_PUBLICADAS||0;
  var contador=document.getElementById('mio');
  if(contador&&hechasAhora.length){
    contador.hidden=false;
    var cifra=contador.querySelector('.n'), texto=contador.querySelector('.texto');
    if(cifra)cifra.textContent=hechasAhora.length;
    if(texto)texto.textContent='/ '+publicadas+' '+T.tuyo;
    var barra=contador.querySelector('.barra i');
    if(barra&&publicadas)barra.style.width=Math.max(hechasAhora.length*100/publicadas,1)+'%';
  }

  // --- en el índice: una marca en cada lección hecha ---
  var filas=document.querySelectorAll('li[data-leccion]');
  if(filas.length){
    var mapa={};hechasAhora.forEach(function(x){mapa[x]=1});
    for(var i=0;i<filas.length;i++){
      if(mapa[parseInt(filas[i].getAttribute('data-leccion'),10)]){
        filas[i].classList.add('hecha');
      }
    }
  }

  // --- el código de respaldo ---
  //
  // El progreso vive en localStorage, que se va con «limpiar datos del
  // navegador» y no viaja a otro teléfono. Cuentas de verdad costarían un
  // servicio, datos personales y soporte; un código que el alumno guarda
  // DONDE QUIERA no cuesta nada y no deja nada nuestro en ningún sitio.
  //
  // Un bit por lección: las 365 caben en 46 bytes, o sea 64 caracteres en
  // base64, y el código NO crece según se avanza. Eso es lo que lo hace
  // pegable en un mensaje de Telegram, que es donde lo va a guardar la gente.
  var BYTES = 46;                       // 365 lecciones / 8, redondeado
  var MARCA = 'ESR1';                   // para reconocer un código nuestro

  function aCodigo(lista, ultima){
    var b = new Uint8Array(2 + BYTES);
    b[0] = (ultima >> 8) & 255; b[1] = ultima & 255;
    for(var i=0;i<lista.length;i++){
      var n = lista[i] - 1;
      if(n >= 0 && n < BYTES*8) b[2 + (n>>3)] |= 1 << (n & 7);
    }
    var cad=''; for(var j=0;j<b.length;j++) cad += String.fromCharCode(b[j]);
    return MARCA + btoa(cad).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  }

  function deCodigo(texto){
    // Devuelve null ante CUALQUIER duda. Restaurar nunca puede destruir lo
    // que el alumno ya tiene por un código mal pegado o cortado a medias.
    try{
      texto = String(texto||'').replace(/\s+/g,'');
      if(texto.slice(0,4) !== MARCA) return null;
      var cad = atob(texto.slice(4).replace(/-/g,'+').replace(/_/g,'/'));
      if(cad.length !== 2 + BYTES) return null;
      var ultima = (cad.charCodeAt(0) << 8) | cad.charCodeAt(1);
      var lista = [];
      for(var i=0;i<BYTES;i++){
        var v = cad.charCodeAt(2+i);
        for(var bit=0;bit<8;bit++) if(v & (1<<bit)) lista.push(i*8 + bit + 1);
      }
      if(ultima < 0 || ultima > BYTES*8) return null;
      return {hechas: lista, ultima: ultima};
    }catch(e){ return null; }
  }

  var copiar = document.getElementById('copiar-progreso');
  if(copiar){
    copiar.hidden = !hechasAhora.length;
    copiar.addEventListener('click', function(){
      var codigo = aCodigo(hechasAhora, leer(CLAVE_ULTIMA,0)||0);
      var aviso = document.getElementById('codigo-aviso');
      function mostrarAviso(){
        if(aviso){ aviso.textContent = T.copiado; aviso.hidden = false; }
      }
      // El portapapeles puede no estar (http, permisos, navegador viejo). Si
      // falla, el código se enseña en un campo para copiarlo a mano: quedarse
      // sin él sería lo único imperdonable aquí.
      function aMano(c){
        var campo = document.getElementById('codigo-mio');
        if(campo){ campo.hidden=false; campo.value=c; campo.select(); }
        mostrarAviso();
      }
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(codigo).then(mostrarAviso, function(){ aMano(codigo); });
      } else { aMano(codigo); }
    });
  }

  var restaurar = document.getElementById('restaurar-progreso');
  var cajaRest = document.getElementById('restaurar-caja');
  if(restaurar && cajaRest){
    restaurar.addEventListener('click', function(){ cajaRest.hidden = !cajaRest.hidden; });
    var aplicar = document.getElementById('restaurar-aplicar');
    if(aplicar) aplicar.addEventListener('click', function(){
      var campo = document.getElementById('restaurar-codigo');
      var aviso = document.getElementById('restaurar-aviso');
      var datos = deCodigo(campo && campo.value);
      function di(t){ if(aviso){ aviso.textContent=t; aviso.hidden=false; } }
      if(!datos){ di(T.malo); return; }
      // Un código viejo trae menos lecciones: se pregunta antes de pisar.
      if(datos.hechas.length < hechasAhora.length){
        // Los huecos que rellena el navegador van con %…% y no con {…}: así
        // se distinguen de un vistazo de los que rellena Python, y la prueba
        // que caza un «{n}» sin sustituir en la página sigue cazándolo.
        var q = (T.menos||'').replace('%a%', datos.hechas.length).replace('%b%', hechasAhora.length);
        if(!window.confirm(q)) return;
      }
      guardar(CLAVE_HECHAS, datos.hechas);
      if(datos.ultima) guardar(CLAVE_ULTIMA, datos.ultima);
      di((T.hecho_restaurar||'').replace('%n%', datos.hechas.length));
      location.reload();
    });
  }

  // --- copiar el enlace de la lección ---
  // Sin widget y sin librería: el navegador ya sabe copiar. Si el portapapeles
  // no está disponible, el botón no miente: se queda como estaba.
  var copiarEnlace = document.getElementById('copiar-enlace');
  if(copiarEnlace && navigator.clipboard && navigator.clipboard.writeText){
    copiarEnlace.addEventListener('click', function(){
      navigator.clipboard.writeText(copiarEnlace.dataset.url).then(function(){
        copiarEnlace.textContent = copiarEnlace.dataset.ok;
      });
    });
  }

  // --- borrar el progreso ---
  var borrar=document.getElementById('borrar-progreso');
  if(borrar){
    borrar.hidden=!hechasAhora.length&&!leer(CLAVE_ULTIMA,null);
    borrar.addEventListener('click',function(){
      if(!window.confirm(T.confirmar))return;
      try{localStorage.removeItem(CLAVE_HECHAS);localStorage.removeItem(CLAVE_ULTIMA)}catch(e){}
      location.reload();
    });
  }
})();