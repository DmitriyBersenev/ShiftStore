import string


def excel_cells() -> list:
    """
    Формирует буквенный диапозон ячеек эксель.
    :return: ['A', 'B', 'C', ..., 'AA', 'AB', ...]
    """
    alphabet = string.ascii_uppercase
    return [liter for liter in alphabet] + [alphabet[0] + liter for index, liter in enumerate(alphabet)]


class ExcelFormula:
    """ Функции для создания формул эксель """

    def __init__(self):
        self.alphabet = excel_cells()

    def sum(self, start_row: int, end_row: int, start_col: int, end_col: int) -> str:
        """ Формула подсчета суммы """
        return f'=СУММ({self.alphabet[start_col]}{start_row + 1}:{self.alphabet[end_col]}{end_row + 1})'

    def count_shifts(self, start_row: int, end_row: int, start_col: int, end_col: int, shift: str) -> str:
        """
        Формула подсчета количества смен в зависимости от ее типа.
        :param start_row: стартовый ряд диапазона;
        :param end_row: конечный ряд диапазона;
        :param start_col: стартовая колонка диапазона;
        :param end_col: конечная колонка диапазона;
        :param shift: значение, которое будем считать.
        """
        cells_range = f'{self.alphabet[start_col]}{start_row + 1}:{self.alphabet[end_col]}{end_row + 1}'
        return f'=СЧЁТЕСЛИ({cells_range};"{shift}")'

    def calculate_additional_hours(self, row: int, col: int) -> str:
        """
        Формула форматирования дополнительных часов.
        :param row: ряд ячеек;
        :param col: колонки ячеек;
        """
        add_hours = f'{self.alphabet[col]}{row}'
        teach_hours = f'{self.alphabet[col + 1]}{row}'
        check = f'OR(ISNUMBER({add_hours});ISBLANK({add_hours}))'

        left = f'=CONCATENATE(IF({check}; {add_hours}; LEFT({add_hours}; FIND("н";{add_hours}) - 2)) + {teach_hours};'
        right = f'" н"; IF({check}; 0; MID({add_hours}; FIND("н";{add_hours}) + 1; 3)))'
        return left + right

    def person_max_hours(self, row: int, col: int) -> str:
        """
        Формула подсчета максимально допустимого количеста часов.
        :param row: ряд ячеек;
        :param col: колонки ячеек;
        """
        general_hours = f'${self.alphabet[col]}$2'
        person_hours = f'{self.alphabet[col]}{row}'
        general_result = f'ROUND({general_hours} * 0,15 + {general_hours})'
        person_result = f'ROUND({person_hours} * 0,15 + {person_hours})'
        return f'=IF({person_hours} = ""; {general_result}; {person_result})'
