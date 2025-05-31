// frontend-hms/src/PatientSelfRegistration.jsx
import React, { useState } from 'react';

const PatientSelfRegistration = ({ apiBaseUrl }) => {
  const [name, setName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState(''); // YYYY-MM-DD
  const [contactInfo, setContactInfo] = useState('');
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
   const API_BASE_URL = apiBaseUrl || 'http://localhost:5000/api'; // Default to local server if not provided

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    const patientData = {
      name: name,
      date_of_birth: dateOfBirth,
      contact_info: contactInfo,
      // Patient type is automatically outpatient and doctor/department unassigned by backend
    };

    try {
      const response = await fetch(`${API_BASE_URL}/patients/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const registeredPatient = await response.json();
      setSuccessMessage(`Registration successful! Welcome, ${registeredPatient.name}. Your ID is ${registeredPatient.id}. You are an Outpatient.`);
      
      // Clear form
      setName('');
      setDateOfBirth('');
      setContactInfo('');

    } catch (e) {
      setError(`Registration failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-xl">
      <h1 className="text-3xl sm:text-4xl font-bold text-center text-indigo-800 mb-8">
        Patient Self-Registration
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

      <form onSubmit={handleSubmit} className="mb-8 p-6 bg-indigo-50 rounded-lg shadow-inner">
        <h2 className="text-2xl font-semibold text-indigo-700 mb-4">Register as a New Patient</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="regName" className="block text-gray-700 text-sm font-bold mb-2">Full Name:</label>
            <input type="text" id="regName" className="form-input" value={name} onChange={(e) => setName(e.target.value)} required disabled={isLoading} />
          </div>
          <div>
            <label htmlFor="regDob" className="block text-gray-700 text-sm font-bold mb-2">Date of Birth:</label>
            <input type="date" id="regDob" className="form-input" value={dateOfBirth} onChange={(e) => setDateOfBirth(e.target.value)} required disabled={isLoading} />
          </div>
        </div>
        <div className="mb-6">
          <label htmlFor="regContact" className="block text-gray-700 text-sm font-bold mb-2">Contact Info (Phone/Email):</label>
          <input type="text" id="regContact" className="form-input" value={contactInfo} onChange={(e) => setContactInfo(e.target.value)} required disabled={isLoading} />
        </div>
        <div className="flex justify-center">
          <button
            type="submit"
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-75 transition duration-200 ease-in-out flex items-center justify-center"
            disabled={isLoading}
          >
            {isLoading && <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>}
            Register Me
          </button>
        </div>
      </form>
      {/* Tailwind form-input classes (for consistency) */}
      <style>{`
        .form-input {
          @apply shadow appearance-none border rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent;
        }
      `}</style>
    </div>
  );
};

export default PatientSelfRegistration;
// Note: This component assumes that the API_BASE_URL prop is passed from a parent component or context.