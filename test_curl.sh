#!/bin/bash

# Test curl command for podcast generation API
curl -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": {
      "name": "User",
      "tone": "Sherlock-like analytical and precise",
      "interests": ["LLM", "electronics", "PCB", "VLSI"],
      "medical_history": {
        "past": ["asthmatic"],
        "current": ["vitamin D deficient at 17.1 ng/mL"]
      },
      "occupation": "Electronics Engineer",
      "study_focus": "VLSI Design"
    },
    "weather_info": {
      "temperature": 24,
      "feels_like": 22,
      "humidity": 65,
      "conditions": "partly cloudy",
      "air_quality_index": 95,
      "air_quality_category": "moderate",
      "uv_index": 6,
      "wind_speed": 12,
      "visibility": 8,
      "pressure": 1013,
      "sunrise": "06:15 AM",
      "sunset": "06:45 PM"
    },
    "interests": ["LLM", "electronics", "PCB", "VLSI"],
    "home_location": "Kharar, Punjab, India",
    "work_location": "IT Park, Chandigarh, India",
    "extra": {
      "calendar_events": [
        {
          "time": "09:00 AM",
          "title": "VLSI Design Review",
          "duration": "1 hour",
          "location": "Conference Room A"
        },
        {
          "time": "02:00 PM",
          "title": "PCB Layout Meeting",
          "duration": "45 minutes",
          "location": "Lab 3"
        },
        {
          "time": "05:00 PM",
          "title": "LLM Research Discussion",
          "duration": "30 minutes",
          "location": "Virtual"
        }
      ],
      "commute_info": {
        "route": "Kharar to IT Park Chandigarh",
        "distance": "18 km",
        "estimated_time": "35 minutes",
        "traffic_status": "moderate",
        "suggested_departure": "08:15 AM"
      },
      "health_reminders": [
        "Take Vitamin D supplement (2000 IU)",
        "Avoid outdoor activities during high AQI",
        "Keep inhaler accessible",
        "Stay hydrated - aim for 3 liters"
      ],
      "workplace_notes": {
        "occupancy": "60%",
        "air_filtration": "active",
        "parking_availability": "good"
      }
    }
  }'
