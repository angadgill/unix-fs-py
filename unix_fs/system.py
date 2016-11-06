""" File/Directory level abstractions go here """
from typing import List, Tuple
from unix_fs.data_structures import Inode, DataBlock, DirectoryBlock

class File(Inode):
    def __init__(self, device=None, index=None):
        super().__init__(i_type=1, device=device, index=index)

    def write(self, data):
        """ Write to the File. Allocate DataBlocks and write text to them """
        # TODO: This is basically "append" right now. Update when "seek" is added
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

    def add(self, entry_name, entry_inode):
        """ Add to the Directory. Allocate DirectoryBlocks and write name and inodes to them """

        # Check to see if name already exits
        existing_names, _ = self.read()
        if entry_name in existing_names:
            raise Exception('{}: entry already exists'.format(self.__class__))

        # Check to see if any DirectoryBlocks is already assigned
        if sum(self.address_direct) != 0:
            # If assigned, append data to last block
            last_assigned = self._last_assigned_address()
            block = DirectoryBlock(device=self._device, index=last_assigned)
            if block.is_full():
                # Assign a new block
                block = DirectoryBlock(device=self._device)
                self._add_to_address_list(block)
        else:
            # assign a new block and add to Inode
            block = DirectoryBlock(device=self._device)
            self._add_to_address_list(block)
        # Write to block
        block.add_entry(entry_name=entry_name, entry_inode_index=entry_inode)

    def remove(self, entry_name, entry_inode):
        """ Remove from Directory """
        if sum(self.address_direct) == 0:
            raise Exception('{} {} contains no files'.format(self.__class__, self.index))

        for address in self.address_direct:
            block = DirectoryBlock(device=self._device, index=address)
            try:
                block.remove_entry(entry_name=entry_name, entry_inode_index=entry_inode)
            # TODO: Change this to not use try except
            except Exception:
                continue

    def read(self) -> Tuple[List[str], List[int]]:
        """ Reads entry names and inode numners from directory """
        entry_names = []  # type: List
        entry_inodes = []  # type: List
        for address in self.address_direct:
            if address != 0:
                block = DirectoryBlock(device=self._device, index=address)
                for e in block.entry_names:
                    if e != '':
                        entry_names += [e]
                for e in block.entry_inode_indices:
                    if e != 0:
                        entry_inodes += [e]
            else:
                break
        return entry_names, entry_inodes
