"""
Borra de los estáticos todo lo que ya no se usa: versiones viejas con hash (base.<hash viejo>.css)
y archivos que se sacaron del código. Se queda SOLO con lo que figura en el manifest (staticfiles.json).

Lo corre deploy.sh después de collectstatic y de verificar que el sitio responde.

    python manage.py limpiarestaticos            # borra
    python manage.py limpiarestaticos --dry-run  # solo lista lo que borraría
"""
from django.contrib.staticfiles.storage import ManifestFilesMixin, staticfiles_storage
from django.core.management.base import BaseCommand, CommandError


def listarArchivos(storage, carpeta=''):
    """Devuelve todos los archivos del storage, recorriendo las subcarpetas."""
    carpetas, archivos = storage.listdir(carpeta)
    for archivo in archivos:
        yield f'{carpeta}/{archivo}' if carpeta else archivo
    for subcarpeta in carpetas:
        yield from listarArchivos(storage, f'{carpeta}/{subcarpeta}' if carpeta else subcarpeta)


class Command(BaseCommand):
    help = 'Borra de los estáticos las versiones viejas y los archivos que ya no están en el manifest'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Solo lista lo que borraría, no borra nada')

    def handle(self, *args, **options):
        if not isinstance(staticfiles_storage, ManifestFilesMixin):
            raise CommandError('Los estáticos no están versionados (sin manifest): no hay nada que limpiar.')

        usados, _ = staticfiles_storage.load_manifest()
        # Sin manifest no se sabe qué se usa: no se borra nada
        if not usados:
            raise CommandError('No se pudo leer staticfiles.json o está vacío: no se borra nada.')

        aconservar = set(usados) | set(usados.values()) | {staticfiles_storage.manifest_name} # Originales, versiones actuales y el manifest
        aborrar = sorted(nombre for nombre in listarArchivos(staticfiles_storage) if nombre not in aconservar)

        for nombre in aborrar:
            if options['dry_run']:
                self.stdout.write(f'Se borraría: {nombre}')
            else:
                staticfiles_storage.delete(nombre)
                self.stdout.write(f'Borrado: {nombre}')

        accion = 'para borrar' if options['dry_run'] else 'borrados'
        self.stdout.write(self.style.SUCCESS(f'{len(aborrar)} archivos viejos {accion}, {len(aconservar)} en uso.'))
