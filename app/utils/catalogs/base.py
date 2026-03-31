class BaseCatalog:

    MAP = {}

    @classmethod
    def get_label(cls, value):
        return cls.MAP.get(value)

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