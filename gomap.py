#!/usr/bin/env python2

'''
Importing all the modules necessary for running the pipeline
pprint is only needed for debugging purposes
'''

import  os, re, logging, json, sys, argparse, jsonmerge, yaml
from argparse import RawTextHelpFormatter
from pprint import pprint
from code.gomap_preprocess import run_preprocess
from code.gomap_aggregate import aggregate
from code.gomap_setup import setup
from code.gomap_seqsim import run_seqsim
from code.gomap_domain import run_domain
from code.gomap_mm_preproc import run_mm_preproc
from code.gomap_mixmeth import run_mixmeth

from code.utils.basic_utils import init_dirs, copy_input
from code.utils.logging_utils import setlogging

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
main_parser = argparse.ArgumentParser(description='Welcome to running the GOMAP pipeline',formatter_class=RawTextHelpFormatter)
main_parser.add_argument('--config',help="The config file in yaml format. \nPlease see test/config.yml for an example.",required=True)
main_parser.add_argument('--step',help="GO-MAP has two distinct steps. Choose the step to run \n1) preprocess \n2) annotate", choices=['setup','seqsim','domain','mixmeth-preproc','mixmeth','aggregate'],required=True)
main_args = main_parser.parse_args()

'''
    This section loads the pipeline base config file from the pipeline script
    location. and loads the pipleine configutation
'''

os.chdir("/opt/GOMAP/")

with open("config/pipeline.yml") as tmp_file:
    pipe_config = yaml.load(tmp_file)

config_file = pipe_config["input"]["workdir"]+"/"+main_args.config
with open(config_file) as tmp_file:
    user_config = yaml.load(tmp_file)
    user_config["input"]["workdir"] = os.path.dirname(config_file)

config = merger.merge(pipe_config, user_config)
config = init_dirs(config)
copy_input(config)

conf_out = config["input"]["gomap_dir"]+"/"+config["input"]["basename"]+".all.yml"
config["input"]["config_file"] = conf_out
with open(conf_out,"w") as out_f:
	yaml.dump(config,out_f)

'''
Depending the step selected by the user we are going to run the relevant part of GO-MAP
'''

if main_args.step == "seqsim":
    print("Running Sequence-similarity based Annotation Step")
    setlogging(config,"seqsim")
    logging.info("Running Sequence-similarity based Annotation Step")
    run_seqsim(config)
elif main_args.step == "domain":
    print("Running Domain Based Annotation Step")
    setlogging(config,"domain")
    logging.info("Running Domain Based Annotation Step")
    run_domain(config)
elif main_args.step == "mixmeth-preproc":
    print("Running preprocessing step for mixed-methods")
    setlogging(config,"mixmeth-preproc")
    logging.info("Running preprocessing step for mixed-methods")
    run_mm_preproc(config)
elif main_args.step == "mixmeth":
    print("Running mixed-method based annotations")
    setlogging(config,"mixmeth")
    logging.info("Running mixed-method based annotations")
    run_mixmeth(config)
elif main_args.step == "aggregate":
    print("Running Aggregate Step")
    setlogging(config,"aggregate")
    logging.info("Running Aggregate Step")
    aggregate(config)
elif main_args.step == "setup":
    print("Downloading data from CyVerse")
    setlogging(config,"base")
    logging.info("Downloading data from CyVerse")
    setup(config)

