import logging, os, re, sys,shutil
from code.utils.basic_utils import check_output_and_run
from pprint import pprint
from lxml import etree, html
from glob import glob
import zipfile
import csv
import requests
from requests_toolbelt import MultipartEncoder
import time


def convert_blast(config):
    workdir=config["input"]["gomap_dir"]+"/"
    blast_xml_dir=workdir+config["data"]["mixed-method"]["preprocess"]["blast_out"]
    blast_xml_files=glob(blast_xml_dir+"/*xml")
    argot_tsv_dir=workdir + config["data"]["mixed-method"]["argot2"]["preprocess"]["blast"]
    xslt_root = etree.parse("config/bl_xml2argot.xsl")
    transform = etree.XSLT(xslt_root)

    for blast_xml in blast_xml_files:
        argot_out=argot_tsv_dir+"/"+re.sub(r'.xml$',".tsv",os.path.basename(blast_xml))
        bl_tree = etree.parse(blast_xml)
        result_txt = transform(bl_tree)
        result_txt.write_output(argot_out)
        zipfile_loc=argot_out+'.zip'
        if os.path.isfile(zipfile_loc):
            logging.info(zipfile_loc +" already exists. Please delete if you need this recreated")
        else:
            zf = zipfile.ZipFile(zipfile_loc, mode='w')
            zf.write(argot_out)
        
def run_hmmer(config):
    workdir = config["input"]["gomap_dir"] + "/"
    fa_dir = workdir+config["data"]["mixed-method"]["preprocess"]["fa_path"]    
    fa_files = glob(fa_dir+"/*fa")
    hmmer_bin = config["software"]["hmmer"]["path"]+"/hmmscan"
    hmmerdb=config["data"]["mixed-method"]["preprocess"]["hmmerdb"]
    cpu = str(config["software"]["hmmer"]["cpu"])
    tmp_file=workdir+"hmmscan.tmp"
        
    for infile in fa_files:
        outfile = workdir+config["data"]["mixed-method"]["argot2"]["preprocess"]["hmmer"] + "/" + re.sub("\.fa",".hmm.out",os.path.basename(infile))
        cmd = [hmmer_bin,"-o",tmp_file,"--tblout",outfile,"--cpu",cpu,hmmerdb,infile]
        zipfile = outfile+".zip"
        check_output_and_run(zipfile,cmd)
        check_output_and_run(zipfile,["zip","-9",zipfile,outfile])
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
            pprint(dict(r_insert.request.headers))
            pprint(dict(r_insert.headers))
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

            print(csv_href,result_file)
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
            pprint(archive.namelist())
            result_file="argot_results_ts0.tsv"            
            archive.extract(result_file,".")
            shutil.move(result_file, outfile)
        else:
            logging.info("Outfile " + outfile + " already exists.\n Please deltreeit to regenerate")
