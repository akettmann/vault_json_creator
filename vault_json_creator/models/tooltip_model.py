from typing import Any, Dict

from pydantic import BaseModel, root_validator

from ..enums import TooltipFields


class Tooltip(BaseModel):
    name: str
    description: str

    @root_validator(pre=True)
    def convert_keys_to_names(cls, values: Dict[str, Any]):
        # Tooltips seem to be backwards from the way the cards are defined, not sure if
        # this will read right until I get a sample
        return {TooltipFields(int(v)).name: k for k, v in values.items()}
