import click
from datetime import datetime
from database import get_db
from models import Patient, OutPatient, InPatient

import sys
import os

# Add the root project directory (one level up from 'src/') to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import DATABASE_URL

@click.group()
# Defines the group of CLI under patients with (cli) as the entry point of the group
def cli():
    """Patient Management CLI"""


# This defines the -----ADD COMMAND------, which adds a new patient.
# It creates a flag (like --type) for your CLI command.
# Provide Prompts for the user to input when the command is run.
# Provide help text (--help) => which explains what an option does.
# *click.Choice* => This restricts the input to only two allowed values: "inpatient" or "outpatient".
#                 If the user enters anything else, they’ll see an error like:
#                 (Error: Invalid value for '--type': 'visitor' is not one of 'inpatient', 'outpatient'.)
# (default = None) => ensures that when a value is not provided it is filled to be automatically none
@cli.command()
@click.option('--name', prompt = 'Name', help = 'Patient Full Name')
@click.option('--dob', prompt = 'Date of Birth (YYYY MM DD)', help = 'Patient birth date')
@click.option('--contact', prompt = 'Contact', help = 'Patient contact')
@click.option('--type', prompt = 'Type (inpatient/outpatient)', type = click.Choice(['inpatient', 'outpatient']))
@click.option('--room', default = None, type = int, help = 'Patient room number')
@click.option('--admission', default = None, help = 'Admission Date (YYY MMM DD)')
@click.option('--discharge', default = None, help = 'Discharge Date (YYY MMM DD)')
@click.option('--last_visit', default = None, help = 'Last Visit Date (YYY MMM DD)')
def add(name, dob, contact, type, room, admission, discharge, last_visit):
    """Add a new patient"""
    # To actually retrieve the session object from the generator, you have to call next():
    # This says: “give me the next (first) value from the generator,” which is your actual database session.
    # Now db is a usable SQLAlchemy session, and you can do things like: [db.query(Patient).all()]

    db = next(get_db())
    # datetime.strptime(admission, '%Y-%M-%D) =>
    #                  'This converts the string (like "2024-06-01") into a proper datetime.date object.
    #                  '%Y-%m-%d' is the format:
    #                   %Y: 4-digit year
    #                   %m: 2-digit month
    #                   %d: 2-digit day


    try: 
        if type == 'inpatient':
            patient = InPatient(
                name = name,
                date_of_birth = dob,
                contact_info = contact,
                type = 'inpatient',
                room_number = room,
                admission_date = datetime.strptime(admission, '%Y-%M-%D') if admission else None , 
                discharge_date = datetime.strptime(discharge, '%Y-%M-%D') if discharge else None,
            )

        else:
            patient = OutPatient(
                name = name,
                date_of_birth = dob,
                contact_info = contact,
                type = 'outpatient',
                last_visit_date = datetime.strptime(last_visit, '%Y-%M-%D') if last_visit else None
            )

        # db.add(patient) => This stages (prepares) the patient object to be added to the database.
        #                    The object isn't saved yet — it's just marked for insertion in the session.
        db.add(patient)
        # db.commit() => This commits the transaction — all changes staged with .add() are written to the database.
        #                If this line succeeds: the new patient is saved permanently in the DB.
        db.commit()
        click.echo(f"{type.capitalize()} '{name}' added successfully!")

    # If something goes wrong in .add() or .commit(), this block catches the error.
    # Catches and prints errors if anything fails
    except Exception as e:
        # db.rollback() => Reverts changes if there's an error(Cancels any uncommitted changes.)
        #                  Ensures the database stays consistent and doesn't save a half-finished transaction.

        db.rollback()
        click.echo(f"Error adding patient: {e}")

    # Always closes the session to avoid open DB connections
    finally:
        db.close()




