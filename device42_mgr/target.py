""" Device42 manager target class """

import pickle
import json

import device42_mgr.lib.utils as utils

class Target(object):
  """ Represent the target object """
  def extract_uris(self):
    """ Extract uris from target files """
    target = None

    try:
      target = utils.load_json_file(self.targetfile)
    except ValueError:
      with open(self.targetfile) as fdesc:
        target = pickle.load(fdesc)

    for target_key, target_values in target.iteritems():
      key = None

      if 'filter' not in target_values:
        key = target_key
      else:
        key = target_key + target_values['filter']

      self.uris[key] = {
        'categories': target_values['categories']
      }
    return self.uris

  def __str__(self):
    """ Handler when object is printed """
    return json.dumps(self.__dict__, indent=2)

  def __init__(self, targetfile):
    self.targetfile = targetfile
    self.uris = {}
    self.extract_uris()
