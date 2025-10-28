import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import { PhotoIcon, VideoCameraIcon, DocumentIcon } from '@heroicons/react/24/outline';

export default function Posts() {
  const { user, token } = useAuth();
  const [posts, setPosts] = useState([]);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await api.get('/api/posts');
      setPosts(response.data);
    } catch (err) {
      console.error('Failed to fetch posts:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/posts', {
        content: content.trim(),
      });
      
      // Add new post to the top of the list
      setPosts([response.data, ...posts]);
      setContent('');
    } catch (err) {
      console.error('Failed to create post:', err);
      setError(err.response?.data?.detail || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;

    try {
      await api.delete(`/api/posts/${postId}`);
      setPosts(posts.filter(post => post.id !== postId));
    } catch (err) {
      console.error('Failed to delete post:', err);
      alert('Failed to delete post');
    }
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

  if (!token) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">Please Login</h2>
          <p className="text-gray-600">You need to be logged in to view and create posts.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Create Post Card */}
        <div className="bg-white shadow-lg rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">{user?.username || 'User'}</h3>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share your thoughts here..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
              rows={4}
              disabled={loading}
            />

            {error && (
              <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                {error}
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="flex gap-4">
                <button
                  type="button"
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors"
                  title="Image (Coming soon)"
                >
                  <PhotoIcon className="w-5 h-5" />
                  <span className="text-sm">Image</span>
                </button>
                <button
                  type="button"
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors"
                  title="Video (Coming soon)"
                >
                  <VideoCameraIcon className="w-5 h-5" />
                  <span className="text-sm">Video</span>
                </button>
                <button
                  type="button"
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors"
                  title="File (Coming soon)"
                >
                  <DocumentIcon className="w-5 h-5" />
                  <span className="text-sm">file</span>
                </button>
              </div>

              <button
                type="submit"
                disabled={loading || !content.trim()}
                className="px-8 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Posting...' : 'Post'}
              </button>
            </div>
          </form>
        </div>

        {/* Posts Feed */}
        <div className="space-y-4">
          {posts.length === 0 ? (
            <div className="bg-white shadow rounded-lg p-8 text-center text-gray-500">
              No posts yet. Be the first to share something!
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="bg-white shadow rounded-lg p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                      {post.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800">{post.username}</h4>
                      <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
                    </div>
                  </div>

                  {user?.username === post.username && (
                    <button
                      onClick={() => handleDelete(post.id)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Delete
                    </button>
                  )}
                </div>

                <p className="text-gray-700 whitespace-pre-wrap">{post.content}</p>

                {/* Media attachments (if any) */}
                {post.image_url && (
                  <img src={post.image_url} alt="Post" className="mt-3 rounded-lg max-w-full" />
                )}
                {post.video_url && (
                  <video src={post.video_url} controls className="mt-3 rounded-lg max-w-full" />
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
