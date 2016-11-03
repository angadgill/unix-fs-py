""" All utility functions go here """
from unix_fs import data_structures


def makefs(root_path):
    print("Creating file system at {}".format(root_path))
    with open(root_path, 'wb') as f:
        f.write(bytes(data_structures.SuperBlock()))
        for _ in range(data_structures.NUM_INODES):  # I-list
            f.write(bytes(data_structures.Inode()))
        f.write(bytes(data_structures.InodeFreeList()))
        f.write(bytes(data_structures.Directory('/')))
