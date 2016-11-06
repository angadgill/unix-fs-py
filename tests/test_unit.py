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

    # def test_seek_read(self):
    #     b = bytearray([12, 12, 12])
    #     f = device_io.Disk(PATH)
    #     f.open()
    #     f.seek(0)
    #     b2 = f.read(len(b))
    #     f.close()
    #     self.assertEqual(b, b2)
    #

""" data_structure.py """


class TestBase(unittest.TestCase):
    def setUp(self):
        self.cls = ds.Base()

    def tearDown(self):
        del self.cls

    def test_pad_bytes_to_block_1(self):
        ds.BLOCK_SIZE = 5
        expected = b'\x00\x00\x00\x00\x00'
        output = self.cls.pad_bytes_to_block(bytes(1))
        self.assertEqual(output, expected)

    def test_pad_bytes_to_block_2(self):
        ds.BLOCK_SIZE = 10
        expected = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        output = self.cls.pad_bytes_to_block(bytes(1))
        self.assertEqual(output, expected)

    def test_int_to_byte_1(self):
        ds.ADDRESS_LENGTH = 4
        expected = b'\x02\x00\x00\x00'
        output = self.cls.int_to_bytes(2)
        self.assertEqual(output, expected)

    def test_int_list_to_bytes_no_padding_1(self):
        ds.ADDRESS_LENGTH = 4
        int_list = [1, 2, 3, 4]
        expected = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'
        output = self.cls.int_list_to_bytes(int_list, pad=False)
        self.assertEqual(output, expected)

    def test_int_list_to_bytes_no_padding_2(self):
        ds.ADDRESS_LENGTH = 2
        int_list = [1, 2, 3, 4]
        expected = b'\x01\x00\x02\x00\x03\x00\x04\x00'
        output = self.cls.int_list_to_bytes(int_list, pad=False)
        self.assertEqual(output, expected)

    def test_int_list_to_bytes_with_padding_1(self):
        ds.BLOCK_SIZE = 10
        ds.ADDRESS_LENGTH = 4
        int_list = [1, 2]
        expected = b'\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00'
        output = self.cls.int_list_to_bytes(int_list, pad=True)
        self.assertEqual(output, expected)

    def test_int_list_to_bytes_with_padding_2(self):
        ds.BLOCK_SIZE = 15
        ds.ADDRESS_LENGTH = 4
        int_list = [1, 2]
        expected = b'\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        output = self.cls.int_list_to_bytes(int_list, pad=True)
        self.assertEqual(output, expected)

    def test_bytes_to_int_4_bytes(self):
        expected = 2
        output = self.cls.bytes_to_int(b'\x02\x00\x00\x00')
        self.assertEqual(output, expected)

    def test_bytes_to_int_8_bytes(self):
        expected = 4
        output = self.cls.bytes_to_int(b'\x04\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(output, expected)

    def test_bytes_to_byte_list(self):
        expected = [b'\x01\x00', b'\x02\x00', b'\x03\x00', b'\x04\x00']
        output = self.cls.bytes_to_byte_list(b'\x01\x00\x02\x00\x03\x00\x04\x00', 2)
        self.assertEqual(output, expected)

    def test_bytes_to_int_list_no_padding(self):
        ds.ADDRESS_LENGTH = 4
        expected = [1, 2, 3, 4]
        input_data = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'
        output = self.cls.bytes_to_int_list(input_data)
        self.assertEqual(output, expected)

    def test_bytes_to_int_list_with_padding(self):
        ds.ADDRESS_LENGTH = 4
        expected = [1, 2, 3, 4, 0]  # extra int added by padding
        input_data = b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00'
        output = self.cls.bytes_to_int_list(input_data)
        self.assertEqual(output, expected)

    def test_str_to_bytes_no_padding(self):
        input_str = 'tests message'
        expected = b'\x74\x65\x73\x74\x73\x20\x6D\x65\x73\x73\x61\x67\x65'
        output = self.cls.str_to_bytes(input_str, pad_to=0)
        self.assertEqual(output, expected)

    def test_str_to_bytes_with_padding_1(self):
        input_str = 'tests message'
        expected = b'\x74\x65\x73\x74\x73\x20\x6D\x65\x73\x73\x61\x67\x65\x20\x20'
        output = self.cls.str_to_bytes(input_str, pad_to=15)
        self.assertEqual(output, expected)

    def test_str_to_bytes_with_padding_2(self):
        input_str = 'tests message'
        expected = b'\x74\x65\x73\x74\x73\x20\x6D\x65\x73\x73\x61\x67\x65'
        output = self.cls.str_to_bytes(input_str, pad_to=5)
        self.assertEqual(output, expected)

    def test_str_list_to_bytes_no_padding(self):
        input_list = ['this', 'is', 'a', 'test']
        expected = b'\x74\x68\x69\x73\x69\x73\x61\x74\x65\x73\x74'
        output = self.cls.str_list_to_bytes(input_list, pad_to=0)
        self.assertEqual(output, expected)

    def test_str_list_to_bytes_with_padding(self):
        input_list = ['this', 'is', 'a', 'test']
        expected = b'\x74\x68\x69\x73\x20\x69\x73\x20\x20\x20\x61\x20\x20\x20\x20\x74\x65\x73\x74\x20'
        output = self.cls.str_list_to_bytes(input_list, pad_to=5)
        self.assertEqual(output, expected)

    def test_bytes_to_str_no_zeros(self):
        expected = 'this'
        output = self.cls.bytes_to_str(b'\x74\x68\x69\x73')
        self.assertEqual(output, expected)

    def test_bytes_to_str_with_zeros(self):
        expected = 'this'
        output = self.cls.bytes_to_str(b'\x74\x68\x69\x73\x00\x00\x00\x00\x00', strip='\x00')
        self.assertEqual(output, expected)

    def test_bytes_to_str_with_spaces(self):
        expected = 'this'
        output = self.cls.bytes_to_str(b'\x74\x68\x69\x73\x20\x20\x20\x20\x20', strip='\x20')
        self.assertEqual(output, expected)

    def test_bytes_to_str_list(self):
        ds.MAX_FILENAME_LENGTH = 5
        input_data = b'\x74\x68\x69\x73\x20\x69\x73\x20\x20\x20\x61\x20\x20\x20\x20\x74\x65\x73\x74\x20'
        expected = ['this', 'is', 'a', 'test']
        output = self.cls.bytes_to_str_list(input_data)
        self.assertEqual(output, expected)


class TestSuperBlock(unittest.TestCase):
    def setUp(self):
        self.cls = ds.SuperBlock()
        open(PATH, 'a').close()

    def tearDown(self):
        del self.cls
        os.remove(PATH)

    def test_bytes(self):
        ds.BLOCK_SIZE = 30
        self.cls = ds.SuperBlock()
        expected = b'\x1e\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        output = bytes(self.cls)
        self.assertEqual(output, expected)

    def test_decode_1(self):
        ds.BLOCK_SIZE = 0  # precaution
        self.cls = ds.SuperBlock()
        input_data = b'\x1e\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        expected = [30, 10]
        output = self.cls.__decode__(input_data)
        self.assertEqual(output, expected)

    def test_decode_2(self):
        ds.BLOCK_SIZE = 0  # precaution
        self.cls = ds.SuperBlock()
        input_data = b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        expected = [10, 10]
        output = self.cls.__decode__(input_data)
        self.assertEqual(output, expected)

    def test_decode_no_device(self):
        ds.BLOCK_SIZE = 0  # precaution
        self.cls = ds.SuperBlock(None)
        input_data = b'\x1e\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        expected = [30, 10]
        output = self.cls.__decode__(input_data)
        self.assertEqual(output, expected)

    def test_read_1(self):
        ds.BLOCK_SIZE = 0  # precaution
        input_data = b'\x1e\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        device = device_io.Disk(PATH)
        self.cls = ds.SuperBlock(device)
        self.assertEqual(self.cls.block_size, 30)
        self.assertEqual(self.cls.num_inodes, 10)

    def test_read_2(self):
        ds.BLOCK_SIZE = 0  # precaution
        input_data = b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        device = device_io.Disk(PATH)
        self.cls = ds.SuperBlock(device)
        self.assertEqual(self.cls.block_size, 10)
        self.assertEqual(self.cls.num_inodes, 10)

    def test_write_1(self):
        ds.BLOCK_SIZE = 30
        device_io.BLOCK_SIZE = 30
        ds.NUM_INODES = 10
        expected = b'\x1e\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.cls = ds.SuperBlock(None)
        self.cls._device = device_io.Disk(PATH)
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

    def test_write_2(self):
        ds.BLOCK_SIZE = 20
        device_io.BLOCK_SIZE = 20
        device_io.BLOCK_SIZE = 20
        ds.NUM_INODES = 10
        expected = b'\x14\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x0A\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x00\x00\x00\x00'
        self.cls = ds.SuperBlock(None)
        self.cls._device = device_io.Disk(PATH)
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)


