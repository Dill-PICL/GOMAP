import logging, os, re
import code.basic_utils as basic_utils

def run_iprs(config):
    dom_config = config["domain"]
    input_config = config["input"]
    out_file=dom_config["output"] + input_config["basename"]
    input_fa = input_config["filt_fasta"]
    cmd = [dom_config["path"]+""+dom_config["bin"],"-goterms","-pa","-i",input_config["filt_fasta"],"-dp","-b",out_file]
    check_out=out_file+".tsv"
    basic_utils.check_output_and_run(check_out,cmd)

def iprs2gaf(config):
    dom_config = config["domain"]
    input_config = config["input"]
    out_file=dom_config["output"] + input_config["basename"] + ".tsv"
    #print(out_file)

    tmp_file="temp/"+os.path.basename(out_file)
    tmp_iprs=open(tmp_file,"w")
    #print(tmp_file)

    with open(out_file,"r+") as raw_iprs:
        for line in raw_iprs:
            if re.search("GO:",line) is not None:
                tmp_iprs.write(line)
                #print >> tmp_iprs, line
    tmp_iprs.close()
    out_gaf = "gaf/raw/"+os.path.basename(out_file)
    out_gaf = re.sub(".tsv","",out_gaf)
    out_gaf = out_gaf +"."+ config["domain"]["software"] + ".gaf"
    cmd = ["Rscript","steps/_5_iprs2gaf.r",config["input"]["config_file"]]
    basic_utils.check_output_and_run(out_gaf,cmd)
