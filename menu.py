from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from datetime import datetime
from src.database import get_db
from src.models import Patient, InPatient, OutPatient, Doctor, Department, Appointment, MedicalRecord, PatientType, AppointmentStatus
import sys


def main_menu():
    while True:
        choice = inquirer.select(
            message="🏥 Hospital Management System - Main Menu 🏥",
            choices=[
                "🧑‍🤝‍🧑 Manage Patients",
                "👨‍⚕️ Manage Doctors",
                "🏢 Manage Departments",
                "📅 Manage Appointments",
                "📋 Manage Medical Records",
                "🚪 Exit"
            ],
        ).execute()

        if choice == "🧑‍🤝‍🧑 Manage Patients":
            patient_menu()
        elif choice == "👨‍⚕️ Manage Doctors":
            doctor_menu()
        elif choice == "🏢 Manage Departments":
            department_menu()
        elif choice == "📅 Manage Appointments":
            appointment_menu()
        elif choice == "📋 Manage Medical Records":
            medical_record_menu()
        else:
            print("👋 Goodbye!")
            sys.exit()


# ----------------- Patient Menu -------------------
def patient_menu():
    while True:
        choice = inquirer.select(
            message="🧑‍🤝‍🧑 Patient Management",
            choices=[
                "➕ Add Patient",
                "📜 List Patients",
                "✏️ Update Patient",
                "🗑️ Delete Patient",
                "🔙 Back to Main Menu"
            ],
        ).execute()

        if choice == "➕ Add Patient":
            add_patient()
        elif choice == "📜 List Patients":
            list_patients()
        elif choice == "✏️ Update Patient":
            update_patient()
        elif choice == "🗑️ Delete Patient":
            delete_patient()
        else:
            break


def add_patient():
    name = inquirer.text(message="🧑‍🤝‍🧑 Patient full name:").execute()
    dob = inquirer.text(message="🎂 Date of Birth (YYYY-MM-DD):").execute()
    contact = inquirer.text(message="📞 Contact Info:").execute()
    patient_type = inquirer.select(
        message="🏥 Patient Type",
        choices=["inpatient 🏨", "outpatient 🚶‍♂️"]
    ).execute()

    room = None
    admission = None
    discharge = None
    last_visit = None

    if patient_type.startswith("inpatient"):
        room = inquirer.number(message="🏨 Room Number:", min_allowed=1).execute()
        admission = inquirer.text(message="🗓️ Admission Date (YYYY-MM-DD):", default="").execute()
        discharge = inquirer.text(message="🗓️ Discharge Date (YYYY-MM-DD):", default="").execute()
    else:
        last_visit = inquirer.text(message="🗓️ Last Visit Date (YYYY-MM-DD):", default="").execute()

    db = next(get_db())
    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        if patient_type.startswith("inpatient"):
            patient = InPatient(
                name=name,
                date_of_birth=dob_date,
                contact_info=contact,
                patient_type=PatientType.INPATIENT,
                room_number=room,
                admission_date=datetime.strptime(admission, '%Y-%m-%d') if admission else None,
                discharge_date=datetime.strptime(discharge, '%Y-%m-%d') if discharge else None,
            )
        else:
            patient = OutPatient(
                name=name,
                date_of_birth=dob_date,
                contact_info=contact,
                patient_type=PatientType.OUTPATIENT,
                last_visit_date=datetime.strptime(last_visit, '%Y-%m-%d') if last_visit else None,
            )

        db.add(patient)
        db.commit()
        print(f"✅ {patient_type.split()[0].capitalize()} patient '{name}' added successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding patient: {e}")
    finally:
        db.close()


def list_patients():
    db = next(get_db())
    try:
        patients = db.query(Patient).all()
        if not patients:
            print("ℹ️ No patients found.")
            return
        for p in patients:
            print(f"ID: {p.id}, Name: {p.name}, Type: {p.patient_type.value}, DOB: {p.date_of_birth}")
    finally:
        db.close()


