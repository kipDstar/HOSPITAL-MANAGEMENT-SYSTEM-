import click
from datetime import datetime
from src.database import get_db
from src.models import Patient, OutPatient, InPatient, MedicalRecord

import sys
import os

# Add the root project directory (one level up from 'src/') to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import DATABASE_URL

@click.group()
# Defines the group of CLI under patients with (cli) as the entry point of the group
def patient():
    """Patient Management CLI"""

# -------------------- PATIENT COMMANDS --------------------

# This defines the -----ADD COMMAND------, which adds a new patient.
# It creates a flag (like --type) for your CLI command.
# Provide Prompts for the user to input when the command is run.
# Provide help text (--help) => which explains what an option does.
# *click.Choice* => This restricts the input to only two allowed values: "inpatient" or "outpatient".
#                 If the user enters anything else, they’ll see an error like:
#                 (Error: Invalid value for '--type': 'visitor' is not one of 'inpatient', 'outpatient'.)
# (default = None) => ensures that when a value is not provided it is filled to be automatically none
@patient.command()
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


    if type == 'inpatient':
        if room is None:
            room = click.prompt('Room number', type=int)
        if admission is None:
            admission = click.prompt('Admission Date (YYYY-MM-DD)', default='', show_default=False)
        if discharge is None:
            discharge = click.prompt('Discharge Date (YYYY-MM-DD)', default='', show_default=False)
    elif type == 'outpatient':
        if last_visit is None:
            last_visit = click.prompt('Last Visit Date (YYYY-MM-DD)', default='', show_default=False)


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
                admission_date = datetime.strptime(admission, '%Y-%m-%d') if admission else None , 
                discharge_date = datetime.strptime(discharge, '%Y-%m-%d') if discharge else None,
            )

        else:
            patient = OutPatient(
                name = name,
                date_of_birth = dob,
                contact_info = contact,
                type = 'outpatient',
                last_visit_date = datetime.strptime(last_visit, '%Y-%m-%d') if last_visit else None
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




# This defines the -----LIST COMMAND----- which lists all the patients
@patient.command()
def list():
    """List all patients"""
    db = next(get_db())
    try: 
        patients = db.query(Patient).all()
        for p in patients:
            click.echo(f"ID: {p.id}, Name: {p.name}, Type: {p.type}, DOB: {p.date_of_birth}" )
    
    finally:
        db.close()




# This defines the -----DELETE COMMAND----- which deletes all the patients
@patient.command()
# @click.argument => This tells Click (the CLI library) that your command will take one required 
#                    argument from the command line:
#                    *patient_id: an integer*
#                    This is not optional — it must be passed when running the command.
@click.argument('patient_id', type = int)
# Defines the actual command logic:
# The function receives the argument (patient_id)
def delete(patient_id):
    """Delete a patient by ID"""
    # Grabs a session object from your get_db() generator so you can interact with the database.
    db = next(get_db())
    
    try:
        #Uses SQLAlchemy’s .get() method to fetch a Patient with the given patient_id.
        patient = db.get(Patient, patient_id)

        if not patient:
            click.echo(f"No patient with ID {patient_id} was found")
            return

        db.delete(patient)
        db.commit()
        click.echo(f"Patient with ID {patient_id} deleted.")

    except Exception as e:
        db.rollback()
        click.echo(f"Error deleting a patient {e}")

    finally:
        db.close()




# This defines -----UPDATE COMMAND-----  which updates patients information
@patient.command()
@click.argument('patient_id', type = int) 
@click.option('--name', default = None, help = 'New name')
@click.option('--dob', default = None, help = 'New DOB (YYYY MM DD)')
@click.option('--contact', default = None, help = 'New contact information')
@click.option('--room', default = None, help = 'New room number(for inpatients only)')
@click.option('--admission', default = None, help = 'New admission date (YYYY MM DD)')
@click.option('--discharge', default = None, help = 'New discharge date (YYYY MM DD)')
@click.option('--last_visit', default = None, help = 'New last visit date (YYYY MM DD)')

def update(patient_id, name, dob, contact, room, admission, discharge, last_visit):
    """Update patients information"""
    db = next(get_db())
    try: 
        patient = db.get(Patient, patient_id)
        if not patient:
            click.echo(f"No patient with ID {patient_id} was found.")
            return
        
        if name:
            patient.name = name 

        if dob:
            patient.date_of_birth = dob 

        if contact:
            patient.contact_info = contact

        if isinstance(patient, InPatient):
            if room is not None:
                patient.room_number = room

            if admission:
                patient.admission_date = datetime.strptime(admission, '%Y-%m-%d')

            if discharge:
                patient.discharge_date = datetime.strptime(discharge, '%Y-%m-%d')

        elif isinstance(patient, OutPatient):
            if last_visit:
                patient.last_visit_date = datetime.strptime(last_visit, '%Y-%m-%d')

        db.commit()
        click.echo(f"Patient ID: {patient_id} updated successfully!")

    except Exception as e:
        db.rollback()
        click.echo(f"Error updating patient: {e}")

    finally:
        db.close()




# -------------------- MEDICAL RECORDS COMMANDS --------------------
# This defines the -----ADD MEDICAL RECORD COMMAND ------ which adds a patients medical record
@patient.command()
@click.argument('patient_id', type=int)
@click.option('--diagnosis', prompt='Diagnosis', help='Diagnosis')
@click.option('--treatment', prompt='Treatment', help='Treatment')
@click.option('--record_date', default=None, help='Record Date (YYYY-MM-DD)')
def add_record(patient_id, diagnosis, treatment, record_date):
    """Add a medical record for a patient"""
    db = next(get_db())
    try:
        patient = db.get(Patient, patient_id)
        if not patient:
            click.echo(f"No patient with ID {patient_id}")
            return
        record = MedicalRecord(
            patient_id=patient_id,
            diagnosis=diagnosis,
            treatment=treatment,
            record_date=datetime.strptime(record_date, '%Y-%m-%d') if record_date else datetime.utcnow()
        )
        db.add(record)
        db.commit()
        click.echo(f"Medical record for patient ID {patient_id} added.")
    except Exception as e:
        db.rollback()
        click.echo(f"Error adding record: {e}")
    finally:
        db.close()


# This defines the ----- LIST MEDICAL RECORD COMMAND ------ which lists all patients medical records
@patient.command()
def list_records():
    """List all medical records"""
    db = next(get_db())
    try:
        records = db.query(MedicalRecord).all()
        for r in records:
            click.echo(f"ID: {r.id}, Patient ID: {r.patient_id}, Diagnosis: {r.diagnosis}, Treatment: {r.treatment}, Date: {r.record_date}")
    finally:
        db.close()




# This defines the ----- DELETE MEDICAL RECORD COMMAND ------ which deletes all patients medical records
@patient.command()
@click.argument('record_id', type=int)
def delete_record(record_id):
    """Delete a medical record by ID"""
    db = next(get_db())
    try:
        record = db.get(MedicalRecord, record_id)
        if not record:
            click.echo(f"No record with ID {record_id}")
            return
        db.delete(record)
        db.commit()

        click.echo(f"Medical record ID {record_id} deleted.")

    except Exception as e:
        db.rollback()
        click.echo(f"Error deleting record: {e}")

    finally:
        db.close()


if __name__ == '__main__':
    patient()




# ---------- COMMANDS TO RUN -----------

# The ADD COMMAND
#      => python -m src.cli patient add

# The LIST COMMAND
#      => python -m src.cli patient list

# The UPDATE COMMAND
#      => python -m src.cli patient update <patient_id> [--name ...] [--dob ...] [--contact ...] [--room ...] [--admission ...] [--discharge ...] [--last_visit ...]
#      => python -m src.cli patient update 1 --name "Updated Name" --contact "0711223344"

# The DELETE COMMAND
#      => python -m src.cli patient delete <patient_id>
#      => python -m src.cli patient delete 2

# To view all available commands
#      => python -m src.cli --help

#  To view help for a sub-class commands 
#      => python -m src.cli patient --help

# -------------------- MEDICAL RECORDS COMMANDS --------------------
# To add a medical record 
#      => python -m src.cli patient add-record <patient_id>

# To list medical records
#      => python -m src.cli patient list-records

# To delete a medical record
#      => python -m src.cli patient delete-record <record_id>

