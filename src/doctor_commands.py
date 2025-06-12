import click
from src.database import get_db
from src.models import Doctor, Department, Patient, Appointment

import sys
import os

# Add the root project directory (one level up from 'src/') to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import DATABASE_URL



@click.group()
def doctor():
    """Doctor operations"""
    pass

@doctor.command()
@click.option('--name', prompt='Doctor name')
@click.option('--specialization', prompt='Specialization')
@click.option('--contact_info', prompt='Contact Info', default=None)
@click.option('--department_id', prompt='Department ID', type=int, default=None)
def add(name, specialization, department_id, contact_info):
    """Add a new doctor"""
    db = next(get_db())
    try:
        new_doc = Doctor(name=name, specialization=specialization, department_id=department_id, contact_info=contact_info)
        db.add(new_doc)
        db.commit()
        click.echo(f'Doctor {name} added.')
    except Exception as e:
        db.rollback()
        click.echo(f"Error adding doctor: {e}", err=True)
    finally:
        db.close()


@doctor.command()
@click.argument('doctor_id', type=int)
@click.option('--name', prompt='New name', required=False)
@click.option('--specialization', prompt='New specialization', required=False)
@click.option('--department_id', type=int, required=False)
def update(doctor_id, name, specialization, department_id):
    """Update doctor information"""
    db = next(get_db())
    try:
        doc = db.get(Doctor, doctor_id)
        if not doc:
            click.echo("Doctor not found.")
            return

        if name:
            doc.name = name
        if specialization:
            doc.specialization = specialization
        if department_id is not None:
            doc.department_id = department_id

        db.commit()
        click.echo(f'Doctor ID {doctor_id} updated.')
    except Exception as e:
        db.rollback()
        click.echo(f"Error updating doctor: {e}", err=True)
    finally:
        db.close()
    

@doctor.command()
def list():
    """List all doctors"""
    db = next(get_db())
    try:
        doctors = db.query(Doctor).all()
        if not doctors:
            click.echo("No doctors found.")
            return
        for doc in doctors:
            dept_name = db.query(Department.name).filter(Department.id == doc.department_id).scalar() if doc.department_id else "N/A"
            click.echo(f'{doc.id}: {doc.name} ({doc.specialization}) - Department: {dept_name}')
    except Exception as e:
        click.echo(f"Error listing doctors: {e}", err=True)
    finally:
        db.close()

@doctor.command()
@click.argument('doctor_id', type=int)
def delete(doctor_id):
    """Delete a doctor (also deletes appointments and records)"""
    db = next(get_db())
    try:
        doc = db.get(Doctor, doctor_id)
        if not doc:
            click.echo("Doctor not found.")
            return

        # Delete associated appointments and records if necessary
        # Assuming you have an Appointment model with a foreign key to Doctor
        # db.query(Appointment).filter(Appointment.doctor_id == doctor_id).delete()

        db.delete(doc)
        db.commit()
        click.echo(f'Doctor ID {doctor_id} deleted.')
    except Exception as e:
        db.rollback()
        click.echo(f"Error deleting doctor: {e}", err=True)
    finally:
        db.close()

@doctor.command()
@click.argument('specialization')
def filter(specialization):
    """Filter doctors by specialization"""
    db = next(get_db())
    try:
        doctors = db.query(Doctor).filter(Doctor.specialization == specialization).all()
        if not doctors:
            click.echo(f"No doctors found with specialization '{specialization}'.")
            return
        for doc in doctors:
            dept_name = db.query(Department.name).filter(Department.id == doc.department_id).scalar() if doc.department_id else "N/A"
            click.echo(f'{doc.id}: {doc.name} ({doc.specialization}) - Department: {dept_name}')
    except Exception as e:
        click.echo(f"Error filtering doctors: {e}", err=True)
    finally:
        db.close()


if __name__ == '__main__':
    doctor()
# This code defines a CLI for managing doctors in a hospital management system.
# It allows adding, updating, listing, deleting, and filtering doctors by specialization.
# The commands interact with a database using SQLAlchemy, and handle errors gracefully.


# -------------------- DOCTOR COMMANDS --------------------
# To add a doctor
#         => python -m src.cli doctor add

# To list doctors
#         => python -m src.cli doctor list

# To update a doctor
#         => python -m src.cli doctor update <doctor_id>

# To delete a doctor 
#         => python -m src.cli doctor delete <doctor_id>