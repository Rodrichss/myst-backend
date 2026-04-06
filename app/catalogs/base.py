from app.utils.base_normalizer import normalize_text

class BaseCatalog:

    MAP = {}

    @classmethod
    def get_value(cls, label):
        if not label:
            return None

        normalized = normalize_text(label)
        return cls.__get_reverse_map().get(normalized)

    @classmethod
    def __get_reverse_map(cls):
        if not hasattr(cls, "_reverse_map"):
            cls._reverse_map = {
                normalize_text(v): k for k, v in cls.MAP.items()
            }
        return cls._reverse_map