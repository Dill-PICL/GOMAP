import logging, os, re, sys,shutil
from code.utils.basic_utils import check_output_and_run
from pprint import pprint
from joblib import Parallel, delayed
from lxml import etree, html
from glob import glob
import zipfile
import csv
import requests
from requests_toolbelt import MultipartEncoder
import time
from Bio import SeqIO
from natsort import natsorted

def xml2tsv(in_xml):
    out_tsv = re.sub(r"xml$","tsv",in_xml)
    if not os.path.exists(out_tsv):
        logging.info("Converting %s into %s." % (in_xml,out_tsv))
        xslt_root = etree.parse("config/bl_xml2argot.xsl")
        transform = etree.XSLT(xslt_root)
        bl_tree = etree.parse(in_xml)
        result_txt = str(transform(bl_tree)).splitlines(True)
        sel_lines = [ line if re.match(r"[0-9A-Za-z]",line) else "" for line in result_txt]
        with open(out_tsv,"w") as outfile:
            outfile.writelines(sel_lines)
            outfile.close()
    else:
        logging.info("Not converting %s into %s. Output file exists" % (in_xml,out_tsv))
        
def concat_tsv(all_tmp_bl_files,argot_out):
    with open(argot_out,"w+") as outfile:
        for tmp_tsv in all_tmp_bl_files:
            with open(tmp_tsv,"r") as infile:
                outfile.write(infile.read())
                infile.close()

def convert_blast(config):
    workdir=config["input"]["gomap_dir"]+"/"
    ncpus=int(config["input"]["cpus"])
    tmp_bl_dir=workdir + config["data"]["mixed-method"]["preprocess"]["blast_out"]+"/temp"
    argot_tsv_dir=workdir + config["data"]["mixed-method"]["argot2"]["preprocess"]["blast"]
    all_tmp_bl_files = sorted(glob(tmp_bl_dir+"/*.xml"))

    Parallel(n_jobs=ncpus)(delayed(xml2tsv)(tmp_bl_file) for tmp_bl_file in all_tmp_bl_files)

def compile_blast_tsv(config):
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
            tmp_xml = [re.sub(r'\.fa$','.tsv',x) for x in fa_files[counter_start:counter_curr+1]]
            chunks.append(tmp_xml)
            counter_start = counter_curr+1
        elif counter_curr+1 == len(fa_files):
            tmp_xml = [re.sub(r'\.fa$','.tsv',x) for x in fa_files[counter_start:]]
            chunks.append(tmp_xml)
    
    argot_tsv_dir=workdir + config["data"]["mixed-method"]["argot2"]["preprocess"]["blast"]+"/"
    for i in range(len(chunks)):
        tsv_out=argot_tsv_dir+config["input"]["basename"]+"."+str(i+1)+".tsv"
        zipfile_loc=tsv_out+'.zip'
        concat_tsv(chunks[i],tsv_out)
        if os.path.isfile(zipfile_loc):
            logging.info(zipfile_loc +" already exists. Please delete if you need this recreated")
        else:
            zf = zipfile.ZipFile(zipfile_loc, mode='w',compression=zipfile.ZIP_DEFLATED)
            zf.write(tsv_out,os.path.basename(tsv_out))

        
def run_hmmer(config):
    workdir = config["input"]["gomap_dir"] + "/"
    fa_dir = workdir+config["input"]["split_path"]
    fa_files = natsorted(glob(fa_dir+"/*fa"))
    hmmer_bin = config["software"]["hmmer"]["path"]+"/hmmsearch"
    hmmerdb=config["data"]["mixed-method"]["preprocess"]["hmmerdb"]
    cpu = str(config["input"]["cpus"])
    tmp_file=workdir+"hmmscan.tmp"
    num_seqs=int(config["input"]["num_seqs"])

    chunks = []
    counter_start=0
    counter_curr=-1
    chunk_seqs = 0
    chunk_count=0
    all_seqs = []
    for fa_file in fa_files:
        counter_curr = counter_curr+1
        seqs = list(SeqIO.parse(fa_file, "fasta"))
        num_fa_records = len(seqs)
        chunk_seqs = chunk_seqs + num_fa_records
        all_seqs = all_seqs + seqs

        if chunk_seqs % num_seqs == 0 or fa_file == fa_files[-1]:
            chunk_count=chunk_count+1
            out_fa=workdir+config["data"]["mixed-method"]["argot2"]["preprocess"]["hmmer"] + "/" + config["input"]["basename"]+"."+str(chunk_count)+".fa"
            SeqIO.write(all_seqs, out_fa, "fasta")
            all_seqs=[]
            chunk_seqs=0
        
    hmmer_dir=workdir+config["data"]["mixed-method"]["argot2"]["preprocess"]["hmmer"]
    fa_files = glob(hmmer_dir+"/*fa")
    for infile in fa_files:
        outfile = re.sub("\.fa",".hmm.out",infile)
        cmd = [hmmer_bin,"-o",tmp_file,"--tblout",outfile,"--cpu",cpu,hmmerdb,infile]
        zipfile_loc = outfile+".zip"
        check_output_and_run(zipfile_loc,cmd)
        if os.path.exists(outfile):
            zf = zipfile.ZipFile(zipfile_loc, 'w',zipfile.ZIP_DEFLATED)
            zf.write(outfile,os.path.basename(outfile))
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)
        

