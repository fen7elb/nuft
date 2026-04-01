from django.db import models

class TypeDepartment(models.Model):
    id_type_department = models.AutoField(primary_key=True)
    name_type = models.CharField(max_length=45, verbose_name="Тип підрозділу")

    class Meta:
        managed = True
        db_table = 'type_department'
        verbose_name = "Тип підрозділу"
        verbose_name_plural = "Типи підрозділів"

    def __str__(self):
        return self.name_type


class Department(models.Model):
    id_department = models.AutoField(primary_key=True, db_comment='унікальний код')
    name = models.CharField(max_length=255, verbose_name="Назва кафедри", db_comment='повна назва')
    short_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Абревіатура", db_comment='абревіатура')
    mail = models.CharField(max_length=100, blank=True, null=True, verbose_name="Email", db_comment='пошта кафедри/відділу')
    type_dep = models.ForeignKey(TypeDepartment, on_delete=models.CASCADE, verbose_name="Тип")
    
    show_in_structure = models.BooleanField(default=True, verbose_name="показувати в структурі")

    # ДОДАЄМО ЗВ'ЯЗОК (Ієрархію)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sub_departments',
        verbose_name="Підпорядковується (Факультет/Інститут)"
    )

    class Meta:
        managed = True # Django керує цією таблицею
        db_table = 'department'
        verbose_name = "Підрозділ"
        verbose_name_plural = "Підрозділи"

    def __str__(self):
        return self.name


class Position(models.Model):
    id_position = models.AutoField(primary_key=True, db_comment='унікальний код')
    title = models.CharField(max_length=100, verbose_name="Назва посади", db_comment='назва посади')

    class Meta:
        managed = True
        db_table = 'position'
        verbose_name = "Посада"
        verbose_name_plural = "Посади"

    def __str__(self):
        return self.title


class Employee(models.Model):
    id_employee = models.AutoField(primary_key=True, db_comment='код співробітника')
    full_name = models.CharField(max_length=150, verbose_name="ПІБ", db_comment='ПІБ')
    
    #max_length=20 (як у базі), on_delete=CASCADE (видаляти людину, якщо видалили посаду)
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон", db_comment='номер телефону')
    mail = models.CharField(max_length=100, blank=True, null=True, verbose_name="Email", db_comment='особиста пошта')
    office = models.CharField(max_length=20, blank=True, null=True, verbose_name="Кабінет", db_comment='кабінет / аудиторія')
    photo = models.ImageField(upload_to='employees_photos/', blank=True, null=True, verbose_name="Фотографія")
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Підрозділ")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Посада")

    class Meta:
        managed = True
        db_table = 'employee'
        verbose_name = "Співробітник"
        verbose_name_plural = "Співробітники"

    def __str__(self):
        return self.full_name