library("jsonlite",quietly = T)

#Reading config file name
args <- commandArgs(T)
config_file <- args[1]

#Reading config file and creating config object
config = fromJSON(config_file)

source("code/R/iprs2gaf.r")
source("code/R/logger.r")

#set the logfile and initiate the logger
set_logger(config)

raw_dir=paste(config$gaf$raw_dir,"/",sep="")

#setting the correct working directory
#if(dir.exists(config$input$work_dir)){
#    setwd(config$input$work_dir)
#}

go_obo = config$go$obo
iprs_out = paste("temp/",paste(config$input$species,config$input$inbred,config$input$version,"tsv",sep="."),sep = "")
out_gaf = paste(raw_dir,gsub(".tsv","",basename(iprs_out)),".",config$software$domain$software,".gaf",sep = "")

if(file.exists(out_gaf)){
    flog.warn(paste("The",out_gaf,"exists, So not regenerating InterProScan dataset"))
    flog.warn(paste("Remove the ",out_gaf,"file to regenerate"))
}else{
    flog.info(paste("The",out_gaf,"missing, So generating the dataset"))
    iprs2gaf(go_obo,iprs_out,out_gaf)
}
