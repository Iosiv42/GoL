""" Parser for RLE (Run Length Encoded) file. """

import re
import pathlib

from module_typing import GameState


def parse_rle(src_or_path: str, encoding: str = "utf8") -> GameState:
    """ Parse RLE file and return list of lived cells.
        src_or_path: path to source or source data.
    """

    if pathlib.Path(src_or_path).expanduser().is_file():
        with open(src_or_path, encoding=encoding) as src:
            data = src.read()
    else:
        data = src_or_path

    data = re.sub("^#.*\n", "", data, flags=re.MULTILINE)
    data = re.sub(" ", "", data, flags=re.MULTILINE)
    data = re.sub("^.*\n", "", data)

    lived_cells = []
    curr_y = 0
    for line in data.split("$"):
        curr_x = 0
        for item in re.findall(r"\d*[bo]", line):
            run_count = int(item[:-1]) if len(item) > 1 else 1
            if item[-1] == "o":
                lived_cells.extend(
                    (curr_x + i, curr_y) for i in range(run_count)
                )

            curr_x += run_count
        curr_y -= 1

    return lived_cells
