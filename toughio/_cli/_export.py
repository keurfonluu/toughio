from __future__ import print_function

__all__ = [
    "export",
]


format_to_ext = {
    "tecplot": ".dat",
    "vtk": ".vtk",
    "vtu": ".vtu",
}


def export(argv=None):
    import os
    from .. import read_mesh, read_output

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that TOUGH output and mesh file exist
    assert os.path.isfile(args.infile), "TOUGH output file '{}' not found.".format(
        args.infile
    )
    if args.mesh:
        assert os.path.isfile(args.mesh), "Pickled mesh file '{}' not found.".format(
            args.mesh
        )

    # Read output file
    print("Reading file '{}' ...".format(args.infile), end="")
    out = read_output(args.infile)
    if args.time_step is not None:
        assert -len(out) <= args.time_step < len(out), "Inconsistent time step value."
        out = out[args.time_step]
    else:
        out = out[-1]
    print(" Done!")

    # Triangulate if no mesh
    if not args.mesh:
        print("Mesh file not specified, performing triangulation...", end="")
        mesh = _triangulate(out)
    else:
        print("Reading mesh file '{}' ...".format(args.mesh), end="")
        try:
            mesh = read_mesh(args.mesh, file_format="pickle")
        except:
            raise ValueError("Cannot unpickle mesh file {}.".format(args.mesh))
        mesh.read_output(out)
    print(" Done!")

    # Output file name
    if args.output_file:
        filename = args.output_file
    else:
        head, ext = os.path.splitext(args.infile)
        filename = "{}{}".format(head, format_to_ext[args.file_format])

    # Write output file
    print("Writing output file '{}' ...".format(filename), end="")
    mesh.cell_data.pop("material")
    mesh.write(filename, file_format=args.file_format)
    print(" Done!")


def _get_parser():
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser(
        description=("Export TOUGH simulation results to a file for visualization."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Input file
    parser.add_argument(
        "infile", type=str, help="TOUGH output file",
    )

    # Mesh file
    parser.add_argument(
        "--mesh", "-m", type=str, default=None, help="Pickled toughio.Mesh",
    )

    # Time step
    parser.add_argument(
        "--time-step", "-t", type=int, default=None, help="Time step to export",
    )

    # Output file
    parser.add_argument(
        "--output-file", "-o", type=str, default=None, help="Exported file",
    )

    # File format
    parser.add_argument(
        "--file-format",
        "-f",
        type=str,
        choices=("tecplot", "vtk", "vtu"),
        default="vtk",
        help="Exported file format",
    )

    return parser


def _triangulate(data):
    import numpy
    from ..meshmaker import triangulate

    # Make sure that point coordinates exist
    assert "X" in data.data.keys(), "Data 'X' not found."
    assert "Y" in data.data.keys(), "Data 'Y' not found."
    assert "Z" in data.data.keys(), "Data 'Z' not found."

    X = data.data["X"]
    Y = data.data["Y"]
    Z = data.data["Z"]

    # Assert dimension of the problem
    nx = len(numpy.unique(X))
    ny = len(numpy.unique(Y))
    nz = len(numpy.unique(Z))

    # Reconstruct points cloud
    points = (
        numpy.column_stack((Y, Z))
        if nx == 1
        else numpy.column_stack((X, Z))
        if ny == 1
        else numpy.column_stack((X, Y))
        if nz == 1
        else numpy.column_stack((X, Y, Z))
    )

    # Triangulate
    mesh = triangulate(points)

    # Attach data to points in mesh
    for label, data in data.data.items():
        if label not in {"X", "Y", "Z"}:
            mesh.add_point_data(label, data)

    return mesh
