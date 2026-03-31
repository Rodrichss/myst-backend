class WaterHelper:
    @staticmethod
    def to_label(value: float):
        if value is None:
            return None
        if value < 1:
            return "Bajo"
        elif value < 2:
            return "Adecuado"
        else:
            return "Alto"