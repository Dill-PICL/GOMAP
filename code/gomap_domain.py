#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''

import  logging, sys, re
from pprint import pprint
from code.utils.logging_utils import setlogging

def run_domain(config):
    """A really useful function.

    Returns None
    """
    
    '''
    Step 5 is to run interproscan5 against the clean input protein sequences
    '''
    logging.info("Running domain annotations using IPRS")
    from code.pipeline.run_iprs import run_iprs,iprs2gaf,process_fasta,compile_iprs_out
    process_fasta(config)
    run_iprs(config)
    compile_iprs_out(config)
    iprs2gaf(config)