#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''
import  logging, sys
from pprint import pprint

def run_preprocess(config):
	'''
		Step 1 is to create a working directory in the current location and
	'''


	'''
	Step 2 is to get the blast searches done, to and against TAIR and UniProt datasets
	'''
	logging.info("Processing Sequence-Similarity Steps")
	from code.pipeline.run_rbh_blast import make_input_blastdb,run_tair_blast,run_uniprot_blast,get_rbh_annotations
	make_input_blastdb(config)
	run_tair_blast(config)
	run_uniprot_blast(config)
	get_rbh_annotations(config)

	'''
	Step 5 is to run interproscan5 against the clean input protein sequences
	'''
	logging.info("Running domain annotations using IPRS")
	from code.pipeline.run_iprs import run_iprs,iprs2gaf
	run_iprs(config)
	iprs2gaf(config)
   
	'''
	Step 6 is to run components of preprocessing pipeline to create input data for the mixed method pipelines
	'''
	from code.pipeline.run_mm_preproc import process_fasta,make_tmp_fa, run_uniprot_blast, compile_blast_out
	process_fasta(config)
	make_tmp_fa(config)
	run_uniprot_blast(config)
	logging.info("All the blast commands have been run and temporary files have been generated")
	compile_blast_out(config)
	

	'''
	Step 7 is to run the preprocessing steps for Argot2.5
	'''
	from code.pipeline.run_argot2 import convert_blast,run_hmmer
	convert_blast(config)
	print("Running Hmmer")	
	run_hmmer(config)
	sys.exit()

	'''
	Step 8 is to run the mixed-method pipeline PANNZER
	'''
	import code.pipeline._8_run_pannzer as run_pannzer
	run_pannzer.convert_blast(config)
	run_pannzer.run_pannzer(config)

	'''
	Step 9 is to run FANN-GO tools and get predictions
	'''
	import code.pipeline._9_run_fanngo as run_fanngo
	run_fanngo.run_fanngo(config)

	logging.info("First part of GAMER pipeline has been completed")
