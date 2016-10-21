# unix-fs-py
Python implementation of the Unix File System.

Core of the file system is in the `unix_fs` folder. All tests are in the `tests` folder.

To run tests run the following:  
- `python -m unittest tests`  

## Loopback file system
A Loopback file system is provided under `fusepy_example` directory for use as a standard to 
test our file system against. Also, it serves as a good reference for building our interface to FUSE. 
The Loopback file system will be mounted on one location (`mountpoint`) and it will replicate
all modification under `mountpoint` at a different location (`root`) also provided by the user.  

To run the Loopback file system:  
- Create two temporary directories:  
  - `mkdir ~/tempfs_root`
  - `mkdir ~/tempfs_mountpoint`
- Mount the file system:  
  - `python fusepy_example/loopback.py ~/tempfs_root ~/tempfs_mountpoint`
- `cd` to `mountpoint` and modify as needed, e.g.:
  - `cd ~/tempfs_mountpoint`
  - `echo "this is a test" >> temp.file`
- `cd` to `root` and verify that modifications are made, e.g:
  - `cd ~/tempfs_root`
  - `cat temp.file`
- Unmount the file system: 
  - `umount Loopback`  

Once the file system has been unmounted, modifications under the `mountpoint` are no longer available in the 
terminal. The mirrored modifications under `root` are still available.  