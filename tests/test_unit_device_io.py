""" All unit tests for unix_fs/device_io """

import os
import unittest

from unix_fs import device_io

PATH = 'temp_unit_test_file'


class TestDisk(unittest.TestCase):
    def setUp(self):
        """ Executed before each test case """
        open(PATH, 'a').close()  # create file
        b = bytearray([12, 12, 12])
        f = device_io.Disk(PATH)
        f.open()
        f.write(b)
        f.close()

    def tearDown(self):
        """ Executed after each test case """
        os.remove(PATH)

    # def test_seek_read(self):
    #     b = bytearray([12, 12, 12])
    #     f = device_io.Disk(PATH)
    #     f.open()
    #     f.seek(0)
    #     b2 = f.read(len(b))
    #     f.close()
    #     self.assertEqual(b, b2)
    #
