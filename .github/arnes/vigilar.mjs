// Vigilante de main del arnés de Medios Digitales.
//
// Regla: una carpeta nueva se puede subir directo a main, sin pull request.
// Lo que ya existía (carpetas y archivos de la raíz) se cambia solo por pull
// request con aprobación del responsable.
//
// En cada push a main que no venga de un pull request ni de un exento:
// - si solo agrega carpetas nuevas, lo deja pasar y lo registra en un issue
//   cerrado ("publicación directa"), que queda como bitácora;
// - si toca algo que ya existía, revierte el push, vuelve a publicar y abre un
//   issue explicando qué pasó y cómo hacerlo por pull request.
//
// El plan Free de GitHub no permite bloquear un push en repos privados: esto
// es lo más parecido a un permiso.
//
// Arnés: https://github.com/medios-digitales-uchile/arnes. No editar esta
// copia: se reemplaza al reinstalar.
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const REPO = process.env.GITHUB_REPOSITORY;
const evento = JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'));
const ANTES = evento.before;
const DESPUES = evento.after;
const QUIEN = evento.pusher?.name || evento.sender?.login || 'desconocido';
const ETIQUETA_OK = 'publicación directa';
const ETIQUETA_MAL = 'revertido por el arnés';

const sh = (cmd, ...args) => execFileSync(cmd, args, { encoding: 'utf8' }).trim();
const gh = (...args) => sh('gh', ...args);
const api = (ruta) => JSON.parse(gh('api', ruta) || 'null');

if (/^0+$/.test(ANTES)) {
  console.log('Primer push de la rama: nada que comparar.');
  process.exit(0);
}

