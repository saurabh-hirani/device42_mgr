#!/usr/bin/env python

""" Manage device42 bulk operations """

# TODO
# - make the cmdline client thinner and abstract out more logic to a device42_mgr
#   class
# - use structured logging

import os
import copy
import click
import json

from device42_mgr.loader import Loader, Device42MgrLoaderException
from device42_mgr.cachier import Cachier
from device42_mgr.lib.utils import InvalidValueException
import device42_mgr.lib.utils as utils

def _find_default_actionfile(ctx, action):
  """ Find the default action file depending on the action """
  actionfile = os.path.join(ctx.obj['config']['actions']['dir'], '%s.json' % action)
  utils.validate_file(actionfile)
  return actionfile

def _find_actionfile(action, ctx, actionfile):
  """ Return default action file if empty - else validate input """
  if actionfile is None:
    return _find_default_actionfile(ctx, action)
  utils.validate_file(actionfile)
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
      try:
        utils.validate_file(filepath)
      except InvalidValueException as invalid_value_exception:
        click.echo(click.style(str(invalid_value_exception), fg='red'))
        ctx.exit(1)

  return targetfiles

def _validate_targets_config(config):
  """ Validate targets section in --configfile """
  return utils.validate_dir_files(config['dir'], config['files'])

def _validate_actions_config(config):
  """ Validate actions section in --configfile """
  return utils.validate_dir_files(config['dir'], config['files'])

def _validate_cache_config(config):
  """ Validate cache section in --configfile """
  return utils.validate_dir_files(config['dir'])

def validate_config(config):
  """ Validate config loaded from --configfile """
  _validate_targets_config(config['targets'])
  _validate_actions_config(config['actions'])
  _validate_cache_config(config['cache'])
  return True

def load_action(actionfile, target_action):
  """ Load the action data """
  action_ds = utils.load_json_file(actionfile)
  actionnames = action_ds.keys()

  if len(actionnames) > 1:
    raise InvalidValueException('Found > 1 action in [%s] - %s' % (actionfile, actionfile))

  actionname = actionnames[0]
  if actionname != target_action:
    raise InvalidValueException('Found invalid action [%s] - expecting %s' % \
                                (actionname, target_action))

  return action_ds

def validate_configfile(ctx, param, value):
  """ Validate the main configfile presence """
  configfile = value
  if configfile is None:
    raise click.BadParameter('not specified - check --help')
  try:
    utils.validate_file(configfile)
  except InvalidValueException as exception_obj:
    raise click.BadParameter(str(exception_obj))
  return configfile

@click.group()
@click.option('-c', '--configfile', envvar='DEVICE42_MGR_CONFIGFILE',
              callback=validate_configfile,
              help='config file. Default: env var DEVICE42_MGR_CONFIGFILE')
@click.pass_context
def cli(ctx, **kwargs):
  """ Manage device42 bulk operations """
  print 'STATUS: Loading config file %s' % kwargs['configfile']
  ctx.obj['config'] = utils.load_json_file(kwargs['configfile'])
  validate_config(ctx.obj['config'])


@cli.command()
@click.pass_context
def create(ctx, **kwargs):
  """ Create device42 objects """
  click.echo(click.style('Not implemented yet', fg='red'))
  ctx.exit(1)

@cli.command()
@click.option('-t', '--targetfile', callback=find_targetfiles, multiple=True,
              help='target files to read and act on. Default "targets" section in --configfile',
              default=None)
@click.option('-a', '--actionfile', callback=find_read_actionfile,
              help='action file to read and act on. Default $actions_dir/read.json',
              default=None)
@click.option('--cache/--no-cache', default=True,
              help='Use cached data. Default: True')
@click.option('--refresh/--no-refresh', default=False,
              help='Refresh the cached data. Makes sense only with --cache. ' + \
                   'Default: False')
@click.option('--maxrecords', default=-1,
              help='Max records to show. Default: -1 - show all')
@click.pass_context
def read(ctx, **kwargs):
  """ Read device42 objects """
  cache_obj = None
  if kwargs['cache'] or kwargs['refresh']:
    cache_obj = Cachier(ctx.obj['config']['cache']['dir'],
                        ctx.obj['config']['cache']['file'])
  loader = Loader(kwargs['targetfile'],
                  cache_obj,
                  use_cache=kwargs['cache'],
                  refresh_cache=kwargs['refresh'])
  try:
    loader.load()
  except Device42MgrLoaderException as loader_exception:
    click.echo(click.style(str(loader_exception), fg='red'))
    click.echo(click.style('ERROR: ' + str(loader_exception), fg='red'))
    ctx.exit(1)
  print loader
  #kwargs['action'] = load_action(kwargs['actionfile'], 'read')

@cli.command()
@click.option('-t', '--targetfile', callback=find_targetfiles, multiple=True,
              help='target files to read and act on. Default "targets"' + 
                   'section in --configfile',
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
  click.echo(click.style('Not implemented yet', fg='red'))
  ctx.exit(1)

@cli.command()
@click.pass_context
def delete(ctx, **kwargs):
  """ Delete device42 objects """
  click.echo(click.style('Not implemented yet', fg='red'))
  ctx.exit(1)

if __name__ == '__main__':
  cli(obj={})
