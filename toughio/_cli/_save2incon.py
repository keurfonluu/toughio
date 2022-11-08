__all__ = [
    "save2incon",
]


def save2incon(argv=None):
    import os

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that SAVE file exists
    if not os.path.isfile(args.infile):
        raise ValueError(f"SAVE file '{args.infile}' not found.")

    # Write INCON file
    with open(args.outfile, "w") as f:
        first = True
        with open(args.infile, "r") as fsave:
            for line in fsave:
                if first:
                    if not line.startswith("INCON"):
                        raise ValueError("Invalid SAVE file.")
                    else:
                        first = False
                if args.reset and line.startswith("+++"):
                    break
                f.write(line)

        if args.reset:
            f.write("\n")


def _get_parser():
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser(
        description=("Convert a SAVE file to an INCON file."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Input file
    parser.add_argument(
        "infile",
        type=str,
        help="SAVE file to convert",
    )

    # Output file
    parser.add_argument(
        "outfile",
        type=str,
        help="converted INCON file",
    )

    # Reset
    parser.add_argument(
        "--reset",
        "-r",
        default=False,
        action="store_true",
        help="reset all counters",
    )

    return parser
