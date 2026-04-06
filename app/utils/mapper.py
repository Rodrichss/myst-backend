from app.utils.base_normalizer import normalize_text

# Mapper para catálogos
def map_to_catalog(value: str | list | None, catalog_class, multiple=False):
    if not value:
        return None

    # soportar lista o string
    if isinstance(value, list):
        values = value
    elif multiple:
        values = [v.strip() for v in value.split(",")]
    else:
        values = [value]

    result = []

    for v in values:

        if not isinstance(v, str):
            continue

        v_clean = v.strip().lower()

        # match directo
        for key in catalog_class.MAP:
            if key.lower() == v_clean:
                result.append(key)
                break
        else:
            # intentar por label
            normalized = normalize_text(v_clean)
            key = catalog_class.get_value(normalized)

            if key:
                result.append(key)

    if not result:
        return None

    return ",".join(result) if multiple else result[0]

# Mapper para enums
def map_to_enum(value: str | None, enum_class):
    if value is None:
        return None

    # ya es int → validar que exista
    if isinstance(value, int):
        if value in enum_class.MAP:
            return value
        return None

    # string → normalizar
    if isinstance(value, str):
        normalized = normalize_text(value)
        return enum_class.REVERSE_MAP.get(normalized)

    return None