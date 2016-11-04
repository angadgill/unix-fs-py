"""
All data structures for the file system

Layout:
Superblock
All Inodes
Inode Freelist
Block Freelist
Root Directory
"""
import math

BLOCK_SIZE = 50
NUM_BLOCKS = 100
ADDRESS_LENGTH = 2  # bytes

NUM_INODES = 10
INODE_NUM_DIRECT_BLOCKS = 5
INODE_NUM_1_INDIRECT_BLOCKS = 1 # number of single indirect blocks

NUM_FILES_PER_DIR = 5
MAX_FILENAME_LENGTH = 5  # bytes


class Block(object):
    address = None

    """ Base Block class for the file system """
    def __init__(self, device):
        self._device = device

    def __bytes__(self):
        """
        Magic function which is called when bytes() is called on the object.
        Block bytes need to be padded to the BLOCK_SIZE of the file system.
        """
        pass

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

    def __write__(self):
        self._device.seek(self.address)
        self._device.write(self.__bytes__())



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
    index0_address = BLOCK_SIZE

    def __init__(self, itype, device, index=None):
        self._device = device

        # default initialization
        self.index = None
        self.itype = itype
        self.address_direct = [0] * INODE_NUM_DIRECT_BLOCKS
        self.address_1_indirect = [0] * INODE_NUM_1_INDIRECT_BLOCKS

        # If no index is provided, allocate new inode
        if index is None:
            self.allocate()
        else: # else, read inode from device
            self.index = index
            self._device.seek(self.address)
            self._device.read()

    def __bytes__(self):
        # return self.pad_bytes_to_block(self.c_long_list_to_bytes(self.address_direct))
        data = [self.itype] + self.address_direct + self.address_1_indirect
        return self.int_list_to_bytes(data)

    def __read__(self, bytes):
        int_list = self.bytes_to_int_list(bytes)
        self.address_direct = int_list[:INODE_NUM_DIRECT_BLOCKS]
        self.address_1_indirect = int_list[INODE_NUM_DIRECT_BLOCKS:INODE_NUM_1_INDIRECT_BLOCKS]

    @property
    def address(self):
        """ Return block address """
        return self.index0_address + self.index*BLOCK_SIZE

    def allocate(self):
        ifree = InodeFreeList(self._device)
        self.index = ifree.allocate()

    def deallocate(self):
        ifree = InodeFreeList(self._device)
        ifree.deallocate(self.index)



class File(Inode):
    def __init__(self, device, index=None):
        super().__init__(itype=1, device=device, index=index)



class Directory(Inode):
    def __init__(self, device, index=None):
        super().__init__(itype=2, device=device, index=index)





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


class InodeFreeListBootstrap(Block):
    def __init__(self):
        self.list = [True] * NUM_INODES  # list of booleans. True means inode is free.

    def __bytes__(self):
        return self.int_list_to_bytes(self.list)

    def __read__(self, bytes):
        self.list = self.bytes_to_int_list(bytes)


class InodeFreeList(InodeFreeListBootstrap):
    address = BLOCK_SIZE * (1 + NUM_INODES)

    def __init__(self, device):
        super().__init__()
        self._device = device
        device.seek(self.address)
        self.__read__(self._device.read(len(bytes(InodeFreeListBootstrap()))))

    def allocate(self):
        """ Finds the first free block and returns block index """
        for i in range(len(self.list)):
            if self.list[i] == 1:
                self.list[i] = 0
                self.__write__()
                return i

    def deallocate(self, index):
        self.list[index] = 1
        self.__write__()


class BlockFreeListBootstrap(Block):
    def __init__(self):
        self.list = [True] * NUM_BLOCKS

    def __bytes__(self):
        return self.int_list_to_bytes(self.list)


    def __read__(self, bytes):
        self.list = self.bytes_to_int_list(bytes)


class BlockFreelist(BlockFreeListBootstrap):
    address = BLOCK_SIZE * (1 + NUM_INODES) + len(bytes(InodeFreeListBootstrap()))

    def __init__(self, device):
        super().__init__()
        self._device = device
        device.seek(self.address)
        self.__read__(self._device.read(len(bytes(BlockFreeListBootstrap()))))

    def allocate(self):
        """ Finds the first free block and returns block index """
        for i in range(len(self.list)):
            if self.list[i] == 1:
                self.list[i] = 0
                self.__write__()
                return i

    def deallocate(self, index):
        self.list[index] = 1
        self.__write__()


class DataBlock(Block):
    index0_address = BLOCK_SIZE + (BLOCK_SIZE * NUM_INODES) + \
                     len(bytes(InodeFreeListBootstrap())) + \
                     len(bytes(BlockFreeListBootstrap())) + \
                     len(bytes(DirectoryBlock('/')))

    def __init__(self, device, index=None):
        self._device = device

        # default initialization
        self.index = None

        # If no index is provided, allocate new inode
        if index is None:
            self.allocate()
        else:  # else, read inode from device
            self.index = index
            self._device.seek(self.address)
            self._device.read()

    def __read__(self, bytes):
        self.data = self.bytes_to_int_list(bytes)

    @property
    def address(self):
        """ Return block address """
        return self.index0_address + self.index*BLOCK_SIZE

    def allocate(self):
        bfree = BlockFreelist(self._device)
        self.index = bfree.allocate()

    def deallocate(self):
        bfree = BlockFreelist(self._device)
        bfree.deallocate(self.index)
