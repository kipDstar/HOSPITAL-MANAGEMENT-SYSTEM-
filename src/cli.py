# src/cli.py

import click
from datetime import date, datetime
from src.database import get_db, create_tables # Import get_db_session and create_tables
from src.models import Department, Doctor, Patient, Appointment, MedicalRecord, InPatient, OutPatient # Import all your models
from src.seed import seed_database # Import the seed function
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}
    pass

@cli.command
def createtables():
    """Initialized Database Tables"""
    print("DEBUG: Calling create_tables() function...", file=sys.stdout, flush=True) # Optional: Add for more debug
    create_tables()
    click.echo("Database Tables Successfully Created")
    pass

@cli.command
def seed():
    """Populate Dummy with fake data"""
    seed_database()
    click.echo("Dummy data created")

# --- Department Commands 
@cli.group()
def department():
    """Manages hospital departments."""
    pass

@department.command('add')
@click.option('--name', required=True, help="Name of the department.")
@click.option('--head-doctor-id', type=int, help="ID of the doctor to assign as head (optional).")
def add_department(name, head_doctor_id):
    """Adds a new department."""
    session = next(get_db()) # Get a new session
    try:
        # Validate if head_doctor_id is provided, that the doctor exists
        if head_doctor_id:
            doctor = Doctor.find_by_id(session, head_doctor_id)
            if not doctor:
                click.echo(f"Error: Doctor with ID {head_doctor_id} not found. Department not added.", err=True)
                return

        dept = Department.create(session, name=name, head_doctor_id=head_doctor_id)
        click.echo(f"Department '{dept.name}' (ID: {dept.id}) added successfully.")
    except Exception as e:
        click.echo(f"Error adding department: {e}", err=True)
    finally:
        session.close() # Always close the session

@department.command('list')
def list_departments():
    """Lists all departments."""
    session = next(get_db())
    try:
        departments = Department.get_all(session)
        if not departments:
            click.echo("No departments found.")
            return

        click.echo("--- Departments ---")
        for dept in departments:
            head_name = dept.head_doctor.name if dept.head_doctor else "None"
            click.echo(f"ID: {dept.id}, Name: {dept.name}, Head: {head_name}")
        click.echo("-------------------")
    except Exception as e:
        click.echo(f"Error listing departments: {e}", err=True)
    finally:
        session.close()

@department.command('show')
@click.argument('department_id', type=int)
def show_department(department_id):
    """Shows details for a specific department."""
    session = next(get_db())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return

        head_name = dept.head_doctor.name if dept.head_doctor else "None"
        staff_count = dept.get_staff_count() # Using the new instance method
        
        click.echo(f"--- Department Details (ID: {dept.id}) ---")
        click.echo(f"Name: {dept.name}")
        click.echo(f"Head Doctor: {head_name}")
        click.echo(f"Number of Doctors: {staff_count}")
        
        # Innovative Feature: List doctors in this department
        if dept.doctors:
            click.echo("Doctors in this Department:")
            for doctor in dept.doctors:
                click.echo(f"  - ID: {doctor.id}, Name: {doctor.name}, Specialization: {doctor.specialization}")
        else:
            click.echo("No doctors assigned to this department.")
        click.echo("------------------------------------")
    except Exception as e:
        click.echo(f"Error showing department: {e}", err=True)
    finally:
        session.close()

@department.command('update')
@click.argument('department_id', type=int)
@click.option('--name', help="New name for the department.")
@click.option('--head-doctor-id', type=int, help="New head doctor ID for the department.")
def update_department(department_id, name, head_doctor_id):
    """Updates an existing department's name or head doctor."""
    session = next(get_db())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return

        # Prepare kwargs for update_info
        update_kwargs = {}
        if name is not None:
            update_kwargs['name'] = name
        if head_doctor_id is not None:
            # Validate if head doctor exists before attempting to assign
            doctor = Doctor.find_by_id(session, head_doctor_id)
            if not doctor:
                click.echo(f"Error: Doctor with ID {head_doctor_id} not found. Department not updated.", err=True)
                return
            update_kwargs['head_doctor_id'] = head_doctor_id # Pass ID to update_info

        if not update_kwargs:
            click.echo("No update parameters provided.", err=True)
            return

        dept.update_info(session, **update_kwargs) # Use the instance method
        click.echo(f"Department '{dept.name}' (ID: {dept.id}) updated successfully.")
    except Exception as e:
        click.echo(f"Error updating department: {e}", err=True)
    finally:
        session.close()

@department.command('delete')
@click.argument('department_id', type=int)
def delete_department(department_id):
    """Deletes a department."""
    session = next(get_db())
    try:
        if Department.delete_by_id(session, department_id):
            click.echo(f"Department with ID {department_id} deleted successfully.")
        else:
            click.echo(f"Department with ID {department_id} not found.", err=True)
    except Exception as e:
        click.echo(f"Error deleting department: {e}", err=True)
    finally:
        session.close()

# --- Innovative Functionalities for Department ---

@department.command('assign-head')
@click.argument('department_id', type=int)
@click.argument('doctor_id', type=int)
def assign_head_doctor_command(department_id, doctor_id):
    """Assigns a specific doctor as the head of a department."""
    session = next(get_db())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return
        
        # The assign_head_doctor instance method handles doctor existence check
        dept.assign_head_doctor(session, doctor_id)
        click.echo(f"Doctor ID {doctor_id} assigned as head of Department '{dept.name}'.")
    except ValueError as e: # Catch ValueError from assign_head_doctor if doctor not found
        click.echo(f"Error assigning head doctor: {e}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
    finally:
        session.close()

@department.command('unassign-head')
@click.argument('department_id', type=int)
def unassign_head_doctor_command(department_id):
    """Removes the head doctor from a department."""
    session = next(get_db())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return
        
        if not dept.head_doctor:
            click.echo(f"Department '{dept.name}' (ID: {dept.id}) has no head doctor assigned.", err=True)
            return

        dept.unassign_head_doctor(session)
        click.echo(f"Head doctor unassigned from Department '{dept.name}'.")
    except Exception as e:
        click.echo(f"Error unassigning head doctor: {e}", err=True)
    finally:
        session.close()

@department.command('staff-list') # Renamed from 'staff' to avoid potential conflicts
@click.argument('department_id', type=int)
def list_department_staff(department_id):
    """Lists all doctors (staff) belonging to a specific department."""
    session = next(get_db())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return

        doctors_in_dept = dept.doctors # Accessing the relationship
        if not doctors_in_dept:
            click.echo(f"No doctors found in Department '{dept.name}'.")
            return
        
        click.echo(f"--- Doctors in Department '{dept.name}' (ID: {dept.id}) ---")
        for doctor in doctors_in_dept:
            click.echo(f"ID: {doctor.id}, Name: {doctor.name}, Specialization: {doctor.specialization}")
        click.echo("-------------------------------------------------")
    except Exception as e:
        click.echo(f"Error listing staff for department: {e}", err=True)
    finally:
        session.close()

# --- Main entry point for the CLI ---
if __name__ == '__main__':
    cli()