import click

@click.group()
def department():
    """Department related commands."""
    pass

# You can add subcommands here, e.g.:
# @department.command()
# def list():
#     click.echo("Listing departments")