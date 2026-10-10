from enum import StrEnum


class DeviceType(StrEnum):
    """Type of the hazard sensor."""
    CO = 'co'                    # угарный газ, ppm
    CO2 = 'co2'                  # углекислый газ, ppm
    METHANE = 'methane'          # горючий газ, % НКПР
    SMOKE = 'smoke'              # задымление
    TEMPERATURE = 'temperature'  # температура, °C
    RADIATION = 'radiation'      # мощность дозы, мкЗв/ч


class AlertLevel(StrEnum):
    """Level of the alert, a higher level is more dangerous."""
    LEVEL_1 = 'level_1'
    LEVEL_2 = 'level_2'
    LEVEL_3 = 'level_3'
    LEVEL_4 = 'level_4'
