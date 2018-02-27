import argparse, re, sys, os, logging
from Bio import SeqIO

def clean_uniprot_fasta(in_data,out_fasta):
    with open("temp/uniport.tmp.fa","w+") as tmp_fa:
        tmp_fa.writelines(in_data)
        seqs = []
        for record in SeqIO.parse("temp/uniport.tmp.fa", "fasta"):
            id_split = record.id.split("|")
            record.id = id_split[1]
            seqs.append(record)
        SeqIO.write(seqs,out_fasta,"fasta")
    os.remove("temp/uniport.tmp.fa")
