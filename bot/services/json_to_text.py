def convert_to_text_order(json_data: dict) -> str:
    order_html = ""
    for field, value in json_data.items():
        order_html += f"{field.capitalize()}: {value}\n"

    return order_html


def convert_to_text_position(json_data: dict) -> str:
    position_html = ""
    for field, value in json_data.items():
        position_html += f"{field.capitalize()}: {value}\n"

    return position_html
