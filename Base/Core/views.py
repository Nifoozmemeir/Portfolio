import logging
import time
from django.core import signing
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .forms import ContactMessageForm
from .models import AboutMeContent, AboutMeStat, AboutMeImage, Project, ProjectCategory, ProjectImage, Skill, ExperienceCategory, Experience, ExperienceMedia, ExperienceHighlightMedia
from .tasks import enviarEmailContacto

logger = logging.getLogger(__name__)

LIMITE_POR_IP = 3 # Mensajes por hora desde una misma IP
LIMITE_DIARIO = 20 # Mensajes por día en total, de cualquier IP
SEGUNDOS_MINIMOS = 3 # Una persona no completa el form en menos de esto

def crearTokenContacto():
    return signing.dumps(time.time(), salt='contacto')

def esMuyRapido(token):
    try:
        renderizado = signing.loads(token, salt='contacto')
    except signing.BadSignature: # Token inventado o ausente: es un bot
        return True
    return time.time() - renderizado < SEGUNDOS_MINIMOS

def obtenerIp(request):
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '') # X-Real-IP lo pone nginx con la IP real

def superoLimite(clave, limite, segundos):
    try:
        cache.add(clave, 0, segundos) # Crea el contador con vencimiento solo si no existe
        return cache.incr(clave) > limite # incr en Redis es atómico: no se puede saltear con requests simultáneos
    except Exception: # Si Redis está caído no se bloquea a nadie: el mensaje igual se guarda en el admin
        logger.exception("No se pudo chequear el límite %s", clave)
        return False

def home(request):
    aboutmecontent = AboutMeContent.load()
    aboutmestats = AboutMeStat.objects.all()
    aboutmeimages = AboutMeImage.objects.all()
    projectimages = ProjectImage.objects.exclude(file__isnull=True).exclude(file='') # Una fila sin archivo no se muestra (si no, media.file.url tira 500)
    projects = Project.objects.select_related('category').prefetch_related(Prefetch('images', queryset=projectimages), 'tags', 'links')
    projectcategories = ProjectCategory.objects.all()
    skills = Skill.objects.select_related('level')
    experiencemedia = ExperienceMedia.objects.exclude((Q(file__isnull=True) | Q(file='')) & Q(url='')) # Una fila sin archivo ni URL no se muestra (si no, media.file.url tira 500)
    highlightmedia = ExperienceHighlightMedia.objects.exclude((Q(image__isnull=True) | Q(image='')) & Q(url='')) # Igual que experiencemedia: sin imagen ni URL no se muestra
    experiences = Experience.objects.prefetch_related('metrics', Prefetch('highlights__media', queryset=highlightmedia), 'skills', 'links', Prefetch('media', queryset=experiencemedia))
    experiencecategories = ExperienceCategory.objects.prefetch_related(Prefetch('experiences', queryset=experiences))
    return render(request, "base.html", {'aboutmecontent': aboutmecontent, 'aboutmestats': aboutmestats, 'aboutmeimages': aboutmeimages, 'projects': projects, 'projectcategories': projectcategories, 'skills': skills, 'experiencecategories': experiencecategories, 'contacttoken': crearTokenContacto()})

@require_POST
def contact(request):
    form = ContactMessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    if form.cleaned_data['website'] or esMuyRapido(form.cleaned_data['token']): # Bot: se le dice que salió bien y no se hace nada
        return JsonResponse({'ok': True})
    if superoLimite(f"contacto:ip:{obtenerIp(request)}", LIMITE_POR_IP, 3600) or superoLimite("contacto:diario", LIMITE_DIARIO, 86400):
        return JsonResponse({'ok': False}, status=429)
    mensaje = form.save()
    try:
        enviarEmailContacto.delay(mensaje.pk) # Solo el id: la tarea lee el mensaje de la base
    except Exception:
        logger.exception("No se pudo encolar el email del mensaje %s (queda en el admin)", mensaje.pk)
    return JsonResponse({'ok': True})