import logging, sys, os
from blast_utils import run_blast

def run_single_blast(fa_files,db,config):
    logging.info(fa_files)
    
    for fa_file in fa_files:
        run_blast(fa_file,db,config)


    

