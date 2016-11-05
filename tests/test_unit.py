""" All unit tests for the file system """

import os
import unittest

from unix_fs import device_io
from unix_fs import data_structures as ds

PATH = 'temp_unit_test_file'

""" device_io.py """


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

    def test_seek_read(self):
        b = bytearray([12, 12, 12])
        f = device_io.Disk(PATH)
        f.open()
        f.seek(0)
        b2 = f.read(len(b))
        f.close()
        self.assertEqual(b, b2)

""" data_structure.py """

class  TestBlock(unittest.TestCase):

    def setUp(self):
        open(PATH, 'a').close()  # create file
        disk = device_io.Disk(PATH)
        self.block = ds.Block(device=disk)

    def tearDown(self):
        os.remove(PATH)  # delete file

    def test_pad_bytes_to_block(self):
        ds.BLOCK_SIZE = 10
        d = self.block.pad_bytes_to_block(bytes(1))
        self.assertEqual(len(d), ds.BLOCK_SIZE)

    def test_int_list_to_bytes_no_padding_1(self):
        ds.ADDRESS_LENGTH = 4
        int_list = [1, 2, 3, 4]
        expected = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'
        output = self.block.int_list_to_bytes(int_list, pad=False)
        self.assertEqual(output, expected)

    def test_int_list_to_bytes_no_padding_2(self):
        ds.ADDRESS_LENGTH = 2
        int_list = [1, 2, 3, 4]
        expected = b'\x01\x00\x02\x00\x03\x00\x04\x00'
        output = self.block.int_list_to_bytes(int_list, pad=False)
        self.assertEqual(output, expected)

    def test_int_list_to_bytes_with_padding_1(self):
        ds.BLOCK_SIZE = 10
        ds.ADDRESS_LENGTH = 4
        int_list = [1, 2]
        expected = b'\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00'
        output = self.block.int_list_to_bytes(int_list, pad=True)
        self.assertEqual(output, expected)

    def test_int_list_to_bytes_with_padding_2(self):
        ds.BLOCK_SIZE = 15
        ds.ADDRESS_LENGTH = 4
        int_list = [1, 2]
        expected = b'\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        output = self.block.int_list_to_bytes(int_list, pad=True)
        self.assertEqual(output, expected)

if __name__ == '__main__':
    unittest.main()