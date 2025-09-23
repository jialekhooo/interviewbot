import React, { useEffect, useRef, useState } from "react";
import api from "../lib/api";

export default function Chat() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]); // {role: 'assistant'|'user'|'system'|'feedback', content: string}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const scrollerRef = useRef(null);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
    });
  };

  // Start a new interview session on mount
  useEffect(() => {
    const start = async () => {
      setLoading(true);
      setError("");
      setStatus("Contacting server… this can take up to 30s on cold start");
      try {
        // Warm-up GET (may return 405; that's fine)
        try { await api.get("/api/interview/start", { timeout: 5000 }); } catch {}

        const { data } = await api.post("/api/interview/start", {
          position: "Software Engineer",
          difficulty: "medium",
          question_types: ["behavioral", "technical"],
          duration: 30,
        }, { timeout: 45000 });

        if (!data?.session_id || !data?.question) {
          setError("Server responded without a question. Please try again shortly.");
          setStatus("");
          return;
        }

        setSessionId(data.session_id);
        setMessages([
          { role: "system", content: "Interview session started. Answer questions to receive feedback." },
          { role: "assistant", content: data.question.text },
        ]);
        setStatus("");
      } catch (err) {
        setError(err?.response?.data?.detail || err?.response?.data?.error || err.message || "Failed to start session");
      } finally {
        setLoading(false);
        scrollToBottom();
      }
    };
    start();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const send = async () => {
    if (!input.trim() || !sessionId) return;
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);
    setError("");

    try {
      const { data } = await api.post("/api/interview/answer", {
        session_id: sessionId,
        response: userMsg,
        time_taken: null,
        confidence_level: null,
      }, { timeout: 45000 });

      if (data?.feedback) {
        // Show structured feedback if available
        const fb = data.feedback;
        let fbText = "";
        if (fb.summary) fbText += fb.summary + "\n\n";
        if (typeof fb.detailed_feedback === "string") fbText += fb.detailed_feedback;
        if (Array.isArray(fb.detailed_feedback)) {
          fbText += fb.detailed_feedback.map((x, i) => `• ${x.detailed_feedback || x.feedback || JSON.stringify(x)}`).join("\n");
        }
        if (!fbText) fbText = JSON.stringify(fb, null, 2);
        setMessages(prev => [...prev, { role: "feedback", content: fbText }]);
      }

      if (data?.type === "next_question" && data?.question?.text) {
        setMessages(prev => [...prev, { role: "assistant", content: data.question.text }]);
      } else if (data?.type === "interview_complete") {
        const overall = data.feedback || {};
        const summary = overall.summary || "Interview complete.";
        setMessages(prev => [...prev, { role: "assistant", content: summary }]);
      }
    } catch (err) {
      setError(err?.response?.data?.detail || err?.response?.data?.error || err.message || "Failed to submit answer");
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto bg-white shadow-lg rounded-lg flex flex-col h-[75vh]">
        <div className="border-b px-4 py-3 text-lg font-semibold text-blue-600">AI Interview Chat</div>
        <div ref={scrollerRef} className="flex-1 overflow-auto p-4 space-y-3 bg-gray-50">
          {messages.map((m, idx) => (
            <div key={idx} className={
              m.role === "user" ? "text-right" : "text-left"
            }>
              <div className={
                "inline-block px-3 py-2 rounded " +
                (m.role === "user" ? "bg-blue-600 text-white" : m.role === "feedback" ? "bg-yellow-100 text-gray-800" : "bg-white border")
              }>
                {m.content}
              </div>
            </div>
          ))}
          {!messages.length && (
            <div className="text-gray-500 text-sm">{status || "Starting session…"}</div>
          )}
        </div>
        <div className="border-t p-3">
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              rows={2}
              placeholder="Type your answer and press Enter to send"
              className="flex-1 border rounded p-2"
              disabled={loading || !sessionId}
            />
            <button
              onClick={send}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              disabled={loading || !sessionId || !input.trim()}
            >
              {loading ? "Sending…" : "Send"}
            </button>
          </div>
          {error && <div className="text-red-600 text-sm mt-2">{error}</div>}
        </div>
      </div>
    </div>
  );
}
