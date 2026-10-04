"""Corta el PNG del Diario Mural en piezas y arma un HTML de correo híbrido (fluid/hybrid).

Lo esencial no depende del <style>: cada fila es una celda con columnas inline-block de
width:100% y max-width en px que suman exactamente el ancho de la fila. A 1000 px quedan
lado a lado como en el original; cuando no caben, el flujo del texto las apila solo.
Cada noticia va recortada a su contenido dentro de una ranura (slot) con márgenes en px
elegidos para que, apilada y centrada, quede casi simétrica.

La media query solo mejora el móvil: ranuras al 100 %, margen lateral parejo de 16 px y
sin marco gris. Si Gmail la borra, el correo sigue apilado y legible.

Uso: python3 build.py [carpeta]   (genera index.html con URLs de GitHub y _preview.html local)
"""
from PIL import Image, ImageChops
import sys, io, hashlib
from itertools import product
from pathlib import Path

carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else '2026-09')
REMOTO = 'https://raw.githubusercontent.com/medios-digitales-uchile/diario-mural-responsive/main/' + carpeta.as_posix() + '/'
for viejo in carpeta.glob('*.png'):
    if viejo.name != 'original.png':
        viejo.unlink()
im = Image.open(carpeta / 'original.png').convert('RGB')
W = im.width
U = 'https://uchile.cl/'

# Zonas verticales del PNG: franja azul a sangre hasta y 126; desde ahí marco gris de
# 3 px a cada lado hasta el pie azul (y 2466). La palabra UNIVERSITARIO baja hasta y 144
# (antialiasing incluido), así que su parte inferior va como banda aparte dentro del marco.
Y_MARCO, Y_CUERPO, Y_PIE = 126, 145, 2466
MARCO = 3
X0, X1 = MARCO, W - MARCO          # zona útil dentro del marco
ANCHO = X1 - X0

# (y0, y1, modo, [(x0, x1, enlace, alt)])
# modo: 'banda' = piezas sin recorte dentro del marco (se estiran al 100 % en móvil);
#       'sangre' = piezas sin recorte a todo el ancho, sin marco (la franja naranja pisa el marco);
#       'recorte' = cada pieza se recorta a su contenido y se centra en su ranura.
filas = [
 (Y_MARCO, Y_CUERPO, 'banda', [(0, 1000, None, '')]),
 (Y_CUERPO, 614, 'recorte', [(0, 353, U+'u244644', 'U+GESTIÓN: U. de Chile fortalece gestión financiera institucional con nuevo Módulo de Transferencias en SAP'),
                   (353, 683, None, 'CSAI: Nuevas/os integrantes académicas/os de la CSAI'),
                   (683, 1000, U+'u243664', 'SISIB: U. de Chile evaluó 67 revistas científicas de universidades estatales')]),
 (614, 941, 'recorte', [(0, 450, 'https://lnkd.in/p/d-UqZe4m', 'Dpto. de Pregrado: Nuevo grupo de estudiantes se une al equipo de acompañamiento par de la U. de Chile'),
                   (450, 1000, U+'u244250', 'DIRBDE: Proyecto Redes reunió a estudiantes en torno a la sustentabilidad')]),
 (941, 1358, 'sangre', [(0, 645, U+'u243621', 'Estrategias metodológicas para el aprendizaje activo. Pueden descargar la guía aquí'),
                     (645, 1000, U+'u243621', 'Portada de la guía Estrategias Metodológicas para el Aprendizaje Activo')]),
 (1358, 1715, 'recorte', [(0, 497, 'https://www.universitaria.cl/product/entrevista-con-ricardo-ffrench-davis-el-otro-economista-de-chicago/', 'Editorial Universitaria: Nuevo libro Entrevista con Ricardo Ffrench-Davis. El otro economista de Chicago'),
                     (497, 1000, 'https://www.youtube.com/playlist?list=PLB4eJlYOs9qc', 'Sustentabilidad UChile: ¿Cómo llegamos hasta aquí?: UChileTV estrena serie sobre los desafíos de la sustentabilidad')]),
 (1715, 2064, 'recorte', [(0, 590, U+'u244761', 'Senado Universitario elige Mesa Directiva para el período 2026-2027'),
                     (590, 1000, 'mailto:diariomural@uchile.cl', '¿Tienes una iniciativa, hito, o proyecto que te gustaría compartir con la comunidad UCHILE? Escríbenos a diariomural@uchile.cl')]),
 (2064, Y_PIE, 'recorte', [(0, 478, U+'u244498', 'Deporte Azul: FEN se corona campeona de los Juegos Olímpicos Estudiantiles 2026'),
                     (478, 1000, U+'u244203', 'Casa de Bello aprueba su nuevo Plan de Desarrollo Institucional y define su rumbo para la próxima década')]),
]

BLANCO, AZUL = '#ffffff', '#004b93'

def fondo(color):
    """Color de fondo que Gmail no invierte en modo oscuro: el degradado es background-image."""
    return f'background-color:{color};background-image:linear-gradient({color},{color});'

piezas = {}

