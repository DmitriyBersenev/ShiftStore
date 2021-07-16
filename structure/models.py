from django.db import models

from schedule.models import Shift


class Team(models.Model):
    name = models.CharField(max_length=25, verbose_name='Название команды')
    persons = models.ManyToManyField('Person', verbose_name='Специалисты', blank=True)
    timezone = models.ForeignKey('TimeZone', on_delete=models.SET_NULL, null=True, verbose_name='Часовой пояс')
    team_priority = models.IntegerField(default=1, blank=True, verbose_name='Индекс в графике')
    type = models.ForeignKey('TeamType', on_delete=models.SET_NULL, null=True, verbose_name='Тип команды')

    def display_count_persons(self) -> int:
        """ Отображает количество специалистов в команде """

    display_count_persons.short_description = 'Количество специалистов'

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):
        return self.name


class Person(models.Model):
    first_name = models.CharField(max_length=25, verbose_name='Имя')
    last_name = models.CharField(max_length=25, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=25, verbose_name='Отчество', null=True, blank=True)

    employment_date = models.DateField(verbose_name='Дата трудоустройства')
    dismissal_date = models.DateField(verbose_name='Дата увольнения', null=True, blank=True)
    transition_history = models.JSONField(verbose_name='История переходов', null=True, blank=True)
    timezone = models.ForeignKey('TimeZone', on_delete=models.SET_NULL, null=True)

    link_channels = models.ManyToManyField('Link', verbose_name='Каналы связи', blank=True)
    roles = models.ManyToManyField('Role', verbose_name='Роли', blank=True)
    contract_type = models.ForeignKey('ContractType', on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name='Тип договора')

    person_priority = models.IntegerField(default=1, verbose_name='Индекс в графике')
    shift_templates = models.ManyToManyField(Shift, verbose_name='Шаблоны графика', blank=True)

    def display_full_name(self) -> str:
        """ Отображает полное имя специалиста """
        return f'{self.last_name} {self.first_name} {self.patronymic}'.strip()

    display_full_name.short_description = 'Имя специалиста'

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.patronymic}'.strip()


class TimeZone(models.Model):
    timezone = models.CharField(max_length=25, verbose_name='Часовой пояс')
    utc = models.IntegerField(default=5, verbose_name='UTC')

    class Meta:
        verbose_name = 'Часовой пояс'
        verbose_name_plural = 'Часовые пояса'

    def __str__(self):
        return f'{self.timezone}'


class Link(models.Model):
    link = models.CharField(max_length=25, verbose_name='Канал связи')

    class Meta:
        verbose_name = 'Канал связи'
        verbose_name_plural = 'Каналы связи'

    def __str__(self):
        return f'{self.link}'


class Role(models.Model):
    role = models.CharField(max_length=25, verbose_name='Роль')
    role_time = models.FloatField(default=0.0, verbose_name='Время на роль')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return f'{self.role}'


class ContractType(models.Model):
    contract_name = models.CharField(max_length=25, verbose_name='Название')
    norma_hours = models.FloatField(default=0.0, verbose_name='Норма часов')

    class Meta:
        verbose_name = 'Тип договора'
        verbose_name_plural = 'Типы договоров'

    def __str__(self):
        return f'{self.contract_name}'


class TeamType(models.Model):
    type = models.CharField(max_length=25, verbose_name='Название типа')

    class Meta:
        verbose_name = 'Тип команды'
        verbose_name_plural = 'Типы команд'

    def __str__(self):
        return f'{self.type}'
