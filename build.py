from PIL import Image
import json
im = Image.open('dm.png').convert('RGB')
U='https://uchile.cl/'
rows = [
 (0,166,[(0,1000,None,'Diario Mural Universitario. Boletín informativo N° 41, septiembre 2026')]),
 (166,614,[(0,353,U+'u244644','U+GESTIÓN: U. de Chile fortalece gestión financiera institucional con nuevo Módulo de Transferencias en SAP'),
           (353,683,None,'CSAI: Nuevas/os integrantes académicas/os de la CSAI'),
           (683,1000,U+'u243664','SISIB: U. de Chile evaluó 67 revistas científicas de universidades estatales')]),
 (614,941,[(0,450,'https://lnkd.in/p/d-UqZe4m','Dpto. de Pregrado: Nuevo grupo de estudiantes se une al equipo de acompañamiento par de la U. de Chile'),
           (450,1000,U+'u244250','DIRBDE: Proyecto Redes reunió a estudiantes en torno a la sustentabilidad')]),
 (941,1357,[(0,645,U+'u243621','Estrategias metodológicas para el aprendizaje activo. Pueden descargar la guía aquí'),
            (645,1000,U+'u243621','Portada de la guía Estrategias Metodológicas para el Aprendizaje Activo')]),
 (1357,1715,[(0,497,'https://www.universitaria.cl/product/entrevista-con-ricardo-ffrench-davis-el-otro-economista-de-chicago/','Editorial Universitaria: Nuevo libro Entrevista con Ricardo Ffrench-Davis. El otro economista de Chicago'),
             (497,1000,'https://www.youtube.com/playlist?list=PLB4eJlYOs9qc','Sustentabilidad UChile: ¿Cómo llegamos hasta aquí?: UChileTV estrena serie sobre los desafíos de la sustentabilidad')]),
 (1715,2048,[(0,590,U+'u244761','Senado Universitario elige Mesa Directiva para el período 2026-2027'),
             (590,1000,'mailto:diariomural@uchile.cl','¿Tienes una iniciativa, hito, o proyecto que te gustaría compartir con la comunidad UCHILE? Escríbenos a diariomural@uchile.cl')]),
 (2048,2451,[(0,478,U+'u244498','Deporte Azul: FEN se corona campeona de los Juegos Olímpicos Estudiantiles 2026'),
             (478,1000,U+'u244203','Casa de Bello aprueba su nuevo Plan de Desarrollo Institucional y define su rumbo para la próxima década')]),
]
files=[]
def save(box,name):
    im.crop(box).save('s/'+name, optimize=True); files.append(name); return name
def img(name,w,alt,link):
    tag=f'<img src="cid:{name}" width="{w}" alt="{alt}" style="display:block;width:100%;height:auto;border:0;outline:none;text-decoration:none;">'
    return f'<a href="{link}" target="_blank" style="text-decoration:none;">{tag}</a>' if link else tag
out=[]
for i,(y0,y1,cols) in enumerate(rows):
    cells=[]
    for j,(x0,x1,link,alt) in enumerate(cols):
        n=save((x0,y0,x1,y1),f'dm-{i}{j}.png'); w=x1-x0
        cls='' if len(cols)==1 else ' class="col"'
        cells.append(f'<div{cls} style="display:inline-block;vertical-align:top;width:{w/10:.1f}%;">{img(n,w,alt,link)}</div>')
    out.append('<div style="font-size:0;line-height:0;">'+''.join(cells)+'</div>')
# footer
save((0,2451,660,2563),'dm-f0.png')
save((660,2451,1000,2495),'dm-f1.png')
save((660,2540,1000,2563),'dm-f3.png')
icons=[(660,726,'https://www.facebook.com/uchile/','Facebook'),(726,792,'https://twitter.com/uchile','X'),(792,856,'https://www.instagram.com/uchile/','Instagram'),(856,920,'https://www.youtube.com/uchile','YouTube'),(920,1000,'https://cl.linkedin.com/school/uchile/','LinkedIn')]
ic=''
for k,(x0,x1,l,a) in enumerate(icons):
    n=save((x0,2495,x1,2540),f'dm-i{k}.png')
    ic+=f'<div style="display:inline-block;vertical-align:top;width:{(x1-x0)/3.4:.2f}%;">{img(n,x1-x0,a,l)}</div>'
right=img('dm-f1.png',340,'Infórmate en @uchile',None)+'<div style="font-size:0;line-height:0;">'+ic+'</div>'+img('dm-f3.png',340,'',None)
out.append('<div style="font-size:0;line-height:0;"><div class="col" style="display:inline-block;vertical-align:top;width:66.0%;">'+img('dm-f0.png',660,'Prensa UChile. Material producido por la Dirección de Comunicaciones junto a comunicadoras y comunicadores de vicerrectorías y direcciones de Rectoría.',None)+'</div><div class="col" style="display:inline-block;vertical-align:top;width:34.0%;background:#0b3f8c;">'+right+'</div></div>')
lk='font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#3f4247;text-decoration:underline;'
html=f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diario Mural Universitario - La Uchile en septiembre</title>
<style>
@media only screen and (max-width:620px){{ .col{{display:block!important;width:100%!important;}} }}
</style></head>
<body style="margin:0;padding:0;background:#ffffff;">
<div style="max-width:1000px;margin:0 auto;">
<!--[if mso]><table role="presentation" width="1000" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<p style="margin:16px 0 0;text-align:center;padding:0 16px;"><a href="https://uchile.cl/diario-mural" target="_blank" style="{lk}">Si no ves correctamente este correo, míralo en tu navegador. Haz clic aquí</a></p>
<p style="margin:12px 0 16px;text-align:center;padding:0 16px;"><a href="https://drive.google.com/file/d/18-0Km1_qAljpQOGSmAsTQOSsOoC3woE4/view?usp=sharing" target="_blank" style="{lk}">Escucha aquí el Diario Mural Universitario</a></p>
{chr(10).join(out)}
<p style="margin:16px 0;padding:0 16px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#3f4247;">¿Quieres dejar de recibir nuestros correos? Puedes darte de baja <a href="[UNSUBSCRIBEURL]" style="color:#3f4247;">aquí</a></p>
<!--[if mso]></td></tr></table><![endif]-->
</div></body></html>'''
open('diario-mural-responsive.html','w').write(html)
json.dump(files,open('files.json','w'))
print(len(html), len(files))