def update_patient():
    patient_id = inquirer.number(message="🆔 Enter Patient ID to update:", min_allowed=1).execute()
    name = inquirer.text(message="New name (leave blank to skip):", default="").execute()
    dob = inquirer.text(message="New DOB (YYYY-MM-DD) (leave blank to skip):", default="").execute()
    contact = inquirer.text(message="New contact info (leave blank to skip):", default="").execute()

    room = None
    admission = None
    discharge = None
    last_visit = None

    db = next(get_db())
    try:
        patient = db.get(Patient, patient_id)
        if not patient:
            print(f"❌ No patient with ID {patient_id} found.")
            return

        if name:
            patient.name = name
        if dob:
            patient.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
        if contact:
            patient.contact_info = contact

        if isinstance(patient, InPatient):
            room_input = inquirer.text(message="New room number (leave blank to skip):", default="").execute()
            room = int(room_input) if room_input.strip() != "" else None
            admission = inquirer.text(message="New admission date (YYYY-MM-DD) (leave blank to skip):", default="").execute()
            discharge = inquirer.text(message="New discharge date (YYYY-MM-DD) (leave blank to skip):", default="").execute()

            if room is not None:
                patient.room_number = room
            if admission:
                patient.admission_date = datetime.strptime(admission, '%Y-%m-%d')
            if discharge:
                patient.discharge_date = datetime.strptime(discharge, '%Y-%m-%d')
        else:
            last_visit = inquirer.text(message="New last visit date (YYYY-MM-DD) (leave blank to skip):", default="").execute()
            if last_visit:
                patient.last_visit_date = datetime.strptime(last_visit, '%Y-%m-%d')

        db.commit()
        print(f"✅ Patient ID {patient_id} updated successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating patient: {e}")
    finally:
        db.close()


def delete_patient():
    patient_id = inquirer.number(message="🆔 Enter Patient ID to delete:", min_allowed=1).execute()
    confirm = inquirer.confirm(message=f"⚠️ Are you sure you want to delete patient ID {patient_id}?", default=False).execute()
    if not confirm:
        print("❎ Delete cancelled.")
        return

    db = next(get_db())
    try:
        patient = db.get(Patient, patient_id)
        if not patient:
            print(f"❌ No patient with ID {patient_id} found.")
            return
        db.delete(patient)
        db.commit()
        print(f"🗑️ Patient ID {patient_id} deleted.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting patient: {e}")
    finally:
        db.close()


# ----------------- Doctor Menu -------------------
def doctor_menu():
    while True:
        choice = inquirer.select(
            message="👨‍⚕️ Doctor Management",
            choices=[
                "➕ Add Doctor 👨‍⚕️",
                "📜 List Doctors 👩‍⚕️",
                "✏️ Update Doctor 🩺",
                "🗑️ Delete Doctor 🚫",
                "🔙 Back to Main Menu"
            ],
        ).execute()

        if choice == "➕ Add Doctor 👨‍⚕️":
            add_doctor()
        elif choice == "📜 List Doctors 👩‍⚕️":
            list_doctors()
        elif choice == "✏️ Update Doctor 🩺":
            update_doctor()
        elif choice == "🗑️ Delete Doctor 🚫":
            delete_doctor()
        else:
            break


def add_doctor():
    name = inquirer.text(message="👨‍⚕️ Doctor full name:").execute()
    specialization = inquirer.text(message="🩺 Specialization:").execute()
    contact = inquirer.text(message="📞 Contact Info:").execute()

    db = next(get_db())
    try:
        departments = db.query(Department).all()
        if not departments:
            print("⚠️ No departments found. Please create a department first.")
            return

        dept_choices = [(f"{d.name} (ID {d.id})", d.id) for d in departments]
        department_id = inquirer.select(
            message="🏥 Select Department:",
            choices=dept_choices
        ).execute()

        doctor = Doctor(
            name=name,
            specialization=specialization,
            contact_info=contact,
            department_id=department_id
        )
        db.add(doctor)
        db.commit()
        print(f"✅ Doctor '{name}' added successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding doctor: {e}")
    finally:
        db.close()


