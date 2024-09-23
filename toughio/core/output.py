from abc import ABC, abstractmethod

import os
import numpy as np

__all__ = [
    "ConnectionOutput",
    "ElementOutput",
    "Output",
]


class Output(ABC):
    def __init__(self, time, data, labels=None):
        """
        Base class for output data.

        Do not use.

        """
        self.time = time
        self.data = data
        self.labels = labels

    @abstractmethod
    def __getitem__(self, islice):
        """Slice output."""
        raise NotImplementedError()

    @abstractmethod
    def index(self, label, *args, **kwargs):
        """Get index of element or connection."""
        if self.labels is None:
            raise AttributeError()

    @property
    def n_data(self):
        """Return number of data points."""
        return len(self.data[list(self.data)[0]])

    @property
    def time(self):
        """Return time step (in seconds)."""
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def data(self):
        """Return data arrays."""
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def labels(self):
        """Return labels."""
        return self._labels

    @labels.setter
    def labels(self, value):
        if value is not None:
            if len(value) != self.n_data:
                raise ValueError()

            self._labels = np.asarray(value)

        else:
            self._labels = None


class ElementOutput(Output):
    def __init__(self, time, data, labels=None):
        """
        Element output data.

        Parameters
        ----------
        time : scalar
            Time step (in seconds).
        data : dict
            Data arrays.
        labels : sequence of str or None, default, None
            Labels of elements.

        """
        super().__init__(time, data, labels)

    def __getitem__(self, islice):
        """
        Slice element output.

        Parameters
        ----------
        islice : int, str, slice, sequence of int or sequence of str
            Indices or labels of elements to slice.

        Returns
        -------
        dict or :class:`toughio.ElementOutput`
            Sliced element outputs.

        """
        if self.labels is None:
            raise AttributeError()

        if np.ndim(islice) == 0:
            if isinstance(islice, slice):
                islice = np.arange(self.n_data)[islice]

            else:
                islice = self.index(islice) if isinstance(islice, str) else islice

                return {k: v[islice] for k, v in self.data.items()}

        elif np.ndim(islice) == 1:
            islice = [self.index(i) if isinstance(i, str) else i for i in islice]

        else:
            raise ValueError()

        return ElementOutput(
            self.time,
            {k: v[islice] for k, v in self.data.items()},
            [self._labels[i] for i in islice],
        )

    def index(self, label, *args, **kwargs):
        """
        Get index of element.

        Parameters
        ----------
        label : str
            Label of element.

        Returns
        -------
        int
            Index of element.

        """
        super().index(label, *args, **kwargs)

        return np.flatnonzero(self.labels == label)[0]


class ConnectionOutput(Output):
    def __init__(self, time, data, labels=None):
        """
        Connection output data.

        Parameters
        ----------
        time : scalar
            Time step (in seconds).
        data : dict
            Data arrays.
        labels : sequence of str or None, default, None
            Labels of connections.

        """
        super().__init__(time, data, labels)

    def __getitem__(self, islice):
        """
        Slice connection output.

        Parameters
        ----------
        islice : int, str, slice, sequence of int or sequence of str
            Indices or labels of connections to slice.

        Returns
        -------
        dict or :class:`toughio.ConnectionOutput`
            Sliced connection outputs.

        """
        if self.labels is None:
            raise AttributeError()

        if np.ndim(islice) == 0:
            if isinstance(islice, str):
                islice = np.flatnonzero((self.labels == islice).any(axis=1))

            elif isinstance(islice, slice):
                islice = np.arange(self.n_data)[islice]

            else:
                return {k: v[islice] for k, v in self.data.items()}

        elif np.ndim(islice) <= 2:
            islice = [self.index(*i) if np.ndim(i) == 1 else i for i in islice]

        else:
            raise ValueError()

        return ConnectionOutput(
            self.time,
            {k: v[islice] for k, v in self.data.items()},
            [self._labels[i] for i in islice],
        )

    def index(self, label, label2=None, *args, **kwargs):
        """
        Get index of connection.

        Parameters
        ----------
        label : str
            Label of connection or label of first element of connection.
        label2 : str or None, optional, default None
            Label of second element of connection (if `label` is the label of the first element).

        Returns
        -------
        int
            Index of connection.

        """
        super().index(label, *args, **kwargs)
        labels = ["".join(label) for label in self.labels]

        if label2 is not None:
            label = f"{label}{label2}"

        return labels.index(label)

    def to_element(self, mesh, ignore_elements=None):
        """
        Project connection data to element centers.

        Parameters
        ----------
        mesh : dict or pathlike
            Mesh parameters or file name.
        ignore_elements : sequence of str, optional
            Labels of elements to ignore.

        Returns
        -------
        :class:`toughio.ElementOutput`
            Element output with projected data.

        References
        ----------
        .. [1] Painter, S. L., Gable, C. W., and Kelkar, S. (2012). "Pathline tracing on fully unstructured control-volume grids". Computational Geosciences, 16(4), 1125-1134
        
        """
        from .. import read_input

        if isinstance(mesh, (str, os.PathLike)):
            mesh = read_input(mesh, file_format="tough", blocks=["ELEME", "CONNE"])

        ignore_elements = set(ignore_elements) if ignore_elements is not None else set()
        centers = {
            k: np.asarray(v["center"]) for k, v in mesh["elements"].items()
            if k not in ignore_elements
        }
        face_areas = {k: v["interface_area"] for k, v in mesh["connections"].items()}
        labels = list(centers)

        # Gather all data to build linear systems to solve
        data = np.row_stack(list(self.data.values()))
        connections = {
            label: {
                "index": [],
                "areas": [],
                "normals": [],
            }
            for label in labels
        }

        for i, (l1, l2) in enumerate(self.labels):
            if l1 in ignore_elements or l2 in ignore_elements:
                continue

            area = face_areas[f"{l1}{l2}"]
            normal = centers[l1] - centers[l2]
            normal /= np.linalg.norm(normal)

            connections[l1]["index"].append(i)
            connections[l1]["areas"].append(area)
            connections[l1]["normals"].append(normal)

            connections[l2]["index"].append(i)
            connections[l2]["areas"].append(area)
            connections[l2]["normals"].append(normal)

        connections = [
            {k: np.array(v) for k, v in connection.items()}
            for connection in connections.values()
        ]

        # Approximate connection data
        Q = np.zeros((len(centers), 3, len(data)))

        for i, connection in enumerate(connections):
            G = connection["areas"][:, np.newaxis] * connection["normals"]
            Q[i] = np.linalg.pinv(G.T @ G) @ G.T @ data[:, connection["index"]].T

        return ElementOutput(
            time=self.time,
            data={
                k: v for k, v in zip(self.data, Q.transpose((2, 0, 1)))
                if k not in {"X", "Y", "Z"}
            },
            labels=labels,
        )
