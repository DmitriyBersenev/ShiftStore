from calendar import monthrange
from googleapiclient import errors
from api.google_sheets import google_sheets
from api.google_sheets.excel_formulas import ExcelFormula
from data import config
from structure.models import Person, Team
from persons_vacation.services.persons_vacation import PersonsVacation
from . import calendar


class ContextGrouper:

    def __init__(self, configurations: dict):
        self.data = configurations
        self.holidays = PersonsVacation().merge_persons_holidays_with_db(self.data['year'], self.data['month'])
        self.weekends_indices = self.weekends_indices(self.data['holidays'], self.data['excepted_holidays'])

    def weekends_indices(self, holidays: str, except_weekends: str) -> set:
        """
        Возвращает множество с индексами всех выходных дней месяца.
        :param holidays: праздничные дни в месяце;
        :param except_weekends: искючение выходных дней в случае переноса праздников;
        """
        weekdays = [calendar.get_weekday(self.data['year'], self.data['month'], day + 1) for day in
                    range(self.data['days_in_month'])]
        weekends_indices = [day + 1 for day, weekday in enumerate(weekdays) if weekday > 5]

        if holidays:
            holidays_indices = [int(i) for i in holidays.split(',')]
            weekends_indices.extend(holidays_indices)  # add holidays

        if except_weekends:
            except_weekends_indices = [int(i) for i in except_weekends.split(',')]
            weekends_indices = [i for i in weekends_indices if i not in except_weekends_indices]  # except weekends

        return set(weekends_indices)  # remove double items

    def _person_template_blank(self, person) -> list:
        """
        Создает пустой список для формирования шаблона только с именем специалиста.
        :param person: модель специалиста;
        :return: [[линия с ФИО и сменами], [линия с часами смен]]
        """
        return [[person.display_full_name()] + ['' for _ in range(self.data['days_in_month'])],
                ['' for _ in range(self.data['days_in_month'] + 1)]]

    def _person_template_with_data(self, person) -> list:
        """
        Создает ряд заполненный пожеланиями и отпуском специалиста.
        :param person: модель специалиста;
        :return: [[линия с ФИО и сменами], [линия с часами смен]]
        """
        return [[person.display_full_name()] + self.holidays[person],
                ['' for _ in range(self.data['days_in_month'] + 1)]]

    def _group_rows_in_team(self, team, persons_holidays: dict) -> list:
        """
        Группирует контескт данных для отрисовки таблицы выбранной команды.
        :param team: модель команды;
        :param persons_holidays: словарь с данными о отпуске специалиста;
        :return: [[], [], []]
        """
        date = calendar.month_days_template(self.data['year'], self.data['month'], self.data['days_in_month'])
        team_context = [date['days'], date['weekdays']]
        team_context[0][0] = team.name

        persons = sorted(team.persons.all(), key=lambda p: (p.person_priority, p.last_name, p.first_name))
        for person in persons:
            if person in persons_holidays:
                person_template = self._person_template_with_data(person)
            else:
                person_template = self._person_template_blank(person)
            team_context.extend(person_template)

        return team_context

    def _group_teams_context(self, teams) -> list:
        """
        Объединяет листы команд в один, при этом сортирует их по приоритету.
        :param teams: модели всех команд;
        """
        sorted_teams = [team for team in sorted(teams, key=lambda t: (t.team_priority, t.name))]
        context = []

        for team in sorted_teams:
            team_list = self._group_rows_in_team(team, self.holidays)
            team_list.extend([[]])
            context.extend(team_list)

        return context

    def _calc_norma_with_holidays(self, person) -> int:
        """
        Подсчитывает норму часа специалиста, если есть отпуск.
        :param person: модель специалиста;
        :return: новая норма часа.
        """
        norma_hours = '!'
        if person in self.holidays:
            excepted_holiday = config.TEMPLATE_NOTATIONS['Отгул']
            holidays_indices = [i + 1 for i, h in enumerate(self.holidays[person]) if h and h != excepted_holiday]

            person_holidays = [h for h in holidays_indices if h not in self.weekends_indices]
            shift_len = 8
            norma_hours = self.data['norma_hours'] - len(person_holidays) * shift_len

            if norma_hours == self.data['norma_hours']:  # Если норма без изменений, то не показываем ее
                norma_hours = ''

        return norma_hours

    def get_context_indices(self, context: list, teams: list, cell_step: int = 2) -> dict:
        """
        Получает индексы для отрисовки формата
        :param context: собранный контекст для записи в таблицу по которому нужно получить индексы;
        :param teams: список с объектами команд, которые нужно записать.
        :param cell_step: шаг ячеек в таблице
        (по умолчанию - 2: ячейки специалиста с диапазоном смены и количеством часов);
        """
        count_columns = self.data['days_in_month'] + 1
        start_indices = {}
        end_indices = {}

        for team in teams:
            for i, row in enumerate(context):
                if team.name in row:
                    start_indices[team.name] = i
                    end_indices[team.name] = int(
                        len(team.persons.all()) * cell_step + start_indices[team.name] + 2 / cell_step)

        return {'count_columns': count_columns,
                'start_teams_indices': start_indices,
                'end_teams_indices': end_indices}

    def context_with_info_columns(self, teams) -> dict:
        """
        Добавляет правые столбики с дополнительной информацией графика. В них входит: формула с суммой часов,
        общая норма, дополнительные часы.
        :param teams: модели команд;
        """
        context_data = self._group_teams_context(teams)
        start_indices = self.get_context_indices(context_data, teams)['start_teams_indices']

        # К командам добавляет шапку дополнительных часов
        for team in teams:
            context_data[start_indices[team.name]].extend(
                ['кол-во часов', 'норма', 'Доп часы', 'Обучение', 'Итог', 'Максимум часов', 'Канал связи',
                 'Часовой пояс'])
            context_data[start_indices[team.name] + 1].extend(['', self.data['norma_hours'], '', '', '', '', '', ''])

            # Добавляет сумму часов к спецу, считает норму, добавляет доп часы и максимальное количество часов
            persons = sorted(team.persons.all(), key=lambda p: (p.person_priority, p.last_name, p.first_name))
            for index, person in enumerate(persons):
                i = start_indices[team.name] + index * 2 + 2
                sum_hours = ExcelFormula().sum(i + 1, i + 1, 1, self.data['days_in_month'])
                norma_hours = self._calc_norma_with_holidays(person)
                additional_hours = ExcelFormula().calculate_additional_hours(i + 1, self.data['days_in_month'] + 3)
                max_hours = ExcelFormula().person_max_hours(i + 1, self.data['days_in_month'] + 2)
                link = person.link_channels.all()[0].link if person.link_channels.all() else ''
                timezone = 'Мск' if person.timezone.timezone == 'Europe/Moscow' else ''
                context_data[i].extend([sum_hours, norma_hours, '', '', additional_hours, max_hours, link, timezone])

        return context_data