def guardar(box, nombre):
    """Guarda la pieza con una huella de su contenido en el nombre: si la imagen cambia,
    cambia la URL, y Gmail o GitHub no pueden servir una versión vieja desde su caché."""
    buf = io.BytesIO()
    im.crop(box).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(buf, 'PNG', optimize=True)
    raiz, ext = nombre.rsplit('.', 1)
    final = f'{raiz}-{hashlib.sha1(buf.getvalue()).hexdigest()[:8]}.{ext}'
    (carpeta / final).write_bytes(buf.getvalue())
    return final

def ancho_contenido(x0, x1, y0, y1):
    x0, x1 = max(x0, X0), min(x1, X1)
    caja = ImageChops.difference(im.crop((x0, y0, x1, y1)), Image.new('RGB', (x1-x0, y1-y0), 'white')).point(lambda v: 255 if v > 12 else 0).getbbox()
    return x0 + caja[0], x0 + caja[2]

def ranuras(contenidos):
    """Elige los cortes entre ranuras (dentro de cada hueco) para que cada pieza quede lo más
    centrada posible en su ranura. Devuelve [(s0, s1)] que cubren X0..X1 sin dejar nada."""
    opciones = [range(b, a + 1) for (_, b), (a, _) in zip(contenidos, contenidos[1:])]
    mejor = None
    for cortes in product(*opciones):
        bordes = [X0, *cortes, X1]
        costo = sum(abs((a - s0) - (s1 - b)) for (a, b), s0, s1 in zip(contenidos, bordes, bordes[1:]))
        if mejor is None or costo < mejor[0]:
            mejor = (costo, bordes)
    bordes = mejor[1]
    return list(zip(bordes, bordes[1:]))

def img(src, w, alt, enlace):
    t = f'<img src="{src}" width="{w}" alt="{alt}" style="display:block;width:100%;height:auto;border:0;outline:none;text-decoration:none;">'
    return f'<a href="{enlace}" target="_blank" style="text-decoration:none;">{t}</a>' if enlace else t

def ranura(ancho, contenido, clase, pl=None, pr=None):
    interior = contenido
    if pl is not None:
        interior = f'<div class="pad" style="padding:0 {pr}px 0 {pl}px;">{contenido}</div>'
    return (f'<div class="{clase}" style="display:inline-block;vertical-align:top;width:100%;max-width:{ancho}px;">'
            f'{interior}</div>')

def fila(html):
    return f'<div style="font-size:0;line-height:0;text-align:center;">{html}</div>'

def en_blanco(a, b, y):
    a, b = max(a, X0), min(b, X1)   # el marco no cuenta
    return not ImageChops.difference(im.crop((a, y, b, y + 1)), Image.new('RGB', (b - a, 1), 'white')).getbbox()

# Cuerpo: (modo, y0, y1, html) por fila
cuerpo = []
for i, (y0, y1, modo, cols) in enumerate(filas):
    lim0, lim1 = (0, W) if modo == 'sangre' else (X0, X1)
    partes, x = [], lim0
    if modo == 'recorte':
        cont = [ancho_contenido(cx0, cx1, y0, y1) for cx0, cx1, _, _ in cols]
        for j, ((s0, s1), (a, b), (_, _, enlace, alt)) in enumerate(zip(ranuras(cont), cont, cols)):
            n = guardar((a, y0, b, y1), f'b{i}{j}.png')
            partes.append(ranura(s1 - s0, img(n, b - a, alt, enlace), 'slot', a - s0, s1 - b))
            x = s1
    else:
        for j, (cx0, cx1, enlace, alt) in enumerate(cols):
            a, b = max(cx0, lim0), min(cx1, lim1)
            # Si la pieza parte con filas en blanco (la portada naranja, bajo la pestaña roja),
            # ese tramo va aparte y se oculta en móvil para no cortar el bloque de color.
            yb = next(y for y in range(y0, y1) if not en_blanco(a, b, y))
            html = ''
            if yb - y0 >= 10:
                html = f'<div class="solo-desk">{img(guardar((a, y0, b, yb), f"b{i}{j}t.png"), b - a, "", None)}</div>'
                y_ini = yb
            else:
                y_ini = y0
            n = guardar((a, y_ini, b, y1), f'b{i}{j}.png')
            partes.append(ranura(b - a, html + img(n, b - a, alt, enlace), 'slot banda'))
            x = b
    assert x == lim1, f'la fila {i} no suma {lim1 - lim0} px'
    cuerpo.append((modo, y0, y1, fila(''.join(partes))))

# Filas consecutivas con marco forman un tramo; el marco de cada tramo es una imagen de fondo
# con la copia exacta de sus columnas en el PNG (lleva un punteado de 4 px a la derecha).
tramos = []
for modo, y0, y1, html in cuerpo:
    if modo != 'sangre' and tramos and tramos[-1][0] == 'marco':
        tramos[-1][2] = y1
        tramos[-1][3].append(html)
    else:
        tramos.append(['sangre' if modo == 'sangre' else 'marco', y0, y1, [html]])
