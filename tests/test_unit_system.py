""" Unit tests for unix_fs/system.py """

import os
import unittest
from importlib import reload

from unix_fs import device_io
from unix_fs import data_structures as ds
from unix_fs import system
from unix_fs import utils

PATH = 'temp_unit_test_file'


class TestSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reload(device_io)
        reload(ds)
        reload(system)
        reload(utils)


class TestFile(TestSystem):
    def setUp(self):
        open(PATH, 'a').close()
        utils.makefs(PATH)
        self.cls = system.File(device=device_io.Disk(PATH))

    def tearDown(self):
        del self.cls
        os.remove(PATH)

    def test_allocate(self):
        expected = self.cls.freelist.list
        expected[0] = False
        output = self.cls.freelist.list
        self.assertEqual(output, expected)

    def test_write_read_short(self):
        input_text = ''.join(['t' for _ in range(ds.BLOCK_SIZE)])
        self.cls.write(input_text)
        self.cls = system.File(device=device_io.Disk(PATH), index=0)
        self.assertEqual(self.cls.read(), input_text)

    def test_write_read_long(self):
        input_text = ''.join(['t' for _ in range(ds.BLOCK_SIZE*2)])
        self.cls.write(input_text)
        self.cls = system.File(device=device_io.Disk(PATH), index=0)
        self.assertEqual(self.cls.read(), input_text)

    def test_multiple_write_partial_block_read(self):
        input_text1 = ''.join(['t' for _ in range(int(ds.BLOCK_SIZE/2))])
        input_text2 = ''.join(['t' for _ in range(ds.BLOCK_SIZE*2)])
        self.cls.write(input_text1)
        self.cls.write(input_text2)
        self.cls = system.File(device=device_io.Disk(PATH), index=0)
        output = self.cls.read()
        self.assertEqual(output, input_text1+input_text2)

    def test_write_overflow(self):
        input_text = ''.join(['t' for _ in range(ds.BLOCK_SIZE*ds.INODE_NUM_DIRECT_BLOCKS + 1)])
        with self.assertRaises(Exception):
            self.cls.write(input_text)
