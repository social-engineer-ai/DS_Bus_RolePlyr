'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, ScenarioListItem, ScenarioCreate, PersonaListItem, RubricListItem } from '@/lib/api';

const DEFAULT_COURSE_ID = '55555555-5555-5555-5555-555555555555';

export default function ScenariosPage() {
  const router = useRouter();
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
  const [personas, setPersonas] = useState<PersonaListItem[]>([]);
  const [rubrics, setRubrics] = useState<RubricListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    persona_id: '',
    rubric_id: '',
    is_practice: true,
    max_turns: 15,
  });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [scenarioData, personaData, rubricData] = await Promise.all([
        api.listScenariosAdmin(),
        api.listPersonas(),
        api.listRubrics(),
      ]);
      setScenarios(scenarioData);
      setPersonas(personaData);
      setRubrics(rubricData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.persona_id || !formData.rubric_id) return;

    try {
      setCreating(true);
      const data: ScenarioCreate = {
        course_id: DEFAULT_COURSE_ID,
        name: formData.name,
        description: formData.description || undefined,
        persona_id: formData.persona_id,
        rubric_id: formData.rubric_id,
        is_practice: formData.is_practice,
        max_turns: formData.max_turns,
      };

      await api.createScenario(data);
      setShowCreateModal(false);
      setFormData({ name: '', description: '', persona_id: '', rubric_id: '', is_practice: true, max_turns: 15 });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create scenario');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (scenarioId: string) => {
    if (!confirm('Delete this scenario? This cannot be undone.')) return;
    try {
      await api.deleteScenario(scenarioId);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete scenario');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading scenarios...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Scenario Management</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor" className="text-indigo-200 hover:text-white">Dashboard</a>
            <a href="/instructor/personas" className="text-indigo-200 hover:text-white">Personas</a>
            <a href="/instructor/rubrics" className="text-indigo-200 hover:text-white">Rubrics</a>
            <a href="/instructor/scenarios" className="text-white font-medium">Scenarios</a>
            <a href="/instructor/assignments" className="text-indigo-200 hover:text-white">Assignments</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">All Scenarios</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700"
          >
            Create Scenario
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Persona</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rubric</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max Turns</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {scenarios.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    No scenarios yet. Click "Create Scenario" to get started.
                  </td>
                </tr>
              ) : (
                scenarios.map((scenario) => (
                  <tr key={scenario.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{scenario.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{scenario.persona_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{scenario.rubric_name}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        scenario.is_practice ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                      }`}>
                        {scenario.is_practice ? 'Practice' : 'Graded'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{scenario.max_turns}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(scenario.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => router.push(`/instructor/scenarios/${scenario.id}`)}
                          className="text-indigo-600 hover:text-indigo-800 text-sm"
                        >
                          View / Edit
                        </button>
                        <button
                          onClick={() => handleDelete(scenario.id)}
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

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">Create Scenario</h2>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="e.g., CEO Budget Presentation"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    rows={2}
                    placeholder="Brief description of the scenario..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Persona *</label>
                  <select
                    value={formData.persona_id}
                    onChange={(e) => setFormData({ ...formData, persona_id: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  >
                    <option value="">Select a persona...</option>
                    {personas.map((p) => (
                      <option key={p.id} value={p.id}>{p.name} - {p.title}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rubric *</label>
                  <select
                    value={formData.rubric_id}
                    onChange={(e) => setFormData({ ...formData, rubric_id: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  >
                    <option value="">Select a rubric...</option>
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
                  <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating || !formData.name || !formData.persona_id || !formData.rubric_id}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {creating ? 'Creating...' : 'Create Scenario'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
