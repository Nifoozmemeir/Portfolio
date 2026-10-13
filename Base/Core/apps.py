from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Base.Core'

    def ready(self):
        # Al guardar un model con campos traducibles (translation.py), se completan solos el inglés y el portugués
        from django.db.models.signals import pre_save
        from modeltranslation.translator import translator
        from .traduccion import traducirAlGuardar
        for model in translator.get_registered_models(abstract=False):
            pre_save.connect(traducirAlGuardar, sender=model, dispatch_uid=f'traducirAlGuardar{model.__name__}')
