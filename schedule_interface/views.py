from django.http import JsonResponse
from django.shortcuts import render
from structure import models
from data import config

from .services import create_template


def index(request):
    """ Создает шаблон главной страницы """
    pass


def create_templates(request):
    """ Представление страницы с формой для создания шаблона графика """
    teams = models.Team.objects.all()
    google_sheet_ids = config.GOOGLE_SHEETS_ADDRESS['Шаблон']
    context = {'teams': teams, 'google_sheet_ids': google_sheet_ids}
    return render(request, 'schedule_interface/create_template.html', context)


def get_form_create_template(request):
    """ Получить данные по созданию шаблона из формы и создать шаблон """
    data = {}
    if request.method == 'POST':
        form_data = {'date': request.POST.get('date'),
                     'norma_hours': int(request.POST.get('norma_hours')),
                     'holidays': request.POST.get('holidays'),
                     'excepted_holidays': request.POST.get('excepted_holidays'),
                     'google_sheet_name': request.POST.get('google_sheet_name'),
                     'teams': request.POST.getlist('teams'),
                     'get_wishes': request.POST.get('get_wishes'),
                     }
        update_form_data = create_template.collect_configurations(form_data)
        data['link'] = create_template.open_template(update_form_data)
    return JsonResponse(data)