class TemplateWriter:
    def __init__(self, configurations: dict, google_client):
        self.data = configurations
        self.context_grouper = ContextGrouper(self.data)
        self.gs = google_client

    def _update_main_formats(self, sheet_id: str, count_columns: int, end_indices: dict) -> list:
        """
        Создает список с базовыми настройками формата таблицы
        :param sheet_id: id листа;
        :param count_columns: количество колонок в контексте;
        :param end_indices: индексы конечного ряда команды в контексте;
        """
        return [self.gs.cell_size(sheet_id, 0, 1, 250),  # ФИО
                self.gs.cell_size(sheet_id, 1, count_columns + 3, 40),  # График
                self.gs.cell_size(sheet_id, count_columns, count_columns + 2, 60),  # Количество и Норма
                self.gs.cell_size(sheet_id, count_columns + 2, count_columns + 3, 65),  # Доп часы
                self.gs.cell_size(sheet_id, count_columns + 3, count_columns + 4, 75),  # Обучение
                self.gs.cell_size(sheet_id, count_columns + 4, count_columns + 5, 55),  # Итог
                self.gs.cell_size(sheet_id, count_columns + 5, count_columns + 6, 70),  # Максимум часов
                self.gs.cell_size(sheet_id, count_columns + 6, count_columns + 7, 70),  # Канал связи
                self.gs.cell_size(sheet_id, count_columns + 7, count_columns + 8, 70),  # Часовой пояс
                self.gs.format_cell(sheet_id, 0, max(end_indices.values()) + 1, 1, count_columns + 8,
                                    config.MEAN_FORMAT['default']['rgb'], config.MEAN_FORMAT['default']['size'])]

    def _update_person_format(self, sheet_id: str, person: Person, person_index: int, count_columns: int) -> list:
        """
        Задает форматы ряда у специалиста.
        :param sheet_id: id листа;
        :param person: модель специалиста;
        :param person_index: ряд специалиста;
        :param count_columns: количество колонок в контексте;
        """
        person_format = [self.gs.merge_cells(sheet_id, person_index, person_index + 2, 0, 1),
                         self.gs.format_cell(sheet_id, person_index, person_index + 1,
                                             count_columns + 2, count_columns + 5,
                                             config.MEAN_FORMAT['add_hours']['rgb'],
                                             config.MEAN_FORMAT['add_hours']['size'])]

        # Если есть отпуск, раскрашивает в синий цвет
        if person in self.context_grouper.holidays:
            person_holidays = [i + 1 for i, day in enumerate(self.context_grouper.holidays[person]) if day]
            for day in person_holidays:
                person_format.append(self.gs.format_cell(sheet_id, person_index, person_index + 2, day, day + 1,
                                                         config.MEAN_FORMAT['holidays']['rgb'],
                                                         config.MEAN_FORMAT['holidays']['size']))
        return person_format

    def _update_weekends_format(self, sheet_id: str, team: Team, day: int, start_indices: dict,
                                end_indices: dict) -> list:
        """
        Возвращает формат для окраски выходных дней внутри команд.
        :param sheet_id: id листа;
        :param team: команда в которой окрасить;
        :param day: день;
        :param start_indices: индексы стартового ряда команды в контексте;
        :param end_indices: индексы конечного ряда команды в контексте;
        """
        return self.gs.format_cell(sheet_id, start_indices[team.name], end_indices[team.name] + 1, day, day + 1,
                                   config.MEAN_FORMAT['weekends']['rgb'],
                                   config.MEAN_FORMAT['weekends']['size'])

    def _update_team_formats(self, sheet_id: str, team: Team, context_indices: dict) -> list:
        """
        Задает форматы внутри комнады.
        :param sheet_id: id листа;
        :param team: модель команды в который меняем формат;
        :param context_indices: основные индексы хранящиеся в контексте;
        """
        count_columns = context_indices['count_columns']
        start = context_indices['start_teams_indices']
        end = context_indices['end_teams_indices']
        format_team_name = team.name if team.name in config.MEAN_FORMAT else 'default_team'

        return [self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, 0, 1),
                self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, count_columns, count_columns + 1),
                self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, count_columns + 2,
                                    count_columns + 3),
                self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, count_columns + 3,
                                    count_columns + 4),
                self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, count_columns + 4,
                                    count_columns + 5),
                self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, count_columns + 5,
                                    count_columns + 6),
                self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, count_columns + 6,
                                    count_columns + 7),
                self.gs.merge_cells(sheet_id, start[team.name], start[team.name] + 2, count_columns + 7,
                                    count_columns + 8),
                self.gs.format_cell(sheet_id, start[team.name], start[team.name] + 2, 0, 1,
                                    config.MEAN_FORMAT[format_team_name]['rgb'],
                                    config.MEAN_FORMAT[format_team_name]['size'],
                                    config.MEAN_FORMAT[format_team_name]['bold'],
                                    config.MEAN_FORMAT[format_team_name]['italic'], 'BOTTOM'),
                self.gs.format_cell(sheet_id, start[team.name], start[team.name] + 2, count_columns + 1,
                                    count_columns + 2,
                                    config.MEAN_FORMAT['norma_hours']['rgb'],
                                    config.MEAN_FORMAT['norma_hours']['size']),
                self.gs.draw_borders(sheet_id, start[team.name], end[team.name] + 1, 0, count_columns + 1, 1)]

    def group_format_requests(self, sheet_id: str, teams: list, context_indices: dict) -> list:
        """
        Формирует запрос изменения формата таблицы.
        :param sheet_id: id листа;
        :param teams: модели команд;
        :param context_indices: основные индексы хранящиеся в контексте;
        """
        request = self._update_main_formats(sheet_id, context_indices['count_columns'],
                                            context_indices['end_teams_indices'])

        for team in teams:
            team_format = self._update_team_formats(sheet_id, team, context_indices)

            persons = sorted(team.persons.all(), key=lambda p: (p.person_priority, p.last_name, p.first_name))
            for i, person in enumerate(persons):  # Настроить формат специалистов
                person_index = context_indices['start_teams_indices'][team.name] + i * 2 + 2
                person_format = self._update_person_format(sheet_id, person, person_index,
                                                           context_indices['count_columns'])
                team_format.insert(0, person_format)

            for day in self.context_grouper.weekends_indices:  # Раскрасить выходные дни
                team_format.insert(0, self._update_weekends_format(sheet_id, team, day,
                                                                   context_indices['start_teams_indices'],
                                                                   context_indices['end_teams_indices']))
            request.extend(team_format)

        return request


