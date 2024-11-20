from argparse import ArgumentParser
import sys

from .ir import from_file, from_string
from .ui import HeatmapApp


def main() -> int:
    default_array = "10x10"

    parser = ArgumentParser(description="IR-Drop Heatmap")
    parser.add_argument(
        "file",
        type=str,
        nargs="*",
        help="input file",
    )
    parser.add_argument(
        "--array",
        type=str,
        help=f"array of heatmap, deafult={default_array!r}",
        default=default_array,
    )
    args = parser.parse_args()

    if args.file:
        collection = from_file(*args.file)
    else:
        collection = from_string(sys.stdin.read())

    col, row = tuple(map(int, args.array.split("x")))

    app = HeatmapApp(
        [],
        collection=collection,
        array=(col, row),
    )
    app.show()
    return app.exec()
