def round_to_10_up(value_mm: float) -> float:
    value_cm = value_mm / 10
    remainder = value_cm % 10
    if remainder == 0:
        return value_cm
    return value_cm + (10 - remainder)
