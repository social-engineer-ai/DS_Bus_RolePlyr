'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, PersonaResponse } from '@/lib/api';

export default function PersonaDetailPage() {
  const params = useParams();
  const router = useRouter();
  const personaId = params.id as string;

  const [persona, setPersona] = useState<PersonaResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    title: '',
    background: '',
    personality: '',
    concerns: '',
    required_questions: '',
  });

  useEffect(() => { loadPersona(); }, [personaId]);

  const loadPersona = async () => {
    try {
      setLoading(true);
      const data = await api.getPersona(personaId);
      setPersona(data);
      setFormData({
        name: data.name,
        title: data.title,
        background: data.background || '',
        personality: data.personality || '',
        concerns: (data.concerns || []).join(', '),
        required_questions: (data.required_questions || []).join(', '),
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load persona');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await api.updatePersona(personaId, {
        name: formData.name,
        title: formData.title,
        background: formData.background || undefined,
        personality: formData.personality || undefined,
        concerns: formData.concerns ? formData.concerns.split(',').map(s => s.trim()).filter(Boolean) : undefined,
        required_questions: formData.required_questions ? formData.required_questions.split(',').map(s => s.trim()).filter(Boolean) : undefined,
      });
      setEditing(false);
      await loadPersona();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update persona');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Deactivate this persona? It will no longer appear in lists.')) return;
    try {
      await api.deletePersona(personaId);
      router.push('/instructor/personas');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deactivate persona');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading persona...</p>
      </div>
    );
  }

  if (!persona) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-red-600">{error || 'Persona not found'}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Persona Detail</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor/personas" className="text-indigo-200 hover:text-white">Back to Personas</a>
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
              <h2 className="text-2xl font-bold text-gray-900">{persona.name}</h2>
              <p className="text-gray-600">{persona.title}</p>
            </div>
            <div className="flex gap-2">
              {!editing && (
                <>
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
                    Deactivate
                  </button>
                </>
              )}
            </div>
          </div>

          {editing ? (
            <form onSubmit={handleSave} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Background</label>
                <textarea
                  value={formData.background}
                  onChange={(e) => setFormData({ ...formData, background: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={4}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Personality</label>
                <textarea
                  value={formData.personality}
                  onChange={(e) => setFormData({ ...formData, personality: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Concerns (comma-separated)</label>
                <input
                  type="text"
                  value={formData.concerns}
                  onChange={(e) => setFormData({ ...formData, concerns: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Required Questions (comma-separated)</label>
                <input
                  type="text"
                  value={formData.required_questions}
                  onChange={(e) => setFormData({ ...formData, required_questions: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button type="button" onClick={() => setEditing(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">
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
            <div className="space-y-6">
              {persona.background && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Background</h3>
                  <p className="text-gray-800 whitespace-pre-wrap">{persona.background}</p>
                </div>
              )}
              {persona.personality && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Personality</h3>
                  <p className="text-gray-800 whitespace-pre-wrap">{persona.personality}</p>
                </div>
              )}
              {persona.concerns && persona.concerns.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Concerns</h3>
                  <div className="flex flex-wrap gap-2">
                    {persona.concerns.map((c, i) => (
                      <span key={i} className="bg-orange-50 text-orange-700 px-3 py-1 rounded-full text-sm">{c}</span>
                    ))}
                  </div>
                </div>
              )}
              {persona.required_questions && persona.required_questions.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Required Questions</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {persona.required_questions.map((q, i) => (
                      <li key={i} className="text-gray-800">{q}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="pt-4 border-t text-sm text-gray-500">
                Status: {persona.is_active ? 'Active' : 'Inactive'} | Created: {new Date(persona.created_at).toLocaleDateString()}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
