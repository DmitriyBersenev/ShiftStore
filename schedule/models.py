from django.db import models


class Shift(models.Model):
    name = models.CharField(max_length=30, verbose_name='Название шаблона')

    start = models.TimeField(verbose_name='Начало смены')
    duration = models.TimeField(verbose_name='Длительность')
    max_duration = models.TimeField(verbose_name='Максимальная длительность')

    working_days = models.IntegerField(verbose_name='Рабочих дней')
    days_off = models.IntegerField(verbose_name='Выходных дней')
    floating_weekend = models.BooleanField(verbose_name='Плавающие выходные', default=False)

    lunch_duration = models.IntegerField(verbose_name='Длительность обеда', help_text='*время в минутах')
    start_duration = models.TimeField(verbose_name='Интервал начала обеда')
    end_duration = models.TimeField(verbose_name='Интервал конца обеда')

    class Meta:
        verbose_name = 'Смена'
        verbose_name_plural = 'Смены'

    def __str__(self):
        return self.name
