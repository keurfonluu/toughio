__all__ = [
    "merge",
]


def merge(argv=None):
    import os

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that input, MESH and INCON files exist
    head = os.path.split(args.infile)[0]
    gener_filename = head + ("/" if head else "") + "GENER"
    mesh_filename = head + ("/" if head else "") + "MESH"
    incon_filename = head + ("/" if head else "") + "INCON"

    if not os.path.isfile(args.infile):
        raise ValueError(f"File '{args.infile}' not found.")

    gener_exists = os.path.isfile(gener_filename)
    mesh_exists = os.path.isfile(mesh_filename)
    incon_exists = os.path.isfile(incon_filename)

    if not (gener_exists or mesh_exists or incon_exists):
        raise ValueError("GENER, MESH or INCON file(s) not found. Nothing to merge.")

    # Buffer input file
    with open(args.infile, "r") as f:
        input_file = list(f)

    # Check that input file has at least blocks ROCKS, PARAM, ENDFI or ENDCY
    count = 0
    for line in input_file:
        count += int(line.upper()[:5] in {"ROCKS", "PARAM", "ENDFI", "ENDCY"})
    if count < 3:
        raise ValueError(f"Invalid input file '{args.infile}'.")
    
    # Buffer GENER
    if gener_exists:
        with open(gener_filename, "r") as f:
            gener_file = list(f)

        if not gener_file[0].startswith("GENER"):
            raise ValueError("Invalid GENER file.")

    # Buffer MESH
    if mesh_exists:
        with open(mesh_filename, "r") as f:
            mesh_file = list(f)

        if not mesh_file[0].startswith("ELEME"):
            raise ValueError("Invalid MESH file.")

    # Buffer INCON if exist
    if incon_exists:
        with open(incon_filename, "r") as f:
            incon_file = list(f)

        if not incon_file[0].startswith("INCON"):
            raise ValueError("Invalid INCON file.")

    # Locate ENDFI or ENDCY
    for i, line in enumerate(input_file):
        if line.upper()[:5] in {"ENDFI", "ENDCY"}:
            break

    # Buffer output file
    output_file = input_file[:i]

    if gener_exists:
        output_file += gener_file

    if mesh_exists:
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
            "Merge input file, GENER and/or MESH and/or INCON into a single file. "
            "The files must be in the same directory as input file."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Input file
    parser.add_argument(
        "infile",
        type=str,
        help="TOUGH input file",
    )

    # Output file
    parser.add_argument("outfile", type=str, help="merged TOUGH input file")

    return parser
