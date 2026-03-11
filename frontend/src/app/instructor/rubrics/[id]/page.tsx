'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, RubricResponse, CriterionSchema } from '@/lib/api';

const DEFAULT_COURSE_ID = '55555555-5555-5555-5555-555555555555';

export default function RubricDetailPage() {
  const params = useParams();
  const router = useRouter();
  const rubricId = params.id as string;

  const [rubric, setRubric] = useState<RubricResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const [name, setName] = useState('');
  const [criteria, setCriteria] = useState<CriterionSchema[]>([]);

  useEffect(() => { loadRubric(); }, [rubricId]);

  const loadRubric = async () => {
    try {
      setLoading(true);
      const data = await api.getRubric(rubricId);
      setRubric(data);
      setName(data.name);
      setCriteria(data.criteria);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load rubric');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await api.updateRubric(rubricId, { name, criteria, course_id: DEFAULT_COURSE_ID });
      setEditing(false);
      await loadRubric();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update rubric');
    } finally {
      setSaving(false);
    }
  };

  const updateCriterion = (index: number, field: keyof CriterionSchema, value: string | number | Record<string, string>) => {
    const updated = [...criteria];
    (updated[index] as Record<string, unknown>)[field] = value;
    setCriteria(updated);
  };

  const addCriterion = () => {
    setCriteria([...criteria, {
      name: '',
      display_name: '',
      description: '',
      max_points: 20,
      scoring_guide: {},
    }]);
  };

  const removeCriterion = (index: number) => {
    setCriteria(criteria.filter((_, i) => i !== index));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading rubric...</p>
      </div>
    );
  }

  if (!rubric) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-red-600">{error || 'Rubric not found'}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Rubric Detail</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor/rubrics" className="text-indigo-200 hover:text-white">Back to Rubrics</a>
            <a href="/instructor" className="text-indigo-200 hover:text-white">Dashboard</a>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
            <button onClick={() => setError(null)} className="ml-4 text-red-500 hover:text-red-700">Dismiss</button>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{rubric.name}</h2>
              <p className="text-gray-600">{rubric.total_points} total points | {rubric.criteria.length} criteria</p>
            </div>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700"
              >
                Edit
              </button>
            )}
          </div>

          {editing ? (
            <form onSubmit={handleSave} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rubric Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-800">Criteria</h3>
                  <button type="button" onClick={addCriterion} className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                    + Add Criterion
                  </button>
                </div>

                {criteria.map((criterion, i) => (
                  <div key={i} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-500">Criterion {i + 1}</span>
                      <button type="button" onClick={() => removeCriterion(i)} className="text-red-500 hover:text-red-700 text-sm">
                        Remove
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Display Name</label>
                        <input
                          type="text"
                          value={criterion.display_name}
                          onChange={(e) => updateCriterion(i, 'display_name', e.target.value)}
                          className="w-full border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Max Points</label>
                        <input
                          type="number"
                          value={criterion.max_points}
                          onChange={(e) => updateCriterion(i, 'max_points', parseInt(e.target.value) || 0)}
                          className="w-full border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          min={1}
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Description</label>
                      <textarea
                        value={criterion.description}
                        onChange={(e) => updateCriterion(i, 'description', e.target.value)}
                        className="w-full border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        rows={2}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button type="button" onClick={() => { setEditing(false); loadRubric(); }} className="px-4 py-2 text-gray-600 hover:text-gray-800">
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              {rubric.criteria.map((criterion, i) => (
                <div key={i} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{criterion.display_name}</h3>
                    <span className="bg-indigo-50 text-indigo-700 px-2 py-1 rounded text-sm font-medium">
                      {criterion.max_points} pts
                    </span>
                  </div>
                  {criterion.description && (
                    <p className="text-sm text-gray-600 mb-3">{criterion.description}</p>
                  )}
                  {criterion.scoring_guide && Object.keys(criterion.scoring_guide).length > 0 && (
                    <div className="bg-gray-50 rounded p-3">
                      <p className="text-xs font-medium text-gray-500 mb-2">Scoring Guide</p>
                      <div className="space-y-1">
                        {Object.entries(criterion.scoring_guide)
                          .sort(([a], [b]) => Number(b) - Number(a))
                          .map(([score, desc]) => (
                            <div key={score} className="flex gap-2 text-sm">
                              <span className="font-medium text-gray-700 w-8">{score}:</span>
                              <span className="text-gray-600">{desc}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div className="pt-4 border-t text-sm text-gray-500">
                Created: {new Date(rubric.created_at).toLocaleDateString()}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
