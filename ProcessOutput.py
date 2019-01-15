import configparser
from copy import deepcopy



def _processSegment(segment):
  segmentCopy = {}
  
  for entry in segment:
    segmentCopy[entry] = eval(segment[entry])
  
  return segmentCopy


def processOutput(fileName):
  
  config = configparser.ConfigParser()
  config.read(fileName)
  
  processedOutput = {}
  
  for entry in config:
    if entry != 'DEFAULT':
      processedOutput[eval(entry)] = _processSegment(config[entry])
  
  return processedOutput