from django.contrib import admin
from .models import Employee, Department, Position, TypeDepartment

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'mail', 'department', 'position', 'office')
    search_fields = ('full_name',) #факап з парсингом
    #list_filter = ('department', 'position') #факап з парсингом

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'mail', 'type_dep', 'parent', 'show_in_structure')
    search_fields = ('name', 'short_name', 'mail', 'type_dep__name_type') #факап з парсингом
    list_filter = ('type_dep', 'parent', 'show_in_structure') #факап з парс
    list_editable = ('show_in_structure',) #факап з парсингом

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(TypeDepartment)
class TypeDepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_type',)
    search_fields = ('name_type',)