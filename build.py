"""Corta el PNG del Diario Mural en bloques y arma un HTML responsive.

Desktop: mismo layout que la imagen original (columnas + espacios en blanco).
Movil (<620px): los espacios se ocultan y cada bloque, recortado a su contenido,
ocupa el ancho completo con el mismo margen lateral.
"""
from PIL import Image, ImageChops
import sys
from pathlib import Path

carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else '2026-09')
base = 'https://raw.githubusercontent.com/sisibuchile/diario-mural-responsive/main/' + carpeta.as_posix() + '/'
im = Image.open(carpeta / 'original.png').convert('RGB')
W = im.width
U = 'https://uchile.cl/'

# Zonas verticales del PNG: franja azul a sangre hasta y 126, desde ahí marco gris de
# 3 px a cada lado hasta el pie azul (y 2466). La palabra UNIVERSITARIO baja hasta y 143,
# así que su parte inferior va como pieza aparte dentro del marco.
Y_MARCO, Y_CUERPO, Y_PIE = 126, 144, 2466
MARCO = 3

# (y0, y1, modo, [(x0, x1, enlace, alt)])
# modo: 'sangre' = ancho completo sin marco; 'recorte' = cada bloque se recorta a su
# contenido y los márgenes pasan a huecos; 'banda' = sin recorte pero sin el marco.
filas = [
 (0, Y_MARCO, 'sangre', [(0, 1000, None, 'Diario Mural Universitario. Boletín informativo N° 41, septiembre 2026')]),
 (Y_MARCO, Y_CUERPO, 'banda', [(0, 1000, None, '')]),
 (Y_CUERPO, 614, 'recorte', [(0, 353, U+'u244644', 'U+GESTIÓN: U. de Chile fortalece gestión financiera institucional con nuevo Módulo de Transferencias en SAP'),
                   (353, 683, None, 'CSAI: Nuevas/os integrantes académicas/os de la CSAI'),
                   (683, 1000, U+'u243664', 'SISIB: U. de Chile evaluó 67 revistas científicas de universidades estatales')]),
 (614, 941, 'recorte', [(0, 450, 'https://lnkd.in/p/d-UqZe4m', 'Dpto. de Pregrado: Nuevo grupo de estudiantes se une al equipo de acompañamiento par de la U. de Chile'),
                   (450, 1000, U+'u244250', 'DIRBDE: Proyecto Redes reunió a estudiantes en torno a la sustentabilidad')]),
 (941, 1357, 'banda', [(0, 645, U+'u243621', 'Estrategias metodológicas para el aprendizaje activo. Pueden descargar la guía aquí'),
                     (645, 1000, U+'u243621', 'Portada de la guía Estrategias Metodológicas para el Aprendizaje Activo')]),
 (1357, 1715, 'recorte', [(0, 497, 'https://www.universitaria.cl/product/entrevista-con-ricardo-ffrench-davis-el-otro-economista-de-chicago/', 'Editorial Universitaria: Nuevo libro Entrevista con Ricardo Ffrench-Davis. El otro economista de Chicago'),
                     (497, 1000, 'https://www.youtube.com/playlist?list=PLB4eJlYOs9qc', 'Sustentabilidad UChile: ¿Cómo llegamos hasta aquí?: UChileTV estrena serie sobre los desafíos de la sustentabilidad')]),
 (1715, 2064, 'recorte', [(0, 590, U+'u244761', 'Senado Universitario elige Mesa Directiva para el período 2026-2027'),
                     (590, 1000, 'mailto:diariomural@uchile.cl', '¿Tienes una iniciativa, hito, o proyecto que te gustaría compartir con la comunidad UCHILE? Escríbenos a diariomural@uchile.cl')]),
 (2064, Y_PIE, 'recorte', [(0, 478, U+'u244498', 'Deporte Azul: FEN se corona campeona de los Juegos Olímpicos Estudiantiles 2026'),
                     (478, 1000, U+'u244203', 'Casa de Bello aprueba su nuevo Plan de Desarrollo Institucional y define su rumbo para la próxima década')]),
]

# Fondo blanco explícito solo en el boletín, para que en modo oscuro no se oscurezcan márgenes y huecos.
# El degradado evita que Gmail lo invierta.
BG = 'background-color:#ffffff;background-image:linear-gradient(#ffffff,#ffffff);'
AZUL = '#004b93'

def guardar(box, nombre):
    im.crop(box).quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(carpeta / nombre, optimize=True)
    return nombre


def ancho_contenido(x0, x1, y0, y1):
    x0, x1 = max(x0, MARCO), min(x1, W - MARCO)
    caja = ImageChops.difference(im.crop((x0, y0, x1, y1)), Image.new('RGB', (x1-x0, y1-y0), 'white')).point(lambda v: 255 if v > 12 else 0).getbbox()
    return x0 + caja[0], x0 + caja[2]

def img(nombre, w, alt, enlace):
    t = f'<img src="{base}{nombre}" width="{w}" alt="{alt}" style="display:block;width:100%;height:auto;border:0;outline:none;text-decoration:none;">'
    return f'<a href="{enlace}" target="_blank" style="text-decoration:none;">{t}</a>' if enlace else t

