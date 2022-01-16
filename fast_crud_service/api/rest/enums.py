from enum import Enum


class TokenType(str, Enum):
    bearer = "bearer"


class DBStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class PasswordPolicyStrength(str, Enum):
    min = "min"
    max = "max"


class DeviceState(str, Enum):
    active = "active"
    inactive = "inactive"
    discontinued = "discontinued"


class Computer(str, Enum):
    raspberry_pi_4 = "raspberry_pi_4"


class Camera(str, Enum):
    raspberry_v2 = "raspberry_v2"
    arducam_imx477_r = "arducam_imx477_r"


class DeviceDeliveryType(str, Enum):
    loan = "loan"
    sale = "sale"
    relacement = "replacement"


class Computation(str, Enum):
    ndvi = "ndvi"
    plants_counter = "plants_counter"
    weed_detection = "weed_detection"
