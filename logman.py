import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import messages

#Global Variables
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FOLDER = "Logs"
LOG_FILE = "msssdo.log"
LOGGER_NAME = "loggy"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_file_handler():
   
   if Path(LOG_FOLDER).is_dir:
      Path(LOG_FOLDER).mkdir(exist_ok=True)
      
   logfile = LOG_FOLDER + os.path.sep + LOG_FILE

   file_handler = TimedRotatingFileHandler(logfile, when='midnight', backupCount=2)
   file_handler.setFormatter(FORMATTER)
   file_handler.createLock()
   file_handler.acquire()
   return file_handler

#Call this method to get back a logger instance
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.INFO)
   #Only for debugging purposes, not deploying
   #logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   logger.propagate = False
   return logger

def exitlogman(logger):
   
   for handler in logger.handlers:
      if isinstance(handler,logging.FileHandler):
         handler.release()
    
   logging.shutdown()
   
#Initializing Logger
logger = get_logger(LOGGER_NAME)
logger.info(messages.LOGGER_INITIALIZED)
