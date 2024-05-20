import logging

def setup_logger():
    logger = logging.getLogger('URL2ChatTests')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('test_logs.log')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
