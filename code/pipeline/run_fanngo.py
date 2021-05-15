import logging, os, re, sys
from code.utils.basic_utils import check_output_and_run
import pprint as pp
import glob
import csv

def generate_fanngo_file(conf_lines,cwd,fanngo_conf,input_fasta,out_score,run_file):
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

def run_fanngo(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fanngo_sw_conf = config["data"]["mixed-method"]["fanngo"]
    out_score = workdir + fanngo_sw_conf["out_dir"] + "/" + config["input"]["basename"] +".score.txt"
    split_out_dir = workdir + fanngo_sw_conf["out_dir"] + "/split" 
    if os.path.exists(out_score):
        logging.warn("The "+out_score+" exists so not running the fanngo\n\"")
        logging.warn("Delete "+ out_score +" to rerun the previous command")
    else:
        split_files = glob.glob(workdir+config["input"]["big_split_path"]+"/*fa")
        for split_file in split_files:
            run_fanngo_split(config,split_file)
        split_scores = glob.glob(split_out_dir+"/*score.txt")
        if len(split_scores) == len(split_files):
            combine_fanngo_scores(split_scores=split_scores, out_score=out_score)
        else:
            exit("""
            The process to run fanngo on split files has not completed successfully\n 
            Please check the output location and re-run fanngo step again
            """)



def run_fanngo_split(config, split_fa):
    workdir=config["input"]["gomap_dir"]+"/"
    fanngo_sw_conf = config["data"]["mixed-method"]["fanngo"]
    fanngo_conf = config["software"]["fanngo"]
    fanngo_template = fanngo_conf["template"]
    out_base = os.path.basename(split_fa.replace(r".fa",""))
    run_file_path = workdir + fanngo_sw_conf["out_dir"] + "/split/" + out_base +".fanngo.m"
    #print fanngo_template
    conf_lines = open(fanngo_template,"r").readlines()
    run_file = open(run_file_path,"w")
    cwd=os.getcwd()
    output = workdir + run_file_path
    out_score = workdir + fanngo_sw_conf["out_dir"] + "/split/" + out_base +".score.txt"
    input_fasta = workdir+"input/"+config["input"]["fasta"]
    with open(run_file_path,"w") as run_file:
        generate_fanngo_file(conf_lines, cwd, fanngo_conf,split_fa,out_score,run_file)
        run_file.close()
    cmd = ["octave", "--norc", "--no-window-system", "--quiet"]
    os.environ["NPROC"] = str(config["input"]["cpus"])
    check_output_and_run(out_score,cmd,run_file_path)

def combine_fanngo_scores(split_scores,out_score):
    #print(split_scores)
    with open(out_score,"w") as out_score_fh:
        with open(split_scores[0],"r") as split_score_fh:
            out_score_fh.writelines(split_score_fh.readlines())
    with open(out_score,"a") as out_score_fh:
        for split_score in split_scores[1:]:
            print(split_score)
            with open(split_score,"r") as split_score_fh:
                lines = list(split_score_fh.readlines())[1:]
                out_score_fh.writelines(lines)
                split_score_fh.close()
        out_score_fh.close()


def fanngo2gaf(config):
    command = ["Rscript", "code/pipeline/fanngo2gaf.R",config["input"]["config_file"]]
    check_output_and_run("test.pod",command)
