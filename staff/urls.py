from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_search, name='home'),
    path('structure/', views.structure_view, name='structure'),
    path('structure/print/', views.print_full_structure, name='print_full_structure'),
    path('structure/print/type/<int:pk>/', views.print_department_type, name='print_department_type'),
    path('structure/print/department/<int:pk>/', views.print_specific_department, name='print_specific_department'),
]