class FileIterator:
    def __init__(self, f, count=0):
        self.f = f
        self.count = count
        self.fiter = iter(f.readline, "")

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        return self.fiter.__next__()

    def next(self):
        return self.__next__()

    def seek(self, i, increment):
        self.count += increment
        self.f.seek(i)

    def tell(self):
        return self.f.tell()
