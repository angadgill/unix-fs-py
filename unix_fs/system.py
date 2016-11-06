""" File/Directory level abstractions go here """
from unix_fs.data_structures import DataBlock, Inode


class File(Inode):
    def __init__(self, device=None, index=None):
        super().__init__(i_type=1, device=device, index=index)

        if self._device is not None and self.index is None:
            self.allocate()

    def write(self, data):
        """ Write to the File. Allocate DataBlocks and write text to them """

        # Check to see if any DataBlock is already assigned
        if sum(self.address_direct) != 0:
            # If assigned, append data to last block
            last_assigned = self._last_assigned_address()
            block = DataBlock(device=self._device, index=last_assigned)
            excess_data = block.append(data)
        else:
            excess_data = data

        # Add all excess data into new blocks
        while len(excess_data) > 0:
            # assign a new block and add to Inode
            block = DataBlock(device=self._device)
            self._add_to_address_list(block)
            # Write to block
            excess_data = block.append(excess_data)
            block.__write__()

    def read(self):
        """ Reads and returns the first block, for now """
        data = ''
        for address in self.address_direct:
            if address != 0:
                block = DataBlock(device=self._device, index=address)
                data += block.data
            else:
                break
        return data


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
