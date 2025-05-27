from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, Enum as SQLEnum
from src.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, date

import enum

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

    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_on': patient_type,
        'polymorphic_identity': 'patient'
    }

    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', type='{self.patient_type.value}')>"

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
    department_id = Column(Integer, ForeignKey('departments.id')) # Foreign key to link to Department

    # Relationships
    department = relationship("Department", back_populates="doctors", foreign_keys=[department_id]) # THIS WAS PREVIOUSLY FIXED
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="doctor", cascade="all, delete-orphan")

    department_headed = relationship(
        "Department",
        back_populates="head_doctor",
        foreign_keys="[Department.head_doctor_id]"
    )

    def __repr__(self):
        return f"<Doctor(id={self.id}, name='{self.name}', spec='{self.specialization}')>"

    @classmethod
    def find_by_id(cls, session, doctor_id):
        return session.query(cls).filter_by(id=doctor_id).first()
    @classmethod
    def get_all(cls, session):
        """
        Retrieves all Doctor objects from the database.
        :param session: The SQLAlchemy session.
        :return: A list of Doctor objects.
        """
        return session.query(cls).all()


# --- Department Model ---
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    specialty = Column(String, nullable=True)

    head_doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=True)

    # Relationships for department
    # THIS IS THE LINE WITH THE CURRENT FIX!
    doctors = relationship('Doctor', back_populates='department', foreign_keys='[Doctor.department_id]')

    head_doctor = relationship(
        'Doctor',
        foreign_keys=[head_doctor_id],
        back_populates='department_headed',
        uselist=False,
        post_update=True
    )

    def __repr__(self):
        head_name = self.head_doctor.name if self.head_doctor else 'None'
        return f"<Department(id={self.id}, name={self.name}, head='{head_name}')>"

    @classmethod
    def create(cls, session, name, specialty=None, head_doctor_id=None):
        department = cls(name=name, specialty=specialty, head_doctor_id=head_doctor_id)
        session.add(department)
        session.commit()
        return department

    @classmethod
    def find_by_id(cls, session, department_id):
        return session.query(cls).filter_by(id=department_id).first()

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def delete_by_id(cls, session, department_id):
        department = cls.find_by_id(session, department_id)
        if department:
            session.delete(department)
            session.commit()
            return True
        return False

    def update_info(self, session, name=None, head_doctor_id=None, specialty=None):
        if name is not None:
            self.name = name
        if specialty is not None:
            self.specialty = specialty
        if head_doctor_id is not None:
            doctor = Doctor.find_by_id(session, head_doctor_id)
            if not doctor:
                raise ValueError(f"Doctor with ID {head_doctor_id} does not exist.")
            self.head_doctor_id = head_doctor_id
        session.commit()

    def assign_head_doctor(self, session, doctor_id):
        doctor = Doctor.find_by_id(session, doctor_id)
        if not doctor:
            raise ValueError(f"Doctor with ID {doctor_id} was not found in our system, consult ADMIN.")
        self.head_doctor_id = doctor_id
        session.commit()

    def unassign_head_doctor(self, session):
        self.head_doctor_id = None
        session.commit()

    def get_staff_count(self, session):
        return len(self.doctors)

    def assign_specialty(self, session, specialty):
        self.specialty = specialty
        session.commit()

    def specialty_doctors(self, session):
        return session.query(Doctor).filter(Doctor.department_id == self.id, Doctor.specialization == self.specialty).all()


# --- Appointment Model ---
class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    appointment_datetime = Column(DateTime, nullable=False, default=datetime.now)
    reason = Column(String)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, date='{self.appointment_datetime.strftime('%Y-%m-%d %H:%M')}')>"

# --- MedicalRecord Model ---
class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    record_date = Column(Date, default=date.today)
    diagnosis = Column(String)
    treatment = Column(Text)

    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")

    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, patient_id={self.patient_id}, diagnosis='{self.diagnosis[:20]}...')>"