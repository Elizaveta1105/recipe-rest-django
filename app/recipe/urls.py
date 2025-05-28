from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recipe'
route = DefaultRouter()
route.register('recipes', views.RecipeViewSets)

urlpatterns = [
    path('', include(route.urls))
]
