import logging

def setlogging(config):
    logging_config = config["logging"]
    
    logger = logging.getLogger()
    logger.setLevel(logging_config['level'])
    log_file = config["input"]["gomap_dir"] + "/log/" + config["input"]["basename"] + '.log'

    handler = logging.FileHandler(log_file,mode="a+")
    formatter = logging.Formatter(logging_config["format"],datefmt=logging_config["formatTime"])

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info("Starting to run the pipline for " + config["input"]["basename"])