from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text 
#from sqlalchemy.ext.declarative import declarative_base
from src.database import Base
from sqlalchemy.orm import relationship
#Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)

class InPatient(Patient):
    __tablename__ = 'inpatients'
    id = Column(Integer, primary_key=True)

class OutPatient(Patient):
    __tablename__ = 'outpatients'
    id = Column(Integer, primary_key=True)

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