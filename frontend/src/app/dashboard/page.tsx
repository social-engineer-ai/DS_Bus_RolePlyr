'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, StudentDashboard } from '@/lib/api';

function StatCard({ label, value, suffix, color }: {
  label: string;
  value: number | string | null;
  suffix?: string;
  color?: string;
}) {
  return (
    <div className="bg-white rounded-lg p-4 shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`text-2xl font-bold ${color || 'text-gray-800'}`}>
        {value !== null ? value : '-'}
        {suffix && value !== null && <span className="text-sm font-normal text-gray-500">{suffix}</span>}
      </p>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<StudentDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await api.getStudentDashboard();
      setDashboard(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-red-600">{error || 'Failed to load dashboard'}</p>
      </div>
    );
  }

  const { stats, recent_conversations, progress_history } = dashboard;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">My Dashboard</h1>
          <nav className="flex gap-4">
            <a href="/assignments" className="text-blue-500 hover:text-blue-700">Assignments</a>
            <a href="/scenarios" className="text-gray-600 hover:text-gray-800">Practice</a>
            <a href="/history" className="text-gray-600 hover:text-gray-800">History</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total Sessions"
            value={stats.total_conversations}
          />
          <StatCard
            label="Average Score"
            value={stats.average_score}
            suffix="/100"
            color={stats.average_score && stats.average_score >= 70 ? 'text-green-600' : 'text-yellow-600'}
          />
          <StatCard
            label="Best Score"
            value={stats.best_score}
            suffix="/100"
            color="text-green-600"
          />
          <StatCard
            label="Improvement"
            value={stats.total_improvement !== null ? `+${stats.total_improvement}` : null}
            suffix=" pts"
            color="text-blue-600"
          />
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Progress Chart */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">Score Progress</h2>
            {progress_history.length > 0 ? (
              <div className="space-y-3">
                {progress_history.slice(-10).map((point, index) => (
                  <div key={point.conversation_id} className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 w-16">
                      {formatDate(point.date)}
                    </span>
                    <div className="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          point.score >= 80 ? 'bg-green-500' :
                          point.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${point.score}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-12 text-right">
                      {Math.round(point.score)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Complete some practice sessions to see your progress!
              </p>
            )}
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
            {recent_conversations.length > 0 ? (
              <div className="space-y-3">
                {recent_conversations.map((conv) => (
                  <div
                    key={conv.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                    onClick={() => router.push(
                      conv.status === 'completed' ? `/grade/${conv.id}` : `/chat/${conv.id}`
                    )}
                  >
                    <div>
                      <p className="font-medium text-gray-800">{conv.persona_name}</p>
                      <p className="text-xs text-gray-500">
                        {formatDate(conv.started_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      {conv.score !== null ? (
                        <p className={`font-bold ${
                          conv.score >= 80 ? 'text-green-600' :
                          conv.score >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {Math.round(conv.score)}/100
                        </p>
                      ) : (
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          conv.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {conv.status.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No recent activity. Start practicing!
              </p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 flex justify-center gap-4">
          <button
            onClick={() => router.push('/scenarios')}
            className="bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600"
          >
            Start New Practice
          </button>
          <button
            onClick={() => router.push('/history')}
            className="bg-white text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 border"
          >
            View All History
          </button>
        </div>
      </main>
    </div>
  );
}
