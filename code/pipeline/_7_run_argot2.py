import logging, os, re
import code.basic_utils as basic_utils
import code.split_fa as split_fa
import pprint as pp

def convert_blast(config):
    archive_dir=config["mixed-meth"]["preprocess"]["blast_out"]
    all_bl_files = basic_utils.get_files_with_ext(archive_dir,".bl.out")
    bl_files = []
    [bl_files.append(tmp_file) if tmp_file.startswith(config['input']['basename']) else None for tmp_file in all_bl_files]
    blast_config = config["blast"]
    argot_blast=config["mixed-meth"]["Argot"]["preprocess"]["blast_files"]
    outfmt="6 qseqid sseqid evalue"
    for bl_file in bl_files:
        in_file = archive_dir + "/" + bl_file
        out_file = argot_blast + "/" + bl_file.replace("out","tsv")
        cmd = [blast_config["bin"]+"/"+"blast_formatter","-archive", in_file ,"-out",out_file, "-outfmt", outfmt]
        # print(cmd)
        basic_utils.check_output_and_run(out_file,cmd)
        zip_file = out_file+".zip"
        basic_utils.check_output_and_run(zip_file,["zip","-9",zip_file,out_file])

def run_hmmer(config):
    fa_dir = config["mixed-meth"]["preprocess"]["fa_path"]
    all_fa_files = basic_utils.get_files_with_ext(fa_dir,".fa")
    fa_files = []
    [fa_files.append(tmp_file) if tmp_file.startswith(config['input']['basename']) else None for tmp_file in all_fa_files]
    hmmer_bin = config["hmmer"]["path"]+"/hmmscan"
    seqdb = config["hmmer"]["seqdb"]
    cpu = str(config["hmmer"]["cpu"])
    tmp_file="temp/hmmer.out"
    for fa_file in fa_files:
        infile = fa_dir + "/" + fa_file
        outfile = config["mixed-meth"]["Argot"]["preprocess"]["hmmer_files"] + "/" + re.sub("\.fa",".hmm.out",fa_file)
        cmd = [hmmer_bin,"-o",tmp_file,"--tblout",outfile,"--cpu",cpu,seqdb,infile]
        basic_utils.check_output_and_run(outfile,cmd)
        zipfile = outfile+".zip"
        basic_utils.check_output_and_run(zipfile,["zip","-9",zipfile,outfile])
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)
