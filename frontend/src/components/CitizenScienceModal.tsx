"use client";

import { useState } from "react";
import { X, UserCheck, MapPin } from "lucide-react";

interface CitizenScienceModalProps {
  onClose: () => void;
  lat: number;
  lon: number;
}

export default function CitizenScienceModal({ onClose, lat, lon }: CitizenScienceModalProps) {
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      // We use FormData because it's the standard for sending files, even if we're not sending one yet.
      const formData = new FormData();
      formData.append('lat', lat.toString());
      formData.append('lon', lon.toString());
      formData.append('description', description);
      formData.append('user_id', '1'); // This would be dynamic in a real login system

      const response = await fetch("http://127.0.0.1:8000/api/v1/reports/submit", {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to submit report. The server may be down.");
      }
      
      alert("Report submitted successfully! It will appear on the map shortly.");
      onClose();

    } catch (err: any) {
      console.error("Report submission failed:", err);
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-gray-800 text-white p-8 rounded-lg shadow-2xl w-full max-w-lg" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center space-x-3">
            <UserCheck size={28} className="text-blue-400" />
            <h2 className="text-3xl font-bold">Citizen Science Report</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white"><X size={28} /></button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center space-x-2 text-gray-400 bg-gray-900/50 p-2 rounded-md">
            <MapPin size={16} />
            <span>Reporting for location: {lat.toFixed(4)}, {lon.toFixed(4)}</span>
          </div>
          
          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-1">Description of Event</label>
            <textarea
              id="description"
              rows={4}
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="w-full bg-gray-700 p-2 rounded-md border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Heavy smoke from a vehicle on Main St."
              required
            />
          </div>

          <div>
            <label htmlFor="image" className="block text-sm font-medium mb-1">Upload Image (Optional)</label>
            <input type="file" id="image" className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"/>
          </div>
          
          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button type="submit" className="w-full bg-blue-600 p-3 rounded-md font-bold hover:bg-blue-700 transition-colors disabled:bg-gray-500" disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>
      </div>
    </div>
  );
}

