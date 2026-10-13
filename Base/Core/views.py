from django.db.models import Prefetch, Q
from django.shortcuts import render
from .models import AboutMeContent, AboutMeStat, AboutMeImage, Project, ProjectCategory, ProjectImage, Skill, ExperienceCategory, Experience, ExperienceMedia, ExperienceHighlightMedia

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
    return render(request, "base.html", {'aboutmecontent': aboutmecontent, 'aboutmestats': aboutmestats, 'aboutmeimages': aboutmeimages, 'projects': projects, 'projectcategories': projectcategories, 'skills': skills, 'experiencecategories': experiencecategories})

def Index(request):
    return render(request, "index.html")

def AboutMe(request):
    return render(request, "about_me.html")

def SpaceCommanderInfo(request):
    return render(request, "space_commander_seu.html")

def GemsCrawlerInfo(request):
    return render(request, "gems_crawler.html")

def FinalProjectInfo(request):
    return render(request, "final_project.html")