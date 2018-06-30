library("futile.logger",quietly = T)

set_logger <- function(config){
    logfile = paste(config[["input"]][["gomap_dir"]], "/logs/", config[["input"]][["basename"]], '-R.log',sep = "")
    a = flog.appender(appender.file(logfile),name="ROOT")
}