'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, StudentQuestionView, AnswerSubmit } from '@/lib/api';
import { useScreenLock } from '@/components/useScreenLock';
import { ViolationToast } from '@/components/ViolationToast';
import { ViolationModal } from '@/components/ViolationModal';

export default function TakeQuizPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = params.id as string;

  const [questions, setQuestions] = useState<StudentQuestionView[]>([]);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState(false);

  // Auto-submit on 4th violation
  const handleTerminate = useCallback(async () => {
    if (!attemptId) return;
    try {
      const answerList: AnswerSubmit[] = questions
        .filter(q => answers[q.id])
        .map(q => ({ question_id: q.id, student_answer: answers[q.id] }));
      const result = await api.submitQuizAttempt(attemptId, { answers: answerList });
      sessionStorage.setItem(`quiz_result_${quizId}`, JSON.stringify(result));
    } catch {
      // best effort
    }
  }, [attemptId, questions, answers, quizId]);

  const {
    violationCount,
    showToast,
    setShowToast,
    showModal,
    modalViolationNumber,
    handleModalAcknowledge,
    terminated,
    isPaused,
  } = useScreenLock({ enabled: started, onTerminate: handleTerminate });

  useEffect(() => {
    loadQuiz();
  }, [quizId]);

  const loadQuiz = async () => {
    try {
      setLoading(true);
      const [questionsData, attemptData] = await Promise.all([
        api.takeQuiz(quizId),
        api.startQuizAttempt(quizId),
      ]);
      setQuestions(questionsData);
      setAttemptId(attemptData.attempt_id);
      setStarted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quiz');
    } finally {
      setLoading(false);
    }
  };

  const setAnswer = useCallback((questionId: string, answer: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  }, []);

  const handleSubmit = async () => {
    if (!attemptId || terminated) return;

    const unanswered = questions.filter(q => !answers[q.id]);
    if (unanswered.length > 0) {
      const proceed = window.confirm(
        `You have ${unanswered.length} unanswered question(s). Submit anyway?`
      );
      if (!proceed) return;
    }

    try {
      setSubmitting(true);
      const answerList: AnswerSubmit[] = questions
        .filter(q => answers[q.id])
        .map(q => ({
          question_id: q.id,
          student_answer: answers[q.id],
        }));

      const result = await api.submitQuizAttempt(attemptId, { answers: answerList });
      sessionStorage.setItem(`quiz_result_${quizId}`, JSON.stringify(result));
      router.push(`/quizzes/${quizId}/results`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit quiz');
      setSubmitting(false);
    }
  };

  const answeredCount = questions.filter(q => answers[q.id]).length;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading quiz...</p>
      </div>
    );
  }

  if (error && !started) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/quizzes')}
            className="text-blue-500 hover:text-blue-700"
          >
            Back to Quizzes
          </button>
        </div>
      </div>
    );
  }

  // Terminated screen
  if (terminated) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/80">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-8">
          <div className="text-center">
            <div className="text-5xl mb-4 text-red-500">X</div>
            <h2 className="text-2xl font-bold text-red-800 mb-2">Session Terminated</h2>
            <p className="text-gray-600 mb-6">
              Your quiz was automatically submitted because you left this page too many times.
              Your answers have been saved as-is.
            </p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => router.push(`/quizzes/${quizId}/results`)}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-600"
              >
                View Results
              </button>
              <button
                onClick={() => router.push('/quizzes')}
                className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg font-semibold hover:bg-gray-300"
              >
                Back to Quizzes
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Violation overlays */}
      <ViolationToast show={showToast} onDismiss={() => setShowToast(false)} />
      <ViolationModal
        show={showModal}
        violationNumber={modalViolationNumber}
        onAcknowledge={handleModalAcknowledge}
      />

      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-800">Quiz</h1>
            <p className="text-sm text-gray-500">
              {answeredCount} answered — pick any 5 of {questions.length}
            </p>
          </div>
          <div className="flex items-center gap-4">
            {violationCount > 0 && (
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                violationCount >= 3 ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {violationCount} violation{violationCount !== 1 ? 's' : ''}
              </span>
            )}
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className={`px-6 py-2 rounded-lg font-medium ${
                submitting
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-500 text-white hover:bg-green-600'
              }`}
            >
              {submitting ? 'Submitting...' : 'Submit Quiz'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            {error}
          </div>
        )}

        {questions.map((question, index) => (
          <div key={question.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start gap-3 mb-4">
              <span className="bg-blue-100 text-blue-700 text-sm font-medium px-2 py-1 rounded">
                Q{index + 1}
              </span>
              <div className="flex-1">
                <p className="text-gray-800 font-medium">{question.question_text}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {question.points} point{question.points !== 1 ? 's' : ''} &middot;{' '}
                  {question.question_type === 'mcq' ? 'Multiple Choice' :
                   question.question_type === 'true_false' ? 'True/False' : 'Short Answer'}
                </p>
              </div>
            </div>

            {/* MCQ or True/False */}
            {(question.question_type === 'mcq' || question.question_type === 'true_false') && question.options && (
              <div className="space-y-2 ml-9">
                {question.options.map((option, optIndex) => (
                  <label
                    key={optIndex}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      answers[question.id] === option
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={option}
                      checked={answers[question.id] === option}
                      onChange={() => setAnswer(question.id, option)}
                      className="text-blue-500"
                    />
                    <span className="text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Short Answer */}
            {question.question_type === 'short_answer' && (
              <div className="ml-9">
                <textarea
                  value={answers[question.id] || ''}
                  onChange={(e) => setAnswer(question.id, e.target.value)}
                  placeholder="Type your answer..."
                  rows={3}
                  className="w-full border border-gray-200 rounded-lg p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            )}
          </div>
        ))}

        <div className="text-center pt-4 pb-8">
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className={`px-8 py-3 rounded-lg font-medium text-lg ${
              submitting
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            {submitting ? 'Submitting...' : 'Submit Quiz'}
          </button>
        </div>
      </main>
    </div>
  );
}
