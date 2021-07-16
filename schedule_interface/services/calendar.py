from datetime import datetime


def get_weekday(year: int, month: int, day: int) -> str:
    """ Получает день недели по заданному дню """
    month = f'0{month}' if len(str(month)) < 2 else month
    day = f'0{day}' if len(str(day)) < 2 else day
    date = f'{year}{month}{day}'
    week_day = datetime.strptime(date, '%Y%m%d')
    return week_day.isoweekday()


def month_days_template(year: int, month: int, days_in_month: int) -> dict:
    """ Создает шаблон для печати календарных дней и их
        дней недели """
    days = [str(day + 1) for day in range(days_in_month)]
    days.insert(0, '')

    weekdays_format = ['ISO Week days start from 1',
                       'пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    weekdays = [weekdays_format[get_weekday(year, month, day + 1)] for day in range(days_in_month)]
    weekdays.insert(0, '')

    return {'days': days, 'weekdays': weekdays}
