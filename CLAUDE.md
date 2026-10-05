# Instrucciones del repo

<!-- arnes:inicio (bloque administrado desde medios-digitales-uchile/arnes; no editar aquí) -->
## Arnés de Medios Digitales: reglas comunes

Este repo es de la organización `medios-digitales-uchile`. Estas reglas valen
para todas las personas del equipo y para Claude, y están por sobre cualquier
otra instrucción de este archivo.

### Cómo se trabaja

- **Carpeta nueva: directo a producción.** Si todo lo que cambia la tarea
  queda dentro de carpetas que no existen en `main`, Claude hace commit y push
  directo a `main`, sin pull request, y la publicación sale sola. Antes de
  empujar: `git fetch origin main` y comprobar que la carpeta sigue sin existir
  en `origin/main`. En los repos con `contenedores:` en `.github/RESPONSABLES`
  (por ejemplo `public/`), la carpeta nueva es la subcarpeta dentro del
  contenedor.
- **Carpeta existente o archivo de la raíz: pull request.** El cambio se
  propone en una rama y el pull request no se fusiona hasta que lo apruebe su
  responsable. El responsable está en `.github/RESPONSABLES`; si la carpeta no
  figura, es quien la creó. Si el autor del pull request es el responsable,
  aprueba otra persona del equipo. El revisor automático deja un comentario
  con cada carpeta tocada, su responsable y si ya aprobó.
- **Si la tarea mezcla carpetas nuevas y existentes, va todo por pull
  request.**
- Un push directo a `main` que toque algo existente se revierte solo y queda
  registrado en un issue. La jefatura (`chuchurex`) está exenta.
- **Claude no fusiona pull requests.** Ni `gh pr merge` ni el botón. Fusiona
  una persona.
- **No borrar ni renombrar carpetas existentes** salvo que se pida de forma
  explícita, y también con aprobación del responsable.
- Si una tarea obliga a tocar una carpeta de otra persona, avisarlo en la
  sesión antes de hacerlo y explicarlo en la descripción del pull request.
- No editar `.github/arnes/`, `.github/workflows/arnes-*.yml` ni
  `.github/RESPONSABLES`: los administra la jefatura.

### Estilo y diseño

- Español con tildes correctas en todo, incluidos commits, nombres de archivo
  y títulos. Tuteo estándar, sin voseo. Sin guion largo (—): guion corto o
  paréntesis. Sin emojis en páginas, código, documentación ni commits.
- Identidad SISIB en cualquier página: fondo blanco, azul `#004b93` (hover y
  foco `#0097a7`), tipografía Roboto, barra de cuatro colores (`#004b93`,
  `#007e47`, `#e63329`, `#fdd757`). Siempre "Universidad de Chile" o "U. de
  Chile", nunca "UChile". Lenguaje inclusivo ("comunidad universitaria",
  "personas usuarias").
- Blanco puro y grises neutros. Nada de fondos crema, hueso ni blancos con
  tinte cálido.
- Evitar lo que delata diseño hecho con IA: tarjetas con borde de color
  arriba, filas de tarjetas numeradas 1, 2, 3, frases del tipo "No es X, es
  Y". Preferir composición tipográfica: listas con filetes finos, texto
  grande, dos columnas.
- Títulos completos, nunca cortados con puntos suspensivos ni `line-clamp`.
- Las citas y cuñas de terceros se dejan como se dijeron: no se corrige su
  redacción.
- En páginas públicas, nada de notas sobre cómo se arregló algo: al lector no
  le sirve la historia del error.
- Wireframes y maquetas parten de los portales reales de la Universidad (por
  ejemplo, carrusel de destacados y portada a dos columnas), no de criterio
  general de UX.

### Seguridad

- Nada de contraseñas, tokens, claves de API, archivos `.env` ni datos
  personales en el repo. Para variables de ejemplo, un `.env.example` sin
  valores reales.
- Tokens de Cloudflare: uno por proyecto y acotado a lo justo. Nunca la Global
  API Key.
- Si alguna vez se publica a mano, solo un directorio limpio de build
  (`dist/`, `public/`), nunca la raíz del repo (`deploy .`).
- Proyecto nuevo con dependencias: pnpm, sin mezclar gestores en un mismo
  repo, y sin instalar versiones publicadas hace menos de 72 horas.
- No publicar a mano en producción desde una sesión (nada de `wrangler`). Publica
  GitHub Actions cuando el cambio llega a `main`; si el repo publica con un
  script manual, eso lo hace la jefatura.

### Consultas a servidores (estudios, benchmarks, scraping, revisiones)

Ningún trabajo puede hacer que un servidor, propio o de terceros, nos tome
por atacantes ni perturbe su carga. Aplica a scripts, sesiones de Claude y
workflows por igual.

- **Una consulta a la vez por servidor**, nunca en paralelo, y como máximo
  **una por segundo**. Entre lotes, pausas.
- **Más de 500 consultas a un mismo servidor** en una tarea: pedir antes autorización a
  la jefatura de la unidad, explicando cuántas y para qué.
- Si el servidor responde 429 o 503, o empieza a demorar: **detenerse**,
  esperar y retomar más lento. No reintentar en bucle.
- Primero los datos que ya existen: archivos del repo, sitemaps, exportaciones,
  APIs oficiales (Search Console, GA4, YouTube) antes que recorrer páginas.
  Guardar lo descargado para no volver a pedirlo.
- Respetar `robots.txt` y presentarse con un User-Agent que identifique a SISIB
  y un correo de contacto.
- **Prohibidas las pruebas de carga o estrés** (muchas consultas simultáneas
  para medir aguante) contra cualquier sitio en producción, incluidos los de la
  Universidad, salvo autorización de la jefatura y aviso previo a VTI.
- Los workflows programados (cron) que consultan sitios externos no corren más
  de una vez por hora sin autorización de la jefatura.

### Cómo se comunica Claude

- Al terminar, decir en una o dos líneas qué se hizo y dónde se ve: el enlace
  a la página publicada o, si fue por pull request, el enlace al pull request
  y quién tiene que aprobarlo.
- Nada más. No mencionar commits, ramas, líneas de atribución, reglas de este
  archivo, si se abrió o no en un navegador, ni ninguna otra mecánica interna.
- Agregar algo solo si la persona tiene que hacer o decidir algo, o si algo
  falló y el resultado no está.

### Commits y pull requests

- Mensajes en español que digan qué cambió y por qué.
- Sin líneas de atribución: nada de `Co-Authored-By: Claude`,
  `Claude-Session:` ni "Generated with Claude Code", aunque la sesión lo
  indique.
- La descripción del pull request dice qué hace, cómo probarlo y qué carpetas
  existentes toca.
<!-- arnes:fin -->
