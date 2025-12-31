'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, Scenario } from '@/lib/api';
import { ScenarioCard } from '@/components/ScenarioCard';

export default function ScenariosPage() {
  const router = useRouter();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [context, setContext] = useState('');
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      const data = await api.getScenarios();
      setScenarios(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectScenario = (scenario: Scenario) => {
    setSelectedScenario(scenario);
    setContext('');
  };

  const handleStartConversation = async () => {
    if (!selectedScenario || !context.trim()) return;

    try {
      setStarting(true);
      const conversation = await api.startConversation(
        selectedScenario.id,
        context.trim()
      );
      router.push(`/chat/${conversation.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start conversation');
      setStarting(false);
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
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">StakeholderSim</h1>
          <nav className="flex gap-4">
            <a href="/" className="text-gray-600 hover:text-gray-800">Home</a>
            <a href="/history" className="text-gray-600 hover:text-gray-800">History</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-red-700">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 text-sm underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Modal for starting conversation */}
        {selectedScenario && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-bold">{selectedScenario.name}</h2>
                    <p className="text-gray-600">
                      {selectedScenario.persona_name} - {selectedScenario.persona_title}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedScenario(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {selectedScenario.persona_background && (
                  <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-medium text-gray-700 mb-2">
                      About {selectedScenario.persona_name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {selectedScenario.persona_background}
                    </p>
                  </div>
                )}

                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Describe Your Model/Project
                  </label>
                  <p className="text-sm text-gray-500 mb-2">
                    Before starting, briefly describe what you're presenting. This helps
                    {selectedScenario.persona_name} ask relevant questions.
                  </p>
                  <textarea
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="Example: I built a resume screening model that predicts which candidates should advance to recruiter review. It has 85% precision and 78% recall on our test set..."
                    className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none"
                  />
                  <p className="mt-1 text-xs text-gray-400">
                    Minimum 10 characters required
                  </p>
                </div>

                <div className="p-4 bg-yellow-50 rounded-lg mb-6">
                  <h4 className="font-medium text-yellow-800 mb-1">Tips</h4>
                  <ul className="text-sm text-yellow-700 list-disc list-inside">
                    <li>Translate technical metrics to business value</li>
                    <li>Be prepared for pushback on ROI and risks</li>
                    <li>This stakeholder appreciates honesty about limitations</li>
                  </ul>
                </div>

                <div className="flex justify-end gap-3">
                  <button
                    onClick={() => setSelectedScenario(null)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleStartConversation}
                    disabled={context.trim().length < 10 || starting}
                    className="px-6 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    {starting ? 'Starting...' : 'Start Conversation'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Practice Scenarios
          </h2>
          <p className="text-gray-600">
            Select a stakeholder persona to practice your presentation skills.
          </p>
        </div>

        {scenarios.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No scenarios available.</p>
            <p className="text-sm text-gray-500 mt-2">
              Run `make seed` to add default scenarios.
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarios.map((scenario) => (
              <ScenarioCard
                key={scenario.id}
                scenario={scenario}
                onSelect={handleSelectScenario}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
