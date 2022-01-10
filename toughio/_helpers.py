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
        return next(self.fiter)

    def next(self):
        """Return next line."""
        return self.__next__()

    def seek(self, i, increment):
        """Set file's position."""
        self.count += increment
        self.f.seek(i)

    def tell(self):
        """Return current position of file."""
        return self.f.tell()
