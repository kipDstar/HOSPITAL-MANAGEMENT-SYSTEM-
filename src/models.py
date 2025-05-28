from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()


#------patient

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    dob = Column(String)
    contact_info = Column(String)
    admission_date = Column(String)
    discharge_date = Column(String, nullable=True)

    type = Column(String(50))

    __mapper_args__={
        "polymorphic_identity": "patient",
        "polymorphic_on": type,
    }

    appointments = relationship('Appointment', back_populates='patient', cascade='all, delete-orphan')
    medical_records = relationship('MedicalRecord', back_populates='patient', cascade='all, delete-orphan')

class InPatient(Patient):
    __tablename__ = 'inpatients'
    id = Column(Integer, ForeignKey('patients.id'), primary_key=True)
    room_number = Column(String)

    __mapper_args__={
        "polymorphic_identity": "inpatient",
    }

class OutPatient(Patient):
    __tablename__ = 'outpatients'
    id = Column(Integer, ForeignKey('patients.id'), primary_key=True)
    last_visit_date = Column(String)

    __mapper_args__={
        "polymorphic_identity": "outpatient",
    }

# -------------------- Doctor

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    specialization = Column(String)

    appointments = relationship('Appointment', back_populates='doctor', cascade='all, delete-orphan')
    medical_records = relationship('MedicalRecord', back_populates='doctor', cascade='all, delete-orphan')
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    department = relationship("Department", back_populates="doctors", foreign_keys=[department_id])

# -------------------- Department

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    head_doctor_id = Column(Integer, ForeignKey('doctors.id'))

    doctors = relationship("Doctor", back_populates="department", foreign_keys="Doctor.department_id")
    head_doctor = relationship("Doctor", foreign_keys=[head_doctor_id])

# -------------------- Appointment

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    appointment_date = Column(DateTime, default=datetime.utcnow)
    reason = Column(String)

    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))

    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('Doctor', back_populates='appointments')

# -------------------- Medical records

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True)
    diagnosis = Column(Text)
    treatment = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))

    patient = relationship('Patient', back_populates='medical_records')
    doctor = relationship('Doctor', back_populates='medical_records')