"use client";

import React, { useState } from 'react';

// Define the type for the props, which includes the function to close the modal
interface RegistrationModalProps {
  onClose: () => void;
}

export default function RegistrationModal({ onClose }: RegistrationModalProps) {
  const [name, setName] = useState('');
  const [ageGroup, setAgeGroup] = useState('');
  const [persona, setPersona] = useState('');
  const [healthConditions, setHealthConditions] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCheckboxChange = (condition: string) => {
    setHealthConditions(prev =>
      prev.includes(condition)
        ? prev.filter(c => c !== condition)
        : [...prev, condition]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    // Package all the data from the form's state
    const userProfile = {
      name: name,
      age_group: ageGroup,
      persona: persona,
      healthConditions: healthConditions,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/users/register", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userProfile),
      });

      if (!response.ok) {
        throw new Error("Failed to save profile. Please try again.");
      }

      const result = await response.json();
      console.log("Profile saved successfully:", result);
      onClose(); // Close the modal after successful submission

    } catch (err: any) {
      console.error("Registration error:", err);
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 text-white p-8 rounded-lg shadow-2xl w-full max-w-md">
        <h2 className="text-3xl font-bold mb-2">Welcome to AURA</h2>
        <p className="text-gray-400 mb-6">Create your profile to get personalized air quality insights.</p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-1">
              What should we call you?
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Paramveer"
              required
            />
          </div>

          <div>
            <label htmlFor="age-group" className="block text-sm font-medium text-gray-300 mb-1">
              Age Group
            </label>
            <select
              id="age-group"
              value={ageGroup}
              onChange={e => setAgeGroup(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2"
            >
              <option value="">Select...</option>
              <option value="Under 18">Under 18</option>
              <option value="18-35">18-35</option>
              <option value="36-55">36-55</option>
              <option value="Over 55">Over 55</option>
            </select>
          </div>

          <div>
            <label htmlFor="persona" className="block text-sm font-medium text-gray-300 mb-1">
              Your Persona
            </label>
            <select
              id="persona"
              value={persona}
              onChange={e => setPersona(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2"
            >
              <option value="">Select...</option>
              <option value="Concerned Citizen">Concerned Citizen</option>
              <option value="Athlete / Health Enthusiast">Athlete / Health Enthusiast</option>
              <option value="Parent">Parent</option>
              <option value="Policy Maker / Researcher">Policy Maker / Researcher</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Do you have any health sensitivities? (Optional)
            </label>
            <div className="space-y-2">
              {['Asthma', 'Allergies', 'Heart Condition', 'Pregnancy'].map(condition => (
                <label key={condition} className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    onChange={() => handleCheckboxChange(condition)}
                    className="h-5 w-5 rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
                  />
                  <span>{condition}</span>
                </label>
              ))}
            </div>
          </div>
          
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-500 text-white font-bold py-3 rounded-md transition-colors"
          >
            {isSubmitting ? 'Saving...' : 'Save Profile & Begin'}
          </button>
        </form>
      </div>
    </div>
  );
}