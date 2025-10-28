import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  ChatBubbleLeftIcon, 
  HeartIcon, 
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

export default function Forum() {
  const { user, token } = useAuth();
  const [posts, setPosts] = useState([]);
  const [filteredPosts, setFilteredPosts] = useState([]);
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('General');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeCommentPostId, setActiveCommentPostId] = useState(null);
  const [commentText, setCommentText] = useState('');

  const categories = ['All', 'General', 'Interview Tips', 'Career Advice', 'Resume Help', 'Technical Questions', 'Other'];

  useEffect(() => {
    if (token) {
      loadPosts();
    }
  }, [token]);

  useEffect(() => {
    filterPosts();
  }, [posts, searchQuery, filterCategory]);

  const loadPosts = () => {
    // Load from localStorage
    const savedPosts = localStorage.getItem('forumPosts');
    if (savedPosts) {
      setPosts(JSON.parse(savedPosts));
    }
  };

  const savePosts = (newPosts) => {
    localStorage.setItem('forumPosts', JSON.stringify(newPosts));
    setPosts(newPosts);
  };

  const filterPosts = () => {
    let filtered = [...posts];

    // Filter by category
    if (filterCategory !== 'All') {
      filtered = filtered.filter(post => post.category === filterCategory);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(post => 
        post.title.toLowerCase().includes(query) ||
        post.content.toLowerCase().includes(query) ||
        post.username.toLowerCase().includes(query)
      );
    }

    setFilteredPosts(filtered);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim() || !title.trim()) {
      setError('Title and content are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const newPost = {
        id: Date.now().toString(),
        title: title.trim(),
        content: content.trim(),
        category,
        username: user?.username || 'Anonymous',
        userId: user?.id || 'anonymous',
        created_at: new Date().toISOString(),
        likes: [],
        comments: []
      };

      const updatedPosts = [newPost, ...posts];
      savePosts(updatedPosts);
      
      setTitle('');
      setContent('');
      setCategory('General');
      setShowCreateModal(false);
    } catch (err) {
      console.error('Failed to create post:', err);
      setError('Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;

    const updatedPosts = posts.filter(post => post.id !== postId);
    savePosts(updatedPosts);
  };

  const handleLike = (postId) => {
    const updatedPosts = posts.map(post => {
      if (post.id === postId) {
        const likes = post.likes || [];
        const userLiked = likes.includes(user?.username);
        
        return {
          ...post,
          likes: userLiked 
            ? likes.filter(u => u !== user?.username)
            : [...likes, user?.username]
        };
      }
      return post;
    });
    savePosts(updatedPosts);
  };

  const handleAddComment = (postId) => {
    if (!commentText.trim()) return;

    const updatedPosts = posts.map(post => {
      if (post.id === postId) {
        const newComment = {
          id: Date.now().toString(),
          username: user?.username || 'Anonymous',
          content: commentText.trim(),
          created_at: new Date().toISOString()
        };
        return {
          ...post,
          comments: [...(post.comments || []), newComment]
        };
      }
      return post;
    });

    savePosts(updatedPosts);
    setCommentText('');
    setActiveCommentPostId(null);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getCategoryColor = (cat) => {
    const colors = {
      'General': 'bg-gray-100 text-gray-700',
      'Interview Tips': 'bg-blue-100 text-blue-700',
      'Career Advice': 'bg-green-100 text-green-700',
      'Resume Help': 'bg-purple-100 text-purple-700',
      'Technical Questions': 'bg-orange-100 text-orange-700',
      'Other': 'bg-pink-100 text-pink-700'
    };
    return colors[cat] || colors['General'];
  };

  if (!token) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">Please Login</h2>
          <p className="text-gray-600">You need to be logged in to access the forum.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-6 mb-6 text-white">
          <h1 className="text-3xl font-bold mb-2">Community Forum</h1>
          <p className="text-blue-100">Share knowledge, ask questions, and connect with others</p>
        </div>

        {/* Search and Filter Bar */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search posts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <FunnelIcon className="w-5 h-5 text-gray-400" />
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Create Post Button */}
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <PlusIcon className="w-5 h-5" />
              New Post
            </button>
          </div>
        </div>

        {/* Posts Feed */}
        <div className="space-y-4">
          {filteredPosts.length === 0 ? (
            <div className="bg-white shadow rounded-lg p-12 text-center">
              <p className="text-gray-500 text-lg">No posts found. Be the first to start a discussion!</p>
            </div>
          ) : (
            filteredPosts.map((post) => (
              <div key={post.id} className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow">
                {/* Post Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {post.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800">{post.username}</h4>
                      <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(post.category)}`}>
                      {post.category}
                    </span>
                    {user?.username === post.username && (
                      <button
                        onClick={() => handleDelete(post.id)}
                        className="text-red-500 hover:text-red-700 text-sm font-medium"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>

                {/* Post Content */}
                <h3 className="text-xl font-bold text-gray-900 mb-2">{post.title}</h3>
                <p className="text-gray-700 whitespace-pre-wrap mb-4">{post.content}</p>

                {/* Post Actions */}
                <div className="flex items-center gap-6 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => handleLike(post.id)}
                    className="flex items-center gap-2 text-gray-600 hover:text-red-500 transition-colors"
                  >
                    {post.likes?.includes(user?.username) ? (
                      <HeartSolidIcon className="w-5 h-5 text-red-500" />
                    ) : (
                      <HeartIcon className="w-5 h-5" />
                    )}
                    <span className="text-sm font-medium">{post.likes?.length || 0}</span>
                  </button>

                  <button
                    onClick={() => setActiveCommentPostId(activeCommentPostId === post.id ? null : post.id)}
                    className="flex items-center gap-2 text-gray-600 hover:text-blue-500 transition-colors"
                  >
                    <ChatBubbleLeftIcon className="w-5 h-5" />
                    <span className="text-sm font-medium">{post.comments?.length || 0} Comments</span>
                  </button>
                </div>

                {/* Comments Section */}
                {activeCommentPostId === post.id && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    {/* Add Comment */}
                    <div className="flex gap-3 mb-4">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {user?.username?.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <input
                          type="text"
                          placeholder="Write a comment..."
                          value={commentText}
                          onChange={(e) => setCommentText(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && handleAddComment(post.id)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                          onClick={() => handleAddComment(post.id)}
                          className="mt-2 px-4 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                        >
                          Comment
                        </button>
                      </div>
                    </div>

                    {/* Comments List */}
                    <div className="space-y-3">
                      {post.comments?.map((comment) => (
                        <div key={comment.id} className="flex gap-3 bg-gray-50 rounded-lg p-3">
                          <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold text-sm">
                            {comment.username.charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-sm text-gray-800">{comment.username}</span>
                              <span className="text-xs text-gray-500">{formatDate(comment.created_at)}</span>
                            </div>
                            <p className="text-sm text-gray-700">{comment.content}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Create Post Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Create New Post</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit}>
                {/* Title */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter post title..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                  />
                </div>

                {/* Category */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                  >
                    {categories.filter(cat => cat !== 'All').map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                {/* Content */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content
                  </label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Share your thoughts, questions, or advice..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={8}
                    disabled={loading}
                  />
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                    {error}
                  </div>
                )}

                {/* Actions */}
                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading || !content.trim() || !title.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    {loading ? 'Posting...' : 'Post'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
