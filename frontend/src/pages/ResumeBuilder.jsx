import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import { DocumentTextIcon, SparklesIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

export default function ResumeBuilder() {
  const { user, token } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    major: '',
    education_background: '',
    skills: '',
    internship_experience: '',
    additional_info: ''
  });
  const [loading, setLoading] = useState(false);
  const [generatedResume, setGeneratedResume] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.major || !formData.education_background || !formData.skills || !formData.internship_experience) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedResume(null);
    setSuggestions([]);

    try {
      const response = await api.post('/api/resume-builder/generate', {
        ...formData,
        user_id: user?.username || 'anonymous'
      });

      setGeneratedResume(response.data.resume_text);
      setSuggestions(response.data.suggestions || []);
    } catch (err) {
      console.error('Error generating resume:', err);
      setError(err.response?.data?.detail || 'Failed to generate resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      name: '',
      major: '',
      education_background: '',
      skills: '',
      internship_experience: '',
      additional_info: ''
    });
    setGeneratedResume(null);
    setSuggestions([]);
    setError('');
  };

  const handleDownload = () => {
    if (!generatedResume) return;
    
    const blob = new Blob([generatedResume], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${formData.name.replace(/\s+/g, '_')}_Resume.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
            <DocumentTextIcon className="w-10 h-10 text-purple-600" />
          </div>
          <h1 className="text-4xl font-bold mb-3 text-gray-800">✏️ Crafting your resume</h1>
          <p className="text-lg text-gray-600">Let AI help you create a professional resume</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name */}
              <div>
                <label className="block text-lg font-semibold text-gray-800 mb-2">
                  what's your name?
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Jia Le"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
                  required
                />
              </div>

              {/* Major */}
              <div>
                <label className="block text-lg font-semibold text-gray-800 mb-2">
                  what's your Major?
                </label>
                <input
                  type="text"
                  name="major"
                  value={formData.major}
                  onChange={handleChange}
                  placeholder="EEE"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
                  required
                />
              </div>

              {/* Education Background */}
              <div>
                <label className="block text-lg font-semibold text-gray-800 mb-2">
                  Education background
                </label>
                <textarea
                  name="education_background"
                  value={formData.education_background}
                  onChange={handleChange}
                  placeholder="e.g., Bachelor of Science in Electrical Engineering, XYZ University, 2020-2024"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition-colors resize-none"
                  rows={3}
                  required
                />
              </div>

              {/* Skills */}
              <div>
                <label className="block text-lg font-semibold text-gray-800 mb-2">
                  Skills you have
                </label>
                <textarea
                  name="skills"
                  value={formData.skills}
                  onChange={handleChange}
                  placeholder="e.g., Python, Java, Circuit Design, MATLAB, Problem Solving"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition-colors resize-none"
                  rows={3}
                  required
                />
              </div>

              {/* Internship Experience */}
              <div>
                <label className="block text-lg font-semibold text-gray-800 mb-2">
                  Internship Experience
                </label>
                <textarea
                  name="internship_experience"
                  value={formData.internship_experience}
                  onChange={handleChange}
                  placeholder="e.g., Software Engineering Intern at ABC Company (Summer 2023) - Developed web applications..."
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition-colors resize-none"
                  rows={4}
                  required
                />
              </div>

              {/* Additional Info */}
              <div>
                <label className="block text-lg font-semibold text-gray-800 mb-2">
                  Anything you want to add?
                </label>
                <textarea
                  name="additional_info"
                  value={formData.additional_info}
                  onChange={handleChange}
                  placeholder="e.g., Awards, certifications, projects, languages, interests..."
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition-colors resize-none"
                  rows={3}
                />
              </div>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <>
                    <ArrowPathIcon className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5" />
                    submit
                  </>
                )}
              </button>

              {generatedResume && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="w-full px-6 py-3 border-2 border-gray-300 text-gray-700 text-lg font-semibold rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Start Over
                </button>
              )}
            </form>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {loading && (
              <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Crafting your professional resume...</p>
              </div>
            )}

            {generatedResume && !loading && (
              <>
                {/* Generated Resume */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-800">Your Resume</h3>
                    <button
                      onClick={handleDownload}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      Download
                    </button>
                  </div>
                  <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap font-mono text-sm text-gray-800">
                      {generatedResume}
                    </pre>
                  </div>
                </div>

                {/* Suggestions */}
                {suggestions.length > 0 && (
                  <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                      <SparklesIcon className="w-6 h-6 text-purple-600" />
                      Suggestions for Improvement
                    </h3>
                    <ul className="space-y-3">
                      {suggestions.map((suggestion, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <span className="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                            {idx + 1}
                          </span>
                          <span className="text-gray-700 flex-1">{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}

            {!generatedResume && !loading && (
              <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <DocumentTextIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Fill in the form and click submit to generate your resume</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
