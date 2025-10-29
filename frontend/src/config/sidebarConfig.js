// Chat Sidebar Configuration
// Edit these values to customize the sidebar appearance and behavior

export const sidebarConfig = {
  // Dimensions
  width: {
    expanded: "w-80", // 320px - change to w-64 (256px) or w-96 (384px)
    collapsed: "w-12", // 48px
  },

  // Colors (Tailwind classes)
  colors: {
    background: "bg-gray-800",
    text: "text-white",
    hover: "hover:bg-gray-700",
    border: "border-gray-700",
    
    // Status badge colors
    status: {
      completed: "bg-green-100 text-green-800",
      in_progress: "bg-blue-100 text-blue-800",
      abandoned: "bg-gray-100 text-gray-800",
      default: "bg-gray-100 text-gray-600",
    },
    
    // Button colors
    newChatButton: "bg-blue-600 hover:bg-blue-700",
    refreshButton: "text-gray-400 hover:text-white",
    retryButton: "text-blue-400 hover:text-blue-300",
  },

  // Text content
  text: {
    header: "Chat History",
    newChat: "New Chat",
    refresh: "Refresh",
    retry: "Retry",
    loading: "Loading chats...",
    empty: "No past chats yet. Start a new interview!",
    error: "Failed to load past chats",
    unknownDate: "Unknown date",
  },

  // Behavior
  behavior: {
    autoRefreshOnMount: true, // Fetch chats when component mounts
    collapseByDefault: false, // Start with sidebar collapsed
    showDifficulty: true, // Show difficulty level in chat items
    showTimestamp: true, // Show timestamp in chat items
    showStatus: true, // Show status badge in chat items
  },

  // Date formatting
  dateFormat: {
    justNow: "Just now",
    minutesAgo: (mins) => `${mins}m ago`,
    hoursAgo: (hours) => `${hours}h ago`,
    daysAgo: (days) => `${days}d ago`,
    fallback: (date) => date.toLocaleDateString(), // For dates older than 7 days
  },

  // API endpoints
  api: {
    pastInterviews: "/api/interview/past_interviews",
    pastInterview: (sessionId) => `/api/interview/past_interview/${sessionId}`,
  },

  // Animation
  animation: {
    transition: "transition-colors",
    duration: "duration-200",
  },
};

export default sidebarConfig;
