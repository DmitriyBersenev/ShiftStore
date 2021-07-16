from django.http import JsonResponse
from django.shortcuts import render

from . import models
from .services import db_commands


# Create your views here.
def index(request):
    """ Создает шаблон главной страницы """
    teams_and_persons = db_commands.persons_in_teams()
    timezone = [tz.timezone for tz in models.TimeZone.objects.all()]
    links = [link.link for link in models.Link.objects.all()]
    contract_types = [contract_type.contract_name for contract_type in models.ContractType.objects.all()]
    roles = [role.role for role in models.Role.objects.all()]

    context = {'teams_and_persons': teams_and_persons, 'timezone': timezone, 'links': links,
               'contract_types': contract_types, 'roles': roles}
    return render(request, 'structure/index.html', context)


def create_person(request):
    """ Обрабатывает форму создания специалиста и добавлет его в базу данных """
    data = {}
    if request.method == 'POST':
        person_data = {'last_name': request.POST.get('last_name').strip(),
                       'first_name': request.POST.get('first_name').strip(),
                       'patronymic': request.POST.get('patronymic').strip(),
                       'employment_date': request.POST.get('employment_date'),
                       'timezone': request.POST.get('timezone'),
                       'team': request.POST.get('team'),
                       'contract_type': request.POST.get('contract_type'),
                       'links': request.POST.getlist('links'),
                       'roles': request.POST.getlist('roles')}

        db_commands.create_new_person(person_data)

    return JsonResponse(data)


def remove_person(request):
    """ Удаляет специалиста из базы данных, если пришел запрос """
    data = {}
    if request.method == 'POST':
        person_id = request.POST.get('person_id')
        db_commands.remove_person(person_id)

    return JsonResponse(data)


def fire_person(request):
    """ Уволняет специалиста, если пришел запрос """
    data = {}
    if request.method == 'POST':
        person_id = request.POST.get('person_id')
        fired_date = request.POST.get('fired_date')
        db_commands.fire_person(person_id, fired_date)

    return JsonResponse(data)


def transfer_person(request):
    """ Переводит специалиста в другую команду, если пришел запрос """
    data = {}
    if request.method == 'POST':
        person_id = request.POST.get('person_id')
        last_team = request.POST.get('last_team')
        new_team = request.POST.get('new_team')
        db_commands.transfer_person(person_id, last_team, new_team)

    return JsonResponse(data)
