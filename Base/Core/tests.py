"""
Tests de humo del Portfolio.

No prueban lógica puntual de cada vista: responden una sola pregunta,
"¿esto levanta sin tirar 500?". Son genéricos a propósito: recorren solos
todas las URLs públicas y todas las pantallas del admin, así que cuando
agregás una sección o un model nuevo quedan cubiertos sin escribir nada.

Corren con la base VACÍA: si una vista o un template asume que siempre
hay contenido cargado, el test lo detecta antes que un visitante.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import URLPattern, URLResolver, get_resolver, reverse


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


def UrlsPublicas(resolver=None, prefijo=''):
    """Devuelve todas las URLs sin parámetros, salteando el admin."""
    resolver = resolver or get_resolver()
    for patron in resolver.url_patterns:
        ruta = str(patron.pattern)
        if isinstance(patron, URLResolver):
            if ruta.startswith('admin'):
                continue
            yield from UrlsPublicas(patron, prefijo + ruta)
        elif isinstance(patron, URLPattern) and patron.pattern.regex.groups == 0:
            yield '/' + prefijo + ruta.lstrip('^').rstrip('$')


class SmokePublicoTest(TestCase):

    def test_hay_urls_para_probar(self):
        self.assertTrue(list(UrlsPublicas()), "No se encontró ninguna URL pública, algo está muy mal")

    def test_ninguna_pagina_publica_tira_500(self):
        # raise_request_exception=False: si la vista explota, devuelve un 500 en vez de cortar el test
        cliente = Client(raise_request_exception=False)
        for url in UrlsPublicas():
            with self.subTest(url=url):
                # secure=True: en producción SECURE_SSL_REDIRECT manda todo a HTTPS
                respuesta = cliente.get(url, secure=True, follow=True)
                if respuesta.status_code >= 500 and url in URLS_VIEJAS:
                    # Formato que GitHub Actions muestra como warning amarillo
                    print(f"::warning title=URL vieja rota::{url} devuelve {respuesta.status_code} (está en URLS_VIEJAS, no corta el pipeline)")
                    continue
                self.assertLess(respuesta.status_code, 500, f"{url} devolvió {respuesta.status_code}")

    def test_login_del_admin_levanta(self):
        respuesta = self.client.get(reverse('admin:login'), secure=True)
        self.assertEqual(respuesta.status_code, 200)


class SmokeAdminTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.Superusuario = get_user_model().objects.create_superuser('smoke', 'smoke@test.com', 'smoke-pass-123')

    def setUp(self):
        self.client.force_login(self.Superusuario)

    def test_home_del_admin(self):
        respuesta = self.client.get(reverse('admin:index'), secure=True)
        self.assertEqual(respuesta.status_code, 200)

    def test_listado_y_alta_de_cada_model_registrado(self):
        for model in admin.site._registry:
            app = model._meta.app_label
            nombre = model._meta.model_name
            for vista in ('changelist', 'add'):
                url = reverse(f'admin:{app}_{nombre}_{vista}')
                with self.subTest(model=nombre, vista=vista):
                    respuesta = self.client.get(url, secure=True, follow=True)
                    self.assertLess(respuesta.status_code, 500, f"{url} devolvió {respuesta.status_code}")