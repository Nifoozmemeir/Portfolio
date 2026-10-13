"""
Traducción automática con DeepL (plan Free): el contenido se carga SOLO en español y el inglés y el portugués se completan solos.

- Al guardar un model en el admin (traducirAlGuardar, conectado en apps.py): se traducen SOLO los campos
  cuyo español cambió o cuya traducción está vacía. Lo que no cambió no se toca ni gasta cupo (y respeta correcciones a mano).
- Si DeepL no responde o se acabó el cupo del mes, el guardado anda igual: la traducción queda vacía
  (en la página se ve el español) y la completa `traducircontenido` en el próximo deploy.
- El plan Free no cobra nunca: si se pasa del cupo del mes, DeepL deja de traducir hasta el mes siguiente.

La key va en el .env (DEEPL_API_KEY). Sin key no se traduce nada y se ve el español.

El texto fijo de los templates ({% translate '...' %}) va en resources/locale/<idioma>/LC_MESSAGES/django.po:
lo completa `traducirtextos` y lo controlan los tests. Para eso no hace falta gettext (solo para compilar el .mo).
"""
import ast
import logging
import re
from pathlib import Path

import requests
from django.conf import settings
from modeltranslation.translator import translator

logger = logging.getLogger(__name__)

DEEPL_URL_FREE = 'https://api-free.deepl.com/v2' # Las keys del plan Free terminan en ":fx"
DEEPL_URL_PRO = 'https://api.deepl.com/v2'
DEEPL_IDIOMAS = {'es': 'ES', 'en': 'EN-GB', 'pt': 'PT-PT'} # Código de LANGUAGES -> código de DeepL (inglés británico y portugués de Portugal, como las banderas)
TIMEOUT = 20 # Segundos por pedido
TRANSLATE_PATTERN = re.compile(r"""{%\s*translate\s+(["'])(.+?)\1""") # Las frases de {% translate '...' %} en los templates


class ErrorDeTraduccion(Exception):
    pass


def idiomaOrigen():
    return settings.LANGUAGE_CODE


def idiomasDestino():
    return [codigo for codigo, _ in settings.LANGUAGES if codigo != idiomaOrigen()]


def pedirDeepL(metodo, ruta, **kwargs):
    key = getattr(settings, 'DEEPL_API_KEY', '')
    if not key:
        raise ErrorDeTraduccion('No hay DEEPL_API_KEY en el .env')
    url = (DEEPL_URL_FREE if key.endswith(':fx') else DEEPL_URL_PRO) + ruta
    try:
        respuesta = requests.request(metodo, url, headers={'Authorization': f'DeepL-Auth-Key {key}'}, timeout=TIMEOUT, **kwargs)
    except requests.RequestException as error:
        raise ErrorDeTraduccion(f'DeepL no respondió: {error}')
    if respuesta.status_code == 456:
        raise ErrorDeTraduccion('Se terminó el cupo del mes de DeepL (vuelve el mes que viene)')
    if respuesta.status_code == 403:
        raise ErrorDeTraduccion('DeepL rechazó la key (revisar DEEPL_API_KEY en el .env)')
    if respuesta.status_code != 200:
        raise ErrorDeTraduccion(f'DeepL respondió {respuesta.status_code}: {respuesta.text[:200]}')
    return respuesta.json()


def traducirDetectando(texto, destino, origen=None):
    """Traduce el texto y devuelve (idioma detectado, traducción). Sin origen, DeepL detecta el idioma (sin costo extra)."""
    datos = {'text': [texto], 'target_lang': DEEPL_IDIOMAS[destino]}
    if origen:
        datos['source_lang'] = DEEPL_IDIOMAS[origen].split('-')[0]
    if destino != idiomaOrigen():
        datos['formality'] = 'prefer_more' # Formal donde el idioma lo permite (ej: portugués); al español no, porque el sitio va en voseo
    traduccion = pedirDeepL('POST', '/translate', json=datos)['translations'][0]
    return traduccion['detected_source_language'].lower(), traduccion['text'].strip()


def traducir(texto, destino, origen=None):
    """Traduce el texto (por default desde el español). Lanza ErrorDeTraduccion si DeepL falla (caído, sin cupo, sin key)."""
    return traducirDetectando(texto, destino, origen or idiomaOrigen())[1]


def usoDeepL():
    """Devuelve (caracteres usados este mes, límite del mes). Consultarlo no gasta cupo."""
    uso = pedirDeepL('GET', '/usage')
    return uso['character_count'], uso['character_limit']


