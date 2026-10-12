from django.db.models import Prefetch
from django.shortcuts import render
from .models import AboutMeContent, AboutMeStat, AboutMeImage, Project, ProjectCategory, ProjectImage, Skill

def home(request):
    aboutmecontent = AboutMeContent.load()
    aboutmestats = AboutMeStat.objects.all()
    aboutmeimages = AboutMeImage.objects.all()
    projectimages = ProjectImage.objects.exclude(file__isnull=True).exclude(file='') # Una fila sin archivo no se muestra (si no, media.file.url tira 500)
    projects = Project.objects.select_related('category').prefetch_related(Prefetch('images', queryset=projectimages), 'tags', 'links')
    projectcategories = ProjectCategory.objects.all()
    skills = Skill.objects.select_related('level')
    return render(request, "base.html", {'aboutmecontent': aboutmecontent, 'aboutmestats': aboutmestats, 'aboutmeimages': aboutmeimages, 'projects': projects, 'projectcategories': projectcategories, 'skills': skills})

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