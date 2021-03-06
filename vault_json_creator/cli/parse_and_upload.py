import sys
from pathlib import Path
from typing import Optional, TYPE_CHECKING

import click

if TYPE_CHECKING:
    from io import TextIOWrapper
    from google.cloud.storage import Blob

_base_dir = Path.home() / r"AppData\Local\VaultoftheVoid"
_default_card = _base_dir / "CardData.json"
_default_tips = _base_dir / "Tooltips.json"


@click.command()
@click.option(
    "--card-source",
    default=str(_default_card),
    help="Name of the card source file",
    type=click.File(),
)
@click.option(
    "--tooltip-source",
    default=str(_default_tips),
    help="Name of the tooltip source file",
    type=click.File(),
)
@click.option(
    "--output-path",
    "-o",
    default="gs://vault-of-the-void/vault_data.json",
    help="Path to output file",
)
@click.option(
    "--indent",
    "-i",
    default=2,
    help="Number of spaces to use when indenting the output json",
)
@click.option(
    "--creds",
    "-c",
    default=None,
    type=click.Path(exists=True),
    help="Path to the GCP service account json, if none provided, use normal inherited",
)
def parse_and_upload(
    card_source: "TextIOWrapper",
    tooltip_source: "TextIOWrapper",
    output_path: str,
    indent: int,
    creds: Optional[str],
):
    import json

    data = {
        **parse_card_data(json.load(card_source)),
        **parse_tooltip_data(json.load(tooltip_source)),
    }
    # Final combined JSON
    output_json = json.dumps(data, indent=indent)
    # Determining the destination, local or GCS
    if len(output_path) > 5 and output_path[:5] == "gs://":
        write_to_gcs(output_json, output_path, creds)
    else:
        write_to_local(output_json, output_path)
    click.echo(f"Wrote output to {click.format_filename(output_path)}")
    sys.exit(0)


# Parsing functions
def parse_card_data(source_data: dict) -> dict:
    from vault_json_creator.models import AllCards

    ac = AllCards(cards=list(source_data.values()))
    pc = ac.make_public_cards()
    return pc.dict()


def parse_tooltip_data(source_data: dict) -> dict:
    from vault_json_creator.models import AllTips

    at = AllTips(tips=list(source_data.values()))
    return at.dict()


# Output functions
def write_to_local(out_data: str, out_path: str):
    from pathlib import Path

    out = Path(out_path)
    out.write_text(out_data)


def write_to_gcs(out_data: str, out_path: str, creds_file: Optional[str]):
    from google.cloud.exceptions import Forbidden
    from google.cloud.storage import Client
    from urllib.parse import urlparse

    if creds_file is not None:
        client = Client.from_service_account_json(creds_file)
    else:
        client = Client()
    url = urlparse(out_path)
    bucket = client.bucket(url.netloc)
    # Stripping the leading /
    blob: "Blob"
    blob = bucket.blob(url.path[1:])
    try:
        blob.upload_from_string(out_data, content_type="application/json")
    except Forbidden as e:
        click.secho(
            f"Unable to write to {out_path}, permission denied:\n"
            f"{e.response.json()['error']['message']}",
            err=True,
        )
        sys.exit(1)
    blob.make_public()


if __name__ == "__main__":
    parse_and_upload()
