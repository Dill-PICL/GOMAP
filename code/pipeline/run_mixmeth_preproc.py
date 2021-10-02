import logging, os, re, json, sys
from code.utils.basic_utils import check_output_and_run
from code.utils.split_fa import split_fasta
from code.utils.blast_utils import combine_blast_xml
from glob import glob
from pprint import pprint
from Bio import SeqIO
from distutils.version import StrictVersion
from natsort import natsorted
from pyrocopy import pyrocopy

def process_fasta(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fa_file=workdir + "input/" + config["input"]["fasta"]
    split_base=workdir + "/" + config["input"]["split_path"]+"/"+config["input"]["basename"]
    num_seqs=config["input"]["small_seqs"]
    split_fasta(fa_file,int(num_seqs),split_base)


def make_uniprotdb(config):
    uniprot_fa = config["mixed-method"]["preprocess"]["uniprot_db"]+".fa"
    uniprot_db = config["mixed-method"]["preprocess"]["uniprot_db"]
    uniprot_db_dir = os.path.dirname(uniprot_db)

    db_dir = os.path.dirname(uniprot_db)   
    files = os.listdir("mixed-method/data/blastdb/")
    db_pattern = os.path.basename(uniprot_db)
    db_pattern = re.compile(db_pattern+".*phd")

    db_exist = [(1 if db_pattern.match(tmp_file) is not None else 0) for tmp_file in files]
    makedb_cmd= ["makeblastdb", "-in", uniprot_fa, "-dbtype", "prot", "-out", uniprot_db, "-parse_seqids", "-hash_index","-max_file_sz","10GB"]
    if 1 in db_exist:
        logging.warn("The Uniprot blast database already exists, if not remove the database files to recreate the database")
        logging.info(makedb_cmd)
    else:
        check_output_and_run("temp/uniprotdb",makedb_cmd)

def make_tmp_fa(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fa_file=workdir + "input/" + config["input"]["fasta"]
    tmp_fa_base=workdir + config["data"]["mixed-method"]["preprocess"]["blast_out"]+"/temp/"+config["input"]["basename"]
    small_seqs=config["data"]["mixed-method"]["preprocess"]["small_seqs"]
    split_fasta(fa_file,small_seqs,tmp_fa_base)

def run_uniprot_blast(config):
    if config["input"]["mpi"] is True:
        from code.utils.run_mpi_blast import run_mpi_blast
        run_mpi_blast(config)
    else:
        from code.utils.run_single_blast import run_single_blast
        print("Running the single blast step")
        workdir=config["input"]["gomap_dir"]+"/"
        #print(workdir)
        tmp_fa_dir=workdir + config["input"]["split_path"]+"/"
        dest=workdir+config["data"]["mixed-method"]["preprocess"]["blast_out"]+"/temp/"
        results = pyrocopy.copy(tmp_fa_dir,dest)
        #print(results)
        fa_pattern=dest+config["input"]["basename"]+"*.fa"
        fa_files = sorted(glob(fa_pattern))
        
        uniprot_db=config["pipeline"]["pipeline_loc"]+"/"+config["data"]["mixed-method"]["preprocess"]["uniprot_db"]
        src_db=os.path.dirname(uniprot_db)
        # print(src_db)
        dest_db="/tmpdir/blastdb"
        results = pyrocopy.copy(src_db,dest_db)
        uniprot_db=dest_db+"/"+os.path.basename(config["data"]["mixed-method"]["preprocess"]["uniprot_db"])
        run_single_blast(fa_files,uniprot_db,config)


def compile_blast_out(config):
    workdir=config["input"]["gomap_dir"]+"/"
    num_seqs=int(config["input"]["num_seqs"])
    tmp_bl_dir=workdir + config["data"]["mixed-method"]["preprocess"]["blast_out"]+"/temp"
    fa_pattern=tmp_bl_dir+"/"+config["input"]["basename"]+"*.fa"
    fa_files = natsorted(glob(fa_pattern))

    chunks = []
    counter_start=0
    counter_curr=-1
    chunk_seqs = 0
    for fa_file in fa_files:
        counter_curr = counter_curr+1
        all_seqs = list(SeqIO.parse(fa_file, "fasta"))
        num_fa_records = len(all_seqs)
        chunk_seqs = chunk_seqs + num_fa_records
        if chunk_seqs % num_seqs == 0:
            tmp_xml = [re.sub(r'\.fa$','.xml',x) for x in fa_files[counter_start:counter_curr+1]]
            chunks.append(tmp_xml)
            counter_start = counter_curr+1
        elif counter_curr+1 == len(fa_files):
            tmp_xml = [re.sub(r'\.fa$','.xml',x) for x in fa_files[counter_start:]]
            chunks.append(tmp_xml)   

    bl_dir=workdir + config["data"]["mixed-method"]["pannzer"]["preprocess"]["blast"]+"/"
    for i in range(len(chunks)):
        bl_out=bl_dir+config["input"]["basename"]+"."+str(i+1)+".xml"
        combine_blast_xml(chunks[i],bl_out)