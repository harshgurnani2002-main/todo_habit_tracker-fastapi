import React, { useState, useEffect } from 'react';
import { usePomodoroSessions } from '../hooks/useData';
import { useUser } from '../context/UserContext';
import PomodoroLogs from '../components/PomodoroLogs';

const Pomodoro = () => {
  const { user } = useUser();
  const { sessions, loading, error, createSession, deleteSession } = usePomodoroSessions(user?.token || null);
  const [selectedSession, setSelectedSession] = useState<any>(null);
  
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isActive, setIsActive] = useState(false);
  const [mode, setMode] = useState<'work' | 'break'>('work');
  const [sessionsCompleted, setSessionsCompleted] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    duration: 25,
    break_duration: 5
  });

  useEffect(() => {
    if (selectedSession) {
      setTimeLeft(selectedSession.duration * 60);
    }
  }, [selectedSession]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(time => time - 1);
      }, 1000);
    } else if (isActive && timeLeft === 0) {
      // Timer finished
      setIsActive(false);
      // Play sound or notification
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, timeLeft]);

  const toggleTimer = () => {
    setIsActive(!isActive);
  };

  const resetTimer = () => {
    setIsActive(false);
    if (selectedSession) {
      setTimeLeft(mode === 'work' ? selectedSession.duration * 60 : selectedSession.break_duration * 60);
    }
  };

  const switchMode = () => {
    if (mode === 'work') {
      setMode('break');
      if (selectedSession) {
        setTimeLeft(selectedSession.break_duration * 60);
      }
    } else {
      setMode('work');
      if (selectedSession) {
        setTimeLeft(selectedSession.duration * 60);
      }
      setSessionsCompleted(sessionsCompleted + 1);
    }
    setIsActive(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleCreateSession = async () => {
    try {
      const newSession = await createSession(formData);
      setShowForm(false);
      setFormData({
        title: '',
        description: '',
        duration: 25,
        break_duration: 5
      });
      setSelectedSession(newSession);
    } catch (err) {
      // Error handling is done in the hook
    }
  };

  if (selectedSession) {
    return (
      <div className="space-y-6">
        <button onClick={() => setSelectedSession(null)} className="text-teal-600 dark:text-teal-400 hover:underline">
          &larr; Back to Sessions
        </button>
        {/* Timer Display */}
        <div className="min-h-screen flex flex-col items-center">
          <div className="mt-16 mb-6">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${ 
              mode === 'work' 
                ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' 
                : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            }`}>
              {mode === 'work' ? 'Work Time' : 'Break Time'}
            </span>
          </div>
          
          <div className="relative w-80 h-80 md:w-96 md:h-96 rounded-full border-8 border-gray-200 dark:border-gray-700 flex items-center justify-center mb-8">
            <div className="text-6xl md:text-7xl font-bold text-gray-800 dark:text-white">
              {formatTime(timeLeft)}
            </div>
            
            {/* Progress circle */}
            <svg className="absolute inset-0 w-full h-full transform -rotate-90">
              <circle
                cx="50%"
                cy="50%"
                r="45%"
                stroke={mode === 'work' ? '#EF4444' : '#10B981'}
                strokeWidth="8"
                fill="transparent"
                strokeDasharray="283"
                strokeDashoffset={283 - (283 * (timeLeft / (mode === 'work' ? selectedSession.duration * 60 : selectedSession.break_duration * 60)))} 
                className="transition-all duration-1000 ease-linear"
              />
            </svg>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={toggleTimer}
              className={`px-6 py-3 rounded-lg font-medium text-white ${ 
                isActive 
                  ? 'bg-yellow-500 hover:bg-yellow-600' 
                  : 'bg-green-500 hover:bg-green-600'
              }`}
            >
              {isActive ? 'Pause' : 'Start'}
            </button>
            
            <button
              onClick={resetTimer}
              className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium"
            >
              Reset
            </button>
            
            <button
              onClick={switchMode}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium"
            >
              Skip
            </button>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-gray-600 dark:text-gray-400">
              Sessions completed: <span className="font-bold text-red-600 dark:text-red-400">{sessionsCompleted}</span>
            </p>
          </div>
          <PomodoroLogs sessions={sessions} />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Pomodoro Sessions</h1>
        <button 
          onClick={() => setShowForm(true)}
          className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          New Session
        </button>
      </div>

      {/* Pomodoro Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">Create New Session</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Session Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter session title"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter description"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Work Duration (minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.duration}
                  onChange={(e) => setFormData({...formData, duration: parseInt(e.target.value) || 25})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Break Duration (minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.break_duration}
                  onChange={(e) => setFormData({...formData, break_duration: parseInt(e.target.value) || 5})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateSession}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-500"
              >
                Create Session
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading and Error States */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500"></div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 dark:bg-red-900 rounded-lg p-4">
          <p className="text-red-700 dark:text-red-200">Error: {error}</p>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sessions.length === 0 && !loading ? (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">No sessions found. Create your first session!</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div 
              key={session.id} 
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-xl transform hover:-translate-y-1 cursor-pointer"
              onClick={() => setSelectedSession(session)}
            >
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">{session.title}</h3>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }}
                    className="p-2 text-red-400 hover:text-red-600 focus:outline-none rounded-full hover:bg-red-100 dark:hover:bg-red-800"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
                {session.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    {session.description}
                  </p>
                )}
                <div className="mt-4 flex justify-between text-sm text-gray-500 dark:text-gray-400">
                  <span>Work: {session.duration} min</span>
                  <span>Break: {session.break_duration} min</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      <PomodoroLogs sessions={sessions} />
    </div>
  );
};

export default Pomodoro;