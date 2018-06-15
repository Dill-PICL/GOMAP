source("code/gaf_tools.r")

remove_dups <- function(in_gaf,out_gaf,config){
    data = read_gaf(in_gaf)
    gaf_cols = fread(config$go$gaf_cols,sep = "\t",header = F)$V1
    uniq_data = data[,.SD[1],by=c("db_object_id","term_accession")]
    setcolorder(uniq_data,gaf_cols)
    dir.create(dirname(out_gaf),showWarnings = F)
    write_gaf(uniq_data,out_gaf)
}