library("jsonlite",quietly = T)

source("code/gaf_tools.r")
source("code/obo_tools.r")
source("code/gen_utils.r")
source("code/get_nr_dataset.r")
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

uniq_gaf_dir = config$gaf$uniq_dir
uniq_datasets=dir(uniq_gaf_dir,full.names = T)
in_gaf=uniq_datasets[1]
tmp_out = lapply(uniq_datasets,function(in_gaf){
    out_gaf=gsub(uniq_gaf_dir,config$gaf$non_red_dir,in_gaf,fixed = T)
    if(file.exists(out_gaf)){
        flog.warn(paste("The",out_gaf,"exists, So not removing duplicates from",in_gaf))
        flog.info(paste("Remove the ",out_gaf,"file to regenerate"))
    }else{
        flog.info(paste("The",out_gaf,"missing, So removing duplicates from",in_gaf))
        remove_redundancy(in_gaf,out_gaf,config)
    }
})