class TestInode(unittest.TestCase):
    def setUp(self):
        ds.BLOCK_SIZE = 50
        device_io.BLOCK_SIZE = 50
        ds.INODE_NUM_DIRECT_BLOCKS = 5
        ds.NUM_INODES = 10
        self.cls = ds.Inode()
        open(PATH, 'a').close()

    def tearDown(self):
        del self.cls
        os.remove(PATH)

    def test_bytes(self):
        self.cls = ds.Inode()
        self.cls.index = 2
        self.cls.i_type = 1
        self.cls.address_direct = [1, 2, 3, 4, 5]
        expected = b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x02\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x03\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x04\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        output = bytes(self.cls)
        self.assertEqual(output, expected)

    def test_write_1(self):
        expected = bytes(ds.BLOCK_SIZE)+ \
                   b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x02\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x03\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x04\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.cls = ds.Inode(device=device_io.Disk(PATH))
        self.cls.index = 0
        self.cls.i_type = 1
        self.cls.address_direct = [1, 2, 3, 4, 5]
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

    def test_write_2(self):
        expected = bytes(ds.BLOCK_SIZE * 3)+ \
                   b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x02\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x03\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x04\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.cls = ds.Inode(device=device_io.Disk(PATH))
        self.cls.index = 2
        self.cls.i_type = 1
        self.cls.address_direct = [1, 2, 3, 4, 5]
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

    def test_read_1(self):
        input_data = bytes(ds.BLOCK_SIZE ) + \
                     b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x02\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x03\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x04\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        expected = [1, 1, 2, 3, 4, 5]
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.Inode(device=device_io.Disk(PATH), index=0)
        output = self.cls._items
        self.assertEqual(output, expected)

    def test_read_2(self):
        input_data = bytes(ds.BLOCK_SIZE * 3) + \
                     b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x01\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x02\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x03\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x04\x00\x00\x00\x00\x00\x00\x00' + \
                     b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        expected = [1, 1, 2, 3, 4, 5]
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.Inode(device=device_io.Disk(PATH), index=2)
        output = self.cls._items
        self.assertEqual(output, expected)

    def test_allocate_with_device(self):
        input_data = bytes(ds.BLOCK_SIZE) + \
                     bytes(ds.NUM_INODES * ds.BLOCK_SIZE) + \
                     bytes(ds.InodeFreeList())
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.Inode(device=device_io.Disk(PATH))
        self.assertEqual(self.cls.index, None)  # New inode should have a None index
        self.cls.allocate()
        self.assertEqual(self.cls.index, 0)
        with self.assertRaises(Exception):
            self.cls.allocate()

    def test_deallocate_with_device(self):
        input_data = bytes(ds.BLOCK_SIZE) + \
                     bytes(ds.NUM_INODES * ds.BLOCK_SIZE) + \
                     bytes(ds.InodeFreeList())
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.Inode(device=device_io.Disk(PATH))
        self.assertEqual(self.cls.index, None)  # New inode should have a None index
        self.cls.allocate()
        self.assertEqual(self.cls.index, 0)
        self.cls.deallocate()
        self.assertEqual(self.cls.index, None)
        with self.assertRaises(Exception):
            self.cls.deallocate()


