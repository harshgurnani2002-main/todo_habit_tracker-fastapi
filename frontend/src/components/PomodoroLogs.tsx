import React from 'react';

const PomodoroLogs = ({ sessions }: { sessions: any[] }) => {
  const completedSessions = sessions.filter(session => session.completed_at);

  if (completedSessions.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 w-full max-w-2xl">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Completed Sessions</h3>
      <div className="space-y-4">
        {completedSessions.map((session) => (
          <div key={session.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-md font-medium text-gray-900 dark:text-white">{session.title}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{session.description}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500 dark:text-gray-400">{new Date(session.completed_at).toLocaleDateString()}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{session.duration} min</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PomodoroLogs;