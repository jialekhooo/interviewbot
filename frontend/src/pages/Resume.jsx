import React, { useState } from "react";
import api from "../lib/api";

export default function Resume() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError("");
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    console.log("Form submitted, file:", file);
    
    if (!file) {
      setError("Please select a file first");
      return;
    }
    
    setLoading(true);
    setError("");
    setResult(null);
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);
    
    console.log("FormData contents:", {
      file: file.name,
      size: file.size,
      type: file.type,
      jobDescription
    });
    
    try {
      console.log("Sending resume for analysis to /api/resume/review...");
      const response = await api.post("/api/resume/review", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Full response:", response);
      console.log("Response data:", response.data);
      
      if (!response.data) {
        throw new Error("No data received from server");
      }
      
      setResult(response.data);
      console.log("Result set successfully:", response.data);
    } catch (err) {
      console.error("Error analyzing resume:", err);
      console.error("Error details:", {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data
      });
      
      const errorMessage = err.response?.data?.detail 
        || err.response?.data?.error
        || err.message 
        || "Analysis failed. Please check console for details.";
      
      setError(errorMessage);
    } finally {
      setLoading(false);
      console.log("Upload process completed");
    }
  };

  const FeedbackDisplay = ({ feedback }) => {
    console.log("Rendering feedback:", feedback, "Type:", typeof feedback);
    
    // If it's a string, render it directly
    if (typeof feedback === 'string') {
      return <>{feedback}</>;
    }
    
    // If it's an object with raw_output
    if (feedback && typeof feedback === 'object' && feedback.raw_output) {
      return <>{feedback.raw_output}</>;
    }
    
    // If it's an object, stringify it
    if (feedback && typeof feedback === 'object') {
      return <pre className="text-xs">{JSON.stringify(feedback, null, 2)}</pre>;
    }
    
    // Fallback
    return <>{String(feedback)}</>;
  };

  const handleReset = () => {
    setFile(null);
    setJobDescription("");
    setResult(null);
    setError("");
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Show results when available */}
          {result && result.review ? (
           <div className="bg-white shadow-xl rounded-lg overflow-hidden">
    <div className="bg-gradient-to-r from-green-500 to-blue-500 px-6 py-4">
      <h2 className="text-2xl font-bold text-white flex items-center">
        <span className="mr-2">✓</span> Resume Feedback & Suggestions
      </h2>
    </div>
    <div className="p-8">
      <div className="bg-gray-50 rounded-lg p-6 overflow-hidden">
        <div className="prose prose-slate max-w-none">
          <div className="text-gray-800 whitespace-pre-wrap leading-relaxed text-base break-words">
            <FeedbackDisplay feedback={result.review} />
          </div>
        </div>
      </div>

                {/* Action buttons */}
      <div className="mt-8 pt-6 border-t border-gray-200 flex gap-4 justify-center flex-wrap">
        <button
          onClick={handleReset}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Analyze Another Resume
        </button>
        <a
          href="/resume-builder"
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium inline-block"
        >
          Create New Resume
        </a>
      </div>
    </div>
  </div>
) : (
            <>
              {/* Upload form */}
              <div className="bg-white shadow-lg rounded-lg p-8">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold mb-2 text-blue-600">Resume Ideas</h2>
                  <p className="text-gray-600">Upload your current resume to get started!</p>
                </div>

                <form onSubmit={handleUpload} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Job position...?
                    </label>
                    <input
                      type="text"
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      placeholder="e.g., Software Engineer, Data Scientist"
                      className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div className="text-center">
                    <label className="inline-block cursor-pointer">
                      <input
                        type="file"
                        accept=".pdf,.docx"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                      <div className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium inline-block">
                        {file ? `Selected: ${file.name}` : "Upload your Resume"}
                      </div>
                    </label>
                    {file && (
                      <p className="mt-2 text-sm text-gray-600">
                        File ready: {file.name}
                      </p>
                    )}
                  </div>

                  {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-center">
                      {error}
                    </div>
                  )}

                  {loading && (
                    <div className="text-center py-4">
                      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      <p className="mt-2 text-gray-600">Analyzing your resume...</p>
                    </div>
                  )}
                </form>

                {/* Tips section at bottom when no results */}
                {!loading && (
                  <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 className="font-semibold text-blue-900 mb-3 text-lg">💡 Quick Tips</h4>
                    <ul className="text-sm text-blue-800 space-y-2">
                      <li>• Use action verbs to describe your achievements</li>
                      <li>• Quantify your accomplishments with numbers and metrics</li>
                      <li>• Tailor your resume to match the job description</li>
                      <li>• Keep formatting clean and consistent</li>
                      <li>• Highlight relevant technical skills and certifications</li>
                    </ul>
                    <div className="mt-4 text-center">
                      <a href="/resume-builder" className="text-blue-600 hover:text-blue-800 font-medium underline">
                        Don't have a resume yet? Click here.
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
