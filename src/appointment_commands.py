import click
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.database import engine
from src.models import Appointment, Patient, Doctor

Session = sessionmaker(bind=engine)
session = Session()

@click.group()
def app_cli():
    """Appointment Management Commands"""
    pass

@app_cli.command("schedule-appointment")
def schedule_appointment():
    """Schedule a new appointment"""
    try:
        patient_id = int(input("Enter patient ID: "))
        doctor_id = int(input("Enter doctor ID: "))
        date_str = input("Enter appointment date (YYYY-MM-DD HH:MM): ")
        reason = input("Enter reason for appointment: ")

        appointment_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

        
        patient = session.query(Patient).get(patient_id)
        doctor = session.query(Doctor).get(doctor_id)

        if not patient or not doctor:
            click.echo("Patient or doctor not found.")
            return

        new_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            reason=reason
        )

        session.add(new_appointment)
        session.commit()
        click.echo("✅ Appointment scheduled successfully.")

    except Exception as e:
        session.rollback()
        click.echo(f"❌ Error scheduling appointment: {e}")

@app_cli.command("list-appointments")
def list_appointments():
    """List all appointments"""
    appointments = session.query(Appointment).all()
    if not appointments:
        click.echo("No appointments found.")
        return
    for appt in appointments:
        click.echo(
            f"Appointment ID: {appt.id}, "
            f"Patient ID: {appt.patient_id}, "
            f"Doctor ID: {appt.doctor_id}, "
            f"Date: {appt.appointment_date}, "
            f"Reason: {appt.reason}"
        )

@app_cli.command("cancel-appointment")
def cancel_appointment():
    """Cancel an appointment"""
    try:
        appt_id = int(input("Enter appointment ID to cancel: "))
        appointment = session.query(Appointment).get(appt_id)
        if not appointment:
            click.echo("Appointment not found.")
            return
        session.delete(appointment)
        session.commit()
        click.echo("✅ Appointment cancelled successfully.")
    except Exception as e:
        session.rollback()
        click.echo(f"❌ Error cancelling appointment: {e}")

@app_cli.command("appointments-by-doctor")
def appointments_by_doctor():
    """List appointments by doctor"""
    try:
        doctor_id = int(input("Enter doctor ID: "))
        appointments = session.query(Appointment).filter_by(doctor_id=doctor_id).all()
        if not appointments:
            click.echo("No appointments found for this doctor.")
            return
        for appt in appointments:
            click.echo(
                f"Appointment ID: {appt.id}, "
                f"Patient ID: {appt.patient_id}, "
                f"Date: {appt.appointment_date}, "
                f"Reason: {appt.reason}"
            )
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@app_cli.command("appointments-by-date")
def appointments_by_date():
    """List appointments by date"""
    try:
        date_str = input("Enter date (YYYY-MM-DD): ")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appointments = session.query(Appointment).all()
        filtered = [a for a in appointments if a.appointment_date.date() == date]

        if not filtered:
            click.echo("No appointments found for this date.")
            return

        for appt in filtered:
            click.echo(
                f"Appointment ID: {appt.id}, "
                f"Patient ID: {appt.patient_id}, "
                f"Doctor ID: {appt.doctor_id}, "
                f"Time: {appt.appointment_date.time()}, "
                f"Reason: {appt.reason}"
            )
    except Exception as e:
        click.echo(f"❌ Error: {e}")
