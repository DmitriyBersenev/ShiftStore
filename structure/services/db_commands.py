import json
from datetime import datetime
from .. import models


def create_new_person(person_data: dict) -> bool:
    """
    Добавляет нового специалиста в базу данных
    :param person_data: словарь с данными о специалисте;
    """

    employment_date = datetime.strptime(person_data['employment_date'], "%Y-%m-%d")
    timezone = models.TimeZone.objects.get(timezone=person_data['timezone'])
    contract = models.ContractType.objects.get(contract_name=person_data['contract_type'])

    person = models.Person(first_name=person_data['first_name'], last_name=person_data['last_name'],
                           patronymic=person_data['patronymic'], employment_date=employment_date, timezone=timezone,
                           contract_type=contract)
    person.save()

    for link in person_data['links']:
        link_model = models.Link.objects.get(link=link)
        person.link_channels.add(link_model)
    for role in person_data['roles']:
        role_model = models.Role.objects.get(role=role)
        person.roles.add(role_model)
    team = models.Team.objects.get(name=person_data['team'])
    team.persons.add(person)

    return True


def transfer_person(person_id: int, last_team: str, new_team: str) -> list:
    """ Переводит специалиста из одной команды в другую """
    person = models.Person.objects.get(id=person_id)
    last_team = models.Team.objects.get(name=last_team)
    new_team = models.Team.objects.get(name=new_team)

    new_team.persons.add(person)
    last_team.persons.remove(person)

    # Записываем изменение команды в историю
    history = json.loads(person.transition_history) if person.transition_history else {}
    current_history = {str(datetime.now()): {'from': last_team.name, 'to': new_team.name}}
    person.transition_history = json.dumps({**history, **current_history})

    person.save()
    return sorted(new_team.persons.all(), key=lambda x: x.last_name)


def remove_person(person_id: int) -> bool:
    """ Удаляет специалиста """
    person = models.Person.objects.get(id=person_id)
    person.delete()
    return True


def fire_person(person_id: int, fired_date: str) -> bool:
    """ Увольняет специалиста. Т.е. специалист не будет удален из БД, но оборвет все связи """
    person = models.Person.objects.get(id=person_id)
    fired_date = datetime.strptime(fired_date, "%Y-%m-%d")
    person.dismissal_date = fired_date

    # Удаляю связи
    teams = person.team_set.all()
    for team in teams:
        team.persons.remove(person)
    for link in person.link_channels.all():
        person.link_channels.remove(link)
    for role in person.roles.all():
        person.roles.remove(role)
    for shift_template in person.shift_templates.all():
        person.shift_templates.remove(shift_template)

    # Записываю в историю
    history = json.loads(person.transition_history) if person.transition_history else {}
    current_history = {str(fired_date): 'fire'}
    person.transition_history = json.dumps({**history, **current_history})
    person.save()
    return True


def persons_in_teams() -> dict:
    """ Создает словарь с командами и сортированными специалистами в них """
    sorted_teams = sorted(models.Team.objects.all(), key=lambda x: (x.team_priority, x.name))
    team_list = {team: '' for team in sorted_teams}
    for team in models.Team.objects.all():
        persons = sorted(team.persons.all(), key=lambda p: (p.person_priority, p.last_name))
        team_list[team] = persons
    return team_list
