
import  click
import math
import random
import time
import sys
from madmigration.config.conf import  Config
from madmigration.mad_migration import MadMigration


@click.group()
def cli():
    """MadMigration group Cli"""
    

@cli.command()
def clear():
    """This will clear the entire screen """
    click.clear()



@cli.command(help='simple Migrate ready on hand with CLI')
def cli():
    
    click.echo("hello world")

    config = Config("test.yaml")

    a = MadMigration(config)
    a.test_func()


    