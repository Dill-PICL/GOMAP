import os, re, logging, subprocess, sys
from code.utils.basic_utils import check_output_and_run
from Bio import SeqIO
import pprint as pp

outcols='6 qseqid sseqid qlen qstart qend slen sstart send evalue bitscore score length pident nident gaps'

def run_blast(config_input,config_pipline):
    main_config = config["input"]
    ss_config = config["seq-sim"]
    blast_config = config["blast"]
    sys.exit()
    for key in ss_config.keys():
        #running main vs other blast.
        base_dir = os.path.dirname(os.path.dirname(ss_config[key]["fasta"]))
        out_file=base_dir+"/blast/"+main_config["basename"]+"-"+ss_config[key]["basename"]+".bl.out"

        main2other_cmd = [config["blast"]["bin"]+"/blastp","-outfmt",outcols, "-db",ss_config[key]["fasta"],"-query",main_config["filt_fasta"],"-out",out_file,"-num_threads",str(blast_config["num_threads"])]
        #main2other_cmd.extend(blast_config["opt_params"])
        check_output_and_run(out_file,main2other_cmd)

        #running other vs main blast
        base_dir = os.path.dirname(os.path.dirname(ss_config[key]["fasta"]))
        out_file=base_dir+"/blast/"+ss_config[key]["basename"]+"-"+main_config["basename"]+".bl.out"

        other2maize_cmd = [config["blast"]["bin"]+"/blastp","-outfmt",outcols, "-db",main_config["filt_fasta"],"-query",ss_config[key]["fasta"],"-out",out_file,"-num_threads",str(blast_config["num_threads"])]
        #other2maize_cmd.extend(blast_config["opt_params"])
        check_output_and_run(out_file,other2maize_cmd)

def run_tair_blast(config_input,config_pipeline):
    pipeline_loc = config_pipeline["pipeline_location"]+"/"
    tair_config = config_pipeline["data"]["seq-sim"]["TAIR"]
    tair_fa = pipeline_loc+tair_config["basedir"]+"/clean/"+tair_config["file_names"]["basename"]+".fa"
    blast_config = config_pipeline["software"]["blast"]
    blast_bin = pipeline_loc+blast_config["bin"]+"/blastp"

    #running main vs other blast.
    tmp_base_dir = tair_config["tmpdir"]
    main2other_file=tmp_base_dir+"/blast/"+config_input["files"]["basename"]+"-vs-"+tair_config["file_names"]["basename"]+".bl.out"

    input_fa = config_input["dir"]["input_dir"]+"/clean/"+config_input["files"]["basename"]+".fa"

    main2other_cmd = [blast_bin,"-outfmt",outcols, "-db",tair_fa,"-query",input_fa,"-out",main2other_file,"-num_threads",str(blast_config["num_threads"]),"-evalue",str(blast_config["evalue"])]


    check_output_and_run(main2other_file,main2other_cmd)

    #running other vs main blast
    other2maize_file=tmp_base_dir+"/blast/"+tair_config["file_names"]["basename"]+"-vs-"+config_input["files"]["basename"]+".bl.out"

    other2maize_cmd = [blast_bin,"-outfmt",outcols, "-db",input_fa,"-query",tair_fa,"-out",other2maize_file,"-num_threads",str(blast_config["num_threads"]),"-evalue",str(blast_config["evalue"])]

    check_output_and_run(other2maize_file,other2maize_cmd)

def run_uniprot_blast(config_input,config_pipeline):
    pipeline_loc = config_pipeline["pipeline_location"]+"/"
    uniprot_config = config_pipeline["data"]["seq-sim"]["uniprot"]
    uniprot_fa = pipeline_loc + uniprot_config["basedir"] + "/clean/"+uniprot_config["filenames"]["basename"]+".fa"
    blast_config = config_pipeline["software"]["blast"]
    blast_bin = pipeline_loc+blast_config["bin"]+"/blastp"

    #running main vs other blast.
    tmp_base_dir = uniprot_config["tmpdir"]
    main2other_file=tmp_base_dir+"/blast/"+config_input["files"]["basename"]+"-vs-"+uniprot_config["filenames"]["basename"]+".bl.out"

    input_fa = config_input["dir"]["input_dir"]+"/clean/"+config_input["files"]["basename"]+".fa"
    main2other_cmd = [blast_bin,"-outfmt",outcols, "-db",uniprot_fa,"-query",input_fa,"-out",main2other_file,"-num_threads",str(blast_config["num_threads"]),"-evalue",str(blast_config["evalue"])]
    check_output_and_run(main2other_file,main2other_cmd)

    #running other vs main blast
    other2maize_file=tmp_base_dir+"/blast/"+uniprot_config["filenames"]["basename"]+"-vs-"+config_input["files"]["basename"]+".bl.out"
    other2maize_cmd = [blast_bin,"-outfmt",outcols, "-db",input_fa,"-query",uniprot_fa,"-out",other2maize_file,"-num_threads",str(blast_config["num_threads"]),"-evalue",str(blast_config["evalue"])]
    check_output_and_run(other2maize_file,other2maize_cmd)

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
