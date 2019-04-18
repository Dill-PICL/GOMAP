library("data.table")
fanngo2gaf <- function(in_file,config){
    print("Reading the input file")
    #in_file="FANNGO_linux_x64/scores.txt"
    #out_gaf="FANNGO_linux_x64/gaf/fanngo-0.0.gaf"
    gaf_date = format(Sys.time(),"%m%d%Y")
    taxon_txt=paste("taxon:",config$input$taxon,sep="")
    
    fanngo_data = fread(in_file)
    
    fanngo_melt = melt(fanngo_data,id.vars = "gene_id")
    colnames(fanngo_melt) = c("db_object_id","term_accession","with")
        
    gaf_cols=fread(config$data$go$gaf_cols,header = F)$V1
    gaf_cols
    
    print("Converting to GAF 2.0")
    gaf_data = data.table(fanngo_melt)
    rm(fanngo_melt,fanngo_data)
    gaf_data$term_accession = gsub("_",":",gaf_data$term_accession,fixed = T)
    
    
    obo_data = check_obo_data(config$data$go$obo)
    
    #tmp_aspect = get_aspect(obo_data,gaf_data$term_accession)
    tmp_aspect=obo_data$aspect[gaf_data$term_accession]
    tmp_aspect[is.null(tmp_aspect)] = "N"
    # tmp_aspect=lapply(tmp_aspect,function(x){
    #     if(is.null(x)){
    #         "N"
    #     }else{
    #         x
    #     }
    # })
    gaf_data[,aspect:=unlist(tmp_aspect)]
    
    min_score=min(gaf_data$with)
    max_score=max(gaf_data$with)
    gaf_data$with = (gaf_data$with - min_score)/(max_score - min_score)
    # quit()
    
    gaf_cols[!gaf_cols %in% colnames(gaf_data)]
    #gaf_data[,db_object_id:=tmp]
    gaf_data[,db_object_symbol:=db_object_id]
    gaf_data[,taxon:=taxon_txt]
    gaf_data[,date:=gaf_date]
    gaf_data[,assigned_by:="FANN-GO"]
    
    return(gaf_data)
}