from datetime import datetime


def format_date(date_str):
    date_obj = datetime.fromisoformat(date_str[:-1])
    return date_obj.strftime('%m/%Y')
