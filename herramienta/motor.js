/* Motor del Diario Mural responsive: misma lógica que build.py, en el navegador.
 *
 * Entrada: el PNG del boletín (bytes) y una configuración con los cortes, el modo de cada
 * fila, los enlaces y los textos. Salida: el HTML del correo y las piezas PNG.
 *
 * Modos de fila:
 *   'recorte' = noticias: cada pieza se recorta a su contenido y se centra en su ranura.
 *   'banda'   = bloque sin recorte dentro del marco (se estira al 100 % en móvil).
 *   'sangre'  = bloque sin recorte a todo el ancho, sin marco (encabezado, franjas de color).
 * El pie institucional se corta siempre igual, desde config.pie hasta el final del PNG.
 */
(function (global) {
  'use strict';

  const REDES = [
    [660, 726, 'https://www.facebook.com/uchile/', 'Facebook'],
    [726, 792, 'https://twitter.com/uchile', 'X'],
    [792, 856, 'https://www.instagram.com/uchile/', 'Instagram'],
    [856, 920, 'https://www.youtube.com/uchile', 'YouTube'],
    [920, 1000, 'https://cl.linkedin.com/school/uchile/', 'LinkedIn'],
  ];
  const BLANCO = '#ffffff', AZUL = '#004b93';

  /* ---------- Imagen ---------- */

  function leerPNG(buffer) {
    // UPNG decodifica sin gestión de color: los píxeles salen exactos, como en PIL.
    const png = UPNG.decode(buffer);
    return { ancho: png.width, alto: png.height, rgba: new Uint8Array(UPNG.toRGBA8(png)[0]) };
  }

  function pixel(im, x, y) {
    const i = (y * im.ancho + x) * 4;
    return [im.rgba[i], im.rgba[i + 1], im.rgba[i + 2]];
  }

  // Un píxel es "contenido" si algún canal se aleja más de 12 del blanco (igual que build.py).
  const esContenido = (im, x, y) => { const [r, g, b] = pixel(im, x, y); return r < 243 || g < 243 || b < 243; };
  const esBlancoPuro = (im, x, y) => { const [r, g, b] = pixel(im, x, y); return r === 255 && g === 255 && b === 255; };

  function recortar(im, x0, y0, x1, y1) {
    const w = x1 - x0, h = y1 - y0, out = new Uint8Array(w * h * 4);
    for (let y = 0; y < h; y++) {
      const ini = ((y0 + y) * im.ancho + x0) * 4;
      out.set(im.rgba.subarray(ini, ini + w * 4), y * w * 4);
    }
    return { ancho: w, alto: h, rgba: out };
  }

  function colores(rgba) {
    const vistos = new Set();
    const u32 = new Uint32Array(rgba.buffer, rgba.byteOffset, rgba.length / 4);
    for (let i = 0; i < u32.length; i++) { vistos.add(u32[i]); if (vistos.size > 256) break; }
    return vistos.size;
  }

  function fnv8(bytes) {
    let h = 0x811c9dc5;
    for (let i = 0; i < bytes.length; i++) { h ^= bytes[i]; h = Math.imul(h, 0x01000193); }
    return (h >>> 0).toString(16).padStart(8, '0');
  }

  /* ---------- Detección (sugerencias para la interfaz) ---------- */

  function detectarMarco(im) {
    // Columnas del borde izquierdo que no son blancas en casi todo el alto: ese es el marco.
    let k = 0;
    while (k < 12) {
      let n = 0;
      for (let y = 0; y < im.alto; y++) if (esContenido(im, k, y)) n++;
      if (n / im.alto < 0.75) break;
      k++;
    }
    return k;
  }

  function detectarPie(im) {
    // El pie es la franja de color de abajo: subir por la columna x=10 hasta el primer blanco.
    let y = im.alto - 1;
    while (y > 0 && esContenido(im, 10, y - 1)) y--;
    return y;
  }

  function filaBlanca(im, y, x0, x1) {
    for (let x = x0; x < x1; x++) if (esContenido(im, x, y)) return false;
    return true;
  }

  function columnaBlanca(im, x, y0, y1) {
    // Se tolera una línea horizontal fina que cruce el medianil (hasta 4 px de contenido).
    let n = 0;
    for (let y = y0; y < y1; y++) if (esContenido(im, x, y) && ++n > 4) return false;
    return true;
  }

  function sugerirCortesY(im, marco, pie) {
    const x0 = marco, x1 = im.ancho - marco, cortes = [];
    // Encabezado: hasta la primera fila blanca bajo el bloque de color de arriba.
    let y = 0;
    while (y < pie && !filaBlanca(im, y, x0, x1)) y++;
    if (y > 0 && y < pie) cortes.push(y);
    // Franjas blancas a todo el ancho. Dos franjas separadas solo por una línea fina
    // (un separador de 6 px o menos) cuentan como una; el corte va en la más larga.
    const franjas = [];
    let ini = null;
    for (; y <= pie; y++) {
      const blanca = y < pie && filaBlanca(im, y, x0, x1);
      if (blanca && ini === null) ini = y;
      if (!blanca && ini !== null) { franjas.push([ini, y]); ini = null; }
    }
    const grupos = [];
    for (const f of franjas) {
      const g = grupos.at(-1);
      if (g && f[0] - g.at(-1)[1] <= 6) g.push(f); else grupos.push([f]);
    }
    for (const g of grupos) {
      const larga = g.reduce((a, f) => (f[1] - f[0] > a[1] - a[0] ? f : a));
      // Entre noticias hay 20 px o más de blanco; dentro de una noticia, 10 px o menos.
      const total = g.at(-1)[1] - g[0][0];
      // La franja que sigue pegada a un corte (como la de bajo el encabezado) no genera otro.
      if (total < 18 || g.at(-1)[1] >= pie || g[0][0] <= (cortes.at(-1) || 0) + 2) continue;
      const c = Math.round((larga[0] + larga[1]) / 2);
      if (c > (cortes.at(-1) || 0) + 20) cortes.push(c);
    }
    return cortes;
  }

  function sugerirColumnas(im, marco, y0, y1) {
    const x0 = marco, x1 = im.ancho - marco, cortes = [];
    let ini = null;
    for (let x = x0; x <= x1; x++) {
      const blanca = x < x1 && columnaBlanca(im, x, y0, y1);
      if (blanca && ini === null) ini = x;
      if (!blanca && ini !== null) {
        // Medianil interior de al menos 16 px (los márgenes que tocan los bordes no cuentan).
        if (x - ini >= 16 && ini > x0 && x < x1) cortes.push(Math.round((ini + x) / 2));
        ini = null;
      }
    }
    return cortes;
  }

  function sugerirModo(im, marco, y0, y1) {
    // Si hay color sobre el marco es 'sangre'; si toca el borde interior, 'banda'; si no, noticias.
    let sobreMarco = 0, borde = 0;
    for (let y = y0; y < y1; y++) {
      if (marco && pixel(im, 0, y).join() !== pixel(im, 0, Math.max(0, y0 - 1)).join()) sobreMarco++;
      if (esContenido(im, marco, y) || esContenido(im, im.ancho - marco - 1, y)) borde++;
    }
    if (y0 === 0 || sobreMarco > (y1 - y0) * 0.2) return 'sangre';
    if (borde > (y1 - y0) * 0.2) return 'banda';
    return 'recorte';
  }

  /* ---------- Generación ---------- */

  function generar(png, config) {
    const im = png.rgba ? png : leerPNG(png);
    const W = im.ancho, H = im.alto;
    const MARCO = config.marco || 0, X0 = MARCO, X1 = W - MARCO;
    const piezas = new Map();   // nombre -> bytes PNG
    const avisos = [];

    function guardar(x0, y0, x1, y1, nombre) {
      const c = recortar(im, x0, y0, x1, y1);
      // Con 256 colores o menos se codifica sin pérdida (UPNG igual usa paleta); con más,
      // se reduce a 256 colores como hacía build.py. UPNG con cnum=256 cuantiza siempre.
      const bytes = new Uint8Array(UPNG.encode([c.rgba.buffer], c.ancho, c.alto, colores(c.rgba) <= 256 ? 0 : 256));
      const final = `${nombre}-${fnv8(bytes)}.png`;
      piezas.set(final, bytes);
      return final;
    }

    function anchoContenido(x0, x1, y0, y1) {
      x0 = Math.max(x0, X0); x1 = Math.min(x1, X1);
      let a = null, b = null;
      for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
        if (esContenido(im, x, y)) { if (a === null || x < a) a = x; if (b === null || x + 1 > b) b = x + 1; }
      }
      if (a === null) return null;
      return [a, b];
    }

    function enBlanco(a, b, y) {
      a = Math.max(a, X0); b = Math.min(b, X1);
      for (let x = a; x < b; x++) if (!esBlancoPuro(im, x, y)) return false;
      return true;
    }

    function ranuras(cont) {
      // Cortes entre ranuras (dentro de cada hueco) que dejan cada pieza lo más centrada posible.
      let mejor = null;
      const opciones = cont.slice(1).map((c, i) => [cont[i][1], c[0]]);
      const probar = (k, bordes) => {
        if (k === opciones.length) {
          const bb = [X0, ...bordes, X1];
          let costo = 0;
          cont.forEach(([a, b], i) => { costo += Math.abs((a - bb[i]) - (bb[i + 1] - b)); });
          if (mejor === null || costo < mejor[0]) mejor = [costo, bb];
          return;
        }
        for (let s = opciones[k][0]; s <= opciones[k][1]; s++) probar(k + 1, [...bordes, s]);
      };
      probar(0, []);
      const bb = mejor[1];
      return bb.slice(0, -1).map((s, i) => [s, bb[i + 1]]);
    }

    const esc = t => String(t ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
    const img = (src, w, alt, enlace) => {
      const t = `<img src="${src}" width="${w}" alt="${esc(alt)}" style="display:block;width:100%;height:auto;border:0;outline:none;text-decoration:none;">`;
      return enlace ? `<a href="${esc(enlace)}" target="_blank" style="text-decoration:none;">${t}</a>` : t;
    };
    const ranura = (ancho, contenido, clase, pl, pr) => {
      const interior = pl !== undefined ? `<div class="pad" style="padding:0 ${pr}px 0 ${pl}px;">${contenido}</div>` : contenido;
      return `<div class="${clase}" style="display:inline-block;vertical-align:top;width:100%;max-width:${ancho}px;">${interior}</div>`;
    };
    const fila = html => `<div style="font-size:0;line-height:0;text-align:center;">${html}</div>`;

    // Cuerpo
    const cuerpo = [];
    config.filas.forEach((f, i) => {
      const { y0, y1, modo } = f;
      const cols = f.columnas;
      const sangre = modo === 'sangre' || !MARCO;
      const lim0 = modo === 'sangre' ? 0 : X0, lim1 = modo === 'sangre' ? W : X1;
      const bordes = [lim0, ...cols.slice(1).map(c => c.x0), lim1];
      const partes = [];
      if (modo === 'recorte') {
        const cont = cols.map((c, j) => anchoContenido(bordes[j], bordes[j + 1], y0, y1));
        if (cont.some(c => c === null)) {
          avisos.push(`Fila ${i + 1}: hay una columna sin contenido. Quita ese corte o cambia el modo.`);
          return;
        }
        ranuras(cont).forEach(([s0, s1], j) => {
          const [a, b] = cont[j];
          const n = guardar(a, y0, b, y1, `f${i}c${j}`);
          partes.push(ranura(s1 - s0, img(n, b - a, cols[j].alt, cols[j].enlace), 'slot', a - s0, s1 - b));
        });
      } else {
        cols.forEach((c, j) => {
          const a = bordes[j], b = bordes[j + 1];
          // Si la pieza parte con filas en blanco (como la portada bajo la pestaña de una franja),
          // ese tramo va aparte y se oculta en móvil para no cortar el bloque de color.
          let yb = y0;
          while (yb < y1 && enBlanco(a, b, yb)) yb++;
          let html = '', yIni = y0;
          if (yb - y0 >= 10 && yb < y1) {
            html = `<div class="solo-desk">${img(guardar(a, y0, b, yb, `f${i}c${j}t`), b - a, '', null)}</div>`;
            yIni = yb;
          }
          const n = guardar(a, yIni, b, y1, `f${i}c${j}`);
          partes.push(ranura(b - a, html + img(n, b - a, c.alt, c.enlace), 'slot banda'));
        });
      }
      cuerpo.push({ sangre, y0, y1, html: fila(partes.join('')) });
    });

    // Filas consecutivas con marco forman un tramo; el marco de cada tramo es una imagen de fondo
    // con la copia exacta de sus columnas en el PNG.
    const tramos = [];
    for (const c of cuerpo) {
      const ult = tramos.at(-1);
      if (!c.sangre && ult && !ult.sangre) { ult.y1 = c.y1; ult.filas.push(c.html); }
      else tramos.push({ sangre: c.sangre, y0: c.y0, y1: c.y1, filas: [c.html] });
    }
    for (const t of tramos) if (!t.sangre) {
      t.marcoI = guardar(0, t.y0, MARCO, t.y1, `marco-i${t.y0}`);
      t.marcoD = guardar(X1, t.y0, W, t.y1, `marco-d${t.y0}`);
    }

    // Pie institucional: firma a la izquierda, redes a la derecha con un enlace por icono
    const P = config.pie;
    const f0 = guardar(0, P, 660, H, 'pie0');
    const f1 = guardar(660, P, 1000, P + 29, 'pie1');
    const f3 = guardar(660, P + 74, 1000, H, 'pie3');
    const iconos = REDES.map(([x0, x1, l, a], k) => [guardar(x0, P + 29, x1, P + 74, `red${k}`), x1 - x0, l, a]);

    function armar(base) {
      const s = n => base + n;
      const reimg = h => h.replace(/src="/g, 'src="' + base);
      const marcoTd = n => `<td class="marco" width="${MARCO}" background="${s(n)}" bgcolor="#dddddc" ` +
        `style="width:${MARCO}px;font-size:0;line-height:0;background-color:#dddddc;background-image:url(${s(n)});background-repeat:no-repeat;"></td>`;
      const span = MARCO ? ' colspan="3"' : '';
      let filasHtml = '';
      for (const t of tramos) {
        if (!t.sangre) filasHtml += `<tr>${marcoTd(t.marcoI)}<td valign="top" style="font-size:0;line-height:0;">\n` +
          t.filas.map(reimg).join('\n') + `\n</td>${marcoTd(t.marcoD)}</tr>\n`;
        else filasHtml += `<tr><td${span} style="font-size:0;line-height:0;">` + t.filas.map(reimg).join('') + '</td></tr>\n';
      }
      const ic = iconos.map(([n, w, l, a]) =>
        `<div style="display:inline-block;vertical-align:top;width:${Math.floor(w / 340 * 10000) / 100}%;">${img(s(n), w, a, l)}</div>`).join('');
      const derecha = img(s(f1), 340, 'Infórmate en @uchile', null) + fila(ic) + img(s(f3), 340, '', null);
      const pie = fila(ranura(660, img(s(f0), 660, 'Prensa UChile. Material producido por la Dirección de Comunicaciones junto a comunicadoras y comunicadores de vicerrectorías y direcciones de Rectoría.', null), 'slot pie')
        + ranura(340, derecha, 'slot pie'));
      const fondo = c => `background-color:${c};background-image:linear-gradient(${c},${c});`;
      const lk = 'font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#3f4247;text-decoration:underline;';
      const tabla = 'role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"';
      const audio = config.urlAudio ? `\n<p style="margin:0;padding:12px 16px 16px;text-align:center;"><a class="txt" href="${esc(config.urlAudio)}" target="_blank" style="${lk}">Escucha aquí el Diario Mural Universitario</a></p>` : '';
      return `<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark">
<title>${esc(config.titulo)}</title>
<style>
@media only screen and (max-width:620px){
  .slot{display:block!important;max-width:none!important;}
  .pad{padding:0 16px!important;}
  .marco,.solo-desk{display:none!important;}
}
@media (prefers-color-scheme:dark){ .txt{color:#d0d2d6!important;} }
</style></head>
<body style="margin:0;padding:0;">
<table ${tabla}><tr><td align="center">
<!--[if mso]><table role="presentation" width="1000" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<div style="max-width:1000px;margin:0 auto;">
<p style="margin:0;padding:16px 16px ${audio ? 0 : 16}px;text-align:center;"><a class="txt" href="${esc(config.urlNavegador)}" target="_blank" style="${lk}">Si no ves correctamente este correo, míralo en tu navegador. Haz clic aquí</a></p>${audio}
<table ${tabla} bgcolor="${BLANCO}" style="${fondo(BLANCO)}">
${filasHtml}<tr><td${span} bgcolor="${AZUL}" style="${fondo(AZUL)}font-size:0;line-height:0;">${pie}</td></tr>
</table>
<p class="txt" style="margin:0;padding:16px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#3f4247;text-align:left;">¿Quieres dejar de recibir nuestros correos? Puedes darte de baja <a class="txt" href="[UNSUBSCRIBEURL]" style="color:#3f4247;">aquí</a></p>
</div>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr></table>
</body></html>`;
    }

    // Revisiones
    if (W !== 1000) avisos.push(`El PNG mide ${W} px de ancho; tiene que medir 1000 px.`);
    config.filas.forEach((f, i) => f.columnas.forEach((c, j) => {
      if (f.columnas.length > 1 || f.modo === 'recorte') {
        if (!c.alt) avisos.push(`Fila ${i + 1}, columna ${j + 1}: falta el título (texto alternativo).`);
      }
    }));

    return { armar, piezas, avisos };
  }

  global.Motor = { leerPNG, generar, detectarMarco, detectarPie, sugerirCortesY, sugerirColumnas, sugerirModo };
})(window);
