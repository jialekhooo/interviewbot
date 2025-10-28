import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import { 
  VideoCameraIcon, 
  StopIcon, 
  ArrowUpTrayIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

export default function VideoInterview() {
  const { user, token } = useAuth();
  const [sessionId, setSessionId] = useState(null);
  const [position, setPosition] = useState('Software Engineer');
  const [question, setQuestion] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [status, setStatus] = useState('idle'); // idle, recording, recorded, uploading, processing, completed, error
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState('');
  const [stream, setStream] = useState(null);
  
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // Sample interview questions
  const sampleQuestions = [
    "Tell me about yourself and your background.",
    "What are your greatest strengths and weaknesses?",
    "Describe a challenging project you worked on and how you overcame obstacles.",
    "Where do you see yourself in 5 years?",
    "Why do you want to work for our company?",
    "Tell me about a time you demonstrated leadership.",
    "How do you handle stress and pressure?",
    "What motivates you in your work?"
  ];

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: true
      });
      
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Failed to access camera. Please ensure camera permissions are granted.');
    }
  };

  const startRecording = async () => {
    if (!stream) {
      await startCamera();
      return;
    }

    try {
      // Create session first
      const response = await api.post('/api/video-interview/create', {
        user_id: user?.username || 'anonymous',
        position: position,
        question_text: question
      });

      setSessionId(response.data.session_id);
      
      // Start recording
      chunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9'
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        setRecordedBlob(blob);
        setStatus('recorded');
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setStatus('recording');
      setError('');
    } catch (err) {
      console.error('Error starting recording:', err);
      setError(err.response?.data?.detail || 'Failed to start recording');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop camera stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        setStream(null);
      }
    }
  };

  const uploadVideo = async () => {
    if (!recordedBlob || !sessionId) return;

    setStatus('uploading');
    setError('');

    try {
      const formData = new FormData();
      formData.append('video', recordedBlob, 'interview.webm');

      const response = await api.post(
        `/api/video-interview/upload/${sessionId}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setUploadProgress(percentCompleted);
          }
        }
      );

      setStatus('processing');
      
      // Poll for results
      pollForResults(sessionId);
    } catch (err) {
      console.error('Error uploading video:', err);
      setError(err.response?.data?.detail || 'Failed to upload video');
      setStatus('error');
    }
  };

  const pollForResults = async (sid) => {
    const maxAttempts = 30; // 30 attempts = 1 minute
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await api.get(`/api/video-interview/status/${sid}`);
        const data = response.data;

        if (data.status === 'completed') {
          // Fetch full results
          const resultsResponse = await api.get(`/api/video-interview/results/${sid}`);
          setFeedback(resultsResponse.data);
          setStatus('completed');
        } else if (data.status === 'failed') {
          setError('Video analysis failed. Please try again.');
          setStatus('error');
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 2000); // Poll every 2 seconds
        } else {
          setError('Analysis is taking longer than expected. Please check back later.');
          setStatus('error');
        }
      } catch (err) {
        console.error('Error polling results:', err);
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 2000);
        } else {
          setError('Failed to get results. Please try again.');
          setStatus('error');
        }
      }
    };

    poll();
  };

  const resetInterview = () => {
    setSessionId(null);
    setRecordedBlob(null);
    setUploadProgress(0);
    setStatus('idle');
    setFeedback(null);
    setError('');
    setIsRecording(false);
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  if (!token) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">Please Login</h2>
          <p className="text-gray-600">You need to be logged in to access video interviews.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-lg p-6 mb-6 text-white">
          <h1 className="text-3xl font-bold mb-2">Video Mock Interview</h1>
          <p className="text-purple-100">Record your interview response and get AI-powered feedback</p>
        </div>

        {status === 'idle' && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Setup Your Interview</h2>
            
            {/* Position Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Position
              </label>
              <input
                type="text"
                value={position}
                onChange={(e) => setPosition(e.target.value)}
                placeholder="e.g., Software Engineer, Product Manager"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            {/* Question Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Interview Question
              </label>
              <select
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 mb-3"
              >
                <option value="">Select a question...</option>
                {sampleQuestions.map((q, idx) => (
                  <option key={idx} value={q}>{q}</option>
                ))}
              </select>
              
              <p className="text-sm text-gray-500 mb-3">Or enter your own:</p>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Enter your interview question..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows={3}
              />
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600">
                {error}
              </div>
            )}

            <button
              onClick={startCamera}
              disabled={!question.trim()}
              className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium text-lg"
            >
              <VideoCameraIcon className="w-6 h-6" />
              Start Camera
            </button>
          </div>
        )}

        {(status === 'recording' || stream) && status !== 'recorded' && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-800 mb-2">Question:</h3>
              <p className="text-gray-700 bg-purple-50 p-4 rounded-lg">{question}</p>
            </div>

            {/* Video Preview */}
            <div className="mb-6">
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="w-full rounded-lg bg-black"
                style={{ maxHeight: '500px' }}
              />
            </div>

            {isRecording && (
              <div className="mb-4 flex items-center justify-center gap-2 text-red-600">
                <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
                <span className="font-medium">Recording...</span>
              </div>
            )}

            <div className="flex gap-4">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  className="flex-1 flex items-center justify-center gap-3 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
                >
                  <VideoCameraIcon className="w-6 h-6" />
                  Start Recording
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="flex-1 flex items-center justify-center gap-3 px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-colors font-medium"
                >
                  <StopIcon className="w-6 h-6" />
                  Stop Recording
                </button>
              )}
            </div>
          </div>
        )}

        {status === 'recorded' && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-6">
              <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Recording Complete!</h3>
              <p className="text-gray-600">Ready to upload and analyze your response</p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={uploadVideo}
                className="flex-1 flex items-center justify-center gap-3 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
              >
                <ArrowUpTrayIcon className="w-6 h-6" />
                Upload & Analyze
              </button>
              <button
                onClick={resetInterview}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Start Over
              </button>
            </div>
          </div>
        )}

        {status === 'uploading' && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">Uploading Video...</h3>
            <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
              <div
                className="bg-purple-600 h-4 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-center text-gray-600">{uploadProgress}%</p>
          </div>
        )}

        {status === 'processing' && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Analyzing Your Response...</h3>
            <p className="text-gray-600">This may take a minute. Please wait.</p>
          </div>
        )}

        {status === 'completed' && feedback && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-6">
              <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Analysis Complete!</h3>
            </div>

            {/* Scores */}
            {feedback.scores && (
              <div className="mb-6 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
                <h4 className="text-lg font-bold text-gray-800 mb-4">Your Scores</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(feedback.scores).map(([key, value]) => (
                    <div key={key} className="text-center">
                      <div className="text-3xl font-bold text-purple-600">{value}/10</div>
                      <div className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Transcript */}
            {feedback.transcript && (
              <div className="mb-6">
                <h4 className="text-lg font-bold text-gray-800 mb-3">Transcript</h4>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-700 whitespace-pre-wrap">{feedback.transcript}</p>
                </div>
              </div>
            )}

            {/* Feedback */}
            <div className="mb-6">
              <h4 className="text-lg font-bold text-gray-800 mb-3">Detailed Feedback</h4>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-gray-700 whitespace-pre-wrap">{feedback.feedback}</p>
              </div>
            </div>

            {/* Analysis Details */}
            {feedback.analysis && (
              <div className="space-y-4">
                {feedback.analysis.strengths && (
                  <div>
                    <h4 className="text-lg font-bold text-green-700 mb-2">Strengths</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {feedback.analysis.strengths.map((strength, idx) => (
                        <li key={idx} className="text-gray-700">{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {feedback.analysis.areas_for_improvement && (
                  <div>
                    <h4 className="text-lg font-bold text-orange-700 mb-2">Areas for Improvement</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {feedback.analysis.areas_for_improvement.map((area, idx) => (
                        <li key={idx} className="text-gray-700">{area}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {feedback.analysis.specific_suggestions && (
                  <div>
                    <h4 className="text-lg font-bold text-blue-700 mb-2">Specific Suggestions</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {feedback.analysis.specific_suggestions.map((suggestion, idx) => (
                        <li key={idx} className="text-gray-700">{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <button
              onClick={resetInterview}
              className="mt-6 w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
            >
              Start New Interview
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <XCircleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-800 mb-2">Something Went Wrong</h3>
            <p className="text-red-600 mb-6">{error}</p>
            <button
              onClick={resetInterview}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
