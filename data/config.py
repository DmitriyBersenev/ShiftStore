import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEETS_TOKEN = str(os.getenv('GOOGLE_SHEETS_TOKEN'))

GOOGLE_SHEETS_ADDRESS = {'График': {'11sTO-45x2J4UPGAFOrrayf-wwvz28fYsV0UekY9Qbt0': [''],
                                    '1IHecmuCg9hhzRW5IiikCUaB5aEWLzVOPL4SubV_veH0': ['']},
                         'График отпусков': {'1Tlizyx0kCZvAY_9WrDnFaXM0fC6geg9kMfvHnxDVvy8': (
                             'Телефон', 'Чат', 'Фокусные круги')},
                         'Шаблон': {'1PZT1_GqBAc9UWqnpi_le4jA1bTHH-lUTLvpHqmUgTxA': 'Экспертный офис',
                                    '1ixn705dWAhXergqgJ9ruYNRv-6aOVXgy-FcYberovbk': 'Фокусные круги'}}

TEMPLATE_NOTATIONS = {'Формальный отпуск': 'фо',
                      'Отпуск': 'о',
                      'Отгул': 'от',
                      'Больничный': 'б',
                      'Декрет': 'д'}

MEAN_FORMAT = {'default': {'rgb': [1, 1, 1, 0], 'size': 9, 'bold': False, 'italic': False},
               'weekends': {'rgb': [0.8509804, 0.8509804, 0.8509804, 0], 'size': 9, 'bold': False, 'italic': False},
               'holidays': {'rgb': [0.6745098, 0.7254902, 0.7921569, 0], 'size': 9, 'bold': False, 'italic': False},
               'norma_hours': {'rgb': [0, 1, 0, 0], 'size': 9, 'bold': False, 'italic': False},
               'add_hours': {'rgb': [0.9372549, 0.972549, 1, 0], 'size': 9, 'bold': False, 'italic': False},

               'Эксперты по процессам': {'rgb': [0, 0.6901961, 0.9411765, 0], 'size': 11, 'bold': True,
                                         'italic': True},
               'Соцсети': {'rgb': [1, 1, 0, 0], 'size': 11, 'bold': True, 'italic': True},
               'default_team': {'rgb': [1, 1, 1, 0], 'size': 11, 'bold': True, 'italic': True}}
