from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_search, name='home'),
    path('structure/', views.structure_view, name='structure'),
    path('structure/print/', views.print_full_structure, name='print_full_structure'),
]