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
    import sys
    from .. import read_mesh, read_output
    from ..meshmaker import voxelize, triangulate

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Display warning if mesh is provided but input file format is 'tecplot'
    # Continue as if mesh was not provided
    with_mesh = bool(args.mesh)
    if args.input_format == "tecplot":
        with_mesh = False
        msg = (
            "Cannot use mesh file with Tecplot TOUGH output, inferring dimensionality"
            if args.mesh
            else "Inferring dimensionality"
        )
    else:
        with_mesh = bool(args.mesh)
        msg = "Mesh file not specified, inferring dimensionality"

    # Check that TOUGH output and mesh file exist
    assert os.path.isfile(args.infile), "TOUGH output file '{}' not found.".format(
        args.infile
    )
    if with_mesh:
        assert os.path.isfile(args.mesh), "Pickled mesh file '{}' not found.".format(
            args.mesh
        )

    # Read output file
    print("Reading file '{}' ...".format(args.infile), end="")
    sys.stdout.flush()
    out = read_output(args.infile, args.input_format)
    if args.time_step is not None:
        assert -len(out) <= args.time_step < len(out), "Inconsistent time step value."
        out = out[args.time_step]
    else:
        out = out[-1]
    print(" Done!")

    # Triangulate or voxelize if no mesh
    if not with_mesh:
        print("{} ...".format(msg), end="")
        sys.stdout.flush()
        points = _get_points(out)
        ndim = 1 if points.ndim == 1 else points.shape[1]
        print(" Done!")

        if ndim > 1:
            print(
                "Mesh is {}D, performing point triangulation ...".format(ndim), end=""
            )
            sys.stdout.flush()

            mesh = triangulate(points)
            for label, data in out.data.items():
                if label not in {"X", "Y", "Z"}:
                    mesh.add_point_data(label, data)

        else:
            print("Mesh is 1D, voxelizing points ...", end="")
            sys.stdout.flush()

            mesh = voxelize(points)
            for label, data in out.data.items():
                if label not in {"X", "Y", "Z"}:
                    mesh.add_cell_data(label, data)

    else:
        print("Reading mesh file '{}' ...".format(args.mesh), end="")
        sys.stdout.flush()
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
        head, _ = os.path.splitext(args.infile)
        filename = "{}{}".format(head, format_to_ext[args.file_format])

    # Write output file
    print("Writing output file '{}' ...".format(filename), end="")
    sys.stdout.flush()
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

    # Input file format
    parser.add_argument(
        "--input-format",
        "-i",
        type=str,
        choices=("tough", "tecplot"),
        default="tough",
        help="TOUGH output file format",
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


def _get_points(data):
    import numpy

    # Number of data points
    n_points = len(next(iter(data.data.values())))

    # Make sure that point coordinates exist
    count = 0

    if "X" in data.data.keys():
        X = numpy.array(data.data["X"])
        count += 1
    else:
        X = numpy.zeros(n_points)

    if "Y" in data.data.keys():
        Y = numpy.array(data.data["Y"])
        count += 1
    else:
        Y = numpy.zeros(n_points)

    if "Z" in data.data.keys():
        Z = numpy.array(data.data["Z"])
        count += 1
    else:
        Z = numpy.zeros(n_points)

    assert count > 0, "No coordinate array ('X', 'Y', 'Z') found."

    # Assert dimension of the problem
    nx = len(numpy.unique(X))
    ny = len(numpy.unique(Y))
    nz = len(numpy.unique(Z))

    # Reconstruct points cloud
    points = (
        X
        if ny == 1 and nz == 1
        else Y
        if nx == 1 and nz == 1
        else Z
        if nx == 1 and ny == 1
        else numpy.column_stack((Y, Z))
        if nx == 1
        else numpy.column_stack((X, Z))
        if ny == 1
        else numpy.column_stack((X, Y))
        if nz == 1
        else numpy.column_stack((X, Y, Z))
    )

    return points
