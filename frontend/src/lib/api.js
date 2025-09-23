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

export default api;
