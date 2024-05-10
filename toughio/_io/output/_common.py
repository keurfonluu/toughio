from abc import ABC, abstractmethod
import logging

import numpy as np

__all__ = [
    "Output",
]


class Output(ABC):
    def __init__(self, time, data, labels=None):
        """
        Base class for output data.

        Do not use.

        """
        self._time = time
        self._data = data
        self._labels = list(labels) if labels is not None else labels

    @abstractmethod
    def __getitem__(self):
        """Slice output."""
        pass
    
    @abstractmethod
    def index(self):
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
            
            self._labels = list(value)

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

    def index(self, label):
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
        super().index()
        
        return self.labels.index(label)


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
                islice = [
                    i for i, (label1, label2) in enumerate(self.labels)
                    if label1 == islice or label2 == islice
                ]

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

    def index(self, label1, label2):
        """
        Get index of connection.
        
        Parameters
        ----------
        label1 : str
            Label of first element of connection.
        label2 : str
            Label of second element of connection.

        Returns
        -------
        int
            Index of connection.
        
        """
        super().index()
        labels = ["".join(label) for label in self.labels]

        return labels.index(f"{label1}{label2}")


def to_output(file_type, labels_order, headers, times, labels, data):
    """Helper function to create output data objects."""
    outputs = []
    for time, labels_, data_ in zip(times, labels, data):
        kwargs = {
            "time": time,
            "labels": labels_ if labels_ is not None and len(labels_) else None,
            "data": {k: v for k, v in zip(headers, np.transpose(data_))},
        }

        output = ElementOutput(**kwargs) if file_type == "element" else ConnectionOutput(**kwargs)
        outputs.append(output)

    # Some older versions of TOUGH3 have duplicate connection outputs when running in parallel
    # Fix the outputs here by summing the duplicate connections
    if file_type == "connection" and len(labels[0]):
        # Check whether there are duplicate connections
        connections = {}
        found_duplicate = False

        for i, (c1, c2) in enumerate(outputs[0].labels):
            if (c1, c2) in connections:
                connections[(c1, c2)].append(i)
                found_duplicate = True

            else:
                connections[(c1, c2)] = [i]

        if found_duplicate:
            logging.warning(
                "Found duplicate connections. Fixing outputs by summing duplicate connections."
            )

            for output in outputs:
                output.labels = list(connections)
                output.data = {
                    k: np.array([v[idx].sum() for idx in connections.values()])
                    for k, v in output.data.items()
                }

    if file_type == "element" and labels_order is not None:
        outputs = [output[labels_order] for output in outputs]

    return outputs[0] if len(outputs) == 1 else outputs
