__all__ = [
    "merge",
]


def merge(argv=None):
    import os

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that input, MESH and INCON files exist
    head = os.path.split(args.infile)[0]
    mesh_filename = head + ("/" if head else "") + "MESH"
    incon_filename = head + ("/" if head else "") + "INCON"

    assert os.path.isfile(args.infile), "File '{}' not found.".format(args.infile)
    assert os.path.isfile(mesh_filename), "MESH file not found."
    incon_exists = os.path.isfile(incon_filename)

    # Buffer input file
    with open(args.infile, "r") as f:
        input_file = list(f)

    # Check that input file has at least blocks ROCKS, PARAM, ENDFI or ENDCY
    count = 0
    for line in input_file:
        count += int(line.upper()[:5] in {"ROCKS", "PARAM", "ENDFI", "ENDCY"})
    assert count >= 3, "Invalid input file '{}'.".format(args.infile)

    # Buffer MESH
    with open(mesh_filename, "r") as f:
        mesh_file = list(f)
    assert mesh_file[0].startswith("ELEME"), "Invalid MESH file."

    # Buffer INCON if exist
    if incon_exists:
        with open(incon_filename, "r") as f:
            incon_file = list(f)
        assert incon_file[0].startswith("INCON"), "Invalid INCON file."

    # Locate ENDFI or ENDCY
    for i, line in enumerate(input_file):
        if line.upper()[:5] in {"ENDFI", "ENDCY"}:
            break

    # Buffer output file
    output_file = input_file[:i]
    output_file += mesh_file
    if incon_exists:
        output_file += incon_file
    output_file += input_file[i:]

    # Write output file
    with open(args.outfile, "w") as f:
        for line in output_file:
            f.write(line)


def _get_parser():
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser(
        description=(
            "Merge input file, MESH and/or INCON into a single file. "
            "The files must be in the same directory."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Input file
    parser.add_argument(
        "infile", type=str, help="TOUGH input file",
    )

    # Output file
    parser.add_argument("outfile", type=str, help="Merged TOUGH input file")

    return parser
