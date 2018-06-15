import os, re, logging, subprocess, sys
import pprint as pp
from code.utils.basic_utils import check_output_and_run

def make_blastdb(in_fasta,config):
    fasta_db = in_fasta + ".phr"
    makedb_command = [config["pipeline_location"]+"/"+config["software"]["blast"]["bin"]+"/makeblastdb","-in",in_fasta,"-dbtype","prot","-out",in_fasta,"-title",in_fasta,"-hash_index"]
    check_output_and_run(fasta_db,makedb_command)
