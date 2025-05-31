// frontend-hms/src/PatientManagement.jsx
import React, { useState, useEffect } from 'react';

const PatientManagement = ({ apiBaseUrl }) => {
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
    const API_BASE_URL = apiBaseUrl || 'http://localhost:5000/api'; // Default to local server if not provided
  // Form states
  const [newName, setNewName] = useState('');
  const [newDob, setNewDob] = useState(''); // YYYY-MM-DD
  const [newContactInfo, setNewContactInfo] = useState('');
  const [newPatientType, setNewPatientType] = useState('outpatient'); // Default to outpatient
  const [newAssignedDoctorId, setNewAssignedDoctorId] = useState('');
  const [newAssignedDepartmentId, setNewAssignedDepartmentId] = useState('');

  // Inpatient specific
  const [newRoomNumber, setNewRoomNumber] = useState('');
  const [newAdmissionDate, setNewAdmissionDate] = useState(''); // YYYY-MM-DD
  const [newDischargeDate, setNewDischargeDate] = useState(''); // YYYY-MM-DD

  // Outpatient specific
  const [newLastVisitDate, setNewLastVisitDate] = useState(''); // YYYY-MM-DD

  const [editingPatientId, setEditingPatientId] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // --- Fetch Data (Patients, Doctors, Departments) ---
  const fetchPatients = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/patients`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPatients(data);
    } catch (e) {
      setError(`Failed to fetch patients: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDoctorsAndDepartments = async () => {
    try {
      const [doctorsRes, departmentsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/doctors`),
        fetch(`${API_BASE_URL}/departments`)
      ]);

      if (!doctorsRes.ok) throw new Error(`HTTP error! status: ${doctorsRes.status} for doctors`);
      if (!departmentsRes.ok) throw new Error(`HTTP error! status: ${departmentsRes.status} for departments`);

      const doctorsData = await doctorsRes.json();
      const departmentsData = await departmentsRes.json();
      
      setDoctors(doctorsData);
      setDepartments(departmentsData);
    } catch (e) {
      console.error("Failed to fetch doctors/departments:", e);
      setError(`Failed to load doctor/department options: ${e.message}`);
    }
  };

  useEffect(() => {
    fetchPatients();
    fetchDoctorsAndDepartments();
  }, []);

  // --- Reset Form Fields ---
  const resetForm = () => {
    setNewName('');
    setNewDob('');
    setNewContactInfo('');
    setNewPatientType('outpatient');
    setNewAssignedDoctorId('');
    setNewAssignedDepartmentId('');
    setNewRoomNumber('');
    setNewAdmissionDate('');
    setNewDischargeDate('');
    setNewLastVisitDate('');
    setEditingPatientId(null);
    setError(null);
    setSuccessMessage(null);
  };

  // --- Handle Form Submission (Add/Update Patient) ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    let patientData = {
      name: newName,
      date_of_birth: newDob,
      contact_info: newContactInfo,
      patient_type: newPatientType,
      assigned_doctor_id: newAssignedDoctorId ? parseInt(newAssignedDoctorId, 10) : null,
      assigned_department_id: newAssignedDepartmentId ? parseInt(newAssignedDepartmentId, 10) : null,
    };

    if (newPatientType === 'inpatient') {
      patientData = {
        ...patientData,
        room_number: newRoomNumber,
        admission_date: newAdmissionDate || new Date().toISOString().split('T')[0], // Default today
        discharge_date: newDischargeDate || null,
      };
    } else { // outpatient
      patientData = {
        ...patientData,
        last_visit_date: newLastVisitDate || new Date().toISOString().split('T')[0], // Default today
      };
    }

    try {
      let response;
      let method;
      let url;

      if (editingPatientId) {
        method = 'PUT';
        url = `${API_BASE_URL}/patients/${editingPatientId}`;
      } else {
        method = 'POST';
        url = `${API_BASE_URL}/patients`;
      }

      response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      await fetchPatients(); // Re-fetch to update the list
      const action = editingPatientId ? 'updated' : 'added';
      setSuccessMessage(`Patient '${newName}' ${action} successfully!`);
      resetForm();

    } catch (e) {
      setError(`Operation failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Handle Edit Button Click ---
  const handleEdit = (patient) => {
    setEditingPatientId(patient.id);
    setNewName(patient.name);
    setNewDob(patient.date_of_birth);
    setNewContactInfo(patient.contact_info);
    setNewPatientType(patient.patient_type);
    setNewAssignedDoctorId(patient.assigned_doctor_id || '');
    setNewAssignedDepartmentId(patient.assigned_department_id || '');

    if (patient.patient_type === 'inpatient') {
      setNewRoomNumber(patient.room_number || '');
      setNewAdmissionDate(patient.admission_date || '');
      setNewDischargeDate(patient.discharge_date || '');
      setNewLastVisitDate(''); // Clear outpatient specific field
    } else { // outpatient
      setNewLastVisitDate(patient.last_visit_date || '');
      setNewRoomNumber(''); // Clear inpatient specific fields
      setNewAdmissionDate('');
      setNewDischargeDate('');
    }
    setError(null);
    setSuccessMessage(null);
  };

  // --- Handle Delete Button Click ---
  const handleDelete = async (patientId) => {
    if (!window.confirm('Are you sure you want to delete this patient?')) {
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/patients/${patientId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      await fetchPatients(); // Re-fetch to update list
      setSuccessMessage("Patient deleted successfully!");
    } catch (e) {
      setError(`Failed to delete patient: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-xl">
      <h1 className="text-3xl sm:text-4xl font-bold text-center text-purple-800 mb-8">
        Patient Management (Admin)
      </h1>

      {/* Messages */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md relative mb-4" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}
      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-md relative mb-4" role="alert">
          <strong className="font-bold">Success!</strong>
          <span className="block sm:inline"> {successMessage}</span>
        </div>
      )}

      {/* Patient Form (Add/Update) */}
      <form onSubmit={handleSubmit} className="mb-8 p-6 bg-purple-50 rounded-lg shadow-inner">
        <h2 className="text-2xl font-semibold text-purple-700 mb-4">
          {editingPatientId ? 'Edit Patient' : 'Register New Patient'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="patientName" className="block text-gray-700 text-sm font-bold mb-2">Name:</label>
            <input type="text" id="patientName" className="form-input" value={newName} onChange={(e) => setNewName(e.target.value)} required disabled={isLoading} />
          </div>
          <div>
            <label htmlFor="patientDob" className="block text-gray-700 text-sm font-bold mb-2">Date of Birth:</label>
            <input type="date" id="patientDob" className="form-input" value={newDob} onChange={(e) => setNewDob(e.target.value)} required disabled={isLoading} />
          </div>
          <div>
            <label htmlFor="patientContact" className="block text-gray-700 text-sm font-bold mb-2">Contact Info:</label>
            <input type="text" id="patientContact" className="form-input" value={newContactInfo} onChange={(e) => setNewContactInfo(e.target.value)} disabled={isLoading} />
          </div>
          <div>
            <label htmlFor="patientType" className="block text-gray-700 text-sm font-bold mb-2">Patient Type:</label>
            <select id="patientType" className="form-select" value={newPatientType} onChange={(e) => setNewPatientType(e.target.value)} disabled={isLoading}>
              <option value="outpatient">Outpatient</option>
              <option value="inpatient">Inpatient</option>
            </select>
          </div>
        </div>

        {/* Type-specific fields */}
        {newPatientType === 'inpatient' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 p-4 bg-purple-100 rounded-md">
            <div>
              <label htmlFor="roomNumber" className="block text-gray-700 text-sm font-bold mb-2">Room Number:</label>
              <input type="text" id="roomNumber" className="form-input" value={newRoomNumber} onChange={(e) => setNewRoomNumber(e.target.value)} required={newPatientType === 'inpatient'} disabled={isLoading} />
            </div>
            <div>
              <label htmlFor="admissionDate" className="block text-gray-700 text-sm font-bold mb-2">Admission Date:</label>
              <input type="date" id="admissionDate" className="form-input" value={newAdmissionDate} onChange={(e) => setNewAdmissionDate(e.target.value)} disabled={isLoading} />
            </div>
            <div>
              <label htmlFor="dischargeDate" className="block text-gray-700 text-sm font-bold mb-2">Discharge Date (Optional):</label>
              <input type="date" id="dischargeDate" className="form-input" value={newDischargeDate} onChange={(e) => setNewDischargeDate(e.target.value)} disabled={isLoading} />
            </div>
          </div>
        )}
        {newPatientType === 'outpatient' && (
          <div className="mb-4 p-4 bg-purple-100 rounded-md">
            <label htmlFor="lastVisitDate" className="block text-gray-700 text-sm font-bold mb-2">Last Visit Date:</label>
            <input type="date" id="lastVisitDate" className="form-input" value={newLastVisitDate} onChange={(e) => setNewLastVisitDate(e.target.value)} disabled={isLoading} />
          </div>
        )}

        {/* Assigned Doctor & Department */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label htmlFor="assignedDoctor" className="block text-gray-700 text-sm font-bold mb-2">Assigned Doctor (Optional):</label>
            <select id="assignedDoctor" className="form-select" value={newAssignedDoctorId} onChange={(e) => setNewAssignedDoctorId(e.target.value)} disabled={isLoading}>
              <option value="">-- Select Doctor --</option>
              {doctors.map(doc => (
                <option key={doc.id} value={doc.id}>{doc.name} ({doc.specialization})</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="assignedDepartment" className="block text-gray-700 text-sm font-bold mb-2">Assigned Department (Optional):</label>
            <select id="assignedDepartment" className="form-select" value={newAssignedDepartmentId} onChange={(e) => setNewAssignedDepartmentId(e.target.value)} disabled={isLoading}>
              <option value="">-- Select Department --</option>
              {departments.map(dept => (
                <option key={dept.id} value={dept.id}>{dept.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            type="submit"
            className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-75 transition duration-200 ease-in-out flex items-center justify-center"
            disabled={isLoading}
          >
            {isLoading && <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>}
            {editingPatientId ? 'Update Patient' : 'Register Patient'}
          </button>
          {editingPatientId && (
            <button
              type="button"
              onClick={resetForm}
              className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-opacity-75 transition duration-200 ease-in-out flex items-center justify-center"
              disabled={isLoading}
            >
              Cancel Edit
            </button>
          )}
        </div>
      </form>

      {/* Patient List */}
      <h2 className="text-2xl font-semibold text-purple-700 mb-4">Existing Patients</h2>
      {isLoading && !patients.length ? (
        <div className="text-center text-gray-600 py-8">Loading patients...</div>
      ) : patients.length === 0 ? (
        <div className="text-center text-gray-600 py-8">No patients found. Register one above!</div>
      ) : (
        <div className="space-y-4">
          {patients.map((patient) => (
            <div key={patient.id} className="bg-white p-4 rounded-lg shadow flex flex-col sm:flex-row justify-between items-start sm:items-center">
              <div className="mb-2 sm:mb-0">
                <p className="text-lg font-medium text-gray-900">
                  <span className="font-bold text-purple-600">ID: {patient.id}</span> - {patient.name} ({patient.patient_type})
                </p>
                <p className="text-sm text-gray-600">DOB: {patient.date_of_birth}</p>
                <p className="text-sm text-gray-600">Contact: {patient.contact_info || 'N/A'}</p>
                {patient.patient_type === 'inpatient' && (
                  <>
                    <p className="text-sm text-gray-600">Room: {patient.room_number || 'N/A'}</p>
                    <p className="text-sm text-gray-600">Adm Date: {patient.admission_date || 'N/A'}</p>
                    <p className="text-sm text-gray-600">Discharge Date: {patient.discharge_date || 'N/A'}</p>
                  </>
                )}
                {patient.patient_type === 'outpatient' && (
                  <p className="text-sm text-gray-600">Last Visit: {patient.last_visit_date || 'N/A'}</p>
                )}
                <p className="text-sm text-gray-600">Assigned Doctor: {patient.assigned_doctor_name || 'Unassigned'}</p>
                <p className="text-sm text-gray-600">Assigned Dept: {patient.assigned_department_name || 'Unassigned'}</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(patient)}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm py-1 px-3 rounded-md transition duration-200"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(patient.id)}
                  className="bg-red-500 hover:bg-red-600 text-white text-sm py-1 px-3 rounded-md transition duration-200"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      {/* Tailwind form-input and form-select classes (for consistency) */}
      <style>{`
        .form-input, .form-select {
          @apply shadow appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent;
        }
      `}</style>
    </div>
  );
};

export default PatientManagement;
// Note: Ensure you have the necessary CSS for Tailwind classes in your project.