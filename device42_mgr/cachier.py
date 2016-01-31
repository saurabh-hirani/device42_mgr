""" Device42 manager caching class """

import os
import glob
import device42_mgr.lib.utils as utils

class Cachier(object):
  """ Read/update the uri cache """

  def load(self, uris=None):
    """ Load cached uri data from previous runs """
    if uris is None:
      uris = []

    # find the cached files
    cache_files = glob.glob(os.path.join(self.cache_dir, '*.json'))
    if not cache_files:
      return {}

    # load the cached files
    data = {}
    for cache_file in cache_files:
      data.update(utils.load_json_file(cache_file))

    # extract out the elements whose keys match uris_to_load
    if uris:
      valid_uris = set(data.keys()) & set(uris)
      if not valid_uris:
        return {}

      # ignore keys other than valid_cached_data keys
      for invalid_uri in set(data.keys()) - valid_uris:
        del data[invalid_uri]

    self.uri_ds_map = data

  def __init__(self, cache_dir):
    self.cache_dir = cache_dir
    self.uri_ds_map = {}
