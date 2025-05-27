from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    # Add column for patient name and patient DOB and make them required fields [nullable = False].
    #      (Input has to be filled) also andd a contact_info and type column
    name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)
    contact_info = Column(String)
    type = Column(String)
    # Type is used to store what kind of patient this is (inpatient/outpatient) and also used in polymorphism

    # Define relationships 
    # (back_populate) => creates a two-way relationship between 2 tables  
    #              It allows us to access parent object from the child and the child object from the parent
    # (cascade = "all, delete") => means that when a patient is deleted, their records and appointments are also deleted
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete")

    # Polymorphic mapping => polymorphic mapping allows different subclasses (like InPatient and OutPatient) to share a common table (patients) 
    #                        and to store their extra fields in separate tables. 
    #                     => It also allows SQLAlchemy to automatically return the correct subclass when querying the database.
    # (__mapper_args__) is a special dictionary used to customize how SQLAlchemy maps your Python class to the database. 
    # *polymorphic_on:*
    #        This tells SQLAlchemy which column in the table it should use to decide which subclass to use.
    #        In this case, it's the (type) column.
    # *polymorphic_identity:*
    #         This sets the identity string that SQLAlchemy uses to distinguish this class in the type column.

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'patient'
    }


class InPatient(Patient):
    # This specifies the table name which will store the extra data specific to inpatients 
    __tablename__ = 'inpatients'
    # This links the inpatients table back to the patients table using a foreign key.
    # Every inpatient is also a patient, so they share the same ID.
    id = Column(Integer, ForeignKey("patients.id"), primary_key=True)
    # The extra fields for inpatients
    room_number = Column(Integer)
    admission_date = Column(Date)
    discharge_date = Column(Date)

    # Specify polymorphic identity

    __mapper_args__ = {
        'polymorphic_identity': 'inpatient'
    }



class OutPatient(Patient):
    # This specifies the table name which will store the extra data specific to outpatients
    __tablename__ = 'outpatients'
    # This links the inpatients table back to the patients table using a foreign key.
    id = Column(Integer, ForeignKey("patients.id"), primary_key=True)
    last_visit_date = Column(Date)

    __mapper_args__ = {
        'polymorphic_identity': 'outpatient'
    }

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True)
    # ForeignKey('patient.id'): This creates a foreign key relationship to the id column of the patient table.
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)
    diagnosis = Column(String, nullable=False)
    treatment = Column(String)
    record_date = Column(DateTime, default=datetime.utcnow)
    # Datetime allows us to print both date and time based on the universal time(datetime.utcnow)


    # Define relationship
    # "Patient" refers to another class (assumed to represent the patient table).
    # back_populates => "medical_records" means the Patient class should have a corresponding
    #                    medical_records relationship defined as well, creating a two-way link.
    
    patient = relationship("Patient", back_populates="medical_records")