from datetime import date

INVALID_VALUES = {None, "", "string", "null", "None", "undefined"}

def clean(value): #safe_text
    if value in INVALID_VALUES:
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
        str(p).strip().title()
        for p in parts
        if p not in INVALID_VALUES
    ]
    if not clean_parts:
        return "No especificado"
    return " ".join(clean_parts)

def format_list(values):
    if not values:
        return "Ninguna"
    clean_values = [str(v) for v in values if v not in INVALID_VALUES]
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

def format_stds(value_from_mapped):
    if isinstance(value_from_mapped, list):
        if not value_from_mapped:
            return "Ninguna"
        # Convierte ["a", "b"] en "a, b"
        return ", ".join(value_from_mapped)
    # Si es un valor simple
    if value_from_mapped in INVALID_VALUES:
        return "Ninguna"
    return str(value_from_mapped)

# dd/mm/yyyy
def format_date(date_val):
    if not date_val:
        return "No especificado"
    if isinstance(date_val, str):
        try:
            date_val = date.fromisoformat(date_val)
        except ValueError:
            return date_val
    return date_val.strftime("%d/%m/%Y")

# dd/mm/yyyy
def format_date_pdf(date_val):
    if not date_val:
        return "No especificado"
    if isinstance(date_val, str):
        try:
            date_val = date.fromisoformat(date_val)
        except ValueError:
            return date_val
    return date_val.strftime("%d-%m-%Y")