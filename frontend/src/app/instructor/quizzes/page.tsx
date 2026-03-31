'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, QuizListItem, QuestionCreate } from '@/lib/api';

const DEFAULT_COURSE_ID = '55555555-5555-5555-5555-555555555555';

interface QuestionForm {
  question_type: string;
  question_text: string;
  options: string[];
  correct_answer: string;
  acceptable_answers: string;
  points: number;
}

const emptyQuestion = (): QuestionForm => ({
  question_type: 'mcq',
  question_text: '',
  options: ['', '', '', ''],
  correct_answer: '',
  acceptable_answers: '',
  points: 1,
});

export default function InstructorQuizzesPage() {
  const router = useRouter();
  const [quizzes, setQuizzes] = useState<QuizListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [maxAttempts, setMaxAttempts] = useState(1);
  const [dueDate, setDueDate] = useState('');
  const [timeLimitMinutes, setTimeLimitMinutes] = useState('');
  const [showAnswers, setShowAnswers] = useState(true);
  const [questions, setQuestions] = useState<QuestionForm[]>([emptyQuestion()]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadQuizzes();
  }, []);

  const loadQuizzes = async () => {
    try {
      setLoading(true);
      const data = await api.listQuizzesAdmin();
      setQuizzes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quizzes');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const addQuestion = () => {
    setQuestions(prev => [...prev, emptyQuestion()]);
  };

  const removeQuestion = (index: number) => {
    if (questions.length <= 1) return;
    setQuestions(prev => prev.filter((_, i) => i !== index));
  };

  const updateQuestion = (index: number, field: string, value: any) => {
    setQuestions(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };

      // Reset options when changing question type
      if (field === 'question_type') {
        if (value === 'true_false') {
          updated[index].options = ['True', 'False'];
          updated[index].correct_answer = '';
        } else if (value === 'mcq') {
          updated[index].options = ['', '', '', ''];
          updated[index].correct_answer = '';
        } else {
          updated[index].options = [];
          updated[index].correct_answer = '';
        }
      }

      return updated;
    });
  };

  const updateOption = (qIndex: number, optIndex: number, value: string) => {
    setQuestions(prev => {
      const updated = [...prev];
      const newOptions = [...updated[qIndex].options];
      newOptions[optIndex] = value;
      updated[qIndex] = { ...updated[qIndex], options: newOptions };
      return updated;
    });
  };

  const handleCreate = async () => {
    if (!title.trim()) return;

    try {
      setCreating(true);
      const questionData: QuestionCreate[] = questions.map((q, i) => ({
        question_type: q.question_type,
        question_text: q.question_text,
        options: q.question_type !== 'short_answer' ? q.options.filter(o => o.trim()) : undefined,
        correct_answer: q.correct_answer,
        acceptable_answers: q.question_type === 'short_answer' && q.acceptable_answers.trim()
          ? q.acceptable_answers.split(',').map(a => a.trim())
          : undefined,
        points: q.points,
        order_index: i,
      }));

      await api.createQuiz({
        title: title.trim(),
        description: description.trim() || undefined,
        course_id: DEFAULT_COURSE_ID,
        max_attempts: maxAttempts,
        due_date: dueDate || undefined,
        time_limit_minutes: timeLimitMinutes ? parseInt(timeLimitMinutes) : undefined,
        show_answers_after_submit: showAnswers,
        questions: questionData,
      });

      setShowCreateModal(false);
      resetForm();
      loadQuizzes();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create quiz');
    } finally {
      setCreating(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setMaxAttempts(1);
    setDueDate('');
    setTimeLimitMinutes('');
    setShowAnswers(true);
    setQuestions([emptyQuestion()]);
  };

  const handleDelete = async (quizId: string) => {
    if (!window.confirm('Deactivate this quiz?')) return;
    try {
      await api.deleteQuiz(quizId);
      loadQuizzes();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete quiz');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading quizzes...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Quiz Management</h1>
            <p className="text-sm text-indigo-200">StakeholderSim</p>
          </div>
          <nav className="flex gap-4">
            <a href="/instructor/personas" className="text-indigo-200 hover:text-white">Personas</a>
            <a href="/instructor/rubrics" className="text-indigo-200 hover:text-white">Rubrics</a>
            <a href="/instructor/scenarios" className="text-indigo-200 hover:text-white">Scenarios</a>
            <a href="/instructor/assignments" className="text-indigo-200 hover:text-white">Assignments</a>
            <a href="/instructor/quizzes" className="text-white font-medium">Quizzes</a>
            <a href="/instructor" className="text-indigo-200 hover:text-white">Dashboard</a>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg">{error}</div>
        )}

        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">All Quizzes</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-indigo-500 text-white px-4 py-2 rounded-lg hover:bg-indigo-600"
          >
            Create Quiz
          </button>
        </div>

        {/* Quizzes Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Questions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attempts</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {quizzes.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    No quizzes yet. Create your first quiz!
                  </td>
                </tr>
              ) : (
                quizzes.map((quiz) => (
                  <tr key={quiz.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{quiz.title}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{quiz.question_count}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{quiz.total_points}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {quiz.due_date ? formatDate(quiz.due_date) : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{quiz.total_attempts}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        quiz.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-500'
                      }`}>
                        {quiz.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <button
                        onClick={() => router.push(`/instructor/quizzes?results=${quiz.id}`)}
                        className="text-indigo-600 hover:text-indigo-800"
                      >
                        Results
                      </button>
                      <button
                        onClick={() => handleDelete(quiz.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>

      {/* Create Quiz Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center z-50 overflow-y-auto py-8">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl mx-4">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-800">Create Quiz</h2>
                <button
                  onClick={() => { setShowCreateModal(false); resetForm(); }}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  &times;
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
              {/* Quiz metadata */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                  <input
                    type="text"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    className="w-full border rounded-lg px-3 py-2"
                    placeholder="Quiz title"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    className="w-full border rounded-lg px-3 py-2"
                    rows={2}
                    placeholder="Optional description"
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Max Attempts</label>
                    <input
                      type="number"
                      min={1}
                      max={10}
                      value={maxAttempts}
                      onChange={e => setMaxAttempts(parseInt(e.target.value) || 1)}
                      className="w-full border rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Time Limit (min)</label>
                    <input
                      type="number"
                      min={1}
                      value={timeLimitMinutes}
                      onChange={e => setTimeLimitMinutes(e.target.value)}
                      className="w-full border rounded-lg px-3 py-2"
                      placeholder="No limit"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                    <input
                      type="datetime-local"
                      value={dueDate}
                      onChange={e => setDueDate(e.target.value)}
                      className="w-full border rounded-lg px-3 py-2"
                    />
                  </div>
                </div>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={showAnswers}
                    onChange={e => setShowAnswers(e.target.checked)}
                  />
                  Show correct answers after submission
                </label>
              </div>

              {/* Questions */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-800">Questions</h3>
                  <button
                    onClick={addQuestion}
                    className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded hover:bg-gray-200"
                  >
                    + Add Question
                  </button>
                </div>

                <div className="space-y-4">
                  {questions.map((q, qIndex) => (
                    <div key={qIndex} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-gray-600">Question {qIndex + 1}</span>
                        <div className="flex items-center gap-3">
                          <select
                            value={q.question_type}
                            onChange={e => updateQuestion(qIndex, 'question_type', e.target.value)}
                            className="text-sm border rounded px-2 py-1"
                          >
                            <option value="mcq">Multiple Choice</option>
                            <option value="true_false">True/False</option>
                            <option value="short_answer">Short Answer</option>
                          </select>
                          <input
                            type="number"
                            min={1}
                            value={q.points}
                            onChange={e => updateQuestion(qIndex, 'points', parseInt(e.target.value) || 1)}
                            className="w-16 text-sm border rounded px-2 py-1"
                          />
                          <span className="text-xs text-gray-500">pts</span>
                          {questions.length > 1 && (
                            <button
                              onClick={() => removeQuestion(qIndex)}
                              className="text-red-500 hover:text-red-700 text-sm"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                      </div>

                      <textarea
                        value={q.question_text}
                        onChange={e => updateQuestion(qIndex, 'question_text', e.target.value)}
                        className="w-full border rounded px-3 py-2 mb-3 text-sm"
                        rows={2}
                        placeholder="Question text"
                      />

                      {/* MCQ options */}
                      {q.question_type === 'mcq' && (
                        <div className="space-y-2">
                          {q.options.map((opt, optIndex) => (
                            <div key={optIndex} className="flex items-center gap-2">
                              <input
                                type="radio"
                                name={`correct-${qIndex}`}
                                checked={q.correct_answer === opt && opt !== ''}
                                onChange={() => updateQuestion(qIndex, 'correct_answer', opt)}
                              />
                              <input
                                type="text"
                                value={opt}
                                onChange={e => {
                                  if (q.correct_answer === opt) {
                                    updateQuestion(qIndex, 'correct_answer', e.target.value);
                                  }
                                  updateOption(qIndex, optIndex, e.target.value);
                                }}
                                className="flex-1 border rounded px-2 py-1 text-sm"
                                placeholder={`Option ${optIndex + 1}`}
                              />
                            </div>
                          ))}
                          <p className="text-xs text-gray-400">Select the radio button next to the correct answer</p>
                        </div>
                      )}

                      {/* True/False */}
                      {q.question_type === 'true_false' && (
                        <div className="space-y-2">
                          {['True', 'False'].map(opt => (
                            <label key={opt} className="flex items-center gap-2 text-sm">
                              <input
                                type="radio"
                                name={`correct-${qIndex}`}
                                checked={q.correct_answer === opt}
                                onChange={() => updateQuestion(qIndex, 'correct_answer', opt)}
                              />
                              {opt}
                            </label>
                          ))}
                        </div>
                      )}

                      {/* Short Answer */}
                      {q.question_type === 'short_answer' && (
                        <div className="space-y-2">
                          <input
                            type="text"
                            value={q.correct_answer}
                            onChange={e => updateQuestion(qIndex, 'correct_answer', e.target.value)}
                            className="w-full border rounded px-2 py-1 text-sm"
                            placeholder="Expected answer"
                          />
                          <input
                            type="text"
                            value={q.acceptable_answers}
                            onChange={e => updateQuestion(qIndex, 'acceptable_answers', e.target.value)}
                            className="w-full border rounded px-2 py-1 text-sm"
                            placeholder="Acceptable keywords (comma-separated)"
                          />
                          <p className="text-xs text-gray-400">Keywords for auto-grading. Answers without a keyword match get flagged for review.</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="p-6 border-t flex justify-end gap-3">
              <button
                onClick={() => { setShowCreateModal(false); resetForm(); }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={creating || !title.trim() || questions.some(q => !q.question_text.trim() || !q.correct_answer.trim())}
                className={`px-4 py-2 rounded-lg font-medium ${
                  creating || !title.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-indigo-500 text-white hover:bg-indigo-600'
                }`}
              >
                {creating ? 'Creating...' : 'Create Quiz'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
