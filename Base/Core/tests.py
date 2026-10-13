"""
Tests de humo del Portfolio.

No prueban lógica puntual de cada vista: responden una sola pregunta,
"¿esto levanta sin tirar 500?". Son genéricos a propósito: recorren solos
todas las URLs públicas y todas las pantallas del admin, así que cuando
agregás una sección o un model nuevo quedan cubiertos sin escribir nada.

Corren con la base VACÍA: si una vista o un template asume que siempre
hay contenido cargado, el test lo detecta antes que un visitante.
"""
import io
import json
import os
import tempfile

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.template.loader import get_template
from django.test import Client, TestCase, override_settings
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from django.utils import translation

from Base.Core.traduccion import idiomasDestino, leerPo, rutaPo, textosDeLosTemplates


# URLs viejas que se van con el revamp (paso 3). Si tiran 500 NO cortan el pipeline:
# aparecen como warning amarillo en GitHub Actions y el deploy sigue.
# Cuando termines el revamp, vaciá esta lista y quedan todas obligatorias.
URLS_VIEJAS = [
    '/portfolio',
    '/about-me',
    '/space-commander-seu',
    '/gems-crawler',
    '/final-project',
]

# Estáticos sin versionar para los tests comunes: con estáticos versionados (manifest),
# {% static %} necesita que antes se haya corrido collectstatic. Eso lo prueba aparte SmokeEstaticosTest.
STORAGES_SIN_MANIFEST = {**settings.STORAGES, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}}
STORAGES_CON_MANIFEST = {**settings.STORAGES, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'}}


def urlsPublicas(resolver=None, prefijo=''):
    """Devuelve todas las URLs sin parámetros, salteando el admin."""
    resolver = resolver or get_resolver()
    for patron in resolver.url_patterns:
        ruta = str(patron.pattern)
        if isinstance(patron, URLResolver):
            if ruta.startswith('admin'):
                continue
            yield from urlsPublicas(patron, prefijo + ruta)
        elif isinstance(patron, URLPattern) and patron.pattern.regex.groups == 0:
            yield '/' + prefijo + ruta.lstrip('^').rstrip('$')


def chequearUrlsPublicas(test):
    """Pide todas las URLs públicas y falla si alguna tira 500 (las de URLS_VIEJAS solo avisan)."""
    # raise_request_exception=False: si la vista explota, devuelve un 500 en vez de cortar el test
    cliente = Client(raise_request_exception=False)
    for url in urlsPublicas():
        with test.subTest(url=url):
            # secure=True: en producción SECURE_SSL_REDIRECT manda todo a HTTPS
            respuesta = cliente.get(url, secure=True, follow=True)
            if respuesta.status_code >= 500 and url in URLS_VIEJAS:
                # Formato que GitHub Actions muestra como warning amarillo
                print(f"::warning title=URL vieja rota::{url} devuelve {respuesta.status_code} (está en URLS_VIEJAS, no corta el pipeline)")
                continue
            test.assertLess(respuesta.status_code, 500, f"{url} devolvió {respuesta.status_code}")


@override_settings(STORAGES=STORAGES_SIN_MANIFEST)
class SmokePublicoTest(TestCase):

    def testHayUrlsParaProbar(self):
        self.assertTrue(list(urlsPublicas()), "No se encontró ninguna URL pública, algo está muy mal")

    def testNingunaPaginaPublicaTira500(self):
        chequearUrlsPublicas(self)

    def testLoginDelAdminLevanta(self):
        respuesta = self.client.get(reverse('admin:login'), secure=True)
        self.assertEqual(respuesta.status_code, 200)


@override_settings(STORAGES=STORAGES_SIN_MANIFEST)
class SmokeAdminTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.superusuario = get_user_model().objects.create_superuser('smoke', 'smoke@test.com', 'smoke-pass-123')

    def setUp(self):
        self.client.force_login(self.superusuario)

    def testHomeDelAdmin(self):
        respuesta = self.client.get(reverse('admin:index'), secure=True)
        self.assertEqual(respuesta.status_code, 200)

    def testTemplatesDeLosFiltrosExisten(self):
        # Con la base vacía los filtros no se dibujan, así que el test del listado no
        # detecta un template faltante (ej: el paquete del filtro fuera de INSTALLED_APPS).
        # Acá se carga el template de cada filtro de cada admin directamente.
        for model, modeladmin in admin.site._registry.items():
            for filtro in modeladmin.list_filter:
                clase = filtro[1] if isinstance(filtro, (tuple, list)) else filtro
                if isinstance(clase, str):
                    continue  # Solo el nombre del campo: usa el filtro default de Django
                with self.subTest(model=model._meta.model_name, filtro=clase.__name__):
                    get_template(clase.template)

    def testListadoYAltaDeCadaModelRegistrado(self):
        for model in admin.site._registry:
            app = model._meta.app_label
            nombre = model._meta.model_name
            for vista in ('changelist', 'add'):
                url = reverse(f'admin:{app}_{nombre}_{vista}')
                with self.subTest(model=nombre, vista=vista):
                    respuesta = self.client.get(url, secure=True, follow=True)
                    self.assertLess(respuesta.status_code, 500, f"{url} devolvió {respuesta.status_code}")


@override_settings(STORAGES=STORAGES_SIN_MANIFEST)
class SmokeIdiomasTest(TestCase):
    """
    El sitio en cada idioma de LANGUAGES (/, /en/, /pt/): que levante con la base vacía y que
    el texto fijo de los templates ({% translate %}) esté traducido y compilado.
    """

    def testHomeEnCadaIdioma(self):
        cliente = Client(raise_request_exception=False)
        for codigo, _ in settings.LANGUAGES:
            with translation.override(codigo):
                url = reverse('home')
            with self.subTest(url=url):
                respuesta = cliente.get(url, secure=True)
                self.assertEqual(respuesta.status_code, 200, f"{url} devolvió {respuesta.status_code}")
                self.assertContains(respuesta, f'<html lang="{codigo}">')

    def testTextoFijoTraducidoEnLosPo(self):
        # Si se agrega o cambia un {% translate %} y no se corre `py manage.py traducirtextos`, falla acá (y no hay deploy)
        textos = textosDeLosTemplates()
        self.assertTrue(textos, "No se encontró ningún {% translate %} en los templates")
        for idioma in idiomasDestino():
            with self.subTest(idioma=idioma):
                traducciones = leerPo(rutaPo(idioma))
                faltan = [texto for texto in textos if not traducciones.get(texto)]
                self.assertFalse(faltan, f"Sin traducir en {rutaPo(idioma)} (correr py manage.py traducirtextos): {faltan}")

    def testTraduccionesCompiladas(self):
        # El .mo lo genera compilemessages en el CI y en el deploy. En una PC sin gettext no existe y se saltea.
        textos = textosDeLosTemplates()
        for idioma in idiomasDestino():
            with self.subTest(idioma=idioma):
                rutamo = rutaPo(idioma).with_suffix('.mo')
                if not rutamo.exists():
                    if os.environ.get('CI'):
                        self.fail(f"No existe {rutamo}: falta correr compilemessages antes de los tests")
                    self.skipTest(f"No existe {rutamo} (sin gettext en esta PC; en el CI se compila)")
                traducciones = leerPo(rutaPo(idioma))
                with translation.override(idioma):
                    distintas = [texto for texto in textos if translation.gettext(texto) != traducciones.get(texto)]
                self.assertFalse(distintas, f"El .mo de {idioma} no coincide con el .po (¿compilemessages viejo?): {distintas}")


class SmokeEstaticosTest(TestCase):
    """
    Simula lo que pasa en producción con los estáticos versionados (base.3f2a91c.js):
    corre un collectstatic real en una carpeta temporal y después pide las páginas.
    Detecta antes del deploy:
      - un url(...) de un CSS que apunta a un archivo que no existe (collectstatic falla)
      - un {% static '...' %} de un template que apunta a un archivo que no existe (la página tira 500)
    """

    def testCollectstaticYPaginasConEstaticosVersionados(self):
        with tempfile.TemporaryDirectory() as carpeta, self.settings(STATIC_ROOT=carpeta, STORAGES=STORAGES_CON_MANIFEST):
            try:
                call_command('collectstatic', interactive=False, verbosity=0)
            except Exception as error:
                self.fail(f"collectstatic falla (en el deploy fallaría igual): {error}")
            chequearUrlsPublicas(self)
            respuesta = Client(raise_request_exception=False).get(reverse('admin:login'), secure=True)
            self.assertEqual(respuesta.status_code, 200, "El login del admin no levanta con estáticos versionados")

    def testLimpiarEstaticosBorraSoloLoQueNoSeUsa(self):
        # limpiarestaticos borra archivos en producción (deploy.sh): tiene que borrar lo viejo y NUNCA algo en uso
        with tempfile.TemporaryDirectory() as carpeta, self.settings(STATIC_ROOT=carpeta, STORAGES=STORAGES_CON_MANIFEST):
            call_command('collectstatic', interactive=False, verbosity=0)
            # Basura de deploys anteriores: una versión vieja con hash y un archivo que se sacó del código
            viejos = [os.path.join(carpeta, 'css', 'base.aaaaaaaaaaaa.css'), os.path.join(carpeta, 'img', 'viejo.gif')]
            for ruta in viejos:
                os.makedirs(os.path.dirname(ruta), exist_ok=True)
                open(ruta, 'w').close()

            call_command('limpiarestaticos', stdout=io.StringIO())

            for ruta in viejos:
                self.assertFalse(os.path.exists(ruta), f"No borró el archivo viejo {ruta}")
            with open(os.path.join(carpeta, 'staticfiles.json'), encoding='utf-8') as manifest:
                usados = json.load(manifest)['paths']
            for original, versionado in usados.items():
                for nombre in (original, versionado):
                    with self.subTest(archivo=nombre):
                        self.assertTrue(os.path.exists(os.path.join(carpeta, nombre)), f"Borró {nombre}, que está en uso")
            chequearUrlsPublicas(self)