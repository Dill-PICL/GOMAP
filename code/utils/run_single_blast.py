import logging, sys, os
from blast_utils import run_blast

def run_single_blast(fa_files,config):
    uniprot_db=config["data"]["mixed-method"]["preprocess"]["uniprot_db"]

    for fa_file in fa_files:
        run_blast(fa_file,uniprot_db,config)


    

