from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_search, name='home'),
    path('structure/', views.structure_view, name='structure'),
]