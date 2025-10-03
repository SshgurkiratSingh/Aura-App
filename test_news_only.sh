#!/bin/bash

# Test curl command for news fetching only
curl -X POST http://localhost:5000/fetch-news \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["LLM", "electronics", "PCB", "VLSI"],
    "home_location": "Kharar, Punjab, India",
    "work_location": "IT Park, Chandigarh, India"
  }'
