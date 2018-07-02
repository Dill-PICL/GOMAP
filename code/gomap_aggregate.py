#!/usr/bin/env python2

'''
This file includes the steps to aggregate
'''

import  os, re, logging, json, sys
from pprint import pprint
from code.utils.logging_utils import setlogging

def aggregate(config):
    setlogging(config,"aggregate")
    '''
    annotate(config)

    Parameters
    ----------
    config : dict
        The config dict generated in the gomap.py script.
    '''

    from code.pipeline.run_argot2 import process_argot2,download_argot2
    logging.info("Obtaining and aggregating Argot2.5 results")
    download_argot2(config)
    process_argot2(config)
    
    from code.pipeline.mixed2gaf import mixed2gaf, filter_mixed
    logging.info("Filtering mixed-method GAF")
    mixed2gaf(config)
    filter_mixed(config)

    
    from code.pipeline.make_aggregate import clean_duplicate, clean_redundant, aggregate_datasets
    logging.info("Cleaning and aggregating GAF files")
    clean_duplicate(config)
    clean_redundant(config)
    aggregate_datasets(config)
