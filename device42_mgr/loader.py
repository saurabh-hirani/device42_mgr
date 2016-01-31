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
      self.uri_ds_map[uri] = new_uris[uri]
      self.uncached_uris.remove(uri)

    return self.uri_ds_map

  def extract_uris(self):
    """ Extract uris from target files """
    for targetfile in self.targetfiles:
      target = None
      try:
        target = utils.load_json_file(targetfile)
      except ValueError :
        target = utils.load_picked_file(targetfile)
      for target_key, target_values in target.iteritems():
        if 'filter' not in target_values:
          self.uri_ds_map[target_key] = {}
        else:
          self.uri_ds_map[target_key + target_values['filter']] = {}
    return self.uri_ds_map

  def load(self):
    """ Main workhorse and wrapper method to load uris """
    self.extract_uris()

    if self.use_cache and not self.refresh_cache:
      cached_uri_ds_map = self.cache_obj.load(self.uri_ds_map.keys())

      for uri in set(self.uri_ds_map.keys()) - set(cached_uri_ds_map.keys()):
        self.uncached_uris.add(uri)

      for uri in cached_uri_ds_map:
        self.uri_ds_map[uri] = cached_uri_ds_map[uri]
    else:
      self.uncached_uris = set(copy.deepcopy(self.uri_ds_map.keys()))

    if self.uncached_uris:
      self.load_from_device42(self.uncached_uris)

    if self.refresh_cache:
      self.cache_obj.refresh(self.uri_ds_map)

    return self.uri_ds_map

  def __str__(self):
    """ Handler when object is printed """
    print_ds = {}
    for attr in self.__dict__:
      if attr == 'uncached_uris':
        print_ds[attr] = list(self.__dict__[attr])
      elif attr == 'cache_obj':
        print_ds[attr] = self.__dict__[attr].__dict__
      else:
        print_ds[attr] = self.__dict__[attr]
    return json.dumps(print_ds, indent=2)

  def __init__(self, targetfiles, cache_obj, use_cache=False,
               refresh_cache=False):
    # renaming key because targetfile contains an array
    self.targetfiles = targetfiles
    self.cache_obj = cache_obj
    self.use_cache = use_cache
    self.refresh_cache = refresh_cache
    self.uri_ds_map = {}
    self.uncached_uris = set()
