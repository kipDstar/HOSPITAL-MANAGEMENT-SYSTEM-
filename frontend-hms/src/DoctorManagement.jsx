// frontend-hms/src/DoctorManagement.jsx
import React, { useState, useEffect } from 'react';

// Accept API_BASE_URL as a prop
const DoctorManagement = ({ API_BASE_URL }) => {
  const [doctors, setDoctors] = useState([]);
  const [newDoctorName, setNewDoctorName] = useState('');
  const [newDoctorSpecialization, setNewDoctorSpecialization] = useState('');
  const [newDoctorDepartmentId, setNewDoctorDepartmentId] = useState(''); // New: for assigning doctor to a department
  const [editingDoctorId, setEditingDoctorId] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [departments, setDepartments] = useState([]); // For department dropdown

  // --- Fetch Doctors ---
  const fetchDoctors = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/doctors`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setDoctors(data);
    } catch (e) {
      setError(`Failed to fetch doctors: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Fetch Departments for Dropdown ---
  const fetchDepartments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/departments`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setDepartments(data);
    } catch (e) {
      console.error("Failed to fetch departments:", e);
    }
  };

  useEffect(() => {
    fetchDoctors();
    fetchDepartments(); // Fetch departments on mount
  }, []);

  // --- Handle Form Submission (Add/Update Doctor) ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    const doctorData = {
      name: newDoctorName,
      specialization: newDoctorSpecialization || null,
      department_id: newDoctorDepartmentId ? parseInt(newDoctorDepartmentId, 10) : null, // New field
    };

    try {
      let response;
      let method;
      let url;

      if (editingDoctorId) {
        method = 'PUT';
        url = `${API_BASE_URL}/doctors/${editingDoctorId}`;
      } else {
        method = 'POST';
        url = `${API_BASE_URL}/doctors`;
      }

      response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(doctorData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      await fetchDoctors(); // Re-fetch all doctors to update list
      
      const action = editingDoctorId ? 'updated' : 'added';
      setSuccessMessage(`Doctor '${newDoctorName}' ${action} successfully!`);

      setNewDoctorName('');
      setNewDoctorSpecialization('');
      setNewDoctorDepartmentId(''); // Clear new field
      setEditingDoctorId(null);

    } catch (e) {
      setError(`Operation failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Handle Edit & Delete ---
  const handleEdit = (doctor) => {
    setEditingDoctorId(doctor.id);
    setNewDoctorName(doctor.name);
    setNewDoctorSpecialization(doctor.specialization || '');
    setNewDoctorDepartmentId(doctor.department_id || ''); // Set new field for edit
    setError(null);
    setSuccessMessage(null);
  };

  const handleCancelEdit = () => {
    setEditingDoctorId(null);
    setNewDoctorName('');
    setNewDoctorSpecialization('');
    setNewDoctorDepartmentId(''); // Clear new field
    setError(null);
    setSuccessMessage(null);
  };

  const handleDelete = async (doctorId) => {
    if (!window.confirm('Are you sure you want to delete this doctor?')) {
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/doctors/${doctorId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      await fetchDoctors(); // Re-fetch to update list
      setSuccessMessage("Doctor deleted successfully!");
    } catch (e) {
      setError(`Failed to delete doctor: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="p-4 bg-white rounded-lg shadow-xl">
      <h1 className="text-3xl sm:text-4xl font-bold text-center text-green-800 mb-8">
        Doctor Management
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

      {/* Doctor Form (Add/Update) */}
      <form onSubmit={handleSubmit} className="mb-8 p-6 bg-green-50 rounded-lg shadow-inner">
        <h2 className="text-2xl font-semibold text-green-700 mb-4">
          {editingDoctorId ? 'Edit Doctor' : 'Add New Doctor'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="doctorName" className="block text-gray-700 text-sm font-bold mb-2">
              Doctor Name:
            </label>
            <input
              type="text"
              id="doctorName"
              className="shadow appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              value={newDoctorName}
              onChange={(e) => setNewDoctorName(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          <div>
            <label htmlFor="doctorSpecialization" className="block text-gray-700 text-sm font-bold mb-2">
              Specialization (Optional):
            </label>
            <input
              type="text"
              id="doctorSpecialization"
              className="shadow appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              value={newDoctorSpecialization}
              onChange={(e) => setNewDoctorSpecialization(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>
        <div className="mb-6">
          <label htmlFor="doctorDepartment" className="block text-gray-700 text-sm font-bold mb-2">
            Assigned Department (Optional):
          </label>
          <select
            id="doctorDepartment"
            className="shadow border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            value={newDoctorDepartmentId}
            onChange={(e) => setNewDoctorDepartmentId(e.target.value)}
            disabled={isLoading}
          >
            <option value="">-- Select a Department --</option>
            {departments.map(dept => (
              <option key={dept.id} value={dept.id}>
                {dept.name} ({dept.specialty || 'General'})
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            type="submit"
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-75 transition duration-200 ease-in-out flex items-center justify-center"
            disabled={isLoading}
          >
            {isLoading && <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>}
            {editingDoctorId ? 'Update Doctor' : 'Add Doctor'}
          </button>
          {editingDoctorId && (
            <button
              type="button"
              onClick={handleCancelEdit}
              className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-opacity-75 transition duration-200 ease-in-out flex items-center justify-center"
              disabled={isLoading}
            >
              Cancel Edit
            </button>
          )}
        </div>
      </form>

      {/* Doctor List */}
      <h2 className="text-2xl font-semibold text-green-700 mb-4">Existing Doctors</h2>
      {isLoading && !doctors.length ? (
        <div className="text-center text-gray-600 py-8">Loading doctors...</div>
      ) : doctors.length === 0 ? (
        <div className="text-center text-gray-600 py-8">No doctors found. Add one above!</div>
      ) : (
        <div className="space-y-4">
          {doctors.map((doc) => (
            <div key={doc.id} className="bg-white p-4 rounded-lg shadow flex flex-col sm:flex-row justify-between items-start sm:items-center">
              <div className="mb-2 sm:mb-0">
                <p className="text-lg font-medium text-gray-900">
                  <span className="font-bold text-green-600">ID: {doc.id}</span> - {doc.name}
                </p>
                <p className="text-sm text-gray-600">Specialization: {doc.specialization || 'N/A'}</p>
                <p className="text-sm text-gray-600">Department: {doc.department_name || 'Unassigned'}</p>
                <p className="text-sm text-gray-600">Heads: {doc.departments_headed_count} Depts</p>
                <p className="text-sm text-gray-600">Assigned Patients: {doc.patients_assigned_count}</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(doc)}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm py-1 px-3 rounded-md transition duration-200"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="bg-red-500 hover:bg-red-600 text-white text-sm py-1 px-3 rounded-md transition duration-200"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DoctorManagement;
