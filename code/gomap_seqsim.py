#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''

import  logging, sys, re
from pprint import pprint
from code.utils.logging_utils import setlogging

def run_seqsim(config):
	"""A really useful function.

	Returns None
	"""

	logging.info("Processing Sequence-Similarity Steps")
	from code.pipeline.run_rbh_blast import make_input_blastdb,run_tair_blast,run_uniprot_blast,get_rbh_annotations
	make_input_blastdb(config)
	run_tair_blast(config)
	run_uniprot_blast(config)
	get_rbh_annotations(config)