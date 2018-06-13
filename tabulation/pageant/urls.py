"""tabulation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('auth', views.Authentication.as_view(), name='auth'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('login', views.LoginView.as_view(), name='login'),
    path('template/<str:name>', views.TemplateView.as_view(), name='template'),
    path('categories', views.CategoriesView.as_view(), name='scoresheet'),
    path('candidates', views.CandidatesView.as_view(), name='candidates'),
    path('scores/<str:category>', views.ScoresView.as_view(), name='scores'),
    path('judges/<str:category>', views.JudgeScoresView.as_view(), name='judges'),
    path('top-seven/<str:format>', views.TopSevenView.as_view()),
    path('results/<str:category>.<str:format>', views.CategoryResultsView.as_view()),
    path('final', views.FinalView.as_view()),
    path('results/final/<str:format>', views.FinalResultsView.as_view()),
]
