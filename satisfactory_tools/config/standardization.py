import re
from dataclasses import dataclass

CLASSNAME_KEYS = ["mClassName", "ClassName"]
DISPLAYNAME_KEY = "mDisplayName"
DURATION_KEY = "mManufacturingDuration"

CYCLES_PER_MINUTE = 60

def standardize(value: str) -> str:
    return "_".join(value.replace("-", "_").replace(":", "").replace(")", "").replace("(", "").split()).title()


def get_class_name(value: str) -> str:
    native_class_pattern = r".*\.(\w+)'?"
    match = re.match(native_class_pattern, value)

    if match is None:
        raise Exception("No class name found.")

    return match.group(1)


@dataclass(frozen=True)
class ConfigData:
    class_name: str
    display_name: str

