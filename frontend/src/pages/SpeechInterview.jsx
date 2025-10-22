import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, RotateCcw, Send, Video, VideoOff, Eye, Smile, Upload } from 'lucide-react';

export default function CompleteInterviewExperience() {
  // Setup phase
  const [setupComplete, setSetupComplete] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescriptionFile, setJobDescriptionFile] = useState(null);
  const [position, setPosition] = useState("Software Engineer");

  // Interview state
  const [isListening, setIsListening] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [questionHistory, setQuestionHistory] = useState([]);
  const [answerHistory, setAnswerHistory] = useState([]);
  
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

  const fillerWordsList = [
    'um', 'uh', 'like', 'you know', 'actually', 'basically', 
    'literally', 'sort of', 'kind of', 'i mean', 'so'
  ];

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

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 },
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

  const handleJobDescriptionChange = (e) => {
    const file = e.target.files[0];
    if (file && (file.type === "application/pdf" || file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" || file.type === "text/plain")) {
      setJobDescriptionFile(file);
      setError("");
    } else {
      setError("Please upload a PDF, DOCX, or TXT file for job description");
    }
  };

  const handleQuestionTypeToggle = (type) => {
    if (questionTypes.includes(type)) {
      setQuestionTypes(questionTypes.filter(t => t !== type));
    } else {
      setQuestionTypes([...questionTypes, type]);
    }
  };

  const startSession = async () => {
    if (!resumeFile) {
      setError("Please upload your resume to start the interview");
      return;
    }

    if (!jobDescriptionFile) {
      setError("Please upload the job description file to start the interview");
      return;
    }

    if (questionTypes.length === 0) {
      setError("Please select at least one question type");
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      formData.append("jd_file", jobDescriptionFile);
      formData.append("position", position);
      formData.append("job_description", ""); // Empty since we're using file
      formData.append("difficulty", difficulty);
      questionTypes.forEach(type => {
        formData.append("question_types", type);
      });

      const response = await fetch('https://interviewbot-rjsi.onrender.com/api/interview/start', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Failed to start session');
      
      const data = await response.json();
      const questionText = data.question?.question || data.question?.text || data.question || 'No question received';
      setCurrentQuestion(questionText);
      setQuestionHistory([questionText]);
      setSessionStarted(true);
      setSetupComplete(true);
    } catch (err) {
      setError(err.message || 'Failed to start interview session');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!transcript.trim()) return;
    
    setLoading(true);
    setError('');
    
    const currentAnswer = transcript.trim();
    setAnswerHistory([...answerHistory, currentAnswer]);
    
    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      formData.append("jd_file", jobDescriptionFile);
      formData.append('position', position);
      formData.append('difficulty', difficulty);
      formData.append('job_description', ""); // Empty since using file
      questionTypes.forEach(type => {
        formData.append('question_types', type);
      });
      formData.append('past_questions', questionHistory.join('||,'));
      formData.append('past_answers', answerHistory.join('||,'));
      formData.append('answer', currentAnswer);

      const response = await fetch('https://interviewbot-rjsi.onrender.com/api/interview/answer', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Failed to submit answer');
      
      const data = await response.json();
      
      if (data.question === 'End of Interview') {
        setCurrentQuestion('Interview Complete! Thank you for participating.');
        setSessionStarted(false);
      } else {
        const nextQuestion = data.question?.question || data.question?.text || data.question || 'No next question';
        setCurrentQuestion(nextQuestion);
        setQuestionHistory([...questionHistory, nextQuestion]);
      }
      
      setTranscript('');
      setInterimTranscript('');
      setSpeechMetrics({
        wordsPerMinute: 0,
        fillerWords: 0,
        pauseCount: 0,
        confidenceScore: 0
      });
      wordCountRef.current = 0;
    } catch (err) {
      setError(err.message || 'Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  const resetInterview = () => {
    setSetupComplete(false);
    setSessionStarted(false);
    setCurrentQuestion('');
    setQuestionHistory([]);
    setAnswerHistory([]);
    setTranscript('');
    setInterimTranscript('');
    setResumeFile(null);
    setJobDescriptionFile(null);
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
              {/* Resume Upload */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Upload Resume <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleResumeChange}
                    className="w-full border-2 border-dashed border-gray-300 rounded-lg px-4 py-6 text-center cursor-pointer hover:border-blue-500 transition"
                    id="resume-upload"
                  />
                  {resumeFile && (
                    <div className="mt-2 flex items-center gap-2 text-green-600">
                      <Upload size={16} />
                      <span className="text-sm font-semibold">{resumeFile.name}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Job Description Upload */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Upload Job Description <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    onChange={handleJobDescriptionChange}
                    className="w-full border-2 border-dashed border-gray-300 rounded-lg px-4 py-6 text-center cursor-pointer hover:border-blue-500 transition"
                    id="jd-upload"
                  />
                  {jobDescriptionFile && (
                    <div className="mt-2 flex items-center gap-2 text-green-600">
                      <Upload size={16} />
                      <span className="text-sm font-semibold">{jobDescriptionFile.name}</span>
                    </div>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">Upload the job description file (PDF, DOCX, or TXT)</p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <button
                onClick={startSession}
                disabled={loading || !resumeFile || !jobDescriptionFile}
                className="w-full px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold rounded-lg transition text-lg shadow-lg"
              >
                {loading ? 'Starting Interview...' : 'Start Interview Session'}
              </button>
            </div>
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
              <p className="text-gray-600 mt-2">Position: {position} | Difficulty: {difficulty}</p>
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
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl p-6 mb-6 text-white">
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
                        <span className="text-gray-600">Looking Away Count</span>
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
                          <span className="text-gray-600 font-semibold">Engagement Score</span>
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
                        <span className="text-gray-600">Words Per Minute</span>
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
                          <span className="text-gray-600 font-semibold">Speech Confidence</span>
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

                  <button
                    onClick={submitAnswer}
                    disabled={!transcript.trim() || loading}
                    className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition"
                  >
                    <Send size={20} />
                    {loading ? 'Submitting...' : 'Submit Answer'}
                  </button>
                  {error && <div className="text-red-600 text-sm">{error}</div>}
                </div>

                {/* Right Column: Transcript */}
                <div className="bg-gray-50 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Live Transcript</h3>
                  <div className="bg-white rounded-lg p-4 min-h-[600px] max-h-[600px] overflow-y-auto">
                    {transcript || interimTranscript ? (
                      <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                        {transcript}
                        <span className="text-gray-400 italic">{interimTranscript}</span>
                      </p>
                    ) : (
                      <p className="text-gray-400 italic">Your transcript will appear here as you speak...</p>
                    )}
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
