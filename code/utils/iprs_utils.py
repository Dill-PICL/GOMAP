import os, re, logging, subprocess, sys
from pprint import pprint
from code.utils.basic_utils import check_output_and_run
from natsort import natsorted
from datetime import datetime


def run_iprs(fa_file,config,iprs_loc=None):
    dom_config = config["data"]["domain"]
    iprs_config = config["software"]["iprs"]
    workdir=config["input"]["gomap_dir"]+"/"
    out_file= re.sub(r"\.fa$","",workdir + "/" + dom_config["split_path"]+"/" + os.path.basename(fa_file))
    temp_dir= workdir + dom_config["tmpdir"] + "/temp"
    
    if iprs_loc is None:
        iprs_loc=iprs_config["path"]

    cmd = [iprs_loc+"/interproscan.sh","-goterms","-pa","-i",fa_file,"-dp","-b",out_file, "-T",temp_dir,"-cpu",str(config["input"]["cpus"])] + iprs_config["options"]
    check_out=out_file+".tsv"
    check_output_and_run(check_out,cmd)

def combine_iprs_tsv(in_files,out_file):
    same_time=False
    if os.path.isfile(out_file):
        logging.info(out_file+" already exists.")
        out_file_time = os.path.getmtime(out_file)
        same_time=True
        for infile in in_files:
            infile_time = os.path.getmtime(infile)
            if infile_time >  out_file_time:
                same_time = False
    if same_time:
        return True

    with open(out_file,"w") as out_f:
        for in_file in in_files:
            with open(in_file,"r") as in_f:
                out_f.writelines(in_f.readlines())
                in_f.close()
        out_f.close()
    
