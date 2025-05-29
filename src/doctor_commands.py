import click
from sqlalchemy.orm import Session
from src.database import engine
from src.models import Doctor, Department, Base

# Create DB tables 
#engine = get_engine()
Base.metadata.create_all(engine)

@click.group()
def doctor():
    """Doctor operations"""
    pass

@doctor.command()
@click.option('--name', prompt='Doctor name')
@click.option('--specialization', prompt='Specialization')
@click.option('--department_id', prompt='Department ID', type=int, default=None)
def add(name, specialization, department_id):
    """Add a new doctor"""
    with Session(engine) as session:
        new_doc = Doctor(name=name, specialization=specialization, department_id=department_id)
        session.add(new_doc)
        session.commit()
        click.echo(f'Doctor {name} added.')

@doctor.command()
@click.argument('doctor_id', type=int)
@click.option('--name', prompt='New name', required=False)
@click.option('--specialization', prompt='New specialization', required=False)
@click.option('--department_id', type=int, required=False)
def update(doctor_id, name, specialization, department_id):
    """Update doctor information"""
    with Session(engine) as session:
        doc = session.get(Doctor, doctor_id)
        if not doc:
            click.echo("Doctor not found.")
            return
        if name:
            doc.name = name
        if specialization:
            doc.specialization = specialization
        if department_id is not None:
            doc.department_id = department_id
        session.commit()
        click.echo(f'Doctor ID {doctor_id} updated.')

@doctor.command()
def list():
    """List all doctors"""
    with Session(engine) as session:
        doctors = session.query(Doctor).all()
        for d in doctors:
            click.echo(f'{d.id}: {d.name} ({d.specialization}) - Department ID: {d.department_id}')

@doctor.command()
@click.argument('doctor_id', type=int)
def delete(doctor_id):
    """Delete a doctor (also deletes appointments and records)"""
    with Session(engine) as session:
        doc = session.get(Doctor, doctor_id)
        if not doc:
            click.echo("Doctor not found.")
            return
        session.delete(doc)
        session.commit()
        click.echo(f'Doctor ID {doctor_id} deleted.')

@doctor.command()
@click.argument('specialization')
def filter(specialization):
    """Filter doctors by specialization"""
    with Session(engine) as session:
        docs = session.query(Doctor).filter(Doctor.specialization.ilike(f'%{specialization}%')).all()
        for d in docs:
            click.echo(f'{d.id}: {d.name} ({d.specialization})')

