import meshio
import numpy as np
import pyvista as pv
from joblib import Parallel, delayed

from .._mesh import Mesh


class ParticleTracker:
    """
    Particle tracer class.
    
    Parameters
    ----------
    mesh : :class:`toughio.Mesh` | :class:`meshio.Mesh` | :class:`pyvista.UnstructuredGrid`
        Input mesh.
    velocity : str | ArrayLike
        Velocity field data.

    """
    def __init__(self, mesh, velocity):
        """Initialize a particle tracker."""
        self.mesh = mesh
        self.velocity = velocity

    def get_velocity(self, point):
        """
        Get velocity vector at any point in mesh.

        Parameters
        ----------
        point : ArrayLike
            Coordinates of query point.
        
        Returns
        -------
        ArrayLike
            Velocity vector at query point.

        """
        return pv.PolyData(point).sample(self.mesh)["velocity"][0]

    def track(
        self,
        particles,
        direction="forward",
        step_size=None,
        time_ini=None,
        max_step=None,
        max_time=None,
        max_length=None,
        end_points=None,
        radius=None,
        window_length=None,
    ):
        """
        Track particle(s) given starting point coordinates.

        Parameters
        ----------
        particles : ArrayLike
            Starting point coordinates of particle(s) to track.
        direction : {'forward', 'backward'}, optional, default 'forward'
            Direction of integration.
        step_size : scalar, optional, default 1.0
            Pathline step size at each time step (in m).
        time_ini : scalar, optional, default 0.0
            Initial time step (in second).
        max_step : int, optional, default 10000
            Maximum number of steps.
        max_time : scalar, optional, default np.inf
            Maximum time of pathline ending point.
        max_length : scalar, optional, default np.inf
            Maximum length of pathline.
        end_points : ArrayLike, optional
            Ending point coordinates.
        radius : scalar, optional, default 1.0
            Ending point radius (in m). The tracking algorithm stops if the pathline is within `radius` meters of an ending point.
        window_length : int, optional, default 32
            Window length for oscillation detection.

        Returns
        -------
        ArrayLike | list[ArrayLike]
            Output pathline(s).

        """
        step_size = step_size if step_size is not None else 1.0
        time_ini = time_ini if time_ini is not None else 0.0
        max_step = max_step if max_step is not None else 10000
        max_time = max_time if max_time is not None else np.inf
        max_length = max_length if max_length is not None else np.inf
        end_points = np.asarray(end_points) if end_points is not None else []
        radius = radius if radius is not None else 1.0
        window_length = window_length if window_length is not None else 32

        if direction == "forward":
            direction = 1.0

        elif direction == "backward":
            direction = -1.0

        else:
            raise ValueError(f"invalid direction '{direction}'")

        args = (
            direction,
            step_size,
            time_ini,
            max_step,
            max_time,
            max_length,
            end_points,
            radius,
            window_length,
        )

        if np.ndim(particles) == 1:
            return self._track(particles, *args)

        elif np.ndim(particles) == 2:
            with Parallel(n_jobs=-1, prefer="threads") as parallel:
                out = parallel(
                    delayed(self._track)(particle, *args)
                    for particle in particles
                )

            return out

        else:
            raise ValueError()

    def _track(
        self,
        particle,
        direction,
        step_size,
        time_ini,
        max_step,
        max_time,
        max_length,
        end_points,
        radius,
        window_length,
    ):
        """Track a particle."""
        x, y, z = particle
        path = np.empty((max_step + 1, 3))
        time = np.empty(max_step + 1)
        path[0] = x, y, z
        time[0] = time_ini
        length = 0.0

        count = 1
        while True:
            in_end_point = False
            exceed_max_time = False
            exceed_max_length = False

            v = self.get_velocity(path[count - 1]) * direction
            vn = np.linalg.norm(v)
            dx = step_size
            dt = dx / vn

            if time[-1] + dt >= max_time:
                exceed_max_time = True
                dt = max_time - time[-1]
                v *= dt

            elif length + dx >= max_length:
                exceed_max_length = True
                dx = max_length - length
                v *= dx / vn

            else:
                v *= dt

            x += v[0]
            y += v[1]
            z += v[2]
            path[count] = x, y, z
            time[count] = time[count - 1] + dt
            length += dx

            # Stop is maximum tracking time is reached
            if exceed_max_time:
                break

            # Stop if maximum path length is reached
            if exceed_max_length:
                break

            # Stop if maximum number of iteration is reached
            if count >= max_step:
                break

            # Stop if particle is out of bound
            if self.mesh.find_containing_cell(path[count]) == -1:
                break

            # Stop if oscillation is detected
            # Oscillation is here characterized by fast changes in particle's direction (the particle is going back and forth)
            # This usually results in rapid changes in the sign of the difference of its position between two consecutive steps
            if count >= window_length:
                if (
                    np.abs(
                        np.sign(
                            np.diff(path[count - window_length : count], axis=0)
                        ).mean(axis=0)
                    )
                    < 0.5
                ).all():
                    break

            # Stop if particle is within distance of specified ending points
            for end_point in end_points:
                if np.linalg.norm(path[-1] - end_point) <= radius:
                    in_end_point = True
                    break

            if in_end_point:
                break

            count += 1

        return path[: count + 1]

    @property
    def mesh(self):
        """Return mesh."""
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        """Set mesh."""
        if isinstance(value, Mesh):
            self._mesh = value.to_pyvista()

        elif isinstance(value, meshio.Mesh):
            self._mesh = pv.from_meshio(value)

        elif isinstance(value, pv.UnstructuredGrid):
            self._mesh = value.copy(deep=True)

        else:
            raise ValueError("invalid input mesh")

    @property
    def velocity(self):
        """Return velocity field data."""
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        """Set velocity field data."""
        if isinstance(value, str):
            if value not in self.mesh.cell_data:
                raise ValueError(f"invalid velocity data '{value}'")

            velocity = self.mesh.cell_data[value]

        elif isinstance(value, np.ndarray):
            if value.shape != (self.mesh.n_cells, 3):
                raise ValueError(f"velocity array size mismatch (expected {(self.mesh.n_cells, 3)}, got {value.shape})")

            velocity = value

        else:
            raise ValueError("invalid velocity data")

        self.mesh.clear_data()
        self.mesh.cell_data["velocity"] = velocity
        self.mesh = self.mesh.cell_data_to_point_data()
