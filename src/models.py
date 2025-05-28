# src/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, Enum as SQLEnum
from src.database import Base # Assuming Base is defined here
from sqlalchemy.orm import relationship, backref
from datetime import datetime, date
import enum
from sqlalchemy.exc import IntegrityError # Import for error handling

# --- Enums for better type handling ---
class PatientType(enum.Enum):
    INPATIENT = "inpatient"
    OUTPATIENT = "outpatient"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# --- Patient Model ---
class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    contact_info = Column(String)
    patient_type = Column(SQLEnum(PatientType), nullable=False)

    # New fields for patient assignment
    assigned_doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='SET NULL'), nullable=True)
    assigned_department_id = Column(Integer, ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

    # Relationship to the assigned doctor
    assigned_doctor = relationship("Doctor", back_populates="patients_assigned", foreign_keys=[assigned_doctor_id])

    # Relationship to the assigned department
    assigned_department = relationship("Department", back_populates="patients_assigned", foreign_keys=[assigned_department_id])


    __mapper_args__ = {
        'polymorphic_on': patient_type,
        'polymorphic_identity': 'patient'
    }

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', type='{self.patient_type.value}')>"

    # --- CRUD Methods for Patient Base Class ---
    def save(self, session):
        """Adds or updates a patient in the database."""
        session.add(self)
        try:
            session.commit()
            return self
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Patient with ID {self.id} already exists or invalid data.")

    def delete(self, session):
        """Deletes a patient from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, session, id):
        """Retrieves a patient by ID."""
        return session.query(cls).get(id)

    @classmethod
    def get_all(cls, session):
        """Retrieves all patients."""
        return session.query(cls).all()

    def to_dict(self):
        """Serializes a Patient object to a dictionary."""
        data = {
            "id": self.id,
            "name": self.name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "contact_info": self.contact_info,
            "patient_type": self.patient_type.value,
            "assigned_doctor_id": self.assigned_doctor_id,
            "assigned_doctor_name": self.assigned_doctor.name if self.assigned_doctor else None,
            "assigned_department_id": self.assigned_department_id,
            "assigned_department_name": self.assigned_department.name if self.assigned_department else None,
        }
        # Add polymorphic specific data
        if self.patient_type == PatientType.INPATIENT:
            data.update({
                "room_number": self.room_number,
                "admission_date": self.admission_date.isoformat() if self.admission_date else None,
                "discharge_date": self.discharge_date.isoformat() if self.discharge_date else None,
            })
        elif self.patient_type == PatientType.OUTPATIENT:
            data.update({
                "last_visit_date": self.last_visit_date.isoformat() if self.last_visit_date else None,
            })
        return data


# --- InPatient Model ---
class InPatient(Patient):
    __tablename__ = 'inpatients'
    id = Column(Integer, ForeignKey("patients.id"), primary_key=True)
    room_number = Column(String)
    admission_date = Column(Date, default=date.today)
    discharge_date = Column(Date)

    __mapper_args__ = {
        'polymorphic_identity': PatientType.INPATIENT
    }

    def __repr__(self):
        return f"<InPatient(id={self.id}, name='{self.name}', room='{self.room_number}')>"


# --- OutPatient Model ---
class OutPatient(Patient):
    __tablename__ = 'outpatients'
    id = Column(Integer, ForeignKey("patients.id"), primary_key=True)
    last_visit_date = Column(Date)

    __mapper_args__ = {
        'polymorphic_identity': PatientType.OUTPATIENT
    }

    def __repr__(self):
        return f"<OutPatient(id={self.id}, name='{self.name}', last_visit='{self.last_visit_date}')>"

# --- Doctor Model ---
class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    specialization = Column(String)
    contact_info = Column(String)

    # Foreign key for the department the doctor works in
    department_id = Column(Integer, ForeignKey('departments.id', ondelete='SET NULL'))

    # Relationships
    # Doctor works in a Department
    department = relationship("Department", back_populates="doctors_in_department", foreign_keys=[department_id])

    # Appointments made with this doctor
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    # Medical records associated with this doctor
    medical_records = relationship("MedicalRecord", back_populates="doctor", cascade="all, delete-orphan")

    # Departments where this doctor is the head
    departments_headed = relationship(
        "Department",
        back_populates="head_doctor",
        foreign_keys="[Department.head_doctor_id]"
    )

    # Patients assigned to this doctor
    patients_assigned = relationship("Patient", back_populates="assigned_doctor", foreign_keys=[Patient.assigned_doctor_id])


    def __repr__(self):
        return f"<Doctor(id={self.id}, name='{self.name}', spec='{self.specialization}')>"

    # --- CRUD Methods for Doctor ---
    def save(self, session):
        """Adds or updates a doctor in the database."""
        session.add(self)
        try:
            session.commit()
            return self
        except IntegrityError:
            session.rollback()
            raise ValueError("Doctor with this name already exists.")

    def delete(self, session):
        """Deletes a doctor from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, session, doctor_id):
        """Retrieves a doctor by ID."""
        return session.query(cls).filter_by(id=doctor_id).first()

    @classmethod
    def get_all(cls, session):
        """Retrieves all doctors."""
        return session.query(cls).all()

    def to_dict(self):
        """Serializes a Doctor object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "contact_info": self.contact_info,
            "department_id": self.department_id,
            "department_name": self.department.name if self.department else None,
            "departments_headed_count": len(self.departments_headed),
            "patients_assigned_count": len(self.patients_assigned)
        }


# --- Department Model ---
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    specialty = Column(String, nullable=True)

    head_doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='SET NULL'), nullable=True)

    # Relationships for department
    # Doctors working in this department
    doctors_in_department = relationship('Doctor', back_populates='department', foreign_keys='[Doctor.department_id]')

    # The head doctor of this department
    head_doctor = relationship(
        'Doctor',
        foreign_keys=[head_doctor_id],
        back_populates='departments_headed',
        uselist=False, # A department has only one head doctor
        post_update=True # Allows updating head_doctor_id without needing to commit first
    )

    # Patients assigned to this department
    patients_assigned = relationship("Patient", back_populates="assigned_department", foreign_keys=[Patient.assigned_department_id])


    def __repr__(self):
        head_name = self.head_doctor.name if self.head_doctor else 'None'
        return f"<Department(id={self.id}, name={self.name}, head='{head_name}')>"

    # --- CRUD Methods for Department ---
    def save(self, session):
        """Adds or updates a department in the database."""
        session.add(self)
        try:
            session.commit()
            return self
        except IntegrityError:
            session.rollback()
            raise ValueError("Department with this name already exists.")

    def delete(self, session):
        """Deletes a department from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, session, department_id):
        """Retrieves a department by ID."""
        return session.query(cls).filter_by(id=department_id).first()

    @classmethod
    def get_all(cls, session):
        """Retrieves all departments."""
        return session.query(cls).all()

    def to_dict(self):
        """Serializes a Department object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty,
            "head_doctor_id": self.head_doctor_id,
            "head_doctor_name": self.head_doctor.name if self.head_doctor else None,
            "num_doctors_in_dept": len(self.doctors_in_department),
            "num_patients_assigned": len(self.patients_assigned)
        }


# --- Appointment Model ---
class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_datetime = Column(DateTime, nullable=False, default=datetime.now)
    reason = Column(String)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, date='{self.appointment_datetime.strftime('%Y-%m-%d %H:%M')}')>"

    # --- CRUD Methods for Appointment ---
    def save(self, session):
        session.add(self)
        session.commit()
        return self

    def delete(self, session):
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, session, id):
        return session.query(cls).get(id)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient.name if self.patient else None,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name if self.doctor else None,
            "appointment_datetime": self.appointment_datetime.isoformat(),
            "reason": self.reason,
            "status": self.status.value,
        }


# --- MedicalRecord Model ---
class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    record_date = Column(Date, default=date.today)
    diagnosis = Column(String)
    treatment = Column(Text)

    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")

    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, patient_id={self.patient_id}, diagnosis='{self.diagnosis[:20]}...')>"

    # --- CRUD Methods for MedicalRecord ---
    def save(self, session):
        session.add(self)
        session.commit()
        return self

    def delete(self, session):
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, session, id):
        return session.query(cls).get(id)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient.name if self.patient else None,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name if self.doctor else None,
            "record_date": self.record_date.isoformat(),
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
        }
