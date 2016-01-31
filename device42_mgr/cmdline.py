#!/usr/bin/env python

""" Manage device42 bulk operations """

import os
import itertools
import json
import glob
import yaml
import copy

import click

def flatten_list(target_list):
  """ Flatten a list """
  return list(itertools.chain(*target_list))

def load_json_file(filepath):
  """ Load json file wrapper to handle file closure + return utf-8 """
  loaded_json = None
  with open(filepath) as fdesc:
    loaded_json = yaml.safe_load(json.dumps(json.loads(fdesc.read())))
  return loaded_json

def _validate_file(filepath):
  """ Validate file """
  if not os.path.exists(filepath):
    raise ValueError('%s: file does not exist' % filepath)
  if not os.path.isfile(filepath):
    raise ValueError('%s: not a file' % filepath)
  return True

def _validate_dir(dirpath):
  """ Validate directory """
  if not os.path.exists(dirpath):
    raise ValueError('%s: directory does not exist' % dirpath)
  if not os.path.isdir(dirpath):
    raise ValueError('%s: directory does not exist' % dirpath)
  return True

def _find_default_actionfile(ctx, action):
  """ Find the default action file depending on the action """
  actionfile = os.path.join(ctx.obj['config']['actions']['dir'], '%s.json' % action)
  _validate_file(actionfile)
  return actionfile

def _find_actionfile(action, ctx, actionfile):
  """ Return default action file if empty - else validate input """
  if actionfile is None:
    return _find_default_actionfile(ctx, action)
  _validate_file(actionfile)
  return actionfile

def find_read_actionfile(ctx, param, value):
  """ Wrapper for find_$action_actionfile """
  return _find_actionfile('read', ctx, value)

def find_update_actionfile(ctx, param, value):
  """ Wrapper for find_$action_actionfile """
  return _find_actionfile('update', ctx, value)

def find_targetfiles(ctx, param, value):
  """ Validate and find targetfiles """
  # if not supplied, load from config
  filenames = value
  from_config = False
  if not filenames:
    from_config = True
    filenames = ctx.obj['config']['targets']['files']

  targets_dir = ctx.obj['config']['targets']['dir']
  targetfiles = [os.path.join(targets_dir, x) for x in filenames]

  # supplied by the user  - validate them
  if not from_config:
    for filepath in targetfiles:
      if not os.path.exists(filepath):
        raise ValueError('%s: file does not exist' % filepath)
      if not os.path.isfile(filepath):
        raise ValueError('%s: not a file' % filepath)

  return targetfiles

def _validate_dir_files(dirpath, filenames=None):
  """ Validate dir path and file paths in it """
  _validate_dir(dirpath)

  if filenames is None:
    return True

  for filename in filenames:
    filepath = os.path.join(dirpath, filename)
    _validate_file(filepath)

  return True

def _validate_targets_config(config):
  """ Validate targets section in --configfile """
  return _validate_dir_files(config['dir'], config['files'])

def _validate_actions_config(config):
  """ Validate actions section in --configfile """
  return _validate_dir_files(config['dir'], config['files'])

def _validate_cache_config(config):
  """ Validate cache section in --configfile """
  # don't validate the cache config files - they will not be created till the
  # first run
  return _validate_dir_files(config['dir'])

def validate_config(config):
  """ Validate config loaded from --configfile """
  _validate_targets_config(config['targets'])
  _validate_actions_config(config['actions'])
  _validate_cache_config(config['cache'])
  return True

def load_cached_targets(cache_config, valid_targets):
  """ Load cached targets """
  # check if there is cached data
  print 'STATUS: Checking cache'

  # data is cached as uri => ds, construct valid uri targets to validate
  valid_target_uris = []
  for valid_target in valid_targets:
    for target_key, target_values in valid_target.iteritems():
      valid_target_uris.append(target_key + target_values['filter'])

  # find the cached files
  cached_files = glob.glob(os.path.join(cache_config['dir'], '*.json'))
  if not cached_files:
    print 'STATUS: No targets cached'
    return []

  # load the cached files
  cached_ds = {}
  for cached_file in cached_files:
    cached_ds.update(load_json_file(cached_file))

  # extract out the elements whose keys match valid_target_uris

  valid_uris = set(cached_ds.keys()) & set(valid_target_uris)
  if not valid_uris:
    print 'STATUS: Did not find any valid cached targets'
    return []
  print 'STATUS: Found cached targets - %s' % sorted(list(valid_uris))

  # ignore keys other than valid_cached_ds keys
  for invalid_uri in set(cached_ds.keys()) - valid_uris:
    del cached_ds[invalid_uri]

  return cached_ds

