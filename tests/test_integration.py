""" All integration tests for the file system """

import unittest
import subprocess
import os

MOUNTPOINT = '/Users/angad/tempfs_mountpoint'
ROOT = '/Users/angad/tempfs_root'


class TestFileSystem(unittest.TestCase):
    """ Base test class for file systems with helper functions """
    @staticmethod
    def filename_to_path(filename):
        """ Convert filename to file path under MOUNTPOINT """
        return os.path.join(MOUNTPOINT, filename)

    @staticmethod
    def create_file(filepath):
        """ Helper function to create an empty file given absolute file path """
        open(filepath, 'a').close()

    @staticmethod
    def delete_file(filepath):
        """ Helper function to delete a file given absolute file path """
        os.remove(filepath)  # cleanup so that all test are independent

    @staticmethod
    def file_exists(filepath):
        """ Helper function to check if file exists given absolute file path """
        return os.path.isfile(filepath)


class TestLoopback(TestFileSystem):
    @classmethod
    def setUpClass(cls):
        """ Runs before first test is run """
        command = 'python fusepy_example/loopback.py {} {} background'.format(ROOT, MOUNTPOINT)
        subprocess.call(command, shell=True)

    @classmethod
    def tearDownClass(cls):
        """ Runs after last test is run """
        command = 'umount Loopback'
        subprocess.call(command, shell=True)

    def test_file_create_delete(self):
        filepath = self.filename_to_path('file1')
        self.create_file(filepath)
        self.assertTrue(self.file_exists(filepath))
        self.delete_file(filepath)

    def test_file_write_read(self):
        test_text = "this is the test text"
        filepath = self.filename_to_path('file2')
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
        filepaths = [self.filename_to_path('file_num_{}').format(i) for i in range(num)]
        # create
        for filepath in filepaths:
            self.create_file(filepath)
        # check that they exist
        for filepath in filepaths:
            self.assertTrue(self.file_exists(filepath))
        # delete to cleanup
        for filepath in filepaths:
            self.delete_file(filepath)


if __name__ == '__main__':
    unittest.main()