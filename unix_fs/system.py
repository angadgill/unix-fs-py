""" File/Directory level abstractions go here """
from unix_fs.data_structures import DataBlock, Inode


class File(Inode):
    def __init__(self, device, index=None):
        super().__init__(i_type=1, device=device, index=index)

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
        super().__init__(i_type=2, device=device, index=index)

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
