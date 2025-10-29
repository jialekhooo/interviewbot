import axios from "axios";

// Use direct backend URL in production to avoid proxy/redirect issues
const baseURL = import.meta.env.PROD
  ? "https://interviewbot-rjsi.onrender.com"
  : ""; // Vite dev server will proxy locally per vite.config.js

const api = axios.create({
  baseURL,
  // Include a reasonable default timeout to avoid hanging forever
  timeout: 20000,
});

// Helper functions for interview API
export const interviewAPI = {
  // Fetch all past interviews for the current user
  getPastInterviews: () => api.get("/api/interview/past_interviews"),
  
  // Fetch a specific past interview by session ID
  getPastInterview: (sessionId) => api.get(`/api/interview/past_interview/${sessionId}`),
  
  // Start a new interview
  startInterview: (data) => api.post("/api/interview/start", data),
  
  // Submit an answer
  submitAnswer: (data) => api.post("/api/interview/answer", data),
  
  // Get feedback for a session
  getFeedback: (sessionId) => api.get(`/api/interview/feedback/${sessionId}`),
};

export default api;
