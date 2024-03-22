# Find-Corrupt-Images

## Note
This script makes use of the tool 'identify' which is part of the ImageMagick suite.

ImageMagick is open-source and cross-platform. More details can be found at https://imagemagick.org/

First, update the value of the variable 'IDENTIFY' to the exact path where the tool identify is installed.

```bash
IDENTIFY = '/usr/local/bin/identify'
```

## Readme
This script searches for corrupt images and moves them to a specified directory.

It can also move images that are good or dimensions > HD (1920x1080) and move them to a directory you specify.

The script also has option to perform a DRY-RUN.


```bash
Usage: find_corrupt_images.py [-h|--help] | [(-i Image_Path)|(--image=Image_Path)] [(-g Good_Path)|(--good=Good_Path)]
          [(-t Trash_Path)|(--trash=Trash_Path)] [(-s File_Size_in_KB)|(--size=File_Size_in_KB)] [-p|--1080p] [-d|--dryrun] ]
Required Arguments:
    -i, --image        Path to the Image Directory

Optional Arguments:
    -g, --good         Good Files are moved here
    -d, --dryrun       Test the action to be taken for MOVE & DELETE.
    -p, --1080p        Only move Good images that have dimensions > HD (1920 x 1080)
    -s, --size         Only move Good images having file size >= given size
    -t, --trash        Corrupt files are moved here

For Help:
    -h, --help         Displays the Command Help Message
```

To run the script just enter the following command...
```bash
find_corrupt_images.py -i /PATH_TO_IMAGE_DIR
```

This is the output you can expect...
```bash
File: ./bad/image_01.jpg is CORRUPT... 
File: ./bad/image_02.jpg is BLANK... 
File: ./bad/image_03.jpg is CORRUPT... 
File: ./bad/image_04.jpg is BLANK... 
File: ./start/image_05.jpg is GOOD... [1920, 1200] ++ 
File: ./start/image_06.jpg is GOOD... [1600, 1200] ++ 
File: ./others/file_01.dmg is NOT IMAGE!
File: ./others/file_02.txt is NOT IMAGE!
```
