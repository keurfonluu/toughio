from __future__ import print_function

__all__ = [
    "export",
]


format_to_ext = {
    "tecplot": ".dat",
    "vtk": ".vtk",
    "vtu": ".vtu",
    "xdmf": ".xdmf",
}


def export(argv=None):
    import os
    import sys
    from .. import read_mesh, read_output, write_time_series
    from .._io._helpers import _reorder_labels
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
    if not os.path.isfile(args.infile):
        raise ValueError("TOUGH output file '{}' not found.".format(args.infile))
    if with_mesh:
        if not os.path.isfile(args.mesh):
            raise ValueError("Mesh file '{}' not found.".format(args.mesh))

    # Read output file
    print("Reading file '{}' ...".format(args.infile), end="")
    sys.stdout.flush()
    output = read_output(args.infile, args.input_format)
    if args.file_format != "xdmf":
        if args.time_step is not None:
            if not (-len(output) <= args.time_step < len(output)):
                raise ValueError("Inconsistent time step value.")
            output = output[args.time_step]
        else:
            output = output[-1]
    print(" Done!")

    # Triangulate or voxelize if no mesh
    if not with_mesh:
        print("{} ...".format(msg), end="")
        sys.stdout.flush()
        points = _get_points(output if args.file_format != "xdmf" else output[0])
        ndim = 1 if points.ndim == 1 else points.shape[1]
        print(" Done!")

        if ndim > 1:
            print(
                "Mesh is {}D, performing point triangulation ...".format(ndim), end=""
            )
            sys.stdout.flush()

            mesh = triangulate(points)
            mesh.cell_dada = {}

            if args.file_format != "xdmf":
                for label, data in output.data.items():
                    if label not in {"X", "Y", "Z"}:
                        mesh.add_point_data(label, data)

        else:
            print("Mesh is 1D, voxelizing points ...", end="")
            sys.stdout.flush()

            mesh = voxelize(points)
            mesh.cell_dada = {}

            if args.file_format != "xdmf":
                for label, data in output.data.items():
                    if label not in {"X", "Y", "Z"}:
                        mesh.add_cell_data(label, data)

    else:
        print("Reading mesh file '{}' ...".format(args.mesh), end="")
        sys.stdout.flush()

        try:
            mesh = read_mesh(args.mesh)
        except Exception as e:
            raise ValueError("Unable to read mesh file {}: {}.".format(args.mesh, e))

        if args.file_format != "xdmf":
            mesh.point_data = {}
            mesh.cell_dada = {}
            mesh.field_data = {}
            mesh.point_sets = {}
            mesh.cell_sets = {}
            mesh.read_output(output)
        else:
            output = [_reorder_labels(data, mesh.labels) for data in output]
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

    if args.file_format != "xdmf":
        mesh.write(filename, file_format=args.file_format)

    else:
        data = [
            {k: v for k, v in out.data.items() if k not in {"X", "Y", "Z"}}
            for out in output
        ]
        time_steps = [out.time for out in output]

        if not with_mesh:
            write_time_series(
                filename,
                mesh.points,
                mesh.cells,
                point_data=data,
                time_steps=time_steps,
            )
        else:
            write_time_series(
                filename,
                mesh.points,
                mesh.cells,
                cell_data=data,
                time_steps=time_steps,
            )

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
        "--mesh", "-m", type=str, default=None, help="pickled toughio.Mesh",
    )

    # Time step
    parser.add_argument(
        "--time-step", "-t", type=int, default=None, help="time step to export",
    )

    # Output file
    parser.add_argument(
        "--output-file", "-o", type=str, default=None, help="exported file",
    )

    # File format
    parser.add_argument(
        "--file-format",
        "-f",
        type=str,
        choices=("tecplot", "vtk", "vtu", "xdmf"),
        default="vtk",
        help="exported file format",
    )

    return parser


def _get_points(output):
    import numpy

    # Number of data points
    n_points = len(next(iter(output.data.values())))

    # Make sure that point coordinates exist
    count = 0

    if "X" in output.data.keys():
        X = numpy.array(output.data["X"])
        count += 1
    else:
        X = numpy.zeros(n_points)

    if "Y" in output.data.keys():
        Y = numpy.array(output.data["Y"])
        count += 1
    else:
        Y = numpy.zeros(n_points)

    if "Z" in output.data.keys():
        Z = numpy.array(output.data["Z"])
        count += 1
    else:
        Z = numpy.zeros(n_points)

    if count == 0:
        raise ValueError("No coordinate array ('X', 'Y', 'Z') found.")

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
