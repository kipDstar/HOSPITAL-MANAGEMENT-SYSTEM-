# src/cli.py
import argparse
from datetime import date, datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Import your database session helper and models
from src.database import Base, engine, get_db
from src.models import Department, Doctor, Patient, InPatient, OutPatient, PatientType, Appointment, MedicalRecord

# --- Database Initialization Commands ---

def create_tables_command():
    """Creates all database tables."""
    print("Attempting to create tables...")
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully!")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")

def seed_db_command():
    """Seeds the database with initial data."""
    print("--- Seeding Database ---")
    session = next(get_db())

    try:
        print("Clearing existing data...")
        from sqlalchemy import delete
        session.execute(delete(MedicalRecord))
        session.execute(delete(Appointment))
        session.execute(delete(InPatient))
        session.execute(delete(OutPatient))
        session.execute(delete(Patient))
        session.execute(delete(Doctor))
        session.execute(delete(Department))
        session.commit()
        print("Existing data cleared.")

        # --- 1. Create Departments ---
        print("Creating Departments...")
        dept1 = Department(name="Cardiology", specialty="Cardiac Surgery")
        dept2 = Department(name="Pediatrics", specialty="Neonatology")
        dept3 = Department(name="General Surgery", specialty="Emergency Surgery")
        dept4 = Department(name="Dentistry", specialty="Orthodontics")
        session.add_all([dept1, dept2, dept3, dept4])
        session.commit()
        print("Departments created.")

        # --- 2. Create Doctors ---
        print("Creating Doctors...")
        doctor1 = Doctor(name="Dr. Jane Smith", specialization="Cardiologist", department=dept1, contact_info="jane.s@example.com")
        doctor2 = Doctor(name="Dr. John Doe", specialization="Pediatrician", department=dept2, contact_info="john.d@example.com")
        doctor3 = Doctor(name="Dr. Emily White", specialization="Surgeon", department=dept3, contact_info="emily.w@example.com")
        doctor4 = Doctor(name="Dr. Michael Green", specialization="General Practitioner", department=dept1, contact_info="michael.g@example.com")
        doctor5 = Doctor(name="Dr. Sarah Brown", specialization="Orthodontist", department=dept4, contact_info="sarah.b@example.com")
        session.add_all([doctor1, doctor2, doctor3, doctor4, doctor5])
        session.commit()
        print("Doctors created.")

        # --- Set Head Doctors (Requires doctors to exist) ---
        dept1.head_doctor = doctor1
        dept2.head_doctor = doctor2
        dept3.head_doctor = doctor3
        dept4.head_doctor = doctor5
        session.add_all([dept1, dept2, dept3, dept4])
        session.commit()
        print("Head doctors assigned.")

        # --- 3. Create Patients (InPatient and OutPatient) ---
        print("Creating Patients...")
        patient1 = InPatient(
            name="Alice Johnson",
            date_of_birth=date(1985, 3, 10),
            contact_info="alice@example.com",
            admission_date=date(2023, 10, 1),
            room_number="101A",
            assigned_doctor=doctor1,
            assigned_department=dept1
        )
        patient2 = OutPatient(
            name="Bob Williams",
            date_of_birth=date(1990, 7, 25),
            contact_info="bob@example.com",
            last_visit_date=date(2024, 1, 15),
            assigned_doctor=doctor2,
            assigned_department=dept2
        )
        patient3 = InPatient(
            name="Carol Davis",
            date_of_birth=date(1970, 1, 1),
            contact_info="carol@example.com",
            admission_date=date(2024, 1, 10),
            room_number="203B",
            assigned_doctor=doctor3,
            assigned_department=dept3
        )
        patient4 = OutPatient(
            name="David Brown",
            date_of_birth=date(2000, 5, 20),
            contact_info="david@example.com",
            last_visit_date=date(2024, 2, 28),
            assigned_doctor=doctor4,
            assigned_department=dept1
        )
        patient5 = OutPatient(
            name="Eve Rhee",
            date_of_birth=date(1995, 11, 12),
            contact_info="eve@example.com",
            last_visit_date=date(2024, 3, 5),
            assigned_doctor=doctor5,
            assigned_department=dept4
        )
        session.add_all([patient1, patient2, patient3, patient4, patient5])
        session.commit()
        print("Patients created.")

        # --- 4. Create Appointments ---
        print("Creating Appointments...")
        today = date.today()
        appointment1 = Appointment(patient=patient1, doctor=doctor1, appointment_datetime=datetime.combine(today, datetime.min.time().replace(hour=10, minute=0)), reason="Routine check-up")
        appointment2 = Appointment(patient=patient2, doctor=doctor2, appointment_datetime=datetime.combine(today, datetime.min.time().replace(hour=11, minute=30)), reason="Child flu symptoms")
        appointment3 = Appointment(patient=patient3, doctor=doctor3, appointment_datetime=datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=9, minute=0)), reason="Pre-surgery consultation")
        appointment4 = Appointment(patient=patient4, doctor=doctor4, appointment_datetime=datetime.combine(today, datetime.min.time().replace(hour=14, minute=0)), reason="Follow-up")
        appointment5 = Appointment(patient=patient5, doctor=doctor5, appointment_datetime=datetime.combine(today + timedelta(days=2), datetime.min.time().replace(hour=10, minute=0)), reason="Orthodontic Consultation")
        session.add_all([appointment1, appointment2, appointment3, appointment4, appointment5])
        session.commit()
        print("Appointments created.")

        # --- 5. Create Medical Records ---
        print("Creating Medical Records...")
        record1 = MedicalRecord(patient=patient1, doctor=doctor1, record_date=date(2023, 10, 1), diagnosis="Hypertension", treatment="Medication adjustment")
        record2 = MedicalRecord(patient=patient2, doctor=doctor2, record_date=date(2023, 10, 5), diagnosis="Common Cold", treatment="Rest and fluids")
        record3 = MedicalRecord(patient=patient1, doctor=doctor4, record_date=date(2024, 1, 20), diagnosis="Chest Pain", treatment="ECG and stress test ordered")
        record4 = MedicalRecord(patient=patient3, doctor=doctor3, record_date=date(2024, 1, 10), diagnosis="Appendicitis", treatment="Scheduled for appendectomy")
        record5 = MedicalRecord(patient=patient5, doctor=doctor5, record_date=date(2024, 3, 5), diagnosis="Dental Malocclusion", treatment="Braces treatment plan discussed")
        session.add_all([record1, record2, record3, record4, record5])
        session.commit()
        print("Medical records created.")

        print("--- Database Seeding Complete! ---")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"An error occurred during seeding: {e}")
    finally:
        session.close()

