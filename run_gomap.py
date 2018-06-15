#!/usr/bin/env python2

'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''
import  os, re, logging, json, sys, argparse, jsonmerge
from argparse import RawTextHelpFormatter

from pprint import pprint

from jsonmerge import Merger
schema = {
             "properties": {
                 "bar": {
                     "mergeStrategy": "append"
                 }
             }
         }
merger = Merger(schema)

'''
    Parsing the input config file that will be supplied by te user.
'''
main_parser = argparse.ArgumentParser(description='Welcome to running the GO-MAP pipeline',formatter_class=RawTextHelpFormatter)
main_parser.add_argument('--config',help="The config file in json format. \nPlease see config.json for an example. \nIf a config file is not provided then the default parameters will be used.",default="/workdir/config.json")
main_parser.add_argument('--step',help="GO-MAP has two distinct steps. Choose the step to run \n1) preprocess \n2) annotate", choices=['preprocess','annotate'],default="preprocess")
main_args = main_parser.parse_args()

'''
    This section loads the pipeline base config file from the pipeline script
    location. and loads the pipleine configutation
'''

with open("pipeline.json") as tmp_file:
    pipe_config = json.load(tmp_file)

if  main_args.config:
    config_file = main_args.config
    with open(config_file) as tmp_file:
        user_config = json.load(tmp_file)

config = merger.merge(pipe_config, user_config)


logging_config = config["logging"]
log_file = config["input"]["workdir"] + "/" + config["input"]["basename"] + '.log'
logging.basicConfig(filename=log_file,level=logging_config['level'],filemode='w+',format=logging_config["format"],datefmt=logging_config["formatTime"])

'''
Depending the step selected by the user we are going to run the relevant part of GO-MAP
'''

if main_args.step == "preprocess":
    logging.info("Running Preprocessing Step")

elif main_args.step == "annotate":
    logging.info("Running Annotation Step")


# '''
# Step 1 is to clean the fasta file downloaded from TAIR to get longest
# representative sequence. We need to check if the filt file already exists
# The TAIR file cannot be downloaded anymore. It has become a subscription
# only resource and is not freely distibuted
# '''
# logging.info("Cleaning TAIR Files")
# from code.process.clean_tair import clean_tair_fasta,tair_go2gaf,clean_tair_data
# clean_tair_data(config,config_file)
#
# '''
# Step 2 is to get relavent sequences from UniProt for the taxonomy ids mentioned in the config files
# '''
# logging.info("Downloading and processing UniProt files")
# from code.process.clean_uniprot import clean_uniprot_data
# clean_uniprot_data(config,config_file)
