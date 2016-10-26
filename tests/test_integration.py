""" All integration tests for the file system """

import unittest
import subprocess
import os

MOUNTPOINT = 'tempfs_mountpoint'
ROOT = 'tempfs_root'

class TestFileSystem(unittest.TestCase):
    """ Base test class for file systems with helper functions """
    @staticmethod
    def name_to_path(name):
        """ Convert filename to file path under MOUNTPOINT """
        return os.path.join(MOUNTPOINT, name)

    @staticmethod
    def create_file(filepath):
        """ Helper function to create an empty file given absolute path """
        open(filepath, 'a').close()

    @staticmethod
    def delete_file(filepath):
        """ Helper function to delete a file given absolute path """
        os.remove(filepath)

    @staticmethod
    def file_exists(filepath):
        """ Helper function to check if file exists given absolute path """
        return os.path.isfile(filepath)

    @staticmethod
    def create_dir(dirpath):
        """ Helper function to create an empty directory given absolute path """
        os.makedirs(dirpath)

    @staticmethod
    def delete_dir(dirpath):
        """ Helper function to delete a directory given absolute path """
        os.removedirs(dirpath)

    @staticmethod
    def dir_exists(dirpath):
        """ Helper function to check if directory exists given absolute path """
        return os.path.isdir(dirpath)

    def assertCommandSuccessful(self, command):
        """" Asserts that a command runs without error. Suppresses print from the command. """
        success_response = 0
        with open(os.devnull, 'w') as FNULL: # null file to redirect stdout
            self.assertEqual(subprocess.call(command, shell=True, stdout=FNULL), success_response)

class TestLoopback(TestFileSystem):
    @classmethod
    def setUpClass(self):
        """ Runs before first test is run """
        # create directories
        for dir in [MOUNTPOINT, ROOT]:
            if not os.path.exists(dir):
                os.makedirs(dir)
        # mount file system
        command = 'python fusepy_example/loopback.py {} {} background'.format(ROOT, MOUNTPOINT)
        subprocess.call(command, shell=True)

    @classmethod
    def tearDownClass(self):
        """ Runs after last test is run """
        # unmount file system
        command = 'umount Loopback'
        subprocess.call(command, shell=True)
        # delete directories
        for dir in [MOUNTPOINT, ROOT]:
            os.removedirs(dir)

    def test_ls(self):
        self.assertCommandSuccessful('ls')

    def test_file_create_delete(self):
        filepath = self.name_to_path('file1')
        self.create_file(filepath)
        self.assertTrue(self.file_exists(filepath))
        self.delete_file(filepath)

    def test_file_write_read(self):
        test_text = "this is the test text"
        filepath = self.name_to_path('file2')
        # write to file
        with open(filepath, 'w') as f:
            f.write(test_text)
        # read from file
        with open(filepath, 'r') as f:
            text = f.read(len(test_text))
        self.delete_file(filepath)
        self.assertEqual(text, test_text)

    def test_num_file_create_delete(self):
        num = 10
        filepaths = [self.name_to_path('file_num_{}').format(i) for i in range(num)]
        # create
        for filepath in filepaths:
            self.create_file(filepath)
        # check that they exist
        for filepath in filepaths:
            self.assertTrue(self.file_exists(filepath))
        # delete to cleanup
        for filepath in filepaths:
            self.delete_file(filepath)

    def test_dir_create_delete(self):
        dirpath = self.name_to_path('dir1')
        self.create_dir(dirpath)
        self.assertTrue(self.dir_exists(dirpath))
        self.delete_dir(dirpath)

if __name__ == '__main__':
    unittest.main()