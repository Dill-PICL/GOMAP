import logging, os, re, ConfigParser
import code.basic_utils as basic_utils
import code.split_fa as split_fa
import pprint as pp

def convert_blast(config):
    archive_dir=config["mixed-meth"]["preprocess"]["blast_out"]
    all_files  = os.listdir(archive_dir)
    all_bl_files = basic_utils.get_files_with_ext(archive_dir,".bl.out")
    bl_files =  []
    [bl_files.append(tmp_file) if tmp_file.startswith(config['input']['basename']) else None for tmp_file in all_bl_files]
    blast_config = config["blast"]
    pannzer_blast=config["mixed-meth"]["PANNZER"]["preprocess"]["blast_files"]

    for bl_file in bl_files:
        in_file = archive_dir + "/" + bl_file
        tmp_xml = "temp/" + bl_file.replace("out","xml")
        outfile = pannzer_blast + "/" + bl_file.replace("out","xml")
        cmd = [blast_config["bin"]+"/"+"blast_formatter","-archive", in_file ,"-out",tmp_xml, "-outfmt", "5","-parse_deflines"]
        basic_utils.check_output_and_run(outfile,cmd)

        if not os.path.isfile(outfile):
            r_id = re.compile(".*Hit_id.*")
            r_def = re.compile(".*Hit_def.*")

            infile = open(tmp_xml, "r")
            outfile = open(outfile,"w")
            id_txt = ""
            for line in infile:
                line = line.rstrip()
                if(r_id.match(line)):
                    id_txt = re.sub('<[^<]+?>', '', line)
                    print >> outfile, line
                elif (r_def.match(line)):
                    #print line
                    out = re.sub('<[^<]+?>', '', line)
                    #print id_txt + out
                    print >> outfile, "<Hit_def>"+id_txt.strip() + " " + out.strip() + "</Hit_def>"
                else:
                    print >> outfile, line
            outfile.close()
            os.remove(tmp_xml)


def run_pannzer(config):
    pannzer_config=config["mixed-meth"]["PANNZER"]
    all_xml_files = basic_utils.get_files_with_ext(pannzer_config["preprocess"]["blast_files"],".xml")
    xml_files = []
    [xml_files.append(tmp_file) if tmp_file.startswith(config['input']['basename']) else None for tmp_file in all_xml_files]
    cwd = os.getcwd()
    os.chdir(cwd+"/"+pannzer_config["path"])

    for xml_file in xml_files:
        blank_config = ConfigParser.ConfigParser()
        blank_config.read(pannzer_config["conf_template"])
        blank_config.set("GENERAL_SETTINGS","INPUT_FOLDER",cwd+"/"+pannzer_config["preprocess"]["blast_files"])
        blank_config.set("GENERAL_SETTINGS","INPUT_FILE",xml_file)
        blank_config.set("GENERAL_SETTINGS","RESULT_FOLDER",cwd+"/"+pannzer_config["result_dir"])
        #blank_config.set("GENERAL_SETTINGS","db",cwd+"/"+pannzer_config["path"]+"/db")
        blank_config.set("GENERAL_SETTINGS","QUERY_TAXON",config["input"]["taxon"])
        out_base = xml_file.replace(".bl.xml","")
        out_conf = cwd+"/"+pannzer_config["conf_dir"]+"/"+out_base+".conf"

        blank_config.set("GENERAL_SETTINGS","RESULT_BASE_NAME",out_base)
        blank_config.set("MYSQL","SQL_DB_HOST",pannzer_config["database"]["SQL_DB_HOST"])
        blank_config.set("MYSQL","SQL_DB_PORT",pannzer_config["database"]["SQL_DB_PORT"])
        blank_config.set("MYSQL","SQL_DB_USER",pannzer_config["database"]["SQL_DB_USER"])
        blank_config.set("MYSQL","SQL_DB_PASSWORD",pannzer_config["database"]["SQL_DB_PASSWORD"])
        blank_config.set("MYSQL","SQL_DB",pannzer_config["database"]["SQL_DB"])
        #pp.pprint(blank_config.items("GENERAL_SETTINGS"))
        blank_config.write(open(out_conf,"w"))
        pannzer_out = blank_config.get("GENERAL_SETTINGS","RESULT_FOLDER")+"/"+out_base + "_results.GO"
        pannzer_cmd = ["python","run.py",out_conf]
        basic_utils.check_output_and_run(pannzer_out,pannzer_cmd)
    os.chdir(cwd)
