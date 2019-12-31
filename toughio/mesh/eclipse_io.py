# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from __future__ import division, with_statement, unicode_literals

import numpy as np

from meshio import Mesh

__all__ = [
    "read",
    "write",
]


def read(filename, repair_conformity, repair_cells, z_precision,
    invert_zaxis):
    """
    Read Eclipse GRDECL grid file.
    """
    with open(filename, "r") as f:
        out = read_buffer(f, repair_conformity, repair_cells, z_precision)
    if invert_zaxis:
        out.points[:,2] *= -1.
    return out


def read_buffer(f, repair_conformity, repair_cells, z_prec):
    """
    Read ASCII file line by line.
    """
    data = {}
    for line in f:
        if line.startswith("COORDSYS"):
            continue
        elif line.startswith("SPECGRID"):
            line = _next_line(f)
            nx, ny, nz, nres = [ int(n) for n in line[:4] ]
            coord_type = line[4]
            if nres > 1:
                raise NotImplementedError(
                    "Multiple reservoirs are not supported."
                )
            if coord_type != "F":
                raise NotImplementedError(
                    "Radial coordinate system is not supported."
                )
        elif line.startswith("COORD"):
            coord = _read_data(f, ( ny+1, nx+1, 6 ), float)
        elif line.startswith("ZCORN"):
            zcorn = _read_data(f, ( 2*nz, 2*ny, 2*nx ), float)
        elif line.startswith("ACTNUM"):
            data["ACTNUM"] = _read_data(f, None, int)
        elif line.startswith("PORO"):
            data["POROSITY"] = _read_data(f, None, float)
        elif line.startswith("PERMEABILITY"):
            data["PERMEABILITY"] = _read_data(f, None, float)
    data["eclipse:layer"] = np.concatenate(
        [ np.full(nx*ny, k+1) for k in range(nz) ]
    )

    if repair_conformity:
        points, cells, cell_data = _translate_points_cells_conform(
            coord, zcorn, data, nx, ny, nz, z_prec,
        )
    else:
        points, cells, cell_data = _translate_points_cells(
            coord, zcorn, data, nx, ny, nz,
        )
    if repair_cells:
        cells, cell_data = _repair_cells(points, cells, cell_data)
    return Mesh(
        points = np.array(points), 
        cells = cells,
        cell_data = cell_data,
    )


def _read_data(f, shape = None, val_type = float):
    """
    Convert section data into an array.
    """
    out = []
    last_data_line = False
    while not last_data_line:
        line = _next_line(f)
        if line[0] == "--":
            continue
        else:
            last_data_line = line[-1] == "/"
            if last_data_line:
                out.extend([ _str2val(l, val_type) for l in line[:-1] ])
            else:
                out.extend([ _str2val(l, val_type) for l in line ])
    out = np.concatenate(out)
    return out.reshape(shape, order = "C") if shape else out


def _next_line(f):
    """
    Ignore ECLIPSE comment and blank lines.
    """
    out = next(f).rstrip().split()
    while not out or out[0] == "--":
        out = next(f).rstrip().split()
    return out


def _str2val(instr, val_type = float):
    """
    Handle asterisks for repeated quantities.
    """
    try:
        out = [ val_type(instr) ]
    except ValueError:
        mult, val = instr.split("*")
        out = [ val_type(val) ] * int(mult)
    return out


def _depth2coord(dvec, p0, z):
    """
    Calculate X and Y coordinates knowing Z on a 3D line.
    """
    cst = ( z - p0[2] ) / dvec[2]
    return [ dvec[0]*cst + p0[0], dvec[1]*cst + p0[1], z ]


