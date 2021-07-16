from django.contrib import admin

from .models import *


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'duration',)
    ordering = ('name',)

    fieldsets = [(None, {'fields': ('name',)}),
                 ('Время', {
                     'fields': (('start',), ('duration', 'max_duration'))}),
                 ('Ротация', {'fields': (('working_days', 'days_off'), ('floating_weekend',))}),
                 ('Обед', {'fields': (('lunch_duration',), ('start_duration', 'end_duration'))}), ]
