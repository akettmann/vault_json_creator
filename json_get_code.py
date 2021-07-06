# %%
import json
from pathlib import Path

dropbox_folder = Path.home() / "Dropbox\_Python\CardData\_2"
src_dir = dropbox_folder / "source"
dest_dir = dropbox_folder / "output"
src_file = src_dir / "create_cards.txt"
src_text = src_file.read_text()
out_file = dest_dir / "create_cards.txt"
out_json = dest_dir / "create_cards.json"
# %%

import re

END_CARD_REGEX = re.compile(r"^i\+\+;$", re.MULTILINE)
MATCH_IN_QUOTES = re.compile(r"\"(.*)\"")
LINE_MATCH = re.compile(
    r"^(?P<subject>global\.CARDDATA\[[ \t]*\#\s*(?P<field>\w+\.\w+)\s*,\s*i]\s*=)\s*(?P<value>[^\r\n;]*)[ \t]*(?P<sc>;?)[ \t]*$",
    re.MULTILINE,
)
assert LINE_MATCH.fullmatch(
    'global.CARDDATA[ # card.cname, i] = json_get(global.LOCALE_WORDS, "cards", "001", "name");'
)
LINE_END_RE = re.compile("\s*;\s*$", re.M)
ALL_WHITESPACE_RE = re.compile("^\s*$")

# %%

cards = END_CARD_REGEX.split(src_text)


# %%


def new_json_get_call(field_name: str, number_str: str, line_match: str):
    return f"""{line_match} json_get(global.LOCALE_WORDS, "cards", "{number_str}", "{field_name}");"""


# %%
keywords = {
    "SPIRITFOCUS": "Shii",
    "FUTURESIGHT": "Vision",
    "RAGE": "Rage",
    "MULTISTRIKE": "Death Strike",
    "FUTURECAST": "Foresight",
    "THRESHOLD": "Threshold",
    "SIPHON": "Siphon",
}
KEYWORD_RE = re.compile(
    r'"[ \t]*\+[ \t]*(?:string\()?(?P<keyword>\w+)(?:\))?[ \t]*\+[ \t]*"', re.UNICODE
)


def replace_keywords(line: str) -> str:
    line_list = list(line)

    while m := KEYWORD_RE.search("".join(line_list)):
        sub_str = "".join(line_list[m.start() : m.end()])
        new_str = KEYWORD_RE.sub(sub_str, keywords.get(m.group("keyword")))
        line_list[m.start() : m.end()] = list(new_str)
    new_line = "".join(line_list)
    for k in keywords:
        assert k not in new_line, (line, new_line)
    return "".join(line_list)


# %%

new_lines = []
new_cards = []
for card in cards:
    if "TOO MANY CARDS" in card:
        new_lines.extend(card.splitlines())
        continue
    c = {}
    card_lines = card.splitlines()
    number = None
    for line in card_lines:
        if match := LINE_MATCH.search(line):
            if not match.group("sc"):
                line = line + ";"
                match = LINE_MATCH.search(line)
                assert match is not None
            field = match.group("field")
            value = match.group("value").lstrip('"').rstrip('"')
            subject = match.group("subject")
            if field == "card.cnumber":
                assert value.isnumeric(), value
                c["number"] = value
                number = value
                new_lines.append(line)
            elif field == "card.cname":
                c["name"] = value
                new_lines.append(new_json_get_call("name", number, subject))
            elif field == "card.cdesc":
                value = replace_keywords(value)
                c["desc"] = value
                new_lines.append(new_json_get_call("desc", number, subject))
            elif field == "card.cdesc_upgrade":
                value = replace_keywords(value)
                c["up_desc"] = value
                new_lines.append(new_json_get_call("up_desc", number, subject))
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    new_cards.append(c)
    new_lines.append("i++;\n")
with open(out_file, "w") as fp:
    fp.writelines(
        [i + "\n" if not ALL_WHITESPACE_RE.fullmatch(i) else i for i in new_lines]
    )
card_dict = {}
for i in new_cards:
    card_dict[i.pop("number")] = i

out_json.write_text(json.dumps({"cards": card_dict}, indent=2))
