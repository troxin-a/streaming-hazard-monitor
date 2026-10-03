from enum import StrEnum


class DeviceType(StrEnum):
    """Type of the hazard sensor."""
    CO = 'co'                    # угарный газ, ppm
    CO2 = 'co2'                  # углекислый газ, ppm
    METHANE = 'methane'          # горючий газ, % НКПР
    SMOKE = 'smoke'              # задымление
    TEMPERATURE = 'temperature'  # температура, °C
    RADIATION = 'radiation'      # мощность дозы, мкЗв/ч
