(function(){
  var CLAVE_HECHAS='curso.hechas', CLAVE_ULTIMA='curso.ultima';
  var CLAVE_FECHAS='curso.fechas', CLAVE_NOMBRE='curso.nombre';
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

  function hoy(){
    // La fecha LOCAL y no toISOString(), que da UTC: quien estudia a las
    // once de la noche en Moscú vería la racha contada como del día
    // siguiente, y quien estudia de madrugada en México la perdería.
    var f=new Date(), m=f.getMonth()+1, d=f.getDate();
    return f.getFullYear()+'-'+(m<10?'0':'')+m+'-'+(d<10?'0':'')+d;
  }
  function fechas(){var v=leer(CLAVE_FECHAS,[]);return Array.isArray(v)?v:[]}
  function anotarHoy(){
    var f=fechas(), h=hoy();
    if(f.indexOf(h)<0){f.push(h);guardar(CLAVE_FECHAS,f)}
  }
  function dia(cadena){var p=String(cadena).split('-');return Date.UTC(+p[0],+p[1]-1,+p[2])}
  function rachas(){
    // Devuelve {actual, mejor}. La actual cuenta hacia atrás desde HOY, y si
    // hoy todavía no hay nada, desde ayer: una racha no se rompe por que
    // sean las diez de la mañana y aún no hayas estudiado.
    var f=fechas().slice().sort(), DIA=86400000;
    if(!f.length)return {actual:0,mejor:0,hoy:false};
    var h=dia(hoy()), ultima=dia(f[f.length-1]);
    var actual=0, mejor=0, seguidas=0, previa=null;
    for(var i=0;i<f.length;i++){
      var d=dia(f[i]);
      seguidas = (previa!==null && d-previa===DIA) ? seguidas+1 : 1;
      if(seguidas>mejor)mejor=seguidas;
      previa=d;
    }
    if(ultima===h||ultima===h-DIA){
      actual=1;
      for(var j=f.length-2;j>=0;j--){
        if(dia(f[j+1])-dia(f[j])===DIA)actual++;else break;
      }
    }
    return {actual:actual,mejor:mejor,hoy:ultima===h};
  }
  function plural(n,formas){
    // Tres formas porque el ruso las pide (1 день, 2-4 дня, 5+ дней). En
    // español y en inglés las dos últimas son la misma y no estorba.
    if(!formas||!formas.length)return '';
    var d=n%10, c=n%100;
    if(d===1&&c!==11)return formas[0];
    if(d>=2&&d<=4&&!(c>=12&&c<=14))return formas[1]||formas[0];
    return formas[2]||formas[1]||formas[0];
  }
  function permutacion(bloque,largo){
    // Fisher-Yates con una semilla que sale del BLOQUE, así que da lo mismo
    // en cada visita: el mensaje de una lección no cambia al recargarla.
    // El multiplicador es el de MINSTD y no el del LCG de libro: con éste
    // todos los productos se quedan por debajo de 2^53, que es hasta donde
    // JavaScript cuenta exacto. Con 1103515245 el producto se sale y la
    // mezcla deja de ser la que se midió.
    var s=((bloque+1)*48271)%2147483647, p=[];
    for(var i=0;i<largo;i++)p.push(i);
    for(var k=largo-1;k>0;k--){
      s=(s*48271)%2147483647;
      var j=(s>>8)%(k+1), t=p[k];p[k]=p[j];p[j]=t;
    }
    return p;
  }
  function variante(n,lista){
    // Dentro de cada bloque de `largo` lecciones salen todas las frases una
    // vez, en un orden que depende del bloque. Hace dos cosas a la vez que
    // ninguna solución simple hace: no repite nunca la frase de la lección
    // anterior Y no deja un ciclo visible —con n%largo la frase de hoy es la
    // de hace nueve lecciones, y en una racha de dos semanas eso se nota, que
    // es justo de lo que el profesor se quejó—. Es el mismo reparto por
    // bloques que la letra correcta de los tests, y por el mismo motivo.
    if(!lista)return '';
    if(!lista.length||typeof lista==='string')return String(lista);
    var largo=lista.length, bloque=Math.floor((n-1)/largo), p=permutacion(bloque,largo);
    if(bloque>0&&p[0]===permutacion(bloque-1,largo)[largo-1]){var t=p[0];p[0]=p[1];p[1]=t}
    return lista[p[(n-1)%largo]];
  }
  function conPlantilla(txt,datos){
    return String(txt||'').replace(/\{(\w+)\}/g,function(_,k){
      return datos[k]!==undefined?datos[k]:'';
    });
  }
  function nombre(){try{return localStorage.getItem(CLAVE_NOMBRE)||''}catch(e){return ''}}


  // --- el certificado, dibujado en el navegador ---
  function partirTexto(g,texto,ancho){
    var palabras=String(texto||'').split(/\s+/), lineas=[], linea='';
    for(var i=0;i<palabras.length;i++){
      var prueba=linea?linea+' '+palabras[i]:palabras[i];
      if(g.measureText(prueba).width>ancho&&linea){lineas.push(linea);linea=palabras[i]}
      else{linea=prueba}
    }
    if(linea)lineas.push(linea);
    return lineas;
  }
  function descargarDiploma(nv,quien){
    var A=1200, B=850, lienzo=document.createElement('canvas');
    lienzo.width=A;lienzo.height=B;
    var g=lienzo.getContext('2d');
    if(!g)return;
    // La paleta va escrita aquí y NO leída de las variables del CSS, a
    // propósito: un certificado se imprime, así que es siempre la versión
    // clara. Leyéndola, quien tenga puesto el tema oscuro se descargaría un
    // papel negro. Es el mismo precio que ya paga `tarjeta_social.py`.
    var PAPEL='#ffffff', TINTA='#101113', ACENTO='#b03f26', TENUE='#6b7076';
    var SANS='Onest,ui-sans-serif,system-ui,sans-serif';
    var SERIF='Literata,ui-serif,Georgia,serif';
    g.fillStyle=PAPEL;g.fillRect(0,0,A,B);
    g.strokeStyle=ACENTO;g.lineWidth=6;g.strokeRect(26,26,A-52,B-52);
    g.strokeStyle='#dcdde0';g.lineWidth=1;g.strokeRect(44,44,A-88,B-88);
    // La marca del sitio: la misma eñe del icono, para que el papel y la
    // pestaña hablen el mismo idioma.
    g.fillStyle=ACENTO;
    var lado=84, mx=(A-lado)/2;
    if(g.roundRect){g.beginPath();g.roundRect(mx,88,lado,lado,20);g.fill()}
    else{g.fillRect(mx,88,lado,lado)}
    g.fillStyle=PAPEL;g.textAlign='center';g.textBaseline='alphabetic';
    g.font='700 56px '+SANS;g.fillText('ñ',A/2,88+lado-20);
    g.fillStyle=TINTA;
    g.font='700 46px '+SANS;g.fillText(T.diploma_titulo||'',A/2,250);
    g.fillStyle=TENUE;
    g.font='400 22px '+SANS;g.fillText(T.diploma_sub||'',A/2,288);
    g.strokeStyle='#dcdde0';g.lineWidth=1;
    g.beginPath();g.moveTo(A/2-180,318);g.lineTo(A/2+180,318);g.stroke();
    g.fillStyle=TENUE;
    g.font='400 20px '+SANS;g.fillText(T.diploma_quien||'',A/2,368);
    g.fillStyle=ACENTO;
    g.font='400 56px '+SERIF;g.fillText(quien,A/2,432);
    g.fillStyle=TINTA;
    g.font='400 26px '+SANS;
    g.fillText(conPlantilla(T.diploma_que,{nivel:nv.nivel,n:nv.hasta}),A/2,492);
    g.fillStyle=TENUE;
    g.font='400 22px '+SANS;
    g.fillText(window.CURSO_SITIO||'',A/2,548);
    g.font='400 19px '+SANS;
    g.fillText((T.diploma_fecha||'')+': '+hoy(),A/2,592);
    // El aviso es la línea que hace honrado el papel, así que va en el
    // certificado y no solo en la página.
    g.fillStyle=TENUE;g.font='400 16px '+SANS;
    var lineas=partirTexto(g,T.diploma_aviso,A-280), y=B-150;
    for(var i=0;i<lineas.length;i++){g.fillText(lineas[i],A/2,y+i*23)}
    var dominio=window.CURSO_DOMINIO||'';
    if(dominio){g.fillStyle=TINTA;g.font='700 18px '+SANS;g.fillText(dominio,A/2,B-78)}
    var archivo='certificado-'+String(nv.nivel).replace(/[^A-Za-z0-9]/g,'')+'.png';
    function bajar(url){
      var a=document.createElement('a');
      a.href=url;a.download=archivo;
      document.body.appendChild(a);a.click();document.body.removeChild(a);
    }
    if(lienzo.toBlob){
      lienzo.toBlob(function(b){
        if(!b){bajar(lienzo.toDataURL('image/png'));return}
        var url=URL.createObjectURL(b);bajar(url);
        setTimeout(function(){URL.revokeObjectURL(url)},10000);
      },'image/png');
    }else{bajar(lienzo.toDataURL('image/png'))}
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
      // El saludo al terminar: por su nombre, cuánto lleva y cuántos días
      // seguidos. Lo pidió el profesor —«que la página le envíe un mensaje
      // con su nombre»— y esto es lo que un sitio estático puede hacer de
      // verdad: saludar aquí. Mandar un correo o una notificación necesita
      // servidor y una dirección, que es lo que se decidió no tener.
      var saludo=document.createElement('p');
      saludo.className='saludo';saludo.hidden=true;
      var pedirNombre=document.createElement('p');
      pedirNombre.className='pide-nombre';pedirNombre.hidden=true;
      function felicitar(){
        var r=rachas(), total=window.CURSO_PUBLICADAS||0, hechasAhora=hechas().length;
        var quien=nombre();
        // La PRIMERA lección lleva su propio mensaje: es donde más gente se
        // va, y una frase de rotación no dice nada de lo que acaba de pasar.
        // De ahí en adelante, una de las nueve, elegida por el NÚMERO DE
        // LECCIÓN y no al azar: al azar, marcar y desmarcar la misma lección
        // daría tres frases distintas para el mismo acto, y eso se lee como
        // que el sitio está probando textos en vez de hablarte.
        var trozos=[hechasAhora===1
          ? conPlantilla(quien?T.primera_con:T.primera,{nombre:quien})
          : conPlantilla(variante(n,quien?T.bravo_con:T.bravo),{nombre:quien})];
        if(total)trozos.push(conPlantilla(T.cuantas,{n:hechasAhora,total:total}));
        if(r.actual>1)trozos.push(conPlantilla(T.racha,
          {n:r.actual,dias:plural(r.actual,T.racha_dias)}));
        if(total&&total>hechasAhora)trozos.push(conPlantilla(T.faltan,{n:total-hechasAhora}));
        saludo.textContent=trozos.join(' · ');
        saludo.hidden=false;
        // El nombre se pide DESPUÉS de la primera lección marcada y no antes:
        // preguntárselo a quien acaba de llegar es un formulario en la puerta.
        pedirNombre.hidden=!!quien;
      }
      boton.addEventListener('click',function(){
        var lista=hechas(), i=lista.indexOf(n);
        if(i>=0){lista.splice(i,1)}else{lista.push(n)}
        guardar(CLAVE_HECHAS,lista);pintar();
        if(i<0){
          anotarHoy();felicitar();
          if(siguiente){siguiente.classList.add('destacado')}
        }else{saludo.hidden=true;pedirNombre.hidden=true}
      });
      pintar();caja.appendChild(boton);caja.appendChild(saludo);

      // El campo del nombre, montado aquí y no servido en el HTML: sin
      // JavaScript no habría dónde guardarlo y sería un formulario que no
      // hace nada.
      var etiqueta=document.createElement('label');
      etiqueta.textContent=T.nombre_label||'';
      var campo=document.createElement('input');
      campo.type='text';campo.autocomplete='given-name';campo.maxLength=40;
      var guardarNombre=document.createElement('button');
      guardarNombre.type='button';guardarNombre.className='boton secundario';
      guardarNombre.textContent=T.nombre_boton||'';
      var notaNombre=document.createElement('span');
      notaNombre.className='aviso-chico';notaNombre.textContent=T.nombre_nota||'';
      guardarNombre.addEventListener('click',function(){
        var v=campo.value.trim().slice(0,40);
        if(!v)return;
        try{localStorage.setItem(CLAVE_NOMBRE,v)}catch(e){}
        pedirNombre.hidden=true;felicitar();
      });
      pedirNombre.appendChild(etiqueta);pedirNombre.appendChild(campo);
      pedirNombre.appendChild(guardarNombre);pedirNombre.appendChild(notaNombre);
      caja.appendChild(pedirNombre);
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

  // --- el nombre, en la portada y desde la primera visita ---
  //
  // Vive FUERA de `#mio` a propósito. `#mio` se enciende solo cuando ya hay
  // lecciones marcadas, así que el campo metido ahí era invisible justo para
  // quien acaba de llegar, que es a quien el profesor quería preguntarle.
  // Lo que no se hace es una ventana al entrar: un formulario que tapa la
  // página antes de que el visitante haya visto nada es la forma más fiable
  // de perderlo.
  var hueco=document.getElementById('nombre-portada');
  if(hueco){
    var ponerNombre=function(){
      hueco.innerHTML='';
      var quien=nombre();
      if(quien){
        // Ya lo dio: se le saluda y se le deja cambiarlo, sin un campo
        // abierto ocupando sitio.
        var hola=document.createElement('span');
        hola.textContent=conPlantilla(T.vuelta,{nombre:quien});
        var otro=document.createElement('button');
        otro.type='button';otro.className='boton secundario';
        otro.textContent=T.nombre_cambiar||T.nombre_boton||'';
        otro.addEventListener('click',function(){
          try{localStorage.removeItem(CLAVE_NOMBRE)}catch(e){}
          ponerNombre();
        });
        hueco.appendChild(hola);hueco.appendChild(otro);
      }else{
        var et=document.createElement('label');et.textContent=T.nombre_label||'';
        var ca=document.createElement('input');
        ca.type='text';ca.autocomplete='given-name';ca.maxLength=40;
        var bo=document.createElement('button');
        bo.type='button';bo.className='boton secundario';bo.textContent=T.nombre_boton||'';
        var no=document.createElement('span');
        no.className='aviso-chico';no.textContent=T.nombre_nota||'';
        var guardarlo=function(){
          var v=ca.value.trim().slice(0,40);
          if(!v)return;
          try{localStorage.setItem(CLAVE_NOMBRE,v)}catch(e){}
          ponerNombre();
        };
        bo.addEventListener('click',guardarlo);
        // Enter guarda: en el móvil el teclado tapa el botón.
        ca.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();guardarlo()}});
        hueco.appendChild(et);hueco.appendChild(ca);hueco.appendChild(bo);hueco.appendChild(no);
      }
      hueco.hidden=false;
    };
    ponerNombre();
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

    // La racha y el nombre, en el recuadro de progreso.
    //
    // Aquí y NO en una ventana al entrar: un formulario en la puerta, antes
    // de que el visitante haya visto nada, es la forma más fiable de
    // perderlo. El sitio pide el nombre donde ya hay una relación —después
    // de la primera lección marcada— y aquí lo deja cambiar.
    var r=rachas(), quien=nombre();
    var linea=document.createElement('p');
    linea.className='racha';
    var partes=[];
    if(r.actual)partes.push(conPlantilla(T.racha,{n:r.actual,dias:plural(r.actual,T.racha_dias)}));
    if(r.mejor>r.actual)partes.push(conPlantilla(T.racha_mejor,
      {n:r.mejor,dias:plural(r.mejor,T.racha_dias)}));
    if(partes.length){
      linea.textContent=(quien?conPlantilla(T.vuelta,{nombre:quien})+' ':'')+partes.join(' · ');
      var antesDe=document.getElementById('calendario');
      if(antesDe&&antesDe.parentNode===contador)contador.insertBefore(linea,antesDe);
      else contador.appendChild(linea);
    }
    if(!quien){
      var pide=document.createElement('p');
      pide.className='pide-nombre';
      var et=document.createElement('label');et.textContent=T.nombre_label||'';
      var ca=document.createElement('input');
      ca.type='text';ca.autocomplete='given-name';ca.maxLength=40;
      var bo=document.createElement('button');
      bo.type='button';bo.className='boton secundario';bo.textContent=T.nombre_boton||'';
      var no=document.createElement('span');
      no.className='aviso-chico';no.textContent=T.nombre_nota||'';
      bo.addEventListener('click',function(){
        var v=ca.value.trim().slice(0,40);
        if(!v)return;
        try{localStorage.setItem(CLAVE_NOMBRE,v)}catch(e){}
        pide.hidden=true;
        linea.textContent=conPlantilla(T.vuelta,{nombre:v})+' '+partes.join(' · ');
        if(!linea.parentNode){
          var ant=document.getElementById('calendario');
          if(ant&&ant.parentNode===contador)contador.insertBefore(linea,ant);
          else contador.appendChild(linea);
        }
      });
      pide.appendChild(et);pide.appendChild(ca);pide.appendChild(bo);pide.appendChild(no);
      contador.appendChild(pide);
    }
  }


  // --- el calendario del año: una casilla por día ---
  //
  // Lo mismo que `#mio` y las barras del mapa, y por la razón escrita allí:
  // solo si ya hay progreso. Trescientas sesenta y cuatro casillas vacías en
  // la primera visita no se leen como «empieza», se leen como un hueco.
  var cal=document.getElementById('calendario');
  if(cal&&hechasAhora.length){
    var DIA2=86400000, hoyCad=hoy(), hoyMs=dia(hoyCad);
    var puestas={};fechas().forEach(function(f){puestas[f]=1});
    // Se arranca en el lunes de hace 51 semanas, así que las 52 columnas son
    // semanas enteras y la última es la de hoy. Los días de esta semana que
    // aún no han llegado se dibujan vacíos y sin fondo: dejarlos fuera
    // cambiaría el alto de la última columna y la rejilla saldría mellada.
    var lunes=hoyMs-((new Date(hoyMs).getUTCDay()+6)%7)*DIA2;
    var ini=lunes-51*7*DIA2, cuenta=0;
    var rejilla=document.createElement('div');
    rejilla.className='cal-rejilla';
    for(var q=0;q<364;q++){
      var ms=ini+q*DIA2, f=new Date(ms);
      var mm=f.getUTCMonth()+1, dd=f.getUTCDate();
      var clave=f.getUTCFullYear()+'-'+(mm<10?'0':'')+mm+'-'+(dd<10?'0':'')+dd;
      var c=document.createElement('span');
      var clases='cal-dia';
      if(ms>hoyMs){clases+=' futuro'}
      else if(puestas[clave]){clases+=' hecho';cuenta++}
      if(clave===hoyCad)clases+=' es-hoy';
      c.className=clases;
      c.title=clave+(clave===hoyCad&&T.calendario_hoy?' · '+T.calendario_hoy:'');
      rejilla.appendChild(c);
    }
    // Una sola etiqueta para la rejilla entera y las casillas calladas: un
    // lector de pantalla leyendo 364 celdas sería inservible, y el dato que
    // de verdad se quiere oír es cuántos días son.
    var nota=conPlantilla(T.calendario_nota,
      {n:cuenta,dias:plural(cuenta,T.racha_dias)});
    rejilla.setAttribute('role','img');
    rejilla.setAttribute('aria-label',nota);
    var cabc=document.createElement('p');
    cabc.className='cal-cab';
    var fuerte=document.createElement('strong');
    fuerte.textContent=T.calendario||'';
    var suave=document.createElement('span');
    suave.textContent=nota;
    cabc.appendChild(fuerte);cabc.appendChild(suave);
    cal.appendChild(cabc);cal.appendChild(rejilla);
    cal.hidden=false;
    // Desplazada hasta hoy. En el móvil la rejilla desborda y lo que importa
    // es el extremo derecho, no enero.
    rejilla.scrollLeft=rejilla.scrollWidth;
  }

  // --- el certificado, al cerrar un nivel ---
  //
  // Es un sitio estático, así que esto se dibuja en el navegador y no lo
  // firma nadie: el propio papel lo dice —«no es un documento oficial»—. No
  // nombra al Instituto Cervantes, que es la decisión del 2026-10-27: el
  // sitio habla del EXAMEN, que es un hecho, no de una autoría prestada.
  var dip=document.getElementById('diploma');
  if(dip&&hechasAhora.length){
    var niveles=window.CURSO_NIVELES||[];
    var dentroN={};hechasAhora.forEach(function(x){dentroN[x]=1});
    // El nivel más alto que esté ENTERO. A2 pide las 365 y no solo las de
    // A2: terminar A2 incluye haber hecho A1, y un certificado de A2 con el
    // A1 a medias no diría la verdad.
    var logrado=null;
    for(var z=0;z<niveles.length;z++){
      var nv=niveles[z], todo=nv.hasta>0;
      for(var w=1;w<=nv.hasta;w++){if(!dentroN[w]){todo=false;break}}
      if(todo)logrado=nv;
    }
    if(logrado){
      var quienD=nombre();
      if(!quienD){
        // Sin nombre no hay certificado que valga: se señala el campo que ya
        // existe arriba en vez de abrir otro aquí.
        var pideD=document.createElement('p');
        pideD.textContent=T.diploma_pide_nombre||'';
        dip.appendChild(pideD);
      }else{
        var botonD=document.createElement('button');
        botonD.type='button';botonD.className='boton secundario';
        botonD.textContent=conPlantilla(T.diploma_boton,{nivel:logrado.nivel});
        botonD.addEventListener('click',function(){
          // Se esperan las fuentes: sin esto el lienzo dibuja con la letra de
          // reserva del navegador y el certificado sale con otra tipografía
          // que el sitio.
          // `fonts.ready` NO basta, y esto se vio mirando el PNG y no
          // razonándolo: cada cara lleva `unicode-range`, así que el
          // navegador no se baja la cirílica hasta que algo la usa, y
          // dibujar en un lienzo no cuenta como usarla. Sin pedirlas por su
          // nombre Y con el texto que se va a escribir, el certificado sale
          // con la letra de reserva del sistema mientras la página de al
          // lado está en Literata y Onest.
          var pintar=function(){descargarDiploma(logrado,quienD)};
          if(document.fonts&&document.fonts.load){
            var muestra=quienD+(T.diploma_titulo||'')+(T.diploma_sub||'')+(T.diploma_quien||'');
            Promise.all([
              document.fonts.load('700 46px Onest',muestra),
              document.fonts.load('400 22px Onest',muestra),
              document.fonts.load('400 56px Literata',quienD)
            ]).then(pintar,pintar);
          }
          else{pintar()}
        });
        dip.appendChild(botonD);
      }
      dip.hidden=false;
    }
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