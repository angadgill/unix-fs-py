""" All low-level device IO classes and functions """

import io

class Disk(object):
    """ Base class for writing to a raw disk """
    def __init__(self, root):
        self.root = root

    def open(self):
        # Open with binary mode with 0 buffering
        try:
            # Open root path in append binary mode 'rb+'
            self._disk = io.open(self.root, 'rb+', buffering = 0)
        except IOError:
            # If root path does not exist, open in write binary mode
            self._disk = io.open(self.root, 'wb', buffering = 0)

    def close(self):
        self._disk.close()

    def read(self, n):
        """ Read n bytes """
        return self._disk.read(n)

    def write(self, b):
        """ Write bytearray b. Returns int n: number of bytes written """
        n = self._disk.write(b)
        return n  # number of bytes actually written

    def seek(self, pos):
        """ Seek to integer pos. Does not return anything."""
        self._disk.seek(pos)

