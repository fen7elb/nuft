from django.db import models

class TypeDepartment(models.Model):
    id_type_department = models.AutoField(primary_key=True)
    name_type = models.CharField(max_length=45)

    class Meta:
        managed = True
        db_table = 'type_department'
        verbose_name = 'Тип підрозділу'
        verbose_name_plural = 'Типи підрозділів'

    # ОЦЕЙ РЯДОК ВИПРАВЛЯЄ ID НА НАЗВУ:
    def __str__(self):
        return self.name_type


class Department(models.Model):
    id_department = models.AutoField(primary_key=True, db_comment='унікальний код')
    name = models.CharField(max_length=255, db_comment='повна назва')
    short_name = models.CharField(max_length=50, db_comment='абревіатура', blank=True, null=True)
    mail = models.CharField(max_length=100, db_comment='пошта кафедри/відділу', blank=True, null=True)
    type_dep = models.ForeignKey(TypeDepartment, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'department'
        verbose_name = 'Підрозділ'
        verbose_name_plural = 'Підрозділи'

    # ОЦЕЙ РЯДОК ВИПРАВЛЯЄ ID НА НАЗВУ:
    def __str__(self):
        return self.name


class Position(models.Model):
    id_position = models.AutoField(primary_key=True, db_comment='унікальний код')
    title = models.CharField(max_length=100, db_comment='назва посади')

    class Meta:
        managed = True
        db_table = 'position'
        verbose_name = 'Посада'
        verbose_name_plural = 'Посади'

    # ОЦЕЙ РЯДОК ВИПРАВЛЯЄ ID НА НАЗВУ:
    def __str__(self):
        return self.title


class Employee(models.Model):
    id_employee = models.AutoField(primary_key=True, db_comment='код співробітника')
    full_name = models.CharField(max_length=150, db_comment='ПІБ')
    phone_number = models.CharField(max_length=100, db_comment='номер телефону')
    mail = models.CharField(max_length=100, blank=True, null=True, db_comment='особиста пошта')
    office = models.CharField(max_length=100, db_comment='кабінет / аудиторія')
    department = models.ForeignKey(Department, models.DO_NOTHING)
    position = models.ForeignKey(Position, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'employee'
        verbose_name = 'Співробітник'
        verbose_name_plural = 'Співробітники'

    def __str__(self):
        return self.full_name