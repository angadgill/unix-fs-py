""" All utility functions go here """
from unix_fs import device_io
from unix_fs import data_structures as ds


def makefs(root_path):
    """
        Layout:
        Superblock
        All Inodes
        Inode Freelist
        Block Freelist
        Root Directory
    """
    print("Creating file system at {}".format(root_path))
    bootstrap_data = bytes(ds.SuperBlock())
    bootstrap_data += bytes(ds.BLOCK_SIZE * ds.NUM_INODES)
    bootstrap_data += bytes(ds.InodeFreeListBootstrap())
    bootstrap_data += bytes(ds.BlockFreeListBootstrap())
    bootstrap_data += bytes(ds.DirectoryBlock('/'))
    disk = device_io.Disk(root_path)
    disk.open()
    disk.seek(0)
    disk.write(bootstrap_data)
    disk.close()
