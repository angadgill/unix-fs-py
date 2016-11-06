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
NUM_DATA_BLOCKS = 100
ADDRESS_LENGTH = 4  # bytes # Not using this! All addresses are 8 bytes (long int)

NUM_INODES = 10
INODE_NUM_DIRECT_BLOCKS = 5
INODE_NUM_1_INDIRECT_BLOCKS = 1 # number of single indirect blocks

NUM_FILES_PER_DIR_BLOCK = 5
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
        self._format = ''  # type: str # Packing format for list self._item

    @property
    def address(self) -> int:
        """ Block address of the object on disk """
        return 0

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

    def __decode__(self, byte_data) -> List:
        byte_data = byte_data[:self._size]  # truncate to remove padding bytes
        return list(struct.unpack(self._format, byte_data))

    def __read__(self):
        self._device.seek(self.address)
        byte_data = self._device.read(self._size)
        self._items = self.__decode__(byte_data)


class SuperBlock(Block):
    def __init__(self, device=None):
        super().__init__(device=device)
        self._format = 'll'
        self.block_size = BLOCK_SIZE
        self.num_inodes = NUM_INODES
        if device is not None:
            self.__read__()

    @property
    def _items(self):
        return [self.block_size, self.num_inodes]

    @_items.setter
    def _items(self, value):
        [self.block_size, self.num_inodes] = value


class FreeList(Block):
    def __init__(self, n=0, device=None):
        super().__init__(device=device)
        self.list = [True] * n
        self._format = '{}?'.format(n)  # format as n booleans

        if device is not None:
            self.__read__()

    @property
    def _items(self):
        return self.list

    @_items.setter
    def _items(self, value):
        self.list = value

    def allocate(self, write_through: bool = True) -> int:
        """ Finds the first free item and returns index """
        for i, item in enumerate(self.list):
            if item:  # is true
                self.list[i] = False
                if write_through:
                    self.__write__()
                return i
        else:
            raise Exception('No free items in {}.'.format(self.__class__))

    def deallocate(self, index: int, write_through: bool = True) -> None:
        self.list[index] = True
        if write_through:
            self.__write__()


class InodeFreeList(FreeList):
    def __init__(self, device=None):
        super().__init__(n=NUM_INODES, device=device)

    @property
    def address(self) -> int:
        byte_address = len(bytes(SuperBlock())) + \
                       len(bytes(Inode()) * NUM_INODES)
        block_address = int(byte_address/BLOCK_SIZE)
        return block_address


class DataBlockFreeList(FreeList):
    def __init__(self, device=None):
        super().__init__(n=NUM_DATA_BLOCKS, device=device)

    @property
    def address(self) -> int:
        byte_address = len(bytes(SuperBlock())) + \
                       len(bytes(Inode()) * NUM_INODES) + \
                       len(bytes(InodeFreeList()))
        block_address = int(byte_address/BLOCK_SIZE)
        return block_address


class AllocableBLock(Block):
    def __init__(self, device=None, index=None):
        super().__init__(device=device)
        self.index = index

    @property
    def freelist(self) -> FreeList:
        return FreeList(self._device)

    def allocate(self) -> None:
        if self.index is None:
            self.index = self.freelist.allocate()
        else:
            raise Exception("{} already allocated at index {}".format(self.__class__, self.index))

    def deallocate(self) -> None:
        if self.index is not None:
            self.freelist.deallocate(self.index)
            self.index = None
        else:
            raise Exception("{} is not allocated".format(self.__class__))


class Inode(AllocableBLock):
    """ Base class for files and directories  """

    def __init__(self, i_type=0, device=None, index=None):
        super().__init__(device=device, index=index)
        self._index0_block_address = 1

        self.i_type = i_type
        self.address_direct = [0] * INODE_NUM_DIRECT_BLOCKS

        self._format = 'l{}l'.format(len(self.address_direct))

        if device is not None and index is not None:
            self.__read__()

        if self._device is not None and self.index is None:
            self.allocate()

    @property
    def freelist(self) -> FreeList:
        return InodeFreeList(device=self._device)

    @property
    def _items(self):
        return [self.i_type, *self.address_direct]

    @_items.setter
    def _items(self, value):
        self.i_type = value[0]
        self.address_direct = value[1:1 + len(self.address_direct)]

    @property
    def address(self) -> int:
        index_0_byte_address = len(bytes(SuperBlock()))
        index_0_block_address = int(index_0_byte_address/BLOCK_SIZE)
        return index_0_block_address + self.index

    def _last_assigned_address(self) -> int:
        index_last_assigned = 0
        for address in self.address_direct:
            if address != 0:
                index_last_assigned = address
        return index_last_assigned

    def _add_to_address_list(self, block, write_through=True) -> None:
        # Find the first spot to add the block index to
        for i in range(len(self.address_direct)):
            if self.address_direct[i] == 0:
                self.address_direct[i] = block.index
                if write_through:
                    self.__write__()
                break
        else:
            raise Exception('File full')


