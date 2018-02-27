#!/usr/bin/env python2
'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''
import  os, re, logging, json, sys, argparse, jsonmerge
import pprint as pp

'''
    Parsing the input config file that will be supplied by te user.
'''
main_parser = argparse.ArgumentParser(description='Running the first part of GAMER pipeline')
main_parser.add_argument('config_file',help="The config file in json format. Please see config.json for an example")
main_args = main_parser.parse_args()

'''
    This section loads the pipeline base config file from the pipeline script
    location. and loads the pipleine configutation
'''
pipeline_config_file = os.path.dirname(sys.argv[0]) + "/pipeline.json"

with open(pipeline_config_file) as tmp_file:
    config_pipline = json.load(tmp_file)

'''
    This section loads the input parameters for the users current job.
'''
with open(main_args.config_file) as tmp_file:
    config_input = json.load(tmp_file)

#This merges the pipline and user configs and makes a single configuration
config = jsonmerge.merge(config_pipline,config_input)
logging_config = config["input"]["logging"]

log_file = config["input"]["dir"]["work_dir"] +"/"+ logging_config["file_name"] + ('.log' if re.match(".*\.log$",logging_config["file_name"]) == None else '')

pp.pprint(log_file)

logging.basicConfig(filename=log_file,level=logging_config['level'],filemode='w+',format=logging_config["format"],datefmt=logging_config["formatTime"])
sys.exit()
'''=======================================================================
Step 1 is to clean the input fasta file downloaded from Gramene/Ensembl to
get longest representative sequence
======================================================================='''
from steps._1_clean_input import clean_input
clean_input(config)

'''
Step 4 is to get the blasts done, to and against TAIR and UniProt datasets
'''
logging.info("Processing Sequence-Similarity Steps")
import steps._4_run_rbh as run_rbh
run_rbh.make_dbs(config)
run_rbh.run_blast(config)
run_rbh.get_rbh_annotations(config)

'''
Step 5 is to run interproscan5 against the clean input protein sequences
'''
logging.info("Running domain annotations using " +config["domain"]["software"])
import steps._5_run_iprs as run_iprs
run_iprs.run_iprs(config)
run_iprs.iprs2gaf(config)

'''
Step 6 is to run components of preprocessing pipeline to create input data for the mixed method pipelines
'''
import steps._6_run_preprocess as run_preprocess
run_preprocess.process_fasta(config)
run_preprocess.make_uniprotdb(config)
run_preprocess.make_tmp_fa(config)
run_preprocess.run_uniprot_blast(config)
logging.info("All the blast commands have been run and temporary files have been generated")
run_preprocess.compile_blast_out(config)

'''
Step 7 is to run the preprocessing steps for Argot2.5
'''
import steps._7_run_argot2 as run_argot
run_argot.convert_blast(config)
run_argot.run_hmmer(config)

'''
Step 8 is to run the mixed-method pipeline PANNZER
'''
import steps._8_run_pannzer as run_pannzer
run_pannzer.convert_blast(config)
run_pannzer.run_pannzer(config)

'''
Step 9 is to run FANN-GO tools and get predictions
'''
import steps._9_run_fanngo as run_fanngo
run_fanngo.run_fanngo(config)

logging.info("First part of GAMER pipeline has been completed")
