import React, { useState } from "react";

const baseURL = "https://interviewbot-rjsi.onrender.com";

export default function Resume() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("upload"); // 'upload' or 'review'

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError("");
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await fetch(`${baseURL}/api/resume/analyze`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Analysis failed");
      const data = await response.json();
      setResult({ type: "analysis", data });
    } catch (err) {
      setError(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);
    try {
      const response = await fetch(`${baseURL}/api/resume/review`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Review failed");
      const data = await response.json();
      setResult({ type: "review", data });
    } catch (err) {
      setError(err.message || "Review failed");
    } finally {
      setLoading(false);
    }
  };

  const formatReviewText = (text) => {
    if (!text) return "";
    
    // Split by double newlines to get paragraphs
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((para, idx) => {
      const trimmed = para.trim();
      if (!trimmed) return null;
      
      // Check if it's a header (starts with ##, is short, ends with :, or is all caps)
      const isHeader = trimmed.startsWith('##') || 
                      trimmed.startsWith('#') || 
                      trimmed.endsWith(':') ||
                      (trimmed.length < 100 && trimmed === trimmed.toUpperCase());
      
      if (isHeader) {
        const headerText = trimmed.replace(/^#+\s*/, ''); // Remove markdown ##
        return (
          <h3 key={idx} className="text-xl font-bold text-blue-700 mt-6 mb-3">
            {headerText}
          </h3>
        );
      }
      
      // Check if it's a bullet point
      if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) {
        return (
          <li key={idx} className="ml-6 mb-2 text-gray-700 leading-relaxed">
            {trimmed.replace(/^[-•*]\s*/, '')}
          </li>
        );
      }
      
      // Regular paragraph
      return (
        <p key={idx} className="mb-4 text-gray-700 leading-relaxed">
          {trimmed}
        </p>
      );
    }).filter(Boolean);
  };

  return (
    <div className="max-w-4xl mx-auto mt-12 p-6">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-8">
          <h2 className="text-3xl font-bold text-white mb-2">Resume Review & Analysis</h2>
          <p className="text-blue-100">Get AI-powered feedback to improve your resume</p>
        </div>

        <div className="border-b border-gray-200">
          <div className="flex">
            <button
              onClick={() => setActiveTab("upload")}
              className={`flex-1 px-6 py-4 font-semibold transition ${
                activeTab === "upload"
                  ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50"
                  : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
              }`}
            >
              Parse Resume
            </button>
            <button
              onClick={() => setActiveTab("review")}
              className={`flex-1 px-6 py-4 font-semibold transition ${
                activeTab === "review"
                  ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50"
                  : "text-gray-600 hover:text-gray-800 hover:bg-gray-50"
              }`}
            >
              Get Improvement Tips
            </button>
          </div>
        </div>

        <div className="p-6">
          {activeTab === "upload" ? (
            <form onSubmit={handleAnalyze} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Upload Resume (PDF or DOCX)
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                disabled={!file || loading}
                className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
              >
                {loading ? "Analyzing..." : "Parse Resume"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleReview} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Upload Resume (PDF or DOCX)
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Job Description (Optional)
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here for tailored suggestions..."
                  rows={4}
                  className="w-full border-2 border-gray-300 rounded-lg px-4 py-3 focus:border-blue-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                disabled={!file || loading}
                className="w-full px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
              >
                {loading ? "Generating Review..." : "Get Improvement Tips"}
              </button>
            </form>
          )}

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-8">
              {result.type === "analysis" ? (
                <>
                  <h3 className="text-xl font-bold text-gray-800 mb-4">Parsed Resume Data</h3>
                  <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                      {JSON.stringify(result.data.analysis, null, 2)}
                    </pre>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-gray-800">Resume Review</h3>
                    <span className="text-sm text-gray-500">
                      Reviewing: {file?.name}
                    </span>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 prose prose-blue max-w-none">
                    {formatReviewText(result.data.review)}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