def list_doctors():
    db = next(get_db())
    try:
        doctors = db.query(Doctor).all()
        if not doctors:
            print("ℹ️ No doctors found.")
            return
        for d in doctors:
            dept_name = d.department.name if d.department else "N/A"
            print(f"ID: {d.id}, Name: {d.name}, Specialization: {d.specialization}, Dept: {dept_name}")
    finally:
        db.close()


def update_doctor():
    doctor_id = inquirer.number(message="🆔 Enter Doctor ID to update:", min_allowed=1).execute()
    name = inquirer.text(message="New name (leave blank to skip):", default="").execute()
    specialization = inquirer.text(message="New specialization (leave blank to skip):", default="").execute()
    contact = inquirer.text(message="New contact info (leave blank to skip):", default="").execute()

    db = next(get_db())
    try:
        doctor = db.get(Doctor, doctor_id)
        if not doctor:
            print(f"❌ No doctor with ID {doctor_id} found.")
            return

        departments = db.query(Department).all()
        dept_choices = [(f"{d.name} (ID {d.id})", d.id) for d in departments]
        current_dept = doctor.department_id
        department_id = inquirer.select(
            message="🏥 Select new Department:",
            choices=dept_choices,
            default=current_dept
        ).execute()

        if name:
            doctor.name = name
        if specialization:
            doctor.specialization = specialization
        if contact:
            doctor.contact_info = contact
        doctor.department_id = department_id

        db.commit()
        print(f"✅ Doctor ID {doctor_id} updated successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating doctor: {e}")
    finally:
        db.close()


def delete_doctor():
    doctor_id = inquirer.number(message="🆔 Enter Doctor ID to delete:", min_allowed=1).execute()
    confirm = inquirer.confirm(message=f"⚠️ Are you sure you want to delete doctor ID {doctor_id}?", default=False).execute()
    if not confirm:
        print("❎ Delete cancelled.")
        return

    db = next(get_db())
    try:
        doctor = db.get(Doctor, doctor_id)
        if not doctor:
            print(f"❌ No doctor with ID {doctor_id} found.")
            return
        db.delete(doctor)
        db.commit()
        print(f"🗑️ Doctor ID {doctor_id} deleted.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting doctor: {e}")
    finally:
        db.close()
# ----------------- Department Menu -------------------


def department_menu():
    while True:
        choice = inquirer.select(
            message="🏥 Department Management Menu",
            choices=[
                "➕ Add Department",
                "📋 List Departments",
                "✏️ Update Department",
                "🗑️ Delete Department",
                "🔙 Back to Main Menu"
            ],
        ).execute()

        if choice == "➕ Add Department":
            add_department()
        elif choice == "📋 List Departments":
            list_departments()
        elif choice == "✏️ Update Department":
            update_department()
        elif choice == "🗑️ Delete Department":
            delete_department()
        else:
            break


def add_department():
    db = next(get_db())
    try:
        while True:
            name = inquirer.text(message="🏥 Enter department name:").execute()
            existing_department = db.query(Department).filter_by(name=name).first()
            if existing_department:
                print(f"❌ Department with name '{name}' already exists. Please choose a different name.")
            else:
                break

        specialty = inquirer.text(message="🩺 Enter specialty (optional):", default="").execute()

        doctors = db.query(Doctor).all()
        head_doctor_id = None

        if doctors:
            assign_head = inquirer.confirm(message="👨‍⚕️ Assign a Head Doctor?", default=False).execute()
            if assign_head:
                # Create a dictionary where keys are the display strings and values are the actual doctor IDs (integers)
                doctor_choices_map = {f"{doc.name} (ID: {doc.id})": doc.id for doc in doctors}

                # Inquirer.select returns the *key* (the string) that the user selected
                selected_doctor_display_string = inquirer.select(
                    message="Select Head Doctor:",
                    choices=list(doctor_choices_map.keys()) # Pass only the display strings as choices
                ).execute()

                # Use the selected display string to get the actual integer ID from our map
                head_doctor_id = doctor_choices_map[selected_doctor_display_string]

        print("DEBUG head_doctor_id before create:", head_doctor_id, type(head_doctor_id))

        department = Department.create(
            session=db,
            name=name,
            specialty=specialty or None,
            head_doctor_id=head_doctor_id
        )
        db.commit() # Commit the transaction

        print(f"✅ Department '{department.name}' added successfully.")
        if department.head_doctor:
            print(f"👑 Head Doctor: {department.head_doctor.name}")

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to add department due to data integrity issue: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        db.close()