def _translate_points_cells(coord, zcorn, data, nx, ny, nz):
    """
    Import all cells as brick (hexahedron). Some cells can be degenerate
    or empty (i.e. have zero volume). Output mesh might be non-conformal
    (i.e. both adjacent cells do not completely share their common faces). 
    """
    dvec = coord[:,:,:3] - coord[:,:,3:]
    npts = nx * ny * nz * 8
    points = np.reshape([ [ [ [
        _depth2coord(
            dvec[j,i],
            coord[j,i,3:],
            zcorn[2*k,2*j,2*i],
        ),
        _depth2coord(
            dvec[j,i+1],
            coord[j,i+1,3:],
            zcorn[2*k,2*j,2*i+1],
        ),
        _depth2coord(
            dvec[j+1,i+1],
            coord[j+1,i+1,3:],
            zcorn[2*k,2*j+1,2*i+1],
        ),
        _depth2coord(
            dvec[j+1,i],
            coord[j+1,i,3:],
            zcorn[2*k,2*j+1,2*i],
        ),
        _depth2coord(
            dvec[j,i],
            coord[j,i,3:],
            zcorn[2*k+1,2*j,2*i],
        ),
        _depth2coord(
            dvec[j,i+1],
            coord[j,i+1,3:],
            zcorn[2*k+1,2*j,2*i+1],
        ),
        _depth2coord(
            dvec[j+1,i+1],
            coord[j+1,i+1,3:],
            zcorn[2*k+1,2*j+1,2*i+1],
        ),
        _depth2coord(
            dvec[j+1,i],
            coord[j+1,i,3:],
            zcorn[2*k+1,2*j+1,2*i],
        ),
        ] for i in range(nx) ] for j in range(ny) ] for k in range(nz)
    ], newshape = ( npts, 3 ), order = "C")
    cells = { "hexahedron": np.arange(npts).reshape(( npts//8, 8 )) }
    cell_data = { "hexahedron": data }
    return points, cells, cell_data


def _translate_points_cells_conform(coord, zcorn, data, nx, ny, nz,
    z_prec):
    """
    Repair mesh conformity (reconnect adjacent cells) by splitting bricks
    as smaller bricks.
    """
    dvec = coord[:,:,:3] - coord[:,:,3:]
    zcorn = np.round(zcorn, z_prec) if z_prec is not None else zcorn

    # Find all Z corners for all lines in the grid
    zlines = [ [ set() for i in range(nx+1) ] for j in range(ny+1) ]
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                zlines[j][i].add(zcorn[2*k,2*j,2*i])
                zlines[j][i+1].add(zcorn[2*k,2*j,2*i+1])
                zlines[j+1][i+1].add(zcorn[2*k,2*j+1,2*i+1])
                zlines[j+1][i].add(zcorn[2*k,2*j+1,2*i])
                zlines[j][i].add(zcorn[2*k+1,2*j,2*i])
                zlines[j][i+1].add(zcorn[2*k+1,2*j,2*i+1])
                zlines[j+1][i+1].add(zcorn[2*k+1,2*j+1,2*i+1])
                zlines[j+1][i].add(zcorn[2*k+1,2*j+1,2*i])
    zlines = [ [ sorted(l) for l in zl ] for zl in zlines ]

    # Split non-conforming cells into several bricks
    points = []
    cell_data = { "hexahedron": { k: [] for k in data.keys() } }

    ic = 0
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                ic += 1

                # For each cell pillar, find all Z corners
                Z = [
                    [ zl for zl in zlines[j][i]
                    if zcorn[2*k,2*j,2*i] <= zl <= zcorn[2*k+1,2*j,2*i] ],
                    [ zl for zl in zlines[j][i+1]
                    if zcorn[2*k,2*j,2*i+1] <= zl <= zcorn[2*k+1,2*j,2*i+1] ],
                    [ zl for zl in zlines[j+1][i+1]
                    if zcorn[2*k,2*j+1,2*i+1] <= zl <= zcorn[2*k+1,2*j+1,2*i+1] ],
                    [ zl for zl in zlines[j+1][i]
                    if zcorn[2*k,2*j+1,2*i] <= zl <= zcorn[2*k+1,2*j+1,2*i] ],
                ]

                # Get longest pillar array (== # of cells to create + 1)
                zmax = max(Z, key = len)
                nz_max = len(zmax)

                # If nz_max == 1, the cell is empty
                if nz_max == 1:
                    continue
                # If nz_max == 2, the cell is a brick
                elif nz_max == 2:
                    Z = [ z + [ z[-1] ] if len(z) < 2 else z for z in Z ]
                # If nz_max > 2, the cell contains at least 2 bricks
                elif nz_max > 2:
                    for zz in zmax[1:-1]:
                        if abs(zz - zmax[0]) < abs(zz - zmax[-1]):
                            Z = [ [ z[0] ] + z if len(z) < nz_max else z
                                    for z in Z ]
                        else:
                            Z = [ z + [ z[-1] ] if len(z) < nz_max else z
                                    for z in Z ]

                # Make all the surfaces for each corner in the 4 pillars
                surfaces = [ [
                    _depth2coord(
                        dvec[j,i],
                        coord[j,i,:3],
                        z0,
                    ),
                    _depth2coord(
                        dvec[j,i+1],
                        coord[j,i+1,:3],
                        z1,
                    ),
                    _depth2coord(
                        dvec[j+1,i+1],
                        coord[j+1,i+1,:3],
                        z2,
                    ),
                    _depth2coord(
                        dvec[j+1,i],
                        coord[j+1,i,:3],
                        z3,
                    ),
                ] for z0, z1, z2, z3 in zip(*Z) ]

                # Make all the bricks from the surfaces
                for sbot, stop in zip(surfaces[:-1], surfaces[1:]):
                    points.append(sbot + stop)
                    for kk, v in data.items():
                        cell_data["hexahedron"][kk].append(v[ic-1])
                # So far, the cells are possibly degenerate bricks
    
    points = np.concatenate(points)
    npts = len(points)
    cells = { "hexahedron": np.arange(npts).reshape(( npts//8, 8 )) }
    for k, v in cell_data["hexahedron"].items():
        cell_data["hexahedron"][k] = np.array(v)
    return points, cells, cell_data


def _repair_cells(points, cells, cell_data):
    """
    Convert bricks as hexahedra, wedges, pyramids or tetrahedra depending
    on the number of unique points. Repaired mesh may be semi-conformal
    (i.e. at least one cell completely shares its face with its neighbor).
    """
    meshio_types = [ "tetra", "pyramid", "wedge", "hexahedron" ]
    repaired_cells = { mt: [] for mt in meshio_types }
    repaired_cell_data = {
        mt: {
            k: [] for k in cell_data["hexahedron"].keys()
        } for mt in meshio_types
    }
    counter = { mt: 0 for mt in meshio_types }

    # Repair brick if degenerate
    for i, c in enumerate(cells["hexahedron"]):
        brick = _repair_brick(c, points[c])

        for k, v in brick.items():
            for corner in v:
                repaired_cells[k].append(corner)
                counter[k] += 1

        for k, v in cell_data["hexahedron"].items():
            for kk, vv in brick.items():
                repaired_cell_data[kk][k].extend([ v[i] ]*len(vv))

    # Tidy up
    for k, v in counter.items():
        if not v:
            repaired_cells.pop(k, None)
            repaired_cell_data.pop(k, None)

    for k, v in repaired_cells.items():
        repaired_cells[k] = np.array(v)

    for k, v in repaired_cell_data.items():
        for kk, vv in v.items():
            repaired_cell_data[k][kk] = np.array(vv)
    return repaired_cells, repaired_cell_data


def _repair_brick(corner, points):
    """
    Convert a brick as a hexahedron, wedge, pyramid or tetrahedron.
    """
    _, pinv, counts = np.unique(
        points,
        axis = 0,
        return_inverse = True,
        return_counts = True,
    )
    npts = len(counts)

    if npts == 4:
        return {}
    else:
        if npts == 5:
            idx = [ i for i, c in enumerate(counts[pinv]) if c == 1 ]
        else:
            idx = [ i for i, c in enumerate(counts[pinv]) if c > 1 ]
        case = "".join([ str(i) for i in idx ])
        select = _select[npts][case]
        cell_types = { k for k in select.keys() }
        return {
            k: [ corner[c].tolist() for c in select[k] ] for k in cell_types
        }


_select = {
    5: {
        "04": {
            "tetra": [
                [ 0, 1, 2, 4 ],
                [ 0, 2, 3, 4 ],
            ],
            # "pyramid": [ [ 0, 1, 2, 3, 4 ] ],
        },
        "15": {
            "tetra": [
                [ 1, 3, 0, 5 ],
                [ 1, 2, 3, 5 ],
            ],
            # "pyramid": [ [ 1, 2, 3, 0, 5 ] ],
        },
        "26": {
            "tetra": [
                [ 2, 0, 1, 6 ],
                [ 2, 3, 0, 6 ],
            ],
            # "pyramid": [ [ 2, 3, 0, 1, 6 ] ],
        },
        "37": {
            "tetra": [
                [ 3, 0, 1, 7 ],
                [ 3, 1, 2, 7 ],
            ],
            # "pyramid": [ [ 3, 0, 1, 2, 7 ] ],
        },
    },
    6: {
        "1256": {
            "wedge": [ [ 0, 1, 4, 3, 2, 7 ] ],
        },
        "0145": {
            "wedge": [ [ 1, 2, 6, 0, 3, 7 ] ],
        },
        "0347": {
            "wedge": [ [ 0, 1, 5, 3, 2, 6 ] ],
        },
        "2367": {
            "wedge": [ [ 1, 2, 5, 0, 3, 4 ] ],
        },
        "0246": {
            "pyramid": [
                [ 1, 5, 7, 3, 0 ],
                [ 1, 3, 7, 5, 2 ],
            ],
        },
        "1357": {
            "pyramid": [
                [ 0, 2, 6, 4, 1 ],
                [ 0, 4, 6, 2, 3 ],
            ],
        },
    },
    7: {
        "01": {
            "pyramid": [ [ 2, 5, 4, 3, 0 ] ],
            "wedge": [ [ 2, 6, 5, 3, 7, 4 ] ],
        },
        "12": {
            "pyramid": [ [ 3, 6, 5, 0, 1 ] ],
            "wedge": [ [ 3, 7, 6, 0, 4, 5 ] ],
        },
        "23": {
            "pyramid": [ [ 0, 7, 6, 1, 2 ] ],
            "wedge": [ [ 0, 4, 7, 1, 5, 6 ] ],
        },
        "03": {
            "pyramid": [ [ 1, 4, 7, 2, 0 ] ],
            "wedge": [ [ 1, 5, 4, 2, 0, 7 ] ],
        },
        "45": {
            "pyramid": [ [ 0, 1, 6, 7, 4 ] ],
            "wedge": [ [ 1, 2, 6, 0, 3, 7 ] ],
        },
        "56": {
            "pyramid": [ [ 1, 2, 7, 4, 5 ] ],
            "wedge": [ [ 2, 3, 7, 1, 0, 4 ] ],
        },
        "67": {
            "pyramid": [ [ 2, 3, 4, 5, 6 ] ],
            "wedge": [ [ 3, 0, 4, 2, 1, 5 ] ],
        },
        "47": {
            "pyramid": [ [ 3, 0, 5, 6, 4 ] ],
            "wedge": [ [ 0, 1, 5, 3, 2, 6 ] ],
        },
        "04": {
            "pyramid": [ [ 3, 1, 5, 7, 0 ] ],
            "wedge": [ [ 2, 1, 3, 6, 5, 7 ] ],
        },
        "15": {
            "pyramid": [ [ 0, 2, 6, 4, 1 ] ],
            "wedge": [ [ 3, 0, 2, 7, 4, 6 ] ],
        },
        "26": {
            "pyramid": [ [ 1, 3, 7, 5, 2 ] ],
            "wedge": [ [ 0, 1, 3, 4, 5, 7 ] ],
        },
        "37": {
            "pyramid": [ [ 2, 0, 4, 6, 3 ] ],
            "wedge": [ [ 1, 2, 0, 5, 6, 4 ] ],
        },
    },
    8: {
        "": {
            "hexahedron": [ [ 0, 1, 2, 3, 4, 5, 6, 7 ] ],
        },
    },
}


def write(filename, mesh):
    """
    Write Eclipse GRDECL grid file is not supported yet. Eclipse grids
    usually are cartesian grids formatted following a specific order while
    meshio and more general mesh formats are independent of cell order.
    """
    raise NotImplementedError(
        "Writing GRDECL file is not supported."
    )