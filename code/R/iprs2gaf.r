library("data.table",quietly = T)
source("code/R/obo_tools.r")
source("code/R/gaf_tools.r")


iprs_cols = fread(config[["software"]][["iprs"]][["cols"]],header = F)$V1

iprs2gaf <- function(go_obo,iprs_out,taxon_txt,config){
    
    assigned_by=config[["data"]][["domain"]][["tool"]][["name"]]
    obo_data = check_obo_data(go_obo)
    #rbh_hits <- fread(rbh_file,header = F,sep = "\t")
    data = fread(iprs_out,header = F)
    colnames(data) = iprs_cols
    gaf_date = format(Sys.time(),"%Y%m%d")
    data[,with:=paste(analysis,sig_acc,sep=":")]
    gaf_data = data[,list(GO=unlist(strsplit(go,"\\|"))),by=list(acc,with)]
    colnames(gaf_data) = c("db_object_id","with","term_accession")
    
    gaf_data[,db:="maize-GAMER"]
    gaf_data[,db_object_symbol:=db_object_id]
    gaf_data[,evidence_code:="IEA"]
    gaf_data[,db_reference:="MG:0000"]    
    gaf_data[,date:=gaf_date]
    gaf_data[,assigned_by:=assigned_by]
    gaf_data[,taxon:=taxon_txt]
    gaf_data[,db_object_type:="protein"]
    gaf_data_filt <- gaf_data[term_accession %in% obo_data$id]
    gaf_data_filt[,aspect:=unlist(obo_data$aspect[gaf_data_filt$term_accession])]
    
    return(gaf_data_filt)
    
}