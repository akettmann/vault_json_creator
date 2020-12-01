import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from ..enums import CardFields, CardType, Keywords


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
    tooltipcard: str
    upgradetags: Optional[List[int]] = Field(default_factory=list)
    hidden: bool
    tooltipcardupgrade: str
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
    crarity: int
    keywords: List[Keywords]

    @validator("keywords")
    def convert_to_enum_name(cls, v):
        if isinstance(v, list):
            return [x.name.capitalize() for x in v]
        return v

    @validator("ctype")
    def convert_to_single_enum_name(cls, v: CardType):
        return v.name.capitalize()


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
