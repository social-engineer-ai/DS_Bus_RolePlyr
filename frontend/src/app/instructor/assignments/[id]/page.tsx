'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, AssignmentResponse, AssignmentSubmission } from '@/lib/api';

export default function AssignmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const assignmentId = params.id as string;

  const [assignment, setAssignment] = useState<AssignmentResponse | null>(null);
  const [submissions, setSubmissions] = useState<AssignmentSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  // Edit form state
  const [editData, setEditData] = useState({
    title: '',
    instructions: '',
    due_date: '',
    max_attempts: 1,
    is_active: true,
  });

  useEffect(() => {
    api.setUser('instructor');
    loadData();
  }, [assignmentId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [assignmentData, submissionData] = await Promise.all([
        api.getAssignment(assignmentId),
        api.getAssignmentSubmissions(assignmentId),
      ]);
      setAssignment(assignmentData);
      setSubmissions(submissionData);
      setEditData({
        title: assignmentData.title,
        instructions: assignmentData.instructions || '',
        due_date: assignmentData.due_date
          ? new Date(assignmentData.due_date).toISOString().slice(0, 16)
          : '',
        max_attempts: assignmentData.max_attempts,
        is_active: assignmentData.is_active,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assignment');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await api.updateAssignment(assignmentId, {
        title: editData.title,
        instructions: editData.instructions || undefined,
        due_date: editData.due_date ? new Date(editData.due_date).toISOString() : undefined,
        max_attempts: editData.max_attempts,
        is_active: editData.is_active,
      });
      setEditing(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update assignment');
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading assignment...</p>
      </div>
    );
  }

  if (error || !assignment) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Assignment not found'}</p>
          <button
            onClick={() => router.push('/instructor/assignments')}
            className="text-indigo-600 hover:text-indigo-800"
          >
            Back to Assignments
          </button>
        </div>
      </div>
    );
  }

  const completedSubmissions = submissions.filter(s => s.status === 'completed');
  const avgScore = completedSubmissions.length > 0
    ? completedSubmissions.reduce((sum, s) => sum + (s.score || 0), 0) / completedSubmissions.length
    : null;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <button
              onClick={() => router.push('/instructor/assignments')}
              className="text-indigo-200 hover:text-white text-sm mb-1 flex items-center gap-1"
            >
              Back to Assignments
            </button>
            <h1 className="text-xl font-bold">{assignment.title}</h1>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor" className="text-indigo-200 hover:text-white">Dashboard</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Assignment Details */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="md:col-span-2 bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Assignment Details</h2>
              {!editing && (
                <button
                  onClick={() => setEditing(true)}
                  className="text-indigo-600 hover:text-indigo-800 text-sm"
                >
                  Edit
                </button>
              )}
            </div>

            {editing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={editData.title}
                    onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Instructions
                  </label>
                  <textarea
                    value={editData.instructions}
                    onChange={(e) => setEditData({ ...editData, instructions: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Due Date
                    </label>
                    <input
                      type="datetime-local"
                      value={editData.due_date}
                      onChange={(e) => setEditData({ ...editData, due_date: e.target.value })}
                      className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Attempts
                    </label>
                    <select
                      value={editData.max_attempts}
                      onChange={(e) => setEditData({ ...editData, max_attempts: parseInt(e.target.value) })}
                      className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {[1, 2, 3, 4, 5].map((n) => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={editData.is_active}
                    onChange={(e) => setEditData({ ...editData, is_active: e.target.checked })}
                    className="rounded"
                  />
                  <label htmlFor="is_active" className="text-sm text-gray-700">
                    Active (visible to students)
                  </label>
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    onClick={() => setEditing(false)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Scenario</p>
                  <p className="font-medium">{assignment.scenario_name}</p>
                  <p className="text-sm text-gray-600">{assignment.persona_name}</p>
                </div>
                {assignment.instructions && (
                  <div>
                    <p className="text-sm text-gray-500">Instructions</p>
                    <p className="text-gray-700">{assignment.instructions}</p>
                  </div>
                )}
                <div className="grid grid-cols-3 gap-4 pt-2">
                  <div>
                    <p className="text-sm text-gray-500">Due Date</p>
                    <p className="font-medium">{formatDate(assignment.due_date)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Max Attempts</p>
                    <p className="font-medium">{assignment.max_attempts}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      assignment.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {assignment.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Stats */}
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-500">Total Submissions</p>
              <p className="text-3xl font-bold text-gray-800">{submissions.length}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-3xl font-bold text-green-600">{completedSubmissions.length}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm text-gray-500">Average Score</p>
              <p className={`text-3xl font-bold ${
                avgScore !== null
                  ? avgScore >= 80 ? 'text-green-600' :
                    avgScore >= 60 ? 'text-yellow-600' : 'text-red-600'
                  : 'text-gray-400'
              }`}>
                {avgScore !== null ? Math.round(avgScore) : '-'}
              </p>
            </div>
          </div>
        </div>

        {/* Submissions Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">Submissions</h2>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Started
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Completed
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {submissions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    No submissions yet.
                  </td>
                </tr>
              ) : (
                submissions.map((submission) => (
                  <tr key={submission.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {submission.student_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {formatDate(submission.started_at)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {formatDate(submission.completed_at)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        submission.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : submission.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {submission.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {submission.score !== null ? (
                        <span className={`font-medium ${
                          submission.score >= 80 ? 'text-green-600' :
                          submission.score >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {Math.round(submission.score)}/100
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => router.push(
                          submission.status === 'completed'
                            ? `/grade/${submission.conversation_id}`
                            : `/chat/${submission.conversation_id}`
                        )}
                        className="text-indigo-600 hover:text-indigo-800 text-sm"
                      >
                        {submission.status === 'completed' ? 'View Grade' : 'View Chat'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
