""" All data structures for the file system """

BLOCK_SIZE = 50
ADDRESS_LENGTH = 2  # bytes

NUM_INODES = 10
INODE_NUM_DIRECT_BLOCKS = 5
INODE_NUM_1_INDIRECT_BLOCKS = 1 # number of single indirect blocks

NUM_FILES_PER_DIR = 5
MAX_FILENAME_LENGTH = 5  # bytes


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
        if len(byte_data) < BLOCK_SIZE:
            byte_data = byte_data + bytes(BLOCK_SIZE - len(byte_data))
        return byte_data

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

    def str_to_bytes(self, string, pad_to = MAX_FILENAME_LENGTH):
        """ Converts str to bytes and pads to max filename length using spaces """
        b = str.encode(string)
        return b + b''.join([str.encode(' ')]*(MAX_FILENAME_LENGTH-len(b)))

    def str_list_to_bytes(self, str_list):
        """ Converts list of ints to bytes of ADDRESS_LENGTH length using Little Endian byte order"""
        b = b''.join([self.str_to_bytes(x) for x in str_list])
        # b = struct.pack('i'*len(int_list), *int_list)
        # if pad:
        #     b = self.pad_bytes_to_block(b)
        return b

    def bytes_to_str(self, bytes):
        return bytes.decode().rstrip()

    def bytes_to_str_list(self, byte_data):
        """ Converts byte data containing MAX_FILENAME_LENGTH size strings. Data is also padded to BLOCK_SIZE"""
        num_str = int(len(byte_data) / MAX_FILENAME_LENGTH)
        byte_list = [byte_data[i * MAX_FILENAME_LENGTH:(i + 1) * MAX_FILENAME_LENGTH] for i in range(num_str)]
        str_list = [b.decode().rstrip() for b in byte_list]
        return str_list


class SuperBlock(Block):
    def __init__(self, bytes=None):
        if bytes is None:
            self.block_size = BLOCK_SIZE
            self.num_inodes = NUM_INODES
        else:
            self.__read__((bytes))

    def __bytes__(self):
        data = [self.block_size, self.num_inodes]
        return self.int_list_to_bytes(data)

    def __read__(self, bytes):
        int_list = self.bytes_to_int_list(bytes)
        self.block_size, self.num_inodes = int_list[:2]


class Inode(Block):
    """ Base class for files and directories  """
    # int.from_bytes(bytes(c_long(10)), 'little')

    def __init__(self):
        self.type = None
        self.address_direct = [0] * INODE_NUM_DIRECT_BLOCKS
        self.address_1_indirect = [0] * INODE_NUM_1_INDIRECT_BLOCKS

    def __bytes__(self):
        # return self.pad_bytes_to_block(self.c_long_list_to_bytes(self.address_direct))
        data = [self.type] + self.address_direct + self.address_1_indirect
        return self.int_list_to_bytes(data)

    def __read__(self, bytes):
        int_list = self.bytes_to_int_list(bytes)
        self.address_direct = int_list[:INODE_NUM_DIRECT_BLOCKS]
        self.address_1_indirect = int_list[INODE_NUM_DIRECT_BLOCKS:INODE_NUM_1_INDIRECT_BLOCKS]
        

class File(Inode):
    def __init__(self):
        super().__init__()
        self.type = 0


class Directory(Inode):
    def __init__(self):
        super().__init__()
        self.type = 1


class DataBlock(Block):
    def __init__(self):
        self.data = 0

    def __read__(self, bytes):
        self.data = self.bytes_to_int_list(bytes)

class InodeFreeList(Block):
    def __init__(self):
        self.free_inodes = [True] * NUM_INODES  # list of booleans. True means inode is free.

    def __bytes__(self):
        return self.int_list_to_bytes(self.free_inodes)

    def __read__(self, bytes):
        self.free_inodes = self.bytes_to_int_list(bytes)


class DirectoryBlock(Block):
    """ Data written to the block pointed to by the Directory Inode """
    def __init__(self, name):
        self.name = name
        self.filenames = [''] * NUM_FILES_PER_DIR
        self.inode_numbers = [0] * NUM_FILES_PER_DIR

    def __bytes__(self):
        return self.str_to_bytes(self.name) +\
               self.str_list_to_bytes(self.filenames) + \
               self.int_list_to_bytes(self.inode_numbers)

    def __read__(self, byte_data):
        self.name = self.bytes_to_str(byte_data[:MAX_FILENAME_LENGTH])
        start = MAX_FILENAME_LENGTH
        end = start + MAX_FILENAME_LENGTH*NUM_FILES_PER_DIR
        self.filenames = self.bytes_to_str_list(byte_data[start:end])
        start = end
        end = start + ADDRESS_LENGTH*NUM_FILES_PER_DIR
        self.inode_numbers = self.bytes_to_int_list(byte_data[start:end])
        print(self.name)
        print(self.filenames)
        print(self.inode_numbers)