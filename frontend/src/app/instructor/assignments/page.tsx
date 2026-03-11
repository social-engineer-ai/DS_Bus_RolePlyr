'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, AssignmentListItem, Scenario, AssignmentCreate, PersonaListItem, RubricListItem, ScenarioCreate } from '@/lib/api';

// Hardcoded course ID from seed data
const DEFAULT_COURSE_ID = '55555555-5555-5555-5555-555555555555';

export default function InstructorAssignmentsPage() {
  const router = useRouter();
  const [assignments, setAssignments] = useState<AssignmentListItem[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [personas, setPersonas] = useState<PersonaListItem[]>([]);
  const [rubrics, setRubrics] = useState<RubricListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [showScenarioModal, setShowScenarioModal] = useState(false);
  const [creatingScenario, setCreatingScenario] = useState(false);
  const [scenarioForm, setScenarioForm] = useState({
    name: '',
    description: '',
    persona_id: '',
    rubric_id: '',
    is_practice: false,
    max_turns: 15,
  });

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    instructions: '',
    scenario_id: '',
    due_date: '',
    max_attempts: 1,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [assignmentData, scenarioData, personaData, rubricData] = await Promise.all([
        api.listAssignments(),
        api.getScenarios(),
        api.listPersonas(),
        api.listRubrics(),
      ]);
      setAssignments(assignmentData);
      setScenarios(scenarioData);
      setPersonas(personaData);
      setRubrics(rubricData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.scenario_id) return;

    try {
      setCreating(true);
      const data: AssignmentCreate = {
        title: formData.title,
        instructions: formData.instructions || undefined,
        scenario_id: formData.scenario_id,
        course_id: DEFAULT_COURSE_ID,
        max_attempts: formData.max_attempts,
      };

      if (formData.due_date) {
        data.due_date = new Date(formData.due_date).toISOString();
      }

      await api.createAssignment(data);
      setShowCreateModal(false);
      setFormData({
        title: '',
        instructions: '',
        scenario_id: '',
        due_date: '',
        max_attempts: 1,
      });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create assignment');
    } finally {
      setCreating(false);
    }
  };

  const toggleAssignmentStatus = async (assignment: AssignmentListItem) => {
    try {
      await api.updateAssignment(assignment.id, {
        is_active: !assignment.is_active,
      });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update assignment');
    }
  };

  const handleCreateScenario = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scenarioForm.name || !scenarioForm.persona_id || !scenarioForm.rubric_id) return;

    try {
      setCreatingScenario(true);
      const data: ScenarioCreate = {
        course_id: DEFAULT_COURSE_ID,
        name: scenarioForm.name,
        description: scenarioForm.description || undefined,
        persona_id: scenarioForm.persona_id,
        rubric_id: scenarioForm.rubric_id,
        is_practice: scenarioForm.is_practice,
        max_turns: scenarioForm.max_turns,
      };
      const created = await api.createScenario(data);
      setShowScenarioModal(false);
      setScenarioForm({ name: '', description: '', persona_id: '', rubric_id: '', is_practice: false, max_turns: 15 });
      // Refresh scenarios and auto-select the new one
      const updatedScenarios = await api.getScenarios();
      setScenarios(updatedScenarios);
      setFormData({ ...formData, scenario_id: created.id });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create scenario');
    } finally {
      setCreatingScenario(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading assignments...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Assignment Management</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor" className="text-indigo-200 hover:text-white">Dashboard</a>
            <a href="/instructor/personas" className="text-indigo-200 hover:text-white">Personas</a>
            <a href="/instructor/rubrics" className="text-indigo-200 hover:text-white">Rubrics</a>
            <a href="/instructor/scenarios" className="text-indigo-200 hover:text-white">Scenarios</a>
            <a href="/instructor/assignments" className="text-white font-medium">Assignments</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Action Bar */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">All Assignments</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700"
          >
            Create Assignment
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-500 hover:text-red-700"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Assignments Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Assignment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Scenario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Due Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Attempts
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Submissions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {assignments.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    No assignments created yet. Click "Create Assignment" to get started.
                  </td>
                </tr>
              ) : (
                assignments.map((assignment) => (
                  <tr key={assignment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{assignment.title}</p>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-900">{assignment.scenario_name}</p>
                      <p className="text-xs text-gray-500">{assignment.persona_name}</p>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {formatDate(assignment.due_date)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {assignment.max_attempts}
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-900">
                        {assignment.total_submissions} total
                      </p>
                      <p className="text-xs text-gray-500">
                        {assignment.graded_submissions} graded
                      </p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        assignment.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {assignment.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => router.push(`/instructor/assignments/${assignment.id}`)}
                          className="text-indigo-600 hover:text-indigo-800 text-sm"
                        >
                          View
                        </button>
                        <button
                          onClick={() => toggleAssignmentStatus(assignment)}
                          className="text-gray-600 hover:text-gray-800 text-sm"
                        >
                          {assignment.is_active ? 'Deactivate' : 'Activate'}
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

      {/* Inline Create Scenario Modal */}
      {showScenarioModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60]">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">Create New Scenario</h2>
              <form onSubmit={handleCreateScenario} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                  <input
                    type="text"
                    value={scenarioForm.name}
                    onChange={(e) => setScenarioForm({ ...scenarioForm, name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="e.g., CEO Budget Presentation"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={scenarioForm.description}
                    onChange={(e) => setScenarioForm({ ...scenarioForm, description: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    rows={2}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Persona *</label>
                  <select
                    value={scenarioForm.persona_id}
                    onChange={(e) => setScenarioForm({ ...scenarioForm, persona_id: e.target.value })}
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
                    value={scenarioForm.rubric_id}
                    onChange={(e) => setScenarioForm({ ...scenarioForm, rubric_id: e.target.value })}
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
                      value={scenarioForm.is_practice ? 'practice' : 'graded'}
                      onChange={(e) => setScenarioForm({ ...scenarioForm, is_practice: e.target.value === 'practice' })}
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
                      value={scenarioForm.max_turns}
                      onChange={(e) => setScenarioForm({ ...scenarioForm, max_turns: parseInt(e.target.value) || 15 })}
                      className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      min={1}
                      max={50}
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setShowScenarioModal(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creatingScenario || !scenarioForm.name || !scenarioForm.persona_id || !scenarioForm.rubric_id}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {creatingScenario ? 'Creating...' : 'Create Scenario'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Create Assignment Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">Create Assignment</h2>
              <form onSubmit={handleCreateAssignment} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="e.g., Week 3: CEO Presentation"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scenario *
                  </label>
                  <select
                    value={formData.scenario_id}
                    onChange={(e) => {
                      if (e.target.value === '__create_new__') {
                        setShowScenarioModal(true);
                      } else {
                        setFormData({ ...formData, scenario_id: e.target.value });
                      }
                    }}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  >
                    <option value="">Select a scenario...</option>
                    {scenarios.map((scenario) => (
                      <option key={scenario.id} value={scenario.id}>
                        {scenario.name} - {scenario.persona_name}
                      </option>
                    ))}
                    <option value="__create_new__">+ Create New Scenario</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Instructions
                  </label>
                  <textarea
                    value={formData.instructions}
                    onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    rows={3}
                    placeholder="Optional instructions for students..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Due Date
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.due_date}
                      onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                      className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Attempts
                    </label>
                    <select
                      value={formData.max_attempts}
                      onChange={(e) => setFormData({ ...formData, max_attempts: parseInt(e.target.value) })}
                      className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {[1, 2, 3, 4, 5].map((n) => (
                        <option key={n} value={n}>
                          {n} {n === 1 ? 'attempt' : 'attempts'}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating || !formData.title || !formData.scenario_id}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {creating ? 'Creating...' : 'Create Assignment'}
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
