from calendar import monthrange
from api.google_sheets import google_sheets
from data import config
from structure.services import db_commands
from structure import models


class PersonsVacation:

    def __init__(self):
        self.vacation_address = config.GOOGLE_SHEETS_ADDRESS['График отпусков']
        self.list_range = 'A1:NE1000'

    def _get_data_from_google_sheets(self) -> list:
        """ Получает все листы гугл таблицы с отпусками специалистов """
        google_sheets_client = google_sheets.GoogleSheetsService()

        lists_addresses = [f'{vacation_list}!{self.list_range}' for sheet in self.vacation_address for vacation_list in
                           self.vacation_address[sheet]]  # Получаю диапазоны всех листов таблицы
        sheet_id = [key for key in self.vacation_address.keys()][0]  # Так как id только один, получаю через индекс
        return google_sheets_client.get_spreadsheet_all_lists(sheet_id, lists_addresses)

    def _combine_data_form_lists(self) -> list:
        """ Объединяет листы с отпусками полученные из гуглдокса массовым способом """
        spreadsheet_data = self._get_data_from_google_sheets()
        vacation_data = []
        for list_data in spreadsheet_data['valueRanges']:
            vacation_data.extend(list_data['values'])
        return vacation_data

    @staticmethod
    def _month_indices_range(year: int, month: int) -> dict:
        """
        Возвращает индексы начала и конца месяца из которого получаем данные об отпусках.
        :param year: год;
        :param month: месяц;
        :return: {'start': int, 'end': int}
        """
        start = sum([monthrange(year, month_number)[1] for month_number in range(1, month)])
        end = start + monthrange(year, month)[1] - 1
        return {'start': start, 'end': end}

    @staticmethod
    def _person_holidays_list_in_month(row_data: list, month_indices: dict) -> list:
        """
        Возвращает даты дней отпуска специалиста, отсчет дат начинается с 1, за месяц в пределах индексов месяца.
        :param row_data: полный ряд с данными полученные c листа отпусков в google sheets;
        :param month_indices: индексы начала и конца месяца;

        :return: лист с данными. Если есть данные в ячейке, то в зависимости от индекса будут обозначены
        формальный отпуск - 0, отпуск - 1, отгул - 2, остальные дни месяца без данных будут пустыми.
        Если лист не получилось конвертировать, то возвращает пустой список.
        """
        month_cells = row_data[month_indices['start']: month_indices['end'] + 1]
        for i, cell in enumerate(month_cells):
            if cell != '':
                try:
                    if int(cell) == 0:
                        month_cells[i] = config.TEMPLATE_NOTATIONS['Формальный отпуск']
                    elif int(cell) == 1:
                        month_cells[i] = config.TEMPLATE_NOTATIONS['Отпуск']
                    elif int(cell) == 2:
                        month_cells[i] = config.TEMPLATE_NOTATIONS['Отгул']
                except ValueError:
                    return list()

        return month_cells

    @staticmethod
    def _get_person_name_from_sheet(row_data: list) -> dict:
        """
        Вычленить ФИО из данных ряда полученных в гуглтаблице.
        :param row_data: полный ряд с данными полученные c листа отпусков в google sheets;
        :return: {'last_name': '', 'first_name': '', 'patronymic': ''}
        """
        name_cell = row_data[1]
        split_name = name_cell.split(' ')
        name_title = ('last_name', 'first_name', 'patronymic')
        full_name = {'last_name': '', 'first_name': '', 'patronymic': ''}

        for i, word in enumerate(split_name[:3]):
            full_name[name_title[i]] = word.strip()
        return full_name

    @staticmethod
    def _check_db_persons_in_google_sheets(holidays_data: list, person: models.Person) -> bool:
        """
        Проверяет есть ли специалист заведенный в базе данных в полученном ответе от гугл докса с отпусками
        :param holidays_data: список со всеми подтянувшимися рядами отпусков специалистов;
        :param person: модель специалиста
        :return: возвращает True если все ок, и False если специалист не найден.
        """
        for row in holidays_data:
            name_in_google_sheets = [row['last_name'], row['first_name'], row['patronymic']]
            count_name_parameters = len([word for word in name_in_google_sheets if word])
            if count_name_parameters <= 2:  # Если в гугл таблицах только Фамилия и Имя
                person_name_in_db = f'{person.last_name} {person.first_name}'
                if person_name_in_db == f'{row["last_name"]} {row["first_name"]}':
                    return True
            elif count_name_parameters == 3:  # Если в гугл таблицах Фамилия Имя Отчество
                person_name_in_db = f'{person.last_name} {person.first_name} {person.patronymic}'
                if person_name_in_db == f'{row["last_name"]} {row["first_name"]} {row["patronymic"]}':
                    return True
        return False

    def person_holidays_in_month(self, year: int, month: int, row_data: list) -> dict:
        """
        Возвращает собранный словарь, в котором раздельными аргументами фамилия, имя, отчество и данные по отпуску.
        :param year: год;
        :param month: месяц;
        :param row_data: ряд из гугл таблиц с данными по отпуску
        :return: {last_name: '...', first_name: '...', patronymic: '...', month_holidays: []}
        """
        dict_with_full_name = self._get_person_name_from_sheet(row_data)

        month_indices = self._month_indices_range(year, month)
        month_holidays = self._person_holidays_list_in_month(row_data[2:], month_indices)
        dict_with_full_name['month_holidays'] = month_holidays
        return dict_with_full_name

    def all_persons_holidays_from_google_sheets(self, year: str, month: str) -> list:
        """
        Возвращает список со всеми подтянувшимися рядами отпусков специалистов
        :param year: год;
        :param month: месяц, который хотим посмотреть;
        :return: [{last_name: '...', first_name: '...', patronymic: '...', month_holidays: []}, {...}]
        """
        holidays_data = self._combine_data_form_lists()
        all_holidays_from_google_sheets = []

        for row in holidays_data:
            if row and row[1]:
                all_holidays_from_google_sheets.append(self.person_holidays_in_month(year, month, row))

        return all_holidays_from_google_sheets

    def merge_persons_holidays_with_db(self, year: int, month: int) -> dict:
        """
        Сопостовляет данные по отпускам из google sheets и persons в db.
        :param year: год;
        :param month: месяц, который хотим посмотреть;
        :return: {Person: [данные по отпуску]}
        """
        google_sheets_holidays = self.all_persons_holidays_from_google_sheets(year, month)
        persons_holidays = {}

        for person in google_sheets_holidays:
            db_answer = db_commands.get_person_by_full_name(person['last_name'], person['first_name'],
                                                            person['patronymic'])
            person_object = db_answer[0]
            if person_object:
                persons_holidays[person_object] = person['month_holidays']

        return persons_holidays

    def find_persons_holidays_errors(self, year: int, month: int) -> dict:
        """
        Возвращает ошибки возникшие при объединении пользователей из db и данных полученных из google sheets.
        :param year: год;
        :param month: месяц, который хотим посмотреть;
        :return: {Имя: 'Описание ошибки'}
        """
        google_sheets_holidays = self.all_persons_holidays_from_google_sheets(year, month)
        holidays_error = {}

        for person in google_sheets_holidays:
            db_answer = db_commands.get_person_by_full_name(person['last_name'], person['first_name'],
                                                            person['patronymic'])
            person_db_object = db_answer[0]
            if not person_db_object:  # Проверка, что person найден в db
                error = db_answer[1]
                object_full_name = f'{person["last_name"]} {person["first_name"]} {person["patronymic"]}'.strip()
                holidays_error[object_full_name] = error
            if person_db_object and not person['month_holidays']:  # Проверка, что данные отпуска найдены
                holidays_error[person_db_object.display_full_name()] = 'Not found holidays in google sheets'

        for person in models.Person.objects.all():  # Проверка, что person из db есть в гугл таблице
            if not self._check_db_persons_in_google_sheets(google_sheets_holidays, person):
                holidays_error[person.display_full_name()] = 'Not found person in google sheets'

        return holidays_error
