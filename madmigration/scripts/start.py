import click
import math
import random
import time
import sys
from madmigration.config.conf import Config
from madmigration.main import Controller


@click.group()
def cli():
    """Takeaway group Cli"""
    

@cli.command()
def clear():
    """This will clear the entire screen """
    click.clear()


@cli.command(help='😄 simple Migrate ready on hand with CLI')
def cli():
    click.echo("hello world")

    config = Config("mysql.yaml")

    a = Controller(config)
    a.test_func()
