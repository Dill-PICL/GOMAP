#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''

import  logging, sys, re
from pprint import pprint
from code.utils.logging_utils import setlogging

def run_mixmeth_blast(config):
	"""A really useful function.

	Returns None
	"""

	'''
	Step 6 is to run components of preprocessing pipeline to create input data for the mixed method pipelines
	'''
	from code.pipeline.run_mixmeth_preproc import process_fasta,make_tmp_fa, run_uniprot_blast, compile_blast_out
	process_fasta(config)
	make_tmp_fa(config)
	run_uniprot_blast(config)
	logging.info("All the blast commands have been run and temporary files have been generated")