"use client";

import React, { useMemo, useState, useEffect } from "react";
import Map, { ViewState, ViewStateChangeEvent } from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { HeatmapLayer } from "@deck.gl/aggregation-layers";
import { IconLayer, ScatterplotLayer, TextLayer } from "@deck.gl/layers";
import { Color } from "@deck.gl/core";
import "maplibre-gl/dist/maplibre-gl.css";

// --- TYPE DEFINITIONS ---
interface MapContainerProps {
  onMapClick: (info: any) => void; // A flexible handler for different click types
  activeLayer?: string;
  timeOffset: number;
  viewState: ViewState;
  onViewStateChange: (vs: ViewState) => void;
}

// --- HELPER FUNCTION ---
const getAqiColor = (aqi: number): Color => {
    if (aqi <= 50) return [76, 175, 80];   // Green
    if (aqi <= 100) return [255, 235, 59]; // Yellow
    if (aqi <= 150) return [255, 152, 0];  // Orange
    if (aqi <= 200) return [244, 67, 54];  // Red
    if (aqi <= 300) return [156, 39, 176]; // Purple
    return [141, 19, 19];                // Maroon
};

// --- CONSTANTS ---
const MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";
const HEATMAP_COLOR_RANGE: Color[] = [
  [5, 138, 91, 0], [5, 138, 91, 128], [254, 224, 139, 128],
  [253, 174, 97, 192], [244, 109, 67, 224], [215, 25, 28, 255]
];
const PARTICLE_ICON = `data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMCIgaGVpZ2h0PSIxMCI+PHNpcmNsZSBjeD0iNSIgY3k9IjUiIHI9IjUiIGZpbGw9IndoaXRlIiBmaWxsLW9wYWNpdHk9IjAuNSIgLz48L3N2Zz4=`;
const WIND_SPEED = 0.1;
const NUM_PARTICLES = 500;

// --- COMPONENT ---
export default function MapContainer({ 
  onMapClick, 
  activeLayer, 
  timeOffset, 
  viewState, 
  onViewStateChange 
}: MapContainerProps) {
  
  const [gridData, setGridData] = useState([]);
  const [stationData, setStationData] = useState([]);
  const [particles, setParticles] = useState<any[]>([]);

  // Effect to fetch heatmap data when active layer or time offset changes
  useEffect(() => {
    const fetchData = async () => {
      if (activeLayer === 'wind' || activeLayer === 'stations') {
        setGridData([]);
        return;
      }
      const pollutantQuery = activeLayer === 'aqi' ? 'auto' : activeLayer;
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/grid/current?pollutant=${pollutantQuery}&time_offset=${timeOffset}`);
        setGridData(await response.json());
      } catch (error) { console.error("Failed to fetch grid data:", error); }
    };
    fetchData();
  }, [activeLayer, timeOffset]);

  // Effect to fetch live station data (runs once on mount)
  useEffect(() => {
    const fetchStationData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/stations/live");
        setStationData(await response.json());
      } catch (error) { console.error("Failed to fetch station data:", error); }
    };
    fetchStationData();
  }, []);

  // Effect for wind animation (runs once on mount)
  useEffect(() => {
    const newParticles = Array.from({ length: NUM_PARTICLES }, () => ({
      position: [-125 + Math.random() * 50, 25 + Math.random() * 25],
    }));
    setParticles(newParticles);
    let animationFrameId: number;
    const animate = () => {
      setParticles(prev => prev.map(p => {
        let [lon] = p.position;
        lon += WIND_SPEED;
        if (lon > -70) lon = -125;
        return { ...p, position: [lon, p.position[1]] };
      }));
      animationFrameId = requestAnimationFrame(animate);
    };
    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  // Prepare layers for Deck.gl using the performant 'visible' property
  const layers = useMemo(() => [
    new HeatmapLayer({
        id: "heatmapLayer", data: gridData,
        visible: activeLayer !== 'stations' && activeLayer !== 'wind',
        getPosition: (d: any) => [d.lon, d.lat], getWeight: (d: any) => d.aqi,
        radiusPixels: 90, intensity: 2, colorRange: HEATMAP_COLOR_RANGE
    }),
    new ScatterplotLayer({
        id: 'station-circles', data: stationData,
        visible: activeLayer === 'stations',
        pickable: true,
        getPosition: d => [d.lon, d.lat], getFillColor: d => getAqiColor(d.aqi),
        getRadius: 8000, stroked: true, getLineColor: [255, 255, 255, 100], lineWidthMinPixels: 1,
    }),
    new TextLayer({
        id: 'station-labels', data: stationData,
        visible: activeLayer === 'stations',
        getPosition: d => [d.lon, d.lat], getText: d => d.aqi.toString(),
        getSize: 16, getColor: [0, 0, 0, 200], getFontWeight: 'bold',
    }),
    new IconLayer({
        id: 'windLayer', data: particles,
        visible: activeLayer === 'wind',
        getIcon: () => ({ url: PARTICLE_ICON, width: 128, height: 128 }),
        getPosition: d => d.position, getSize: 15, getColor: [255, 255, 255, 100]
    })
  ], [activeLayer, gridData, stationData, particles]);

  // Intelligent click handler that passes the correct data up to the parent
  const handleMapClick = (info: any) => {
    onMapClick(info.object || { coordinate: info.coordinate });
  };

  return (
    <DeckGL
      layers={layers}
      viewState={viewState}
      controller={true}
      onViewStateChange={e => onViewStateChange(e.viewState)}
      onClick={handleMapClick}
      style={{ width: "100%", height: "100%", position: "relative" }}
    >
      <Map mapStyle={MAP_STYLE} reuseMaps />
    </DeckGL>
  );
}

