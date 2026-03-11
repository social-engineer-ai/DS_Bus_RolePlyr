'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, ScenarioResponse, PersonaListItem, RubricListItem } from '@/lib/api';

export default function ScenarioDetailPage() {
  const params = useParams();
  const router = useRouter();
  const scenarioId = params.id as string;

  const [scenario, setScenario] = useState<ScenarioResponse | null>(null);
  const [personas, setPersonas] = useState<PersonaListItem[]>([]);
  const [rubrics, setRubrics] = useState<RubricListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    persona_id: '',
    rubric_id: '',
    is_practice: true,
    max_turns: 15,
  });

  useEffect(() => { loadData(); }, [scenarioId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [scenarioData, personaData, rubricData] = await Promise.all([
        api.getScenarioAdmin(scenarioId),
        api.listPersonas(),
        api.listRubrics(),
      ]);
      setScenario(scenarioData);
      setPersonas(personaData);
      setRubrics(rubricData);
      setFormData({
        name: scenarioData.name,
        description: scenarioData.description || '',
        persona_id: scenarioData.persona_id,
        rubric_id: scenarioData.rubric_id,
        is_practice: scenarioData.is_practice,
        max_turns: scenarioData.max_turns,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenario');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await api.updateScenario(scenarioId, {
        name: formData.name,
        description: formData.description || undefined,
        persona_id: formData.persona_id,
        rubric_id: formData.rubric_id,
        is_practice: formData.is_practice,
        max_turns: formData.max_turns,
      });
      setEditing(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update scenario');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Delete this scenario? This cannot be undone.')) return;
    try {
      await api.deleteScenario(scenarioId);
      router.push('/instructor/scenarios');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scenario');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading scenario...</p>
      </div>
    );
  }

  if (!scenario) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-red-600">{error || 'Scenario not found'}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Scenario Detail</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor/scenarios" className="text-indigo-200 hover:text-white">Back to Scenarios</a>
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
              <h2 className="text-2xl font-bold text-gray-900">{scenario.name}</h2>
              <div className="flex items-center gap-3 mt-1">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  scenario.is_practice ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                }`}>
                  {scenario.is_practice ? 'Practice' : 'Graded'}
                </span>
                <span className="text-gray-500 text-sm">Max {scenario.max_turns} turns</span>
              </div>
            </div>
            {!editing && (
              <div className="flex gap-2">
                <button
                  onClick={() => setEditing(true)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700"
                >
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  className="bg-red-50 text-red-600 px-4 py-2 rounded-lg font-medium hover:bg-red-100"
                >
                  Delete
                </button>
              </div>
            )}
          </div>

          {editing ? (
            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Persona</label>
                <select
                  value={formData.persona_id}
                  onChange={(e) => setFormData({ ...formData, persona_id: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                >
                  {personas.map((p) => (
                    <option key={p.id} value={p.id}>{p.name} - {p.title}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rubric</label>
                <select
                  value={formData.rubric_id}
                  onChange={(e) => setFormData({ ...formData, rubric_id: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                >
                  {rubrics.map((r) => (
                    <option key={r.id} value={r.id}>{r.name} ({r.total_points} pts)</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select
                    value={formData.is_practice ? 'practice' : 'graded'}
                    onChange={(e) => setFormData({ ...formData, is_practice: e.target.value === 'practice' })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="practice">Practice</option>
                    <option value="graded">Graded</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Turns</label>
                  <input
                    type="number"
                    value={formData.max_turns}
                    onChange={(e) => setFormData({ ...formData, max_turns: parseInt(e.target.value) || 15 })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    min={1}
                    max={50}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button type="button" onClick={() => { setEditing(false); loadData(); }} className="px-4 py-2 text-gray-600 hover:text-gray-800">
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
              {scenario.description && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Description</h3>
                  <p className="text-gray-800">{scenario.description}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Persona</h3>
                  <p className="text-gray-800">{scenario.persona_name}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Rubric</h3>
                  <p className="text-gray-800">{scenario.rubric_name}</p>
                </div>
              </div>
              <div className="pt-4 border-t text-sm text-gray-500">
                Created: {new Date(scenario.created_at).toLocaleDateString()}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
