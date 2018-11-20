#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''

import  logging, sys, re
from pprint import pprint
from code.utils.logging_utils import setlogging

def run_mm_preproc(config):
	"""A really useful function.

	Returns None
	"""

	if config["input"]["email"] is "" or config["input"]["email"] is None:
		logging.error("Please add an email address to the config file")
		sys.exit("You have to add an email address to the config file")
	else:
		valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', config["input"]["email"])
		if not valid_email:
			logging.error("The email address specified is not valid. Please check the email or use a different email address")
			sys.exit("The email in the config file is not valid")

	'''
	Step 6 is to run components of preprocessing pipeline to create input data for the mixed method pipelines
	'''
	from code.pipeline.run_mixmeth_preproc import compile_blast_out
	compile_blast_out(config)
	
	'''
	Step 7 is to run the preprocessing steps for Argot2.5
	sadsdsadsa
	'''
	from code.pipeline.run_argot2 import convert_blast,run_hmmer, compile_blast_tsv
	convert_blast(config)
	compile_blast_tsv(config)
	run_hmmer(config)

	'''
	Step 8 is to run the mixed-method pipeline PANNZER
	'''
	#from code.pipeline.run_pannzer import copy_blast
	#copy_blast(config)

	logging.info("Completed Running mixmeth-preproc step")
	print("Completed Running mixmeth-preproc step")
	