def load_targets(targetfiles):
  """ Load the targets data """
  print 'STATUS: Loading target names from %s' % targetfiles
  targets_ds = [load_json_file(x) for x in targetfiles]
  targetnames = flatten_list([x.keys() for x in targets_ds])
  print 'STATUS: Found targets - %s' % sorted(targetnames)
  return targets_ds

def load_action(actionfile, target_action):
  """ Load the action data """
  print 'STATUS: Loading actionfile %s' % actionfile
  action_ds = load_json_file(actionfile)
  actionnames = action_ds.keys()

  if len(actionnames) > 1:
    raise ValueError('Found > 1 action in [%s] - %s' % (actionfile, actionfile))

  actionname = actionnames[0]
  if actionname != target_action:
    raise ValueError('Found invalid action [%s] - expecting %s' % (actionname,
                                                                   target_action))

  print 'STATUS: Found action - %s' % actionname
  return action_ds

def validate_configfile(ctx, param, value):
  """ Validate the main configfile presence """
  configfile = value
  if configfile is None:
    raise click.BadParameter('not specified - check --help')
  try:
    _validate_file(configfile)
  except ValueError as exception_obj:
    raise click.BadParameter(str(exception_obj))
  return configfile

@click.group()
@click.option('-c', '--configfile', envvar='DEVICE42_MGR_CONFIGFILE',
              callback=validate_configfile,
              help='config file. Default: env var DEVICE42_MGR_CONFIGFILE')
@click.pass_context
def cli(ctx, **kwargs):
  """ Manage device42 bulk operations """
  ctx.obj['config'] = load_json_file(kwargs['configfile'])
  validate_config(ctx.obj['config'])
  print 'STATUS: Loading config file %s' % kwargs['configfile']

@cli.command()
@click.pass_context
def create(ctx, **kwargs):
  """ Create device42 objects """
  raise NotImplementedError('Not implemented yet')

@cli.command()
@click.option('-t', '--targetfile', callback=find_targetfiles, multiple=True,
              help='target files to read and act on. Default "targets" section in --configfile',
              default=None)
@click.option('-a', '--actionfile', callback=find_read_actionfile,
              help='action file to read and act on. Default $actions_dir/read.json',
              default=None)
@click.option('--cache/--no-cache', default=True,
              help='Use cached data. Default: True')
@click.option('--maxrecords', default=-1,
              help='Max records to show. Default: -1 - show all')
@click.pass_context
def read(ctx, **kwargs):
  """ Read device42 objects """
  # renaming key because targetfile contains an array
  kwargs['targetfiles'] = copy.deepcopy(kwargs['targetfile'])
  del kwargs['targetfile']
  kwargs['targets'] = load_targets(kwargs['targetfiles'])
  kwargs['action'] = load_action(kwargs['actionfile'], 'read')
  cached_targets = []
  if kwargs['cache']:
    cached_targets = load_cached_targets(ctx.obj['config']['cache'], kwargs['targets'])
    if not cached_targets:
      print kwargs['targets']

@cli.command()
@click.option('-t', '--targetfile', callback=find_targetfiles, multiple=True,
              help='target files to read and act on. Default "targets" section in --configfile',
              default=None)
@click.option('-a', '--actionfile', callback=find_update_actionfile,
              help='action file to read and act on. Default $actions_dir/update.json',
              default=None)
@click.option('--cache/--no-cache', default=True,
              help='Use cached data. Default: True')
@click.option('--dry-run', default=True,
              help='Perform dry run. Default: True')
@click.pass_context
def update(ctx, **kwargs):
  """ Update device42 objects """
  kwargs['targetfiles'] = copy.deepcopy(kwargs['targetfile'])
  del kwargs['targetfile']
  kwargs['targets'] = load_targets(kwargs['targetfiles'])
  kwargs['action'] = load_action(kwargs['actionfile'], 'update')

@cli.command()
@click.pass_context
def delete(ctx, **kwargs):
  """ Delete device42 objects """
  print ctx, kwargs
  raise NotImplementedError('Not implemented yet')

if __name__ == '__main__':
  cli(obj={})