class TestFreeList(unittest.TestCase):
    def setUp(self):
        ds.BLOCK_SIZE = 20
        device_io.BLOCK_SIZE = 20
        self.cls = ds.FreeList(n=10)
        open(PATH, 'a').close()

    def tearDown(self):
        del self.cls
        os.remove(PATH)

    def test_bytes(self):
        expected = b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        output = bytes(self.cls)
        self.assertEqual(output, expected)

    def test_read(self):
        input_data = b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.FreeList(n=10, device=device_io.Disk(PATH))
        output = self.cls.list
        expected = [True] * 10
        self.assertEqual(output, expected)

    def test_write(self):
        expected = b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.cls._device = device_io.Disk(PATH)
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

    def test_allocate_no_device_1(self):
        _ = self.cls.allocate(write_back=False)
        output = self.cls.list
        expected = [False] + [True]*9
        self.assertEqual(output, expected)

    def test_allocate_no_device_2(self):
        for i in range(3):
            _ = self.cls.allocate(write_back=False)
        output = self.cls.list
        expected = [False]*3 + [True]*7
        self.assertEqual(output, expected)

    def test_allocate_no_device_3(self):
        # over allocate
        with self.assertRaises(Exception):
            for _ in range(11):
                i = self.cls.allocate(write_back=False)

    def test_deallocate_no_device(self):
        for i in range(2):
            _ = self.cls.allocate(write_back=False)
        self.cls.deallocate(index=0, write_back=False)
        output = self.cls.list
        expected = [True, False] + [True]*8
        self.assertEqual(output, expected)

    def test_allocate_with_device(self):
        input_data = b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.FreeList(n=10, device=device_io.Disk(PATH))
        for i in range(3):
            _ = self.cls.allocate(write_back=False)
        output = self.cls.list
        expected = [False]*3 + [True]*7
        self.assertEqual(output, expected)

    def test_deallocate_with_device(self):
        input_data = b'\x00\x00\x00\x00\x01\x01\x01\x01\x01\x01' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.FreeList(n=10, device=device_io.Disk(PATH))
        self.cls.deallocate(index=1)
        output = self.cls.list
        expected = [False, True, False, False] + [True]*6
        self.assertEqual(output, expected)


