Hospital Management System (HMS)

A full-stack web application designed to manage hospital operations, including departments, medical staff, and patient records. The system provides administrative interfaces for comprehensive data management and a patient-facing portal for self-registration.

✨ Features
This Hospital Management System offers the following key functionalities:
##Department Management:
Create, View, Edit, Delete: Full CRUD operations for hospital departments.

Head Doctor Assignment: Assign and reassign a specific doctor as the head of a department.

Department Overview: View details like department name, specialty, head doctor, and count of doctors/patients assigned to it.

##Doctor Management:
Create, View, Edit, Delete: Full CRUD operations for doctor profiles.

Specialization & Department Assignment: Track doctor's specialization and the department they primarily work in.

##Patient Management (Admin Side):
Register Patients: Manually add new patient records with personal details, contact info, and patient type (Inpatient/Outpatient).

Inpatient/Outpatient Details: Capture specific information based on patient type (e.g., room number, admission/discharge dates for inpatients; last visit date for outpatients).

Doctor & Department Assignment: Assign patients to specific doctors and departments.

View, Edit, Delete: Comprehensive management of existing patient records.

##Patient Self-Registration:
New Patient Onboarding: A dedicated interface allowing new patients to register themselves by providing basic personal and contact information. Self-registered patients are initially classified as outpatients.

🚀 Techstack:
This project leverages a modern full-stack architecture:

Backend:
Flask: A lightweight Python web framework for building the RESTful API.

SQLAlchemy: Python SQL toolkit and Object-Relational Mapper (ORM) for interacting with the database.

SQLite: A file-based SQL database used for development.

Flask-CORS: Enables Cross-Origin Resource Sharing for seamless communication with the frontend.

Pipenv: A dependency management tool for Python projects.


Frontend:
React: A JavaScript library for building interactive user interfaces.

Vite: A fast build tool that provides a rapid development environment for React.

Tailwind CSS: A utility-first CSS framework for rapid and responsive UI styling.


⚙️ Setup Instructions
Follow these steps to get the project up and running on your local machine.

##Prerequisites
Before you begin, ensure you have the following installed:

Python 3.8+: Download Python 

Node.js (LTS recommended) & npm: Download Node.js

Flask: pip install flask

Flask-cors: pip install flask_cors

Pipenv: Install globally using pip: pip install pipenv


1. Backend Setup
Clone the Repository:

Navigate to your desired development directory and clone your project repository (assuming your backend is part of a larger repo or is the root of HOSPITAL-MANAGEMENT-SYSTEM-):

git clone <your-repo-url>
cd HOSPITAL-MANAGEMENT-SYSTEM-


Install Python Dependencies:
pipenv install

This will create a virtual environment and install all dependencies listed in Pipfile.
Activate the Virtual Environment:
pipenv shell

Your terminal prompt should change to indicate the active virtual environment (e.g., (HOSPITAL-MANAGEMENT-SYSTEM-)).
Set Flask Application:
Tell Flask where to find your main application file:
export FLASK_APP=src/api.py
alternatively pass in the cli command: python -m src.api to launch the api file


Initialize the Database:
Delete any old hospital.db file if it exists, then create the database tables:
rm -f hospital.db # Use 'del hospital.db' on Windows
python -m src.cli createtables


Seed Initial Data (Optional but Recommended):
Populate your database with some sample data for testing:
python -m src.cli seed


2. Frontend Setup
Navigate to the Frontend Directory:
From your backend root, go into the frontend folder:
cd frontend-hms


Install Node.js Dependencies:
npm install


🏃‍♀️ Running the Application
Ensure both your backend API and frontend development server are running concurrently.
1. Run the Backend API
In your backend terminal (where you activated pipenv shell and set FLASK_APP):
flask run


The API will typically run on http://127.0.0.1:5000. Keep this terminal open.
2. Run the Frontend Development Server
In a new terminal tab/window (navigate to frontend-hms and run):
npm run dev


The frontend will typically open in the browser at http://localhost:5173/.
You should now see the Hospital Management Dashboard in your browser, with navigation options for Departments, Doctors, Patient Management (Admin), and Patient Self-Registration.

