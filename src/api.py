# src/api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date, datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Import your database session helper and models
from src.database import get_db # Assuming get_db is your session generator
from src.models import Department, Doctor, Patient, InPatient, OutPatient, Appointment, MedicalRecord, PatientType, AppointmentStatus

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing your React frontend to access it

# --- API Endpoints for Department Management ---

@app.route('/departments', methods=['GET'])
def get_departments():
    session = next(get_db())
    try:
        departments = Department.get_all(session)
        return jsonify([dept.to_dict() for dept in departments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    session = next(get_db())
    try:
        dept = Department.get_by_id(session, department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404
        return jsonify(dept.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/departments', methods=['POST'])
def add_department():
    session = next(get_db())
    data = request.get_json()
    name = data.get('name')
    specialty = data.get('specialty')
    head_doctor_id = data.get('head_doctor_id')

    if not name:
        return jsonify({"error": "Department name is required"}), 400

    try:
        # Validate head_doctor_id if provided
        if head_doctor_id:
            doctor = Doctor.get_by_id(session, head_doctor_id)
            if not doctor:
                return jsonify({"error": f"Doctor with ID {head_doctor_id} not found."}), 400

        dept = Department(name=name, specialty=specialty, head_doctor_id=head_doctor_id)
        dept.save(session)
        return jsonify(dept.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # Conflict, e.g., unique name violation
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

@app.route('/departments/<int:department_id>', methods=['PUT'])
def update_department_api(department_id):
    session = next(get_db())
    data = request.get_json()

    try:
        dept = Department.get_by_id(session, department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404

        if 'name' in data:
            dept.name = data['name']
        if 'specialty' in data:
            dept.specialty = data['specialty']
        if 'head_doctor_id' in data:
            head_doctor_id = data['head_doctor_id']
            if head_doctor_id is not None:
                doctor = Doctor.get_by_id(session, head_doctor_id)
                if not doctor:
                    return jsonify({"error": f"Doctor with ID {head_doctor_id} not found."}), 400
            dept.head_doctor_id = head_doctor_id # Can be None

        dept.save(session)
        return jsonify(dept.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

@app.route('/departments/<int:department_id>', methods=['DELETE'])
def delete_department_api(department_id):
    session = next(get_db())
    try:
        dept = Department.get_by_id(session, department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404
        
        dept.delete(session)
        return jsonify({"message": "Department deleted successfully"}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

# --- DOCTOR ROUTES ---
@app.route('/doctors', methods=['GET'])
def get_all_doctors():
    session = next(get_db())
    try:
        doctors = Doctor.get_all(session)
        return jsonify([doc.to_dict() for doc in doctors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/doctors', methods=['POST'])
def add_doctor():
    session = next(get_db())
    data = request.json
    name = data.get('name')
    specialization = data.get('specialization')
    department_id = data.get('department_id') # New: doctor can be assigned to a department

    if not name:
        return jsonify({"error": "Doctor name is required"}), 400

    try:
        if department_id:
            department = Department.get_by_id(session, department_id)
            if not department:
                return jsonify({"error": f"Department with ID {department_id} not found."}), 400

        new_doctor = Doctor(name=name, specialization=specialization, department_id=department_id)
        new_doctor.save(session)
        return jsonify(new_doctor.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

@app.route('/doctors/<int:id>', methods=['PUT'])
def update_doctor(id):
    session = next(get_db())
    data = request.json
    try:
        doctor = Doctor.get_by_id(session, id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        if 'name' in data:
            doctor.name = data['name']
        if 'specialization' in data:
            doctor.specialization = data['specialization']
        if 'department_id' in data: # Allow updating department
            department_id = data['department_id']
            if department_id is not None:
                department = Department.get_by_id(session, department_id)
                if not department:
                    return jsonify({"error": f"Department with ID {department_id} not found."}), 400
            doctor.department_id = department_id
        
        doctor.save(session)
        return jsonify(doctor.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

@app.route('/doctors/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    session = next(get_db())
    try:
        doctor = Doctor.get_by_id(session, id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404
        
        doctor.delete(session)
        return jsonify({"message": "Doctor deleted successfully"}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

# --- PATIENT ROUTES (NEW) ---

@app.route('/patients', methods=['GET'])
def get_all_patients():
    session = next(get_db())
    try:
        patients = Patient.get_all(session)
        return jsonify([p.to_dict() for p in patients])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/patients/<int:id>', methods=['GET'])
def get_patient(id):
    session = next(get_db())
    try:
        patient = Patient.get_by_id(session, id)
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        return jsonify(patient.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/patients', methods=['POST'])
def add_patient():
    session = next(get_db())
    data = request.json
    name = data.get('name')
    date_of_birth_str = data.get('date_of_birth')
    contact_info = data.get('contact_info')
    patient_type_str = data.get('patient_type') # 'inpatient' or 'outpatient'
    assigned_doctor_id = data.get('assigned_doctor_id')
    assigned_department_id = data.get('assigned_department_id')

    # Type-specific fields
    room_number = data.get('room_number')
    admission_date_str = data.get('admission_date')
    discharge_date_str = data.get('discharge_date')
    last_visit_date_str = data.get('last_visit_date')

    if not all([name, date_of_birth_str, patient_type_str]):
        return jsonify({"error": "Name, Date of Birth, and Patient Type are required"}), 400

    try:
        date_of_birth = date.fromisoformat(date_of_birth_str)
        patient_type = PatientType(patient_type_str) # Convert string to Enum

        # Validate assigned doctor and department
        if assigned_doctor_id:
            doctor = Doctor.get_by_id(session, assigned_doctor_id)
            if not doctor:
                return jsonify({"error": f"Assigned Doctor with ID {assigned_doctor_id} not found."}), 400
        if assigned_department_id:
            department = Department.get_by_id(session, assigned_department_id)
            if not department:
                return jsonify({"error": f"Assigned Department with ID {assigned_department_id} not found."}), 400

        patient_kwargs = {
            "name": name,
            "date_of_birth": date_of_birth,
            "contact_info": contact_info,
            "assigned_doctor_id": assigned_doctor_id,
            "assigned_department_id": assigned_department_id,
        }

        if patient_type == PatientType.INPATIENT:
            if not room_number:
                return jsonify({"error": "Room number is required for Inpatients"}), 400
            admission_date = date.fromisoformat(admission_date_str) if admission_date_str else date.today()
            discharge_date = date.fromisoformat(discharge_date_str) if discharge_date_str else None
            patient = InPatient(
                room_number=room_number,
                admission_date=admission_date,
                discharge_date=discharge_date,
                **patient_kwargs
            )
        elif patient_type == PatientType.OUTPATIENT:
            last_visit_date = date.fromisoformat(last_visit_date_str) if last_visit_date_str else date.today()
            patient = OutPatient(
                last_visit_date=last_visit_date,
                **patient_kwargs
            )
        else:
            return jsonify({"error": "Invalid patient type"}), 400

        patient.save(session)
        return jsonify(patient.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Bad request for date format or invalid type
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

@app.route('/patients/<int:id>', methods=['PUT'])
def update_patient(id):
    session = next(get_db())
    data = request.json

    try:
        patient = Patient.get_by_id(session, id)
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Update common fields
        if 'name' in data: patient.name = data['name']
        if 'date_of_birth' in data: patient.date_of_birth = date.fromisoformat(data['date_of_birth'])
        if 'contact_info' in data: patient.contact_info = data['contact_info']

        # Update assigned doctor and department
        if 'assigned_doctor_id' in data:
            assigned_doctor_id = data['assigned_doctor_id']
            if assigned_doctor_id is not None:
                doctor = Doctor.get_by_id(session, assigned_doctor_id)
                if not doctor:
                    return jsonify({"error": f"Assigned Doctor with ID {assigned_doctor_id} not found."}), 400
            patient.assigned_doctor_id = assigned_doctor_id
        if 'assigned_department_id' in data:
            assigned_department_id = data['assigned_department_id']
            if assigned_department_id is not None:
                department = Department.get_by_id(session, assigned_department_id)
                if not department:
                    return jsonify({"error": f"Assigned Department with ID {assigned_department_id} not found."}), 400
            patient.assigned_department_id = assigned_department_id

        # Update type-specific fields (careful with polymorphic updates)
        if patient.patient_type == PatientType.INPATIENT:
            if 'room_number' in data: patient.room_number = data['room_number']
            if 'admission_date' in data: patient.admission_date = date.fromisoformat(data['admission_date'])
            if 'discharge_date' in data: patient.discharge_date = date.fromisoformat(data['discharge_date'])
        elif patient.patient_type == PatientType.OUTPATIENT:
            if 'last_visit_date' in data: patient.last_visit_date = date.fromisoformat(data['last_visit_date'])
        
        patient.save(session)
        return jsonify(patient.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

@app.route('/patients/<int:id>', methods=['DELETE'])
def delete_patient(id):
    session = next(get_db())
    try:
        patient = Patient.get_by_id(session, id)
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        patient.delete(session)
        return jsonify({"message": "Patient deleted successfully"}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

# --- Patient Self-Registration Endpoint ---
@app.route('/patients/register', methods=['POST'])
def patient_self_register():
    session = next(get_db())
    data = request.json
    name = data.get('name')
    date_of_birth_str = data.get('date_of_birth')
    contact_info = data.get('contact_info')

    if not all([name, date_of_birth_str, contact_info]):
        return jsonify({"error": "Name, Date of Birth, and Contact Info are required for registration"}), 400

    try:
        date_of_birth = date.fromisoformat(date_of_birth_str)
        
        # Self-registered patients are initially OutPatients, not assigned doctor/department
        patient = OutPatient(
            name=name,
            date_of_birth=date_of_birth,
            contact_info=contact_info,
            patient_type=PatientType.OUTPATIENT,
            last_visit_date=date.today() # Set initial last visit date
        )
        patient.save(session)
        return jsonify(patient.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()


# If you run this file directly, it will start the Flask development server.
# For production, use a WSGI server like Gunicorn.
if __name__ == '__main__':
    # Ensure your database tables exist before starting the API
    from src.database import create_tables
    create_tables()
    app.run(debug=True, port=5000)
