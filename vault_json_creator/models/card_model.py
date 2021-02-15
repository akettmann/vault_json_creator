import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from ..enums import CardFields, CardType, ClassNames, Keywords, Rarity
from .model_utils import convert_to_enum_name


class Card(BaseModel):
    cnumber: int
    cname: str
    ctype: CardType
    cbasedamage: int
    csecondbasedamage: int
    cdesc: str
    cenergy: int
    cenergy_upgrade: int
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
    cdesc_upgrade: str
    cbasedamage_upgrade: int
    csecondbasedamage_upgrade: int
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
        return {CardFields(int(k)).name: v for k, v in values.items()}

    @validator("keywords", "tags", "upgradetags", pre=True)
    def check_for_empty(cls, v):
        """ This is to deal with the slightly derpy json output from GMS2"""
        if isinstance(v, float):
            return list()
        return v

    @validator("cdesc", "cdesc_upgrade")
    def _format_description(cls, desc, values):
        desc = cls._remove_bracket_re.sub("", desc)
        desc = desc.replace("\n", " ")
        desc = cls._replace_base_damage.sub(str(values.get("cbasedamage")), desc)
        desc = cls._replace_second_base_damage.sub(
            str(values.get("csecondbasedamage")), desc
        )
        desc = desc.replace("$", "X")
        return desc

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
    cenergy: int
    cenergy_upgrade: int
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
