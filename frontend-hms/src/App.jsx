// App.jsx
// This is the main React component for your Hospital Management Frontend.
// It will manage different sections of the application:
// Department Management, Patient Management, and Patient Self-Registration.

import React, { useState, useEffect } from 'react';
import PatientManagement from './PatientManagement'; // Assuming you'll create this component
import PatientSelfRegistration from './PatientSelfRegistration'; // Assuming you'll create this component

// Main App component
const App = () => {
  // State to store the list of departments fetched from the API
  const [departments, setDepartments] = useState([]);
  // State to manage the form input for adding/updating departments
  const [newDepartmentName, setNewDepartmentName] = useState('');
  const [newDepartmentSpecialty, setNewDepartmentSpecialty] = useState('');
  const [newDepartmentHeadDoctorId, setNewDepartmentHeadDoctorId] = useState('');
  // State to track which department is being edited (null if not editing)
  const [editingDepartmentId, setEditingDepartmentId] = useState(null);
  // State to store any error messages from API calls
  const [error, setError] = useState(null);
  // State to store success messages
  const [successMessage, setSuccessMessage] = useState(null);
  // State to store the list of doctors for the head doctor dropdown
  const [doctors, setDoctors] = useState([]);
  // State for loading indicators
  const [isLoading, setIsLoading] = useState(false);

  // NEW: State to manage the active view
  const [activeView, setActiveView] = useState('departments'); // 'departments', 'patients', 'self-register'

  // --- API Base URL ---
  // IMPORTANT: Replace with your Render API URL when deployed!
  // For local development, it's usually http://localhost:5000
  const API_BASE_URL = 'http://localhost:5000';

  // --- Fetch Departments ---
  // useEffect hook to fetch departments when the component mounts or data changes
  useEffect(() => {
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

    // Only fetch departments if the active view is 'departments'
    if (activeView === 'departments') {
        fetchDepartments();
    }
  }, [activeView]); // Re-run when activeView changes

  // --- Fetch Doctors for Dropdown ---
  useEffect(() => {
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

    // Fetch doctors regardless of the active view as they might be needed for PatientManagement too
    fetchDoctors();
  }, []); // Fetch doctors once on component mount, they are relatively static

  // --- Handle Form Submission (Add/Update Department) ---
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior (page reload)
    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    const departmentData = {
      name: newDepartmentName,
      specialty: newDepartmentSpecialty || null, // Send null if empty
      head_doctor_id: newDepartmentHeadDoctorId ? parseInt(newDepartmentHeadDoctorId, 10) : null, // Convert to int or null
    };

    try {
      let response;
      let method;
      let url;

      if (editingDepartmentId) {
        // Update existing department
        method = 'PUT';
        url = `${API_BASE_URL}/departments/${editingDepartmentId}`;
        response = await fetch(url, {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(departmentData),
        });
      } else {
        // Add new department
        method = 'POST';
        url = `${API_BASE_URL}/departments`;
        response = await fetch(url, {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(departmentData),
        });
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const updatedDept = await response.json();

      if (editingDepartmentId) {
        // Update the list of departments in state
        setDepartments(departments.map(dept => 
          dept.id === editingDepartmentId ? updatedDept : dept
        ));
        setSuccessMessage(`Department '${updatedDept.name}' updated successfully!`);
      } else {
        // Add the new department to the list in state
        setDepartments([...departments, updatedDept]);
        setSuccessMessage(`Department '${updatedDept.name}' added successfully!`);
      }

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

  // --- Handle Edit Button Click (Department) ---
  const handleEdit = (dept) => {
    setEditingDepartmentId(dept.id);
    setNewDepartmentName(dept.name);
    setNewDepartmentSpecialty(dept.specialty || ''); // Ensure it's not null for input
    setNewDepartmentHeadDoctorId(dept.head_doctor_id || ''); // Ensure it's not null for input
    setError(null);
    setSuccessMessage(null);
  };

  // --- Handle Cancel Edit Button Click (Department) ---
  const handleCancelEdit = () => {
    setEditingDepartmentId(null);
    setNewDepartmentName('');
    setNewDepartmentSpecialty('');
    setNewDepartmentHeadDoctorId('');
    setError(null);
    setSuccessMessage(null);
  };

  // --- Handle Delete Button Click (Department) ---
  const handleDelete = async (departmentId) => {
    // Using window.confirm for simplicity, but for a real app, use a custom modal UI
    if (!window.confirm('Are you sure you want to delete this department?')) {
      return; // User cancelled
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

      // Filter out the deleted department from the state
      setDepartments(departments.filter(dept => dept.id !== departmentId));
      setSuccessMessage("Department deleted successfully!");
    } catch (e) {
      setError(`Failed to delete department: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8 font-sans antialiased">
      <div className="max-w-4xl mx-auto bg-white bg-opacity-90 p-6 rounded-lg shadow-xl">
        <h1 className="text-3xl sm:text-4xl font-bold text-center text-blue-800 mb-8">
          Hospital Management Dashboard
        </h1>

        {/* --- Navigation Buttons --- */}
        <div className="flex justify-center space-x-4 mb-8">
          <button
            onClick={() => setActiveView('departments')}
            className={`py-2 px-4 rounded-md text-lg font-semibold transition duration-300 ${activeView === 'departments' ? 'bg-blue-700 text-white shadow-md' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            Department Management
          </button>
          <button
            onClick={() => setActiveView('patients')}
            className={`py-2 px-4 rounded-md text-lg font-semibold transition duration-300 ${activeView === 'patients' ? 'bg-blue-700 text-white shadow-md' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            Patient Management
          </button>
          <button
            onClick={() => setActiveView('self-register')}
            className={`py-2 px-4 rounded-md text-lg font-semibold transition duration-300 ${activeView === 'self-register' ? 'bg-blue-700 text-white shadow-md' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            Patient Self-Registration
          </button>
        </div>

        {/* --- Render Active View --- */}
        {activeView === 'departments' && (
          <>
            {/* --- Messages --- */}
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

            {/* --- Department Form (Add/Update) --- */}
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
                  className="shadow appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

            {/* --- Department List --- */}
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
                      <p className="text-sm text-gray-600">Doctors: {dept.num_doctors_in_dept}</p>
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
          </>
        )}

        {/* Render Patient Management component when activeView is 'patients' */}
        {activeView === 'patients' && <PatientManagement doctors={doctors} departments={departments} apiBaseUrl={API_BASE_URL} />}

        {/* Render Patient Self-Registration component when activeView is 'self-register' */}
        {activeView === 'self-register' && <PatientSelfRegistration apiBaseUrl={API_BASE_URL} />}
      </div>
    </div>
  );
};

export default App;