def list_departments():
    db = next(get_db())
    try:
        departments = Department.get_all(db)
        if not departments:
            print("ℹ️ No departments available.")
            return
        print("\n📋 Departments:")
        for dept in departments:
            head_name = dept.head_doctor.name if dept.head_doctor else "None"
            print(f"ID: {dept.id} | Name: {dept.name} | Specialty: {dept.specialty or 'N/A'} | Head Doctor: {head_name}")
    finally:
        db.close()


def update_department():
    dept_id = inquirer.number(message="🆔 Enter Department ID to update:").execute()
    db = next(get_db())
    try:
        dept = Department.find_by_id(db, dept_id)
        if not dept:
            print(f"❌ Department with ID {dept_id} not found.")
            return

        name = inquirer.text(message="New name (leave blank to keep current):", default="").execute()
        specialty = inquirer.text(message="New specialty (leave blank to keep current):", default="").execute()

        change_head = inquirer.confirm(message="👑 Change Head Doctor?", default=False).execute()
        head_doctor_id = None
        if change_head:
            doctors = db.query(Doctor).all()
            if doctors:
                choices = [(f"{doc.name} (ID: {doc.id})", doc.id) for doc in doctors]
                head_doctor_id = inquirer.select(message="Select new Head Doctor:", choices=choices).execute()

        dept.update_info(
            session=db,
            name=name or None,
            specialty=specialty or None,
            head_doctor_id=head_doctor_id
        )
        print(f"✅ Department '{dept.name}' updated.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error updating department: {e}")
    finally:
        db.close()


def delete_department():
    dept_id = inquirer.number(message="🆔 Enter Department ID to delete:").execute()
    confirm = inquirer.confirm(
        message=f"⚠️ Are you sure you want to delete Department ID {dept_id}?",
        default=False
    ).execute()

    if not confirm:
        print("❎ Deletion cancelled.")
        return

    db = next(get_db())
    try:
        success = Department.delete_by_id(db, dept_id)
        if success:
            print(f"🗑️ Department ID {dept_id} deleted.")
        else:
            print(f"❌ Department ID {dept_id} not found.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting department: {e}")
    finally:
        db.close()

# ----------------- Medical Record Menu -------------------

def medical_record_menu():
    while True:
        choice = inquirer.select(
            message="🩺 Medical Records Management",
            choices=[
                "➕ Add Medical Record",
                "📜 List Medical Records",
                "✏️ Update Medical Record",
                "🗑️ Delete Medical Record",
                "🔙 Back to Main Menu"
            ],
        ).execute()

        if choice == "➕ Add Medical Record":
            add_medical_record()
        elif choice == "📜 List Medical Records":
            list_medical_records()
        elif choice == "✏️ Update Medical Record":
            update_medical_record()
        elif choice == "🗑️ Delete Medical Record":
            delete_medical_record()
        else:
            break

