
import  click
import math
import random
import time
import sys
from config.conf import  Config
from src.mad_migration import MadMigration


@click.group()
def cli():
    """Takeaway group Cli"""
    

@cli.command()
def clear():
    """This will clear the entire screen """
    click.clear()



@cli.command(help='😄 simple boilerplate ready for development')
def cli():
    print("hello wprl")
    click.echo("test")

    config = Config("test.yaml")

    a = MadMigration(config)
    a.test_func()


