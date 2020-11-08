pannzer2gaf <- function(in_files,config){
    print("Reading the input file")
    in_files=pannzer_results
    #out_file="PANNZER/gaf/pannzer-0.0.gaf"
    gaf_date = format(Sys.time(),"%Y%m%d")
    taxon_txt=paste("taxon:",config$input$taxon,sep="")
    
    
    tmp_out = lapply(in_files,function(infile){
        tmp_data = fread(infile,sep = "\t")
        colnames(tmp_data) = gsub("#","",colnames(tmp_data))
        tmp_data
    })
    pannzer_data = do.call(rbind,tmp_out)
    #argot2_data = argot2_data[!grep("#",`SeqID`)]
    pannzer_data
    
    
    gaf_cols=fread(config$data$go$gaf_cols,header = F)$V1
    print("Converting to GAF 2.0")
    gaf_data = pannzer_data[,.(QueryId,GO_class,Score)]
    colnames(gaf_data) = c("db_object_id","term_accession","with")
    
    min_score=min(gaf_data$with)
    max_score=max(gaf_data$with)
    gaf_data$with = (gaf_data$with - min_score)/(max_score - min_score)
    
    obo_data = check_obo_data(config$data$go$obo)
    tmp_aspect=lapply(gaf_data$term_accession,function(x){
        out = obo_data$aspect[[x]]
        if(is.null(out)){
            print(x)
            "N"
        }else{
            out    
        }
    })
    gaf_data[,aspect:=unlist(tmp_aspect)]
    
    
    gaf_data[,db_object_symbol:=db_object_id]
    gaf_data[,taxon:=taxon_txt]
    gaf_data[,date:=gaf_date]
    gaf_data[,assigned_by:="PANNZER"]
    
    return(gaf_data)
}