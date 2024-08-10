from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', WelcomeIndex, name="WelcomeIndex"),
    path('portfolio', Index, name="Index"),
    path('about-me', AboutMe, name="AboutMe"),
    path('space-commander-seu', SpaceCommanderInfo, name="SpaceCommanderSEU"),
    path('gems-crawler', GemsCrawlerInfo, name="GemsCrawler"),
    path('final-project', FinalProjectInfo, name="FinalProject"),
]