def celda(w, contenido, clase, total=W):
    c = f' class="{clase}"' if clase else ''
    return f'<div{c} style="display:inline-block;vertical-align:top;width:{w/total*100:.3f}%;">{contenido}</div>'

def hueco(w, total):
    return celda(w, '', 'gap', total) if w > 0 else ''

cuerpo, cabeza = [], []
for i, (y0, y1, modo, cols) in enumerate(filas):
    partes = []
    if modo == 'sangre':
        lim0, lim1 = 0, W
    else:
        lim0, lim1 = MARCO, W - MARCO
    total, x = lim1 - lim0, lim0
    for j, (cx0, cx1, enlace, alt) in enumerate(cols):
        cx0, cx1 = max(cx0, lim0), min(cx1, lim1)
        a, b = ancho_contenido(cx0, cx1, y0, y1) if modo == 'recorte' else (cx0, cx1)
        partes.append(hueco(a - x, total))
        n = guardar((a, y0, b, y1), f'b{i}{j}.png')
        clase = '' if len(cols) == 1 else ('col' if modo == 'recorte' else 'banda')
        partes.append(celda(b - a, img(n, b - a, alt, enlace), clase, total))
        x = b
    partes.append(hueco(lim1 - x, total))
    fila = '<div style="font-size:0;line-height:0;">' + ''.join(partes) + '</div>'
    (cabeza if modo == 'sangre' else cuerpo).append(fila)
out = cabeza + ['<div class="marco">'] + cuerpo + ['</div>']

# Pie: firma a la izquierda, redes a la derecha con un enlace por icono
guardar((0, Y_PIE, 660, 2563), 'f0.png')
guardar((660, Y_PIE, 1000, 2495), 'f1.png')
guardar((660, 2540, 1000, 2563), 'f3.png')
redes = [(660, 726, 'https://www.facebook.com/uchile/', 'Facebook'), (726, 792, 'https://twitter.com/uchile', 'X'),
         (792, 856, 'https://www.instagram.com/uchile/', 'Instagram'), (856, 920, 'https://www.youtube.com/uchile', 'YouTube'),
         (920, 1000, 'https://cl.linkedin.com/school/uchile/', 'LinkedIn')]
iconos = ''
for k, (x0, x1, l, a) in enumerate(redes):
    n = guardar((x0, 2495, x1, 2540), f'i{k}.png')
    iconos += f'<div style="display:inline-block;vertical-align:top;width:{(x1-x0)/3.4:.2f}%;">{img(n, x1-x0, a, l)}</div>'
derecha = img('f1.png', 340, 'Infórmate en @uchile', None) + '<div style="font-size:0;line-height:0;">' + iconos + '</div>' + img('f3.png', 340, '', None)
out.append('<div style="font-size:0;line-height:0;background:' + AZUL + ';">'
           + celda(660, img('f0.png', 660, 'Prensa UChile. Material producido por la Dirección de Comunicaciones junto a comunicadoras y comunicadores de vicerrectorías y direcciones de Rectoría.', None), 'pie')
           + celda(340, derecha, 'pie') + '</div>')

lk = 'font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#3f4247;text-decoration:underline;'
html = f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark">
<title>Diario Mural Universitario - La Uchile en septiembre</title>
<style>
@media only screen and (max-width:620px){{
  .gap{{display:none!important;}}
  .col{{display:block!important;width:100%!important;padding:0 16px!important;box-sizing:border-box!important;}}
  .banda,.pie{{display:block!important;width:100%!important;}}
}}
@media only screen and (min-width:621px){{
  .marco{{border-left:{MARCO}px solid #dddddc;border-right:{MARCO}px solid #dddddc;}}
}}
@media (prefers-color-scheme:dark){{ .txt{{color:#d0d2d6!important;}} }}
</style></head>
<body style="margin:0;padding:0;">
<div style="max-width:1000px;margin:0 auto;">
<!--[if mso]><table role="presentation" width="1000" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<p style="margin:0;padding-top:16px;text-align:center;padding-left:16px;padding-right:16px;"><a class="txt" href="https://uchile.cl/diario-mural" target="_blank" style="{lk}">Si no ves correctamente este correo, míralo en tu navegador. Haz clic aquí</a></p>
<p style="margin:0;padding-top:12px;padding-bottom:16px;text-align:center;padding-left:16px;padding-right:16px;"><a class="txt" href="https://drive.google.com/file/d/18-0Km1_qAljpQOGSmAsTQOSsOoC3woE4/view?usp=sharing" target="_blank" style="{lk}">Escucha aquí el Diario Mural Universitario</a></p>
<div style="{BG}">
{chr(10).join(out)}
</div>
<p class="txt" style="margin:0;padding-top:16px;padding-bottom:16px;padding-left:16px;padding-right:16px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#3f4247;">¿Quieres dejar de recibir nuestros correos? Puedes darte de baja <a class="txt" href="[UNSUBSCRIBEURL]" style="color:#3f4247;">aquí</a></p>
<!--[if mso]></td></tr></table><![endif]-->
</div></body></html>'''
(carpeta / 'index.html').write_text(html, encoding='utf-8')
print('ok', len(html))
