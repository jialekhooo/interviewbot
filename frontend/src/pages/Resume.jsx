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

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto bg-white shadow-lg rounded-lg p-8">
        <h2 className="text-3xl font-bold mb-2 text-blue-600">Resume Ideas</h2>
        <p className="text-gray-600 mb-6">Get suggestions for your resume and stand out from all other interviewees</p>
        
        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload your Resume
            </label>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Position (Optional)
            </label>
            <input
              type="text"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="e.g., Software Engineer, Data Scientist"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={!file || loading}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? "Analyzing..." : "Get Resume Feedback"}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8">
            {result.review ? (
              <div className="bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-500 p-6 rounded-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="mr-2">✓</span> Resume Feedback & Suggestions
                </h3>
                <div className="prose max-w-none">
                  <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                    <FeedbackDisplay feedback={result.review} />
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                <p className="text-yellow-800">Received response but no review data found.</p>
                <details className="mt-2">
                  <summary className="cursor-pointer text-sm text-yellow-700">Show raw response</summary>
                  <pre className="mt-2 text-xs bg-white p-2 rounded overflow-auto">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </details>
              </div>
            )}

            {/* Additional tips section */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">💡 Quick Tips</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Use action verbs to describe your achievements</li>
                <li>• Quantify your accomplishments with numbers and metrics</li>
                <li>• Tailor your resume to match the job description</li>
                <li>• Keep formatting clean and consistent</li>
                <li>• Highlight relevant technical skills and certifications</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
