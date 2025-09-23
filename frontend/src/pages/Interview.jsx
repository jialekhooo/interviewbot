import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/api";

export default function Interview() {
  const navigate = useNavigate();
  const [started, setStarted] = useState(false);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [debugInfo, setDebugInfo] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [lastStartInfo, setLastStartInfo] = useState(null);

  // Helper to POST with timeout + retry to handle Render cold starts / transient errors
  const postWithRetry = async (url, body, { retries = 3, timeout = 45000 } = {}) => {
    let attempt = 0;
    let lastErr;
    while (attempt <= retries) {
      try {
        return await api.post(url, body, { timeout });
      } catch (err) {
        lastErr = err;
        const status = err?.response?.status;
        const retriable = !status || [429, 500, 502, 503, 504].includes(status);
        if (!retriable || attempt === retries) break;
        const backoffMs = 1000 * Math.pow(2, attempt);
        setStatusMessage(`Server warming up (attempt ${attempt + 2}/${retries + 1})… retrying in ${backoffMs / 1000}s`);
        await new Promise(r => setTimeout(r, backoffMs));
        attempt += 1;
      }
    }
    throw lastErr;
  };

  const startInterview = async () => {
    setLoading(true);
    setError("");
    setFeedback(null);
    try {
      setStatusMessage("Contacting server… this can take up to 30s on cold start");
      // Warm up Render service: a quick GET that is expected to 405 but wakes the server
      try {
        await api.get("/api/interview/start", { timeout: 5000 });
      } catch (werr) {
        // Intentionally ignore; 405/404 is fine as long as it hits the server
      }
      const resp = await postWithRetry("/api/interview/start", {
        position: "Software Engineer",
        difficulty: "medium",
        question_types: ["behavioral", "technical"],
        duration: 30,
      }, { retries: 3, timeout: 45000 });
      const data = resp?.data;
      console.log("/api/interview/start response", data);
      setDebugInfo({ startResponse: data });
      setLastStartInfo({
        url: `${api.defaults.baseURL || ''}/api/interview/start`,
        method: "POST",
        response: data,
      });
      if (!data || !data.session_id || !data.question) {
        setError("Server responded without a question. Please try again shortly.");
        setDebugInfo((prev) => ({ ...(prev || {}), startData: data }));
        setStatusMessage("");
        return;
      }
      setSessionId(data.session_id);
      setQuestion(data.question);
      setStarted(true);
      // Redirect to AI Chat page to continue the conversation UI
      navigate("/chat");
      setStatusMessage("");
    } catch (err) {
      console.error("startInterview error", err);
      setError(
        err.response?.data?.detail ||
          err.response?.data?.error ||
          err.message ||
          "Failed to start interview"
      );
      setDebugInfo({ startError: err.response?.data || err.toString?.() });
      setStatusMessage("Failed to reach server. Please try again in a few seconds.");
      setLastStartInfo({
        url: `${api.defaults.baseURL || ''}/api/interview/start`,
        method: "POST",
        error: err.response?.data || err.message || String(err),
        status: err.response?.status,
      });
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!sessionId || !question) return;
    setLoading(true);
    setError("");
    setFeedback(null);
    try {
      setStatusMessage("");
      const { data } = await postWithRetry("/api/interview/answer", {
        session_id: sessionId,
        response: answer,
        time_taken: null,
        confidence_level: null,
      }, { retries: 2, timeout: 45000 });
      console.log("/api/interview/answer response", data);
      setDebugInfo((prev) => ({ ...(prev || {}), answerResponse: data }));

      if (data.type === "next_question") {
        setFeedback(data.feedback);
        setQuestion(data.question);
        setAnswer("");
      } else if (data.type === "interview_complete") {
        setFeedback(data.feedback);
        setQuestion(null);
      }
    } catch (err) {
      console.error("submitAnswer error", err);
      setError(
        err.response?.data?.detail ||
          err.response?.data?.error ||
          err.message ||
          "Submission failed"
      );
      setDebugInfo((prev) => ({ ...(prev || {}), answerError: err.response?.data || err.toString?.() }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-3xl font-bold mb-6 text-blue-600">Interview Simulation</h2>
        <p className="text-gray-600 mb-6">Practice your interview skills with AI-powered questions and feedback.</p>
        {statusMessage && (
          <div className="mb-3 text-sm text-gray-600">{statusMessage}</div>
        )}
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
          {question ? (
            <div className="mb-4">
              <div className="font-semibold">Question:</div>
              <div className="mb-2 text-gray-800">{question.text}</div>
            </div>
          ) : started && (
            <div className="mb-4 text-sm text-gray-600">Waiting for question...</div>
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
          {feedback ? (
            <div className="mt-4 bg-gray-100 p-3 rounded">
              <div className="font-semibold mb-1">Feedback</div>
              {/* Overall feedback (summary + array of detailed entries) */}
              {feedback.summary && <div className="mb-2">{feedback.summary}</div>}

              {/* Per-question feedback: show string detailed_feedback */}
              {typeof feedback.detailed_feedback === "string" && (
                <div className="text-sm text-gray-700 whitespace-pre-wrap">{feedback.detailed_feedback}</div>
              )}

              {/* Overall detailed list or structured array */}
              {Array.isArray(feedback.detailed_feedback) && (
                <ul className="text-sm text-gray-700">
                  {feedback.detailed_feedback.map((fb, idx) => (
                    <li key={idx} className="mb-1">• {fb.detailed_feedback || fb.feedback || JSON.stringify(fb)}</li>
                  ))}
                </ul>
              )}

              {/* Optional extra fields if present */}
              {Array.isArray(feedback.strengths) && feedback.strengths.length > 0 && (
                <div className="mt-2">
                  <div className="font-medium">Strengths</div>
                  <ul className="list-disc list-inside text-sm text-gray-700">
                    {feedback.strengths.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}
              {Array.isArray(feedback.areas_for_improvement) && feedback.areas_for_improvement.length > 0 && (
                <div className="mt-2">
                  <div className="font-medium">Areas for Improvement</div>
                  <ul className="list-disc list-inside text-sm text-gray-700">
                    {feedback.areas_for_improvement.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}
              {typeof feedback.score === "number" && (
                <div className="mt-2 text-sm text-gray-700">Score: {feedback.score.toFixed(1)} / 1.0</div>
              )}
              {feedback.error && (
                <div className="mt-2 text-sm text-red-600">{feedback.error}</div>
              )}
            </div>
          ) : null}
          {/* Debug info (only shown if there is an error) */}
          {error && debugInfo && (
            <details className="mt-3 text-xs text-gray-500">
              <summary>Debug details</summary>
              <pre className="whitespace-pre-wrap break-words">{JSON.stringify(debugInfo, null, 2)}</pre>
            </details>
          )}
          {/* Always-visible start response inspector for troubleshooting */}
          {lastStartInfo && (
            <details className="mt-3 text-xs text-gray-600">
              <summary>Start request inspector</summary>
              <div className="mb-1">URL: {lastStartInfo.url || "/api/interview/start"}</div>
              <div className="mb-1">Method: {lastStartInfo.method}</div>
              {lastStartInfo.status && <div className="mb-1">Status: {lastStartInfo.status}</div>}
              <div className="mb-1 font-medium">Response/Error:</div>
              <pre className="whitespace-pre-wrap break-words">
                {JSON.stringify(lastStartInfo.response || lastStartInfo.error, null, 2)}
              </pre>
            </details>
          )}
        </>
      )}
      {error && <div className="text-red-600 mt-2">{error}</div>}
      </div>
    </div>
  );
}