for t in tramos:
    if t[0] == 'marco':
        t.append((guardar((0, t[1], MARCO, t[2]), f'marco-i{t[1]}.png'), guardar((X1, t[1], W, t[2]), f'marco-d{t[1]}.png')))

cabeza = guardar((0, 0, W, Y_MARCO), 'cabeza.png')

# Pie: firma a la izquierda, redes a la derecha con un enlace por icono
f0 = guardar((0, Y_PIE, 660, 2563), 'f0.png')
f1 = guardar((660, Y_PIE, 1000, 2495), 'f1.png')
f3 = guardar((660, 2540, 1000, 2563), 'f3.png')
redes = [(660, 726, 'https://www.facebook.com/uchile/', 'Facebook'), (726, 792, 'https://twitter.com/uchile', 'X'),
         (792, 856, 'https://www.instagram.com/uchile/', 'Instagram'), (856, 920, 'https://www.youtube.com/uchile', 'YouTube'),
         (920, 1000, 'https://cl.linkedin.com/school/uchile/', 'LinkedIn')]
iconos = [(guardar((x0, 2495, x1, 2540), f'i{k}.png'), x1 - x0, l, a) for k, (x0, x1, l, a) in enumerate(redes)]

def armar(base):
    s = lambda n: base + n
    def reimg(html):
        return html.replace('src="', 'src="' + base)
    marco = lambda n: (f'<td class="marco" width="{MARCO}" background="{s(n)}" bgcolor="#dddddc" '
                       f'style="width:{MARCO}px;font-size:0;line-height:0;background-color:#dddddc;background-image:url({s(n)});background-repeat:no-repeat;"></td>')
    filas_html = ''
    for t in tramos:
        if t[0] == 'marco':
            filas_html += (f'<tr>{marco(t[4][0])}<td valign="top" style="font-size:0;line-height:0;">\n'
                           + '\n'.join(reimg(f) for f in t[3]) + f'\n</td>{marco(t[4][1])}</tr>\n')
        else:
            filas_html += f'<tr><td colspan="3" style="font-size:0;line-height:0;">' + ''.join(reimg(f) for f in t[3]) + '</td></tr>\n'
    # Iconos en % del bloque de 340 px, redondeados hacia abajo para no pasar del 100 %
    ic = ''.join(f'<div style="display:inline-block;vertical-align:top;width:{int(w/340*10000)/100}%;">{img(s(n), w, a, l)}</div>'
                 for n, w, l, a in iconos)
    derecha = img(s(f1), 340, 'Infórmate en @uchile', None) + fila(ic) + img(s(f3), 340, '', None)
    pie = fila(ranura(660, img(s(f0), 660, 'Prensa UChile. Material producido por la Dirección de Comunicaciones junto a comunicadoras y comunicadores de vicerrectorías y direcciones de Rectoría.', None), 'slot pie')
               + ranura(340, derecha, 'slot pie'))
    lk = 'font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#3f4247;text-decoration:underline;'
    tabla = 'role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"'
    return f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark">
<title>Diario Mural Universitario - La Uchile en septiembre</title>
<style>
@media only screen and (max-width:620px){{
  .slot{{display:block!important;max-width:none!important;}}
  .pad{{padding:0 16px!important;}}
  .marco,.solo-desk{{display:none!important;}}
}}
@media (prefers-color-scheme:dark){{ .txt{{color:#d0d2d6!important;}} }}
</style></head>
<body style="margin:0;padding:0;">
<table {tabla}><tr><td align="center">
<!--[if mso]><table role="presentation" width="1000" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<div style="max-width:1000px;margin:0 auto;">
<p style="margin:0;padding:16px 16px 0;text-align:center;"><a class="txt" href="https://uchile.cl/diario-mural" target="_blank" style="{lk}">Si no ves correctamente este correo, míralo en tu navegador. Haz clic aquí</a></p>
<p style="margin:0;padding:12px 16px 16px;text-align:center;"><a class="txt" href="https://drive.google.com/file/d/18-0Km1_qAljpQOGSmAsTQOSsOoC3woE4/view?usp=sharing" target="_blank" style="{lk}">Escucha aquí el Diario Mural Universitario</a></p>
<table {tabla} bgcolor="{BLANCO}" style="{fondo(BLANCO)}">
<tr><td colspan="3" style="font-size:0;line-height:0;">{img(s(cabeza), W, 'Diario Mural Universitario. Boletín informativo N° 41, septiembre 2026', None)}</td></tr>
{filas_html}<tr><td colspan="3" bgcolor="{AZUL}" style="{fondo(AZUL)}font-size:0;line-height:0;">{pie}</td></tr>
</table>
<p class="txt" style="margin:0;padding:16px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#3f4247;text-align:left;">¿Quieres dejar de recibir nuestros correos? Puedes darte de baja <a class="txt" href="[UNSUBSCRIBEURL]" style="color:#3f4247;">aquí</a></p>
</div>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr></table>
</body></html>'''

html = armar(REMOTO)
(carpeta / 'index.html').write_text(html, encoding='utf-8')
(carpeta / '_preview.html').write_text(armar(''), encoding='utf-8')
print('ok', len(html), 'bytes')
