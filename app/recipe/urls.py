from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recipe'
route = DefaultRouter()
route.register('recipes', views.RecipeViewSets)
route.register('tags', views.TagViewSet)
route.register('ingredients', views.IngredientViewSet)

urlpatterns = [
    path('', include(route.urls))
]
