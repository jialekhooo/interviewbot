import React, { useState } from "react";
import axios from "axios";

export default function Interview() {
  const [started, setStarted] = useState(false);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState(null);

  const startInterview = async () => {
    setLoading(true);
    setError("");
    setFeedback(null);
    try {
      const { data } = await axios.post("https://interviewbot-rjsi.onrender.com/api/interview/start", {
        position: "Software Engineer",
        difficulty: "medium",
        question_types: ["behavioral", "technical"],
        duration: 30,
      });
      setSessionId(data.session_id);
      setQuestion(data.question);
      setStarted(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start interview");
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    setLoading(true);
    setError("");
    setFeedback(null);
    try {
      // For demo: just echo the answer as feedback
      setFeedback({ summary: "(Demo) Feedback: Your answer was received." });
      setAnswer("");
      // In a real app, connect to WebSocket for live feedback
    } catch (err) {
      setError("Submission failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-3xl font-bold mb-6 text-blue-600">Interview Simulation</h2>
        <p className="text-gray-600 mb-6">Practice your interview skills with AI-powered questions and feedback.</p>
      {!started ? (
        <button
          onClick={startInterview}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? "Starting..." : "Start Interview"}
        </button>
      ) : (
        <>
          {question && (
            <div className="mb-4">
              <div className="font-semibold">Question:</div>
              <div className="mb-2 text-gray-800">{question.text}</div>
            </div>
          )}
          <textarea
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            rows={5}
            className="w-full p-2 border rounded mb-2"
            placeholder="Type your answer here..."
          />
          <button
            onClick={submitAnswer}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            disabled={loading || !answer}
          >
            {loading ? "Submitting..." : "Submit Answer"}
          </button>
          {feedback && (
            <div className="mt-4 bg-gray-100 p-3 rounded">
              <div className="font-semibold mb-1">Feedback</div>
              <div>{feedback.summary}</div>
            </div>
          )}
        </>
      )}
      {error && <div className="text-red-600 mt-2">{error}</div>}
      </div>
    </div>
  );
}
