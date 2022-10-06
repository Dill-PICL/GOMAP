#!/usr/bin/env python2

'''
This submodule lets the user download the data files necessary for running the GOMAP pipline from CyVerse

Currently the files are stored in Gokul's personal directory so the download has to be initiated by gokul's own CyVerse account with icommands
'''
import  os, re, logging, json, sys, argparse, jsonmerge, gzip, shutil
from pprint import pprint
from code.utils.basic_utils import check_output_and_run
import tarfile
cyverse_path="i:/iplant/home/shared/dillpicl/gomap/GOMAP-data.v1.2/"
from code.utils.logging_utils import setlogging

def setup(config):
    setlogging(config,"setup")
    """
    setup(config)

    This function downloads the **GOMAP-data.tar.gz** directory from CyVerse and extracts the content to the **data** directory. The steps run by this function is given below

    1. asdsdsa
    2. sadsadsad
    3. sadsadsad

    Parameters
    ----------
    config : dict
        The config dict generated in the gomap.py script.
    """
    
    outdir="data/"
    cmd = ["irsync","-rv",cyverse_path,outdir]
    logging.info("Downloading file from Cyverse using irsync")
    #The irsync will checksum the files on both ends and dtermine if the download is necessary and will only download if necessary
    # might take time to check if the files needs to be downloaded
    print(os.getcwd())
    print(" ".join(cmd))
    check_output_and_run("outfile",cmd)

    with open("data/compress_files.txt","r") as comp_files:
        counter=0
        for infile in comp_files.readlines():
            counter=counter+1
            outfile = outdir+infile.strip()
            gzfile = outdir+infile.strip()+".gz"
            if os.path.exists(gzfile):
                if os.path.exists(outfile):
                    print( gzfile + " already extracted")
                else:
                    print("Extracting " +  gzfile)
                    with gzip.open(gzfile,"rb") as in_f:
                        with open(outfile,"wb") as out_f:
                            shutil.copyfileobj(in_f,out_f)
                    os.remove(gzfile)
            else:
                print(gzfile + " doesn't exist")

    with open("data/tar_files.txt","r") as comp_files:
        for infile in comp_files.readlines():
            infile=infile.strip()
            outfile = outdir+infile.strip()
            tar_f = outdir+infile.strip()+".tar.gz"
            base_dir=os.path.basename(outfile)
            if os.path.exists(tar_f):
                if os.path.exists(outfile):
                    print(tar_f + " already extracted")
                else:
                    print("Extracting " +  tar_f)
                    with tarfile.open(tar_f) as tar:
                        
                        import os
                        
                        def is_within_directory(directory, target):
                            
                            abs_directory = os.path.abspath(directory)
                            abs_target = os.path.abspath(target)
                        
                            prefix = os.path.commonprefix([abs_directory, abs_target])
                            
                            return prefix == abs_directory
                        
                        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                        
                            for member in tar.getmembers():
                                member_path = os.path.join(path, member.name)
                                if not is_within_directory(path, member_path):
                                    raise Exception("Attempted Path Traversal in Tar File")
                        
                            tar.extractall(path, members, numeric_owner=numeric_owner) 
                            
                        
                        safe_extract(tar, "data/")
                    os.remove(tar_f)
            else:
                print(tar_f + " doesn't exist")