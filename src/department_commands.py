import click
from src.database import get_db_session # Import the session helper
from src.models import Department, Doctor # Import Department and Doctor models

@click.group()
def department():
    """Manages hospital departments."""
    pass

@department.command('add')
@click.option('--name', required=True, help="Name of the department.")
@click.option('--specialty', help="Primary specialty of the department (e.g., 'Cardiology').") # New option
@click.option('--head-doctor-id', type=int, help="ID of the doctor to assign as head (optional).")
def add_department(name, specialty, head_doctor_id): # Updated signature
    """Adds a new department."""
    session = next(get_db_session())
    try:
        if head_doctor_id:
            doctor = Doctor.find_by_id(session, head_doctor_id)
            if not doctor:
                click.echo(f"Error: Doctor with ID {head_doctor_id} not found. Department not added.", err=True)
                return

        dept = Department.create(session, name=name, specialty=specialty, head_doctor_id=head_doctor_id) # Pass specialty
        click.echo(f"Department '{dept.name}' (ID: {dept.id}) added successfully.")
    except Exception as e:
        click.echo(f"Error adding department: {e}", err=True)
    finally:
        session.close()

@department.command('list')
def list_departments():
    """Lists all departments."""
    session = next(get_db_session())
    try:
        departments = Department.get_all(session)
        if not departments:
            click.echo("No departments found.")
            return

        click.echo("--- Departments ---")
        for dept in departments:
            head_name = dept.head_doctor.name if dept.head_doctor else "None"
            # Display the new specialty column
            dept_specialty = dept.specialty if dept.specialty else "None"
            click.echo(f"ID: {dept.id}, Name: {dept.name}, Specialty: {dept_specialty}, Head: {head_name}")
        click.echo("----*-------*--------")
    except Exception as e:
        click.echo(f"Error listing departments: {e}", err=True)
    finally:
        session.close()

@department.command('show')
@click.argument('department_id', type=int)
def show_department(department_id):
    """Shows details for a specific department, including staff."""
    session = next(get_db_session())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return

        head_name = dept.head_doctor.name if dept.head_doctor else "None"
        staff_count = dept.get_staff_count()
        dept_specialty = dept.specialty if dept.specialty else "None" # Display specialty

        click.echo(f"--- Department Details (ID: {dept.id}) ---")
        click.echo(f"Name: {dept.name}")
        click.echo(f"Specialty: {dept_specialty}") # Display specialty
        click.echo(f"Head Doctor: {head_name}")
        click.echo(f"Number of Doctors: {staff_count}")
        
        if dept.doctors:
            click.echo("Doctors in this Department:")
            for doctor in dept.doctors:
                click.echo(f"  - ID: {doctor.id}, Name: {doctor.name}, Specialization: {doctor.specialization}")
        else:
            click.echo("No doctors assigned to this department.")
        click.echo("------*-----*-----*-----*--------*-------")
    except Exception as e:
        click.echo(f"Error showing department: {e}", err=True)
    finally:
        session.close()

@department.command('update')
@click.argument('department_id', type=int)
@click.option('--name', help="New name for the department.")
@click.option('--specialty', help="New primary specialty for the department.") # New option
@click.option('--head-doctor-id', type=int, help="New head doctor ID for the department.")
def update_department(department_id, name, specialty, head_doctor_id): # Updated signature
    """Updates an existing department's name, specialty, or head doctor."""
    session = next(get_db_session())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return

        update_kwargs = {}
        if name is not None:
            update_kwargs['name'] = name
        if specialty is not None: # Handle specialty update
            update_kwargs['specialty'] = specialty
        if head_doctor_id is not None:
            doctor = Doctor.find_by_id(session, head_doctor_id)
            if not doctor:
                click.echo(f"Error: Doctor with ID {head_doctor_id} not found. Department not updated.", err=True)
                return
            update_kwargs['head_doctor_id'] = head_doctor_id

        if not update_kwargs:
            click.echo("No update parameters provided.", err=True)
            return

        dept.update_info(session, **update_kwargs)
        click.echo(f"Department '{dept.name}' (ID: {dept.id}) updated successfully.")
    except Exception as e:
        click.echo(f"Error updating department: {e}", err=True)
    finally:
        session.close()

@department.command('delete')
@click.argument('department_id', type=int)
def delete_department(department_id):
    """Deletes a department."""
    session = next(get_db_session())
    try:
        if Department.delete_by_id(session, department_id):
            click.echo(f"Department with ID {department_id} deleted successfully.")
        else:
            click.echo(f"Department with ID {department_id} not found.", err=True)
    except Exception as e:
        click.echo(f"Error deleting department: {e}", err=True)
    finally:
        session.close()

# Department Functionalities 

@department.command('assign-head')
@click.argument('department_id', type=int)
@click.argument('doctor_id', type=int)
def assign_head_doctor_command(department_id, doctor_id):
    """Assigns a specific doctor as the head of a department."""
    session = next(get_db_session())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return
        
        dept.assign_head_doctor(session, doctor_id)
        click.echo(f"Doctor ID {doctor_id} assigned as head of Department '{dept.name}'.")
    except ValueError as e:
        click.echo(f"Error assigning head doctor: {e}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
    finally:
        session.close()

@department.command('unassign-head')
@click.argument('department_id', type=int)
def unassign_head_doctor_command(department_id):
    """Removes the head doctor from a department."""
    session = next(get_db_session())
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

@department.command('staff-list')
@click.argument('department_id', type=int)
def list_department_staff(department_id):
    """Lists all doctors (staff) belonging to a specific department."""
    session = next(get_db_session())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return

        doctors_in_dept = dept.doctors
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

# --- New Innovative Department Commands based on your additions ---

@department.command('assign-dept-specialty')
@click.argument('department_id', type=int)
@click.argument('specialty_name', type=str)
def assign_department_specialty_command(department_id, specialty_name):
    """Assigns a primary specialty to a department."""
    session = next(get_db_session())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return
        
        dept.assign_specialty(session, specialty_name) # Call your new instance method
        click.echo(f"Specialty '{specialty_name}' assigned to Department '{dept.name}'.")
    except Exception as e:
        click.echo(f"Error assigning department specialty: {e}", err=True)
    finally:
        session.close()

@department.command('list-dept-specialty-doctors')
@click.argument('department_id', type=int)
def list_department_specialty_doctors_command(department_id):
    """
    Lists doctors in a department who match the department's own assigned specialty.
    """
    session = next(get_db_session())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            click.echo(f"Department with ID {department_id} not found.", err=True)
            return
        
        if not dept.specialty:
            click.echo(f"Department '{dept.name}' has no primary specialty assigned to filter doctors by.", err=True)
            return

        matching_doctors = dept.specialty_doctors(session) # Call your new instance method

        if not matching_doctors:
            click.echo(f"No doctors found in Department '{dept.name}' with specialty '{dept.specialty}'.")
            return
        
        click.echo(f"--- Doctors in Department '{dept.name}' with specialty '{dept.specialty}' ---")
        for doctor in matching_doctors:
            click.echo(f"ID: {doctor.id}, Name: {doctor.name}, Specialization: {doctor.specialization}")
        click.echo("----*----*--------*------*------*---------*---------*------------")
    except Exception as e:
        click.echo(f"Error listing specialty doctors for department: {e}", err=True)
    finally:
        session.close()