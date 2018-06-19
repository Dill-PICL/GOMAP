import logging, os, re, sys
from code.utils.basic_utils import check_output_and_run
from pprint import pprint


def mixed2gaf(config):
    command = ["Rscript", "code/pipeline/mixed2gaf.r",config["input"]["config_file"]]
    print(command)
    check_output_and_run("test.pod",command)

def filter_mixed(config):
    command = ["Rscript","code/pipeline/filter_mixed.r",config["input"]["config_file"]]
    basic_utils.check_output_and_run("test.pod",command)
