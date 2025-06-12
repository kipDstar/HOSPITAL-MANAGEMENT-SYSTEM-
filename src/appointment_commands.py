import click
from src.database import get_db
from src.models import Appointment, Patient, Doctor, Department, AppointmentStatus
from datetime import datetime

import sys
import os

# Add the root project directory (one level up from 'src/') to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import DATABASE_URL


@click.group()
def appointment():
    """Manage appointments."""
    pass

@appointment.command('add')
@click.option('--patient-id', required=True, type=int, help='ID of the patient.')
@click.option('--doctor-id', required=True, type=int, help='ID of the doctor.')
@click.option('--datetime', 'appointment_datetime', required=True, help="Appointment datetime in 'YYYY-MM-DD HH:MM' format.")
@click.option('--reason', default='', help='Reason for the appointment.')
@click.option('--status', default='scheduled', type=click.Choice([status.value for status in AppointmentStatus]), help='Appointment status.')
def add_appointment(patient_id, doctor_id, appointment_datetime, reason, status):
    """Add a new appointment."""
    session = next(get_db())
    try:
        patient = Patient.find_by_id(session, patient_id)
        doctor = Doctor.find_by_id(session, doctor_id)
        if not patient:
            click.echo(f"Patient with ID {patient_id} not found.", err=True)
            return
        if not doctor:
            click.echo(f"Doctor with ID {doctor_id} not found.", err=True)
            return
        
        # Parse datetime
        try:
            dt = datetime.strptime(appointment_datetime, '%Y-%m-%d %H:%M')
        except ValueError:
            click.echo("Invalid datetime format. Use 'YYYY-MM-DD HH:MM'", err=True)
            return
        
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=dt,
            reason=reason,
            status=AppointmentStatus(status)
        )
        session.add(appointment)
        session.commit()
        click.echo(f"Appointment ID {appointment.id} added successfully.")
    except Exception as e:
        click.echo(f"Error adding appointment: {e}", err=True)
    finally:
        session.close()
    

@appointment.command('list')
@click.option('--patient-id', type=int, help='Filter appointments by patient ID.')
@click.option('--doctor-id', type=int, help='Filter appointments by doctor ID.')
def list_appointments(patient_id, doctor_id):
    """List appointments. Can filter by patient or doctor."""
    session = next(get_db())
    try:
        query = session.query(Appointment)
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        appointments = query.all()
        if not appointments:
            click.echo("No appointments found.")
            return

        for appt in appointments:
            click.echo(f"ID: {appt.id} | Patient ID: {appt.patient_id} | Doctor ID: {appt.doctor_id} | "
                       f"Date: {appt.appointment_datetime.strftime('%Y-%m-%d %H:%M')} | Reason: {appt.reason} | "
                       f"Status: {appt.status.value}")
    except Exception as e:
        click.echo(f"Error listing appointments: {e}", err=True)
    finally:
        session.close()


@appointment.command('update')
@click.argument('appointment_id', type=int)
@click.option('--patient-id', type=int, help='New patient ID.')
@click.option('--doctor-id', type=int, help='New doctor ID.')
@click.option('--datetime', 'appointment_datetime', help="New appointment datetime in 'YYYY-MM-DD HH:MM' format.")
@click.option('--reason', help='New reason.')
@click.option('--status', type=click.Choice([status.value for status in AppointmentStatus]), help='New status.')
def update_appointment(appointment_id, patient_id, doctor_id, appointment_datetime, reason, status):
    """Update an appointment by ID."""
    session = next(get_db())
    try:
        appt = session.query(Appointment).filter_by(id=appointment_id).first()
        if not appt:
            click.echo(f"Appointment with ID {appointment_id} not found.", err=True)
            return

        if patient_id:
            patient = Patient.find_by_id(session, patient_id)
            if not patient:
                click.echo(f"Patient with ID {patient_id} not found.", err=True)
                return
            appt.patient_id = patient_id
        
        if doctor_id:
            doctor = Doctor.find_by_id(session, doctor_id)
            if not doctor:
                click.echo(f"Doctor with ID {doctor_id} not found.", err=True)
                return
            appt.doctor_id = doctor_id

        if appointment_datetime:
            try:
                dt = datetime.strptime(appointment_datetime, '%Y-%m-%d %H:%M')
                appt.appointment_datetime = dt
            except ValueError:
                click.echo("Invalid datetime format. Use 'YYYY-MM-DD HH:MM'", err=True)
                return

        if reason is not None:
            appt.reason = reason
        
        if status is not None:
            appt.status = AppointmentStatus(status)

        session.commit()
        click.echo(f"Appointment ID {appointment_id} updated successfully.")
    except Exception as e:
        click.echo(f"Error updating appointment: {e}", err=True)
    finally:
        session.close()

@appointment.command('delete')
@click.argument('appointment_id', type=int)
def delete_appointment(appointment_id):
    """Delete an appointment by ID."""
    session = next(get_db())
    try:
        appt = session.query(Appointment).filter_by(id=appointment_id).first()
        if not appt:
            click.echo(f"Appointment with ID {appointment_id} not found.", err=True)
            return
        
        session.delete(appt)
        session.commit()
        click.echo(f"Appointment ID {appointment_id} deleted successfully.")
    except Exception as e:
        click.echo(f"Error deleting appointment: {e}", err=True)
    finally:
        session.close()

if __name__ == '__main__':
    appointment()
# This code defines a command-line interface (CLI) for managing appointments in a hospital management system.



# -------------------- APPOINTMENT COMMANDS --------------------
# To add a appointment
#         => python -m src.cli appointment add --patient-id 1 --doctor-id 2 --datetime "2025-06-10 14:00" --reason "Checkup" --status scheduled

# To list appointments
#         => python -m src.cli appointment list

# To list specific patient appointments
#         => python -m src.cli appointment list --patient-id 1

# To list specific doctor appointments
#         => python -m src.cli appointment list --doctor-id 1

# To update a appointment
#         => python -m src.cli appointment update 3 --patient-id 2 --doctor-id 4 --datetime "2025-06-15 09:00" --reason "Follow-up" --status completed

# To delete a appointment 
#         => python -m src.cli appointment delete <appointment_id>