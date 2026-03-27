from django.shortcuts import render
from django.db.models import Q, Prefetch
from .models import Employee, Department, TypeDepartment

def home_search(request):
    query = request.GET.get('q', '').strip()
    
    final_results = []
    
    if query:
        # 1. Шукаємо як і раніше
        raw_results = Employee.objects.filter(
            Q(full_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(office__icontains=query) |
            Q(mail__icontains=query) |
            Q(position__title__icontains=query) |
            Q(department__name__icontains=query) |
            Q(department__short_name__icontains=query)
        ).select_related('department', 'position')
        
        # 2. Групуємо людей за ПІБ
        grouped_persons = {}
        for person in raw_results:
            name = person.full_name
            
            # Якщо таку людину бачимо вперше — створюємо для неї "контейнер"
            if name not in grouped_persons:
                grouped_persons[name] = {
                    'full_name': name,
                    'jobs': [], # Тут буде список усіх її посад і кафедр
                    'phones': set(), # set() гарантує, що не буде однакових телефонів
                    'mails': set()
                }
            
            # Додаємо посаду в список цієї людини
            grouped_persons[name]['jobs'].append({
                'position': person.position.title if person.position else '',
                'department': person.department.name if person.department else '',
                'office': person.office
            })
            
            # Додаємо контакти (якщо вони є)
            if person.phone_number:
                grouped_persons[name]['phones'].add(person.phone_number)
            if person.mail:
                grouped_persons[name]['mails'].add(person.mail)
                
        # 3. Перетворюємо наш словник назад у звичайний список для HTML
        final_results = list(grouped_persons.values())

    context = {
        'query': query,
        'results': final_results,
    }
    
    return render(request, 'staff/home.html', context)


def structure_view(request):
    """
    Сторінка структури (акордеон). Поки що просто пуста заготовка.
    """
    return render(request, 'staff/structure.html')



def structure_view(request):
    """
    Сторінка структури (акордеон).
    """
    
    #active_departments = Department.objects.filter(show_in_structure=True)
    active_departments = Department.objects.filter(show_in_structure=True).prefetch_related(
        Prefetch('employee_set', queryset=Employee.objects.select_related('position'))
    )
    
    # Дістаємо всі типи підрозділів і одразу "чіпляємо" до них їхні кафедри/відділи
    # prefetch_related робить так, щоб база не "зависла" від кількості запитів
    #types = TypeDepartment.objects.prefetch_related(
    #    Prefetch('department_set', queryset=active_departments)
    #).all()

    types = TypeDepartment.objects.prefetch_related(
        Prefetch('department_set', queryset=active_departments)
    ).all()
    
    context = {
        'types': types
    }
    
    return render(request, 'staff/structure.html', context)