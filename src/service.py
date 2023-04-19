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


def k_handler(num):
    num_str = str(num)
    if len(num_str.split('.')[0]) > 3:
        num_str = num_str.split('.')[0][:2] + 'k'
    else:
        if abs(num) < 10:
            num_str = "{:.2f}".format(num)
        else:
            num_str = "{:.0f}".format(num)
    return num_str
