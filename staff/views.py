import re
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch
from .models import Employee, Department, TypeDepartment

def home_search(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')      # Рівень 1: 'faculties', 'divisions', 'rectorate'
    faculty_id = request.GET.get('faculty', '')     # Рівень 2: конкретний факультет
    department_id = request.GET.get('department', '') # Рівень 3: конкретна кафедра або відділ

    # --- ДАНІ ДЛЯ ІНТЕРАКТИВНИХ ТЕГІВ ---
    faculties = Department.objects.filter(
        type_dep__name_type__in=['Факультет', 'Інститут'],
        show_in_structure=True
    ).order_by('name').distinct()

    divisions = Department.objects.filter(
        type_dep__name_type='Відділ',
        show_in_structure=True
    ).order_by('name')

    child_departments = []
    selected_faculty_obj = None
    selected_department_obj = None

    if faculty_id:
        child_departments = Department.objects.filter(parent_id=faculty_id, show_in_structure=True).order_by('name')
        selected_faculty_obj = Department.objects.filter(pk=faculty_id).first()

    if department_id:
        selected_department_obj = Department.objects.filter(pk=department_id).first()

    final_results = []
    has_search = bool(query or category or faculty_id or department_id)

    # --- ЛОГІКА ПОШУКУ ТА ФІЛЬТРАЦІЇ ---
    if has_search:
        raw_results = Employee.objects.select_related('department', 'position', 'department__parent')

        # 1. Текстовий пошук
        if query:
            raw_results = raw_results.filter(
                Q(full_name__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(office__icontains=query) |
                Q(mail__icontains=query) |
                Q(position__title__icontains=query) |
                Q(department__name__icontains=query) |
                Q(department__short_name__icontains=query)
            )

        # 2. Фільтрація за тегами (Ієрархія)
        if department_id:
            # Вибрано конкретну кафедру чи відділ
            raw_results = raw_results.filter(department_id=department_id)
        elif faculty_id:
            # Вибрано факультет: показуємо деканат + всі його підпорядковані кафедри
            raw_results = raw_results.filter(
                Q(department_id=faculty_id) | Q(department__parent_id=faculty_id)
            )
        elif category == 'divisions':
            # Показуємо всіх співробітників відділів
            raw_results = raw_results.filter(department__type_dep__name_type='Відділ')
        elif category == 'faculties':
            # Показуємо всіх співробітників факультетів та інститутів
            raw_results = raw_results.filter(
                Q(department__type_dep__name_type__in=['Факультет', 'Інститут']) |
                Q(department__parent__type_dep__name_type__in=['Факультет', 'Інститут'])
            )
        elif category == 'rectorate':
            # Ректорат (шукаємо за назвою підрозділу)
            raw_results = raw_results.filter(department__name__icontains='Ректорат')

        # --- ГРУПУВАННЯ РЕЗУЛЬТАТІВ ---
        grouped_persons = {}
        for person in raw_results:
            name = person.full_name
            if name not in grouped_persons:
                grouped_persons[name] = {
                    'full_name': name,
                    'photo_url': person.photo.url if person.photo else None,
                    'jobs': [],
                    'phones': set(),
                    'mails': set()
                }
            
            grouped_persons[name]['jobs'].append({
                'position': person.position.title if person.position else '',
                'department': person.department.name if person.department else '',
                'office': person.office
            })
            
            if person.phone_number:
                grouped_persons[name]['phones'].add(person.phone_number)
            if person.mail:
                grouped_persons[name]['mails'].add(person.mail)
                
        final_results = list(grouped_persons.values())

    context = {
        'query': query,
        'category': category,
        'faculty_id': faculty_id,
        'department_id': department_id,
        'faculties': faculties,
        'divisions': divisions,
        'child_departments': child_departments,
        'selected_faculty_obj': selected_faculty_obj,
        'selected_department_obj': selected_department_obj,
        'results': final_results,
        'has_search': has_search
    }
    
    return render(request, 'staff/home.html', context)


def structure_view(request):
    """
    Сторінка структури (акордеон).
    """
    active_departments = Department.objects.filter(show_in_structure=True).prefetch_related(
        Prefetch('employee_set', queryset=Employee.objects.select_related('position'))
    ).select_related('parent')
    
    types = TypeDepartment.objects.prefetch_related(
        Prefetch('department_set', queryset=active_departments)
    ).all()

    parent_units = Department.objects.filter(
        type_dep__name_type__in=['Факультет', 'Інститут'],
        show_in_structure=True
    ).order_by('name').distinct()
    
    context = {
        'types': types,
        'parent_units': parent_units,
    }
    return render(request, 'staff/structure.html', context)

def print_full_structure(request):
    """
    Генерація сторінки для друку всієї структури університету
    """
    types = TypeDepartment.objects.prefetch_related(
        Prefetch(
            'department_set', 
            queryset=Department.objects.filter(show_in_structure=True).order_by('name').prefetch_related(
                Prefetch(
                    'employee_set', 
                    queryset=Employee.objects.select_related('position').order_by('full_name')
                )
            )
        )
    ).all()
    
    context = {
        'types': types,
    }
    return render(request, 'staff/print_structure.html', context)


def print_department_type(request, pk):
    """Друк всіх підрозділів певного типу (наприклад, Всі Факультети) з їхніми кафедрами"""
    dep_type = get_object_or_404(TypeDepartment, pk=pk)
    
    departments = Department.objects.filter(type_dep=dep_type, show_in_structure=True).prefetch_related(
        Prefetch('employee_set', queryset=Employee.objects.select_related('position').order_by('full_name')),
        Prefetch('sub_departments', queryset=Department.objects.filter(show_in_structure=True).prefetch_related(
            Prefetch('employee_set', queryset=Employee.objects.select_related('position').order_by('full_name'))
        ).order_by('name'))
    ).order_by('name')

    return render(request, 'staff/print_partial_structure.html', {
        'dep_type': dep_type,
        'departments': departments
    })

def print_specific_department(request, pk):
    """Друк ОДНОГО конкретного підрозділу (з модального вікна) та його кафедр"""
    single_dep = get_object_or_404(Department.objects.prefetch_related(
        Prefetch('employee_set', queryset=Employee.objects.select_related('position').order_by('full_name')),
        Prefetch('sub_departments', queryset=Department.objects.filter(show_in_structure=True).prefetch_related(
            Prefetch('employee_set', queryset=Employee.objects.select_related('position').order_by('full_name'))
        ).order_by('name'))
    ), pk=pk)

    return render(request, 'staff/print_partial_structure.html', {
        'single_dep': single_dep,
        'departments': [single_dep] 
    })