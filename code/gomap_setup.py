#!/usr/bin/env python2

'''
This submodule lets the user download the data files necessary for running the GOMAP pipline from CyVerse

Currently the files are stored in Gokul's personal directory so the download has to be initiated by gokul's own CyVerse account with icommands
'''
import  os, re, logging, json, sys, argparse, jsonmerge
from pprint import pprint
from code.utils.basic_utils import check_output_and_run
import tarfile
cyverse_path="i:/iplant/home/shared/dillpicl/gomap/GOMAP-data/"
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
    
    outfile="data/"+os.path.basename(cyverse_path)
    cmd = ["irsync","-rsv",cyverse_path,outfile]
    logging.info("Downloading file from Cyverse using irsync")
    #The irsync will checksum the files on both ends and dtermine if the download is necessary and will only download if necessary
    # might take time to check if the files needs to be downloaded
    check_output_and_run("outfile",cmd)

    # if not os.path.isfile("data/software/PANNZER/GO.py"):
    #     logging.info("Extracting the files")
    #     tar = tarfile.open(outfile)
    #     # tar.extract("GOMAP-data/","data/")
    #     try:
    #         tar.extractall("data/")
    #     except:
    #         print("Error extracting files")
    #     os.remove(outfile)
    # else:
    #     logging.info("The GOMAP-data files have been already extracted")
 
