// frontend-hms/src/DepartmentManagement.jsx
import React, { useState, useEffect } from 'react';

// Accept API_BASE_URL as a prop
const DepartmentManagement = ({ API_BASE_URL }) => {
  const [departments, setDepartments] = useState([]);
  const [newDepartmentName, setNewDepartmentName] = useState('');
  const [newDepartmentSpecialty, setNewDepartmentSpecialty] = useState('');
  const [newDepartmentHeadDoctorId, setNewDepartmentHeadDoctorId] = useState('');
  const [editingDepartmentId, setEditingDepartmentId] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [doctors, setDoctors] = useState([]); // For head doctor dropdown
  const [isLoading, setIsLoading] = useState(false);

  // --- Fetch Departments ---
  const fetchDepartments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/departments`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setDepartments(data);
    } catch (e) {
      setError(`Failed to fetch departments: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Fetch Doctors for Dropdown ---
  const fetchDoctors = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/doctors`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setDoctors(data);
    } catch (e) {
      console.error("Failed to fetch doctors:", e);
      // Optionally, set an error state for doctors specifically
    }
  };

  useEffect(() => {
    fetchDepartments();
    fetchDoctors(); // Also fetch doctors when component mounts
  }, []);

  // --- Handle Form Submission (Add/Update) ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    const departmentData = {
      name: newDepartmentName,
      specialty: newDepartmentSpecialty || null,
      head_doctor_id: newDepartmentHeadDoctorId ? parseInt(newDepartmentHeadDoctorId, 10) : null,
    };

    try {
      let response;
      let method;
      let url;

      if (editingDepartmentId) {
        method = 'PUT';
        url = `${API_BASE_URL}/departments/${editingDepartmentId}`;
      } else {
        method = 'POST';
        url = `${API_BASE_URL}/departments`;
      }

      response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(departmentData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      // Re-fetch all departments which ensures the list is up-to-date
      await fetchDepartments();
      
      const action = editingDepartmentId ? 'updated' : 'added';
      setSuccessMessage(`Department '${newDepartmentName}' ${action} successfully!`);

      // Clear form fields and reset editing state
      setNewDepartmentName('');
      setNewDepartmentSpecialty('');
      setNewDepartmentHeadDoctorId('');
      setEditingDepartmentId(null);

    } catch (e) {
      setError(`Operation failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Handle Edit Button Click ---
  const handleEdit = (dept) => {
    setEditingDepartmentId(dept.id);
    setNewDepartmentName(dept.name);
    setNewDepartmentSpecialty(dept.specialty || '');
    setNewDepartmentHeadDoctorId(dept.head_doctor_id || '');
    setError(null);
    setSuccessMessage(null);
  };

  //  Handle Cancel Edit Button Click 
  const handleCancelEdit = () => {
    setEditingDepartmentId(null);
    setNewDepartmentName('');
    setNewDepartmentSpecialty('');
    setNewDepartmentHeadDoctorId('');
    setError(null);
    setSuccessMessage(null);
  };

  // --- Handle Delete Button Click ---
  const handleDelete = async (departmentId) => {
    if (!window.confirm('Are you sure you want to delete this department?')) {
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/departments/${departmentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      await fetchDepartments(); // Re-fetch to update list
      setSuccessMessage("Department deleted successfully!");
    } catch (e) {
      setError(`Failed to delete department: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-xl">
      <h1 className="text-3xl sm:text-4xl font-bold text-center text-blue-800 mb-8">
        Hospital Department Management
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

      {/* Department Form (Add/Update) */}
      <form onSubmit={handleSubmit} className="mb-8 p-6 bg-blue-50 rounded-lg shadow-inner">
        <h2 className="text-2xl font-semibold text-blue-700 mb-4">
          {editingDepartmentId ? 'Edit Department' : 'Add New Department'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="name" className="block text-gray-700 text-sm font-bold mb-2">
              Department Name:
            </label>
            <input
              type="text"
              id="name"
              className="shadow appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={newDepartmentName}
              onChange={(e) => setNewDepartmentName(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          <div>
            <label htmlFor="specialty" className="block text-gray-700 text-sm font-bold mb-2">
              Specialty (Optional):
            </label>
            <input
              type="text"
              id="specialty"
              className="shadow appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={newDepartmentSpecialty}
              onChange={(e) => setNewDepartmentSpecialty(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>
        <div className="mb-6">
          <label htmlFor="headDoctor" className="block text-gray-700 text-sm font-bold mb-2">
            Head Doctor (Optional):
          </label>
          <select
            id="headDoctor"
            className="shadow border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={newDepartmentHeadDoctorId}
            onChange={(e) => setNewDepartmentHeadDoctorId(e.target.value)}
            disabled={isLoading}
          >
            <option value="">-- Select a Doctor --</option>
            {doctors.map(doctor => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.name} ({doctor.specialization})
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 transition duration-200 ease-in-out flex items-center justify-center"
            disabled={isLoading}
          >
            {isLoading && <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>}
            {editingDepartmentId ? 'Update Department' : 'Add Department'}
          </button>
          {editingDepartmentId && (
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

      {/* Department List */}
      <h2 className="text-2xl font-semibold text-blue-700 mb-4">Existing Departments</h2>
      {isLoading && !departments.length ? (
        <div className="text-center text-gray-600 py-8">Loading departments...</div>
      ) : departments.length === 0 ? (
        <div className="text-center text-gray-600 py-8">No departments found. Add one above!</div>
      ) : (
        <div className="space-y-4">
          {departments.map((dept) => (
            <div key={dept.id} className="bg-white p-4 rounded-lg shadow flex flex-col sm:flex-row justify-between items-start sm:items-center">
              <div className="mb-2 sm:mb-0">
                <p className="text-lg font-medium text-gray-900">
                  <span className="font-bold text-blue-600">ID: {dept.id}</span> - {dept.name}
                </p>
                <p className="text-sm text-gray-600">Specialty: {dept.specialty || 'N/A'}</p>
                <p className="text-sm text-gray-600">Head: {dept.head_doctor_name || 'Unassigned'}</p>
                <p className="text-sm text-gray-600">Doctors in Dept: {dept.num_doctors_in_dept}</p>
                <p className="text-sm text-gray-600">Patients Assigned: {dept.num_patients_assigned}</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(dept)}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm py-1 px-3 rounded-md transition duration-200"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(dept.id)}
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

export default DepartmentManagement;
