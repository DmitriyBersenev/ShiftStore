from calendar import monthrange
from api.google_sheets import google_sheets
from data import config



class PersonsVacation:

    def __init__(self, *args, **kwargs):
        self.vacation_address = config.GOOGLE_SHEETS_ADDRESS['График отпусков']
        self.list_range = 'A1:NE1000'


    def get_vacation_data(self):
        """
        Получает все листы гугл таблицы с отпусками специалистов.
        :return:
        """
        google_sheets_client = google_sheets.GoogleSheetsService()

        for vacation_list in self.vacation_address[self.vacation_address]:
            list_range = f'{vacation_list}!{self.list_range}'
            list_data = google_sheets_client.get_spreadsheet(self.vacation_address, list_range)['values']
            print('_____________________________________________________________________')
            print(list_data)
