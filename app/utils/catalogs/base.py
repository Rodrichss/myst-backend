class BaseCatalog:

    MAP = {}

    @classmethod
    def get_label(cls, value):
        return cls.MAP.get(value)

    @classmethod
    def get_value(cls, label):
        if not label:
            return None
        return cls.__get_reverse_map().get(label.lower())

    @classmethod
    def is_valid(cls, value):
        return value in cls.MAP

    @classmethod
    def validate_list(cls, values: list[str]):
        for v in values:
            if v not in cls.MAP:
                raise ValueError(f"Invalid value: {v}")

    @classmethod
    def serialize(cls, values: list[str]) -> str:
        cls.validate_list(values)
        return ",".join(values)

    @classmethod
    def deserialize(cls, value: str) -> list[str]:
        return value.split(",") if value else []

    @classmethod
    def __get_reverse_map(cls):
        if not hasattr(cls, "_reverse_map"):
            cls._reverse_map = {v.lower(): k for k, v in cls.MAP.items()}
        return cls._reverse_map