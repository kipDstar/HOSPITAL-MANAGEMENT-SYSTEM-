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

    specialty = Column(String, nullable=False)
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
    
    # class methods
    @classmethod
    def create(cls, session, name, specialty=None, head_doctor_id=None): # Updated to accept specialty
        """
        Creates a new Department in the database.
        :param session: The SQLAlchemy session.
        :param name: The name of the department (string).
        :param specialty: The primary specialty of the department (string, optional).
        :param head_doctor_id: Optional ID of the head doctor (integer).
        :return: The newly created Department object.
        """
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
    
    #instance methods for departments
    def update_info(self, session, name=None, head_doctor_id=None):
        #what it does
        """
        updates the name or head doctor of a department
        :param session: SQLAlchemy session to commit changes
        :param name: New name for the department (is optional)
        :param head_doctor_id: New head doctor ID for the department (which is optional)
        """
        if name is not None:
            self.name = name
        if head_doctor_id is not None:
            doctor = Doctor.find_by_id(session, head_doctor_id) # to check if a doctor exists before adding him as head
            if not doctor:
                raise ValueError(f"Doctor with ID {head_doctor_id} does not exist.")
            self.head_doctor_id = head_doctor_id
        session.commit()
        
    
    def assign_head_doctor(self, session, doctor_id):
        """
        Assigns a head doctor to the department.
        :param session: SQLAlchemy session to commit changes
        :param doctor_id: ID of the doctor to be assigned as head
        """
        doctor = Doctor.find_by_id(session, doctor_id)
        if not doctor:
            raise ValueError(f"Doctor with ID {doctor_id} was not found in our system, consult ADMIN.")
        self.head_doctor_id = doctor_id
        session.commit()
    
    def unassign_head_doctor(self, session):
        """
        Unassigns the head doctor from the department.
        :param session: SQLAlchemy session to commit changes
        """
        self.head_doctor_id = None
        session.commit()
    
    def get_staff_count(self, session):
        """
        this returns the number of doctors in the department
        """
        return len(self.doctors)
    
    def assign_specialty(self, session, specialty):
        """
        Assigns a specialty to the department.
        :param session: SQLAlchemy session to commit changes
        :param specialty: Specialty to be assigned to the department
        """
        self.specialty = specialty
        session.commit()

    def specialty_doctors(self, session):
        """
        Returns a list of doctors in the department with the specified specialty.
        :param session: SQLAlchemy session to query the database
        :return: List of doctors with the specified specialty
        """
        return session.query(Doctor).filter(Doctor.department_id == self.id, Doctor.specialization == self.specialty).all()


class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)

class MedicalRecord(Base):
    __tablename__ = 'medical_records'
    id = Column(Integer, primary_key=True)
