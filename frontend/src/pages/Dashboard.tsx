import React from 'react';
import { useDashboardStats } from '../hooks/useData';
import { useUser } from '../context/UserContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const { user } = useUser();
  const { stats, loading, error } = useDashboardStats(user?.token || null);

  // Format stats with fallback values
  const todoStats = stats?.todo_stats || { total: 0, completed: 0, pending: 0, completion_rate: 0 };
  const habitStats = stats?.habit_stats || { total: 0, active: 0, completion_rate: 0, average_streak: 0 };
  const productivityTrend = stats?.productivity_trend || [];

  // Format the productivity trend data for the chart
  const chartData = productivityTrend.map((item) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' }),
    todos: item.todos_completed,
    habits: item.habits_completed
  }));

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
      
      {/* Productivity Overview Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Productivity Overview (Last 7 Days)</h2>
        {chartData.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="todos" 
                  stroke="#14B8A6" 
                  activeDot={{ r: 8 }} 
                  name="Completed Todos"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="habits" 
                  stroke="#8B5CF6" 
                  name="Completed Habits"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-lg">
            <p className="text-gray-500 dark:text-gray-400">No productivity data available</p>
          </div>
        )}
      </div>
      
      {/* Recent Activity */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <p className="text-gray-500 dark:text-gray-400 text-center py-8">No recent activity</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;