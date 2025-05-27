# src/api.py
# This file will define your Flask API endpoints to interact with the database.

from flask import Flask, request, jsonify
from flask_cors import CORS # Used for Cross-Origin Resource Sharing
from datetime import date, datetime

# Import your database session helper and models
from src.database import get_db # Assuming get_db is your session generator
from src.models import Department, Doctor, Patient, Appointment, MedicalRecord, PatientType, AppointmentStatus # Import all necessary models

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing your React frontend to access it

# Helper function to serialize SQLAlchemy objects to dictionaries
# This is a basic serializer. For more complex objects, you might need a more robust one.
def serialize_department(dept):
    """Serializes a Department object to a dictionary."""
    return {
        "id": dept.id,
        "name": dept.name,
        "specialty": dept.specialty,
        "head_doctor_id": dept.head_doctor_id,
        "head_doctor_name": dept.head_doctor.name if dept.head_doctor else None,
        "num_doctors": len(dept.doctors) # Accessing the relationship to get count
    }

def serialize_doctor(doctor):
    """Serializes a Doctor object to a dictionary."""
    return {
        "id": doctor.id,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "contact_info": doctor.contact_info,
        "department_id": doctor.department_id,
        "department_name": doctor.department.name if doctor.department else None
    }

# --- New Root Endpoint ---
@app.route('/', methods=['GET'])
def home():
    """A simple welcome message for the API root."""
    return jsonify({"message": "Welcome to the Hospital Management API! Access /departments or /doctors for data."})


# --- API Endpoints for Department Management ---

@app.route('/departments', methods=['GET'])
def get_departments():
    """API endpoint to list all departments."""
    session = next(get_db())
    try:
        departments = Department.get_all(session)
        # Serialize each department object into a dictionary
        return jsonify([serialize_department(dept) for dept in departments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """API endpoint to get details of a specific department."""
    session = next(get_db())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404
        
        # Serialize department details
        dept_data = serialize_department(dept)
        
        # Also include a list of doctors in the department
        doctors_in_dept = [serialize_doctor(doc) for doc in dept.doctors]
        dept_data["doctors_in_department"] = doctors_in_dept

        return jsonify(dept_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/departments', methods=['POST'])
def add_department():
    """API endpoint to add a new department."""
    data = request.get_json()
    name = data.get('name')
    specialty = data.get('specialty')
    head_doctor_id = data.get('head_doctor_id')

    if not name:
        return jsonify({"error": "Department name is required"}), 400

    session = next(get_db())
    try:
        # Validate if head_doctor_id is provided, that the doctor exists
        if head_doctor_id:
            doctor = Doctor.find_by_id(session, head_doctor_id)
            if not doctor:
                return jsonify({"error": f"Doctor with ID {head_doctor_id} not found."}), 400

        dept = Department.create(session, name=name, specialty=specialty, head_doctor_id=head_doctor_id)
        return jsonify(serialize_department(dept)), 201 # 201 Created
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/departments/<int:department_id>', methods=['PUT'])
def update_department_api(department_id):
    """API endpoint to update an existing department."""
    data = request.get_json()
    name = data.get('name')
    specialty = data.get('specialty')
    head_doctor_id = data.get('head_doctor_id')

    session = next(get_db())
    try:
        dept = Department.find_by_id(session, department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404

        update_kwargs = {}
        if name is not None:
            update_kwargs['name'] = name
        if specialty is not None:
            update_kwargs['specialty'] = specialty
        if head_doctor_id is not None:
            doctor = Doctor.find_by_id(session, head_doctor_id)
            if not doctor:
                return jsonify({"error": f"Doctor with ID {head_doctor_id} not found."}), 400
            update_kwargs['head_doctor_id'] = head_doctor_id
        
        if not update_kwargs:
            return jsonify({"message": "No update parameters provided."}), 200

        dept.update_info(session, **update_kwargs)
        return jsonify(serialize_department(dept)), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/departments/<int:department_id>', methods=['DELETE'])
def delete_department_api(department_id):
    """API endpoint to delete a department."""
    session = next(get_db())
    try:
        if Department.delete_by_id(session, department_id):
            return jsonify({"message": "Department deleted successfully"}), 200
        else:
            return jsonify({"error": "Department not found"}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# --- Utility Endpoints (e.g., for dropdowns in frontend) ---

@app.route('/doctors', methods=['GET'])
def get_all_doctors():
    """API endpoint to list all doctors (useful for head_doctor dropdowns)."""
    session = next(get_db())
    try:
        doctors = Doctor.get_all(session) # Assuming Doctor has a get_all class method
        return jsonify([serialize_doctor(doc) for doc in doctors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# If you run this file directly, it will start the Flask development server.
# For production, use a WSGI server like Gunicorn.
if __name__ == '__main__':
    # Ensure your database tables exist before starting the API
    # This is fine for development, but for production, migrations are preferred.
    from src.database import create_tables
    create_tables()
    app.run(debug=True, port=5000) # Run on port 5000 for development
