from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch
from .models import Employee, Department, TypeDepartment

def home_search(request):
    query = request.GET.get('q', '').strip()
    final_results = []
    
    if query:
        raw_results = Employee.objects.filter(
            Q(full_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(office__icontains=query) |
            Q(mail__icontains=query) |
            Q(position__title__icontains=query) |
            Q(department__name__icontains=query) |
            Q(department__short_name__icontains=query)
        ).select_related('department', 'position')
        
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
        'results': final_results,
    }
    return render(request, 'staff/home.html', context)


def structure_view(request):
    """
    Сторінка структури (акордеон).
    """
    # Завантажуємо підрозділи разом з їхніми "батьками" для фільтрації
    active_departments = Department.objects.filter(show_in_structure=True).prefetch_related(
        Prefetch('employee_set', queryset=Employee.objects.select_related('position'))
    ).select_related('parent')
    
    types = TypeDepartment.objects.prefetch_related(
        Prefetch('department_set', queryset=active_departments)
    ).all()

    # Отримуємо список факультетів та інститутів для випадаючого списку
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
        # Магія: витягуємо підпорядковані кафедри!
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
        'departments': [single_dep] # Передаємо як список, щоб шаблон був універсальним
    })