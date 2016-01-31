""" Device42 API access class """

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, ConnectTimeout

import device42_mgr.lib.utils as utils

class Device42ApiException(Exception):
  pass

class Api(object):
  """ Device42 API class """

  def get(self, uri):
    """ Perform a GET request """
    url = '%s://%s:%s%s%s' % (self.transport, self.host, self.port, 
                              self.api_uri, uri)
    try:
      response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password),
                              timeout=self.request_timeout, verify=self.verify_https)
    except (ConnectionError, ConnectTimeout) as request_exceptions:
      raise Device42ApiException(str(request_exceptions))

    if response.status_code != 200:
      raise Device42ApiException('Request - %s - HTTP status - %d' % \
                                 (url, response.status_code))

    if response.headers['content-type'] != 'application/json':
      raise Device42ApiException('Request - %s - expecting json - got %s' % \
                                 (url, response.headers['content-type']))
    return response.json()

  def __str__(self):
    """ Handler when object is printed """
    return json.dumps(self.__dict__, indent=2)

  def __init__(self, **kwargs):
    """ Initialize connection params """

    # initialize attributes
    self.host = self.port = self.username = self.password = None
    self.request_timeout = 60
    self.transport = 'http'
    self.api_uri = '/api/1.0/'
    self.verify_https = False

    # override default values with user-supplied values or from env vars
    conn_params = {}
    for attr in self.__dict__:
      conn_params[attr] = {'supplied': attr in kwargs and kwargs[attr] or None,
                           'env': 'DEVICE42_API_' + attr.upper()}

    # skip the optional params from verification
    del conn_params['transport']
    del conn_params['verify_https']
    del conn_params['api_uri']

    for attr in conn_params:
      supplied_val = conn_params[attr]['supplied']
      if supplied_val is not None:
        setattr(self, attr, supplied_val)
        continue

      env_key = conn_params[attr]['env']
      if env_key not in os.environ:
        err = 'No value provided for %s and env var %s not set' % \
              (attr, env_key)
        raise Device42ApiException(err)

      env_val = os.environ[env_key]
      setattr(self, attr, env_val)

    # massage captured data
    self.port = int(self.port)
    self.request_timeout = int(self.request_timeout)
    if self.verify_https == 'FALSE' or self.verify_https is None:
      self.verify_https = False
    if self.port == 443:
      self.transport = 'https'
