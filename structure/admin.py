from django.contrib import admin

from .models import *


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'timezone', 'type', 'display_count_persons')

    ordering = ('team_priority', 'name')

    fieldsets = [(None, {'fields': ('name', 'timezone',)}),
                 ('Специалисты', {'fields': ('persons',)}),
                 (None, {'fields': (('type', 'team_priority',),)}),
                 ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('display_full_name', 'timezone', 'employment_date')

    ordering = ('last_name', 'first_name')

    fieldsets = [(None, {'fields': (('last_name', 'first_name', 'patronymic'),)}),
                 ('Даты', {
                     'fields': (('employment_date', 'dismissal_date', 'timezone'), ('transition_history',))}),
                 ('Принадлежность', {'fields': (('link_channels', 'roles',), ('contract_type',))}),
                 ('График', {'fields': ('person_priority', 'shift_templates')}), ]


@admin.register(TimeZone)
class TimeZoneAdmin(admin.ModelAdmin):
    list_display = ('timezone', 'utc',)
    ordering = ('timezone',)
    fields = ['timezone', 'utc', ]


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('link',)
    ordering = ('link',)
    fields = ['link', ]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'role_time')
    ordering = ('role',)
    fields = ['role', 'role_time']


@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('contract_name', 'norma_hours')
    ordering = ('contract_name',)
    fields = ['contract_name', 'norma_hours']


@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)
    ordering = ('type',)
    fields = ['type', ]
