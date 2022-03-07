from __future__ import print_function

import numpy as np

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
    from .._io.output._common import reorder_labels
    from ..meshmaker import triangulate, voxelize

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that TOUGH output and mesh file exist
    if not os.path.isfile(args.infile):
        raise ValueError("TOUGH output file '{}' not found.".format(args.infile))

    with_mesh = bool(args.mesh)
    if with_mesh:
        if not os.path.isfile(args.mesh):
            raise ValueError("Mesh file '{}' not found.".format(args.mesh))
        if args.voxelize:
            print("Mesh file has been provided. Skipping option --voxelize.")
    else:
        if args.voxelize:
            if not args.origin:
                raise ValueError("Option --voxelize requires option --origin.")
            elif len(args.origin) != 3:
                raise ValueError(
                    "Option --origin requires 3 parameters, got {}.".format(
                        len(args.origin)
                    )
                )

    # Read output file
    print("Reading file '{}' ...".format(args.infile), end="")
    sys.stdout.flush()
    output = read_output(args.infile)
    if args.file_format != "xdmf":
        if args.time_step is not None:
            if not (-len(output) <= args.time_step < len(output)):
                raise ValueError("Inconsistent time step value.")
            output = output[args.time_step]
        else:
            output = output[-1]
        input_format = output.format
    else:
        input_format = output[-1].format
    print(" Done!")

    # Display warning if mesh is provided but input file format is 'tecplot'
    # Continue as if mesh was not provided
    if input_format == "tecplot":
        with_mesh = False
        msg = (
            "Cannot use mesh file with Tecplot TOUGH output, inferring dimensionality"
            if args.mesh
            else "Inferring dimensionality"
        )
    else:
        with_mesh = bool(args.mesh)
        msg = "Mesh file not specified, inferring dimensionality"

    # Triangulate or voxelize if no mesh
    voxelized = False
    if not with_mesh:
        print("{} ...".format(msg), end="")
        sys.stdout.flush()
        points, axis = _get_points(output if args.file_format != "xdmf" else output[0])
        ndim = len(axis)
        print(" Done!")

        if args.voxelize or ndim == 1:
            if ndim == 1:
                if not args.origin:
                    raise ValueError(
                        "Mesh is {}D and requires option --origin.".format(ndim)
                    )
                elif len(args.origin) != 3:
                    raise ValueError(
                        "Option --origin requires 3 parameters, got {}.".format(
                            len(args.origin)
                        )
                    )

            print("Mesh is {}D, voxelizing mesh ...".format(ndim), end="")
            sys.stdout.flush()

            mesh = voxelize(points, args.origin, layer=args.layer)
            mesh.cell_dada = {}

            idx = np.arange(len(points))
            idx = np.array(
                [
                    x
                    for x, _ in sorted(
                        zip(idx, points), key=lambda x: (x[1][2], x[1][1], x[1][0])
                    )
                ]
            )

            if args.file_format != "xdmf":
                for label, data in output.data.items():
                    if label not in {"X", "Y", "Z"}:
                        mesh.add_cell_data(label, data[idx])

            voxelized = True

        else:
            print(
                "Mesh is {}D, performing point triangulation ...".format(ndim), end=""
            )
            sys.stdout.flush()

            mesh = triangulate(points[:, axis])
            mesh.cell_data = {}

            if args.file_format != "xdmf":
                for label, data in output.data.items():
                    if label not in {"X", "Y", "Z"}:
                        mesh.add_point_data(label, data)

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
            output = [reorder_labels(data, mesh.labels) for data in output]
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
        if voxelized:
            data = [
                {k: v[idx] for k, v in out.data.items() if k not in {"X", "Y", "Z"}}
                for out in output
            ]
        else:
            data = [
                {k: v for k, v in out.data.items() if k not in {"X", "Y", "Z"}}
                for out in output
            ]
        time_steps = [out.time for out in output]

        if with_mesh or voxelized:
            write_time_series(
                filename,
                mesh.points,
                mesh.cells,
                cell_data=data,
                time_steps=time_steps,
            )
        else:
            write_time_series(
                filename,
                mesh.points,
                mesh.cells,
                point_data=data,
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

    # Voxelize
    parser.add_argument(
        "--voxelize",
        "-v",
        default=False,
        action="store_true",
        help="voxelize mesh (only if mesh is not provided, requires option --origin)",
    )

    # Origin
    parser.add_argument(
        "--origin",
        nargs="+",
        type=float,
        default=None,
        help="coordinates of origin point (only if option --voxelize is enabled)",
    )

    # Layer
    parser.add_argument(
        "--layer",
        default=False,
        action="store_true",
        help="voxelize mesh by layers (only if option --voxelize is enabled)",
    )

    return parser


def _get_points(output):
    # Number of data points
    n_points = len(next(iter(output.data.values())))

    # Make sure that point coordinates exist
    count = 0

    if "X" in output.data.keys():
        X = np.array(output.data["X"])
        count += 1
    else:
        X = np.zeros(n_points)

    if "Y" in output.data.keys():
        Y = np.array(output.data["Y"])
        count += 1
    else:
        Y = np.zeros(n_points)

    if "Z" in output.data.keys():
        Z = np.array(output.data["Z"])
        count += 1
    else:
        Z = np.zeros(n_points)

    if count == 0:
        raise ValueError("No coordinate array ('X', 'Y', 'Z') found.")

    # Assert dimension of the problem
    nx = len(np.unique(X))
    ny = len(np.unique(Y))
    nz = len(np.unique(Z))

    # Reconstruct points cloud
    zeros = np.zeros(n_points)
    if ny == 1 and nz == 1:
        points = np.column_stack((X, zeros, zeros))
        axis = [0]
    elif nx == 1 and nz == 1:
        points = np.column_stack((zeros, Y, zeros))
        axis = [1]
    elif nx == 1 and ny == 1:
        points = np.column_stack((zeros, zeros, Z))
        axis = [2]
    elif nx == 1:
        points = np.column_stack((zeros, Y, Z))
        axis = [1, 2]
    elif ny == 1:
        points = np.column_stack((X, zeros, Z))
        axis = [0, 2]
    elif nz == 1:
        points = np.column_stack((X, Y, zeros))
        axis = [0, 1]
    else:
        points = np.column_stack((X, Y, Z))
        axis = [0, 1, 2]

    return points, axis
