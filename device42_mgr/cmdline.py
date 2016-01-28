#!/usr/bin/env python

""" Manage device42 bulk operations """

import click

@click.group()
@click.option('--configfile', envvar='D42_CONFIGFILE',
              help='device42_mgr config file. Default: env var D42_CONFIGFILE')
def cli(**kwargs):
  """ Manage device42 bulk operations """
  pass

@cli.command()
@click.argument('datafile')
def create(**kwargs):
  """ Create device42 objects """
  pass

@cli.command()
@click.argument('datafile')
@click.option('--cached', default=True,
              help='Use cached data. Default: True')
@click.option('--maxrecords', default=-1,
              help='Max records to show. Default: -1 - show all')
def read(**kwargs):
  """ Read device42 objects """
  pass

@cli.command()
@click.argument('datafile')
@click.option('--cached', default=True,
              help='Use cached data. Default: True')
def update(**kwargs):
  """ Update device42 objects """
  pass

@cli.command()
@click.argument('datafile')
def delete(**kwargs):
  """ Delete device42 objects """
  pass

if __name__ == '__main__':
  cli()
