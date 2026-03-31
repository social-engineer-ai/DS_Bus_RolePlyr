'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, StudentQuiz, AttemptResponse } from '@/lib/api';

export default function QuizzesPage() {
  const router = useRouter();
  const [quizzes, setQuizzes] = useState<StudentQuiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedQuiz, setExpandedQuiz] = useState<string | null>(null);
  const [attempts, setAttempts] = useState<Record<string, AttemptResponse[]>>({});
  const [loadingAttempts, setLoadingAttempts] = useState<string | null>(null);

  useEffect(() => {
    loadQuizzes();
  }, []);

  const loadQuizzes = async () => {
    try {
      setLoading(true);
      const data = await api.getStudentQuizzes();
      setQuizzes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quizzes');
    } finally {
      setLoading(false);
    }
  };

  const toggleAttempts = async (quizId: string) => {
    if (expandedQuiz === quizId) {
      setExpandedQuiz(null);
      return;
    }
    setExpandedQuiz(quizId);
    if (!attempts[quizId]) {
      try {
        setLoadingAttempts(quizId);
        const data = await api.getMyAttempts(quizId);
        setAttempts(prev => ({ ...prev, [quizId]: data }));
      } catch {
        // silently fail
      } finally {
        setLoadingAttempts(null);
      }
    }
  };

  const viewAttemptResults = (quizId: string, attempt: AttemptResponse) => {
    sessionStorage.setItem(`quiz_result_${quizId}`, JSON.stringify(attempt));
    router.push(`/quizzes/${quizId}/results`);
  };

  const formatDate = (dateString: string) => {
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading quizzes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-800">Quizzes</h1>
            <p className="text-sm text-gray-500">Test your understanding</p>
          </div>
          <a href="/" className="text-blue-500 hover:text-blue-700 text-sm">Back to Home</a>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {quizzes.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No quizzes available yet.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {quizzes.map((quiz) => (
              <div key={quiz.id} className="bg-white rounded-lg shadow">
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h2 className="text-lg font-semibold text-gray-800">{quiz.title}</h2>
                      {quiz.description && (
                        <p className="text-gray-600 text-sm mt-1">{quiz.description}</p>
                      )}
                      <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-500">
                        <span>{quiz.question_count} questions</span>
                        <span>{quiz.max_score} points</span>
                        {quiz.time_limit_minutes && (
                          <span>{quiz.time_limit_minutes} min time limit</span>
                        )}
                        {quiz.due_date && (
                          <span className={isOverdue(quiz.due_date) ? 'text-red-600 font-medium' : ''}>
                            Due: {formatDate(quiz.due_date)}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 mt-3">
                        <span className="text-sm text-gray-500">
                          Attempts: {quiz.attempts_used} / {quiz.max_attempts}
                        </span>
                        {quiz.best_score !== null && (
                          <span className={`text-sm font-medium ${
                            (quiz.best_score / quiz.max_score) * 100 >= 80 ? 'text-green-600' :
                            (quiz.best_score / quiz.max_score) * 100 >= 60 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            Best: {quiz.best_score}/{quiz.max_score} ({Math.round((quiz.best_score / quiz.max_score) * 100)}%)
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 flex flex-col gap-2">
                      <button
                        onClick={() => router.push(`/quizzes/${quiz.id}`)}
                        disabled={!quiz.can_attempt}
                        className={`px-4 py-2 rounded-lg font-medium ${
                          quiz.can_attempt
                            ? 'bg-blue-500 text-white hover:bg-blue-600'
                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {quiz.attempts_used > 0 && quiz.can_attempt ? 'Retry' : quiz.can_attempt ? 'Take Quiz' : 'Max Reached'}
                      </button>
                      {quiz.attempts_used > 0 && (
                        <button
                          onClick={() => toggleAttempts(quiz.id)}
                          className="text-sm text-blue-500 hover:text-blue-700"
                        >
                          {expandedQuiz === quiz.id ? 'Hide' : 'View'} Past Attempts
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Past attempts dropdown */}
                {expandedQuiz === quiz.id && (
                  <div className="border-t px-6 py-4 bg-gray-50">
                    {loadingAttempts === quiz.id ? (
                      <p className="text-sm text-gray-500">Loading attempts...</p>
                    ) : attempts[quiz.id]?.length ? (
                      <div className="space-y-2">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">Past Attempts</h3>
                        {attempts[quiz.id].map((attempt, i) => {
                          const pct = attempt.max_score > 0
                            ? Math.round((attempt.score / attempt.max_score) * 100)
                            : 0;
                          return (
                            <div
                              key={attempt.id}
                              className="flex items-center justify-between bg-white rounded p-3 border cursor-pointer hover:bg-blue-50"
                              onClick={() => viewAttemptResults(quiz.id, attempt)}
                            >
                              <div>
                                <span className="text-sm font-medium text-gray-700">
                                  Attempt {attempts[quiz.id].length - i}
                                </span>
                                <span className="text-xs text-gray-400 ml-3">
                                  {formatDate(attempt.submitted_at)}
                                </span>
                              </div>
                              <div className="flex items-center gap-3">
                                <span className={`text-sm font-medium ${
                                  pct >= 80 ? 'text-green-600' :
                                  pct >= 60 ? 'text-yellow-600' : 'text-red-600'
                                }`}>
                                  {attempt.score}/{attempt.max_score} ({pct}%)
                                </span>
                                <span className="text-xs text-blue-500">View</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">No submitted attempts yet.</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
