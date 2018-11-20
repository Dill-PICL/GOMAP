import logging, sys, os
from iprs_utils import run_iprs

def run_single_iprs(fa_files,config):
    
    for fa_file in fa_files:
        print(fa_file)
        run_iprs(fa_file,config)

