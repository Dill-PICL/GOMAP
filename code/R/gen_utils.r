source("code/R/logger.r")

print_dt_progress = function(unit_size,idxs,unit_perc=1,tool_name="data"){
    if(sum(idxs %% unit_size == 0)>0){
        perc = idxs[idxs %% unit_size == 0] / unit_size * unit_perc
        if(perc[1] %% 100){
            flog.info(paste("Processing",tool_name,sprintf("%05.1f",perc),"%"))
        }
        else{
            flog.info(paste("Processing",tool_name,sprintf("%05.1f",perc,"%")))
        }
    }
}
