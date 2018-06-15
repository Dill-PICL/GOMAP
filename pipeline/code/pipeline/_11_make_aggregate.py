import logging, os, re
import code.basic_utils as basic_utils
import pprint as pp


def clean_duplicate(config):
    command = ["Rscript", "steps/_11a_clean_duplicate.r",config["input"]["config_file"]]
    basic_utils.check_output_and_run("test.pod",command)

def clean_redundant(config):
    command = ["Rscript","steps/_11b_clean_redundancy.r",config["input"]["config_file"]]
    basic_utils.check_output_and_run("test.pod",command)

def combine_datasets(config):
    command = ["Rscript","steps/_11c_combine_datasets.r",config["input"]["config_file"]]
    basic_utils.check_output_and_run("test.pod",command)
