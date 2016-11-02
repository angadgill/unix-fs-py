""" All data structures for the file system """

from ctypes import c_long
import struct

BLOCK_SIZE = 64
ADDRESS_LENGTH = 4  # bytes

NUM_INODES = 10
INODE_NUM_DIRECT_BLOCKS = 5
INODE_NUM_1_INDIRECT_BLOCKS = 1 # number of single indirect blocks

class Block(object):
    """ Base Block class for the file system """
    def __init__(self, data):
        self.data = data

    def __bytes__(self):
        """
        Magic function which is called when bytes() is called on the object.
        Block bytes need to be padded to the BLOCK_SIZE of the file system.
        """
        return self.pad_bytes_to_block(bytes(self.data))

    def pad_bytes_to_block(self, byte_data):
        """ Pads byte data to BLOCK_SIZE """
        return byte_data + bytes(BLOCK_SIZE - len(byte_data))

    def int_list_to_bytes(self, int_list, pad=True):
        """ Converts list of ints to bytes of ADDRESS_LENGTH length using Little Endian byte order"""
        b = b''.join([x.to_bytes(ADDRESS_LENGTH, 'little') for x in int_list])
        # b = struct.pack('i'*len(int_list), *int_list)
        if pad:
            b = self.pad_bytes_to_block(b)
        return b

    def bytes_to_int_list(self, byte_data):
        """ Converts byte data containing ADDRESS_LENGTH size ints. Data is also padded to BLOCK_SIZE"""
        num_ints = int(len(byte_data)/ADDRESS_LENGTH)
        byte_list = [byte_data[i*ADDRESS_LENGTH:(i+1)*ADDRESS_LENGTH] for i in range(num_ints)]
        int_list = [int.from_bytes(b, 'little') for b in byte_list]
        # int_list = struct.unpack('i'*num_ints, byte_data)
        return int_list

class SuperBlock(Block):
    def __init__(self):
        self.block_size = BLOCK_SIZE
        self.num_inodes = NUM_INODES

class Inode(Block):
    """ Base class for files and directories  """
    # int.from_bytes(bytes(c_long(10)), 'little')

    def __init__(self):
        self.address_direct = [0] * INODE_NUM_DIRECT_BLOCKS
        self.address_1_indirect = [1] * INODE_NUM_1_INDIRECT_BLOCKS

    def __bytes__(self):
        # return self.pad_bytes_to_block(self.c_long_list_to_bytes(self.address_direct))
        data = self.address_direct + self.address_1_indirect
        return self.int_list_to_bytes(data)

    def c_long_list_to_bytes(self, c_long_list):
        return b''.join([bytes(x) for x in c_long_list])