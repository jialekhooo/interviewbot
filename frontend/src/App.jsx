import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Resume from "./pages/Resume";
import Interview from "./pages/Interview";
import Chat from "./pages/Chat";
import SpeechInterview from "./pages/SpeechInterview";

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow mb-4">
          <div className="container mx-auto px-4 py-3">
            <div className="flex justify-between items-center">
              <Link to="/" className="text-xl font-bold text-blue-600">Interview Chatbot</Link>
              <div className="flex space-x-6">
                <Link to="/resume" className="text-gray-700 hover:text-blue-600 font-medium">Resume Review</Link>
                <Link to="/interview" className="text-gray-700 hover:text-blue-600 font-medium">Interview Simulation</Link>
                <Link to="/chat" className="text-gray-700 hover:text-blue-600 font-medium">AI Chat</Link>
                <Link to="/speech-interview" className="text-gray-700 hover:text-blue-600 font-medium">Speech + Vision</Link>
              </div>
            </div>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/resume" element={<Resume />} />
          <Route path="/interview" element={<Interview />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/speech-interview" element={<SpeechInterview />} />
        </Routes>
      </div>
    </Router>
  );
}
