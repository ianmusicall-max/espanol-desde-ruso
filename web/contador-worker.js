/**
 * El contador de visitas del pie. Se despliega en la cuenta de Cloudflare del
 * profesor, que es la misma donde ya vive el dominio.
 *
 * POR QUÉ PROPIO Y NO UN CONTADOR GRATUITO: los de siempre son proyectos de
 * aficionado que se caen. hits.sh tuvo que mudarse de dominio porque no podía
 * pagar la renovación, y un dominio caducado cargándose en las 394 páginas de
 * este sitio deja de ser un contador y pasa a ser una petición a quien lo haya
 * registrado después. Esto no puede desaparecer y no mete a nadie en el medio:
 * por eso la política de privacidad puede decir que el contador es nuestro.
 *
 * NO GUARDA NADA DEL LECTOR. Un entero en KV y nada más: ni IP, ni cabeceras,
 * ni cookie. Cloudflare ve la IP porque la ve en cualquier petición, y eso
 * está escrito en la política.
 *
 * ────────────────────────────────── desplegarlo ──────────────────────────────
 *  1. dash.cloudflare.com → Storage & Databases → KV → Create a namespace,
 *     de nombre `visitas`.
 *  2. Compute (Workers) → Create → Start from Hello World → nombre
 *     `contador`. Pegar este archivo en el editor y Deploy.
 *  3. En el Worker → Settings → Bindings → Add → KV namespace:
 *     Variable name `VISITAS`, namespace `visitas`.
 *  4. Copiar la URL que da (`https://contador.<algo>.workers.dev`) y pegarla
 *     en `contador.endpoint` de `web/sitio.yaml`. Reconstruir el sitio.
 *
 * El plan gratuito da 100.000 lecturas y 1.000 ESCRITURAS al día. Se escribe
 * una vez por visita y no por página, así que 1.000 son 1.000 visitas diarias;
 * pasadas esas, la escritura falla y el número deja de subir hasta mañana,
 * pero el contador sigue leyéndose. El día que el sitio tenga ese tráfico,
 * esto se cambia por Durable Objects.
 */

// Solo este origen puede sumar. Sin esto, cualquiera infla el número desde su
// propia página y el contador deja de medir este sitio.
const ORIGEN = "https://espanoldesderuso.com";
const CLAVE = "total";

export default {
  async fetch(request, env) {
    const cabeceras = {
      "access-control-allow-origin": ORIGEN,
      "access-control-allow-methods": "GET, POST, OPTIONS",
      "cache-control": "no-store",
      "content-type": "application/json; charset=utf-8",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: cabeceras });
    }

    let total = parseInt((await env.VISITAS.get(CLAVE)) || "0", 10) || 0;

    // GET lee y POST suma. Quién de los dos se manda lo decide el navegador
    // mirando su propia pestaña, así que recargar no infla nada.
    if (request.method === "POST" && request.headers.get("origin") === ORIGEN) {
      total += 1;
      // KV es de consistencia eventual y esto es leer-sumar-guardar, así que
      // dos visitas en el mismo segundo pueden contarse como una. Con el
      // tráfico de hoy no pasa, y perder una visita de vez en cuando es
      // mucho más barato que montar un Durable Object para esto.
      try {
        await env.VISITAS.put(CLAVE, String(total));
      } catch (e) {
        // Agotadas las escrituras del día. Se devuelve el número leído: que
        // el contador no suba es un detalle; que la página reviente, no.
      }
    }

    return new Response(JSON.stringify({ total }), { headers: cabeceras });
  },
};
