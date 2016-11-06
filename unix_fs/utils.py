""" All utility functions go here """
from unix_fs import device_io
from unix_fs import data_structures as ds


def makefs(root_path, verbose=False):
    """
        Layout:
        Superblock
        All Inodes
        Inode Freelist
        Block Freelist
        Root Directory
    """
    if verbose:
        print("Creating file system at {}".format(root_path))
    bootstrap_data = bytes(ds.SuperBlock())
    bootstrap_data += bytes(ds.BLOCK_SIZE * ds.NUM_INODES)
    bootstrap_data += bytes(ds.InodeFreeList())
    bootstrap_data += bytes(ds.DataBlockFreeList())
    # TODO: Update write a real root directory
    bootstrap_data += bytes(ds.DirectoryBlock())
    bootstrap_data += bytes(ds.BLOCK_SIZE * ds.NUM_DATA_BLOCKS)
    disk = device_io.Disk(root_path)
    disk.open()
    disk.seek(0)
    disk.write(bootstrap_data)
    # TODO: remove this hack when real root directory is written
    ds.DataBlockFreeList(device=disk).allocate()
    disk.close()
