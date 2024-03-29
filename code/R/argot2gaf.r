argot2gaf <- function(in_files,config){
    print("Reading the input file")
    gaf_date = format(Sys.time(),"%Y%m%d")
    tmp_out = lapply(in_files,function(infile){
        tmp_data = fread(infile,sep = "\t",header = T)
        colnames(tmp_data) = gsub("#","",colnames(tmp_data))
        tmp_data
    })
    argot2_data = do.call(rbind,tmp_out)
    argot2_data = argot2_data[!grep("#",`SeqID`)]
    taxon_txt=paste("taxon:",config$input$taxon,sep="")
    
    gaf_cols=fread(config$data$go$gaf_cols,header = F)$V1
    gaf_cols
    
    print("Converting to GAF 2.0")
    gaf_data = argot2_data[,.(`SeqID`,`GO ID`,`Int. Confidence`)]
    colnames(gaf_data) = c("db_object_id","term_accession","with")
    
    
    gaf_data$with = as.numeric(gaf_data$with)
    min_score=min(gaf_data$with)
    max_score=max(gaf_data$with)
    gaf_data$with = (gaf_data$with - min_score)/(max_score - min_score)
    
    
    obo_data = check_obo_data(config$data$go$obo)
    aspect = unlist(obo_data$aspect[gaf_data$term_accession])
    gaf_data[,aspect:=aspect]
    
    #gaf_data[,db_object_id:=tmp]
    
    gaf_data[,db_object_symbol:=db_object_id]
    gaf_data[,taxon:=taxon_txt]
    gaf_data[,date:=gaf_date]
    gaf_data[,assigned_by:="Argot2.5"]
    
    return(gaf_data)
    # print("Writing the outfile")
    # write_gaf(gaf_data,out_file)
}