__all__ = [
    "co2tab",
]


def co2tab(argv=None):
    import os
    import shutil

    import pkg_resources

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that target directory exists
    if not os.path.isdir(args.path):
        raise ValueError(f"Directory '{args.path}' not found.")

    # Copy CO2TAB file
    filename = pkg_resources.resource_filename("toughio", "data/CO2TAB")
    output_filename = os.path.join(args.path, "CO2TAB")
    shutil.copy(filename, output_filename)


def _get_parser():
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser(
        description=("Write CO2TAB in target directory."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Output path
    parser.add_argument(
        "path",
        type=str,
        help="directory path",
    )

    return parser
