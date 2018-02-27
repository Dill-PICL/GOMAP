import os, re, logging, subprocess, sys
import code.basic_utils as basic_utils
from Bio import SeqIO

outcols='6 qseqid sseqid qlen qstart qend slen sstart send evalue bitscore score length pident nident gaps'
def make_dbs(config):
    fasta_files = [config["input"]["filt_fasta"]]
    for key in config["seq-sim"].keys():
        fasta_files.append(config["seq-sim"][key]["fasta"])

    for fasta in fasta_files:
        fasta_db = fasta + ".phr"
        makedb_command = [config["blast"]["bin"]+"/makeblastdb","-in",fasta,"-dbtype","prot","-out",fasta,"-hash_index"]
        basic_utils.check_output_and_run(fasta_db,makedb_command)

def run_blast(config):
    main_config = config["input"]
    ss_config = config["seq-sim"]
    blast_config = config["blast"]
    for key in ss_config.keys():
        #running main vs other blast.
        base_dir = os.path.dirname(os.path.dirname(ss_config[key]["fasta"]))
        out_file=base_dir+"/blast/"+main_config["basename"]+"-"+ss_config[key]["basename"]+".bl.out"

        main2other_cmd = [config["blast"]["bin"]+"/blastp","-outfmt",outcols, "-db",ss_config[key]["fasta"],"-query",main_config["filt_fasta"],"-out",out_file,"-num_threads",str(blast_config["num_threads"])]
        #main2other_cmd.extend(blast_config["opt_params"])
        basic_utils.check_output_and_run(out_file,main2other_cmd)

        #running other vs main blast
        base_dir = os.path.dirname(os.path.dirname(ss_config[key]["fasta"]))
        out_file=base_dir+"/blast/"+ss_config[key]["basename"]+"-"+main_config["basename"]+".bl.out"

        other2maize_cmd = [config["blast"]["bin"]+"/blastp","-outfmt",outcols, "-db",main_config["filt_fasta"],"-query",ss_config[key]["fasta"],"-out",out_file,"-num_threads",str(blast_config["num_threads"])]
        #other2maize_cmd.extend(blast_config["opt_params"])
        basic_utils.check_output_and_run(out_file,other2maize_cmd)

def get_rbh_annotations(config):
    file_exist = True
    ss_config = config["seq-sim"]
    for key in ss_config.keys():
        base_dir = os.path.dirname(os.path.dirname(ss_config[key]["fasta"]))
        out_file=base_dir+"/blast/"+config["input"]["basename"]+"-"+ss_config[key]["basename"]+".bl.out"
        logging.info(out_file)
        out_gaf=config["gaf"]["raw_dir"]+"/"+config["input"]["basename"]+"."+ss_config[key]["species"]+".gaf"
        logging.info(out_gaf)
        if not os.path.isfile(out_file) or not os.path.isfile(out_gaf):
            #print(out_file)
            file_exist = False

    if not file_exist:
        command = ["Rscript", "steps/_4_run_rbh.r",config["input"]["config_file"]]
        subprocess.call(command)
    else:
        logging.info("RBH and GAF Files already exist. Please remove them if you want to rerun the analysis.")
