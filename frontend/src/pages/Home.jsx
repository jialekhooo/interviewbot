import React from "react";

export default function Home() {
  return (
    <div className="max-w-2xl mx-auto mt-16 text-center">
      <h1 className="text-3xl font-bold mb-4 text-blue-700">Welcome to the Interview Chatbot</h1>
      <p className="text-gray-700 mb-8">
        Get AI-powered resume feedback and practice real interview questions. Start by uploading your resume or try an interview simulation!
      </p>
      <img src="/static/ai-interview.svg" alt="Interview Chatbot" className="mx-auto w-48" />
    </div>
  );
}
