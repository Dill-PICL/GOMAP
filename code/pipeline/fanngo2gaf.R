
library("yaml",quietly = T)


if(F){
    config_file = "../test3/GOMAP-ZmAGPv4/ZmAGPv4.all.yml"
}


source("code/R/gaf_tools.r")
source("code/R/obo_tools.r")
source("code/R/fanngo2gaf.r")
source("code/R/filter_mixed.r")
source("code/R/logger.r")

#Reading config file name
args <- commandArgs(T)
config_file <- args[1]

#Reading config file and creating config object
config = read_yaml(config_file)

#set the logfile and initiate the logger
set_logger(config)

#setting the correct working directory
workdir=paste(config$input$gomap_dir,"/",sep="")
gaf_dir = paste(workdir,config$data$gaf[["mixed_method_dir"]],"/",sep="")
mm_gaf_dir=paste(workdir,config$data$gaf$mixed_method_dir,"/",sep="")
raw_gaf_dir=paste(workdir,config$data$gaf$raw_dir,"/",sep="")
basename <- config$input$basename
setDTthreads(as.numeric(config[["input"]][["cpus"]]))

#processing FANN-GO results
# Commented out because matlab is cannot be supplied in an image
fanngo_res= paste(workdir,config$data$`mixed-method`$fanngo$out_dir,"/",basename,".score.txt",sep="")
fanngo_gaf = paste(gaf_dir,paste(basename,"fanngo","gaf",sep="."),sep = "")
print(fanngo_gaf)
if(!file.exists(fanngo_gaf) & file.exists(fanngo_res)){
    fanngo_gaf_data <- fanngo2gaf(fanngo_res,config)
    print("Writing FANNGO gaf ")
    write_gaf(config = config,out_gaf = fanngo_gaf_data,outfile = fanngo_gaf)
}else{
    flog.warn(paste("The",fanngo_gaf,"exists. So not Running converting FANN-GO results"))
    flog.info(paste("Remove the file to reconvert"))
}

#processing FANN-GO results
#fanngo_cafa = paste(mm_gaf_dir,paste(config$input$basename,"fanngo","gaf",sep="."),sep = "")
fanngo_raw = paste(raw_gaf_dir,paste(config$input$basename,"fanngo","gaf",sep="."),sep = "")
if(!file.exists(fanngo_raw) & file.exists(fanngo_gaf)){
    fanngo_filt = filter_mixed_gaf(fanngo_gaf,"fanngo",config)
    write_gaf(config = config,out_gaf = fanngo_filt,outfile = fanngo_raw)
    
}else{
    flog.warn(paste("The",fanngo_raw,"exists. So not filtering FANN-GO results"))
    flog.info(paste("Remove the file to reconvert"))
}
