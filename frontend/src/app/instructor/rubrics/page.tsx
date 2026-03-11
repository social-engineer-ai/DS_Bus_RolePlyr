'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, RubricListItem } from '@/lib/api';

export default function RubricsPage() {
  const router = useRouter();
  const [rubrics, setRubrics] = useState<RubricListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.listRubrics();
      setRubrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load rubrics');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (rubricId: string) => {
    if (!confirm('Delete this rubric? This cannot be undone.')) return;
    try {
      await api.deleteRubric(rubricId);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete rubric');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading rubrics...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Rubric Management</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor" className="text-indigo-200 hover:text-white">Dashboard</a>
            <a href="/instructor/personas" className="text-indigo-200 hover:text-white">Personas</a>
            <a href="/instructor/rubrics" className="text-white font-medium">Rubrics</a>
            <a href="/instructor/scenarios" className="text-indigo-200 hover:text-white">Scenarios</a>
            <a href="/instructor/assignments" className="text-indigo-200 hover:text-white">Assignments</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">All Rubrics</h2>
          <button
            onClick={() => router.push('/instructor/rubrics/create')}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700"
          >
            Build Rubric with AI
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
            <button onClick={() => setError(null)} className="ml-4 text-red-500 hover:text-red-700">Dismiss</button>
          </div>
        )}

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Criteria</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Points</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {rubrics.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No rubrics yet. Click "Build Rubric with AI" to create one.
                  </td>
                </tr>
              ) : (
                rubrics.map((rubric) => (
                  <tr key={rubric.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{rubric.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{rubric.criteria_count} criteria</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{rubric.total_points} pts</td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(rubric.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => router.push(`/instructor/rubrics/${rubric.id}`)}
                          className="text-indigo-600 hover:text-indigo-800 text-sm"
                        >
                          View / Edit
                        </button>
                        <button
                          onClick={() => handleDelete(rubric.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Delete
                        </button>
                      </div>
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
