library("jsonlite",quietly = T)

source("code/R/gaf_tools.r")
source("code/R/obo_tools.r")
source("code/R/rm_dup_annot.r")
source("code/R/gen_utils.r")
source("code/R/logger.r")



#Reading config file name
args <- commandArgs(T)
config_file <- args[1]

#Reading config file and creating config object
config = fromJSON(config_file)

#set the logfile and initiate the logger
set_logger(config)

#setting the correct working directory
#setwd(config$input$work_dir)

raw_gaf_dir = config$gaf$raw_dir
dup_datasets=dir(raw_gaf_dir,full.names = T)

tmp_out = lapply(dup_datasets,function(in_gaf){
    out_gaf=gsub(raw_gaf_dir,config$gaf$uniq_dir,in_gaf,fixed = T)
    if(file.exists(out_gaf)){
        flog.warn(paste("The",out_gaf,"exists, So not removing duplicates from",in_gaf))
        flog.info(paste("Remove the ",out_gaf,"file to regenerate"))
    }else{
        flog.info(paste("The",out_gaf,"missing, So removing duplicates from",in_gaf))
        remove_dups(in_gaf,out_gaf,config)
    }
})
