"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, X } from 'lucide-react';

interface AuraGuideChatProps {
  onClose: () => void;
  latitude: number;
  longitude: number;
}

interface Message {
  text: string;
  sender: 'user' | 'ai';
}

export default function AuraGuideChat({ onClose, latitude, longitude }: AuraGuideChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    { text: "Hello! I'm the AURA Guide. How can I help you with air quality today?", sender: 'ai' }
  ]);
  const [input, setInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Automatically scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() === '' || isSubmitting) return;

    setIsSubmitting(true);
    const userMessage: Message = { text: input, sender: 'user' };
    const currentInput = input;
    
    // Add user message and a "thinking..." placeholder for instant feedback
    setMessages(prev => [...prev, userMessage, { text: "Thinking...", sender: 'ai' }]);
    setInput('');

    try {
      // Make a POST request to our AI endpoint
      const response = await fetch("http://127.0.0.1:8000/api/v1/ai_guide/chat", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 1, // This will come from a login state in the future
          question: currentInput,
          lat: latitude,   // Use the dynamic latitude from props
          lon: longitude, // Use the dynamic longitude from props
        }),
      });

      if (!response.ok) {
        throw new Error("The AI guide is currently unavailable. Please try again later.");
      }

      const data = await response.json();

      // Check if the backend returned an application-level error message
      if (data.error) {
        throw new Error(data.error);
      }

      const aiResponse: Message = { text: data.response, sender: 'ai' };
      
      // Replace the "Thinking..." message with the real response from the AI
      setMessages(prev => [...prev.slice(0, -1), aiResponse]);

    } catch (error: any) {
      console.error("Chat error:", error);
      const errorResponse: Message = { text: `Sorry, an error occurred: ${error.message}`, sender: 'ai' };
      
      // Replace the "Thinking..." message with the error message
      setMessages(prev => [...prev.slice(0, -1), errorResponse]);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed bottom-24 right-6 bg-gray-800 text-white rounded-lg shadow-2xl w-96 h-[60vh] flex flex-col z-40">
      {/* Header */}
      <div className="flex justify-between items-center p-4 border-b border-gray-700">
        <h3 className="font-bold text-lg">AURA Guide</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-white">
          <X size={24} />
        </button>
      </div>

      {/* Message Area */}
      <div className="flex-1 p-4 space-y-4 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs px-4 py-2 rounded-2xl ${
              msg.sender === 'user' 
                ? 'bg-blue-600 rounded-br-none' 
                : 'bg-gray-700 rounded-bl-none'
            }`}>
              <p>{msg.text}</p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-gray-700">
        <form onSubmit={handleSend} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about air quality..."
            className="flex-1 bg-gray-700 border border-gray-600 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSubmitting}
          />
          <button type="submit" className="bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700 disabled:bg-gray-500" disabled={isSubmitting}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}