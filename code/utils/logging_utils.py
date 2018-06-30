import logging

def setlogging(config,file_base):
    logging_config = config["logging"]
    
    logger = logging.getLogger()
    logger.setLevel(logging_config['level'])
    log_file = config["input"]["gomap_dir"] + "/logs/" + config["input"]["basename"] + "-" + file_base + '.log'

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)

    handler = logging.FileHandler(log_file,mode="w+")
    formatter = logging.Formatter(logging_config["format"],datefmt=logging_config["formatTime"])

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info("Starting to run the pipline for " + config["input"]["basename"])