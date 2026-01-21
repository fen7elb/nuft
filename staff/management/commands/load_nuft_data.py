import openpyxl
import os
import re
from django.core.management.base import BaseCommand
from staff.models import Department, Employee, Position, TypeDepartment
from django.conf import settings

class Command(BaseCommand):
    help = 'імпорт даних нухт з виправленням регістру прізвищ'

    def handle(self, *args, **kwargs):
        file_path = settings.BASE_DIR / 'data' / 'Довідник НУХТ.xlsx'
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'файл {file_path} не знайдено!'))
            return

        self.stdout.write(self.style.WARNING('очищення старих записів'))
        Employee.objects.all().delete()
        Department.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS(f'відкриваємо Excel...'))
        workbook = openpyxl.load_workbook(file_path, data_only=True)

        sheets_map = {
            'Ректорат': 'Ректорат',
            'Інститути': 'Інститут',
            'Деканати': 'Факультет',
            'Кафедри': 'Кафедра',
            'Відділи': 'Відділ'
        }

        for sheet_name, type_name in sheets_map.items():
            if sheet_name not in workbook.sheetnames:
                continue

            type_dep, _ = TypeDepartment.objects.get_or_create(name_type=type_name)
            sheet = workbook[sheet_name]
            
            self.stdout.write(self.style.SUCCESS(f'--- Обробка вкладки: {sheet_name} ---'))
            current_department = None

            for row in sheet.iter_rows(min_row=2, values_only=True):
                val0 = str(row[0]).strip() if row[0] else ""  # посада або назва відділу
                val1 = str(row[1]).strip() if row[1] else ""  # піб
                val2 = str(row[2]).strip() if row[2] else ""  # пошта
                val3 = str(row[3]).strip() if row[3] else ""  # телефон
                val4 = str(row[4]).strip() if len(row) > 4 and row[4] else "" # кабінет

                if not val0 and not val1:
                    continue 

                # назва кафедри/відділу
                if val0 and not val1:
                    raw_text = val0
                    
                    #витягуємо email з назви (якщо він там є)
                    found_email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
                    dept_mail = val2 
                    
                    if found_email:
                        email_str = found_email.group(0)
                        if not dept_mail: 
                            dept_mail = email_str
                        raw_text = raw_text.replace(email_str, '')

                    #чистимо назву
                    clean_name = re.sub(r'^\(\d+\)\s*', '', raw_text)
                    clean_name = clean_name.replace('\n', ' ').strip()
                    clean_name = re.sub(r'\s+', ' ', clean_name)

                    current_department, _ = Department.objects.get_or_create(
                        name=clean_name,
                        defaults={
                            'short_name': clean_name[:50],
                            'mail': dept_mail,
                            'type_dep': type_dep
                        }
                    )
                    continue

                # співробітник
                if val1 and current_department:
                    # піб: прибираємо ентери + прибираємо капс
                    full_name_clean = val1.replace('\n', ' ').strip().title()

                    # посада
                    position_clean = val0.replace('\n', ' ').strip().capitalize()

                    # телефон
                    phone_clean = val3.replace('\n', ', ').strip()[:20]

                    # кабінет
                    office_clean = val4.replace('\n', ' ').strip()[:20]

                    position_obj, _ = Position.objects.get_or_create(title=position_clean)

                    Employee.objects.get_or_create(
                        full_name=full_name_clean,
                        defaults={
                            'phone_number': phone_clean,
                            'mail': val2,
                            'office': office_clean,
                            'department': current_department,
                            'position': position_obj
                        }
                    )

        self.stdout.write(self.style.SUCCESS('імпорт завершено'))