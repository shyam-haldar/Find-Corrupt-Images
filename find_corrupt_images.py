#!env python3

import getopt
import os
import shutil
import subprocess
import sys

from glob import glob
from itertools import chain

IDENTIFY = '/usr/local/bin/identify'

def get_walker_generator(at_path):
    return (
        chain.from_iterable(
            glob(
                os.path.join( x[0].replace('[', '[[]').replace(']', '[]]'),'*.*' )
            ) for x in os.walk(at_path)
        )
    )


def Split_Filename_Ext(File_Name):
    File_Name_Base = ''
    File_Name_Ext  = ''
    File_Name_List = File_Name.split('.')
    if len(File_Name_List[-1]) <= 5:
        File_Name_Base = '.'.join(File_Name_List[:-1])
        File_Name_Ext = File_Name_List[-1]
    else:
        File_Name_Base = '.'.join(File_Name_List)
    return(File_Name_Base, File_Name_Ext)


def Is_Image_Bad(FileName=None):
    """
    This function checks if an image is corrupt and returns the following status...
    None   When the file is not present or cannot be parsed
    True   When the file is an Image file and is CORRUPT
    False  When the file is an Image file and is GOOD
    """
    Is_Bad = None
    Dimension = [0, 0]
    Dims_Temp = []
    if FileName:
        StdOut, StdErr = None, None
        try:
            Out = subprocess.Popen([IDENTIFY, '-verbose', FileName], 
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            StdOut, StdErr = Out.communicate()
        except:
            pass
        if StdOut:
            Is_Bad = False
            if type(StdOut) == type(b'abc'):
                if b'Corrupt JPEG data' in StdOut:
                    Is_Bad = True
                elif b'Page geometry' in StdOut:
                    for row in StdOut.splitlines():
                        if b'Page geometry' in row:
                            Dims_Temp = row.decode('ascii').split(':')[1].strip().split('+')[0].split('x')
                elif b'identify: no decode delegate for this image format' in StdOut or b'identify: improper image header' in StdOut:
                    Is_Bad = None
            elif type(StdOut) == type('abc'):
                if 'Corrupt JPEG data' in StdOut:
                    Is_Bad = True
                elif 'Page geometry' in StdOut:
                    for row in StdOut.splitlines():
                        if 'Page geometry' in row:
                            Dims_Temp = row.split(':')[1].strip().split('+')[0].split('x')
                elif 'identify: no decode delegate for this image format' in StdOut or 'identify: improper image header' in StdOut:
                    Is_Bad = None
    if len(Dims_Temp) == 2:
        Dimension[0] = int(Dims_Temp[0])
        Dimension[1] = int(Dims_Temp[1])
    return Is_Bad, Dimension


def Main_Function(ImageDirName=None, GoodDirName=None, TrashDirName=None, DryRun=None, HDImages=None, FileSize=None):
    if ImageDirName:
        if DryRun == None:
            DryRun = False
        for fname in get_walker_generator(ImageDirName):
            Image_is_Bad  = None
            File_is_Blank = False
            Dimension     = [0, 0]
            FileSize_Act  = 0
            if os.path.isfile(fname):
                FileSize_Act = os.stat(fname).st_size
                if FileSize_Act == 0:
                    Image_is_Bad  = True
                    File_is_Blank = True
                    Dimension     = [0, 0]
                else:
                    try:
                        Image_is_Bad, Dimension = Is_Image_Bad(fname)
                    except:
                        print('\nException on ', fname)
                        raise
            # When the image is bad...
            if Image_is_Bad == True:
                if File_is_Blank:
                    print('File: %s is BLANK... ' % (fname), end='', flush=True)
                else:
                    print('File: %s is CORRUPT... ' % (fname), end='', flush=True)
                if TrashDirName:
                    print('Move to TrashDir... -- ', end='', flush=True)
                    if DryRun == False:
                        Move_File(fname, TrashDirName)
                    elif DryRun == True:
                        print('MOVED! (Dryrun)')
                else:
                    print()
            # When the image is good...
            elif Image_is_Bad == False:
                if HDImages:
                    if (Dimension[0] >= 1920 and Dimension[1] >= 1080) or (Dimension[1] >= 1920 and Dimension[0] >= 1080):
                        Image_is_Bad = False
                    else:
                        Image_is_Bad = True
                        print('File: %s is NOT_HD... %s  **SKIPPED!' % (fname, repr(Dimension)))
                if Image_is_Bad == False and FileSize:
                    if int(FileSize_Act/1024) < FileSize:
                        Image_is_Bad = True
                        print('File: %s is SMALL...  %s %s  **SKIPPED!' % (fname, repr(Dimension), "(%s KB)"%repr(int(FileSize_Act/1024))))
                if Image_is_Bad == False:
                    print("File: %s is GOOD... %s ++ " % (fname, repr(Dimension)), end='', flush=True)
                    if GoodDirName:
                        print('Move to GoodDir... ', end='', flush=True)
                        if DryRun == False:
                            Move_File(fname, GoodDirName)
                        elif DryRun == True:
                            print('MOVED! (Dryrun)')
                    else:
                        print()
            # When the file is not an image or cannot be parsed...
            elif Image_is_Bad == None:
                print('File: %s is NOT IMAGE!' % (fname))


def Move_File(ImageDirName=None, TrashDirName=None):
    if ImageDirName and TrashDirName:
        if os.path.exists(TrashDirName):
            if os.path.exists(ImageDirName):
                try:
                    shutil.move(ImageDirName, TrashDirName)
                    print('MOVED!')
                except:
                    print("Unable to move: %s to %s" % (ImageDirName, TrashDirName))


def Usage():
    print("""
    Usage: %s [-h|--help] | [(-i Image_Path)|(--image=Image_Path)] [(-g Good_Path)|(--good=Good_Path)]
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
    """ % sys.argv[0])


if __name__ == '__main__':
    argv = sys.argv
    ImageDirName   = None    # This directory will be used for reference, any duplicates files
                             #   in this folder will not be moved/deleted.
    GoodDirName    = None
    TrashDirName   = None    # All the duplicates found in Slave directory will be moved here.
    DryRun         = False
    ActionRequired = 'list'  # The specified action will be taken [list, move, delete]
    ActionReqPH    = ''
    HD_Imgs_Only   = False
    File_Size      = 0
    File_Size_Str  = ''
    if len(argv) == 1 or len(argv) < 3:
        Usage()
        sys.exit(1)
    else:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hi:g:t:dps:", ["help", "image=", "good=", "trash=", "dryrun", "1080p", "size="])
        except getopt.GetoptError as err:
            # print help information and exit:
            # will print something like "option -a not recognized"
            print('ERROR: %s' % err)
            Usage()
            sys.exit(2)

    for Option, Argument in opts:
        if Option in ('-i', '--image'):
            ImageDirName = Argument
        if Option in ('-g', '--good'):
            GoodDirName = Argument
        if Option in ('-t', '--trash'):
            TrashDirName = Argument
        if Option in ('-s', '--size'):
            try:
                File_Size = int(Argument)
            except:
                File_Size = None
                File_Size_Str = Argument
        if Option in ('-d', '--dryrun'):
            DryRun = True
        if Option in ('-p', '--1080p'):
            HD_Imgs_Only = True
        if Option in ('-h', '--help'):
            Usage()
            sys.exit(2)

        ErrorMsg = ''
    if ImageDirName:
        if not os.path.exists(ImageDirName):
            if ErrorMsg:
                ErrorMsg = ErrorMsg + "\r\n" + "Invalid Image directory: %s" % ImageDirName
            else:
                ErrorMsg = "Invalid Image directory: %s" % ImageDirName
    else:
        print('    ERROR! Missing... ImageDirName: %s' % ImageDirName)

    if GoodDirName:
        if not os.path.exists(GoodDirName):
            if ErrorMsg:
                ErrorMsg = ErrorMsg + "\r\n" + "Invalid GOOD directory: %s" % GoodDirName
            else:
                ErrorMsg = "Invalid GOOD directory: %s" % GoodDirName

    if TrashDirName:
        if not os.path.exists(TrashDirName):
            if ErrorMsg:
                ErrorMsg = ErrorMsg + "\r\n" + "Invalid TRASH directory: %s" % TrashDirName
            else:
                ErrorMsg = "Invalid TRASH directory: %s" % TrashDirName

    if File_Size == None:
        if ErrorMsg:
            ErrorMsg = ErrorMsg + "\r\n" + "Invalid File Size provided: %s" % File_Size_Str
        else:
            ErrorMsg = "Invalid File Size provided: %s" % File_Size_Str

    if ErrorMsg:
        print(ErrorMsg)
        Usage()
        sys.exit(2)
    elif not (ImageDirName):
        Usage()
        sys.exit(2)
    else:
        Main_Function(ImageDirName=ImageDirName, GoodDirName=GoodDirName, TrashDirName=TrashDirName, DryRun=DryRun, HDImages=HD_Imgs_Only, FileSize=File_Size)

