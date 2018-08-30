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

def xml2tsv(in_xml):
    out_tsv = re.sub(r"xml$","tsv",in_xml)
    if not os.path.exists(out_tsv):
        logging.info("Converting %s into %s." % (in_xml,out_tsv))
        xslt_root = etree.parse("config/bl_xml2argot.xsl")
        transform = etree.XSLT(xslt_root)
        bl_tree = etree.parse(in_xml)
        result_txt = transform(bl_tree)
        result_txt.write_output(out_tsv)
    else:
        logging.info("Not converting %s into %s. Output file exists" % (in_xml,out_tsv))
        
def concat_tsv(all_tmp_bl_files,argot_out):
    with open(argot_out,"w+") as oufile:
        for tmp_tsv in all_tmp_bl_files:
            oufile.write(open(tmp_tsv,"r").read())

def convert_blast(config):
    workdir=config["input"]["gomap_dir"]+"/"
    ncpus=int(config["input"]["cpus"])
    tmp_bl_dir=workdir + config["data"]["mixed-method"]["preprocess"]["blast_out"]+"/temp"
    argot_tsv_dir=workdir + config["data"]["mixed-method"]["argot2"]["preprocess"]["blast"]
    all_tmp_bl_files = sorted(glob(tmp_bl_dir+"/*.xml"))

    Parallel(n_jobs=ncpus)(delayed(xml2tsv)(tmp_bl_file) for tmp_bl_file in all_tmp_bl_files)

    tmp_fa_dir=workdir + config["data"]["mixed-method"]["preprocess"]["fa_path"]
    fa_pattern=tmp_fa_dir+"/"+config["input"]["basename"]+"*.fa"
    fa_files = sorted(glob(fa_pattern))

    for fa_file in fa_files:        
        tmp_fa_pat=re.sub(r'.fa$',"",os.path.basename(fa_file))
        argot_out=argot_tsv_dir+"/"+tmp_fa_pat+".tsv"
        bl_pattern=tmp_bl_dir+"/"+tmp_fa_pat+"*.tsv"
        all_tmp_bl_files = sorted(glob(bl_pattern))
        concat_tsv(all_tmp_bl_files,argot_out)
        zipfile_loc=argot_out+'.zip'
        if os.path.isfile(zipfile_loc):
            logging.info(zipfile_loc +" already exists. Please delete if you need this recreated")
        else:
            zf = zipfile.ZipFile(zipfile_loc, mode='w',compression=zipfile.ZIP_DEFLATED)
            zf.write(argot_out)
        os.remove(argot_out)    
        
def run_hmmer(config):
    workdir = config["input"]["gomap_dir"] + "/"
    fa_dir = workdir+config["data"]["mixed-method"]["preprocess"]["fa_path"]    
    fa_files = glob(fa_dir+"/*fa")
    hmmer_bin = config["software"]["hmmer"]["path"]+"/hmmscan"
    hmmerdb=config["data"]["mixed-method"]["preprocess"]["hmmerdb"]
    cpu = str(config["input"]["cpus"])
    tmp_file=workdir+"hmmscan.tmp"
        
    for infile in fa_files:
        outfile = workdir+config["data"]["mixed-method"]["argot2"]["preprocess"]["hmmer"] + "/" + re.sub("\.fa",".hmm.out",os.path.basename(infile))
        cmd = [hmmer_bin,"-o",tmp_file,"--tblout",outfile,"--cpu",cpu,hmmerdb,infile]
        zipfile_loc = outfile+".zip"
        check_output_and_run(zipfile_loc,cmd)
        if os.path.exists(outfile):
            zf = zipfile.ZipFile(zipfile_loc, 'w',zipfile.ZIP_DEFLATED)
            zf.write(outfile)
        if os.path.isfile(tmp_file):
            os.remove(tmp_file)

def submit_argot2(config):
    workdir = config["input"]["gomap_dir"] + "/"
    argot_config=config["data"]["mixed-method"]["argot2"]
    argot2_blast_dir=workdir+argot_config["preprocess"]["blast"]+"/"
    argot2_hmmer_dir=workdir+argot_config["preprocess"]["hmmer"]+"/"
    fa_path=workdir + config["data"]["mixed-method"]["preprocess"]["fa_path"]+"/"
    fa_pattern=fa_path+"*fa"
    fa_files = [ re.sub(".fa","",os.path.basename(fa_file)) for fa_file in glob(fa_pattern)]
    for fa_file in fa_files:
        blast_file=glob(argot2_blast_dir+fa_file+"*tsv")[0]
        blast_zip=blast_file+".zip"
        with zipfile.ZipFile(blast_zip, 'w') as myzip:
            myzip.write(blast_file,os.path.basename(blast_file))
        
        hmmer_file=glob(argot2_hmmer_dir+fa_file+"*out")[0]
        hmmer_zip=hmmer_file+".zip"
        with zipfile.ZipFile(hmmer_zip, 'w') as myzip:
            myzip.write(hmmer_file,os.path.basename(hmmer_file))
            
        payload=argot_config["payload"]
        payload["email"] = config["input"]["email"]
        payload["descr"] = fa_file
        payload['scient_name'] = config["input"]["species"]
        payload["tax_id"] = config["input"]["taxon"]
        payload["taxon_ID"] = config["input"]["taxon"]
        files={
            "blast_file":(blast_zip,open(blast_zip, 'rb'),'text/plain'),
            "hmmer_file":(hmmer_zip,open(hmmer_zip, 'rb'),'text/plain')
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
        html_file=workdir+argot_config["preprocess"]["html"]+"/"+fa_file+".insert.html"   
        
        if os.path.isfile(html_file):
            logging.info("This file has been previously submitted")
            logging.info("Remove "+html_file+ " to resubmit")
        else:
            s = requests.session()
            r_batch = s.post("http://www.medcomp.medicina.unipd.it/Argot2-5/form_batch.php",headers=headers)
            #r_batch = s.post("http://localhost/test/upload.php",headers=headers,data=payload,files=files)

            r_insert = s.post(argot_url,data=payload,files=files,headers=headers)
            # pprint(dict(r_insert.request.headers))
            # pprint(dict(r_insert.headers))
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
