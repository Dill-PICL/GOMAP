library("jsonlite",quietly = T)

source("code/gaf_tools.r")
source("code/obo_tools.r")
source("code/filter_mixed.r")
source("code/logger.r")


#Reading config file name
args <- commandArgs(T)
config_file <- args[1]

#Reading config file and creating config object
config = fromJSON(config_file)

#set the logfile and initiate the logger
set_logger(config)

#setting the correct working directory
#setwd(config$input$work_dir)

mm_gaf_dir=paste(config$`mixed-meth`$gaf,"/",sep="")
raw_gaf_dir=paste(config$gaf$raw_dir,"/",sep="")

#processing argot2.5 results
argot2_cafa=paste(mm_gaf_dir,paste(config$input$basename,"argot2.5","gaf",sep="."),sep = "")
argot2_raw=paste(raw_gaf_dir,paste(config$input$basename,"argot2.5","gaf",sep="."),sep = "")
if(!file.exists(argot2_raw)){
    filter_mixed_gaf(argot2_cafa,argot2_raw,"Argot",config=config)
}else{
    flog.warn(paste("The",argot2_raw,"exists. So not filtering Argot-2.5 results"))
    flog.info(paste("Remove the file to reconvert"))
}

#processing PANNZER results
pannzer_cafa = paste(mm_gaf_dir,paste(config$input$basename,"pannzer","gaf",sep="."),sep = "")
pannzer_raw = paste(raw_gaf_dir,paste(config$input$basename,"pannzer","gaf",sep="."),sep = "")
if(!file.exists(pannzer_raw)){
    filter_mixed_gaf(pannzer_cafa,pannzer_raw,"PANNZER",config=config)
}else{
    flog.warn(paste("The",pannzer_raw,"exists. So not filtering PANNZER results"))
    flog.info(paste("Remove the file to reconvert"))
}

#processing FANN-GO results

fanngo_cafa = paste(mm_gaf_dir,paste(config$input$basename,"fanngo","gaf",sep="."),sep = "")
fanngo_raw = paste(raw_gaf_dir,paste(config$input$basename,"fanngo","gaf",sep="."),sep = "")
if(!file.exists(fanngo_raw)){
    filter_mixed_gaf(fanngo_cafa,fanngo_raw,"fanngo",config)
}else{
    flog.warn(paste("The",fanngo_raw,"exists. So not filtering FANN-GO results"))
    flog.info(paste("Remove the file to reconvert"))
}
