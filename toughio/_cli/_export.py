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
        raise ValueError(f"TOUGH output file '{args.infile}' not found.")

    with_mesh = bool(args.mesh)
    if with_mesh:
        if not os.path.isfile(args.mesh):
            raise ValueError(f"Mesh file '{args.mesh}' not found.")
        if args.voxelize:
            print("Mesh file has been provided. Skipping option --voxelize.")
    else:
        if args.voxelize:
            if not args.origin:
                raise ValueError("Option --voxelize requires option --origin.")
            elif len(args.origin) != 3:
                raise ValueError(
                    f"Option --origin requires 3 parameters, got {len(args.origin)}."
                )

    # Read output file
    print(f"Reading file '{args.infile}' ...", end="")
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
        labels = output.labels
    else:
        input_format = output[-1].format
        labels = output[-1].labels
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
        print(f"{msg} ...", end="")
        sys.stdout.flush()
        points, axis = _get_points(
            output if args.file_format != "xdmf" else output[0],
            args.ignore_elements,
        )
        ndim = len(axis)
        print(" Done!")

        if args.ignore_elements:
            mask = np.ones(len(labels), dtype=bool)
            for element in args.ignore_elements:
                mask = np.logical_and(mask, labels != element)

        if args.voxelize or ndim == 1:
            if ndim == 1:
                if not args.origin:
                    raise ValueError(f"Mesh is {ndim}D and requires option --origin.")
                elif len(args.origin) != 3:
                    raise ValueError(
                        f"Option --origin requires 3 parameters, got {len(args.origin)}."
                    )

            print(f"Mesh is {ndim}D, voxelizing mesh ...", end="")
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
                    if label in {"X", "Y", "Z"}:
                        continue

                    if args.ignore_elements:
                        data = data[mask]

                    mesh.add_cell_data(label, data[idx])

            voxelized = True

        else:
            print(f"Mesh is {ndim}D, performing point triangulation ...", end="")
            sys.stdout.flush()

            mesh = triangulate(points[:, axis])
            mesh.cell_data = {}

            if args.file_format != "xdmf":
                for label, data in output.data.items():
                    if label in {"X", "Y", "Z"}:
                        continue

                    if args.ignore_elements:
                        data = data[mask]

                    mesh.add_point_data(label, data)

    else:
        print(f"Reading mesh file '{args.mesh}' ...", end="")
        sys.stdout.flush()

        try:
            mesh = read_mesh(args.mesh)
        except Exception as e:
            raise ValueError(f"Unable to read mesh file {args.mesh}: {e}.")

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
        filename = f"{head}{format_to_ext[args.file_format]}"

    # Write output file
    print(f"Writing output file '{filename}' ...", end="")
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
        "infile",
        type=str,
        help="TOUGH output file",
    )

    # Mesh file
    parser.add_argument(
        "--mesh",
        "-m",
        type=str,
        default=None,
        help="pickled toughio.Mesh",
    )

    # Time step
    parser.add_argument(
        "--time-step",
        "-t",
        type=int,
        default=None,
        help="time step to export",
    )

    # Output file
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        default=None,
        help="exported file",
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

    # Ignore elements
    parser.add_argument(
        "--ignore-elements",
        nargs="+",
        type=str,
        help="list of elements to ignore (only if mesh is not provided)",
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


def _get_points(output, ignore_elements):
    # Number of data points
    n_points = len(next(iter(output.data.values())))

    # Make sure that point coordinates exist
    count = 0

    if "X" in output.data:
        X = np.array(output.data["X"])
        count += 1
    else:
        X = np.zeros(n_points)

    if "Y" in output.data:
        Y = np.array(output.data["Y"])
        count += 1
    else:
        Y = np.zeros(n_points)

    if "Z" in output.data:
        Z = np.array(output.data["Z"])
        count += 1
    else:
        Z = np.zeros(n_points)

    if count == 0:
        raise ValueError("No coordinate array ('X', 'Y', 'Z') found.")

    # Ignore elements
    if ignore_elements:
        mask = np.ones(n_points, dtype=bool)
        for element in ignore_elements:
            mask = np.logical_and(mask, output.labels != element)

        X = X[mask]
        Y = Y[mask]
        Z = Z[mask]
        n_points = mask.sum()

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
