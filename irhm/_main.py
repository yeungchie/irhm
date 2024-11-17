from argparse import ArgumentParser

from .ir import from_file
from .ui import HeatmapApp


def main() -> int:
    default_array = "10x10"

    parser = ArgumentParser(description="IR-Drop Heatmap")
    parser.add_argument(
        "file",
        type=str,
        help="input file",
    )
    parser.add_argument(
        "--array",
        type=str,
        help=f"array of heatmap, deafult={default_array!r}",
        default=default_array,
    )
    args = parser.parse_args()

    app = HeatmapApp(
        [],
        collection=from_file(args.file),
        array=tuple(map(int, args.array.split("x"))),
    )
    app.show()
    return app.exec()