def textosDeLosTemplates():
    """Las frases de todos los {% translate '...' %} de resources/templates, sin repetir y en orden de aparición."""
    textos = []
    for carpeta in settings.TEMPLATES[0]['DIRS']:
        for ruta in sorted(Path(carpeta).rglob('*.html')):
            for _, texto in TRANSLATE_PATTERN.findall(ruta.read_text(encoding='utf-8')):
                if texto not in textos:
                    textos.append(texto)
    return textos


def rutaPo(idioma):
    return Path(settings.LOCALE_PATHS[0]) / idioma / 'LC_MESSAGES' / 'django.po'


def leerPo(ruta):
    """Devuelve {frase en español: traducción} de un .po (sin el encabezado ni las entradas obsoletas)."""
    entradas, msgid, msgstr, clave = {}, None, '', None
    if not ruta.exists():
        return entradas
    for linea in ruta.read_text(encoding='utf-8').splitlines() + ['']:
        linea = linea.strip()
        if linea.startswith('msgid '):
            msgid, msgstr, clave = ast.literal_eval(linea[6:]), '', 'msgid'
        elif linea.startswith('msgstr '):
            msgstr, clave = ast.literal_eval(linea[7:]), 'msgstr'
        elif linea.startswith('"') and clave == 'msgid':
            msgid += ast.literal_eval(linea)
        elif linea.startswith('"') and clave == 'msgstr':
            msgstr += ast.literal_eval(linea)
        elif not linea and msgid: # Línea en blanco: termina la entrada
            entradas[msgid] = msgstr
            msgid, clave = None, None
    return entradas


def escribirPo(ruta, idioma, entradas):
    """Escribe el .po con las entradas [(frase en español, traducción)] en el formato que espera compilemessages."""
    escapar = lambda texto: texto.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    nombre = dict(settings.LANGUAGES)[idioma]
    lineas = [
        f'# Texto fijo de los templates en {nombre}.',
        '# Lo completa `py manage.py traducirtextos` (traduce con DeepL las frases nuevas y saca las que ya no se usan).',
        '# Cualquier msgstr se puede corregir a mano: traducirtextos no pisa lo que ya está traducido.',
        'msgid ""',
        'msgstr ""',
        '"Project-Id-Version: Portfolio\\n"',
        f'"Language: {idioma}\\n"',
        '"MIME-Version: 1.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"',
        '',
    ]
    for msgid, msgstr in entradas:
        lineas += [f'msgid "{escapar(msgid)}"', f'msgstr "{escapar(msgstr)}"', '']
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text('\n'.join(lineas), encoding='utf-8', newline='\n')


def entraEnCampo(model, nombre, texto):
    """La traducción puede salir más larga que el español: si pasa el max_length del campo, la base la rechazaría."""
    largo = model._meta.get_field(nombre).max_length
    return largo is None or len(texto) <= largo


def esTraducible(instance):
    """Un model puede definir la property esTraducible para que algunas filas no se traduzcan (ej: ExperienceSkill de tecnologías)."""
    return getattr(instance, 'esTraducible', True)


def traducirAlGuardar(sender, instance, raw=False, **kwargs):
    """pre_save de los models registrados en translation.py: completa el inglés y el portugués a partir del español."""
    if raw: # loaddata: los datos ya vienen completos
        return
    campos = translator.get_options_for_model(sender).fields
    anterior = sender._default_manager.filter(pk=instance.pk).first() if instance.pk else None
    traducible = esTraducible(instance)
    sinservicio = False # Si DeepL falla una vez, no se le sigue pidiendo en este guardado (así no tarda de más)
    for campo in campos:
        espanol = getattr(instance, f'{campo}_{idiomaOrigen()}') or ''
        cambio = anterior is None or espanol != (getattr(anterior, f'{campo}_{idiomaOrigen()}') or '')
        for idioma in idiomasDestino():
            nombre = f'{campo}_{idioma}'
            if not traducible or not espanol.strip():
                if cambio:
                    setattr(instance, nombre, '') # Vacío = en la página se ve el español
                continue
            if not cambio and getattr(instance, nombre):
                continue # El español no cambió y ya tiene traducción: no se toca (no gasta cupo)
            if sinservicio:
                setattr(instance, nombre, '')
                continue
            try:
                traduccion = traducir(espanol, idioma)
                if not entraEnCampo(sender, nombre, traduccion):
                    # Queda el español (no vacío): así traducircontenido no la reintenta en cada deploy gastando cupo
                    logger.warning('La traducción de %s.%s a %s no entra en el campo (%s caracteres): queda en español', sender.__name__, campo, idioma, len(traduccion))
                    traduccion = espanol
                setattr(instance, nombre, traduccion)
            except ErrorDeTraduccion as error:
                logger.warning('No se pudo traducir %s.%s a %s: %s', sender.__name__, campo, idioma, error)
                setattr(instance, nombre, '')
                sinservicio = True
