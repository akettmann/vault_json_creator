from enum import IntEnum


class CardFields(IntEnum):
    cnumber = 0
    cname = 1
    ctype = 2
    cdesc = 3
    cenergy = 4
    cenergy_upgrade = 5
    crarity = 6
    ccardart = 7
    cattacktype = 8
    ceffect = 9
    cbasedamage = 10
    csecondbasedamage = 11
    ctarget = 12
    cexpel = 13
    tags = 14
    slots = 15
    keywords = 16
    upgrade = 17
    cdesc_upgrade = 18
    cbasedamage_upgrade = 19
    csecondbasedamage_upgrade = 20
    tooltipcard = 21
    upgradetags = 22
    hidden = 23
    tooltipcardupgrade = 24
    mastery = 25
    basedamagepercent = 26
    upgradedamagepercent = 27
    cexpel_upgrade = 28
    damagerepeat = 29
    damagerepeat_upgrade = 30
    firstdamagetype = 31
    seconddamagetype = 32


class CardType(IntEnum):
    attack = 0
    aoe = 1
    ability = 2
    magictarget = 3
    wound = 4
    bane = 5
    daze = 6
    temp = 7
    gem = 8
    heal = 9
    sanity = 10
    condition = 11
    sinner = 12
    booster = 13
    bleed = 14
    ignorefort = 15
    malediction = 16
    buff = 17
    item = 18
    weakness = 19
    direct = 20
    curse = 21
    futurestrike = 22
    spiritfocus = 23


class Rarity(IntEnum):
    rare = 2
    uncommon = 3
    common = 4
    gempack = 5
    item = 10
    weakness = 11
    secret = 13
