"use client";

import { useState, useEffect } from "react";
import { X, TestTube2, LineChart as LineChartIcon } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

interface ForecastModalProps {
  onClose: () => void;
  lat: number;
  lon: number;
}

interface ForecastDataPoint {
  hour: string;
  predicted_aqi: number;
}

export default function ForecastModal({ onClose, lat, lon }: ForecastModalProps) {
  const [forecastData, setForecastData] = useState<ForecastDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const generateForecast = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/forecast/point?lat=${lat}&lon=${lon}`);
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        setForecastData(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    generateForecast();
  }, [lat, lon]);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div 
        className="bg-gray-800 text-white p-8 rounded-lg shadow-2xl w-full max-w-3xl h-[80vh] flex flex-col" 
        onClick={e => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
          <div className="flex items-center space-x-3">
            <TestTube2 size={28} className="text-blue-400" />
            <h2 className="text-3xl font-bold">Predictive Forecast Model</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X size={28} />
          </button>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          {isLoading && <p>Generating forecast...</p>}
          {error && <p className="text-red-400">Error: {error}</p>}
          {!isLoading && !error && forecastData.length > 0 && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecastData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
                <XAxis dataKey="hour" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" domain={[0, 'dataMax + 20']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(31, 41, 55, 0.8)', borderColor: '#4a5568', borderRadius: '0.5rem' }} 
                />
                <Legend />
                <Line type="monotone" dataKey="predicted_aqi" name="Predicted AQI" stroke="#8884d8" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
