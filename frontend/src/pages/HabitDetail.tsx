import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Calendar from 'react-calendar';
import '../components/Calendar.css';
import '../components/CalendarOverride.css';

const HabitDetail = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { habit } = location.state || {};

  if (!habit) {
    return <div>Habit not found</div>;
  }

  const getProgressPercentage = (habit: any) => {
    if (!habit.entries || habit.entries.length === 0) return 0;
    const today = new Date().toISOString().split('T')[0];
    const todayEntries = habit.entries.filter((entry: any) => 
      entry.date.split('T')[0] === today
    );
    
    const completedToday = todayEntries.reduce((sum: number, entry: any) => 
      sum + (entry.completed_count || 0), 0
    );
    
    return Math.min(100, Math.round((completedToday / habit.target_count) * 100));
  };

  const completedDates = habit.entries?.map((entry: any) => new Date(entry.date)) || [];

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/habits')} className="text-teal-600 dark:text-teal-400 hover:underline">
        &larr; Back to Habits
      </button>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">{habit.name}</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">{habit.description}</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">Progress</h3>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
              <div 
                className="bg-teal-600 h-4 rounded-full" 
                style={{ width: `${getProgressPercentage(habit)}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400 mt-1">
              <span>
                {habit.entries?.reduce((sum: number, entry: any) => 
                  sum + (entry.completed_count || 0), 0) || 0}/{habit.target_count} completed
              </span>
              <span>{getProgressPercentage(habit)}%</span>
            </div>
          </div>
          
          <div className="flex justify-around">
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Streak</p>
              <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">{habit.streak_count || 0}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Best Streak</p>
              <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">{habit.best_streak || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Completion Calendar</h3>
        <div className="w-full">
          <Calendar
            className="react-calendar-modern w-full text-black dark:text-white"
            tileClassName={({ date, view }) => {
              if (view === 'month' && completedDates.find((d: Date) => d.toDateString() === date.toDateString())) {
                return 'border-2 border-green-500 rounded-full';
              }
              return null;
            }}
            navigationLabel={({ date }) => date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            nextLabel={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>}
            prevLabel={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>}
            next2Label={null}
            prev2Label={null}
          />
        </div>
      </div>
    </div>
  );
};

export default HabitDetail;