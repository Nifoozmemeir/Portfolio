from django.shortcuts import render

def WelcomeIndex(request):
    return render(request, "welcome_index.html")

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