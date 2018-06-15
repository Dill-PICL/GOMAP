library("jsonlite",quietly = T)

source("code/gaf_tools.r")
source("code/obo_tools.r")
source("code/gen_utils.r")
source("code/get_comp.r")
source("code/get_nr_dataset.r")
source("code/logger.r")

#Reading config file name
args <- commandArgs(T)
config_file <- args[1]

if(F){
    config_file = "maize.B73.AGPv4.json"
}

#Reading config file and creating config object
config = fromJSON(config_file)

#set the logfile and initiate the logger
set_logger(config)

#setting the correct working directory
#setwd(config$input$work_dir)

nr_dir = config$gaf$non_red_dir
all_nr_datasets=dir(nr_dir,full.names = T)
nr_datasets = all_nr_datasets[grep(config$input$basename,all_nr_datasets)]
nr_datasets

agg_dir=paste(config$gaf$agg_dir,"/",sep="")
out_gaf=paste(agg_dir,paste(config$input$basename,"aggregate","gaf",sep="."),sep = "")

if(file.exists(out_gaf)){
    flog.warn(paste("The",out_gaf,"exists, So not regenerating aggregate dataset"))
    flog.info(paste("Remove the ",out_gaf,"file to regenerate"))
}else{
    flog.info(paste("The",out_gaf,"missing, So generating the dataset"))
    compile_comprehensive(nr_datasets,out_gaf,config)
}
