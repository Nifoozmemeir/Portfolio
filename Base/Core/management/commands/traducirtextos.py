"""
Mantiene al día los .po del texto fijo de los templates (resources/locale/<idioma>/LC_MESSAGES/django.po):
  - frase nueva o cambiada en un {% translate '...' %} -> la traduce con DeepL y la agrega
  - frase que ya no está en ningún template -> la saca
  - frase que ya tiene traducción -> no la toca (respeta las correcciones a mano)

Se corre después de cambiar texto fijo en un template. Si no se corre, los tests fallan y no hay deploy.

    python manage.py traducirtextos
"""
from django.core.management.base import BaseCommand, CommandError

from Base.Core.traduccion import ErrorDeTraduccion, escribirPo, idiomasDestino, leerPo, rutaPo, textosDeLosTemplates, traducir


class Command(BaseCommand):
    help = 'Traduce las frases nuevas de los {% translate %} de los templates y saca de los .po las que ya no se usan'

    def handle(self, *args, **options):
        textos = textosDeLosTemplates()
        if not textos:
            raise CommandError('No se encontró ningún {% translate %} en los templates.')

        sintraducir = 0
        for idioma in idiomasDestino():
            ruta = rutaPo(idioma)
            existentes = leerPo(ruta)
            entradas, nuevas = [], 0
            for texto in textos:
                traduccion = existentes.get(texto, '')
                if not traduccion:
                    try:
                        traduccion = traducir(texto, idioma)
                        nuevas += 1
                        self.stdout.write(f'[{idioma}] {texto} -> {traduccion}')
                    except ErrorDeTraduccion as error:
                        sintraducir += 1
                        self.stderr.write(f'[{idioma}] No se pudo traducir "{texto}": {error}')
                entradas.append((texto, traduccion))
            sacadas = len(set(existentes) - set(textos))
            escribirPo(ruta, idioma, entradas)
            self.stdout.write(self.style.SUCCESS(f'{idioma}: {nuevas} nuevas, {sacadas} sacadas, {len(entradas)} en total.'))

        if sintraducir:
            raise CommandError(f'Quedaron {sintraducir} frases sin traducir (se ven en español). Volvé a correr el comando más tarde.')