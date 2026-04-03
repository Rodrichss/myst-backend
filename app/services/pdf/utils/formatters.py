def clean(value): #safe_text
    if value in [None, "", "string", "null", "None"]:
        return "No especificado"
    return str(value)

def bool_text(value):
    if value is None:
        return "No especificado"
    return "Sí" if value else "No"

def format_full_name(user, history):
    parts = [
        history.last_name,
        history.second_last_name,
        user.name
    ]

    # clean each part and filter out empty ones
    clean_parts = [
        p for p in parts
        if p not in [None, "", "string", "null", "None"]
    ]

    if not clean_parts:
        return "No especificado"

    return " ".join(clean_parts)

def format_list(values):
    if not values:
        return "Ninguna"

    clean_values = [clean(v) for v in values]

    if not clean_values:
        return "Ninguna"

    return ", ".join(clean_values)

def format_abortions(value):
    if value is None:
        return "No especificado"
    elif value == 0:
        return "No"
    else:
        return f"Sí, {value} aborto(s)"