library("data.table",quietly = T)
tool="Argot"
#cafa_gaf <- argot2_cafa

filter_mixed_gaf <- function(cafa_gaf,raw_gaf,tool,config){
    cafa_data = read_gaf(cafa_gaf)
    score_ths = config$`mixed-meth`[[tool]]$score_th
    
    flog.info(paste("Filtering annotations with follwing score thresholds for ",tool))
    flog.info(paste(score_ths,names(score_ths)))
    
    cafa_data[,with:=as.numeric(with)]
    
    tmp_out <- lapply(names(score_ths),function(x){
        score_th = as.numeric(score_ths[[x]])
        cafa_data[aspect == x & with>score_th]
    })
    
    out_gaf = do.call(rbind,tmp_out)
    out_gaf[,with:=as.character(with)]
    out_gaf[,with:=""]
    write_gaf(out_gaf,raw_gaf)
}