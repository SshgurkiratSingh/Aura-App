"use client";

import { useState } from "react";
import { ViewState } from "react-map-gl";
import DataPanel from "@/components/DataPanel";
import MapContainer from "@/components/MapContainer";
import RegistrationModal from "@/components/RegistrationModal";
import LeftSidebar from "@/components/LeftSidebar";
import ProfileModal from "@/components/ProfileModal";
import TimeScrubber from "@/components/TimeScrubber";
import AuraGuideButton from "@/components/AuraGuideButton";
import AuraGuideChat from "@/components/AuraGuideChat";
import Header from "@/components/Header";
import ForecastModal from "@/components/Forecast_modal";
import PolicySimulatorModal from "@/components/PolicySimulatorModal";
import CitizenScienceModal from "@/components/CitizenScienceModal"; // 1. Import the final modal

// Define a flexible type for our location data to handle different API responses
export type LocationData = any; 

// Define a type for the empty map click event
interface CoordinateClickInfo {
  coordinate: [longitude: number, latitude: number];
}

// Define a type for the station pin click event
interface StationClickInfo {
    uid: number;
    lat: number;
    lon: number;
    aqi: string;
    name: string;
}

// The complete, correct initial state for the map
const INITIAL_VIEW_STATE: ViewState = {
    longitude: 77.2090, latitude: 28.6139,
    zoom: 4, pitch: 0, bearing: 0,
    padding: { top: 0, right: 0, bottom: 0, left: 0 }
};

export default function Home() {
  const [selectedLocation, setSelectedLocation] = useState<LocationData | null>(null);
  const [viewState, setViewState] = useState<ViewState>(INITIAL_VIEW_STATE);
  const [activeLayer, setActiveLayer] = useState("aqi");
  const [timeOffset, setTimeOffset] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isForecastModalOpen, setIsForecastModalOpen] = useState(false);
  const [isPolicyModalOpen, setIsPolicyModalOpen] = useState(false);
  const [isCitizenModalOpen, setIsCitizenModalOpen] = useState(false); // 2. Add state for the new modal

  // Intelligent click handler that calls the correct API based on what was clicked
  const handleMapClick = async (clickedInfo: StationClickInfo | CoordinateClickInfo) => {
    // Case 1: A station pin was clicked
    if ('uid' in clickedInfo) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/stations/details/${clickedInfo.uid}`);
        const stationDetails = await response.json();
        const now = new Date();
        setSelectedLocation({
          ...stationDetails,
          date: now.toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" }),
          time: now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true }),
        });
      } catch (error) { console.error("Failed to fetch station details:", error); }
    } 
    // Case 2: The empty map was clicked
    else if ('coordinate' in clickedInfo) {
      const [lon, lat] = clickedInfo.coordinate;
      const userId = 1;
      try {
        const [alertResponse, nameResponse] = await Promise.all([
          fetch(`http://127.0.0.1:8000/api/v1/users/${userId}/personalized_alert?lat=${lat}&lon=${lon}`),
          fetch(`http://127.0.0.1:8000/api/v1/location/name?lat=${lat}&lon=${lon}`)
        ]);
        const alertData = await alertResponse.json();
        const nameData = await nameResponse.json();
        const now = new Date();
        setSelectedLocation({
          placeName: nameData.name || `Lat: ${lat.toFixed(2)}, Lon: ${lon.toFixed(2)}`,
          date: now.toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" }),
          time: now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true }),
          alert: alertData,
        });
      } catch (error) { console.error("Failed to fetch data on map click:", error); }
    }
  };

  return (
    <main className="flex h-screen w-screen bg-gray-900 overflow-hidden">
      {/* All Modals */}
      {isModalOpen && <RegistrationModal onClose={() => setIsModalOpen(false)} />}
      {isProfileOpen && <ProfileModal onClose={() => setIsProfileOpen(false)} />}
      {isForecastModalOpen && <ForecastModal onClose={() => setIsForecastModalOpen(false)} lat={viewState.latitude} lon={viewState.longitude} />}
      {isPolicyModalOpen && <PolicySimulatorModal onClose={() => setIsPolicyModalOpen(false)} lat={viewState.latitude} lon={viewState.longitude} />}
      {isCitizenModalOpen && <CitizenScienceModal onClose={() => setIsCitizenModalOpen(false)} lat={viewState.latitude} lon={viewState.longitude} />}

      {/* Main Layout */}
      <div className="flex-grow relative">
        <Header 
          onForecastClick={() => setIsForecastModalOpen(true)}
          onPolicyClick={() => setIsPolicyModalOpen(true)}
          onCitizenClick={() => setIsCitizenModalOpen(true)}
        />
        <LeftSidebar
          activeLayer={activeLayer}
          onLayerChange={setActiveLayer}
          onProfileClick={() => setIsProfileOpen(true)}
        />
        <MapContainer
          onMapClick={handleMapClick}
          activeLayer={activeLayer}
          timeOffset={timeOffset}
          viewState={viewState}
          onViewStateChange={setViewState}
        />
        <TimeScrubber timeOffset={timeOffset} onTimeChange={setTimeOffset} />
      </div>

      <DataPanel locationData={selectedLocation} />

      {!isChatOpen && <AuraGuideButton onClick={() => setIsChatOpen(true)} />}
      {isChatOpen && (
        <AuraGuideChat
          onClose={() => setIsChatOpen(false)}
          latitude={viewState.latitude}
          longitude={viewState.longitude}
        />
      )}
    </main>
  );
}

