library("jsonlite",quietly = T)
library("yaml",quietly = T)

#Reading config file name
args <- commandArgs(T)
config_file <- args[1]

if(F){
    config_file = "maize.W22.AGPv2.json"
}

#Reading config file and creating config object
config = read_yaml(config_file)

source("code/R/gaf_tools.r")
source("code/R/obo_tools.r")
source("code/R/argot2gaf.r")
source("code/R/pannzer2gaf.r")
source("code/R/fanngo2gaf.r")
source("code/R/logger.r")

#set the logfile and initiate the logger
set_logger(config)

#setting the correct working directory
#setwd(config$input$work_dir)


gaf_dir = paste(config$input$gomap_dir,"/",config$gaf[["mixed_method_dir"]],"/",sep="")
print("===========================")
print(gaf_dir)

species <- config$input$basename

#processing argot2.5 results
argot_result_dir = config[["data"]][["mixed-method"]][["argot2"]][["result_dir"]]
all_argot2_results = dir(argot_result_dir,full.names = T)
argot2_results = all_argot2_results[grep(species,all_argot2_results)]
print(argot2_results)
print("===========================")
stop()
argot2_gaf=paste(gaf_dir,paste(species,"argot2.5","gaf",sep="."),sep = "")
if(!file.exists(argot2_gaf)){
    filter_argot2(in_file=argot2_results,out_file=argot2_gaf,config=config)
}else{
    flog.warn(paste("The",argot2_gaf,"exists. So not Running converting Argot-2.5 results"))
    flog.info(paste("Remove the file to reconvert"))
}

#processing PANNZER results
all_pannzer_results =  dir(config$`mixed-meth`$PANNZER$result_dir,pattern = ".GO",full.names = T)
pannzer_results = all_pannzer_results[grep(species,all_pannzer_results)]
pannzer_gaf = paste(gaf_dir,paste(species,"pannzer","gaf",sep="."),sep = "")
if(!file.exists(pannzer_gaf)){
    pannzer2gaf(in_files = pannzer_results,out_gaf=pannzer_gaf,config)
}else{
    flog.warn(paste("The",pannzer_gaf,"exists. So not Running converting PANNZER results"))
    flog.info(paste("Remove the file to reconvert"))
}

#processing FANN-GO results
fanngo_res= paste(config$`mixed-meth`$fanngo$output,"/",species,".score.txt",sep="")
fanngo_gaf = paste(gaf_dir,paste(species,"fanngo","gaf",sep="."),sep = "")
if(!file.exists(fanngo_gaf)){
    fanngo2gaf(fanngo_res,fanngo_gaf,config)
}else{
    flog.warn(paste("The",fanngo_gaf,"exists. So not Running converting FANN-GO results"))
    flog.info(paste("Remove the file to reconvert"))
}
