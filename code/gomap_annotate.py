import  os, re, logging, json, sys
from pprint import pprint


def annotate(config):
    print("annotate")

    from code.pipeline.run_argot2 import process_argot2
    process_argot2(config)
    
    # '''
    # Step 10 is to convert the outputs from CAFA to GAF 2.0 files to work with the
    # rest of the code written in R
    # '''
    from code.pipeline.mixed2gaf import mixed2gaf, filter_mixed
    mixed2gaf(config)
    sys.exit()
    filter_mixed(config)

    # '''
    # Step 11 is to clean the gaf files and create non-redundant GAF for final dataset
    # '''
    # import steps._11_make_aggregate as make_aggregate
    # make_aggregate.clean_duplicate(config)
    # make_aggregate.clean_redundant(config)
    # make_aggregate.combine_datasets(config)
