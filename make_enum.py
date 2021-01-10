from typing import TYPE_CHECKING
import subprocess

import click

if TYPE_CHECKING:
    from io import TextIOWrapper

CLASS_LINE = "class {name}(Enum):\n"
member_line = "    {member} = auto()\n"


@click.command()
@click.argument("source_file", type=click.File())
@click.argument("dest_file", type=click.File(mode="w"))
def main(source_file: "TextIOWrapper", dest_file: "TextIOWrapper"):
    source_data = source_file.read()
    output = ["from enum import Enum, auto\n", "\n"]
    for line in source_data.splitlines():
        if "enum" in line:
            output.append(CLASS_LINE.format(name=line.split()[1]))
        elif "}" in line:
            break
        else:
            output.append(member_line.format(member=line.strip(",").replace(" ", "")))
    dest_file.writelines(output)
    out = subprocess.run(["black.exe", dest_file.name], text=True, capture_output=True)


if __name__ == "__main__":
    main()
