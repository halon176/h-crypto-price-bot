from datetime import datetime


def format_date(date_str):
    date_obj = datetime.fromisoformat(date_str[:-1])
    return date_obj.strftime('%m/%y')


def max_column_size(arr):
    return max((len(string) for string in arr))


def at_handler(at):
    if at > 10:
        return round(at)
    elif 0.1 < at < 1:
        return round(at, 2)
    else:
        fep = 0
        at_str = str(at)
        for i in range(3, len(at_str)):
            if at_str[i] != 0:
                fep = i
                break
        return round(at, fep)


def human_format(num) -> str:
    magnitude = 0
    suffixes = ['', 'K', 'M', 'B', 'T']
    max_suffix_index = len(suffixes) - 1

    while abs(num) >= 1000 and magnitude < max_suffix_index:
        magnitude += 1
        num /= 1000.0

    num = float('{:.3g}'.format(num))
    additional_digits = max(int(magnitude - max_suffix_index), 0)

    formatted_num = '{:f}'.format(num).rstrip('0').rstrip('.')

    formatted_num += '0' * additional_digits

    return '{}{}'.format(formatted_num, suffixes[magnitude])
