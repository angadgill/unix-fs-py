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
from typing import List
import struct

BLOCK_SIZE = 50
NUM_BLOCKS = 100
ADDRESS_LENGTH = 4  # bytes # Not using this! All addresses are 8 bytes (long int)

NUM_INODES = 10
INODE_NUM_DIRECT_BLOCKS = 5
INODE_NUM_1_INDIRECT_BLOCKS = 1 # number of single indirect blocks

NUM_FILES_PER_DIR = 5
MAX_FILENAME_LENGTH = 5  # bytes


class Base(object):
    """ Base class with helper functions """
    @staticmethod
    def pad_bytes_to_block(byte_data: bytes) -> bytes:
        """ Pads byte data to BLOCK_SIZE """
        if len(byte_data) < BLOCK_SIZE:
            byte_data = byte_data + bytes(BLOCK_SIZE - len(byte_data))
        return byte_data

    """ int <--> bytes conversions """
    @staticmethod
    def int_to_bytes(int_data: int) -> bytes:
        """ Converts ints to bytes and pads it to ADDRESS_LENGTH using little endian. """
        return int_data.to_bytes(ADDRESS_LENGTH, 'little')

    def int_list_to_bytes(self, int_list: List[int], pad: bool = True) -> bytes:
        """ Converts list of ints to bytes of ADDRESS_LENGTH length using Little Endian byte order"""
        b = b''.join([self.int_to_bytes(x) for x in int_list])
        if pad:
            b = self.pad_bytes_to_block(b)
        return b

    @staticmethod
    def bytes_to_int(byte_data: bytes) -> int:
        return int.from_bytes(byte_data, 'little')

    @staticmethod
    def bytes_to_byte_list(bytes_data: bytes, chunk: int) -> List[bytes]:
        num_ints = int(len(bytes_data)/chunk)
        byte_list = [bytes_data[i*chunk:(i+1)*chunk] for i in range(num_ints)]
        return byte_list  # Still padded to ADDRESS_LENGTH

    def bytes_to_int_list(self, byte_data: bytes) -> List[int]:
        """ Converts byte data containing ADDRESS_LENGTH size ints """
        byte_list = self.bytes_to_byte_list(byte_data, chunk=ADDRESS_LENGTH)
        int_list = [self.bytes_to_int(b) for b in byte_list]
        return int_list

    """ str <---> bytes conversions """
    @staticmethod
    def str_to_bytes(string: str, pad_to: int = MAX_FILENAME_LENGTH) -> bytes:
        """
        Converts str to bytes and pads using spaces (\x20).
        Padding applied only if it is longer than the input.
        """
        b = str.encode(string)
        return b + b''.join([str.encode(' ')]*(pad_to-len(b)))

    def str_list_to_bytes(self, str_list: List[str], pad_to: int = MAX_FILENAME_LENGTH) -> bytes:
        b = b''.join([self.str_to_bytes(x, pad_to=pad_to) for x in str_list])
        return b

    @staticmethod
    def bytes_to_str(bytes_data: bytes, strip: str = '\x20') -> str:
        """Converts bytes to str and strips trailing bytes"""
        return bytes_data.decode().rstrip(strip)

    def bytes_to_str_list(self, byte_data: bytes, strip: str='\x20') -> List[str]:
        """ Converts byte data containing MAX_FILENAME_LENGTH size strings. Data is also padded to BLOCK_SIZE"""
        # num_str = int(len(byte_data) / MAX_FILENAME_LENGTH)
        # byte_list = [byte_data[i * MAX_FILENAME_LENGTH:(i + 1) * MAX_FILENAME_LENGTH] for i in range(num_str)]
        byte_list = self.bytes_to_byte_list(byte_data, chunk=MAX_FILENAME_LENGTH)
        str_list = [self.bytes_to_str(b, strip) for b in byte_list]
        return str_list


class Block(Base):
    """ All data types stored on disk are stored as Blocks. Data is read and written to device in BLOCK_SIZE chunks """

    def __init__(self, device=None):
        self._device = device
        self.address = 0  # type: int
        self._format = ''  # type: str # Packing format for list self._item

    @property
    def _items(self) -> List:
        """ Returns a list of all properties that are written to disk """
        return []

    @_items.setter
    def _items(self, value) -> None:
        """ Reassign values read from disk to object properties """
        [_] = value  # List here should be the same as the one in @property def _items

    @property
    def _size(self) -> int:
        """ Byte size of object on disk """
        return struct.calcsize(self._format)

    def __bytes__(self) -> bytes:
        """
        Magic function which is called when bytes() is called on the object.
        Must return bytes padded to the BLOCK_SIZE of the file system.
        """
        bytes_data = struct.pack(self._format, *self._items)
        return self.pad_bytes_to_block(bytes_data)

    def __write__(self) -> None:
        self._device.seek(self.address)
        self._device.write(self.__bytes__())

    def __decode__(self, byte_data):
        byte_data = byte_data[:self._size]  # truncate to remove padding bytes
        return struct.unpack(self._format, byte_data)

    def __read__(self):
        self._device.seek(self.address)
        byte_data = self._device.read(self._size)
        self._items = self.__decode__(byte_data)


