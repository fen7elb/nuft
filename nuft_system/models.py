# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Department(models.Model):
    id_department = models.AutoField(primary_key=True, db_comment='унікальний код')
    name = models.CharField(max_length=255, db_comment='повна назва')
    short_name = models.CharField(max_length=50, db_comment='абревіатура')
    mail = models.CharField(max_length=100, db_comment='пошта кафедри/відділу')
    type_dep = models.ForeignKey('TypeDepartment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'department'


class Employee(models.Model):
    id_employee = models.AutoField(primary_key=True, db_comment='код співробітника')
    full_name = models.CharField(max_length=150, db_comment='ПІБ')
    phone_number = models.CharField(max_length=20, db_comment='номер телефону')
    mail = models.CharField(max_length=100, blank=True, null=True, db_comment='особиста пошта')
    office = models.CharField(max_length=20, db_comment='кабінет / аудиторія')
    department = models.ForeignKey(Department, models.DO_NOTHING)
    position = models.ForeignKey('Position', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'employee'


class Position(models.Model):
    id_position = models.AutoField(primary_key=True, db_comment='унікальний код')
    title = models.CharField(max_length=100, db_comment='назва посади')

    class Meta:
        managed = False
        db_table = 'position'


class TypeDepartment(models.Model):
    id_type_department = models.AutoField(primary_key=True)
    name_type = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'type_department'
