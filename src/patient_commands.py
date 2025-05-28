import click
from src.database import get_db

@click.group()
def patient():
    """Patient related commands."""
    pass

# You can add subcommands here, e.g.:
# @patient.command()
# def list():
#     click.echo("Listing patients")