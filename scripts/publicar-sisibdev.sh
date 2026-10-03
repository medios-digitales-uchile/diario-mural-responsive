#!/bin/sh
# Copia la herramienta al repositorio sisibdev, que publica sisibdev.uchile.cl en
# Cloudflare Pages con cada push a main:
#
#   herramienta/  ->  sisibdev/diario-mural/   (https://sisibdev.uchile.cl/diario-mural/)
#
# El build de sisibdev la copia a su dist con `cp -r diario-mural dist/diario-mural`.
# Este script no hace commit ni push: eso se revisa y se hace a mano en sisibdev.
set -eu
AQUI=$(cd "$(dirname "$0")/.." && pwd)
SISIBDEV=${SISIBDEV:-$HOME/Sites/active/sisibdev}
rm -rf "$SISIBDEV/diario-mural"
cp -R "$AQUI/herramienta" "$SISIBDEV/diario-mural"
echo "Copiado a $SISIBDEV/diario-mural"
