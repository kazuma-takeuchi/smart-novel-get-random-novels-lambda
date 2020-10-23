from datetime import datetime


def validate_date_text(date_text: str, format_text: str = '%Y-%m-%d') -> None:
    try:
        datetime.strptime(date_text, format_text)
        return True
    except ValueError:
        raise ValueError(
            "Incorrect data format, should be {format_text}, input_date:{date_text}".format(
                format_text=format_text,
                date_text=date_text
            ))
