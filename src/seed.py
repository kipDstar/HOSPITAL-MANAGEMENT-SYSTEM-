# This script is meant to seed the database with initial data.

# src/seed.py

from datetime import date, datetime, timedelta
from sqlalchemy.orm import sessionmaker
from src.database import engine, Base, get_db  # Import engine, Base, and the session helper
from src.models import Patient, InPatient, OutPatient, Doctor, Department, Appointment, MedicalRecord # Import all your models


def seed_database():
    """
    Populates the database with initial dummy data.
    """
    print("--- Seeding Database ---")

    # Get a database session
    # We use next(get_db_session()) to get the session object from our generator function.
    session = next(get_db())

    try:
        # Clear existing data (optional, but good for fresh seeds)
        # Be careful with this, It deletes all data.
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
        dept1 = Department(name="Cardiology", specialty="Cardiac Surgery") # Added specialty
        dept2 = Department(name="Pediatrics", specialty="Neonatology")    # Added specialty
        dept3 = Department(name="General Surgery") # This one remains without a direct specialty
        session.add_all([dept1, dept2, dept3])
        session.commit()
        print("Departments created.")

        # --- 2. Create Doctors ---
        print("Creating Doctors...")
        doctor1 = Doctor(name="Dr. Jane Smith", specialization="Cardiologist", department=dept1)
        doctor2 = Doctor(name="Dr. John Doe", specialization="Pediatrician", department=dept2)
        doctor3 = Doctor(name="Dr. Emily White", specialization="Surgeon", department=dept3)
        doctor4 = Doctor(name="Dr. Michael Green", specialization="General Practitioner", department=dept1) # Another doctor in Cardiology
        session.add_all([doctor1, doctor2, doctor3, doctor4])
        session.commit()
        print("Doctors created.")

        # --- Set Head Doctors (Requires doctors to exist) ---
        dept1.head_doctor = doctor1
        dept2.head_doctor = doctor2
        dept3.head_doctor = doctor3
        session.add_all([dept1, dept2, dept3]) # Add them back to session to update
        session.commit()
        print("Head doctors assigned.")

        # --- 3. Create Patients (InPatient and OutPatient) ---
        print("Creating Patients...")

        patient1 = InPatient(name="Alice Johnson", date_of_birth=date(1985, 3, 10), contact_info="alice@example.com", admission_date=date(2023, 10, 1), room_number="101A")
        patient2 = OutPatient(name="Bob Williams", date_of_birth=date(1990, 7, 25), contact_info="bob@example.com", last_visit_date=date(2024, 1, 15))
        patient3 = InPatient(name="Carol Davis", date_of_birth=date(1970, 1, 1), contact_info="carol@example.com", admission_date=date(2024, 1, 10), room_number="203B")
        patient4 = OutPatient(name="David Brown", date_of_birth=date(2000, 5, 20), contact_info="david@example.com", last_visit_date=date(2024, 2, 28))
        session.add_all([patient1, patient2, patient3, patient4])
        session.commit()
        print("Patients created.")

        # --- 4. Create Appointments ---
        print("Creating Appointments...")
        # Today's date for appointments
        today = date.today()
        # Ensure times are specific for demonstration
        appointment1 = Appointment(patient=patient1, doctor=doctor1, appointment_date=datetime.combine(today, datetime.min.time().replace(hour=10, minute=0)), reason="Routine check-up")
        appointment2 = Appointment(patient=patient2, doctor=doctor2, appointment_date=datetime.combine(today, datetime.min.time().replace(hour=11, minute=30)), reason="Child flu symptoms")
        appointment3 = Appointment(patient=patient3, doctor=doctor3, appointment_date=datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=9, minute=0)), reason="Pre-surgery consultation")
        appointment4 = Appointment(patient=patient4, doctor=doctor4, appointment_date=datetime.combine(today, datetime.min.time().replace(hour=14, minute=0)), reason="Follow-up")
        session.add_all([appointment1, appointment2, appointment3, appointment4])
        session.commit()
        print("Appointments created.")

        # --- 5. Create Medical Records ---
        print("Creating Medical Records...")
        record1 = MedicalRecord(patient=patient1, doctor=doctor1, record_date=date(2023, 10, 1), diagnosis="Hypertension", treatment="Medication adjustment")
        record2 = MedicalRecord(patient=patient2, doctor=doctor2, record_date=date(2023, 10, 5), diagnosis="Common Cold", treatment="Rest and fluids")
        record3 = MedicalRecord(patient=patient1, doctor=doctor4, record_date=date(2024, 1, 20), diagnosis="Chest Pain", treatment="ECG and stress test ordered")
        record4 = MedicalRecord(patient=patient3, doctor=doctor3, record_date=date(2024, 1, 10), diagnosis="Appendicitis", treatment="Scheduled for appendectomy")
        session.add_all([record1, record2, record3, record4])
        session.commit()
        print("Medical records created.")

        print("--- Database Seeding Complete! ---")

    except Exception as e:
        session.rollback() # Rollback changes if any error occurs
        print(f"An error occurred during seeding: {e}")
    finally:
        session.close() # Always close the session

# This block ensures seed_database() is called only when the script is run directly
if __name__ == "__main__":
    seed_database()