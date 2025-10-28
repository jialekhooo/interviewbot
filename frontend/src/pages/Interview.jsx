import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/api";

export default function Interview() {
  const navigate = useNavigate();
  const [started, setStarted] = useState(false);
  const [file, setFile] = useState(null);
  const [position, setPosition] = useState("");  // ← Empty, user must input
  const [jobDescription, setJobDescription] = useState("");
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [questionId, setQuestionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [summary, setSummary] = useState(null);

  const startInterview = async () => {
    // Validate required fields
    if (!file) {
      setError("Please upload your resume first");
      return;
    }

    if (!position.trim()) {
      setError("Please enter the job position");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("position", position.trim());
    formData.append("job_description", jobDescription);

    try {
      const { data } = await api.post("/api/interview/start", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 45000,
      });

      setSessionId(data.session_id);
      setQuestionId(data.question_id);
      setQuestion({ text: data.question });
      setStarted(true);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start interview");
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!file || !questionId || !answer) return;

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("question_id", questionId);
    formData.append("response_text", answer);

    try {
      const { data } = await api.post("/api/interview/answer", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 45000,
      });

      if (data.type === "next_question") {
        setQuestionId(data.next_question.id);
        setQuestion({ text: data.next_question.text });
        setAnswer("");
      } else if (data.type === "interview_complete") {
        setIsComplete(true);
        setSummary(data.summary);
        alert("Interview complete!\n\n" + data.feedback);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-3xl font-bold mb-6 text-blue-600">Mock Interview</h2>
        <p className="text-gray-600 mb-6">
          Upload your resume and provide job details to start your personalized mock interview
        </p>

        {!started ? (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Upload Resume <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full"
              />
              {file && (
                <p className="text-xs text-green-600 mt-1">
                  ✓ {file.name}
                </p>
              )}
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Position <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={position}
                onChange={(e) => setPosition(e.target.value)}
                className="w-full p-2 border rounded"
                placeholder="e.g., Software Engineer, Data Scientist, Product Manager"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter the job position you're interviewing for
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Job Description (Optional)
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={4}
                className="w-full p-2 border rounded"
                placeholder="Paste the job description here to get more relevant questions..."
              />
            </div>

            <button
              onClick={startInterview}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
              disabled={loading || !file || !position.trim()}
            >
              {loading ? "Starting Interview..." : "Start Mock Interview"}
            </button>
          </>
        ) : isComplete ? (
          <div className="space-y-6">
            <div className="bg-green-50 border-l-4 border-green-500 p-4">
              <h3 className="text-xl font-bold text-green-800 mb-2">🎉 Interview Complete!</h3>
              <p className="text-green-700">Thank you for completing the mock interview.</p>
            </div>

            {summary && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-lg text-blue-900 mb-3">Summary</h4>
                <div className="space-y-2 text-gray-700">
                  <div>Questions Answered: {summary.questions_answered}</div>
                  <div>Session ID: {summary.session_id}</div>
                </div>
              </div>
            )}

            <button
              onClick={() => {
                setStarted(false);
                setIsComplete(false);
                setFile(null);
                setPosition("");
                setJobDescription("");
                setQuestion(null);
                setAnswer("");
                setSummary(null);
              }}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Start New Interview
            </button>
          </div>
        ) : (
          <>
            {question && (
              <div className="mb-4 p-4 bg-blue-50 rounded">
                <div className="font-semibold text-blue-900 mb-2">Question:</div>
                <div className="text-gray-800">{question.text}</div>
              </div>
            )}
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={6}
              className="w-full p-3 border rounded mb-3"
              placeholder="Type your answer here..."
            />
            <button
              onClick={submitAnswer}
              className="w-full px-4 py-3 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
              disabled={loading || !answer.trim()}
            >
              {loading ? "Submitting..." : "Submit Answer"}
            </button>
          </>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-600">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}}