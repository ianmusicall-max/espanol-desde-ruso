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

  // --- en el mapa de unidades: TU progreso, no el del curso ---
  //
  // La barra de cada tarjeta medía cuántas lecciones de esa unidad están
  // ESCRITAS, y desde que el curso está entero eso son las catorce en las
  // veinticuatro: una barra llena que no dice nada. El navegador sí sabe
  // cuáles has hecho tú, así que la misma barra pasa a medir eso.
  //
  // Solo si ya hay progreso, igual que `#mio` y por la misma razón: en la
  // primera visita, veinticuatro barras en cero desaniman. Sin nada hecho la
  // página se queda exactamente como la sirve el servidor.
  var tarjetas=document.querySelectorAll('.u-tarjeta[data-desde]');
  if(tarjetas.length&&hechasAhora.length){
    var dentro={};hechasAhora.forEach(function(x){dentro[x]=1});
    for(var k=0;k<tarjetas.length;k++){
      var tj=tarjetas[k],
          desde=parseInt(tj.getAttribute('data-desde'),10),
          hasta=parseInt(tj.getAttribute('data-hasta'),10);
      if(!(desde>0)||!(hasta>=desde))continue;
      var total=hasta-desde+1, mias=0;
      for(var d=desde;d<=hasta;d++){if(dentro[d])mias++}
      var cuenta=tj.querySelector('.hechas');
      if(cuenta){
        var palabra=cuenta.getAttribute('data-palabra')||'';
        cuenta.textContent=mias+'/'+total+(palabra?' '+palabra:'');
      }
      var barra=tj.querySelector('.mini');
      if(barra){
        barra.hidden=false;
        var raya=barra.querySelector('i');
        if(raya)raya.style.width=(mias?Math.max(mias*100/total,3):0)+'%';
      }
      if(mias===total)tj.classList.add('completa');
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
(function(){
  // La guia de la leccion: los seis pasos de los 30 minutos, con el que toca
  // marcado y un boton que lleva al siguiente.
  //
  // Por que. Una leccion es una pagina larga con seis apartados y sus franjas
  // de minutos escritas en los titulos («## 3. Новое (6–16 мин)»), y hasta hoy
  // el alumno tenia que ir encontrandolos solo entre el texto. El profesor lo
  // pidio asi: «que sea un aprendizaje intuitivo, colocar algo mas guiado».
  // Esto no anade materia: hace visible la que ya estaba.
  //
  // Los pasos salen de los PROPIOS titulos de la leccion y no de una lista en
  // el codigo. Una lista se queda vieja el dia que un tipo de dia use otros
  // apartados —los de examen, simulacro y proyecto ya lo hacen— y el sintoma
  // seria una guia que señala donde no es.
  var art=document.querySelector('article[data-leccion]');
  var caja=document.getElementById('guia');
  var T=window.CURSO_TEXTOS||{};
  if(!art||!caja)return;

  var FRANJA=/^\s*(\d+)\.\s*(.+?)\s*\((\d+)\s*[–—-]\s*(\d+)\s*мин\)\s*$/;
  var pasos=[];
  Array.prototype.forEach.call(art.querySelectorAll('h2'),function(h){
    var m=(h.textContent||'').match(FRANJA);
    if(m)pasos.push({el:h,nombre:m[2],a:+m[3],b:+m[4]});
  });
  // Menos de tres no es una leccion con sus franjas (la clave, por ejemplo, no
  // es un paso: no se hace, se consulta). Sin guia, la pagina se queda igual.
  if(pasos.length<3)return;

  // La cabecera del sitio es pegajosa a partir de 40rem, asi que la guia tiene
  // que pegarse DEBAJO de ella. Se mide, no se escribe: cambiar el menu movia
  // el numero y nadie se enteraria hasta ver la guia tapada.
  function altoCabecera(){
    var h=document.querySelector('header.sitio');
    if(!h)return 0;
    return getComputedStyle(h).position==='sticky'?Math.round(h.getBoundingClientRect().height):0;
  }
  function ajustarTope(){
    document.documentElement.style.setProperty('--alto-cabecera',altoCabecera()+'px');
  }
  ajustarTope();
  window.addEventListener('resize',ajustarTope);

  var barra=document.createElement('div');barra.className='guia-barra';
  var puntos=pasos.map(function(p,i){
    var b=document.createElement('button');
    b.type='button';b.className='guia-punto';b.textContent=String(i+1);
    b.setAttribute('data-i',String(i));
    b.title=p.nombre;b.setAttribute('aria-label',p.nombre);
    b.addEventListener('click',function(){irA(i)});
    barra.appendChild(b);return b;
  });
  var ahora=document.createElement('div');ahora.className='guia-ahora';
  var cual=document.createElement('b'), franja=document.createElement('span');
  ahora.appendChild(cual);ahora.appendChild(franja);
  var ir=document.createElement('button');
  ir.type='button';ir.className='guia-ir';
  ir.addEventListener('click',function(){
    if(actual+1<pasos.length){irA(actual+1)}
    else{
      // En el ultimo paso la guia deja de guiar la leccion y lleva al boton de
      // marcarla: es lo unico que queda por hacer, y es lo que encadena con el
      // dia siguiente.
      var m=document.getElementById('marcar-caja');
      if(m)m.scrollIntoView({behavior:'smooth',block:'center'});
    }
  });
  caja.appendChild(barra);caja.appendChild(ahora);caja.appendChild(ir);
  caja.hidden=false;

  var actual=-1, hasta=0;
  function irA(i){
    var tope=caja.getBoundingClientRect().height+altoCabecera()+10;
    var y=pasos[i].el.getBoundingClientRect().top+window.pageYOffset-tope;
    // Se pinta el paso YA y se bloquea al vigilante un momento. Sin esto, el
    // desplazamiento suave todavia no ha terminado cuando `mirar()` vuelve a
    // calcular, el titulo aun cae un pixel por debajo del corte y el paso se
    // queda en el anterior: el siguiente clic repetia el mismo apartado. Se
    // vio recorriendo la leccion en el navegador, no leyendo el codigo.
    pintar(i); hasta=Date.now()+700;
    window.scrollTo({top:Math.max(y,0),behavior:'smooth'});
  }
  function pintar(i){
    if(i===actual)return;
    actual=i;
    for(var k=0;k<puntos.length;k++){
      puntos[k].classList.toggle('aqui',k===i);
      puntos[k].classList.toggle('hecho',k<i);
    }
    var p=pasos[i];
    cual.textContent=p.nombre;
    franja.textContent=p.a+'–'+p.b+' '+(T.guia_min||'мин');
    ir.textContent=(i+1<pasos.length?(T.guia_siguiente||'Дальше'):(T.guia_final||''))+' ↓';
    caja.setAttribute('aria-label',(T.guia_paso||'{n}/{total}')
      .replace('{n}',i+1).replace('{total}',pasos.length));
  }
  function mirar(){
    if(Date.now()<hasta)return;
    var corte=altoCabecera()+caja.getBoundingClientRect().height+16;
    var i=0;
    for(var k=0;k<pasos.length;k++){
      if(pasos[k].el.getBoundingClientRect().top<=corte)i=k;
    }
    pintar(i);
  }
  var esperando=false;
  window.addEventListener('scroll',function(){
    if(esperando)return;esperando=true;
    requestAnimationFrame(function(){esperando=false;mirar()});
  },{passive:true});
  mirar();
})();
(function(){
  // Las tarjetas del mapa aparecen subiendo al llegar a ellas.
  //
  // La clase que las esconde la pone ESTE guion y no el servidor, y es la
  // linea que no se puede cruzar: si el navegador no trae
  // IntersectionObserver, o el sistema pide menos movimiento, no se anade
  // nada y las tarjetas nacen visibles. Al reves —un `opacity:0` servido en
  // el HTML— deja la pagina en blanco para quien no tenga JavaScript, que es
  // justo lo que este sitio no hace en ninguna otra parte.
  //
  // Se desconecta cada tarjeta en cuanto entra: si no, el observador sigue
  // trabajando en cada scroll durante toda la visita para nada.
  var mapa=document.querySelector('.mapa');
  if(!mapa||!window.IntersectionObserver)return;
  try{
    if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  }catch(e){}
  var tarjetas=mapa.querySelectorAll('.u-tarjeta');
  if(!tarjetas.length)return;
  mapa.classList.add('anima');
  var ojo=new IntersectionObserver(function(entradas){
    entradas.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('dentro');ojo.unobserve(e.target)}
    });
  },{rootMargin:'0px 0px -40px 0px'});
  for(var i=0;i<tarjetas.length;i++)ojo.observe(tarjetas[i]);
  // Red: si algo impidiera que el observador disparara, a los dos segundos
  // se encienden igual. Una tarjeta invisible para siempre seria peor que
  // no tener efecto.
  setTimeout(function(){
    for(var j=0;j<tarjetas.length;j++)tarjetas[j].classList.add('dentro');
  },2000);
})();