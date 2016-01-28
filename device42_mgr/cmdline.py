#!/usr/bin/env python

""" Manage device42 bulk operations """

import click

@click.group()
@click.option('--configfile', envvar='D42_CONFIGFILE',
              help='device42_mgr config file. Default: env var D42_CONFIGFILE')
@click.pass_context
def cli(ctx, **kwargs):
  """ Manage device42 bulk operations """
  pass

@cli.command()
@click.argument('datafile')
@click.pass_context
def create(ctx, **kwargs):
  """ Create device42 objects """
  print kwargs
  pass

@cli.command()
@click.argument('datafile')
@click.option('--cache/--no-cache', default=True,
              envvar='D42_CACHE_READS',
              help='Use cached data. Default: True')
@click.option('--maxrecords', default=-1,
              help='Max records to show. Default: -1 - show all')
@click.pass_context
def read(ctx, **kwargs):
  """ Read device42 objects """
  pass

@cli.command()
@click.argument('datafile')
@click.option('--cached', default=True,
              help='Use cached data. Default: True')
@click.pass_context
def update(ctx, **kwargs):
  """ Update device42 objects """
  pass

@cli.command()
@click.argument('datafile')
@click.pass_context
def delete(ctx, **kwargs):
  """ Delete device42 objects """
  pass

if __name__ == '__main__':
  cli()
