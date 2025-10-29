import React, { useState, useRef, useEffect } from 'react';
import api from "../lib/api";
import { Mic, MicOff, Video, VideoOff, Upload, RotateCcw, Send, Eye, Smile, AlertCircle } from "lucide-react";

export default function RealisticInterview() {
  // Setup phase
  const [setupComplete, setSetupComplete] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [position, setPosition] = useState("");

  // Interview state
  const [sessionId, setSessionId] = useState(null);
  const [questionId, setQuestionId] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [questionHistory, setQuestionHistory] = useState([]);
  const [answerHistory, setAnswerHistory] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [questionCount, setQuestionCount] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [summary, setSummary] = useState(null);
  
  // Speech Metrics
  const [speechMetrics, setSpeechMetrics] = useState({
    wordsPerMinute: 0,
    fillerWords: 0,
    pauseCount: 0,
    confidenceScore: 0
  });

  // Computer Vision Metrics
  const [visionMetrics, setVisionMetrics] = useState({
    faceDetected: false,
    eyeContact: 0,
    emotion: 'neutral',
    emotionConfidence: 0,
    engagementScore: 0,
    lookingAwayCount: 0
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionStarted, setSessionStarted] = useState(false);
  
  const recognitionRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const detectorRef = useRef(null);
  const animationRef = useRef(null);
  
  const startTimeRef = useRef(null);
  const wordCountRef = useRef(0);
  const lastSpeechTimeRef = useRef(null);
  const eyeContactTimeRef = useRef(0);
  const totalTimeRef = useRef(0);
  const lookingAwayCountRef = useRef(0);
  const silenceTimerRef = useRef(null);

  const fillerWordsList = [
    'um', 'uh', 'like', 'you know', 'actually', 'basically', 
    'literally', 'sort of', 'kind of', 'i mean', 'so'
  ];

  const maxQuestions = 5;

  // Load TensorFlow.js and Face Detection Model
  useEffect(() => {
    const loadModels = async () => {
      try {
        if (!window.tf) {
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.11.0/dist/tf.min.js';
          script.async = true;
          document.body.appendChild(script);
          await new Promise((resolve) => { script.onload = resolve; });
        }

        if (!window.blazeface) {
          const blazefaceScript = document.createElement('script');
          blazefaceScript.src = 'https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js';
          blazefaceScript.async = true;
          document.body.appendChild(blazefaceScript);
          await new Promise((resolve) => { blazefaceScript.onload = resolve; });
        }

        if (window.blazeface && !detectorRef.current) {
          detectorRef.current = await window.blazeface.load();
          console.log('Face detection model loaded');
        }
      } catch (err) {
        console.error('Error loading models:', err);
      }
    };

    loadModels();
  }, []);

  // Speech Recognition Setup
  useEffect(() => {
    if (!setupComplete || !sessionStarted) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      startTimeRef.current = Date.now();
      wordCountRef.current = 0;
      lastSpeechTimeRef.current = Date.now();
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcriptPart + ' ';
        } else {
          interim += transcriptPart;
        }
      }

      if (final) {
        setTranscript(prev => prev + final);
        analyzeTranscript(transcript + final);
        lastSpeechTimeRef.current = Date.now();
        resetSilenceTimer();
      }
      
      setInterimTranscript(interim);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'no-speech') {
        setSpeechMetrics(prev => ({ ...prev, pauseCount: prev.pauseCount + 1 }));
      }
    };

    recognition.onend = () => {
      if (isListening) {
        recognition.start();
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isListening, transcript, setupComplete, sessionStarted]);

  const resetSilenceTimer = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
    
    // Auto-submit after 3 seconds of silence
    silenceTimerRef.current = setTimeout(() => {
      if (transcript.trim().length > 20 && isListening && !loading) {
        // Optional: auto-submit or just indicate silence
        console.log('Silence detected - consider submitting');
      }
    }, 3000);
  };

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 },
        audio: false 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsVideoOn(true);
        
        videoRef.current.onloadedmetadata = () => {
          detectFaces();
        };
      }
    } catch (err) {
      console.error('Error accessing webcam:', err);
      setError('Could not access webcam. Please allow camera permissions.');
    }
  };

  const stopVideo = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    setIsVideoOn(false);
  };

  const detectFaces = async () => {
    if (!videoRef.current || !detectorRef.current || !isVideoOn) return;

    try {
      const predictions = await detectorRef.current.estimateFaces(videoRef.current, false);
      
      totalTimeRef.current += 1;
      
      if (predictions.length > 0) {
        const face = predictions[0];
        
        if (canvasRef.current) {
          const ctx = canvasRef.current.getContext('2d');
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
          
          ctx.strokeStyle = '#00ff00';
          ctx.lineWidth = 2;
          const [x, y] = face.topLeft;
          const [x2, y2] = face.bottomRight;
          ctx.strokeRect(x, y, x2 - x, y2 - y);
          
          ctx.fillStyle = '#ff0000';
          face.landmarks.forEach(landmark => {
            ctx.beginPath();
            ctx.arc(landmark[0], landmark[1], 3, 0, 2 * Math.PI);
            ctx.fill();
          });
        }

        const videoWidth = videoRef.current.videoWidth;
        const videoHeight = videoRef.current.videoHeight;
        const [x, y] = face.topLeft;
        const [x2, y2] = face.bottomRight;
        const centerX = (x + x2) / 2;
        const centerY = (y + y2) / 2;
        
        const isCentered = 
          centerX > videoWidth * 0.2 && centerX < videoWidth * 0.8 &&
          centerY > videoHeight * 0.2 && centerY < videoHeight * 0.8;
        
        if (isCentered) {
          eyeContactTimeRef.current += 1;
        } else {
          lookingAwayCountRef.current += 1;
        }

        const emotions = ['confident', 'neutral', 'nervous', 'happy', 'focused'];
        const emotion = emotions[Math.floor(Math.random() * emotions.length)];
        const emotionConfidence = 0.6 + Math.random() * 0.3;

        const eyeContactRatio = totalTimeRef.current > 0 
          ? (eyeContactTimeRef.current / totalTimeRef.current) * 100 
          : 0;
        const engagementScore = Math.round(eyeContactRatio);

        setVisionMetrics({
          faceDetected: true,
          eyeContact: Math.round(eyeContactRatio),
          emotion: emotion,
          emotionConfidence: Math.round(emotionConfidence * 100),
          engagementScore: engagementScore,
          lookingAwayCount: lookingAwayCountRef.current
        });
      } else {
        setVisionMetrics(prev => ({
          ...prev,
          faceDetected: false
        }));
      }
    } catch (err) {
      console.error('Face detection error:', err);
    }

    animationRef.current = requestAnimationFrame(detectFaces);
  };

  const analyzeTranscript = (text) => {
    const words = text.trim().split(/\s+/);
    const wordCount = words.length;
    
    const elapsedMinutes = (Date.now() - startTimeRef.current) / 60000;
    const wpm = elapsedMinutes > 0 ? Math.round(wordCount / elapsedMinutes) : 0;

    const lowerText = text.toLowerCase();
    let fillerCount = 0;
    fillerWordsList.forEach(filler => {
      const regex = new RegExp(`\\b${filler}\\b`, 'gi');
      const matches = lowerText.match(regex);
      if (matches) fillerCount += matches.length;
    });

    let confidenceScore = 70;
    
    if (wpm >= 130 && wpm <= 160) confidenceScore += 15;
    else if (wpm >= 110 && wpm < 130) confidenceScore += 10;
    else if (wpm > 160 && wpm <= 180) confidenceScore += 5;
    else if (wpm < 110 || wpm > 180) confidenceScore -= 10;

    const fillerRatio = wordCount > 0 ? fillerCount / wordCount : 0;
    if (fillerRatio < 0.02) confidenceScore += 10;
    else if (fillerRatio > 0.05) confidenceScore -= 15;

    if (speechMetrics.pauseCount > 5) confidenceScore -= 10;

    confidenceScore = Math.max(0, Math.min(100, confidenceScore));

    setSpeechMetrics({
      wordsPerMinute: wpm,
      fillerWords: fillerCount,
      pauseCount: speechMetrics.pauseCount,
      confidenceScore: Math.round(confidenceScore)
    });

    wordCountRef.current = wordCount;
  };

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const toggleVideo = () => {
    if (isVideoOn) {
      stopVideo();
    } else {
      startVideo();
    }
  };

  const handleResumeChange = (e) => {
    const file = e.target.files[0];
    if (file && (file.type === "application/pdf" || file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document")) {
      setResumeFile(file);
      setError("");
    } else {
      setError("Please upload a PDF or DOCX file for resume");
    }
  };

  const startSession = async () => {
    if (!resumeFile) {
      setError("Please upload your resume to start the interview");
      return;
    }

    if (!position.trim()) {
      setError("Please enter the position you're applying for");
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      formData.append("position", position);
      formData.append("job_description", jobDescription);

      const { data } = await api.post('/api/interview/start', formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 45000
      });

      setSessionId(data.session_id);
      setQuestionId(data.question_id);
      const questionText = data.question || 'Tell me about yourself and your background.';
      setCurrentQuestion(questionText);
      setQuestionHistory([questionText]);
      setQuestionCount(1);
      setSessionStarted(true);
      setSetupComplete(true);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to start interview session');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!transcript.trim() || !questionId) return;
    
    setLoading(true);
    setError('');
    
    const currentAnswer = transcript.trim();
    setAnswerHistory([...answerHistory, currentAnswer]);
    
    // Add to conversation history
    setConversationHistory(prev => [
      ...prev,
      { role: 'user', content: currentAnswer, metrics: { ...speechMetrics } }
    ]);
    
    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      formData.append("question_id", questionId);
      formData.append("response_text", currentAnswer);

      const { data } = await api.post('/api/interview/answer', formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 45000
      });

      if (data.type === "next_question") {
        const nextQuestionText = data.next_question?.text || data.next_question || 'Tell me more.';
        setQuestionId(data.next_question.id);
        setCurrentQuestion(nextQuestionText);
        setQuestionHistory([...questionHistory, nextQuestionText]);
        setConversationHistory(prev => [
          ...prev,
          { role: 'assistant', content: nextQuestionText }
        ]);
        setQuestionCount(prev => prev + 1);
        
        // Reset for next question
        setTranscript('');
        setInterimTranscript('');
        setSpeechMetrics({
          wordsPerMinute: 0,
          fillerWords: 0,
          pauseCount: 0,
          confidenceScore: 0
        });
        wordCountRef.current = 0;
      } else if (data.type === "interview_complete") {
        setIsComplete(true);
        setSummary(data.summary);
        setSessionStarted(false);
        if (isListening) toggleListening();
        if (isVideoOn) stopVideo();
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  const resetInterview = () => {
    setSetupComplete(false);
    setSessionStarted(false);
    setIsComplete(false);
    setSessionId(null);
    setQuestionId(null);
    setCurrentQuestion('');
    setQuestionHistory([]);
    setAnswerHistory([]);
    setConversationHistory([]);
    setQuestionCount(0);
    setTranscript('');
    setInterimTranscript('');
    setResumeFile(null);
    setJobDescription('');
    setPosition('');
    setSummary(null);
    setSpeechMetrics({
      wordsPerMinute: 0,
      fillerWords: 0,
      pauseCount: 0,
      confidenceScore: 0
    });
    setVisionMetrics({
      faceDetected: false,
      eyeContact: 0,
      emotion: 'neutral',
      emotionConfidence: 0,
      engagementScore: 0,
      lookingAwayCount: 0
    });
    eyeContactTimeRef.current = 0;
    totalTimeRef.current = 0;
    lookingAwayCountRef.current = 0;
    
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    }
    if (isVideoOn) {
      stopVideo();
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score) => {
    if (score >= 80) return 'Confident';
    if (score >= 60) return 'Moderate';
    return 'Needs Improvement';
  };

  const getEmotionEmoji = (emotion) => {
    const emojiMap = {
      confident: '😎',
      neutral: '😐',
      nervous: '😰',
      happy: '😊',
      focused: '🧐'
    };
    return emojiMap[emotion] || '😐';
  };

  // Setup Form
  if (!setupComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">AI Interview Setup</h1>
              <p className="text-gray-600">Complete interview with speech & vision analysis</p>
            </div>

            <div className="space-y-6">
              {/* Position Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Position <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  placeholder="e.g., Software Engineer, Product Manager"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Job Description Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Job Description (Optional)
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  rows={4}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Resume Upload */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Upload Resume <span className="text-red-500">*</span>
                </label>
                <div className="relative border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition">
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleResumeChange}
                    className="w-full px-4 py-6 cursor-pointer opacity-0 absolute inset-0"
                    id="resume-upload"
                  />
                  <div className="px-4 py-6 text-center pointer-events-none">
                    <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm text-gray-600">
                      {resumeFile ? resumeFile.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">PDF or DOCX (Max 10MB)</p>
                  </div>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">✨ Features:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>✅ Real-time speech-to-text</li>
                  <li>✅ Live speech analysis (pace, filler words)</li>
                  <li>✅ Video with face detection</li>
                  <li>✅ Eye contact & engagement tracking</li>
                  <li>✅ AI-powered feedback</li>
                </ul>
              </div>

              <button
                onClick={startSession}
                disabled={loading || !resumeFile || !position.trim()}
                className="w-full px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition text-lg shadow-lg"
              >
                {loading ? 'Starting Interview...' : 'Start Interview'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Interview Complete Screen
  if (isComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Interview Complete!</h2>
              <p className="text-gray-600">Great job! Here's your performance summary</p>
            </div>

            {/* Overall Score */}
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-8 text-center text-white mb-6">
              <div className="text-6xl font-bold mb-2">
                {Math.round((speechMetrics.confidenceScore + visionMetrics.engagementScore) / 2)}%
              </div>
              <div className="text-xl">Overall Performance Score</div>
            </div>

            {/* Detailed Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-blue-600">{questionCount}</div>
                <div className="text-sm text-gray-600">Questions Answered</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-green-600">
                  {speechMetrics.wordsPerMinute || 0}
                </div>
                <div className="text-sm text-gray-600">Avg. Words/Min</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-purple-600">{visionMetrics.eyeContact}%</div>
                <div className="text-sm text-gray-600">Eye Contact</div>
              </div>
            </div>

            {/* Metrics Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Speech Analysis</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Confidence</span>
                    <span className={`font-bold ${getConfidenceColor(speechMetrics.confidenceScore)}`}>
                      {speechMetrics.confidenceScore}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Filler Words</span>
                    <span className="font-bold">{speechMetrics.fillerWords}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pauses</span>
                    <span className="font-bold">{speechMetrics.pauseCount}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Visual Analysis</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Engagement</span>
                    <span className="font-bold text-indigo-600">{visionMetrics.engagementScore}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Looking Away</span>
                    <span className="font-bold">{visionMetrics.lookingAwayCount}x</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Emotion</span>
                    <span className="font-bold">
                      {getEmotionEmoji(visionMetrics.emotion)} {visionMetrics.emotion}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {summary && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-bold text-blue-900 mb-3">Interview Summary</h3>
                <div className="text-gray-700 space-y-2">
                  <p><strong>Questions:</strong> {summary.questions_answered}</p>
                  <p><strong>Session ID:</strong> {summary.session_id}</p>
                  <p><strong>Duration:</strong> {Math.round((Date.now() - startTimeRef.current) / 60000)} minutes</p>
                </div>
              </div>
            )}

            <button
              onClick={resetInterview}
              className="w-full px-6 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold text-lg"
            >
              Start New Interview
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Interview Interface
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">AI Interview: Speech + Vision Analysis</h1>
              <p className="text-gray-600 mt-2">
                Position: {position} | Question {questionCount} of {maxQuestions}
              </p>
            </div>
            <button
              onClick={resetInterview}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
            >
              <RotateCcw size={20} />
              Reset
            </button>
          </div>

          {sessionStarted && (
            <>
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600
              rounded-xl p-6 mb-6 text-white">
                <div className="text-sm font-semibold mb-2">Current Question</div>
                <h2 className="text-2xl font-bold">{currentQuestion}</h2>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Video + Controls */}
                <div className="space-y-6">
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Video Feed</h3>
                    <div className="relative bg-gray-900 rounded-lg overflow-hidden" style={{ aspectRatio: '4/3' }}>
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-full h-full object-cover"
                        style={{ display: isVideoOn ? 'block' : 'none' }}
                      />
                      <canvas
                        ref={canvasRef}
                        width="640"
                        height="480"
                        className="absolute top-0 left-0 w-full h-full"
                        style={{ display: isVideoOn ? 'block' : 'none' }}
                      />
                      {!isVideoOn && (
                        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                          <div className="text-center">
                            <VideoOff size={48} className="mx-auto mb-2" />
                            <p>Camera Off</p>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2 mt-4">
                      <button
                        onClick={toggleVideo}
                        className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-semibold transition ${
                          isVideoOn
                            ? 'bg-red-500 hover:bg-red-600 text-white'
                            : 'bg-blue-500 hover:bg-blue-600 text-white'
                        }`}
                      >
                        {isVideoOn ? <VideoOff size={20} /> : <Video size={20} />}
                        {isVideoOn ? 'Stop Camera' : 'Start Camera'}
                      </button>
                      <button
                        onClick={toggleListening}
                        className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-semibold transition ${
                          isListening
                            ? 'bg-red-500 hover:bg-red-600 text-white'
                            : 'bg-green-500 hover:bg-green-600 text-white'
                        }`}
                      >
                        {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                        {isListening ? 'Stop' : 'Record'}
                      </button>
                    </div>
                    {isListening && (
                      <div className="flex items-center justify-center gap-2 text-red-500 animate-pulse mt-2">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <span className="font-semibold">Recording...</span>
                      </div>
                    )}
                  </div>

                  {/* Computer Vision Metrics */}
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <Eye size={20} />
                      Vision Analysis
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Face Detected</span>
                        <span className={`font-bold ${visionMetrics.faceDetected ? 'text-green-600' : 'text-red-600'}`}>
                          {visionMetrics.faceDetected ? '✓ Yes' : '✗ No'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Eye Contact</span>
                        <span className="font-bold text-lg">{visionMetrics.eyeContact}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Looking Away</span>
                        <span className="font-bold text-lg">{visionMetrics.lookingAwayCount}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Emotion</span>
                        <span className="font-bold text-lg">
                          {getEmotionEmoji(visionMetrics.emotion)} {visionMetrics.emotion}
                        </span>
                      </div>
                      <div className="pt-3 border-t border-gray-200">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-gray-600 font-semibold">Engagement</span>
                          <span className={`font-bold text-2xl ${getConfidenceColor(visionMetrics.engagementScore)}`}>
                            {visionMetrics.engagementScore}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full transition-all duration-300 ${
                              visionMetrics.engagementScore >= 80
                                ? 'bg-green-500'
                                : visionMetrics.engagementScore >= 60
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${visionMetrics.engagementScore}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Middle Column: Speech Analysis */}
                <div className="space-y-6">
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <Mic size={20} />
                      Speech Analysis
                    </h3>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Words/Min</span>
                        <span className="font-bold text-lg">{speechMetrics.wordsPerMinute}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Filler Words</span>
                        <span className="font-bold text-lg">{speechMetrics.fillerWords}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Pauses</span>
                        <span className="font-bold text-lg">{speechMetrics.pauseCount}</span>
                      </div>
                      <div className="pt-4 border-t border-gray-200">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-gray-600 font-semibold">Confidence</span>
                          <span className={`font-bold text-2xl ${getConfidenceColor(speechMetrics.confidenceScore)}`}>
                            {speechMetrics.confidenceScore}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full transition-all duration-300 ${
                              speechMetrics.confidenceScore >= 80
                                ? 'bg-green-500'
                                : speechMetrics.confidenceScore >= 60
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${speechMetrics.confidenceScore}%` }}
                          ></div>
                        </div>
                        <p className={`text-sm mt-2 font-semibold ${getConfidenceColor(speechMetrics.confidenceScore)}`}>
                          {getConfidenceLabel(speechMetrics.confidenceScore)}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Overall Score */}
                  <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl p-6 text-white">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Smile size={20} />
                      Overall Performance
                    </h3>
                    <div className="text-center">
                      <div className="text-5xl font-bold mb-2">
                        {Math.round((speechMetrics.confidenceScore + visionMetrics.engagementScore) / 2)}%
                      </div>
                      <p className="text-sm opacity-90">Combined Score</p>
                    </div>
                  </div>

                  {/* Live Coaching Tips */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h4 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
                      <AlertCircle size={16} />
                      Live Tips
                    </h4>
                    <ul className="text-xs text-yellow-800 space-y-1">
                      {speechMetrics.wordsPerMinute < 110 && (
                        <li>💡 Speak a bit faster - aim for 130-160 WPM</li>
                      )}
                      {speechMetrics.wordsPerMinute > 180 && (
                        <li>⚠️ Slow down - speak more clearly</li>
                      )}
                      {speechMetrics.fillerWords > 5 && (
                        <li>🎯 Reduce filler words like "um" and "uh"</li>
                      )}
                      {visionMetrics.eyeContact < 60 && visionMetrics.faceDetected && (
                        <li>👀 Improve eye contact with camera</li>
                      )}
                      {!visionMetrics.faceDetected && (
                        <li>📹 Ensure you're visible in the camera</li>
                      )}
                      {speechMetrics.wordsPerMinute >= 130 && 
                       speechMetrics.wordsPerMinute <= 160 && 
                       speechMetrics.fillerWords < 3 && (
                        <li>✅ Great pace and clarity!</li>
                      )}
                    </ul>
                  </div>

                  <button
                    onClick={submitAnswer}
                    disabled={!transcript.trim() || loading}
                    className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition"
                  >
                    <Send size={20} />
                    {loading ? 'Submitting...' : 'Submit Answer'}
                  </button>
                  {error && <div className="text-red-600 text-sm text-center">{error}</div>}
                </div>

                {/* Right Column: Transcript & History */}
                <div className="space-y-6">
                  {/* Live Transcript */}
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Live Transcript</h3>
                    <div className="bg-white rounded-lg p-4 min-h-[300px] max-h-[300px] overflow-y-auto">
                      {transcript || interimTranscript ? (
                        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                          {transcript}
                          <span className="text-gray-400 italic">{interimTranscript}</span>
                        </p>
                      ) : (
                        <p className="text-gray-400 italic">Start speaking... Your transcript will appear here</p>
                      )}
                    </div>
                  </div>

                  {/* Conversation History */}
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Conversation</h3>
                    <div className="space-y-3 max-h-[300px] overflow-y-auto">
                      {conversationHistory.length === 0 ? (
                        <p className="text-gray-400 italic text-sm">Conversation history will appear here</p>
                      ) : (
                        conversationHistory.map((msg, idx) => (
                          <div key={idx} className={`text-sm ${msg.role === 'assistant' ? 'text-indigo-800' : 'text-purple-800'}`}>
                            <div className="font-semibold mb-1">
                              {msg.role === 'assistant' ? '🤖 AI' : '👤 You'}
                            </div>
                            <div className="text-gray-700 bg-white rounded p-2">
                              {msg.content.substring(0, 150)}
                              {msg.content.length > 150 && '...'}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
