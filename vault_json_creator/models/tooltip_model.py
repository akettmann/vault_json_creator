from typing import Any, Dict, List
import re

from pydantic import BaseModel, root_validator, validator

from ..enums import TooltipFields


class Tooltip(BaseModel):
    _fix_whitespace_re = re.compile(r" {2,}")
    name: str
    description: str

    @root_validator(pre=True)
    def convert_keys_to_names(cls, values: Dict[str, Any]):
        # Tooltips are backwards from the way the cards are defined
        return {TooltipFields(int(k)).name: v for k, v in values.items()}

    @validator("description")
    def remove_newlines(cls, value: str):
        desc = value.replace("\n", " ")
        return cls._fix_whitespace_re.sub(" ", desc)


class AllTips(BaseModel):
    tips: List[Tooltip]

    @validator("tips")
    def strip_empty_tips(cls, value: List[Tooltip]):
        return list(
            filter(
                lambda x: False if x.name == "0.0" and x.description == "0.0" else True,
                value,
            )
        )
