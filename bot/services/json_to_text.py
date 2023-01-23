def convert_to_text_history(json_data: dict) -> str:
    history_html = ""
    for field, value in json_data.items():
        history_html += f"{field.capitalize()}: {value}\n"

    return history_html


def convert_to_text_position(json_data: dict) -> str:
    position_html = ""
    for field, value in json_data.items():
        position_html += f"{field.capitalize()}: {value}\n"

    return position_html
