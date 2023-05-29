from service import human_format, format_date, at_handler


class PriceChangeEntry:
    def __init__(self, change_label, change_value):
        self.strEntry = change_label
        if change_value is None:
            self.strPercentage = "N/A"
        else:
            self.strPercentage = f"{change_value:.1f}%"


class GeneralDataEntry:
    def __init__(self, data_emoji, data_type, data_value):
        self.emoji = data_emoji
        self.type = data_type
        if data_value == "N/A" or data_value is None:
            self.value = "N/A"
        else:
            self.value = human_format(float(data_value))


class AtEntry:
    def __init__(self, allt_emoji, allt_symbol, allt_price, allt_percentage, allt_date):
        self.emoji = allt_emoji
        self.symbol = allt_symbol
        if allt_price and "usd" in allt_price:
            self.at_price = human_format(at_handler(allt_price["usd"])) + "$"
        else:
            self.at_price = "N/A"
        if allt_percentage and "usd" in allt_percentage:
            self.at_percentage = human_format(allt_percentage["usd"]) + "%"
        else:
            self.at_percentage = "N/A"
        if allt_date and "usd" in allt_date:
            self.date = format_date(allt_date["usd"])
        else:
            self.date = "N/A"
