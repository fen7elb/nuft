from django.shortcuts import render
from django.db.models import Q, Prefetch
from .models import Employee, Department, TypeDepartment

def home_search(request):
    """
    Головна сторінка з пошуком.
    """
    # Отримуємо те, що юзер ввів у рядок пошуку (name="q" в HTML-формі)
    query = request.GET.get('q', '')
    
    # Створюємо порожній список результатів
    results = []
    
    # Якщо юзер щось ввів, починаємо шукати
    if query:
        # Шукаємо співробітників, де запит збігається з ПІБ, телефоном АБО кабінетом
        results = Employee.objects.filter(
            Q(full_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(office__icontains=query) |
            Q(mail__icontains=query) |
            Q(position__title__icontains=query) |
            Q(department__name__icontains=query) |
            Q(department__short_name__icontains=query)
        ).select_related('department', 'position') # select_related для швидкості бази
        
    # Віддаємо словник контексту в HTML-шаблон
    context = {
        'query': query,
        'results': results,
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
    
    active_departments = Department.objects.filter(show_in_structure=True)
    
    # Дістаємо всі типи підрозділів і одразу "чіпляємо" до них їхні кафедри/відділи
    # prefetch_related робить так, щоб база не "зависла" від кількості запитів
    types = TypeDepartment.objects.prefetch_related(
        Prefetch('department_set', queryset=active_departments)
    ).all()
    
    context = {
        'types': types
    }
    
    return render(request, 'staff/structure.html', context)