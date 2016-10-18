""" All unit tests for the file system """

import os
import unittest

from unix_fs import device_io

""" device_io.py """

class DiskClass(unittest.TestCase):

    def setUp(self):
        """ Executed before each test case """
        b = bytearray([12, 12, 12])
        path = 'temp_test_file'
        f = device_io.Disk(path)
        f.open()
        f.write(b)
        f.close()

    def tearDown(self):
        """ Executed after each test case """
        path = 'temp_test_file'
        os.remove(path)

    def test_seek_read(self):
        b = bytearray([12, 12, 12])
        path = 'temp_test_file'
        f = device_io.Disk(path)
        f.open()
        f.seek(0)
        b2 = f.read(len(b))
        f.close()
        self.assertEqual(b, b2)

if __name__ == '__main__':
    unittest.main()