def add_medical_record():
    db = next(get_db())
    try:
        patient_id = inquirer.number(message="🆔 Patient ID:", min_allowed=1).execute()
        doctor_id = inquirer.number(message="🆔 Doctor ID:", min_allowed=1).execute()
        record_date_str = inquirer.text(
            message="📅 Record Date (YYYY-MM-DD) [leave blank for today]:",
            default=""
        ).execute()
        diagnosis = inquirer.text(message="📝 Diagnosis:").execute()
        treatment = inquirer.text(message="💊 Treatment:").execute()

        record_date_obj = datetime.today()
        if record_date_str:
            record_date_obj = datetime.strptime(record_date_str, '%Y-%m-%d').date()

        if not db.get(Patient, patient_id):
            print(f"❌ No patient with ID {patient_id} found.")
            return
        if not db.get(Doctor, doctor_id):
            print(f"❌ No doctor with ID {doctor_id} found.")
            return

        record = MedicalRecord(
            patient_id=patient_id,
            doctor_id=doctor_id,
            record_date=record_date_obj,
            diagnosis=diagnosis,
            treatment=treatment
        )
        db.add(record)
        db.commit()
        print("✅ Medical record added successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding record: {e}")
    finally:
        db.close()

def list_medical_records():
    db = next(get_db())
    try:
        records = db.query(MedicalRecord).all()
        if not records:
            print("ℹ️ No medical records found.")
            return
        for r in records:
            print(f"🩺 ID: {r.id}, Patient ID: {r.patient_id}, Doctor ID: {r.doctor_id}, "
                  f"Date: {r.record_date}, Diagnosis: {r.diagnosis}, Treatment: {r.treatment[:30]}...")
    finally:
        db.close()

def update_medical_record():
    db = next(get_db())
    try:
        record_id = inquirer.number(message="🆔 Enter Medical Record ID to update:", min_allowed=1).execute()
        record = db.get(MedicalRecord, record_id)
        if not record:
            print(f"❌ No medical record with ID {record_id} found.")
            return

        patient_id = inquirer.text(message="New Patient ID (leave blank to keep):", default="").execute()
        doctor_id = inquirer.text(message="New Doctor ID (leave blank to keep):", default="").execute()
        date_str = inquirer.text(message="New Record Date (YYYY-MM-DD, blank to keep):", default="").execute()
        diagnosis = inquirer.text(message="New Diagnosis (leave blank to keep):", default="").execute()
        treatment = inquirer.text(message="New Treatment (leave blank to keep):", default="").execute()

        if patient_id:
            if db.get(Patient, int(patient_id)):
                record.patient_id = int(patient_id)
            else:
                print(f"❌ No patient with ID {patient_id} found.")
                return

        if doctor_id:
            if db.get(Doctor, int(doctor_id)):
                record.doctor_id = int(doctor_id)
            else:
                print(f"❌ No doctor with ID {doctor_id} found.")
                return

        if date_str:
            record.record_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        if diagnosis:
            record.diagnosis = diagnosis

        if treatment:
            record.treatment = treatment

        db.commit()
        print(f"✅ Medical record ID {record_id} updated successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating record: {e}")
    finally:
        db.close()

def delete_medical_record():
    db = next(get_db())
    try:
        record_id = inquirer.number(message="🆔 Enter Medical Record ID to delete:", min_allowed=1).execute()
        confirm = inquirer.confirm(
            message=f"⚠️ Are you sure you want to delete medical record ID {record_id}?",
            default=False
        ).execute()
        if not confirm:
            print("❎ Delete cancelled.")
            return

        record = db.get(MedicalRecord, record_id)
        if not record:
            print(f"❌ No record with ID {record_id} found.")
            return

        db.delete(record)
        db.commit()
        print(f"🗑️ Medical record ID {record_id} deleted.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting record: {e}")
    finally:
        db.close()
# ----------------- Appointment Menu -------------------

def appointment_menu():
    while True:
        choice = inquirer.select(
            message="📅 Appointment Management",
            choices=[
                "➕ Add Appointment 📅",
                "📜 List Appointments",
                "✏️ Update Appointment",
                "🗑️ Delete Appointment",
                "🔙 Back to Main Menu"
            ],
        ).execute()

        if choice == "➕ Add Appointment 📅":
            add_appointment()
        elif choice == "📜 List Appointments":
            list_appointments()
        elif choice == "✏️ Update Appointment":
            update_appointment()
        elif choice == "🗑️ Delete Appointment":
            delete_appointment()
        else:
            break

