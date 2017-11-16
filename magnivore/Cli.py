# -*- coding: utf-8 -*-
import click

from .App import App
from .Config import Config
from .Tracker import Tracker, database


class Cli:
    """
    Provides command line access to Magnivore functionalites
    """
    @click.group()
    def main():
        pass

    @staticmethod
    @main.command()
    @click.argument('rulesfile', required=False)
    @click.option('--verbose', '-v', count=True)
    def run(rulesfile, verbose):
        """
        Performs migrations using rules.json or a given file
        """
        kwargs = {}
        if rulesfile:
            kwargs['rules_file'] = rulesfile
        if verbose:
            kwargs['verbosity'] = verbose
        App.run(**kwargs)

    @main.command()
    def init():
        """
        Initial setup for magnivore
        """
        database.create_tables([Tracker])
        database.commit()

    @main.command(name='config-skeleton')
    def config_skeleton():
        """
        Generates a skeleton configuration file
        """
        config = Config()
        config.set_to_default()
        config.save()

    @main.command()
    def hello():
        """
        Outputs the version
        """
        click.echo('0.3.1')

    @main.command()
    def version():
        click.echo('0.3.1')
