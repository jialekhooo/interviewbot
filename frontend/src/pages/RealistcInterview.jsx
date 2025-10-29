import React, { useState, useRef, useEffect } from 'react';

// Simple icon components to replace @heroicons/react
const VideoCameraIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
  </svg>
);

const MicrophoneIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
  </svg>
);

const UserCircleIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const ChatBubbleLeftRightIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
  </svg>
);

const CheckCircleIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export default function RealisticInterview() {
  // Interview flow state
  const [stage, setStage] = useState('setup'); // setup, interviewing, analyzing, completed
  const [position, setPosition] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [questionCount, setQuestionCount] = useState(0);
  const [error, setError] = useState('');
  const maxQuestions = 5;

  // Recording state
  const [isListening, setIsListening] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [interimText, setInterimText] = useState('');
  
  // Live coaching
  const [liveHints, setLiveHints] = useState([]);
  const [speechMetrics, setSpeechMetrics] = useState({
    wpm: 0,
    fillerCount: 0,
    duration: 0,
    clarity: 'good'
  });

  // Camera state
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [stream, setStream] = useState(null);

  // Refs
  const videoRef = useRef(null);
  const recognitionRef = useRef(null);
  const startTimeRef = useRef(null);
  const silenceTimerRef = useRef(null);
  const aiSpeakingRef = useRef(false);

  const fillerWords = ['um', 'uh', 'like', 'you know', 'actually', 'basically'];

  const API_URL = import.meta.env.PROD 
    ? 'https://interviewbot-rjsi.onrender.com'
    : 'http://localhost:8001';

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      startTimeRef.current = Date.now();
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript + ' ';
        } else {
          interim += transcript;
        }
      }

      if (final) {
        setCurrentAnswer(prev => prev + final);
        analyzeSpeech(currentAnswer + final);
        resetSilenceTimer();
      }
      setInterimText(interim);
    };

    recognition.onend = () => {
      if (isListening && stage === 'interviewing') {
        recognition.start();
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isListening, currentAnswer, stage]);

  // Analyze speech in real-time
  const analyzeSpeech = (text) => {
    const words = text.trim().split(/\s+/);
    const wordCount = words.length;
    
    const elapsed = (Date.now() - startTimeRef.current) / 60000;
    const wpm = elapsed > 0 ? Math.round(wordCount / elapsed) : 0;

    // Count fillers
    let fillerCount = 0;
    const lowerText = text.toLowerCase();
    fillerWords.forEach(filler => {
      const matches = lowerText.match(new RegExp(`\\b${filler}\\b`, 'gi'));
      if (matches) fillerCount += matches.length;
    });

    setSpeechMetrics({
      wpm,
      fillerCount,
      duration: Math.round(elapsed * 60),
      clarity: wpm >= 120 && wpm <= 160 ? 'good' : wpm < 120 ? 'slow' : 'fast'
    });

    // Live coaching hints
    const hints = [];
    if (wpm < 100) hints.push('💡 Speak a bit faster - you seem hesitant');
    if (wpm > 180) hints.push('⚠️ Slow down - speak more clearly');
    if (fillerCount > 5) hints.push('🎯 Try to reduce filler words like "um" and "uh"');
    if (wordCount < 20 && elapsed > 0.5) hints.push('💬 Elaborate more on your answer');
    
    setLiveHints(hints);
  };

  // Reset silence timer (detects when user stops speaking)
  const resetSilenceTimer = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
    
    // If user is silent for 3 seconds, consider answer complete
    silenceTimerRef.current = setTimeout(() => {
      if (currentAnswer.trim().length > 20 && isListening) {
        handleAnswerComplete();
      }
    }, 3000);
  };

  // Start camera
  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: true
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setIsCameraOn(true);
    } catch (err) {
      alert('Camera access denied. Please grant permissions.');
    }
  };

  // Start interview
  const startInterview = async () => {
    if (!resumeFile) {
      setError('Please upload your resume to start the interview');
      return;
    }

    if (!isCameraOn) {
      await startCamera();
    }
    
    setStage('interviewing');
    setError('');
    
    try {
      // Call your existing backend API to get first question
      const formData = new FormData();
      formData.append('file', resumeFile);
      
      // Only append JD file if it exists
      if (jdFile) {
        formData.append('jd_file', jdFile);
      }
      
      formData.append('position', '');
      formData.append('job_description', '');

      const response = await fetch(`${API_URL}/api/interview/start`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Failed to start interview');
      
      const data = await response.json();
      
      // Extract position from response if available
      const extractedPosition = data.position || (jdFile ? 'this position' : 'a position that matches your background');
      setPosition(extractedPosition);
      
      // Get first question from backend
      const firstQuestion = data.question?.text || data.question || 
        `Hello! Thanks for joining today's interview. Let's start - tell me about yourself and your background.`;
      
      setQuestionCount(1);
      setCurrentQuestion(firstQuestion);
      setConversationHistory([{
        type: 'ai',
        text: firstQuestion,
        timestamp: new Date()
      }]);

      // Speak the question
      speakText(firstQuestion);

      // Start listening after AI finishes speaking
      setTimeout(() => {
        if (recognitionRef.current) {
          recognitionRef.current.start();
          setIsListening(true);
        }
      }, 3000);
      
    } catch (err) {
      console.error('Failed to start interview:', err);
      setError('Failed to start interview. Please try again.');
      setStage('setup');
    }
  };

  // Text-to-Speech
  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      aiSpeakingRef.current = true;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      
      utterance.onend = () => {
        aiSpeakingRef.current = false;
      };
      
      window.speechSynthesis.speak(utterance);
    }
  };

  // Handle answer complete
  const handleAnswerComplete = async () => {
    if (!currentAnswer.trim()) return;

    // Stop listening
    setIsListening(false);
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    // Add user's answer to history
    const userMessage = {
      type: 'user',
      text: currentAnswer,
      timestamp: new Date(),
      metrics: { ...speechMetrics }
    };
    setConversationHistory(prev => [...prev, userMessage]);

    // Generate follow-up question
    setStage('analyzing');
    
    setTimeout(async () => {
      const nextQuestion = await generateFollowUpQuestion(currentAnswer);
      
      setCurrentQuestion(nextQuestion);
      setConversationHistory(prev => [...prev, {
        type: 'ai',
        text: nextQuestion,
        timestamp: new Date()
      }]);

      // Speak next question
      speakText(nextQuestion);

      // Check if interview should end
      if (questionCount >= maxQuestions) {
        setTimeout(() => {
          endInterview();
        }, 4000);
      } else {
        // Continue interview
        setQuestionCount(prev => prev + 1);
        setCurrentAnswer('');
        setInterimText('');
        setStage('interviewing');
        
        setTimeout(() => {
          if (recognitionRef.current) {
            recognitionRef.current.start();
            setIsListening(true);
          }
        }, 3000);
      }
    }, 2000);
  };

  // Generate follow-up question based on answer
  const generateFollowUpQuestion = async (answer) => {
    try {
      // Build conversation history for context
      const pastQuestions = conversationHistory
        .filter(msg => msg.type === 'ai')
        .map(msg => msg.text)
        .join('||,');
      
      const pastAnswers = conversationHistory
        .filter(msg => msg.type === 'user')
        .map(msg => msg.text)
        .join('||,');

      // Call your backend for next question
      const formData = new FormData();
      formData.append('file', resumeFile);
      
      // Only append JD file if it was provided at the start
      if (jdFile) {
        formData.append('jd_file', jdFile);
      }
      
      formData.append('position', position || '');
      formData.append('job_description', '');
      formData.append('past_questions', pastQuestions);
      formData.append('past_answers', pastAnswers);
      formData.append('answer', answer);

      const response = await fetch(`${API_URL}/api/interview/answer`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Failed to get next question');
      
      const data = await response.json();
      
      // Check if interview is complete
      if (data.question === 'End of Interview' || questionCount >= maxQuestions) {
        return "Thank you for completing this mock interview! You did great. I'll now analyze your performance and provide detailed feedback.";
      }
      
      return data.question?.text || data.question || "Tell me more about your experience.";
      
    } catch (err) {
      console.error('Failed to generate question:', err);
      // Fallback to generic question if API fails
      if (questionCount === 1) {
        return "That's great! Now, can you describe a challenging project you worked on and how you overcame the obstacles?";
      } else if (questionCount === 2) {
        return "Interesting! How do you typically approach problem-solving when facing technical challenges?";
      } else if (questionCount === 3) {
        return "What technologies or tools are you most excited to learn in the next year?";
      } else {
        return "Finally, what makes you a good fit for this type of role?";
      }
    }
  };

  // End interview
  const endInterview = () => {
    setStage('completed');
    setIsListening(false);
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    const finalMessage = "Thank you for completing this mock interview! You did great. I'll now analyze your performance and provide detailed feedback.";
    
    setConversationHistory(prev => [...prev, {
      type: 'ai',
      text: finalMessage,
      timestamp: new Date()
    }]);
    
    speakText(finalMessage);
  };

  // Calculate overall score
  const calculateScore = () => {
    if (conversationHistory.length === 0) return 0;
    
    const userAnswers = conversationHistory.filter(msg => msg.type === 'user');
    const avgWpm = userAnswers.reduce((sum, msg) => sum + (msg.metrics?.wpm || 0), 0) / userAnswers.length;
    const totalFillers = userAnswers.reduce((sum, msg) => sum + (msg.metrics?.fillerCount || 0), 0);
    
    let score = 70;
    if (avgWpm >= 130 && avgWpm <= 160) score += 15;
    if (totalFillers < 10) score += 10;
    if (userAnswers.length >= maxQuestions) score += 5;
    
    return Math.min(100, score);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-blue-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Setup Stage */}
        {stage === 'setup' && (
          <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <UserCircleIcon className="w-20 h-20 text-indigo-600 mx-auto mb-4" />
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                Realistic Mock Interview
              </h1>
              <p className="text-gray-600">Experience a real interview with AI-powered conversation</p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Your Resume <span className="text-red-500">*</span>
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(e) => {
                    setResumeFile(e.target.files[0]);
                    setError('');
                  }}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                {resumeFile && (
                  <p className="text-sm text-green-600 mt-1">✓ {resumeFile.name}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Job Description (Optional)
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                  onChange={(e) => {
                    setJdFile(e.target.files[0]);
                    setError('');
                  }}
                  className="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent hover:border-indigo-400 transition-colors"
                />
                {jdFile && (
                  <p className="text-sm text-green-600 mt-1">✓ {jdFile.name}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Optional: Upload JD for tailored questions (PDF, DOCX, TXT, PNG/JPG)
                </p>
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {error}
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">✨ What Makes This Realistic:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>✅ AI interviewer speaks and listens to you</li>
                  <li>✅ Follow-up questions based on your answers</li>
                  <li>✅ Real-time speech coaching</li>
                  <li>✅ Natural conversation flow</li>
                  <li>✅ Live performance metrics</li>
                </ul>
              </div>

              <button
                onClick={startInterview}
                disabled={!resumeFile}
                className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-lg font-semibold shadow-lg"
              >
                <VideoCameraIcon className="w-6 h-6" />
                Start Interview
              </button>
              
              {!jdFile && resumeFile && (
                <p className="text-center text-sm text-amber-600">
                  💡 Tip: Upload a job description for more targeted interview questions
                </p>
              )}
            </div>
          </div>
        )}

        {/* Interview Stage */}
        {(stage === 'interviewing' || stage === 'analyzing') && (
          <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3 text-white">
                <ChatBubbleLeftRightIcon className="w-6 h-6" />
                <span className="font-semibold">Live Interview - Question {questionCount} of {maxQuestions}</span>
              </div>
              {isListening && (
                <div className="flex items-center gap-2 bg-green-500 px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  <span className="text-white text-sm font-medium">Listening</span>
                </div>
              )}
              {stage === 'analyzing' && (
                <div className="flex items-center gap-2 bg-yellow-500 px-3 py-1 rounded-full">
                  <span className="text-white text-sm font-medium">Thinking...</span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
              {/* Video + Current Question */}
              <div className="lg:col-span-2 space-y-4">
                <div className="relative bg-gray-900 rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Current Question */}
                <div className="bg-indigo-50 border-l-4 border-indigo-600 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <UserCircleIcon className="w-8 h-8 text-indigo-600 flex-shrink-0" />
                    <div>
                      <div className="text-sm font-semibold text-indigo-900 mb-1">AI Interviewer</div>
                      <p className="text-gray-800">{currentQuestion}</p>
                    </div>
                  </div>
                </div>

                {/* Your Answer (Live) */}
                {(currentAnswer || interimText) && (
                  <div className="bg-purple-50 border-l-4 border-purple-600 rounded-lg p-4">
                    <div className="text-sm font-semibold text-purple-900 mb-1">Your Answer</div>
                    <p className="text-gray-800">
                      {currentAnswer}
                      <span className="text-gray-400 italic">{interimText}</span>
                    </p>
                  </div>
                )}

                {/* Live Coaching Hints */}
                {liveHints.length > 0 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <div className="text-sm font-semibold text-yellow-900 mb-2">💡 Live Coaching</div>
                    <div className="space-y-1">
                      {liveHints.map((hint, idx) => (
                        <div key={idx} className="text-sm text-yellow-800">{hint}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Panel: Metrics + History */}
              <div className="space-y-4">
                {/* Speech Metrics */}
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
                  <h3 className="font-bold text-gray-800 mb-3">📊 Performance</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-700">Words/Min</span>
                      <span className="font-bold">{speechMetrics.wpm}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-700">Filler Words</span>
                      <span className="font-bold">{speechMetrics.fillerCount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-700">Clarity</span>
                      <span className="font-bold capitalize">{speechMetrics.clarity}</span>
                    </div>
                  </div>
                </div>

                {/* Conversation History */}
                <div className="bg-gray-50 rounded-lg p-4 h-80 overflow-y-auto">
                  <h3 className="font-bold text-gray-800 mb-3 sticky top-0 bg-gray-50">Conversation</h3>
                  <div className="space-y-3">
                    {conversationHistory.map((msg, idx) => (
                      <div key={idx} className={`text-sm ${msg.type === 'ai' ? 'text-indigo-800' : 'text-purple-800'}`}>
                        <div className="font-semibold mb-1">
                          {msg.type === 'ai' ? '🤖 Interviewer' : '👤 You'}
                        </div>
                        <div className="text-gray-700">{msg.text.substring(0, 100)}...</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Completed Stage */}
        {stage === 'completed' && (
          <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-8">
              <CheckCircleIcon className="w-20 h-20 text-green-500 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Interview Complete!</h2>
              <p className="text-gray-600">Great job! Here's your performance summary</p>
            </div>

            {/* Overall Score */}
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-8 text-center text-white mb-6">
              <div className="text-6xl font-bold mb-2">{calculateScore()}%</div>
              <div className="text-xl">Overall Performance Score</div>
            </div>

            {/* Detailed Breakdown */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-blue-600">{questionCount}</div>
                <div className="text-sm text-gray-600">Questions Answered</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-green-600">
                  {Math.round(conversationHistory.filter(m => m.type === 'user').reduce((sum, m) => sum + (m.metrics?.wpm || 0), 0) / questionCount) || 0}
                </div>
                <div className="text-sm text-gray-600">Avg. Words/Min</div>
              </div>
            </div>

            <button
              onClick={() => window.location.reload()}
              className="w-full px-6 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
            >
              Start New Interview
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
