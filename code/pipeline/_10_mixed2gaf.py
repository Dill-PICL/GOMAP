import logging, os, re
import code.basic_utils as basic_utils
import pprint as pp


def mixed2gaf(config):
    command = ["Rscript", "steps/_10a_mixed2gaf.r",config["input"]["config_file"]]
    basic_utils.check_output_and_run("test.pod",command)

def filter_mixed(config):
    command = ["Rscript","steps/_10b_filter_mixed.r",config["input"]["config_file"]]
    basic_utils.check_output_and_run("test.pod",command)
