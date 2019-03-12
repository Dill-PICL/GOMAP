library("yaml",quietly = T)

#Reading config file name
args <- commandArgs(T)
config_file <- args[1]

#Reading config file and creating config object
config = read_yaml(config_file)

source("code/R/iprs2gaf.r")
source("code/R/logger.r")

#set the logfile and initiate the logger
set_logger(config)

go_obo = config[["data"]][["go"]][["obo"]]
workdir=paste(config[["input"]][["gomap_dir"]],"/",sep="")
raw_dir=paste(workdir,config$data$gaf$raw_dir,"/",sep="")
taxon_txt=paste("taxon:",config$input$taxon,sep="")
setDTthreads(as.numeric(config[["input"]][["cpus"]]))

iprs_out=paste(workdir,config[["data"]][["domain"]][["tmpdir"]], "/", config[["input"]][["basename"]],".go.tsv",sep="")

out_gaf = paste(raw_dir,gsub("go.tsv","",basename(iprs_out)),config$data$domain$tool$name,".gaf",sep = "")
if(file.exists(out_gaf)){
    flog.warn(paste("The",out_gaf,"exists, So not regenerating InterProScan dataset"))
    flog.warn(paste("Remove the ",out_gaf,"file to regenerate"))
}else{
    flog.info(paste("The",out_gaf,"missing, So generating the dataset"))
    iprs_data = iprs2gaf(go_obo,iprs_out,taxon_txt,config)
    write_gaf(config,iprs_data,out_gaf)
}
