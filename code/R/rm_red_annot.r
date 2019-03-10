source("code/gaf_tools.r")
source("code/obo_tools.r")
source("code/gen_utils.r")
source("code/get_nr_dataset.r")

#in_args = commandArgs(trailingOnly = T)
datasets = fread("datasets.txt")
exist_dataset = fread("exist_datasets.txt")
datasets = rbind(datasets,exist_dataset)

obo_file="obo/go.obo"
proc_dts = datasets#[5:6]

tmp_out = apply(proc_dts,1,function(dataset){
    infile = paste("uniq_data/",dataset["file"],sep="")
    print(paste("Processing",dataset["dataset"]))
    remove_redundancy(infile,obo=obo_file)
})
