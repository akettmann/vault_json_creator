from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from io import TextIOWrapper


@click.command()
@click.argument("source", type=click.File("r"))
@click.option(
    "--dest", help="Output file", type=click.File("w", encoding="utf-8"), default="-"
)
@click.option(
    "--model",
    help="Model to be used to validate file",
    default="card",
    type=click.Choice(("card", "tooltip"), case_sensitive=False),
)
@click.option(
    "--indent",
    help="How much each level should be indented in the json",
    default=2,
    type=click.INT,
)
def main(source: "TextIOWrapper", dest: click.utils.LazyFile, model: str, indent: int):
    import json

    dest.write(parse_funcs[model](json.load(source), indent))
    click.echo("Finished!")


def parse_card_data(source_data: dict, indent: int) -> str:
    from vault_json_creator.models import AllCards

    ac = AllCards(cards=list(source_data.values()))
    pc = ac.make_public_cards()
    return pc.json(indent=indent)


def parse_tooltip_data(source_data: dict, indent: int) -> str:
    from vault_json_creator.models import AllTips

    at = AllTips(tips=list(source_data.values()))
    return at.json(indent=indent)


parse_funcs = {"card": parse_card_data, "tooltip": parse_tooltip_data}
if __name__ == "__main__":
    main()
