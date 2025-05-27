from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text 
#from sqlalchemy.ext.declarative import declarative_base
from src.database import Base
from sqlalchemy.orm import relationship
#from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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
    # In this class we define the department model. It will be used to categorize different doctors and their specialties and patients assigned to these departments
    # It is a base class for all departments meaning it can be inherited by other classes.
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    # the head_doctor_id id a foreign key but wwe start out with a simple column first then link it with a relationship later.
    # It is nullable because not all depts may have an assigned head doctor at the time of creation
    head_doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=True, unique=True) #unique=True ensures only 1 doctor can be a department head at a time
    #Relationships for department
    doctors = relationship('Doctor', back_populates='department') # one to many relationship of one department having many doctors
    head_doctor_id = relationship('Doctor', back_populates='department_headed',
                                  foreign_keys=[head_doctor_id], uselist=False, post_update=True)
    # one to one relationship of a departent to another 
    # 'head_doctor is a relationship to the Doctor model, allowing us to access the head doctor of the department directly.
    # 'Doctor is the target model, back_populates="department_headed" is the attribute in the Doctor model that refers back to this relationship.
    # foreign_keys=[head_doctor_id] to specify which specific foreign key column in the department model is used for the relationship
    # 'uselist=False' explicitly tells SQLAlchemy this is a one-to-one relationship, so it won't return a list.
    # 'post_update=True' helps resolve potential circular dependency issues during updates, especially with nullable FKs.

    def __repr__(self):
        head_name = self.head_doctor.name if self.head_doctor else 'None'
        return f"<Department(id={self.id}, name={self.name}, head_doctor_id='{self.head_doctor_id}', head='{head_name})>"

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True)
