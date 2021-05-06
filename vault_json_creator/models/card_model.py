import re
from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, Union

from pydantic import BaseModel, Field, root_validator, validator

from ..enums import CardFields, CardType, ClassNames, Keywords, Rarity
from .model_utils import convert_to_enum_name

if TYPE_CHECKING:
    from pydantic.fields import ModelField


class Card(BaseModel):
    cnumber: int
    cname: str
    ctype: CardType
    cbasedamage: int
    csecondbasedamage: int
    cenergy: Union[int, Literal["X"]]
    cenergy_upgrade: Union[int, Literal["X"]]
    crarity: int
    ccardart: str
    cattacktype: str
    ceffect: str
    ctarget: int
    cexpel: str
    tags: Optional[List[int]] = Field(default_factory=list)
    slots: str
    keywords: Optional[List[Keywords]] = Field(default_factory=list)
    upgrade: str
    cbasedamage_upgrade: int
    csecondbasedamage_upgrade: int
    cdesc: str
    cdesc_upgrade: str
    tooltipcard: Any
    upgradetags: Optional[List[int]] = Field(default_factory=list)
    hidden: bool
    tooltipcardupgrade: Any
    mastery: str
    basedamagepercent: str
    upgradedamagepercent: str
    cexpel_upgrade: str
    damagerepeat: str
    damagerepeat_upgrade: str
    firstdamagetype: str
    seconddamagetype: str

    _remove_bracket_re = re.compile(r"\[/?[kuid]?]")
    _replace_base_damage = re.compile(r"#[ad]")
    _replace_second_base_damage = re.compile(r"@[ad]")

    @root_validator(pre=True)
    def convert_keys_to_names(cls, values: Dict[str, Any]):
        new_vals = {}
        for k, v in values.items():
            try:
                name = CardFields(int(k)).name
            except ValueError:
                # Ignoring new enums until I am told otherwise
                continue
            new_vals[name] = v
        return new_vals

    @validator("keywords", "tags", "upgradetags", pre=True)
    def check_for_empty(cls, v):
        """ This is to deal with the slightly derpy json output from GMS2"""
        if isinstance(v, float):
            return list()
        return v

    @validator("cdesc", "cdesc_upgrade")
    def _format_description(cls, desc, values, field: "ModelField"):
        if field.name == "cdesc":
            base_dmg = str(values.get("cbasedamage"))
            second_base_dmg = str(values.get("csecondbasedamage"))
        else:
            base_dmg = str(values.get("cbasedamage_upgrade"))
            second_base_dmg = str(values.get("csecondbasedamage_upgrade"))
        desc = cls._remove_bracket_re.sub("", desc)
        desc = desc.replace("\n", " ")
        desc = cls._replace_base_damage.sub(base_dmg, desc)
        desc = cls._replace_second_base_damage.sub(second_base_dmg, desc)
        desc = desc.replace("$", "X")
        return desc

    @validator("cenergy", "cenergy_upgrade")
    def _replace_x_cost_energy_cost(cls, value: int):
        # Josh is using 99 for the cost to signify X costs, so changing the value to be
        # "X" here
        if value == 99:
            return "X"

        return value

    @property
    def is_public(self):
        if self.hidden or (self.keywords and Keywords.deathknight in self.keywords):
            return False
        return True

    def as_public_card(self):
        return PublicCard(**self.dict())

    def __repr__(self):
        return f"Card({self.cname})"

    def __str__(self):
        return self.__repr__()


class PublicCard(BaseModel):
    cnumber: int
    cname: str
    ctype: CardType
    cdesc: str
    cdesc_upgrade: str
    cenergy: Union[int, Literal["X"]]
    cenergy_upgrade: Union[int, Literal["X"]]
    crarity: Rarity
    keywords: List[Keywords]

    @validator("keywords", each_item=True)
    def fix_character_names(cls, v: Keywords):
        if v.name in ClassNames.__members__.keys():
            return ClassNames[v.name].value
        return v

    convert_enums_to_str = validator(
        "keywords", "crarity", each_item=True, allow_reuse=True
    )(convert_to_enum_name)


class AllPublicCards(BaseModel):
    cards: List[PublicCard]

    @root_validator
    def sort_card_list(cls, values):
        values["cards"].sort(key=lambda x: x.cnumber)
        return values


class AllCards(BaseModel):
    cards: List[Card]

    @root_validator
    def remove_invalid_cards(cls, values):
        cards = values.get("cards")
        cards = list(filter(lambda x: x.is_public, cards))
        cards = list(filter(lambda x: not x.cname == "0.0", cards))
        values["cards"] = cards
        return values

    def make_public_cards(self) -> AllPublicCards:
        # noinspection PyTypeChecker
        return AllPublicCards(cards=self.cards)
