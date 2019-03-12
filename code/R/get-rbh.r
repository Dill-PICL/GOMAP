library("data.table",quietly = T)
library("parallel",quietly = T)
blast_cols = fread(config$software$blast$cols,header = F)$V1
source("code/R/gaf_tools.r")

if(F){
    main2other     <- "blast/maize-arabidopsis.bl.out"
    other2main     <- "blast/arabidopsis-maize.bl.out"
    evalue_th  <- 10e-10
    rbh_out    <- "blast/maize_v3_vs_tair10.rbh.txt"
    blast_cols = fread("misc/blast_cols.txt",header = F)$V1
    get_rbh(main2other,other2main,evalue_th,"tmp.txt",blast_cols)

}

get_uniprot_rbh <- function(main2other,other2main, config){
    spp="uniprot"
    evalue_th= as.numeric(config$software$blast$evalue)
    main2other_blast <- fread(main2other,header = F,sep = "\t",stringsAsFactors = F)
    colnames(main2other_blast) <- blast_cols
    #db2mz_blast <- data.table(db2mz_blast)
    setkeyv(main2other_blast,c("qseqid","sseqid"))
    main2other_blast <- main2other_blast[evalue <= evalue_th]
    
    other2main_blast <- fread(other2main,header = F,sep = "\t",stringsAsFactors = F)
    colnames(other2main_blast) <- blast_cols
    #other2main_blast <- data.table(other2main_blast)
    setkeyv(other2main_blast,c("qseqid","sseqid"))
    other2main_blast <- other2main_blast[evalue < evalue_th]
    
    gaf_file = paste(config[["data"]]$`seq-sim`[[spp]]$basedir,"/",config[["data"]]$`seq-sim`[[spp]]$basename,".gaf",sep="")
    uniprot_gaf = read_gaf(gaf_file)
    uniprot_gaf[db_object_id == main2other_blast$sseqid[1]]

    tmp_taxon = lapply(strsplit(uniprot_gaf$taxon,"\\:"),function(x){
        x[[2]]
    })
    uniprot_gaf[,taxon:=unlist(tmp_taxon)]
    tax_ids = setdiff(config$data$`seq-sim`$uniprot$cleaning$sel_tax,config$input$taxon)
    uniprot_gaf = uniprot_gaf[taxon %in% tax_ids]

    rbh_tmp <- lapply(tax_ids,function(taxid){

        tmp_uniprot_ids = uniprot_gaf[taxon==taxid]$db_object_id
        main2other_tmp = main2other_blast[sseqid %in% tmp_uniprot_ids]
        print(sum(main2other_blast$sseqid %in% tmp_uniprot_ids))
        which_max_score <- main2other_tmp[,list(max_score=.I[which.max(score)]),by=qseqid]
        main2other_blast_filt <- main2other_tmp[which_max_score$max_score]
        #db2mz_blast_filt
        main2other_hits <- paste(main2other_blast_filt$qseqid,main2other_blast_filt$sseqid,sep = "-")
        other2main_tmp = other2main_blast[qseqid %in% tmp_uniprot_ids]

        which_min_eval <- other2main_tmp[,list(min_ind=.I[which.min(evalue)]),by=qseqid]
        other2main_blast_filt <- other2main_tmp[which_min_eval$min_ind]
        #other2main_blast_filt
        other2main_hits <- paste(other2main_blast_filt$sseqid,other2main_blast_filt$qseqid,sep="-")

        #head(other2main_hits)

        rbh <- main2other_blast_filt[main2other_hits %in% other2main_hits]
        rbh
    })

    rbh_data = do.call(rbind,rbh_tmp)[,1:2,with=F]

    rbh_out = gsub("bl.out","rbh.out",main2other)

    write.table(rbh_data,file = rbh_out,sep = "\t",quote = F,row.names = F,col.names = F)
    return(rbh_data)
}

