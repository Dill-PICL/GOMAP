import logging, os, re, sys
from code.utils.basic_utils import check_output_and_run
import pprint as pp


def run_fanngo(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fanngo_sw_conf = config["data"]["mixed-method"]["fanngo"]
    fanngo_conf = config["software"]["fanngo"]
    fanngo_template = fanngo_conf["path"]+"/"+fanngo_conf["template"]
    run_file_path = workdir + fanngo_sw_conf["out_dir"] + "/" + config["input"]["basename"] +".fanngo.m"
    #print fanngo_template
    conf_lines = open(fanngo_template,"r").readlines()
    run_file = open(run_file_path,"w")
    cwd=os.getcwd()
    output = workdir + run_file_path
    out_score = workdir + fanngo_sw_conf["out_dir"] + "/" + config["input"]["basename"] +".score.txt"
    input_fasta = workdir+"input/"+config["input"]["fasta"]


    for line in conf_lines:
        line = line.strip()
        if line.find("$PATH") > -1:
            code_path = cwd+"/"+fanngo_conf["path"]+"/code"
            outline = line.replace("$PATH",code_path)
            print >>run_file, outline
        elif line.find("$INPUT_FASTA") > -1:
            outline = line.replace("$INPUT_FASTA",input_fasta)
            print >>run_file, outline
        elif line.find("$OUTPUT_SCORE") > -1:
            outline = line.replace("$OUTPUT_SCORE",out_score)
            print >>run_file, outline
        else:
            print >>run_file, line
    run_file.close()
    cmd = ["octave", "--norc", "--no-window-system", "--quiet"]
    print(" ".join(cmd))
    os.environ["NPROC"] = str(config["input"]["cpus"]);
    check_output_and_run(out_score,cmd,run_file_path)

