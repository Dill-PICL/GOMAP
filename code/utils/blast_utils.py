import os, re, logging, subprocess, sys
from pprint import pprint
from code.utils.basic_utils import check_output_and_run
import xml.etree.ElementTree as ET
from Bio import SearchIO, SeqIO
from natsort import natsorted
from datetime import datetime


def make_blastdb(in_fasta,config):
    fasta_db = in_fasta + ".phr"
    makedb_command = ["/"+config["software"]["blast"]["bin"]+"/makeblastdb","-in",in_fasta,"-dbtype","prot","-out",in_fasta,"-title",in_fasta,"-hash_index"]
    check_output_and_run(fasta_db,makedb_command)

def check_bl_out(in_fasta,in_xml):
    skip_blast=False
    if not os.path.isfile(in_xml):
        logging.info(in_xml+" does not exist")
        skip_blast=False
    elif os.stat(in_xml).st_size==0:
        logging.info(in_xml+" is empty")
        os.remove(in_xml)
        skip_blast=False
    else:
        try:
            blast_ids = natsorted([qresult.id for qresult in SearchIO.parse(in_xml, 'blast-xml')])
            fa_ids = natsorted([seq.id for seq in SeqIO.parse(in_fasta,"fasta")])
            if blast_ids == fa_ids:
                skip_blast=True
            else:
                logging.info("Number of input and output sequences do not match"+in_xml)
                os.remove(in_xml)
                skip_blast=False
        except:
            logging.info("Cannot read "+in_xml)
            os.remove(in_xml)
            skip_blast=False

    return(skip_blast)
    
def combine_blast_xml(in_files,out_file):
    same_time=False
    if os.path.isfile(out_file):
        logging.info(out_file+" already exists.")
        out_file_time = os.path.getmtime(out_file)
        same_time=True
        for infile in in_files:
            infile_time = os.path.getmtime(infile)
            if infile_time >  out_file_time:
                same_time = True
    if same_time:
        return True

    tree = ET.parse(in_files[0])
    root = tree.getroot()

    with open(out_file,"w") as out_f:
        out_f.write('<?xml version="1.0"?> \n \
<!DOCTYPE BlastOutput PUBLIC "-//NCBI//NCBI BlastOutput/EN" "http://www.ncbi.nlm.nih.gov/dtd/NCBI_BlastOutput.dtd">\n \
<BlastOutput> \n \
')
        for child in root:
            if child.tag not in "BlastOutput_iterations":
                out_f.write(ET.tostring(child))
        out_f.write('<BlastOutput_iterations>')
        for in_file in in_files:
            tmp_tree = ET.parse(in_file)
            tmp_root = tmp_tree.getroot()
            for elem in tmp_root.findall("./BlastOutput_iterations/Iteration"):
                hits = elem.findall("Iteration_hits/Hit")
                for hit in hits:
                    hit_id=hit.find("Hit_id")
                    hit_def=hit.find("Hit_def")
                    hit_def.text = hit_id.text + " " + hit_def.text
                out_f.write(ET.tostring(elem))
        out_f.write('</BlastOutput_iterations>\n')
        out_f.write('</BlastOutput>')
        out_f.close()
    # os.remove(out_file)

    
def run_blast(fa_file,blast_db,config):
    in_file=fa_file
    out_file=re.sub(r'fa$',"xml",fa_file)
    blast_config=config["software"]["blast"]
    workdir=config["input"]["gomap_dir"]+"/"

    blast_opts=config["data"]["mixed-method"]["preprocess"]["blast_opts"]
    skip_blast = check_bl_out(in_file,out_file)

    if skip_blast:
            logging.info(out_file+" already exists.\n The number of sequences in output match input")
    else:
        blast_cmd = [blast_config["bin"]+ "/blastp","-outfmt","5", "-db",blast_db,"-query",in_file,"-out",out_file,"-num_threads",str(config["input"]["cpus"])]+blast_opts
        print(" ".join(blast_cmd))
        check_output_and_run(out_file,blast_cmd)