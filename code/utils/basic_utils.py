import os, re, logging, subprocess, sys

def make_dir(file):
    dir_name = os.path.dirname(file)
    if not os.path.exists(dir_name) and dir_name != '':
        os.makedirs(dir_name)

def check_output_and_run(outfile,command,stdin_file=None,stdout_file=None):
    make_dir(outfile)
    if not os.path.exists(outfile):
        logging.info(outfile+" not present so running command\n" +" ".join(command))
        if stdin_file is not None:
            stdin_file = open(stdin_file,"r")
        if stdout_file is not None:
            stdout_file = open(stdout_file,"w")
        subprocess.check_call(command,stdin=stdin_file,stdout=stdout_file)
    else:
        logging.warn("The "+outfile+" exists so not running the command\n\""+" ".join(command)+"\"")
        logging.warn("Delete existing output file(s) to rerun the previous command")

def get_files_with_ext(in_dir,extension="fa"):
    all_files  = os.listdir(in_dir)
    out_files = []
    [out_files.append(tmp_file) if tmp_file.endswith(extension) else None for tmp_file in all_files]
    return out_files

def get_output_file(config):
    print(config)
