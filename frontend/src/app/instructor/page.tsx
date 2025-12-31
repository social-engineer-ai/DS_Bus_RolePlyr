'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, InstructorDashboard } from '@/lib/api';

function StatCard({ label, value, subtitle }: {
  label: string;
  value: number | string | null;
  subtitle?: string;
}) {
  return (
    <div className="bg-white rounded-lg p-4 shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-800">
        {value !== null ? value : '-'}
      </p>
      {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
    </div>
  );
}

export default function InstructorDashboardPage() {
  const router = useRouter();
  const [dashboard, setDashboard] = useState<InstructorDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Set user to instructor for this page
    api.setUser('instructor');
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await api.getInstructorDashboard();
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
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading instructor dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500">
            Make sure you're accessing as an instructor (use ?user_key=instructor)
          </p>
        </div>
      </div>
    );
  }

  if (!dashboard) return null;

  const { class_stats, students, grades_needing_review, recent_activity } = dashboard;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Instructor Dashboard</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor/assignments" className="text-indigo-200 hover:text-white">Assignments</a>
            <a href="/" className="text-indigo-200 hover:text-white">Home</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Class Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <StatCard
            label="Total Students"
            value={class_stats.total_students}
          />
          <StatCard
            label="Active (7 days)"
            value={class_stats.active_students}
          />
          <StatCard
            label="Total Sessions"
            value={class_stats.total_conversations}
          />
          <StatCard
            label="Graded"
            value={class_stats.total_graded}
          />
          <StatCard
            label="Class Average"
            value={class_stats.average_score ? `${Math.round(class_stats.average_score)}` : null}
            subtitle="/100"
          />
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Score Distribution */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">Score Distribution</h2>
            <div className="space-y-2">
              {Object.entries(class_stats.score_distribution).map(([range, count]) => (
                <div key={range} className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 w-20">{range}</span>
                  <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        range.startsWith('90') ? 'bg-green-500' :
                        range.startsWith('80') ? 'bg-green-400' :
                        range.startsWith('70') ? 'bg-yellow-400' :
                        range.startsWith('60') ? 'bg-orange-400' : 'bg-red-400'
                      }`}
                      style={{ width: `${(count / Math.max(...Object.values(class_stats.score_distribution), 1)) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-8 text-right">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Common Struggles */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">Common Struggles</h2>
            {class_stats.common_struggles.length > 0 ? (
              <ul className="space-y-2">
                {class_stats.common_struggles.map((struggle, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <span className="text-orange-500">!</span>
                    {struggle}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-sm">No common struggles identified yet.</p>
            )}
          </div>

          {/* Grades Needing Review */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h2 className="text-lg font-semibold mb-4">Needs Review</h2>
            {grades_needing_review.length > 0 ? (
              <div className="space-y-2">
                {grades_needing_review.slice(0, 5).map((grade) => (
                  <div
                    key={grade.id}
                    className="p-2 bg-yellow-50 rounded cursor-pointer hover:bg-yellow-100"
                    onClick={() => router.push(`/grade/${grade.conversation_id}`)}
                  >
                    <p className="text-sm font-medium">{grade.student_name}</p>
                    <p className="text-xs text-gray-500">
                      {grade.persona_name} - {Math.round(grade.score)}/100
                    </p>
                    <p className="text-xs text-yellow-600">
                      Confidence: {Math.round(grade.ai_confidence * 100)}%
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No grades need review.</p>
            )}
          </div>
        </div>

        {/* Students Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">Students</h2>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Sessions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Avg Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Last Active
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {students.map((student) => (
                <tr key={student.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <p className="font-medium text-gray-900">{student.name}</p>
                    <p className="text-xs text-gray-500">{student.email}</p>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {student.total_conversations}
                  </td>
                  <td className="px-6 py-4">
                    {student.average_score !== null ? (
                      <span className={`font-medium ${
                        student.average_score >= 80 ? 'text-green-600' :
                        student.average_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {Math.round(student.average_score)}
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {student.last_active ? formatDate(student.last_active) : 'Never'}
                  </td>
                  <td className="px-6 py-4">
                    {student.needs_attention ? (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
                        Needs Attention
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">
                        On Track
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">Recent Activity</h2>
          </div>
          <div className="divide-y">
            {recent_activity.map((activity) => (
              <div
                key={activity.id}
                className="px-6 py-3 flex items-center justify-between hover:bg-gray-50 cursor-pointer"
                onClick={() => router.push(`/chat/${activity.id}`)}
              >
                <div>
                  <p className="font-medium text-gray-800">{activity.persona_name}</p>
                  <p className="text-xs text-gray-500">{formatDate(activity.started_at)}</p>
                </div>
                <div className="flex items-center gap-3">
                  {activity.score !== null && (
                    <span className="font-medium text-gray-700">
                      {Math.round(activity.score)}/100
                    </span>
                  )}
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    activity.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : activity.status === 'in_progress'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {activity.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
