from django.contrib import admin
from .models import Employee, Department, Position, TypeDepartment

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'mail', 'department', 'position')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'mail')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(TypeDepartment)
class TypeDepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_type',)