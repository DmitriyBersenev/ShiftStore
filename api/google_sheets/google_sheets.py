from datetime import datetime, timedelta

import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from schedule.models import Shift
from data import config


class GoogleSheetsService:
    def __init__(self):
        self.service = self.spreadsheet_service()

    @staticmethod
    def spreadsheet_service():
        """ Создается клиент google spreadsheet для работы с таблицами """
        credentials_file = config.GOOGLE_SHEETS_TOKEN
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        http_auth = credentials.authorize(httplib2.Http())
        return discovery.build('sheets', 'v4', http=http_auth)

    def get_spreadsheet(self, spreadsheet_id: str, range_list: str, dimension: str = 'ROWS') -> dict:
        """
        Получает данные листа выбранной таблицы.
        :param spreadsheet_id: id таблицы
        :param range_list: диапазон листа, прописывается в формате Лист!A1:B3
        :param dimension: подход получения данных. По рядам или по колонкам
        """
        spreadsheet = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_list,
            majorDimension=dimension
        ).execute()
        return spreadsheet

    def add_sheet(self, spreadsheet_id: str, title: str, rows: int, columns: int) -> dict:
        """
        Создает новый лист в выбранной таблице.
        :param spreadsheet_id: id таблицы
        :param title: название листа
        :param rows: количество рядов
        :param columns: количество колонок
        """
        spreadsheet = self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={'requests': [{
                'addSheet': {
                    'properties': {
                        'title': title,
                        'gridProperties': {
                            'rowCount': rows,
                            'columnCount': columns}}}}]}).execute()
        sheet = spreadsheet['replies'][0]['addSheet']['properties']
        return {'sheet_id': sheet['sheetId'], 'title': sheet['title']}

    def find_sheet_id_by_title(self, spreadsheet_id: str, title: str) -> int:
        """
        Находит id листа по его названию и id таблицы;
        :param spreadsheet_id: id таблицы;
        :param title: имя листа;
        """
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        properties = spreadsheet.get('sheets')

        for item in properties:
            if item.get("properties").get('title') == title:
                return item.get("properties").get('sheetId')

    def write_in_sheet(self, spreadsheet_id: str, range_list: str, context: list, dimension: str = 'ROWS') -> dict:
        """
        Записать данные в таблицу.
        :param spreadsheet_id: id таблицы
        :param range_list: диапазон для записи
        :param context: записываемые данные. Формат [[...], [...]]
        :param dimension: направление записи. Либо ROWS, либо COLUMNS.
        """
        spreadsheet = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED',
                  'data': [
                      {'range': range_list,
                       'majorDimension': dimension,
                       'values': context}]
                  }).execute()
        return spreadsheet

    def requests_constructor(self, spreadsheet_id: str, requests: list) -> dict:
        """
        Формирует общий запрос для массового апдейта таблицы.
        :param spreadsheet_id: id таблицы
        :param requests: собранный апдейт в формате [[...], [...]]
        """
        results = self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
            'requests': requests}).execute()
        return results

    @staticmethod
    def cell_size(sheet_id: str, start: int, end: int, size: int, dimension='COLUMNS'):
        """ Изменяет размер ячеек. Размер в пикселях """
        requests = {'updateDimensionProperties': {
            'range': {'sheetId': sheet_id,
                      'dimension': dimension,
                      'startIndex': start,
                      'endIndex': end},
            'properties': {'pixelSize': size},
            'fields': 'pixelSize'}}
        return requests

    @staticmethod
    def merge_cells(sheet_id: str, start_row: int, end_row: int, start_col: int, end_col: int):
        """ Объединяет заданные ячейки """
        requests = {'mergeCells': {'range': {
            'sheetId': sheet_id,
            'startRowIndex': start_row,
            'endRowIndex': end_row,
            'startColumnIndex': start_col,
            'endColumnIndex': end_col},
            'mergeType': 'MERGE_ALL'}}
        return requests

    @staticmethod
    def format_cell(sheet_id: str, start_row: int, end_row: int, start_col: int, end_col: int, rgba: list, size: int,
                    bold: bool = False, italic: bool = False, vertical_alignment: str = 'MIDDLE'):
        """
        Форматирует ячейку по определенному стилю.
        :param sheet_id: id листа
        :param start_row: первый ряд
        :param end_row: последний ряд
        :param start_col: первая колонка
        :param end_col: поледняя колонка
        :param rgba: цвет заливки ['red', 'green', 'blue', 'alfa']
        :param size: размер текста
        :param bold: толщина текста
        :param italic: стиль текста
        :param vertical_alignment: выравнивание текста
        """
        requests = {'repeatCell': {
            'cell': {
                'userEnteredFormat': {
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': vertical_alignment,
                    'wrapStrategy': 'WRAP',
                    'backgroundColor': {
                        'red': rgba[0],
                        'green': rgba[1],
                        'blue': rgba[2],
                        'alpha': rgba[3]},
                    'textFormat': {
                        'bold': bold,
                        'italic': italic,
                        'fontSize': size}}},
            'range': {'sheetId': sheet_id,
                      'startRowIndex': start_row,
                      'endRowIndex': end_row,
                      'startColumnIndex': start_col,
                      'endColumnIndex': end_col},
            'fields': 'userEnteredFormat'}}
        return requests

    @staticmethod
    def conditional_formatting(sheet_id: str, start_row: int, end_row: int, start_col: int, end_col: int, text: str,
                               rgba: list):
        """ Создает правила условного форматирования с содержанием определенного текста """
        requests = {'addConditionalFormatRule': {'rule': {'ranges': [
            {'sheetId': sheet_id,
             'startRowIndex': start_row,
             'endRowIndex': end_row,
             'startColumnIndex': start_col,
             'endColumnIndex': end_col}],
            'booleanRule': {'condition': {'type': 'TEXT_CONTAINS',
                                          'values': [{'userEnteredValue': text}]},
                            'format': {'backgroundColor': {
                                'red': rgba[0],
                                'green': rgba[1],
                                'blue': rgba[2],
                                'alpha': rgba[3]}}}},
            'index': 0}}
        return requests

    @staticmethod
    def group_cells(sheet_id: str, start: int, end: int, dimension='ROWS'):
        """ Группирует ячейки по определенному направлению """
        requests = {'addDimensionGroup': {'range': {
            'sheetId': sheet_id,
            'dimension': dimension,
            'startIndex': start,
            'endIndex': end}}}
        return requests

    @staticmethod
    def add_datetime(t1: datetime, t2: datetime, t3: int = 0) -> str:
        """
        Суммирует несколько объектов datetime
        :param t1: Объект datetime, обычно начало смены
        :param t2: Объект datetime, обычно продолжительность смены
        :param t3: Длительность обеда в минутах
        :return:
        """
        time1 = timedelta(hours=t1.hour, minutes=t1.minute)
        time2 = timedelta(hours=t2.hour, minutes=t2.minute)
        time3 = timedelta(hours=0, minutes=t3)
        delta = time1 + time2 + time3
        format_delta = datetime.strptime(str(delta), '%H:%M:%S')
        return format_delta.strftime('%H:%M')

    def render_shifts_for_wishes(self, additional_shifts: list) -> list:
        """
        Создает шаблон для генерации проверки данных в пожеланиях.
        :param additional_shifts: список со строчками смен, которые нужно добавить помимо тех, что есть в модели
        """
        shift_objects = Shift.objects.all()
        shifts = [f'{s.start.strftime("%H:%M")} {self.add_datetime(s.start, s.duration, s.lunch_duration)}'
                  for s in shift_objects]
        all_shift_for_wishes = shifts + additional_shifts
        return [{'userEnteredValue': shift} for shift in all_shift_for_wishes]

    def data_validation(self, sheet_id: str, start_row: int, end_row: int, start_col: int, end_col: int,
                        add_shifts: list):
        """
        Создает правило проверки данных для удобного выбора смен.
        :param sheet_id: id листа
        :param start_row: начало ряда
        :param end_row: конец ряда
        :param start_col: начало колонки
        :param end_col: конец колонки
        :param add_shifts: добавляемые смены в списке [str, str, ...]
        """
        requests = {'setDataValidation': {'range': {
            'sheetId': sheet_id,
            'startRowIndex': start_row,
            'endRowIndex': end_row,
            'startColumnIndex': start_col,
            'endColumnIndex': end_col},
            'rule': {'condition': {'type': 'ONE_OF_LIST',
                                   'values': self.render_shifts_for_wishes(add_shifts)},
                     'strict': True}}}
        return requests

    @staticmethod
    def draw_borders(sheet_id: str, start_row: int, end_row: int, start_col: int, end_col: int, width: int):
        """
        Рисует таблицу по заданным координатам.
        :param sheet_id: id листа
        :param start_row: начальный ряд
        :param end_row: последний ряд
        :param start_col: начальная колонка
        :param end_col: последняя колонка
        :param width: толщина линий
        """
        requests = {'updateBorders': {'range': {
            'sheetId': sheet_id,
            'startRowIndex': start_row,
            'endRowIndex': end_row,
            'startColumnIndex': start_col,
            'endColumnIndex': end_col},
            'bottom': {  # Задаем стиль для верхней границы
                'style': 'SOLID',
                'width': width,
                'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},  # Черный цвет
            'top': {  # Задаем стиль для нижней границы
                'style': 'SOLID',
                'width': width,
                'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
            'left': {  # Задаем стиль для левой границы
                'style': 'SOLID',
                'width': width,
                'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
            'right': {  # Задаем стиль для правой границы
                'style': 'SOLID',
                'width': width,
                'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
            'innerHorizontal': {  # Задаем стиль для внутренних горизонтальных линий
                'style': 'SOLID',
                'width': width,
                'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
            'innerVertical': {  # Задаем стиль для внутренних вертикальных линий
                'style': 'SOLID',
                'width': width,
                'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}}
        }}
        return requests

    def get_cell_data(self, spreadsheet_id: str, range_list: str) -> None:
        """
        Получить все данные ячейки.
        :param spreadsheet_id: id таблицы
        :param range_list: адрес ячейки, обычно в формате Лист!A1:A1
        """
        results = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id,
                                                  ranges=[range_list], includeGridData=True).execute()
        print('Основные данные')
        print(results['properties'])
        print('\nЗначения и раскраска')
        print(results['sheets'][0]['data'][0]['rowData'])
        print('\nВысота ячейки')
        print(results['sheets'][0]['data'][0]['rowMetadata'])
        print('\nШирина ячейки')
        print(results['sheets'][0]['data'][0]['columnMetadata'])

        # get_cell_data('15xiqNCpihS0A-s0qTpu6AdBCLoeVaZPUMV3rn_3e2_U', 'Апрель!A360:A361')