class SuperBlock(Block):
    def __init__(self, device=None):
        super().__init__(device)
        self.block_size = BLOCK_SIZE
        self.num_inodes = NUM_INODES
        self._format = 'll'
        if device is not None:
            self.__read__()

    @property
    def _items(self):
        return [self.block_size, self.num_inodes]

    @_items.setter
    def _items(self, value):
        [self.block_size, self.num_inodes] = value


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
            self.__read__()

    def __bytes__(self):
        # return self.pad_bytes_to_block(self.c_long_list_to_bytes(self.address_direct))
        data = self.itype + self.address_direct + self.address_1_indirect
        return self.int_list_to_bytes(data)

    def __read__(self):
        self._device.seek(self.address)
        data = self._device.read(BLOCK_SIZE)
        int_list = self.bytes_to_int_list(data)
        self.itype = int_list[:1]
        start = 1
        end = start + INODE_NUM_DIRECT_BLOCKS
        self.address_direct = int_list[start:end]
        start = end
        end = start + INODE_NUM_1_INDIRECT_BLOCKS
        self.address_1_indirect = int_list[start:end]

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

    def write(self, data):
        block = DataBlock(self._device)
        self.add_block_to_list(block)
        block.__write__(data)

    def read(self):
        """ Reads and returns the first block, for now """
        block = DataBlock(self._device, self.address_direct[0])
        return block.__read__()

    def add_block_to_list(self, block):
        # Find the first spot to add the block index to
        for i in range(len(self.address_direct)):
            if self.address_direct[i] == 0:
                self.address_direct[i] = block.index
                break
        else:
             raise Exception('File full')
        self.__write__()


class Directory(Inode):
    def __init__(self, device, index=None):
        super().__init__(itype=2, device=device, index=index)

    def write(self, data):
        block = Directory(self._device)
        self.add_block_to_list(block)
        block.__write__(data)

    def read(self):
        """ Reads and returns the first block, for now """
        block = DataBlock(self._device, self.address_direct[0])
        return block.__read__()

    def add_block_to_list(self, block):
        # Find the first spot to add the block index to
        for i in range(len(self.address_direct)):
            if self.address_direct[i] == 0:
                self.address_direct[i] = block.index
                break
        else:
             raise Exception('File full')
        self.__write__()


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


class InodeFreeList(InodeFreeListBootstrap):
    address = BLOCK_SIZE * (1 + NUM_INODES)

    def __init__(self, device):
        super().__init__()
        self._device = device
        self.__read__()

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

    def __read__(self):
        self._device.seek(self.address)
        data = self._device.read(len(bytes(InodeFreeListBootstrap())))
        self.list = self.bytes_to_int_list(data)


class BlockFreeListBootstrap(Block):
    def __init__(self):
        self.list = [True] * NUM_BLOCKS

    def __bytes__(self):
        return self.int_list_to_bytes(self.list)


class BlockFreelist(BlockFreeListBootstrap):
    address = BLOCK_SIZE * (1 + NUM_INODES) + len(bytes(InodeFreeListBootstrap()))

    def __init__(self, device):
        super().__init__()
        self._device = device
        self.__read__()

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

    def __read__(self):
        self._device.seek(self.address)
        data = self._device.read(len(bytes(InodeFreeListBootstrap())))
        self.list = self.bytes_to_int_list(data)


class DataBlock(Block):
    index0_address = BLOCK_SIZE + (BLOCK_SIZE * NUM_INODES) + \
                     len(bytes(InodeFreeListBootstrap())) + \
                     len(bytes(BlockFreeListBootstrap())) + \
                     len(bytes(DirectoryBlock('/')))

    def __init__(self, device, index=None):
        self._device = device

        # default initialization
        self.index = None
        self.data = None

        # If no index is provided, allocate new inode
        if index is None:
            self.allocate()
        else:  # else, read inode from device
            self.index = index
            self.data = self.__read__()

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

    def __write__(self, data):
        self._device.seek(self.address)
        if type(data) == str:
            self._device.write(self.str_to_bytes(data, pad_to=BLOCK_SIZE))
        else:
            self._device.write(bytes(data))

    def __read__(self):
        self._device.seek(self.address)
        data = self._device.read(BLOCK_SIZE)
        return self.bytes_to_str(data)
