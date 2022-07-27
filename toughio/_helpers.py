import numpy as np


class FileIterator:
    def __init__(self, f, count=0):
        """File iterator helper class."""
        self.f = f
        self.count = count
        self.fiter = iter(f.readline, "")

    def __iter__(self):
        """Return iterator."""
        return self

    def __next__(self):
        """Return next item."""
        self.count += 1
        self.line = next(self.fiter)
        return self.line

    def next(self, skip_empty=False, comments=None):
        """Return next line."""
        if skip_empty:
            while True:
                line = self.__next__().strip()

                if comments:
                    if line and not line.startswith(comments):
                        self.line = line
                        return line

                elif line:
                    self.line = line
                    return line

        elif comments:
            while True:
                line = self.__next__().strip()

                if not line.startswith(comments):
                    self.line = line
                    return line

        else:
            self.line = self.__next__()
            return self.line

    def seek(self, i, increment):
        """Set file's position."""
        self.count += increment
        self.f.seek(i)

    def tell(self):
        """Return current position of file."""
        return self.f.tell()


def convert_labels(labels, zeros_to_spaces=True):
    """
    Convert non-leading characters.

    Parameters
    ----------
    labels : list of str
        List of labels to convert.
    zeros_to_spaces: bool, optional, default True
        If `True`, convert non-leading zeros to whitespaces. Otherwise, convert non-leading whitespaces to zeros.

    Note
    ----
    This function aims to help transitionning to labeling convention introduced in v1.9.0.

    """

    def convert(label, char_in, char_out):
        prefix, suffix = label[:3], label[3:]
        fmt = f"{{:{char_out}>{len(label) - 3}}}"

        label = prefix + fmt.format(suffix.lstrip(char_in))
        if label[-1] == char_out:
            label = label[:-1] + char_in

        return label

    if zeros_to_spaces:
        char_in, char_out = "0", " "

    else:
        char_in, char_out = " ", "0"

    return np.array([convert(label, char_in, char_out) for label in labels])
