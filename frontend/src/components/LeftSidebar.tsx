"use client";

import { useState, useEffect } from "react";
import { User, Layers3, Wind, Leaf, TowerControl } from "lucide-react";

// Define the types for the component's props
interface LeftSidebarProps {
  activeLayer: string;
  onLayerChange: (layerId: string) => void;
  onProfileClick: () => void;
}

// Helper to map layer names to icons
const PollutantIcon = ({ name }: { name: string }) => {
  if (name.includes('Stations')) return <TowerControl size={20} />;
  if (name.includes('Wind')) return <Wind size={20} />;
  if (name.includes('AQI')) return <Layers3 size={20} />;
  return <Leaf size={20} />; // Default icon for other pollutants
};

export default function LeftSidebar({ activeLayer, onLayerChange, onProfileClick }: LeftSidebarProps) {
  // State to hold the list of layers fetched from the backend
  const [pollutantOptions, setPollutantOptions] = useState<string[]>([]);

  // This effect runs once to fetch the available pollutants from our API
  useEffect(() => {
    const fetchPollutants = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/pollutants/available");
        const data = await response.json();
        // Add "AQI Heatmap", "Live Stations", and "Wind Flow" as default options
        setPollutantOptions(["AQI Heatmap", "Live Stations", "Wind Flow", ...data]);
      } catch (error) {
        console.error("Failed to fetch available pollutants:", error);
        // Fallback to default options if API fails
        setPollutantOptions(["AQI Heatmap", "Live Stations", "Wind Flow"]);
      }
    };
    fetchPollutants();
  }, []); // Empty array ensures this runs only once

  // Helper to get the correct ID for the layer
  const getLayerId = (name: string) => {
    if (name.includes('Stations')) return 'stations';
    if (name.includes('AQI')) return 'aqi';
    if (name.includes('Wind')) return 'wind';
    return name.toLowerCase();
  };

  return (
    <div className="absolute top-4 left-4 z-10 flex flex-col space-y-4">
      <button 
        onClick={onProfileClick}
        className="bg-gray-800 p-3 rounded-full text-white shadow-lg hover:bg-gray-700 transition-colors"
        aria-label="Open Profile"
      >
        <User size={24} />
      </button>

      <div className="bg-gray-800 p-2 rounded-lg text-white shadow-lg space-y-1">
        {pollutantOptions.map(name => {
          const id = getLayerId(name);
          return (
            <button
              key={id}
              onClick={() => onLayerChange(id)}
              className={`flex items-center space-x-3 w-full text-left p-2 rounded-md transition-colors ${
                activeLayer === id
                  ? 'bg-blue-600'
                  : 'hover:bg-gray-700'
              }`}
            >
              <PollutantIcon name={name} />
              <span className="font-medium">{name}</span>
            </button>
          )
        })}
      </div>
    </div>
  );
}

