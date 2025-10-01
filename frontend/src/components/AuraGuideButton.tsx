"use client";

import { Bot } from "lucide-react";

// Define the type for the component's props
interface AuraGuideButtonProps {
  onClick: () => void;
}

export default function AuraGuideButton({ onClick }: AuraGuideButtonProps) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-transform hover:scale-110"
      aria-label="Open AURA Guide"
    >
      <Bot size={28} />
    </button>
  );
}