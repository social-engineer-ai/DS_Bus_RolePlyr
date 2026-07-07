'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AttemptResponse } from '@/lib/api';

export default function QuizResultsPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = params.id as string;

  const [result, setResult] = useState<AttemptResponse | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem(`quiz_result_${quizId}`);
    if (stored) {
      setResult(JSON.parse(stored));
    }
  }, [quizId]);

  if (!result) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">No results found.</p>
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

  const percentage = result.max_score > 0 ? Math.round((result.score / result.max_score) * 100) : 0;
  const scoreColor = percentage >= 80 ? 'text-green-600' : percentage >= 60 ? 'text-yellow-600' : 'text-red-600';
  const scoreBg = percentage >= 80 ? 'bg-green-50 border-green-200' : percentage >= 60 ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200';
  const reviewCount = result.answers.filter(a => a.needs_review).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">Quiz Results</h1>
          <button
            onClick={() => router.push('/quizzes')}
            className="text-blue-500 hover:text-blue-700 text-sm"
          >
            Back to Quizzes
          </button>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Score Summary */}
        <div className={`rounded-lg border p-6 mb-8 text-center ${scoreBg}`}>
          <p className={`text-4xl font-bold ${scoreColor}`}>
            {result.score}/{result.max_score}
          </p>
          <p className={`text-lg font-medium ${scoreColor} mt-1`}>
            {percentage}%
          </p>
          <p className="text-gray-500 text-sm mt-2">
            {result.answers.filter(a => a.is_correct).length} of {result.answers.length} auto-matched
            {reviewCount > 0 && (
              <span className="text-yellow-600"> &middot; {reviewCount} pending instructor review</span>
            )}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Submitted: {new Date(result.submitted_at).toLocaleString()}
          </p>
        </div>

        {/* Per-question breakdown */}
        <div className="space-y-4">
          {result.answers.map((answer, index) => (
            <div
              key={answer.question_id}
              className={`bg-white rounded-lg shadow p-6 border-l-4 ${
                answer.needs_review
                  ? 'border-l-yellow-400'
                  : answer.is_correct
                  ? 'border-l-green-400'
                  : 'border-l-red-400'
              }`}
            >
              <div className="flex items-start gap-3">
                <span className={`text-sm font-medium px-2 py-1 rounded ${
                  answer.needs_review
                    ? 'bg-yellow-100 text-yellow-700'
                    : answer.is_correct
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}>
                  Q{index + 1}
                </span>
                <div className="flex-1">
                  <p className="text-gray-800 font-medium">{answer.question_text}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {answer.question_type === 'mcq' ? 'Multiple Choice' :
                     answer.question_type === 'true_false' ? 'True/False' :
                     answer.question_type === 'self_authored' ? 'Self-Authored Q&A' : 'Short Answer'}
                    {' '}&middot; {answer.points_awarded}/{answer.points_possible} pts
                  </p>

                  <div className="mt-3 space-y-2">
                    {answer.question_type === 'self_authored' ? (
                      <>
                        {(() => {
                          let parsed = { question: '', answer: '' };
                          try { parsed = JSON.parse(answer.student_answer || '{}'); } catch {}
                          return (
                            <>
                              <div>
                                <span className="text-xs font-medium text-gray-500 uppercase">Your Question:</span>
                                <p className="text-sm mt-0.5 text-gray-800 bg-gray-50 rounded p-2">
                                  {parsed.question || '(no question written)'}
                                </p>
                              </div>
                              <div>
                                <span className="text-xs font-medium text-gray-500 uppercase">Your Answer:</span>
                                <p className="text-sm mt-0.5 text-gray-800 bg-gray-50 rounded p-2">
                                  {parsed.answer || '(no answer written)'}
                                </p>
                              </div>
                            </>
                          );
                        })()}
                        {answer.needs_review && (
                          <p className="text-sm text-yellow-600 font-medium mt-2">
                            Pending instructor review
                          </p>
                        )}
                      </>
                    ) : (
                      <>
                        <div>
                          <span className="text-xs font-medium text-gray-500 uppercase">Your Answer:</span>
                          <p className={`text-sm mt-0.5 ${
                            answer.is_correct ? 'text-green-700' : answer.needs_review ? 'text-gray-700' : 'text-red-700'
                          }`}>
                            {answer.student_answer || '(no answer)'}
                          </p>
                        </div>
                        {answer.correct_answer && (
                          <div>
                            <span className="text-xs font-medium text-gray-500 uppercase">Reference Answer:</span>
                            <p className="text-sm mt-0.5 text-green-700">{answer.correct_answer}</p>
                          </div>
                        )}
                        {answer.needs_review && (
                          <p className="text-sm text-yellow-600 font-medium mt-2">
                            Pending instructor review
                          </p>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center py-8">
          <button
            onClick={() => router.push('/quizzes')}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
          >
            Back to Quizzes
          </button>
        </div>
      </main>
    </div>
  );
}
