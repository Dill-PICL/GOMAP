library("futile.logger")

set_logger <- function(config){
    logfile = paste(config[["input"]][["workdir"]], "/", config[["input"]][["basename"]], '.log',sep = "")
    print(logfile)
    a = flog.appender(appender.file(logfile),name="ROOT")
}