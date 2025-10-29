import React, { useEffect, useState } from "react";
import api from "../lib/api";

export default function ChatSidebar({ onSelectChat, currentSessionId }) {
  const [pastChats, setPastChats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    fetchPastChats();
  }, []);

  const fetchPastChats = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get("/api/interview/past_interviews");
      setPastChats(data || []);
    } catch (err) {
      // If 404, it means no past interviews - not an error
      if (err?.response?.status === 404) {
        setPastChats([]);
      } else {
        setError("Failed to load past chats");
        console.error("Failed to fetch past chats:", err);
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown date";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "in_progress":
        return "bg-blue-100 text-blue-800";
      case "abandoned":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  if (isCollapsed) {
    return (
      <div className="w-12 bg-gray-800 text-white flex flex-col items-center py-4">
        <button
          onClick={() => setIsCollapsed(false)}
          className="p-2 hover:bg-gray-700 rounded transition-colors"
          title="Expand sidebar"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className="w-80 bg-gray-800 text-white flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex justify-between items-center">
        <h2 className="text-lg font-semibold">Chat History</h2>
        <button
          onClick={() => setIsCollapsed(true)}
          className="p-1 hover:bg-gray-700 rounded transition-colors"
          title="Collapse sidebar"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3 border-b border-gray-700">
        <button
          onClick={() => window.location.reload()}
          className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Chat
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="p-4 text-center text-gray-400">
            Loading chats...
          </div>
        )}

        {error && (
          <div className="p-4 text-center text-red-400 text-sm">
            {error}
            <button
              onClick={fetchPastChats}
              className="block mx-auto mt-2 text-blue-400 hover:text-blue-300"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && pastChats.length === 0 && (
          <div className="p-4 text-center text-gray-400 text-sm">
            No past chats yet. Start a new interview!
          </div>
        )}

        {!loading && !error && pastChats.length > 0 && (
          <div className="space-y-1 p-2">
            {pastChats.map((chat) => (
              <button
                key={chat.session_id}
                onClick={() => onSelectChat(chat.session_id)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  currentSessionId === chat.session_id
                    ? "bg-gray-700"
                    : "hover:bg-gray-700/50"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate">
                      {chat.position || "Interview"}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {formatDate(chat.start_time)}
                    </div>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded ${getStatusColor(
                      chat.status
                    )}`}
                  >
                    {chat.status}
                  </span>
                </div>
                {chat.difficulty && (
                  <div className="text-xs text-gray-500 mt-1 capitalize">
                    {chat.difficulty}
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-700">
        <button
          onClick={fetchPastChats}
          className="w-full py-2 text-sm text-gray-400 hover:text-white transition-colors"
        >
          Refresh
        </button>
      </div>
    </div>
  );
}
