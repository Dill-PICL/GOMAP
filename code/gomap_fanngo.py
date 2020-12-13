#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''

import  logging, sys, re
from pprint import pprint
from code.utils.logging_utils import setlogging
from code.utils.split_fa import split_fasta

def process_fasta(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fa_file=workdir + "input/" + config["input"]["fasta"]
    split_base=workdir + "/" + config["input"]["split_path"]+"/"+config["input"]["basename"]
    num_seqs=config["input"]["small_seqs"]
    split_fasta(fa_file,int(num_seqs),split_base)

def run_fanngo(config):
	"""A really useful function.

	Returns None
	"""

	'''
	Step 7 is to run FANNGO
	'''
	from code.pipeline.run_fanngo import run_fanngo
	process_fasta(config)
	run_fanngo(config)