def add_appointment():
    db = next(get_db())
    try:
        patient_id = inquirer.number(message="🆔 Patient ID:", min_allowed=1).execute()
        doctor_id = inquirer.number(message="🆔 Doctor ID:", min_allowed=1).execute()
        date_str = inquirer.text(message="🗓️ Appointment Date (YYYY-MM-DD):").execute()
        time_str = inquirer.text(message="⏰ Appointment Time (HH:MM, 24h):").execute()
        reason = inquirer.text(message="📝 Reason for Appointment:").execute()
        status = inquirer.select(
            message="📌 Status:",
            choices=[status.value for status in AppointmentStatus]
        ).execute()

        appointment_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')

        # Validate foreign keys
        if not db.get(Patient, patient_id):
            print(f"❌ No patient with ID {patient_id} found.")
            return
        if not db.get(Doctor, doctor_id):
            print(f"❌ No doctor with ID {doctor_id} found.")
            return

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_datetime,
            reason=reason,
            status=AppointmentStatus(status)
        )
        db.add(appointment)
        db.commit()
        print(f"✅ Appointment added successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding appointment: {e}")
    finally:
        db.close()

def list_appointments():
    db = next(get_db())
    try:
        appointments = db.query(Appointment).all()
        if not appointments:
            print("ℹ️ No appointments found.")
            return
        for a in appointments:
            print(f"ID: {a.id}, Patient ID: {a.patient_id}, Doctor ID: {a.doctor_id}, "
                  f"Date: {a.appointment_datetime}, Reason: {a.reason}, Status: {a.status.value}")
    finally:
        db.close()

def update_appointment():
    db = next(get_db())
    try:
        appointment_id = inquirer.number(message="🆔 Appointment ID to update:", min_allowed=1).execute()
        appointment = db.get(Appointment, appointment_id)
        if not appointment:
            print(f"❌ No appointment with ID {appointment_id} found.")
            return

        patient_id = inquirer.text(message="New Patient ID (leave blank to keep):", default="").execute()
        doctor_id = inquirer.text(message="New Doctor ID (leave blank to keep):", default="").execute()
        date_str = inquirer.text(message="New Date (YYYY-MM-DD, leave blank to keep):", default="").execute()
        time_str = inquirer.text(message="New Time (HH:MM, 24h, leave blank to keep):", default="").execute()
        reason = inquirer.text(message="New Reason (leave blank to keep):", default="").execute()
        status = inquirer.select(
            message="New Status:",
            choices=[status.value for status in AppointmentStatus],
            default=appointment.status.value
        ).execute()

        if patient_id:
            if db.get(Patient, int(patient_id)):
                appointment.patient_id = int(patient_id)
            else:
                print(f"❌ No patient with ID {patient_id}")
                return

        if doctor_id:
            if db.get(Doctor, int(doctor_id)):
                appointment.doctor_id = int(doctor_id)
            else:
                print(f"❌ No doctor with ID {doctor_id}")
                return

        if date_str and time_str:
            appointment.appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        if reason:
            appointment.reason = reason

        appointment.status = AppointmentStatus(status)

        db.commit()
        print(f"✅ Appointment ID {appointment_id} updated.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating appointment: {e}")
    finally:
        db.close()

def delete_appointment():
    db = next(get_db())
    try:
        appointment_id = inquirer.number(message="🆔 Enter Appointment ID to delete:", min_allowed=1).execute()
        confirm = inquirer.confirm(
            message=f"⚠️ Are you sure you want to delete appointment ID {appointment_id}?",
            default=False
        ).execute()
        if not confirm:
            print("❎ Delete cancelled.")
            return

        appointment = db.get(Appointment, appointment_id)
        if not appointment:
            print(f"❌ No appointment with ID {appointment_id} found.")
            return

        db.delete(appointment)
        db.commit()
        print(f"🗑️ Appointment ID {appointment_id} deleted.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting appointment: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main_menu()