# --- Helper for printing objects ---
def print_object_details(obj, prefix=""):
    if obj:
        print(f"{prefix}ID: {obj.id}")
        if hasattr(obj, 'name'): print(f"{prefix}Name: {obj.name}")
        if hasattr(obj, 'specialty'): print(f"{prefix}Specialty: {obj.specialty or 'N/A'}")
        if hasattr(obj, 'specialization'): print(f"{prefix}Specialization: {obj.specialization or 'N/A'}")
        if hasattr(obj, 'contact_info'): print(f"{prefix}Contact: {obj.contact_info or 'N/A'}")
        if hasattr(obj, 'date_of_birth'): print(f"{prefix}DOB: {obj.date_of_birth.isoformat()}")
        if hasattr(obj, 'patient_type'): print(f"{prefix}Type: {obj.patient_type.value}")
        if hasattr(obj, 'room_number'): print(f"{prefix}Room: {obj.room_number or 'N/A'}")
        if hasattr(obj, 'admission_date'): print(f"{prefix}Admission: {obj.admission_date.isoformat() if obj.admission_date else 'N/A'}")
        if hasattr(obj, 'discharge_date'): print(f"{prefix}Discharge: {obj.discharge_date.isoformat() if obj.discharge_date else 'N/A'}")
        if hasattr(obj, 'last_visit_date'): print(f"{prefix}Last Visit: {obj.last_visit_date.isoformat() if obj.last_visit_date else 'N/A'}")
        if hasattr(obj, 'head_doctor') and obj.head_doctor: print(f"{prefix}Head Doctor: {obj.head_doctor.name}")
        if hasattr(obj, 'department') and obj.department: print(f"{prefix}Works in Dept: {obj.department.name}")
        if hasattr(obj, 'assigned_doctor') and obj.assigned_doctor: print(f"{prefix}Assigned Doctor: {obj.assigned_doctor.name}")
        if hasattr(obj, 'assigned_department') and obj.assigned_department: print(f"{prefix}Assigned Dept: {obj.assigned_department.name}")
    else:
        print(f"{prefix}Not found.")