class TestInodeFreeList(TestFreeList):
    def setUp(self):
        ds.BLOCK_SIZE = 20
        device_io.BLOCK_SIZE = 20
        ds.NUM_INODES = 10
        self.cls = ds.InodeFreeList()
        open(PATH, 'a').close()

    def test_write(self):
        expected = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                   b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.cls._device = device_io.Disk(PATH)
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

    def test_allocate_with_device(self):
        input_data = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                     b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.InodeFreeList(device=device_io.Disk(PATH))
        for i in range(3):
            _ = self.cls.allocate(write_back=False)
        output = self.cls.list
        expected = [False]*3 + [True]*7
        self.assertEqual(output, expected)

    def test_deallocate_with_device(self):
        input_data = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                     b'\x00\x00\x00\x00\x01\x01\x01\x01\x01\x01' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.InodeFreeList(device=device_io.Disk(PATH))
        self.cls.deallocate(index=1)
        output = self.cls.list
        expected = [False, True, False, False] + [True]*6
        self.assertEqual(output, expected)


class TestDataBlockFreelist(TestFreeList):
    def setUp(self):
        ds.BLOCK_SIZE = 20
        device_io.BLOCK_SIZE = 20
        ds.NUM_DATA_BLOCKS = 10
        self.cls = ds.DataBlockFreeList()
        open(PATH, 'a').close()

    def test_write(self):
        expected = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                   b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.cls._device = device_io.Disk(PATH)
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

    def test_allocate_with_device(self):
        input_data = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                     b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.DataBlockFreeList(device=device_io.Disk(PATH))
        for i in range(3):
            _ = self.cls.allocate(write_back=False)
        output = self.cls.list
        expected = [False]*3 + [True]*7
        self.assertEqual(output, expected)

    def test_deallocate_with_device(self):
        input_data = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                     b'\x00\x00\x00\x00\x01\x01\x01\x01\x01\x01' + \
                     b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.DataBlockFreeList(device=device_io.Disk(PATH))
        self.cls.deallocate(index=1)
        output = self.cls.list
        expected = [False, True, False, False] + [True]*6
        self.assertEqual(output, expected)


