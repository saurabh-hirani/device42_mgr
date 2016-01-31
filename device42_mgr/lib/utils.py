""" device42_mgr helpers """

import os
import itertools
import json
import yaml

class InvalidValueException(Exception):
  pass

def flatten_list(target_list):
  """ Flatten a list """
  return list(itertools.chain(*target_list))

def load_json_file(filepath):
  """ Load json file wrapper to handle file closure + return utf-8 """
  loaded_json = None
  with open(filepath) as fdesc:
    loaded_json = yaml.safe_load(json.dumps(json.loads(fdesc.read())))
  return loaded_json

def validate_file(filepath):
  """ Validate file """
  if not os.path.exists(filepath):
    raise InvalidValueException('%s: file does not exist' % filepath)
  if not os.path.isfile(filepath):
    raise InvalidValueException('%s: not a file' % filepath)
  return True

def validate_dir(dirpath):
  """ Validate directory """
  if not os.path.exists(dirpath):
    raise InvalidValueException('%s: directory does not exist' % dirpath)
  if not os.path.isdir(dirpath):
    raise InvalidValueException('%s: directory does not exist' % dirpath)
  return True

def validate_dir_files(dirpath, filenames=None):
  """ Validate dir path and file paths in it """
  validate_dir(dirpath)

  if filenames is None:
    return True

  for filename in filenames:
    filepath = os.path.join(dirpath, filename)
    validate_file(filepath)

  return True
