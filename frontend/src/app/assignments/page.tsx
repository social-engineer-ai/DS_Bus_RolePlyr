'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, StudentAssignment, Scenario } from '@/lib/api';

export default function StudentAssignmentsPage() {
  const router = useRouter();
  const [assignments, setAssignments] = useState<StudentAssignment[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingAssignment, setStartingAssignment] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [assignmentData, scenarioData] = await Promise.all([
        api.getStudentAssignments(),
        api.getScenarios(),
      ]);
      setAssignments(assignmentData);
      setScenarios(scenarioData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assignments');
    } finally {
      setLoading(false);
    }
  };

  const startAssignment = async (assignment: StudentAssignment) => {
    try {
      setStartingAssignment(assignment.id);
      // Find the matching scenario
      const scenario = scenarios.find(s => s.name === assignment.scenario_name);
      if (!scenario) {
        throw new Error('Scenario not found');
      }

      const conversation = await api.startConversation(
        scenario.id,
        `Assignment: ${assignment.title}`,
        assignment.id
      );
      router.push(`/chat/${conversation.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start assignment');
      setStartingAssignment(null);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const isOverdue = (dueDate: string | null) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading assignments...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="text-blue-500 hover:text-blue-700"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">Assignments</h1>
          <nav className="flex gap-4">
            <a href="/dashboard" className="text-gray-600 hover:text-gray-800">Dashboard</a>
            <a href="/scenarios" className="text-gray-600 hover:text-gray-800">Practice</a>
            <a href="/history" className="text-gray-600 hover:text-gray-800">History</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {assignments.length === 0 ? (
          <div className="bg-white rounded-lg p-8 shadow text-center">
            <p className="text-gray-500 mb-4">No assignments available at this time.</p>
            <a
              href="/scenarios"
              className="text-blue-500 hover:text-blue-700"
            >
              Try practice scenarios instead
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {assignments.map((assignment) => (
              <div
                key={assignment.id}
                className="bg-white rounded-lg shadow overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h2 className="text-lg font-semibold text-gray-800">
                        {assignment.title}
                      </h2>
                      <p className="text-sm text-gray-500 mt-1">
                        {assignment.persona_name} - {assignment.persona_title}
                      </p>
                      {assignment.instructions && (
                        <p className="text-gray-600 mt-2">{assignment.instructions}</p>
                      )}
                    </div>
                    <div className="text-right ml-4">
                      <p className={`text-sm font-medium ${
                        isOverdue(assignment.due_date) && assignment.can_attempt
                          ? 'text-red-600'
                          : 'text-gray-500'
                      }`}>
                        {formatDate(assignment.due_date)}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center gap-6 text-sm">
                      <span className="text-gray-500">
                        Attempts: {assignment.attempts_used} / {assignment.max_attempts}
                      </span>
                      {assignment.best_score !== null && (
                        <span className={`font-medium ${
                          assignment.best_score >= 80 ? 'text-green-600' :
                          assignment.best_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          Best: {Math.round(assignment.best_score)}/100
                        </span>
                      )}
                    </div>

                    <div>
                      {assignment.can_attempt ? (
                        <button
                          onClick={() => startAssignment(assignment)}
                          disabled={startingAssignment === assignment.id}
                          className="bg-blue-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {startingAssignment === assignment.id
                            ? 'Starting...'
                            : assignment.attempts_used > 0
                            ? 'Retry'
                            : 'Start'}
                        </button>
                      ) : (
                        <span className={`px-4 py-2 rounded-lg text-sm font-medium ${
                          isOverdue(assignment.due_date)
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {isOverdue(assignment.due_date)
                            ? 'Past Due'
                            : 'Max Attempts Reached'}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Progress bar for attempts */}
                <div className="h-1 bg-gray-100">
                  <div
                    className={`h-full ${
                      assignment.best_score !== null && assignment.best_score >= 80
                        ? 'bg-green-500'
                        : assignment.attempts_used >= assignment.max_attempts
                        ? 'bg-gray-400'
                        : 'bg-blue-500'
                    }`}
                    style={{ width: `${(assignment.attempts_used / assignment.max_attempts) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
