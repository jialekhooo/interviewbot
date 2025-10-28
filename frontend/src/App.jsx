import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Home from "./pages/Home";
import Resume from "./pages/Resume";
import Interview from "./pages/Interview";
import SpeechInterview from "./pages/SpeechInterview";
import Chat from "./pages/Chat";
import Posts from "./pages/Posts";
import Forum from "./pages/Forum";
import VideoInterview from "./pages/VideoInterview";
import ResumeBuilder from "./pages/ResumeBuilder";
import Login from "./pages/Login";

function Navigation() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow mb-4">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-blue-600">Interview Chatbot</Link>
          <div className="flex items-center space-x-6">
            <Link to="/resume" className="text-gray-700 hover:text-blue-600 font-medium">Resume Review</Link>
            <Link to="/interview" className="text-gray-700 hover:text-blue-600 font-medium">Interview</Link>
            <Link to="/speech-interview" className="text-gray-700 hover:text-blue-600 font-medium">Live Interview</Link>
            <Link to="/chat" className="text-gray-700 hover:text-blue-600 font-medium">AI Chat</Link>
            <Link to="/posts" className="text-gray-700 hover:text-blue-600 font-medium">Posts</Link>
            <Link to="/forum" className="text-gray-700 hover:text-blue-600 font-medium">Forum</Link>
            <Link to="/video-interview" className="text-gray-700 hover:text-blue-600 font-medium">Video Interview</Link>
            <Link to="/resume-builder" className="text-gray-700 hover:text-blue-600 font-medium">Resume Builder</Link>
            {user ? (
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">Hi, {user.username}</span>
                <button
                  onClick={logout}
                  className="px-4 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link to="/login" className="px-4 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/resume" element={<Resume />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/speech-interview" element={<SpeechInterview />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/posts" element={<Posts />} />
            <Route path="/forum" element={<Forum />} />
            <Route path="/video-interview" element={<VideoInterview />} />
            <Route path="/resume-builder" element={<ResumeBuilder />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}
