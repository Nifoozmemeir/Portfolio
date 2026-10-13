"""
Completa con DeepL las traducciones que falten en el contenido de la base (los campos de translation.py).

  - Fila nunca traducida (inglés y portugués vacíos): DeepL detecta en qué idioma está, porque el contenido
    viejo está mezclado. Si estaba en inglés, lo pasa a español y deja el original como inglés.
  - Fila con alguna traducción vacía (ej: DeepL no respondió al guardar): completa solo esa.
  - Lo que ya está traducido no se toca ni gasta cupo: se puede correr las veces que sea.

Lo corre deploy.sh en cada deploy (si falla, solo avisa). También se puede correr a mano:

    python manage.py traducircontenido
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from modeltranslation.translator import translator

from Base.Core.traduccion import ErrorDeTraduccion, entraEnCampo, esTraducible, idiomaOrigen, idiomasDestino, traducir, traducirDetectando, usoDeepL

# El contenido viejo está en español o en inglés. Si DeepL detecta otro idioma (pasa con textos cortos o nombres
# propios), se trata como español.
IDIOMAS_DEL_CONTENIDO_VIEJO = ('en',)


class Command(BaseCommand):
    help = 'Traduce con DeepL el contenido de la base que todavía no tiene inglés o portugués'

    def handle(self, *args, **options):
        # Los campos _es recién creados por la migración arrancan vacíos: se copian del campo original
        call_command('update_translation_fields', verbosity=0)

        origen = idiomaOrigen()
        traducidos, detectados, nocaben = 0, [], []

        def guardable(model, obj, nombre, traduccion, respaldo):
            """Si la traducción no entra en el campo, queda el respaldo (el texto sin traducir): se ve igual que hoy y no se reintenta en cada deploy."""
            if entraEnCampo(model, nombre, traduccion):
                return traduccion
            nocaben.append(f'{model.__name__} #{obj.pk} {nombre}: "{traduccion}" ({len(traduccion)} caracteres, máximo {model._meta.get_field(nombre).max_length})')
            return respaldo

        try:
            for model in translator.get_registered_models(abstract=False):
                campos = translator.get_options_for_model(model).fields
                for obj in model._default_manager.all():
                    if not esTraducible(obj):
                        continue
                    cambios = {}
                    for campo in campos:
                        espanol = getattr(obj, f'{campo}_{origen}') or ''
                        faltan = [idioma for idioma in idiomasDestino() if not getattr(obj, f'{campo}_{idioma}')]
                        if not espanol.strip() or not faltan:
                            continue
                        if len(faltan) == len(idiomasDestino()): # Nunca se tradujo: puede estar en otro idioma
                            primero = faltan.pop(0)
                            idioma, traduccion = traducirDetectando(espanol, primero) # La detección viene con la traducción, sin costo extra
                            if idioma != origen and idioma not in IDIOMAS_DEL_CONTENIDO_VIEJO:
                                idioma, traduccion = origen, traducir(espanol, primero) # Mal detectado (ej: portugués): se traduce desde el español
                            if idioma in IDIOMAS_DEL_CONTENIDO_VIEJO:
                                original = espanol
                                espanol = guardable(model, obj, f'{campo}_{origen}', traducir(original, origen, origen=idioma), original)
                                cambios[f'{campo}_{origen}'] = espanol
                                cambios[f'{campo}_{idioma}'] = original
                                detectados.append(f'{model.__name__} #{obj.pk} {campo} ({idioma}): "{original}" -> "{espanol}"')
                            else:
                                cambios[f'{campo}_{primero}'] = guardable(model, obj, f'{campo}_{primero}', traduccion, espanol)
                        for idioma in faltan:
                            if f'{campo}_{idioma}' not in cambios:
                                cambios[f'{campo}_{idioma}'] = guardable(model, obj, f'{campo}_{idioma}', traducir(espanol, idioma), espanol)
                    if cambios:
                        # update() y no save(): así no se vuelve a disparar la traducción al guardar
                        model._default_manager.filter(pk=obj.pk).rewrite(False).update(**cambios)
                        traducidos += 1
        except ErrorDeTraduccion as error:
            raise CommandError(f'{error}. Se guardaron {traducidos} filas; el resto se completa en la próxima corrida.')
        finally:
            if detectados:
                self.stdout.write(self.style.WARNING('Textos que estaban en inglés y se pasaron a español (revisalos en el admin):'))
                for linea in detectados:
                    self.stdout.write(f'  {linea}')
            if nocaben:
                self.stdout.write(self.style.WARNING('Traducciones que no entran en el campo (quedaron sin traducir: acortá el español o agrandá el max_length):'))
                for linea in nocaben:
                    self.stdout.write(f'  {linea}')

        usados, limite = usoDeepL()
        self.stdout.write(self.style.SUCCESS(f'{traducidos} filas traducidas. Cupo de DeepL: {usados:,} de {limite:,} caracteres usados este mes.'))