💻 Running as a Standalone CLI Application
At the core this is a CLI application so you can manage your hospital data directly from the command line using python -m src.cli, which is often useful for scripting, batch operations, or quick data checks without starting the web server.
Prerequisites: Ensure you are in your backend project's root directory (HOSPITAL-MANAGEMENT-SYSTEM-) and have activated your pipenv shell.
General Commands:
##Create Database Tables:
python -m src.cli createtables

##Resets and creates all tables based on src/models.py.
Seed Initial Data:
python -m src.cli seed

##Populates the database with sample departments, doctors, and patients.
Department Management:
List all Departments:
python -m src.cli department list


##Add a new Department:
python -m src.cli department add --name "Emergency" --specialty "Trauma" --head-doctor-id 1

(Replace 1 with an actual Doctor ID if you have one.)
##Update info on a Department:
python -m src.cli department update 1 --name "Emergency Department" --specialty "Emergency Medicine"

(Replace 1 with the Department ID you want to update.)
##To unassign a head doctor:
python -m src.cli department update 1 --head-doctor-id 0


##Delete a Department:
python -m src.cli department delete 1

(Replace 1 with the Department ID you want to delete.)
Doctor Management:
##List all Doctors:
python -m src.cli doctor list


##Add a new Doctor:
python -m src.cli doctor add --name "Dr. Alice Wonderland" --specialization "Pediatrician" --contact-info "alice@example.com" --department-id 2

(Replace 2 with an actual Department ID.)
##Update a Doctor:
python -m src.cli doctor update 1 --specialization "Senior Cardiologist" --contact-info "new.email@example.com"

(Replace 1 with the Doctor ID you want to update.)
##To unassign from a department:
python -m src.cli doctor update 1 --department-id 0


##Delete a Doctor:
python -m src.cli doctor delete 1

(Replace 1 with the Doctor ID you want to delete.)
Patient Management:
##List all Patients:
python -m src.cli patient list


##Add a new Patient (Outpatient):
python -m src.cli patient add --name "New Outpatient" --date-of-birth "1999-01-01" --contact-info "new.out@example.com" --patient-type "outpatient" --last-visit-date "2024-05-28" --assigned-doctor-id 1 --assigned-department-id 1

(Adjust IDs and dates as needed.)
##Add a new Patient (Inpatient):
python -m src.cli patient add --name "New Inpatient" --date-of-birth "1980-06-15" --contact-info "new.in@example.com" --patient-type "inpatient" --room-number "305" --admission-date "2024-05-27" --assigned-doctor-id 3 --assigned-department-id 3

(Adjust IDs, room, and dates as needed.)
##Update a Patient:
python -m src.cli patient update 5 --contact-info "updated.contact@example.com" --assigned-doctor-id 2

(Replace 5 with the Patient ID you want to update.)
##To update inpatient specific fields:
python -m src.cli patient update 3 --room-number "401B" --discharge-date "2024-06-05"


##Delete a Patient:
python -m src.cli patient delete 5

(Replace 5 with the Patient ID you want to delete.)

☁️ Deployment
This project has been tested for deployment on platforms like Render.

Backend Deployment: Deploy your Flask API as a "Web Service" on Render. Ensure your Procfile (if used) points to your Flask app (e.g., web: gunicorn src.api:app).

Frontend Deployment: Deploy your React application as a "Static Site" on Render.

Build Command: npm run build
Publish Directory: dist

Update API Base URL: Crucially, once your backend API is deployed on Render, you have to update the API_BASE_URL in frontend-hms/src/App.jsx to point to your live Render backend API URL (e.g., https://your-hms-api.onrender.com). 
Then, redeploy your frontend.

🚀 Future Enhancements
1. Authentication & Authorization: Implement user login, roles (Admin, Doctor, Patient), and restrict access to certain functionalities based on roles.
2. Appointments & Medical Records UI: Create dedicated frontend interfaces for managing appointments and viewing/adding medical records.
3. Doctor Dashboard: A more detailed view for doctors to see their assigned patients and appointments.
4. Patient Dashboard: A more detailed view for patients to manage their appointments, view basic medical records, and update their contact info.
5. Search & Filtering: Add robust search and filtering capabilities to lists of departments, doctors, and patients.
6. Notifications: Implement notifications for appointments, patient updates, etc.
7. Database Migrations: Integrate Alembic for managing database schema changes in a production-safe manner.
8. Improved Form Validations: More comprehensive client-side and server-side validation.
9.Styling & Responsiveness: Further refine the UI/UX and ensure full responsiveness across all devices.
