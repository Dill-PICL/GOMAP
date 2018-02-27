import  os, re, logging, json, sys, argparse
import pprint as pp

parser = argparse.ArgumentParser(description='Running the second part of GAMER pipeline. Please make sure you have gotten the results from Argot2.5 before proceeding')
parser.add_argument('config_file',help="The config file in json format. Please see config.json for an example")
args = parser.parse_args()


with open(args.config_file) as data_file:
    config = json.load(data_file)

log_file = config["input"]["basename"] + ".log"

logging.basicConfig(filename=log_file,level=config['logging']['level'],filemode='a',format=config['logging']["format"],datefmt=config['logging']["formatTime"])

'''
Step 10 is to convert the outputs from CAFA to GAF 2.0 files to work with the
rest of the code written in R
'''
import steps._10_mixed2gaf as mixed2gaf
mixed2gaf.mixed2gaf(config)
mixed2gaf.filter_mixed(config)

'''
Step 11 is to clean the gaf files and create non-redundant GAF for final dataset
'''
import steps._11_make_aggregate as make_aggregate
make_aggregate.clean_duplicate(config)
make_aggregate.clean_redundant(config)
make_aggregate.combine_datasets(config)
