""" Device42 manager caching class """

import os
import json
import pickle
import glob
import device42_mgr.lib.utils as utils

class Cachier(object):
  """ Read/update the uri cache """
  def _load_from_cache(self, only_pickle=False):
    """ Method to load from cache - abstract how data is cached """
    data = {}

    if not only_pickle:
      json_files = glob.glob(os.path.join(self.cache_dir, '*.json'))
      for json_file in json_files:
        data.update(utils.load_json_file(json_file))

    pickled_files = glob.glob(os.path.join(self.cache_dir, '*.pickle'))
    for pickled_file in pickled_files:
      with open(pickled_file) as fdesc:
        data.update(pickle.load(fdesc))

    return data

  def _dump_to_cache(self, data):
    """ Method to dump to cache - abstract how data is cached """
    curr_ds = {}
    if os.path.exists(self.cache_filepath):
      curr_ds.update(self._load_from_cache(only_pickle=True))

    curr_ds.update(data)

    with open(self.cache_filepath, 'wb') as fdesc:
      pickle.dump(curr_ds, fdesc)

  def refresh(self, uris_ds_map):
    """ Refresh the cache """
    self._dump_to_cache(uris_ds_map)

  def load(self, uris=None):
    """ Load cached uri data from previous runs """
    if uris is None:
      uris = []

    data = self._load_from_cache()

    if not data:
      return {}

    if uris:
      valid_uris = set(data.keys()) & set(uris)
      if not valid_uris:
        return {}

      for invalid_uri in set(data.keys()) - valid_uris:
        del data[invalid_uri]

    return data

  def __str__(self):
    """ Handler when object is printed """
    return json.dumps(self.__dict__, indent=2)

  def __init__(self, cache_dir, cache_filename):
    self.cache_dir = cache_dir
    self.cache_filename = cache_filename
    self.cache_filepath = os.path.join(cache_dir, cache_filename)
    self.cache_exists = True
    if not os.path.exists(self.cache_filepath):
      self.cache_exists = False
