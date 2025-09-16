import React, { useState } from 'react';
import { useHabits } from '../hooks/useData';
import { useUser } from '../context/UserContext';

const Habits = () => {
  const { user } = useUser();
  const [showForm, setShowForm] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showEntryForm, setShowEntryForm] = useState<{[key: number]: boolean}>({});
  const [entryData, setEntryData] = useState<{[key: number]: any}>({});
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    frequency: 'daily',
    target_count: 1
  });
  const [filters, setFilters] = useState({
    frequency: '',
    search: ''
  });
  const { habits, loading, error, createHabit, createHabitEntry } = useHabits(user?.token || null, filters);

  const handleCreateHabit = async () => {
    try {
      await createHabit(formData);
      setShowForm(false);
      setFormData({
        name: '',
        description: '',
        frequency: 'daily',
        target_count: 1
      });
    } catch (err) {
      // Error handling is done in the hook
    }
  };

  const handleCreateEntry = async (habitId: number) => {
    try {
      await createHabitEntry(habitId, entryData[habitId] || { completed_count: 1 });
      setShowEntryForm(prev => ({ ...prev, [habitId]: false }));
      setEntryData(prev => ({ ...prev, [habitId]: { completed_count: 1 } }));
    } catch (err) {
      // Error handling is done in the hook
    }
  };

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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Habits</h1>
        <div className="flex space-x-2">
          {/* Filter button for mobile */}
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className="md:hidden p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
          </button>
          <button 
            onClick={() => setShowForm(true)}
            className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Add Habit
          </button>
        </div>
      </div>

      {/* Desktop Filters */}
      <div className="hidden md:block bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Filter by Frequency
            </label>
            <select 
              value={filters.frequency}
              onChange={(e) => setFilters({...filters, frequency: e.target.value})}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Search
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Search habits..."
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
        </div>
      </div>
      
      {/* Mobile Filters */}
      <>
        {showFilters && (
          <div className="md:hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 w-full max-w-md max-h-[90vh] overflow-y-auto">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Filter by Frequency
                  </label>
                  <select 
                    value={filters.frequency}
                    onChange={(e) => setFilters({...filters, frequency: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="">All</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Search
                  </label>
                  <input
                    type="text"
                    value={filters.search}
                    onChange={(e) => setFilters({...filters, search: e.target.value})}
                    placeholder="Search habits..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      setFilters({ frequency: '', search: '' });
                      setShowFilters(false);
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                  >
                    Clear
                  </button>
                  <button
                    onClick={() => setShowFilters(false)}
                    className="flex-1 px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-teal-600 hover:bg-teal-700"
                  >
                    Apply
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </>
      
      {/* Habit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">Create New Habit</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Habit Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter habit name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter description"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Frequency
                </label>
                <select
                  value={formData.frequency}
                  onChange={(e) => setFormData({...formData, frequency: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Target Count
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.target_count}
                  onChange={(e) => setFormData({...formData, target_count: parseInt(e.target.value) || 1})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateHabit}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
              >
                Create Habit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Entry Form Modal */}
      {Object.keys(showEntryForm).map(habitId => 
        showEntryForm[parseInt(habitId)] && (
          <div key={habitId} className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">Log Habit Entry</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Completed Count
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={entryData[parseInt(habitId)]?.completed_count || 1}
                    onChange={(e) => setEntryData(prev => ({
                      ...prev,
                      [parseInt(habitId)]: {
                        ...prev[parseInt(habitId)],
                        completed_count: parseInt(e.target.value) || 1
                      }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={entryData[parseInt(habitId)]?.notes || ''}
                    onChange={(e) => setEntryData(prev => ({
                      ...prev,
                      [parseInt(habitId)]: {
                        ...prev[parseInt(habitId)],
                        notes: e.target.value
                      }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white"
                    placeholder="Add any notes about your progress"
                    rows={3}
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowEntryForm(prev => ({ ...prev, [parseInt(habitId)]: false }))}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleCreateEntry(parseInt(habitId))}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500"
                >
                  Log Entry
                </button>
              </div>
            </div>
          </div>
        )
      )}

      {/* Loading and Error States */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 dark:bg-red-900 rounded-lg p-4">
          <p className="text-red-700 dark:text-red-200">Error: {error}</p>
        </div>
      )}

      {/* Habit List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {habits.length === 0 && !loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">No habits found. Create your first habit!</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {habits.map((habit) => (
              <li key={habit.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">{habit.name}</h3>
                    {habit.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {habit.description}
                      </p>
                    )}
                    <div className="mt-2 flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <span className="mr-3">
                        Frequency: <span className="font-medium">{habit.frequency}</span>
                      </span>
                      <span>
                        Target: <span className="font-medium">{habit.target_count} per {habit.frequency}</span>
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-500 dark:text-gray-400">Streak</p>
                      <p className="text-xl font-bold text-teal-600 dark:text-teal-400">{habit.streak_count || 0}</p>
                    </div>
                    
                    <div className="text-center">
                      <p className="text-sm text-gray-500 dark:text-gray-400">Best</p>
                      <p className="text-xl font-bold text-teal-600 dark:text-teal-400">{habit.best_streak || 0}</p>
                    </div>
                    
                    <button 
                      onClick={() => {
                        setShowEntryForm(prev => ({ ...prev, [habit.id]: true }));
                        setEntryData(prev => ({ 
                          ...prev, 
                          [habit.id]: { completed_count: 1 } 
                        }));
                      }}
                      className="px-3 py-1 bg-teal-100 dark:bg-teal-900 text-teal-800 dark:text-teal-200 rounded-md text-sm font-medium hover:bg-teal-200 dark:hover:bg-teal-800 transition-colors"
                    >
                      Log Entry
                    </button>
                  </div>
                </div>
                
                {/* Progress bar */}
                <div className="mt-3">
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-teal-600 h-2 rounded-full" 
                      style={{ width: `${getProgressPercentage(habit)}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                    <span>
                      {habit.entries?.reduce((sum: number, entry: any) => 
                        sum + (entry.completed_count || 0), 0) || 0}/{habit.target_count} completed
                    </span>
                    <span>{getProgressPercentage(habit)}%</span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Habits;