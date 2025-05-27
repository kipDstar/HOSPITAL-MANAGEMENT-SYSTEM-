import click

@click.group()
def doctor():
    """Doctor commands."""
    pass

#@doctor.command()
#def list():
#    click.echo("Listing the doctors")