# --- Department CLI Commands ---

def list_departments_command():
    session = next(get_db())
    try:
        departments = Department.get_all(session)
        if not departments:
            print("No departments found.")
            return
        print("\n--- All Departments ---")
        for dept in departments:
            print(f"Department ID: {dept.id}, Name: {dept.name}, Specialty: {dept.specialty or 'N/A'}")
            print(f"  Head Doctor: {dept.head_doctor.name if dept.head_doctor else 'Unassigned'}")
            print(f"  Doctors in Dept: {len(dept.doctors_in_department)}")
            print(f"  Patients Assigned: {len(dept.patients_assigned)}")
            print("-" * 30)
    finally:
        session.close()

def add_department_command(args):
    session = next(get_db())
    try:
        head_doctor = None
        if args.head_doctor_id:
            head_doctor = Doctor.get_by_id(session, args.head_doctor_id)
            if not head_doctor:
                print(f"Error: Doctor with ID {args.head_doctor_id} not found.")
                return

        new_dept = Department(name=args.name, specialty=args.specialty, head_doctor=head_doctor)
        new_dept.save(session)
        print(f"Department '{new_dept.name}' (ID: {new_dept.id}) added successfully.")
    except ValueError as e:
        print(f"Error: {e}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

def update_department_command(args):
    session = next(get_db())
    try:
        dept = Department.get_by_id(session, args.id)
        if not dept:
            print(f"Error: Department with ID {args.id} not found.")
            return

        if args.name:
            dept.name = args.name
        if args.specialty:
            dept.specialty = args.specialty
        if args.head_doctor_id is not None: # Allow setting to None
            head_doctor = None
            if args.head_doctor_id:
                head_doctor = Doctor.get_by_id(session, args.head_doctor_id)
                if not head_doctor:
                    print(f"Error: Doctor with ID {args.head_doctor_id} not found.")
                    return
            dept.head_doctor = head_doctor # Set relationship directly
        
        dept.save(session)
        print(f"Department '{dept.name}' (ID: {dept.id}) updated successfully.")
    except ValueError as e:
        print(f"Error: {e}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

def delete_department_command(args):
    session = next(get_db())
    try:
        dept = Department.get_by_id(session, args.id)
        if not dept:
            print(f"Error: Department with ID {args.id} not found.")
            return
        
        dept.delete(session)
        print(f"Department '{dept.name}' (ID: {dept.id}) deleted successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

# --- Doctor CLI Commands ---

def list_doctors_command():
    session = next(get_db())
    try:
        doctors = Doctor.get_all(session)
        if not doctors:
            print("No doctors found.")
            return
        print("\n--- All Doctors ---")
        for doc in doctors:
            print(f"Doctor ID: {doc.id}, Name: {doc.name}, Specialization: {doc.specialization or 'N/A'}")
            print(f"  Works in Dept: {doc.department.name if doc.department else 'Unassigned'}")
            print(f"  Heads: {len(doc.departments_headed)} Departments")
            print(f"  Assigned Patients: {len(doc.patients_assigned)}")
            print("-" * 30)
    finally:
        session.close()

def add_doctor_command(args):
    session = next(get_db())
    try:
        department = None
        if args.department_id:
            department = Department.get_by_id(session, args.department_id)
            if not department:
                print(f"Error: Department with ID {args.department_id} not found.")
                return

        new_doc = Doctor(name=args.name, specialization=args.specialization, contact_info=args.contact_info, department=department)
        new_doc.save(session)
        print(f"Doctor '{new_doc.name}' (ID: {new_doc.id}) added successfully.")
    except ValueError as e:
        print(f"Error: {e}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

def update_doctor_command(args):
    session = next(get_db())
    try:
        doc = Doctor.get_by_id(session, args.id)
        if not doc:
            print(f"Error: Doctor with ID {args.id} not found.")
            return

        if args.name:
            doc.name = args.name
        if args.specialization:
            doc.specialization = args.specialization
        if args.contact_info:
            doc.contact_info = args.contact_info
        if args.department_id is not None: # Allow setting to None
            department = None
            if args.department_id:
                department = Department.get_by_id(session, args.department_id)
                if not department:
                    print(f"Error: Department with ID {args.department_id} not found.")
                    return
            doc.department = department # Set relationship directly
        
        doc.save(session)
        print(f"Doctor '{doc.name}' (ID: {doc.id}) updated successfully.")
    except ValueError as e:
        print(f"Error: {e}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

def delete_doctor_command(args):
    session = next(get_db())
    try:
        doc = Doctor.get_by_id(session, args.id)
        if not doc:
            print(f"Error: Doctor with ID {args.id} not found.")
            return
        
        doc.delete(session)
        print(f"Doctor '{doc.name}' (ID: {doc.id}) deleted successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

# --- Patient CLI Commands ---

def list_patients_command():
    session = next(get_db())
    try:
        patients = Patient.get_all(session)
        if not patients:
            print("No patients found.")
            return
        print("\n--- All Patients ---")
        for p in patients:
            print(f"Patient ID: {p.id}, Name: {p.name}, Type: {p.patient_type.value}, DOB: {p.date_of_birth}")
            print(f"  Contact: {p.contact_info or 'N/A'}")
            if p.patient_type == PatientType.INPATIENT:
                print(f"  Room: {p.room_number or 'N/A'}, Admission: {p.admission_date.isoformat() if p.admission_date else 'N/A'}, Discharge: {p.discharge_date.isoformat() if p.discharge_date else 'N/A'}")
            elif p.patient_type == PatientType.OUTPATIENT:
                print(f"  Last Visit: {p.last_visit_date.isoformat() if p.last_visit_date else 'N/A'}")
            print(f"  Assigned Doctor: {p.assigned_doctor.name if p.assigned_doctor else 'Unassigned'}")
            print(f"  Assigned Department: {p.assigned_department.name if p.assigned_department else 'Unassigned'}")
            print("-" * 30)
    finally:
        session.close()

def add_patient_command(args):
    session = next(get_db())
    try:
        dob = date.fromisoformat(args.date_of_birth)
        patient_type = PatientType(args.patient_type)

        assigned_doctor = None
        if args.assigned_doctor_id:
            assigned_doctor = Doctor.get_by_id(session, args.assigned_doctor_id)
            if not assigned_doctor:
                print(f"Error: Assigned Doctor with ID {args.assigned_doctor_id} not found.")
                return

        assigned_department = None
        if args.assigned_department_id:
            assigned_department = Department.get_by_id(session, args.assigned_department_id)
            if not assigned_department:
                print(f"Error: Assigned Department with ID {args.assigned_department_id} not found.")
                return

        patient_kwargs = {
            "name": args.name,
            "date_of_birth": dob,
            "contact_info": args.contact_info,
            "assigned_doctor": assigned_doctor,
            "assigned_department": assigned_department,
        }

        if patient_type == PatientType.INPATIENT:
            if not args.room_number:
                print("Error: Room number is required for inpatient.")
                return
            admission_date = date.fromisoformat(args.admission_date) if args.admission_date else date.today()
            discharge_date = date.fromisoformat(args.discharge_date) if args.discharge_date else None
            new_patient = InPatient(
                room_number=args.room_number,
                admission_date=admission_date,
                discharge_date=discharge_date,
                **patient_kwargs
            )
        elif patient_type == PatientType.OUTPATIENT:
            last_visit_date = date.fromisoformat(args.last_visit_date) if args.last_visit_date else date.today()
            new_patient = OutPatient(
                last_visit_date=last_visit_date,
                **patient_kwargs
            )
        else:
            print("Error: Invalid patient type.")
            return

        new_patient.save(session)
        print(f"Patient '{new_patient.name}' (ID: {new_patient.id}, Type: {new_patient.patient_type.value}) added successfully.")
    except ValueError as e:
        print(f"Error: Invalid input or data: {e}. Ensure dates are YYYY-MM-DD.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

def update_patient_command(args):
    session = next(get_db())
    try:
        patient = Patient.get_by_id(session, args.id)
        if not patient:
            print(f"Error: Patient with ID {args.id} not found.")
            return

        if args.name: patient.name = args.name
        if args.date_of_birth: patient.date_of_birth = date.fromisoformat(args.date_of_birth)
        if args.contact_info: patient.contact_info = args.contact_info

        if args.assigned_doctor_id is not None:
            assigned_doctor = None
            if args.assigned_doctor_id:
                assigned_doctor = Doctor.get_by_id(session, args.assigned_doctor_id)
                if not assigned_doctor:
                    print(f"Error: Assigned Doctor with ID {args.assigned_doctor_id} not found.")
                    return
            patient.assigned_doctor = assigned_doctor
        
        if args.assigned_department_id is not None:
            assigned_department = None
            if args.assigned_department_id:
                assigned_department = Department.get_by_id(session, args.assigned_department_id)
                if not assigned_department:
                    print(f"Error: Assigned Department with ID {args.assigned_department_id} not found.")
                    return
            patient.assigned_department = assigned_department

        if patient.patient_type == PatientType.INPATIENT:
            if args.room_number: patient.room_number = args.room_number
            if args.admission_date: patient.admission_date = date.fromisoformat(args.admission_date)
            if args.discharge_date: patient.discharge_date = date.fromisoformat(args.discharge_date)
        elif patient.patient_type == PatientType.OUTPATIENT:
            if args.last_visit_date: patient.last_visit_date = date.fromisoformat(args.last_visit_date)
        
        patient.save(session)
        print(f"Patient '{patient.name}' (ID: {patient.id}) updated successfully.")
    except ValueError as e:
        print(f"Error: Invalid input or data: {e}. Ensure dates are YYYY-MM-DD.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()

def delete_patient_command(args):
    session = next(get_db())
    try:
        patient = Patient.get_by_id(session, args.id)
        if not patient:
            print(f"Error: Patient with ID {args.id} not found.")
            return
        
        patient.delete(session)
        print(f"Patient '{patient.name}' (ID: {patient.id}) deleted successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()


# --- Main Parser Setup ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hospital Management System CLI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Global Commands ---
    create_tables_parser = subparsers.add_parser("createtables", help="Create database tables")
    create_tables_parser.set_defaults(func=create_tables_command)

    seed_db_parser = subparsers.add_parser("seed", help="Seed the database with initial data")
    seed_db_parser.set_defaults(func=seed_db_command)

    # --- Department Subcommands ---
    dept_parser = subparsers.add_parser("department", help="Manage departments")
    dept_subparsers = dept_parser.add_subparsers(dest="dept_command", help="Department commands")

    # Department List
    dept_list_parser = dept_subparsers.add_parser("list", help="List all departments")
    dept_list_parser.set_defaults(func=list_departments_command)

    # Department Add
    dept_add_parser = dept_subparsers.add_parser("add", help="Add a new department")
    dept_add_parser.add_argument("--name", required=True, help="Name of the department")
    dept_add_parser.add_argument("--specialty", help="Specialty of the department")
    dept_add_parser.add_argument("--head-doctor-id", type=int, help="ID of the head doctor (optional)")
    dept_add_parser.set_defaults(func=add_department_command)

    # Department Update
    dept_update_parser = dept_subparsers.add_parser("update", help="Update an existing department")
    dept_update_parser.add_argument("id", type=int, help="ID of the department to update")
    dept_update_parser.add_argument("--name", help="New name of the department")
    dept_update_parser.add_argument("--specialty", help="New specialty of the department")
    dept_update_parser.add_argument("--head-doctor-id", type=int, help="New ID of the head doctor (use 0 or 'None' to unassign)")
    dept_update_parser.set_defaults(func=update_department_command)

    # Department Delete
    dept_delete_parser = dept_subparsers.add_parser("delete", help="Delete a department")
    dept_delete_parser.add_argument("id", type=int, required=True, help="ID of the department to delete")
    dept_delete_parser.set_defaults(func=delete_department_command)

    # --- Doctor Subcommands ---
    doctor_parser = subparsers.add_parser("doctor", help="Manage doctors")
    doctor_subparsers = doctor_parser.add_subparsers(dest="doctor_command", help="Doctor commands")

    # Doctor List
    doctor_list_parser = doctor_subparsers.add_parser("list", help="List all doctors")
    doctor_list_parser.set_defaults(func=list_doctors_command)

    # Doctor Add
    doctor_add_parser = doctor_subparsers.add_parser("add", help="Add a new doctor")
    doctor_add_parser.add_argument("--name", required=True, help="Name of the doctor")
    doctor_add_parser.add_argument("--specialization", help="Specialization of the doctor")
    doctor_add_parser.add_argument("--contact-info", help="Contact information of the doctor")
    doctor_add_parser.add_argument("--department-id", type=int, help="ID of the department the doctor works in")
    doctor_add_parser.set_defaults(func=add_doctor_command)

    # Doctor Update
    doctor_update_parser = doctor_subparsers.add_parser("update", help="Update an existing doctor")
    doctor_update_parser.add_argument("id", type=int, help="ID of the doctor to update")
    doctor_update_parser.add_argument("--name", help="New name of the doctor")
    doctor_update_parser.add_argument("--specialization", help="New specialization of the doctor")
    doctor_update_parser.add_argument("--contact-info", help="New contact information of the doctor")
    doctor_update_parser.add_argument("--department-id", type=int, help="New ID of the department the doctor works in (use 0 or 'None' to unassign)")
    doctor_update_parser.set_defaults(func=update_doctor_command)

    # Doctor Delete
    doctor_delete_parser = doctor_subparsers.add_parser("delete", help="Delete a doctor")
    doctor_delete_parser.add_argument("id", type=int, required=True, help="ID of the doctor to delete")
    doctor_delete_parser.set_defaults(func=delete_doctor_command)

    # --- Patient Subcommands ---
    patient_parser = subparsers.add_parser("patient", help="Manage patients")
    patient_subparsers = patient_parser.add_subparsers(dest="patient_command", help="Patient commands")

    # Patient List
    patient_list_parser = patient_subparsers.add_parser("list", help="List all patients")
    patient_list_parser.set_defaults(func=list_patients_command)

    # Patient Add
    patient_add_parser = patient_subparsers.add_parser("add", help="Add a new patient")
    patient_add_parser.add_argument("--name", required=True, help="Name of the patient")
    patient_add_parser.add_argument("--date-of-birth", required=True, help="Patient's date of birth (YYYY-MM-DD)")
    patient_add_parser.add_argument("--contact-info", help="Patient's contact information")
    patient_add_parser.add_argument("--patient-type", choices=['inpatient', 'outpatient'], required=True, help="Type of patient (inpatient or outpatient)")
    patient_add_parser.add_argument("--assigned-doctor-id", type=int, help="ID of the assigned doctor (optional)")
    patient_add_parser.add_argument("--assigned-department-id", type=int, help="ID of the assigned department (optional)")
    # Inpatient specific
    patient_add_parser.add_argument("--room-number", help="Room number for inpatient")
    patient_add_parser.add_argument("--admission-date", help="Admission date for inpatient (YYYY-MM-DD, defaults to today)")
    patient_add_parser.add_argument("--discharge-date", help="Discharge date for inpatient (YYYY-MM-DD, optional)")
    # Outpatient specific
    patient_add_parser.add_argument("--last-visit-date", help="Last visit date for outpatient (YYYY-MM-DD, defaults to today)")
    patient_add_parser.set_defaults(func=add_patient_command)

    # Patient Update
    patient_update_parser = patient_subparsers.add_parser("update", help="Update an existing patient")
    patient_update_parser.add_argument("id", type=int, help="ID of the patient to update")
    patient_update_parser.add_argument("--name", help="New name of the patient")
    patient_update_parser.add_argument("--date-of-birth", help="New date of birth (YYYY-MM-DD)")
    patient_update_parser.add_argument("--contact-info", help="New contact information")
    patient_update_parser.add_argument("--assigned-doctor-id", type=int, help="New ID of the assigned doctor (use 0 or 'None' to unassign)")
    patient_update_parser.add_argument("--assigned-department-id", type=int, help="New ID of the assigned department (use 0 or 'None' to unassign)")
    # Inpatient specific
    patient_update_parser.add_argument("--room-number", help="New room number for inpatient")
    patient_update_parser.add_argument("--admission-date", help="New admission date for inpatient (YYYY-MM-DD)")
    patient_update_parser.add_argument("--discharge-date", help="New discharge date for inpatient (YYYY-MM-DD)")
    # Outpatient specific
    patient_update_parser.add_argument("--last-visit-date", help="New last visit date for outpatient (YYYY-MM-DD)")
    patient_update_parser.set_defaults(func=update_patient_command)

    # Patient Delete
    patient_delete_parser = patient_subparsers.add_parser("delete", help="Delete a patient")
    patient_delete_parser.add_argument("id", type=int, required=True, help="ID of the patient to delete")
    patient_delete_parser.set_defaults(func=delete_patient_command)

    # Parse arguments and run the selected function
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args) # Pass args to the function
    else:
        parser.print_help()

