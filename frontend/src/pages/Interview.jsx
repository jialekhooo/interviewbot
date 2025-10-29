import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../lib/api";
import { Mic, MicOff, Video, VideoOff, Type, AlertCircle } from "lucide-react";

export default function Interview() {
  const navigate = useNavigate();

  // Interview State
  const [started, setStarted] = useState(false);
  const [file, setFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [questionId, setQuestionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [summary, setSummary] = useState(null);

  // Input Mode State
  const [inputMode, setInputMode] = useState("text"); // "text", "speech", "video"
  const [isRecording, setIsRecording] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");

  // Speech Metrics
  const [speechMetrics, setSpeechMetrics] = useState({
    wordsPerMinute: 0,
    fillerWords: 0,
    pauseCount: 0,
    confidenceScore: 0
  });

  // Refs
  const recognitionRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const startTimeRef = useRef(null);
  const wordCountRef = useRef(0);

  const fillerWordsList = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally', 'sort of', 'kind of', 'i mean', 'so'];

  // Speech Recognition Setup
  useEffect(() => {
    if (inputMode !== "speech" && inputMode !== "video") return;
    if (!started) return;

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
        setAnswer(prev => prev + final);
        analyzeTranscript(transcript + final);
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
      if (isRecording) {
        recognition.start();
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isRecording, transcript, inputMode, started]);

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

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current?.start();
      setIsRecording(true);
    }
  };

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
    setIsVideoOn(false);
  };

  const toggleVideo = () => {
    if (isVideoOn) {
      stopVideo();
    } else {
      startVideo();
    }
  };

  const startInterview = async () => {
    if (!file) {
      setError("Please upload your resume first");
      return;
    }

    if (!jdFile) {
      setError("Please upload the job description file (screenshot/PDF/DOCX)");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("jd_file", jdFile);
    formData.append("position", "Position from Job Description");
    formData.append("job_description", ""); // Empty since we're using file

    try {
      const { data } = await api.post("/api/interview/start", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 45000,
      });

      setSessionId(data.session_id);
      setQuestionId(data.question_id);
      setQuestion({ text: data.question });
      setStarted(true);

      // Auto-start recording if speech/video mode
      if (inputMode === "speech" || inputMode === "video") {
        setTimeout(() => toggleRecording(), 500);
      }
      if (inputMode === "video") {
        setTimeout(() => startVideo(), 500);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start interview");
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!file || !questionId || !answer) return;

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("jd_file", jdFile);
    formData.append("question_id", questionId);
    formData.append("response_text", answer);

    try {
      const { data } = await api.post("/api/interview/answer", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 45000,
      });

      if (data.type === "next_question") {
        setQuestionId(data.next_question.id);
        setQuestion({ text: data.next_question.text });
        setAnswer("");
        setTranscript("");
        setInterimTranscript("");
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
        if (isRecording) toggleRecording();
        if (isVideoOn) stopVideo();
        alert("Interview complete!\n\n" + data.feedback);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit answer");
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h2 className="text-3xl font-bold mb-6 text-blue-600">Mock Interview</h2>
          <p className="text-gray-600 mb-6">
            Upload your resume, job description screenshot/file, and choose your preferred input method
          </p>

          {!started ? (
            <>
              {/* Input Mode Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-3">
                  Choose Interview Mode
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setInputMode("speech")}
                    className={`p-6 border-2 rounded-lg flex flex-col items-center gap-2 transition ${
                      inputMode === "speech" 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-blue-300'
                    }`}
                  >
                    <Mic size={40} className={inputMode === "speech" ? 'text-blue-600' : 'text-gray-600'} />
                    <span className="font-medium text-lg">Voice Interview</span>
                    <span className="text-xs text-gray-500 text-center">Speak your answers with real-time speech analysis</span>
                  </button>

                  <button
                    onClick={() => setInputMode("video")}
                    className={`p-6 border-2 rounded-lg flex flex-col items-center gap-2 transition ${
                      inputMode === "video" 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-blue-300'
                    }`}
                  >
                    <Video size={40} className={inputMode === "video" ? 'text-blue-600' : 'text-gray-600'} />
                    <span className="font-medium text-lg">Video Interview</span>
                    <span className="text-xs text-gray-500 text-center">Full experience with camera + speech metrics</span>
                  </button>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Upload Resume <span className="text-red-500">*</span>
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(e) => setFile(e.target.files[0])}
                  className="w-full"
                />
                {file && (
                  <p className="text-xs text-green-600 mt-1">
                    ✓ {file.name}
                  </p>
                )}
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  Upload Job Description <span className="text-red-500">*</span>
                  <span className="text-xs text-gray-500 ml-2">(screenshot, PDF, DOCX, or TXT)</span>
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                  onChange={(e) => setJdFile(e.target.files[0])}
                  className="w-full"
                />
                {jdFile && (
                  <p className="text-xs text-green-600 mt-1">
                    ✓ {jdFile.name}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  💡 You can upload a screenshot image (.png, .jpg), PDF, DOCX, or text file of the job description
                </p>
              </div>

              <button
                onClick={startInterview}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
                disabled={loading || !file || !jdFile}
              >
                {loading ? "Starting Interview..." : "Start Mock Interview"}
              </button>
            </>
          ) : isComplete ? (
            <div className="space-y-6">
              <div className="bg-green-50 border-l-4 border-green-500 p-4">
                <h3 className="text-xl font-bold text-green-800 mb-2">🎉 Interview Complete!</h3>
                <p className="text-green-700">Thank you for completing the mock interview.</p>
              </div>

              {summary && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-lg text-blue-900 mb-3">Summary</h4>
                  <div className="space-y-2 text-gray-700">
                    <div>Questions Answered: {summary.questions_answered}</div>
                    <div>Session ID: {summary.session_id}</div>
                  </div>
                </div>
              )}

              <button
                onClick={() => {
                  setStarted(false);
                  setIsComplete(false);
                  setFile(null);
                  setJdFile(null);
                  setQuestion(null);
                  setAnswer("");
                  setSummary(null);
                  setTranscript("");
                  setInterimTranscript("");
                  setSpeechMetrics({
                    wordsPerMinute: 0,
                    fillerWords: 0,
                    pauseCount: 0,
                    confidenceScore: 0
                  });
                }}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Start New Interview
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Interview Area */}
              <div className="lg:col-span-2 space-y-4">
                {question && (
                  <div className="p-4 bg-blue-50 rounded border-l-4 border-blue-500">
                    <div className="font-semibold text-blue-900 mb-2">Question:</div>
                    <div className="text-gray-800">{question.text}</div>
                  </div>
                )}

                {/* Video Feed (if video mode) */}
                {inputMode === "video" && (
                  <div className="bg-gray-900 rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover"
                      style={{ display: isVideoOn ? 'block' : 'none' }}
                    />
                    {!isVideoOn && (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <div className="text-center">
                          <VideoOff size={48} className="mx-auto mb-2" />
                          <p>Camera Off</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Answer Input Area */}
                {inputMode === "text" ? (
                  <textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    rows={8}
                    className="w-full p-3 border rounded"
                    placeholder="Type your answer here..."
                  />
                ) : (
                  <div className="bg-white border rounded-lg p-4 min-h-[200px]">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Live Transcript</span>
                      {isRecording && (
                        <span className="flex items-center gap-2 text-red-500 text-sm">
                          <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                          Recording
                        </span>
                      )}
                    </div>
                    <div className="text-gray-800 whitespace-pre-wrap">
                      {transcript || interimTranscript ? (
                        <>
                          {transcript}
                          <span className="text-gray-400 italic">{interimTranscript}</span>
                        </>
                      ) : (
                        <span className="text-gray-400 italic">Your transcript will appear here...</span>
                      )}
                    </div>
                  </div>
                )}

                {/* Control Buttons */}
                <div className="flex gap-2">
                  {(inputMode === "speech" || inputMode === "video") && (
                    <>
                      <button
                        onClick={toggleRecording}
                        className={`flex items-center gap-2 px-4 py-2 rounded font-medium ${
                          isRecording
                            ? 'bg-red-500 hover:bg-red-600 text-white'
                            : 'bg-blue-500 hover:bg-blue-600 text-white'
                        }`}
                      >
                        {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
                        {isRecording ? 'Stop Recording' : 'Start Recording'}
                      </button>

                      {inputMode === "video" && (
                        <button
                          onClick={toggleVideo}
                          className={`flex items-center gap-2 px-4 py-2 rounded font-medium ${
                            isVideoOn
                              ? 'bg-red-500 hover:bg-red-600 text-white'
                              : 'bg-gray-500 hover:bg-gray-600 text-white'
                          }`}
                        >
                          {isVideoOn ? <VideoOff size={20} /> : <Video size={20} />}
                          {isVideoOn ? 'Stop Camera' : 'Start Camera'}
                        </button>
                      )}
                    </>
                  )}

                  <button
                    onClick={submitAnswer}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
                    disabled={loading || !answer.trim()}
                  >
                    {loading ? "Submitting..." : "Submit Answer"}
                  </button>
                </div>
              </div>

              {/* Sidebar - Metrics (if speech/video mode) */}
              {(inputMode === "speech" || inputMode === "video") && (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <Mic size={20} />
                      Speech Analysis
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600 text-sm">Words/Min</span>
                        <span className="font-bold">{speechMetrics.wordsPerMinute}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 text-sm">Filler Words</span>
                        <span className="font-bold">{speechMetrics.fillerWords}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 text-sm">Pauses</span>
                        <span className="font-bold">{speechMetrics.pauseCount}</span>
                      </div>
                      <div className="pt-3 border-t">
                        <div className="flex justify-between mb-2">
                          <span className="text-gray-600 font-medium text-sm">Confidence</span>
                          <span className={`font-bold text-lg ${getConfidenceColor(speechMetrics.confidenceScore)}`}>
                            {speechMetrics.confidenceScore}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${
                              speechMetrics.confidenceScore >= 80
                                ? 'bg-green-500'
                                : speechMetrics.confidenceScore >= 60
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${speechMetrics.confidenceScore}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                      <AlertCircle size={16} />
                      Tips
                    </h4>
                    <ul className="text-xs text-blue-800 space-y-1">
                      <li>• Speak clearly and at a moderate pace</li>
                      <li>• Avoid filler words like "um" and "uh"</li>
                      <li>• Take brief pauses to organize thoughts</li>
                      <li>• Maintain eye contact with camera</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-600">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}