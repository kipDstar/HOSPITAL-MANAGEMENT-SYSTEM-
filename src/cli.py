#print(f"DEBUG: Entering src/cli.py execution.")
import click

# We are importing a file form database
#    create_tables => creates the database tables
from src.database import create_tables
# Imports the function that fills your database with dummy test data (like fake patients and doctors).
from src.seed import seed_database

# This imports the files that define extra commands(These files hold organized subcommands like add, list, or update)
from src import patient_commands, doctor_commands, department_commands
import src.models


# This function will be the main command group for the app.(Stores related commands)
@click.group() 
# Defines the cli() function — which is the main entry point for your CLI.
def cli():
    # This is the CLI description(it appears when one runs python cli.py --help)
    """Hospital Management CLI"""


# Registers a new CLI command (in this case, initdb).[It allows us to run *python cli.py getdb*]
@cli.command() 
# This function will create your database tables.
def createtables():
    """Initialized Database Tables"""
    # get_db => Actually runs the logic to create tables using SQLAlchemy.
    print('DEBUG: calling the create tables function now')
    create_tables()
    # Prints a success message to the terminal.(just like print())
    click.echo("Database Tables Successfully Created")
    pass 


# Follows same structure as the getdb function
@cli.command() 
def seed():
    """Populate Dummy with fake data"""
    seed_database()
    click.echo("Dummy data created")

#registers commands from other files

# Adds all commands from patient_commands.py to the CLI.(Allows us to run *python cli.py patient add*)
cli.add_command(patient_commands.patient)
# Adds all commands from doctor_commands.py to the CLI.(Allows us to run *python cli.py doctor list*)
#cli.add_command(doctor_commands.doctor)
# Adds all commands from department_commands.py to the CLI.(Allows us to run *python cli.py department delete 3*)
#cli.add_command(department_commands.department)


# You will need to import (get_db) in all the command files