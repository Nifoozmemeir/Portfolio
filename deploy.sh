#!/usr/bin/env bash
# Deploy de jersdev.com en el server de Lightsail.
#
# Lo corre GitHub Actions por SSH después de que pasan los tests,
# pero también se puede correr a mano desde el server:
#     bash /var/www/Portfolio/deploy.sh
#
# Si el sitio no responde 200 al final, vuelve solo al commit anterior.

set -Eeuo pipefail

APP_DIR=/var/www/Portfolio
URLS_A_VERIFICAR=("https://jersdev.com/" "https://jersdev.com/admin/login/")

log() { echo "[$(date '+%H:%M:%S')] $*"; }

verificarSitio() {
    for url in "${URLS_A_VERIFICAR[@]}"; do
        local codigo=""
        for intento in 1 2 3 4 5; do
            codigo=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url" || true)
            [ "$codigo" = "200" ] && break
            sleep 3
        done
        if [ "$codigo" != "200" ]; then
            log "ERROR: $url respondió $codigo"
            return 1
        fi
        log "OK: $url respondió 200"
    done
}

main() {
    cd "$APP_DIR"
    # shellcheck disable=SC1091
    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=Base.settingsproduction

    local commitanterior
    commitanterior=$(git rev-parse HEAD)
    log "Commit actual: $(git log --oneline -1)"

    log "1/6 Bajando código de GitHub"
    git fetch --quiet origin main
    # reset --hard: el server queda idéntico a GitHub. Cualquier edición a mano se descarta.
    git reset --hard origin/main
    log "    Ahora en: $(git log --oneline -1)"

    rollback() {
        log "ROLLBACK: volviendo a $commitanterior"
        git reset --hard "$commitanterior"
        pip install --quiet -r requirements.txt
        sudo systemctl restart gunicorn
        log "Código restaurado. Ojo: si una migración nueva ya se aplicó, la base NO vuelve atrás sola."
        exit 1
    }
    trap rollback ERR

    log "2/6 Instalando requirements"
    pip install --quiet -r requirements.txt

    log "3/6 Chequeando settings y .env"
    python manage.py check --deploy --fail-level ERROR

    log "4/6 Migraciones"
    python manage.py migrate --noinput

    log "5/6 Subiendo estáticos a S3"
    python manage.py collectstatic --noinput

    log "6/6 Reiniciando gunicorn y verificando"
    sudo systemctl restart gunicorn
    sleep 3
    verificarSitio

    trap - ERR
    log "Deploy terminado: $(git log --oneline -1)"
}

# Todo adentro de main(): bash lee la función entera antes de ejecutarla,
# así que el git reset de arriba no puede romper el script a la mitad.
main "$@"
exit 0