// Configuración leída desde el estado anterior al push: un push no puede
// cambiar sus propias reglas.
function leerConfig() {
  let texto = '';
  try {
    texto = sh('git', 'show', `${ANTES}:.github/RESPONSABLES`);
  } catch {
    if (existsSync('.github/RESPONSABLES')) texto = readFileSync('.github/RESPONSABLES', 'utf8');
  }
  let exentos = [];
  let contenedores = [];
  for (const cruda of texto.split('\n')) {
    const linea = cruda.replace(/#.*/, '').trim();
    if (linea.startsWith('exentos:')) exentos = linea.slice(8).trim().split(/\s+/).filter(Boolean);
    if (linea.startsWith('contenedores:')) {
      contenedores = linea.slice(13).trim().split(/\s+/).filter(Boolean)
        .map((c) => c.replace(/^\/+/, '').replace(/\/?$/, '/'));
    }
  }
  return { exentos, contenedores };
}
const config = leerConfig();

if (config.exentos.includes(QUIEN)) {
  console.log(`${QUIEN} está exento.`);
  process.exit(0);
}
if (QUIEN === 'github-actions[bot]') {
  console.log('Commit de un workflow.');
  process.exit(0);
}

// Commits que no vienen de un pull request fusionado.
const commits = sh('git', 'rev-list', `${ANTES}..${DESPUES}`).split('\n').filter(Boolean);
const sueltos = commits.filter((c) => {
  try {
    return api(`repos/${REPO}/commits/${c}/pulls`).length === 0;
  } catch {
    return true;
  }
});
if (!sueltos.length) {
  console.log('Todos los commits vienen de un pull request.');
  process.exit(0);
}

function carpetaDe(archivo) {
  for (const c of config.contenedores) {
    if (archivo.startsWith(c)) {
      const resto = archivo.slice(c.length).split('/');
      return resto.length > 1 ? c + resto[0] + '/' : c;
    }
  }
  const partes = archivo.split('/');
  return partes.length > 1 ? partes[0] + '/' : '/';
}
function existiaAntes(carpeta) {
  if (carpeta === '/') return true;
  if (config.contenedores.includes(carpeta)) return true;
  try {
    sh('git', 'cat-file', '-e', `${ANTES}:${carpeta.slice(0, -1)}`);
    return true;
  } catch {
    return false;
  }
}

const archivos = sh('git', 'diff', '--name-only', '--no-renames', ANTES, DESPUES).split('\n').filter(Boolean);
const nuevas = new Set();
const existentes = new Map();
for (const a of archivos) {
  const carpeta = carpetaDe(a);
  if (existiaAntes(carpeta)) {
    if (!existentes.has(carpeta)) existentes.set(carpeta, []);
    existentes.get(carpeta).push(a);
  } else nuevas.add(carpeta);
}

const crearEtiqueta = (nombre, color, descripcion) => {
  try {
    gh('label', 'create', nombre, '-R', REPO, '--color', color, '--description', descripcion);
  } catch {}
};
const enlaceCommits = `https://github.com/${REPO}/compare/${ANTES.slice(0, 12)}...${DESPUES.slice(0, 12)}`;

if (!existentes.size) {
  const lista = [...nuevas].map((c) => `- \`${c}\``).join('\n');
  console.log(`Publicación directa de carpetas nuevas por ${QUIEN}:\n${lista}`);
  crearEtiqueta(ETIQUETA_OK, '007e47', 'Carpeta nueva subida directo a main, permitido por el arnés');
  const url = gh(
    'issue', 'create', '-R', REPO, '--label', ETIQUETA_OK,
    '--title', `Publicación directa: ${[...nuevas].join(', ')}`,
    '--body', `Carpetas nuevas subidas directo a \`main\` por @${QUIEN}. Permitido por el arnés: no existían.\n\n${lista}\n\nCambios: ${enlaceCommits}`
  );
  gh('issue', 'close', url, '-R', REPO, '--reason', 'completed');
  process.exit(0);
}

// Tocó algo que ya existía: revertir el push completo y volver a publicar.
sh('git', 'config', 'user.name', 'Arnés de Medios Digitales');
sh('git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com');
let revertido = false;
try {
  sh('git', 'fetch', 'origin', 'main');
  if (sh('git', 'rev-parse', 'origin/main') !== DESPUES) throw new Error('main avanzó desde este push');
  sh('git', 'revert', '--no-edit', '--no-commit', `${ANTES}..${DESPUES}`);
  sh('git', 'commit', '-m', `Arnés: revertir cambios directos a carpetas existentes (${QUIEN})`);
  sh('git', 'push', 'origin', 'HEAD:main');
  revertido = true;
} catch (e) {
  console.log('No se pudo revertir automáticamente:', e.message);
}

// Los commits hechos con el token del workflow no disparan otros workflows:
// la publicación se lanza a mano si el repo tiene una.
if (revertido) {
  for (const flujo of ['publicar.yml']) {
    try {
      gh('workflow', 'run', flujo, '-R', REPO, '--ref', 'main');
      console.log(`Publicación relanzada (${flujo}).`);
    } catch {}
  }
}

const detalle = [...existentes]
  .map(([c, a]) => `- \`${c}\`: ${a.map((x) => `\`${x}\``).join(', ')}`)
  .join('\n');
crearEtiqueta(ETIQUETA_MAL, 'e63329', 'Cambio directo a carpetas existentes, revertido por el arnés');
gh(
  'issue', 'create', '-R', REPO, '--label', ETIQUETA_MAL,
  '--title', `Cambio directo a carpetas existentes (${QUIEN})`,
  '--body', [
    `@${QUIEN} subió directo a \`main\` cambios en carpetas que ya existían:`,
    '',
    detalle,
    '',
    revertido
      ? 'El arnés **revirtió** esos commits y volvió a publicar el sitio como estaba.'
      : '**No se pudo revertir automáticamente** (main avanzó o hubo un conflicto). Hay que revisarlo a mano.',
    '',
    'Las carpetas existentes se cambian por pull request, con aprobación de su responsable. Para rehacer el cambio: crear una rama desde `main`, aplicar el cambio y abrir el pull request.',
    '',
    `Cambios originales: ${enlaceCommits}`,
  ].join('\n')
);
process.exit(revertido ? 1 : 2);