class TestDirectoryBlock(unittest.TestCase):
    def setUp(self):
        ds.BLOCK_SIZE = device_io.BLOCK_SIZE = 10
        ds.NUM_DATA_BLOCKS = 10
        ds.MAX_FILENAME_LENGTH = 5
        ds.NUM_FILES_PER_DIR = 5
        self.cls = ds.DirectoryBlock()
        open(PATH, 'a').close()

    def tearDown(self):
        del self.cls
        os.remove(PATH)

    def test_bytes(self):
        self.cls.name = 'test'
        self.cls.entry_names = ['f{}'.format(i) for i in range(5)]
        self.cls.entry_inode_indices = list(range(5))
        output = bytes(self.cls)
        expected = b'test\x00' \
                   b'f0\x00\x00\x00f1\x00\x00\x00f2\x00\x00\x00f3\x00\x00\x00f4\x00\x00\x00' \
                   b'\x00\x00' \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
                   b'\x01\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x02\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x03\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x04\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual(output, expected)

    def test_write(self):
        self.cls = ds.DirectoryBlock(index=0)
        self.cls._device = device_io.Disk(PATH)
        self.cls.name = 'test'
        self.cls.entry_names = ['f{}'.format(i) for i in range(5)]
        self.cls.entry_inode_indices = list(range(5))
        self.cls.__write__()
        expected = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                   b'test\x00' \
                   b'f0\x00\x00\x00f1\x00\x00\x00f2\x00\x00\x00f3\x00\x00\x00f4\x00\x00\x00' \
                   b'\x00\x00' \
                   b'\x00\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x01\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x02\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x03\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x04\x00\x00\x00\x00\x00\x00\x00'
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

        def test_read(self):
            self.cls = ds.DirectoryBlock(index=0)
            input_data = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                         b'test\x00' \
                         b'f0\x00\x00\x00f1\x00\x00\x00f2\x00\x00\x00f3\x00\x00\x00f4\x00\x00\x00' + \
                         b'\x00\x00' \
                         b'\x00\x00\x00\x00\x00\x00\x00\x00' \
                         b'\x01\x00\x00\x00\x00\x00\x00\x00' \
                         b'\x02\x00\x00\x00\x00\x00\x00\x00' \
                         b'\x03\x00\x00\x00\x00\x00\x00\x00' \
                         b'\x04\x00\x00\x00\x00\x00\x00\x00'

            with open(PATH, 'wb') as f:
                f.write(input_data)
            self.cls = ds.DirectoryBlock(device=device_io.Disk(PATH), index=0)
            self.assertEqual(self.cls.name, 'test')
            self.assertEqual(self.cls.entry_names, ['f{}'.format(i) for i in range(5)])
            self.assertEqual(self.cls.entry_inode_indices, list(range(5)))


class TestDataBlock(unittest.TestCase):
    def setUp(self):
        ds.BLOCK_SIZE = 20
        device_io.BLOCK_SIZE = 20
        ds.NUM_DATA_BLOCKS = 10
        self.cls = ds.DataBlock()
        open(PATH, 'a').close()

    def tearDown(self):
        del self.cls
        os.remove(PATH)

    def test_bytes(self):
        self.cls.data = 'this is test data'
        expected = b'this is test data\x00\x00\x00'
        output = bytes(self.cls)
        self.assertEqual(output, expected)

    def test_write(self):
        self.cls = ds.DataBlock(index=0)
        expected = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                   b'this is test data\x00\x00\x00'
        self.cls._device = device_io.Disk(PATH)
        self.cls.data = 'this is test data'
        self.cls.__write__()
        with open(PATH, 'rb') as f:
            output = f.read()
        self.assertEqual(output, expected)

    def test_read(self):
        self.cls = ds.DataBlock(index=0)
        input_data = bytes(self.cls.address * ds.BLOCK_SIZE) + \
                     b'this is test data\x00\x00\x00'
        with open(PATH, 'wb') as f:
            f.write(input_data)
        self.cls = ds.DataBlock(device=device_io.Disk(PATH), index=0)
        expected = 'this is test data'
        output = self.cls.data
        self.assertEqual(output, expected)



if __name__ == '__main__':
    unittest.main()
