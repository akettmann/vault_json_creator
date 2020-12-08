from enum import Enum


def convert_to_enum_name(v):
    if isinstance(v, Enum):
        return v.name.capitalize()
    return v
