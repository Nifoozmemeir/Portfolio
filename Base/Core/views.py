from django.shortcuts import render
from .models import AboutMeContent, AboutMeStat, AboutMeImage

def Home(request):
    aboutmecontent = AboutMeContent.load()
    aboutmestats = AboutMeStat.objects.all()
    aboutmeimages = AboutMeImage.objects.all()
    return render(request, "base.html", {'AboutMeContent': aboutmecontent, 'AboutMeStats': aboutmestats, 'AboutMeImages': aboutmeimages})

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