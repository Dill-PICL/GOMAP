import logging, os, re, json, sys
from code.utils.basic_utils import check_output_and_run
from code.utils.split_fa import split_fasta
from glob import glob
from pprint import pprint
from distutils.version import StrictVersion

def process_fasta(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fa_file=workdir + "input/" + config["input"]["fasta"]
    split_dir=workdir + config["data"]["mixed-meth"]["preprocess"]["fa_path"]
    num_seqs=config["data"]["mixed-meth"]["preprocess"]["num_seqs"]
    split_fasta(fa_file,split_dir,num_seqs)

def make_uniprotdb(config):
    uniprot_fa = config["mixed-meth"]["preprocess"]["uniprot_db"]+".fa"
    uniprot_db = config["mixed-meth"]["preprocess"]["uniprot_db"]
    uniprot_db_dir = os.path.dirname(uniprot_db)

    db_dir = os.path.dirname(uniprot_db)   
    files = os.listdir("mixed-meth/data/blastdb/")
    db_pattern = os.path.basename(uniprot_db)
    db_pattern = re.compile(db_pattern+".*phd")

    db_exist = [(1 if db_pattern.match(tmp_file) is not None else 0) for tmp_file in files]
    makedb_cmd= ["makeblastdb", "-in", uniprot_fa, "-dbtype", "prot", "-out", uniprot_db, "-parse_seqids", "-hash_index","-max_file_sz","10GB"]
    if 1 in db_exist:
        logging.warn("The Uniprot blast database already exists, if not remove the database files to recreate the database")
        logging.info(makedb_cmd)
    else:
        basic_utils.check_output_and_run("temp/uniprotdb",makedb_cmd)

def make_tmp_fa(config):
    workdir=config["input"]["gomap_dir"]+"/"
    fa_path=workdir + config["data"]["mixed-meth"]["preprocess"]["fa_path"]
    tmp_fa_dir=workdir + config["data"]["mixed-meth"]["preprocess"]["blast_out"]+"/temp/"
    fa_pattern=fa_path+"/"+config["input"]["basename"]+"*.fa"
    fa_files = glob(fa_pattern)
    
    for fa_file in fa_files:
        split_fasta(fa_file,tmp_fa_dir,10)

def run_uniprot_blast(config):
    workdir=config["input"]["gomap_dir"]+"/"
    tmp_fa_dir=workdir + config["data"]["mixed-meth"]["preprocess"]["blast_out"]+"/temp"
    fa_pattern=tmp_fa_dir+"/"+config["input"]["basename"]+"*.fa"
    fa_files = sorted(glob(fa_pattern))
    blast_config=config["software"]["blast"]
    uniprot_db=config["data"]["mixed-meth"]["preprocess"]["uniprot_db"]
        
    for fa_file in fa_files:
        in_file=fa_file
        out_file=re.sub(r'fa$',"bl.out",fa_file)
        if os.path.isfile(out_file):
             logging.warn(out_file+" already exists.\nPlease clean to regenerate")
        else:
            print(out_file)
            blast_cmd = [blast_config["bin"]+"/blastp","-outfmt","11", "-db",uniprot_db,"-query",in_file,"-out",out_file,"-num_threads",str(blast_config["num_threads"])]
            check_output_and_run(out_file,blast_cmd)
            logging.info("BLASTP run completed and "+out_file+" created")
            sys.exit()

def compile_blast_out(config):
        fa_path = config["mixed-meth"]["preprocess"]["tmp_bl_dir"]
        all_dirs  = []
        for root, dirs, files in os.walk(fa_path, topdown=False):
            for name in dirs:
                if name.startswith(config['input']['basename']):
                    all_dirs.append(os.path.join(root,name))
        #print(all_dirs)
        logging.warn("-".join(all_dirs))
        for tmp_dir in all_dirs:
            all_tmp_files  = []
            for root, dirs, files in os.walk(tmp_dir, topdown=False):
                for name in files:
                    all_tmp_files.append(os.path.join(root,name))
            bl_files = []
            [bl_files.append(tmp_file) if tmp_file.endswith("bl.out") and config['input']['basename'] in tmp_file else None for tmp_file in all_tmp_files]
            logging.warn(" ".join(bl_files))
            bl_out=os.path.join(config["mixed-meth"]["preprocess"]["blast_out"],os.path.basename(tmp_dir))
            bl_out=bl_out.replace(".fa",".bl.out")
            #print(bl_out)
            if len(bl_files)>0:
                #print(bl_files[0])
                if os.path.isfile(bl_out):
                    logging.warn("The output file "+ bl_out+" exists. Please delete it to regenerate.")
                else:
                    bl_out_f = open(bl_out,"w")
                    for tmp_bl in bl_files:
                        bl_out_f.writelines(open(tmp_bl,"r").readlines())
