# Script para limpar imagens Docker não utilizadas
# Uso: bash cleanup.sh

docker image prune -a -f
