#!/usr/bin/env python2

'''
This file includes the steps to aggregate
'''

import  os, re, logging, json, sys
from pprint import pprint


def aggregate(config):
    '''
    annotate(config)

    Parameters
    ----------
    config : dict
        The config dict generated in the gomap.py script.
    '''

    from code.pipeline.run_argot2 import process_argot2
    process_argot2(config)
    
    
    from code.pipeline.mixed2gaf import mixed2gaf, filter_mixed
    mixed2gaf(config)
    filter_mixed(config)

    
    from code.pipeline.make_aggregate import clean_duplicate, clean_redundant, aggregate_datasets
    clean_duplicate(config)
    clean_redundant(config)
    aggregate_datasets(config)
