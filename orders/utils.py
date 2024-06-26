import datetime


def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%S")
    return f"{current_datetime}{str(pk)}"
