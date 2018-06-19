import  os, re, logging, json, sys, argparse
from pprint import pprint


def annotate(config):
    print("annotate")
    # '''
    # Step 10 is to convert the outputs from CAFA to GAF 2.0 files to work with the
    # rest of the code written in R
    # '''
    from code.pipline.mixed2gaf import mixed2gaf, filter_mixed
    mixed2gaf.mixed2gaf(config)
    mixed2gaf.filter_mixed(config)

    # '''
    # Step 11 is to clean the gaf files and create non-redundant GAF for final dataset
    # '''
    # import steps._11_make_aggregate as make_aggregate
    # make_aggregate.clean_duplicate(config)
    # make_aggregate.clean_redundant(config)
    # make_aggregate.combine_datasets(config)
