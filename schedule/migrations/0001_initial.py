# Generated by Django 3.2.4 on 2021-06-18 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название шаблона')),
                ('start', models.TimeField(verbose_name='Начало смены')),
                ('duration', models.TimeField(verbose_name='Длительность')),
                ('max_duration', models.TimeField(verbose_name='Максимальная длительность')),
                ('working_days', models.IntegerField(verbose_name='Рабочих дней')),
                ('days_off', models.IntegerField(verbose_name='Выходных дней')),
                ('floating_weekend', models.BooleanField(default=False, verbose_name='Плавающие выходные')),
                ('lunch_duration', models.IntegerField(verbose_name='Длительность обеда')),
                ('start_duration', models.TimeField(verbose_name='Интервал начала обеда')),
                ('end_duration', models.TimeField(verbose_name='Интервал конца обеда')),
            ],
            options={
                'verbose_name': 'Смена',
                'verbose_name_plural': 'Смены',
            },
        ),
    ]