def submit_argot2(config):
    workdir = config["input"]["gomap_dir"] + "/"
    argot_config=config["data"]["mixed-method"]["argot2"]
    argot2_blast_dir=workdir+argot_config["preprocess"]["blast"]+"/"
    argot2_hmmer_dir=workdir+argot_config["preprocess"]["hmmer"]+"/"
    fa_path=workdir + config["data"]["mixed-method"]["preprocess"]["fa_path"]+"/"
    tsv_pattern=argot2_blast_dir+"*tsv"
    tsv_files = [ re.sub(".tsv","",os.path.basename(fa_file)) for fa_file in glob(tsv_pattern)]
    for tsv_file in tsv_files:
        blast_file=glob(argot2_blast_dir+tsv_file+"*tsv.zip")[0]
        hmmer_file=glob(argot2_hmmer_dir+tsv_file+"*out.zip")[0]
                    
        payload=argot_config["payload"]
        payload["email"] = config["input"]["email"]
        payload["descr"] = tsv_file
        payload['scient_name'] = config["input"]["species"]
        payload["tax_id"] = config["input"]["taxon"]
        payload["taxon_ID"] = config["input"]["taxon"]
        files={
            "blast_file":(blast_file,open(blast_file, 'rb')),
            "hmmer_file":(hmmer_file,open(hmmer_file, 'rb'))
            }
       
        headers = {
            "Host": "www.medcomp.medicina.unipd.it",
            "Origin": "www.medcomp.medicina.unipd.it",
            'User-agent': 'Mozilla/5.0 (X11; Linux x86_64)',
            'Referer': "http://www.medcomp.medicina.unipd.it/Argot2-5/form_batch.php",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Pragma": "no-cache",
            "Connection": "keep-alive"
        }

        argot_url=argot_config["batch_url"]
        html_file=workdir+argot_config["preprocess"]["html"]+"/"+tsv_file+".insert.html"   
        
        if os.path.isfile(html_file):
            logging.info("This file has been previously submitted")
            logging.info("Remove "+html_file+ " to resubmit")
        else:
            logging.info("Submitting %s and %s to Argot2.5" % (os.path.basename(blast_file),os.path.basename(hmmer_file)))
            print("Submitting %s and %s to Argot2.5" % (os.path.basename(blast_file),os.path.basename(hmmer_file)))
            s = requests.session()
            r_batch = s.post("http://www.medcomp.medicina.unipd.it/Argot2-5/form_batch.php",headers=headers)
            #r_batch = s.post("http://localhost/test/upload.php",headers=headers,data=payload,files=files)

            r_insert = s.post(argot_url,data=payload,files=files,headers=headers)
            with open(html_file,"w") as outfile:
                outfile.writelines(r_insert.text)
        

def download_argot2(config):
    workdir = config["input"]["gomap_dir"] + "/"
    argot_config=config["data"]["mixed-method"]["argot2"]
    html_dir=workdir+argot_config["preprocess"]["html"]+"/"
    result_dir=workdir+argot_config["result_dir"]+"/"
    argot_files = glob(html_dir+"*html")
    for argot_file in argot_files:
        result_file = result_dir+re.sub(".insert.html",".tsv",os.path.basename(argot_file))
        if os.path.isfile(result_file):
            logging.info("The result file already exists.")
            logging.info("Delete "+result_file+" if you want to redownload it" )
        else:
            logging.info("Downloading results for " +os.path.basename(result_file) + " from Argot2.5 webservice")
            tree = html.parse(argot_file)
            all_links = tree.findall(".//a")
            link_href = [ link.attrib["href"] for link in all_links if "getStatus_batch.php" in link.attrib["href"] ][0]
            res_link = re.sub("getStatus_batch.php","viewResults_batch.php",link_href)
            r = requests.get(res_link)
            res_tree = html.fromstring(r.text)
            all_links = res_tree.findall(".//a")
            csv_href = argot_config["baseurl"]+"/"+[ link.attrib["href"] for link in all_links if "getTSVFile.php" in link.attrib["href"] ][0]

            csv_r = requests.get(csv_href)
            with open(result_file+".zip","w") as outfile:
                outfile.write(csv_r.content)
    
    # r = requests.get(csv_href)
    # with open("")


def process_argot2(config):
    workdir = config["input"]["gomap_dir"] + "/"
    result_dir = workdir + config["data"]["mixed-method"]["argot2"]["result_dir"]
    zipfiles=glob(result_dir+"/*zip")
    for result_zip in zipfiles:
        outfile=re.sub(r".zip","",result_zip)
        if not os.path.isfile(outfile):
            logging.info("Unzipping " + os.path.basename(result_zip))
            archive = zipfile.ZipFile(result_zip)
            result_file="argot_results_ts0.tsv"
            archive.extract(result_file,workdir)
            shutil.move(workdir+"/"+result_file, outfile)
        else:
            logging.info("Outfile " + outfile + " already exists.\n Please deltreeit to regenerate")
