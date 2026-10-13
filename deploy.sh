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
URLS_A_VERIFICAR=("https://jersdev.com/" "https://jersdev.com/en/" "https://jersdev.com/pt/" "https://jersdev.com/admin/login/")

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

    log "1/8 Bajando código de GitHub"
    git fetch --quiet origin main
    # reset --hard: el server queda idéntico a GitHub. Cualquier edición a mano se descarta.
    git reset --hard origin/main
    log "    Ahora en: $(git log --oneline -1)"

    rollback() {
        log "ROLLBACK: volviendo a $commitanterior"
        git reset --hard "$commitanterior"
        pip install --quiet -r requirements.txt
        sudo systemctl restart gunicorn celery
        log "Código restaurado. Ojo: si una migración nueva ya se aplicó, la base NO vuelve atrás sola."
        exit 1
    }
    trap rollback ERR

    log "2/8 Instalando requirements"
    pip install --quiet -r requirements.txt

    log "3/8 Chequeando settings y .env"
    python manage.py check --deploy --fail-level ERROR

    log "4/8 Migraciones"
    python manage.py migrate --noinput

    log "5/8 Compilando traducciones del texto fijo (.po -> .mo, necesita gettext en el server)"
    python manage.py compilemessages --ignore=venv

    log "6/8 Traduciendo el contenido nuevo de la base (DeepL)"
    # Solo completa lo que falte (no gasta cupo en lo ya traducido). Si DeepL no responde, avisa y sigue: esos textos se ven en español hasta el próximo deploy.
    python manage.py traducircontenido || log "AVISO: no se pudo traducir todo el contenido (el sitio anda igual, se reintenta en el próximo deploy)"

    log "7/8 Subiendo estáticos a S3"
    python manage.py collectstatic --noinput

    log "8/8 Reiniciando gunicorn y celery y verificando"
    sudo systemctl restart gunicorn celery
    sleep 3
    verificarSitio
    # Si redis o celery no están corriendo, el form de contacto no manda emails: dispara el rollback
    systemctl is-active --quiet redis-server
    systemctl is-active --quiet celery
    log "OK: redis y celery corriendo"

    trap - ERR

    # Recién con el sitio verificado: gunicorn ya usa el manifest nuevo, así que las versiones viejas no las pide nadie.
    # Si la limpieza falla, solo avisa (no hace rollback): el sitio ya está andando.
    log "Limpiando estáticos viejos de S3 (versiones anteriores y archivos que ya no están en el código)"
    python manage.py limpiarestaticos || log "AVISO: no se pudieron limpiar los estáticos viejos (el sitio anda igual)"

    log "Deploy terminado: $(git log --oneline -1)"
}

# Todo adentro de main(): bash lee la función entera antes de ejecutarla,
# así que el git reset de arriba no puede romper el script a la mitad.
main "$@"
exit 0