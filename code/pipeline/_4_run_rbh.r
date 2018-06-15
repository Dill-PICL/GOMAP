#Loading Necessary libraries and packages
library("jsonlite",quietly = T)

source("code/get-rbh.r")
source("code/logger.r")

args <- commandArgs(T)

config_file <- args[1]

#Reading config file and creating config object
config = fromJSON(config_file)
if(F){
    config = fromJSON("maize.W22.AGPv2.json")
}

#set the logfile and initiate the logger
set_logger(config)

#setting the correct working directory
#if(dir.exists(config$input$work_dir)){
#    setwd(config$input$work_dir)
#}

ommited_ev_codes = config$go$evidence_codes$omitted

#processing arabidopsis results
spp = "TAIR"
flog.info(paste("Processing", spp))
eval_th = as.numeric(config$blast$evalue)
bl_out = get_blast_out(config[["input"]],config[["seq-sim"]][[spp]])
main2other = bl_out$main2other
other2main = bl_out$other2main
gaf_file = config$`seq-sim`[[spp]]$gaf_file
out_gaf_file=paste(config$gaf$raw_dir,"/",config$input$basename,".",config$`seq-sim`$TAIR$species,".gaf",sep = "")
#out_gaf_file=get_gaf_out(config[["input"]],config[["seq-sim"]][[spp]])
rbh_out = gsub("bl.out","rbh.out",main2other)
if(!file.exists(rbh_out)){
    rbh_hits = get_rbh(main2other,other2main,eval_th)
}else{
    flog.info(paste(rbh_out, "already exists. Delete to regenerate"))
    rbh_hits = fread(rbh_out,header = F)
    colnames(rbh_hits) <- c("qseqid","sseqid")
}
assign_gaf_go(rbh_hits,spp,gaf_file,ommited_ev_codes,out_gaf_file)

#Processing UniProt plants results
spp = "UniProt"
flog.info(paste("Processing", spp))
bl_out = get_blast_out(config[["input"]],config[["seq-sim"]][[spp]])
main2other = bl_out$main2other
other2main = bl_out$other2main
gaf_file = config$`seq-sim`[[spp]]$gaf_file
out_gaf_file=get_gaf_out(config[["input"]],config[["seq-sim"]][[spp]])
rbh_out = gsub("bl.out","rbh.out",main2other)
if(!file.exists(rbh_out)){
    rbh_hits = get_rbh(main2other,other2main,eval_th)
}else{
        flog.info(paste(rbh_out, "already exists. Delete to regenerate"))
        rbh_hits = fread(rbh_out,header = F)
        colnames(rbh_hits) <- c("qseqid","sseqid")
}
assign_gaf_go(rbh_hits,spp,gaf_file,ommited_ev_codes,out_gaf_file)
