library("futile.logger")

set_logger <- function(config){
    log_ext = ifelse(length(grep("\\.log$",config$logging$file_name))==1,"",".log")
    logfile=paste(config$logging$file_name,log_ext,sep="")
    a = flog.appender(appender.file(logfile),name="ROOT")
}