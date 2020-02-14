import numpy

from .._io._helpers import Output

__all__ = [
    "extract",
]


def extract(argv=None):
    import os

    parser = _get_parser()
    args = parser.parse_args(argv)

    # Check that TOUGH output and MESH file exist
    assert os.path.isfile(args.infile), "TOUGH output file '{}' not found.".format(
        args.infile
    )
    assert os.path.isfile(args.mesh), "MESH file '{}' not found.".format(args.mesh)

    # Read MESH and extract X, Y and Z
    nodes, is_eleme = {}, False
    with open(args.mesh, "r") as f:
        for line in f:
            line = line.upper().strip()
            if line[:5].startswith("ELEME"):
                is_eleme = True
                line = next(f)
                while line.strip():
                    label = line[:5]
                    X = float(line[50:60]) if line[50:60].strip() else 0.0
                    Y = float(line[60:70]) if line[60:70].strip() else 0.0
                    Z = float(line[70:80]) if line[70:80].strip() else 0.0
                    nodes[label] = [X, Y, Z]
                    line = next(f)
                headers = ["X", "Y", "Z"]
                break
    assert is_eleme, "Invalid MESH file '{}'.".format(args.mesh)

    # Read TOUGH output file
    out = []
    with open(args.infile, "r") as f:
        for line in f:
            line = line.upper().strip()
            if line.startswith("OUTPUT DATA AFTER"):
                out.append(_read_table(f, nodes, args.version))

    # Write TOUGH3 element output file
    if not args.split or len(out) == 1:
        with open(args.output_file, "w") as f:
            _write_header(f, headers, out[0])
            for data in out:
                _write_table(f, data, nodes)
    else:
        head, ext = os.path.splitext(args.output_file)
        for i, data in enumerate(out):
            with open("{}_{}{}".format(head, i + 1, ext), "w") as f:
                _write_header(f, headers, data)
                _write_table(f, data, nodes)


def _get_parser():
    import argparse

    # Initialize parser
    parser = argparse.ArgumentParser(
        description=(
            "Extract results from TOUGH main output file and reformat as a TOUGH3 element output file."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Input file
    parser.add_argument(
        "infile", type=str, help="TOUGH output file",
    )

    # Mesh file
    parser.add_argument(
        "mesh", type=str, help="TOUGH MESH file (can be INFILE)",
    )

    # Output file
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        default="OUTPUT_ELEME.csv",
        help="TOUGH3 element output file",
    )

    # TOUGH output file version
    parser.add_argument(
        "--version",
        "-v",
        type=int,
        choices=(2, 3),
        default=2,
        help="TOUGH output file version",
    )

    # Split or not
    parser.add_argument(
        "--split",
        "-s",
        default=False,
        action="store_true",
        help="Write one file per time step",
    )

    return parser


def _read_table(f, points, version):
    def str2float(s):
        """
        Convert primary variables string to float.
        """
        s = s.lower()
        significand, exponent = s[:-4], s[-4:].replace("e", "")
        return float("{}e{}".format(significand, exponent))

    # Skip next 5 lines
    n_skip = 5 if version == 2 else 4
    for _ in range(n_skip):
        line = next(f)

    # Read time step
    time = float(line.strip().split()[0])

    # Skip next 4 lines
    n_skip = 4 if version == 2 else 3
    for _ in range(n_skip):
        line = next(f)

    # Read headers once (ignore ELEM and INDEX)
    headers = line.strip().split()[2:]

    # Skip next 2 lines
    for _ in range(2):
        line = next(f).strip()

    # Loop until end of output block
    count = 0
    variables, labels = [], []
    end_char = "@" if version == 2 else "0@"
    while True:
        if line[:5] in points.keys():
            count += 1
            labels.append(line[:5])
            variables.append([str2float(x) for x in line[5:].split()[1:]])

        line = next(f).strip()
        if line.startswith(end_char):
            break
    assert count == len(points), "Inconsistent number of elements."

    return Output(
        time, labels, {k: v for k, v in zip(headers, numpy.transpose(variables))}
    )


def _write_table(f, data, nodes):
    # Write time step
    f.write('"TIME [sec]  {:.8e}"\n'.format(data.time))

    # Loop over elements
    formats = ['"{:>18}"'] + (len(data.data.keys()) + 3) * ["  {:>.12e}"]
    for i, label in enumerate(data.labels):
        record = [label] + nodes[label] + [v[i] for v in data.data.values()]
        record = ",".join(fmt.format(rec) for fmt, rec in zip(formats, record)) + "\n"
        f.write(record)


def _write_header(f, headers, data):
    headers = ["ELEM"] + headers + list(data.data.keys())
    units = [""] + 3 * ["(M)"] + len(data.data.keys()) * ["(-)"]
    f.write(",".join('"{:>18}"'.format(header) for header in headers) + "\n")
    f.write(",".join('"{:>18}"'.format(unit) for unit in units) + "\n")
