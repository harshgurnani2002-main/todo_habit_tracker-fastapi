import React from 'react';
import { useDashboardStats } from '../hooks/useData';
import { useUser } from '../context/UserContext';
import Calendar from 'react-calendar';
import '../components/Calendar.css';

const Dashboard = () => {
  const { user } = useUser();
  const { stats, loading, error } = useDashboardStats(user?.token || null);

  // Format stats with fallback values
  const todoStats = stats?.todo_stats || { total: 0, completed: 0, pending: 0, completion_rate: 0 };
  const habitStats = stats?.habit_stats || { total: 0, active: 0, completion_rate: 0, average_streak: 0 };
  const habitHeatmap = stats?.habit_heatmap || [];

  const getTileClassName = ({ date, view }: { date: Date; view: string }) => {
    if (view === 'month') {
      const formattedDate = date.toISOString().split('T')[0];
      const heatmapData = habitHeatmap.find((item: any) => item.date === formattedDate);
      if (heatmapData) {
        if (heatmapData.completed_count > 0 && heatmapData.completed_count <= 2) {
          return 'react-calendar__tile--heatmap-1';
        } else if (heatmapData.completed_count > 2 && heatmapData.completed_count <= 4) {
          return 'react-calendar__tile--heatmap-2';
        } else if (heatmapData.completed_count > 4 && heatmapData.completed_count <= 6) {
          return 'react-calendar__tile--heatmap-3';
        } else if (heatmapData.completed_count > 6) {
          return 'react-calendar__tile--heatmap-4';
        }
      }
    }
    return 'react-calendar__tile--heatmap';
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Dashboard</h1>
      
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
      
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Total Todos</h3>
          <p className="text-3xl font-bold text-teal-600 dark:text-teal-400">{todoStats.total}</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Completed Todos</h3>
          <p className="text-3xl font-bold text-teal-600 dark:text-teal-400">{todoStats.completed}</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Active Habits</h3>
          <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">{habitStats.active}</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Pomodoro Sessions</h3>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400">0</p>
        </div>
      </div>
      
      {/* Habit Heatmap */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Habit Heatmap (Last 30 Days)</h2>
        {habitHeatmap.length > 0 ? (
          <div className="h-auto">
            <Calendar
              tileClassName={getTileClassName}
              className="w-full border-0"
            />
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-lg">
            <p className="text-gray-500 dark:text-gray-400">No habit data available for the heatmap</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;