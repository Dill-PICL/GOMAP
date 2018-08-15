#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''

import  logging, sys, re
from pprint import pprint
from code.utils.logging_utils import setlogging

def run_mixmeth(config):
	"""A really useful function.

	Returns None
	"""
	setlogging(config,"preprocess")

	'''
	Step 7 is to run the preprocessing steps for Argot2.5
	sadsdsadsa
	'''
	from code.pipeline.run_argot2 import convert_blast,run_hmmer,submit_argot2
	convert_blast(config)
	run_hmmer(config)
	submit_argot2(config)

	'''
	Step 8 is to run the mixed-method pipeline PANNZER
	'''
	from code.pipeline.run_pannzer import copy_blast, run_pannzer
	copy_blast(config)
	run_pannzer(config)

	