get_rbh <- function(main2other,other2main, evalue_th){
    main2other_blast <- fread(main2other,header = F,sep = "\t",stringsAsFactors = F)
    colnames(main2other_blast) <- blast_cols
    setkeyv(main2other_blast,c("qseqid","sseqid"))
    main2other_blast <- main2other_blast[evalue <= evalue_th]
    which_max_score <- main2other_blast[,list(max_ind=.I[which.max(score)]),by=qseqid]
    main2other_blast_filt <- main2other_blast[which_max_score$max_ind]
    main2other_hits <- paste(main2other_blast_filt$qseqid,main2other_blast_filt$sseqid,sep = "-")

    other2main_blast <- fread(other2main,header = F,sep = "\t",stringsAsFactors = F)
    colnames(other2main_blast) <- blast_cols
    setkeyv(other2main_blast,c("qseqid","sseqid"))
    other2main_blast <- other2main_blast[evalue < evalue_th]
    which_max_score <- other2main_blast[,list(max_ind=.I[which.max(score)]),by=qseqid]
    other2main_blast_filt <- other2main_blast[which_max_score$max_ind]
    other2main_hits <- paste(other2main_blast_filt$sseqid,other2main_blast_filt$qseqid,sep="-")
    

    rbh <- main2other_blast_filt[main2other_hits %in% other2main_hits]
    rbh_data = rbh[,1:2,with=F]

    rbh_out = gsub("bl.out","rbh.out",main2other)
    write.table(rbh[,1:2,with=F],file = rbh_out,sep = "\t",quote = F,row.names = F,col.names = F)
    return(rbh_data)
}

assign_gaf_go <- function(rbh_data,spp,gaf_file,ommited_ev_codes,taxon_txt){

    rbh_hits = data.table(rbh_data)
    colnames(rbh_hits) <- c("main","other")
    gaf_date = format(Sys.time(),"%m%d%Y")


    db_gaf <- read_gaf(gaf_file)
    db_gaf_hc <- db_gaf[!evidence_code %in% ommited_ev_codes]
    setkey(db_gaf_hc,db_object_id)


    tmp_out <- apply(rbh_hits,1,function(x){
        tmp_dt <- db_gaf_hc[x[2],nomatch=0]
        if(dim(tmp_dt)[1]>0){
            tmp_dt[,db_object_id:=x[1]]
            tmp_dt[,db_object_symbol:=x[1]]
            tmp_dt[,with:=paste("RBH",x[2],sep=":")]
            return(tmp_dt)
        }
    })

    ass_by = config[["data"]]$`seq-sim`[[spp]][["metadata"]]$species
    out_gaf <- do.call(rbind,tmp_out)
    out_gaf[,assigned_by:=ass_by]
    out_gaf[,taxon:=taxon_txt]
    out_gaf[,date:=gaf_date]
    out_gaf[,db_object_name:=""]
    out_gaf[,db_object_synonym:=""]     
    
    out_dir <- dirname(out_gaf_file)
    ifelse(!dir.exists(out_dir),dir.create(out_dir,recursive = T),paste(out_dir,"already exists so not creating one"))
    return(out_gaf)
}

get_blast_out <- function(config1,config2){
    # print(config1)
    base_name = paste(config1[["gomap_dir"]],config2[["tmpdir"]],sep="/")
    # out1=paste(base_name, "/blast/", config1[["basename"]], "-", config2[["basename"]], ".bl.out", sep = "")
    out1=dir(base_name,pattern = paste("^",config1["basename"],sep=""),full.names = T)[1]
    # out2=paste(base_name, "/blast/", config2[["basename"]], "-", config1[["basename"]], ".bl.out", sep = "")
    out2=dir(base_name,pattern = paste(config1["basename"],".bl.out",sep=""),full.names = T)[1]
    return(list(main2other=out1,other2main=out2))
}

get_gaf_out <- function(config1,config2){
    base_name = dirname(dirname(config1[["fasta"]]))
    #
    out_file=paste("gaf/raw/",
                   config1[["species"]],
                   ifelse(config1[["inbred"]]!="",paste(".",config1[["inbred"]],sep = ""),""),
                   ifelse(config1[["version"]]!="",paste(".",config1[["version"]],sep = ""),""),
                   ".",config2[["species"]],
                   ".gaf",
                   sep = "")
    #ifelse("."+config1["inbred"] if "inbred" in config1 else "") +\
    # ("."+config1["version"] if "version" in config1 else "") +\
    # "-"+config2["species"]+\
    # ("."+config2["inbred"] if "inbred" in config2 else "") +\
    # ("."+config2["version"] if "version" in config2 else "") +\
    # ".bl.out")
    # logging.info(out_file)
    return(out_file)

}

