""" Unit tests for unix_fs/system.py """

import os
import unittest
from importlib import reload

from unix_fs import device_io
from unix_fs import system
from unix_fs import utils

PATH = 'temp_unit_test_file'


class TestSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reload(device_io)
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
        self.cls.allocate()
        output = self.cls.freelist.list
        self.assertEqual(output, expected)