class DataBlock(AllocableBLock):
    """ All data stored as utf-8 text characters """
    def __init__(self, device=None, index=None):
        super().__init__(device=device, index=index)
        self.data = None
        self._format = '{}s'.format(BLOCK_SIZE)
        if device is not None and index is not None:
            self.__read__()
        if device is not None and index is None:
            self.allocate()

    @property
    def freelist(self) -> FreeList:  # List to check when allocating / deallocating
        return DataBlockFreeList(device=self._device)

    @property
    def _items(self):
        return [self.str_to_bytes(self.data, pad_to=0)]

    @_items.setter
    def _items(self, value):
        self.data = self.bytes_to_str(value[0], strip='\x00')

    @property
    def address(self) -> int:
        index_0_byte_address = len(bytes(SuperBlock())) + \
                       len(bytes(Inode()) * NUM_INODES) + \
                       len(bytes(InodeFreeList())) + \
                       len(bytes(DataBlockFreeList()))  # + BLOCK_SIZE  # for the root directory
        index_0_block_address = int(index_0_byte_address/BLOCK_SIZE)
        return index_0_block_address + self.index

    def is_full(self) -> bool:
        self.__read__()
        return len(self.data) == BLOCK_SIZE

    def append(self, new_data: str, write_through=True) -> str:
        """ Append data to self.data up to BLOCK_SIZE. Return remaining """
        if self.data is None:
            end = BLOCK_SIZE
            self.data = new_data[:end]
        else:
            end = BLOCK_SIZE - len(self.data)
            self.data += new_data[:end]
        if write_through:
            self.__write__()
        return new_data[end:]


class DirectoryBlock(DataBlock):
    """ Data written to the block pointed to by the Directory Inode """
    def __init__(self, device=None, index=None, name=''):
        super().__init__(device=device, index=index)
        self.name = name
        self.entry_names = [''] * NUM_FILES_PER_DIR_BLOCK
        self.entry_inode_indices = [0] * NUM_FILES_PER_DIR_BLOCK

        self._format = '{}s'.format(MAX_FILENAME_LENGTH) + \
                       ''.join(['{}s'.format(MAX_FILENAME_LENGTH)] * NUM_FILES_PER_DIR_BLOCK) + \
                       '{}l'.format(NUM_FILES_PER_DIR_BLOCK)

        if device is not None and index is not None:
            self.__read__()

    @property
    def _items(self):
        return [self.str_to_bytes(self.name, pad_to=0)] + \
               [self.str_to_bytes(f, pad_to=0) for f in self.entry_names] + \
               self.entry_inode_indices

    @_items.setter
    def _items(self, value):
        self.name = self.bytes_to_str(value[0], strip='\x00')
        self.entry_names = [self.bytes_to_str(v, strip='\x00') for v in value[1:1+NUM_FILES_PER_DIR_BLOCK]]
        self.entry_inode_indices = value[1+NUM_FILES_PER_DIR_BLOCK:]

    def is_full(self) -> bool:
        self.__read__()
        full = True
        for e in self.entry_names:
            if e == '':
                full = False
        return full

    def add_entry(self, entry_name, entry_inode_index, write_through=True):
        """ Add entry to Dir Block, in the first available location """
        if len(entry_name) > MAX_FILENAME_LENGTH:
            raise Exception('Given entry_name "" is too long (> {})'.format(entry_name, MAX_FILENAME_LENGTH))

        for i in range(NUM_FILES_PER_DIR_BLOCK):
            if self.entry_names[i] == '' and self.entry_inode_indices[i] == 0:
                self.entry_names[i] = entry_name
                self.entry_inode_indices[i] = entry_inode_index
                if write_through:
                    self.__write__()
                break
        else:
            raise Exception('{} {} ("{}") full'.format(self.__class__, self.index, self.name))

    def remove_entry(self, entry_name, entry_inode_index, write_through=True):
        """ Remove entry based on name and index """
        for i in range(NUM_FILES_PER_DIR_BLOCK):
            if self.entry_names[i] == entry_name and self.entry_inode_indices[i] == entry_inode_index:
                self.entry_names[i] = ''
                self.entry_inode_indices[i] = 0
                if write_through:
                    self.__write__()
                break
        else:
            raise Exception('{} {} ("{}") does not contain entry "{}"'.
                            format(self.__class__, self.index,
                                   self.name, entry_name))
