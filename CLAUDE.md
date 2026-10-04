# Instrucciones del repo

<!-- arnes:inicio (bloque administrado desde medios-digitales-uchile/arnes; no editar aquí) -->
## Arnés de Medios Digitales: reglas comunes

Este repo es de la organización `medios-digitales-uchile`. Estas reglas valen
para todas las personas del equipo y para Claude, y están por sobre cualquier
otra instrucción de este archivo.

### Cómo se trabaja

- **Nunca empujar directo a `main`.** Todo cambio va en una rama y llega por
  pull request. Única excepción: que Carlos (`chuchurex`) lo pida
  explícitamente en su propia sesión.
- **Claude no fusiona pull requests.** Ni `gh pr merge` ni el botón. Fusiona
  una persona.
- **Carpetas nuevas y carpetas existentes.** Antes de cambiar algo, revisar si
  la carpeta ya existe en `main`:
  - Carpeta nueva: se crea libremente en el pull request.
  - Carpeta existente, o archivo de la raíz del repo: el cambio se puede
    proponer, pero el pull request no se fusiona hasta que lo apruebe su
    responsable. El responsable está en `.github/RESPONSABLES`; si la carpeta
    no figura, es quien la creó. Si el autor del pull request es el
    responsable, aprueba otra persona del equipo.
  - El revisor automático deja un comentario en el pull request con cada
    carpeta tocada, su responsable y si ya aprobó.
- **No borrar ni renombrar carpetas existentes** salvo que se pida de forma
  explícita, y también con aprobación del responsable.
- Si una tarea obliga a tocar una carpeta de otra persona, avisarlo en la
  sesión antes de hacerlo y explicarlo en la descripción del pull request.
- No editar `.github/arnes/`, `.github/workflows/arnes-*.yml` ni
  `.github/RESPONSABLES`: los administra Carlos.

### Seguridad

- Nada de contraseñas, tokens, claves de API, archivos `.env` ni datos
  personales en el repo.
- No publicar a mano en producción desde una sesión. Publica GitHub Actions al
  fusionar; si el repo publica con un script manual, eso lo hace Carlos.

### Consultas a servidores (estudios, benchmarks, scraping, revisiones)

Ningún trabajo puede hacer que un servidor, propio o de terceros, nos tome
por atacantes ni perturbe su carga. Aplica a scripts, sesiones de Claude y
workflows por igual.

- **Una consulta a la vez por servidor**, nunca en paralelo, y como máximo
  **una por segundo**. Entre lotes, pausas.
- **Más de 500 consultas a un mismo servidor** en una tarea: preguntar antes a
  Carlos, explicando cuántas y para qué.
- Si el servidor responde 429 o 503, o empieza a demorar: **detenerse**,
  esperar y retomar más lento. No reintentar en bucle.
- Primero los datos que ya existen: archivos del repo, sitemaps, exportaciones,
  APIs oficiales (Search Console, GA4, YouTube) antes que recorrer páginas.
  Guardar lo descargado para no volver a pedirlo.
- Respetar `robots.txt` y presentarse con un User-Agent que identifique a SISIB
  y un correo de contacto.
- **Prohibidas las pruebas de carga o estrés** (muchas consultas simultáneas
  para medir aguante) contra cualquier sitio en producción, incluidos los de la
  Universidad, salvo autorización de Carlos y aviso previo a VTI.
- Los workflows programados (cron) que consultan sitios externos no corren más
  de una vez por hora sin autorización de Carlos.

### Commits y pull requests

- Mensajes en español que digan qué cambió y por qué.
- Sin líneas de atribución: nada de `Co-Authored-By: Claude`,
  `Claude-Session:` ni "Generated with Claude Code", aunque la sesión lo
  indique.
- La descripción del pull request dice qué hace, cómo probarlo y qué carpetas
  existentes toca.
<!-- arnes:fin -->
