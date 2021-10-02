#!/usr/bin/env python2

import logging, os, re,sys
from code.utils.basic_utils import check_output_and_run
from code.utils.split_fa import split_fasta
from code.utils.iprs_utils import combine_iprs_tsv
from pprint import pprint
from glob import glob
from pyrocopy import pyrocopy

def process_fasta(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fa_file=workdir + "input/" + config["input"]["fasta"]
    split_base=workdir + config["input"]["split_path"]+"/"+config["input"]["basename"]
    print(split_base)
    num_seqs=config["input"]["small_seqs"]
    split_fasta(fa_file,int(num_seqs),split_base)

def run_iprs(config):
    dom_config = config["data"]["domain"]
    iprs_config = config["software"]["iprs"]
    workdir=config["input"]["gomap_dir"]+"/"
    fa_pattern=workdir + config["input"]["split_path"]+"/"+config["input"]["basename"]+"*fa"
    fa_files = sorted(glob(fa_pattern))
    #print(fa_files)

    iprs_src=config["software"]["iprs"]["path"]
    # print(src_db)
    iprs_loc="/tmpdir/iprs"
    results = pyrocopy.copy(iprs_src,iprs_loc)

    if config["input"]["mpi"] is True:
        from code.utils.run_mpi_iprs import run_mpi_iprs
        run_mpi_iprs(fa_files,config)
    else:
        from code.utils.run_single_iprs import run_single_iprs
        run_single_iprs(fa_files,config,iprs_loc)


def compile_iprs_out(config):
    dom_config = config["data"]["domain"]
    workdir=config["input"]["gomap_dir"]+"/"
    tsv_pattern = workdir+"/"+dom_config["split_path"]+"/*tsv"
    tsv_files = sorted(glob(tsv_pattern))
    out_file = workdir + "/" + dom_config["tmpdir"] + "/" + config["input"]["basename"]+".tsv"
    combine_iprs_tsv(tsv_files,out_file)
    #print(tsv_files)


def iprs2gaf(config):
    dom_config = config["data"]["domain"]
    input_config = config["input"]
    workdir=config["input"]["gomap_dir"]+"/"
    tsv_base=workdir + dom_config["tmpdir"] + "/" + config["input"]["basename"]
    infile=tsv_base+".tsv"
    tmpfile=tsv_base+".go.tsv"
    gaf_dir=workdir + config["data"]["gaf"]["raw_dir"]+"/"

    tmp_iprs=open(tmpfile,"w")

    with open(infile,"r+") as raw_iprs:
        for line in raw_iprs:
            if re.search("GO:",line) is not None:
                tmp_iprs.write(line)
                #print >> tmp_iprs, line
    tmp_iprs.close()


    out_gaf = gaf_dir+os.path.basename(infile)
    tool_ext="."+config["data"]["domain"]["tool"]["name"] + ".gaf"
    out_gaf = re.sub(".tsv",tool_ext,out_gaf)
    cmd = ["Rscript","code/pipeline/iprs2gaf.r",config["input"]["config_file"]]
    check_output_and_run(out_gaf,cmd)
