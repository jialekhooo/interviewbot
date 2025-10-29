# Chat Sidebar Customization Guide

Quick reference for making common frontend changes to the chat sidebar.

## 🎨 Common Customizations

### 1. Change Sidebar Width

**File:** `frontend/src/components/ChatSidebar.jsx`  
**Line:** 89

```javascript
// Current: 320px
<div className="w-80 bg-gray-800 text-white flex flex-col h-full">

// Options:
w-64  // 256px (narrower)
w-72  // 288px
w-80  // 320px (current)
w-96  // 384px (wider)
```

### 2. Change Color Theme

**File:** `frontend/src/components/ChatSidebar.jsx`

#### Dark Theme (Current):
```javascript
// Line 89
className="w-80 bg-gray-800 text-white"

// Line 91 (header border)
className="p-4 border-b border-gray-700"

// Line 94 (collapse button)
className="p-1 hover:bg-gray-700 rounded"
```

#### Light Theme:
```javascript
// Replace bg-gray-800 with bg-white
// Replace text-white with text-gray-800
// Replace border-gray-700 with border-gray-200
// Replace hover:bg-gray-700 with hover:bg-gray-100

className="w-80 bg-white text-gray-800"
className="p-4 border-b border-gray-200"
className="p-1 hover:bg-gray-100 rounded"
```

#### Blue Theme:
```javascript
className="w-80 bg-blue-900 text-white"
className="p-4 border-b border-blue-800"
className="p-1 hover:bg-blue-800 rounded"
```

### 3. Change Header Title

**File:** `frontend/src/components/ChatSidebar.jsx`  
**Line:** 92

```javascript
// Current
<h2 className="text-lg font-semibold">Chat History</h2>

// Options
<h2 className="text-lg font-semibold">Past Interviews</h2>
<h2 className="text-lg font-semibold">My Chats</h2>
<h2 className="text-lg font-semibold">Interview History</h2>
```

### 4. Change Status Badge Colors

**File:** `frontend/src/components/ChatSidebar.jsx`  
**Lines:** 49-60

```javascript
const getStatusColor = (status) => {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-800"; // Change these
    case "in_progress":
      return "bg-blue-100 text-blue-800";
    case "abandoned":
      return "bg-gray-100 text-gray-800";
    default:
      return "bg-gray-100 text-gray-600";
  }
};
```

**Color Options:**
```javascript
// Green variants
"bg-green-50 text-green-700"
"bg-green-100 text-green-800"
"bg-green-500 text-white"

// Blue variants
"bg-blue-50 text-blue-700"
"bg-blue-100 text-blue-800"
"bg-blue-500 text-white"

// Red variants
"bg-red-50 text-red-700"
"bg-red-100 text-red-800"
"bg-red-500 text-white"

// Purple variants
"bg-purple-50 text-purple-700"
"bg-purple-100 text-purple-800"
"bg-purple-500 text-white"
```

### 5. Change "New Chat" Button Action

**File:** `frontend/src/components/ChatSidebar.jsx`  
**Line:** 117

```javascript
// Current: Reloads the page
onClick={() => window.location.reload()}

// Option 1: Navigate to a route
onClick={() => navigate('/chat/new')}

// Option 2: Call a custom function
onClick={() => onNewChat()}

// Option 3: Clear current chat
onClick={() => {
  setMessages([]);
  setSessionId(null);
  // Start new session
}}
```

### 6. Customize Chat Item Display

**File:** `frontend/src/components/ChatSidebar.jsx`  
**Lines:** 175-196

```javascript
// Current format:
<div className="font-medium text-sm truncate">
  {chat.position || "Interview"}
</div>
<div className="text-xs text-gray-400 mt-1">
  {formatDate(chat.start_time)}
</div>

// Add more info:
<div className="font-medium text-sm truncate">
  {chat.position || "Interview"}
</div>
<div className="text-xs text-gray-400 mt-1">
  {formatDate(chat.start_time)} • {chat.question_types?.join(', ')}
</div>
<div className="text-xs text-gray-500 mt-1">
  Questions: {chat.question_ids?.length || 0}
</div>
```

### 7. Add Search/Filter

**File:** `frontend/src/components/ChatSidebar.jsx`  
**Add after line 135:**

```javascript
{/* Search Bar */}
<div className="p-3 border-b border-gray-700">
  <input
    type="text"
    placeholder="Search chats..."
    value={searchQuery}
    onChange={(e) => setSearchQuery(e.target.value)}
    className="w-full px-3 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
  />
</div>
```

**Add state:**
```javascript
const [searchQuery, setSearchQuery] = useState("");
```

**Filter chats:**
```javascript
const filteredChats = pastChats.filter(chat =>
  chat.position?.toLowerCase().includes(searchQuery.toLowerCase())
);
```

### 8. Change Date Format

**File:** `frontend/src/components/ChatSidebar.jsx`  
**Lines:** 33-47

```javascript
// Current: Relative time (5m ago, 2h ago)
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

// Option 1: Always show full date
const formatDate = (dateString) => {
  if (!dateString) return "Unknown date";
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

// Option 2: Show date and time
const formatDate = (dateString) => {
  if (!dateString) return "Unknown date";
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
```

### 9. Add Icons to Buttons

**Install Lucide React (if not already):**
```bash
npm install lucide-react
```

**Import icons:**
```javascript
import { Plus, RefreshCw, Search, Trash2 } from 'lucide-react';
```

**Use in buttons:**
```javascript
// New Chat button with icon
<button className="...">
  <Plus size={20} />
  New Chat
</button>

// Refresh button with icon
<button className="...">
  <RefreshCw size={16} />
  Refresh
</button>
```

### 10. Add Animations

**File:** `frontend/src/components/ChatSidebar.jsx`

**Fade in animation:**
```javascript
// Add to chat list container (line 164)
<div className="space-y-1 p-2 animate-fadeIn">

// Add to your CSS or Tailwind config:
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

**Slide in animation:**
```javascript
// Add to sidebar container (line 89)
<div className="w-80 bg-gray-800 text-white flex flex-col h-full transform transition-transform duration-300">

// When collapsed:
className="transform -translate-x-full"

// When expanded:
className="transform translate-x-0"
```

## 📁 File Locations

```
frontend/
├── src/
│   ├── components/
│   │   └── ChatSidebar.jsx          ← Main sidebar component
│   ├── pages/
│   │   └── Chat.jsx                 ← Chat page (integrates sidebar)
│   ├── config/
│   │   └── sidebarConfig.js         ← Configuration file
│   └── lib/
│       └── api.js                   ← API helper functions
```

## 🚀 Quick Start

1. **Open the file you want to edit**
2. **Find the line number** from this guide
3. **Make your changes**
4. **Save the file** (hot reload will update)
5. **Check the browser** to see changes

## 💡 Tips

- Use browser DevTools to inspect elements and test styles
- Tailwind CSS classes can be chained: `bg-blue-500 hover:bg-blue-600 rounded-lg p-4`
- Test on different screen sizes
- Keep accessibility in mind (contrast, focus states)
- Use semantic HTML elements

## 🐛 Common Issues

**Sidebar not showing:**
- Check if `ChatSidebar` is imported in `Chat.jsx`
- Verify the component is rendered in the JSX

**Styles not applying:**
- Make sure Tailwind classes are spelled correctly
- Check if custom CSS is overriding Tailwind
- Clear browser cache

**Data not loading:**
- Check browser console for API errors
- Verify backend is running
- Check authentication status

## 📚 Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Docs](https://react.dev)
- [Lucide Icons](https://lucide.dev)

---

**Ready to customize!** Start with simple changes like colors and text, then move to more complex features.
