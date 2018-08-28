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

	if config["input"]["email"] is "" or config["input"]["email"] is None:
		logging.error("Please add an email address to the config file")
		sys.exit("You have to add an email address to the config file")
	else:
		valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', config["input"]["email"])
		if not valid_email:
			logging.error("The email address specified is not valid. Please check the email or use a different email address")
			sys.exit("The email in the config file is not valid")

	'''
	Step 7 is to run the preprocessing steps for Argot2.5
	sadsdsadsa
	'''
	from code.pipeline.run_argot2 import submit_argot2
	submit_argot2(config)

	'''
	Step 8 is to run the mixed-method pipeline PANNZER
	'''
	from code.pipeline.run_pannzer import  run_pannzer
	run_pannzer(config)