def get_key_by_value(dict_data: dict, value: str) -> str:
    """ Возвращает ключ словаря по его уникальному значению """
    for key in dict_data:
        if dict_data[key] == value:
            return key


def collect_configurations(form_data: dict) -> dict:
    """
    Возвращает словарь с основными конфигурационными данными.
    :param form_data: данные из формы;
    """
    date = form_data['date'].split('-')
    days_in_month = monthrange(int(date[0]), int(date[1]))[1]
    template_spreadsheet_id = get_key_by_value(config.GOOGLE_SHEETS_ADDRESS['Шаблон'], form_data['google_sheet_name'])

    get_wishes = False
    if form_data['get_wishes']:
        get_wishes = True

    return {'year': int(date[0]), 'month': int(date[1]), 'norma_hours': form_data['norma_hours'],
            'days_in_month': days_in_month, 'get_wishes': get_wishes, 'holidays': form_data['holidays'],
            'excepted_holidays': form_data['excepted_holidays'],
            'template_spreadsheet_id': template_spreadsheet_id,
            'teams': form_data['teams']}


def open_template(form_data: dict):
    """ Функция создает лист шаблона, если такой уже есть, то перезаписывает его """
    spreadsheet_id = form_data['template_spreadsheet_id']
    title = f'{form_data["month"]}.{form_data["year"]}'

    google_client = google_sheets.GoogleSheetsService()

    try:
        sheet = google_client.add_sheet(spreadsheet_id, title, 1100, 50)
        sheet_id = sheet['sheet_id']
    except errors.HttpError:
        sheet_id = google_client.find_sheet_id_by_title(spreadsheet_id, title)

    template_writer = TemplateWriter(form_data, google_client)
    teams = [team for team in Team.objects.all() if team.name in form_data['teams']]
    context = template_writer.context_grouper.context_with_info_columns(teams)
    google_client.write_in_sheet(spreadsheet_id, f'{title}!A1:AT1100', context)

    context_indices = template_writer.context_grouper.get_context_indices(context, teams)
    format_data = template_writer.group_format_requests(sheet_id, teams, context_indices)
    google_client.requests_constructor(spreadsheet_id, format_data)
    return f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}'

# Добавить сбор пожеланий
# Оживить форму, отдавать ей ответ
