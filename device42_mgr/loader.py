""" Device42 manager loader class """

import copy
import json

import device42_mgr.lib.utils as utils
from device42_mgr.cachier import Cachier
from device42_mgr.device42api import Api
from device42_mgr.device42api import Device42ApiException

class Device42MgrLoaderException(Exception):
  """ Device42 manager loader exception class """
  pass

class Loader(object):
  """ Load the targetfiles through the API or cache """
  def load_from_device42(self, uris):
    """ Contact device42 api and load the data """
    try:
      api = Api()
    except Device42ApiException as api_exception:
      err = 'ERROR: Failed to initialize device42 api'
      raise Device42MgrLoaderException(err + ':' + str(api_exception))

    new_uris = {}
    for uri in uris:
      print 'STATUS: Loading uri - %s' % uri
      try:
        response_json = api.get(uri)
      except Device42ApiException as api_exception:
        err = 'ERROR: Failed to get %s' % uri
        raise Device42MgrLoaderException(err + ':' + str(api_exception))
      new_uris[uri] = response_json

    # ring in the new, ring out the uncached
    for uri in new_uris:
      self.uri_ds_map[uri] = response_json
      self.uncached_uris.remove(uri)

  def extract_uris(self):
    """ Extract uris from target files """
    for target in [utils.load_json_file(x) for x in self.targetfiles]:
      for target_key, target_values in target.iteritems():
        if 'filter' not in target_values:
          self.uri_ds_map[target_key] = None
        else:
          self.uri_ds_map[target_key + target_values['filter']] = None

  def load(self):
    """ Main workhorse and wrapper method to load uris """
    self.extract_uris()

    if self.use_cache:
      self.cache = Cachier(self.cache_dir)
      self.cache.load(self.uri_ds_map.keys())
      for uri in set(self.uri_ds_map.keys()) - set(self.cache.uri_ds_map.keys()):
        self.uncached_uris.add(uri)
    else:
      self.uncached_uris = set(copy.deepcopy(self.uri_ds_map.keys()))

    if self.uncached_uris:
      self.load_from_device42(self.uncached_uris)

  def __str__(self):
    """ Handler when object is printed """
    print_ds = {}
    for attr in self.__dict__:
      if attr == 'uncached_uris':
        print_ds[attr] = list(self.__dict__[attr])
      elif attr == 'cache':
        print_ds[attr] = self.__dict__[attr].__dict__
      else:
        print_ds[attr] = self.__dict__[attr]
    return json.dumps(print_ds, indent=2)

  def __init__(self, targetfiles, cache_dir, use_cache=False):
    # renaming key because targetfile contains an array
    self.targetfiles = targetfiles
    self.cache_dir = cache_dir
    self.use_cache = use_cache
    self.uri_ds_map = {}
    self.uncached_uris = set()
    self.cache = None
