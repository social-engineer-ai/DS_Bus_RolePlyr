'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, AttemptListItem, AttemptResponse, AnswerResult } from '@/lib/api';

export default function InstructorQuizResultsPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = params.id as string;

  const [attempts, setAttempts] = useState<AttemptListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bulkGrading, setBulkGrading] = useState(false);
  const [bulkSummary, setBulkSummary] = useState<string | null>(null);

  const [openAttemptId, setOpenAttemptId] = useState<string | null>(null);
  const [attemptDetail, setAttemptDetail] = useState<AttemptResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [gradingAttempt, setGradingAttempt] = useState(false);

  useEffect(() => {
    void loadAttempts();
  }, [quizId]);

  const loadAttempts = async () => {
    try {
      setLoading(true);
      const data = await api.getQuizResults(quizId);
      setAttempts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load attempts');
    } finally {
      setLoading(false);
    }
  };

  const loadDetail = async (attemptId: string) => {
    try {
      setDetailLoading(true);
      const data = await api.getAttemptDetail(attemptId);
      setAttemptDetail(data);
      setOpenAttemptId(attemptId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load attempt detail');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleBulkLLMGrade = async () => {
    if (!window.confirm('Grade every submitted attempt with the LLM? This may take a minute.')) return;
    try {
      setBulkGrading(true);
      setBulkSummary(null);
      const s = await api.gradeAllAttemptsWithLLM(quizId);
      setBulkSummary(`Graded ${s.graded} answer(s) across ${s.attempts} attempt(s). Skipped ${s.skipped}. Failed ${s.failed}.`);
      await loadAttempts();
      if (openAttemptId) await loadDetail(openAttemptId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'LLM bulk grading failed');
    } finally {
      setBulkGrading(false);
    }
  };

  const handleGradeOneWithLLM = async (attemptId: string, regrade: boolean = false) => {
    try {
      setGradingAttempt(true);
      await api.gradeAttemptWithLLM(attemptId, regrade);
      await loadDetail(attemptId);
      await loadAttempts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'LLM grading failed');
    } finally {
      setGradingAttempt(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading attempts...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <button onClick={() => router.push('/instructor/quizzes')} className="text-indigo-200 hover:text-white text-sm mb-1">&larr; All quizzes</button>
            <h1 className="text-xl font-bold">Quiz Attempts</h1>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleBulkLLMGrade}
              disabled={bulkGrading || attempts.length === 0}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                bulkGrading || attempts.length === 0
                  ? 'bg-indigo-400 text-indigo-100 cursor-not-allowed'
                  : 'bg-white text-indigo-700 hover:bg-indigo-50'
              }`}
            >
              {bulkGrading ? 'Grading with LLM...' : 'Grade all with LLM'}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {error && <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg">{error}</div>}
        {bulkSummary && <div className="mb-4 p-3 bg-green-50 text-green-800 rounded-lg text-sm">{bulkSummary}</div>}

        <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Submitted</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Needs Review</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {attempts.length === 0 ? (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No attempts yet.</td></tr>
              ) : (
                attempts.map(a => (
                  <tr key={a.id} className={openAttemptId === a.id ? 'bg-indigo-50' : 'hover:bg-gray-50'}>
                    <td className="px-6 py-4 font-medium text-gray-900">{a.student_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {a.is_submitted ? `${a.score ?? 0} / ${a.max_score ?? 0}` : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {a.submitted_at ? new Date(a.submitted_at).toLocaleString() : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {a.needs_review ? (
                        <span className="inline-flex px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 text-xs">Needs review</span>
                      ) : (
                        <span className="inline-flex px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs">Confirmed</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <button onClick={() => loadDetail(a.id)} className="text-indigo-600 hover:text-indigo-800">
                        {openAttemptId === a.id ? 'Refresh' : 'Review'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {openAttemptId && (
          <AttemptDetailPanel
            detail={attemptDetail}
            loading={detailLoading}
            gradingAttempt={gradingAttempt}
            onGradeWithLLM={() => handleGradeOneWithLLM(openAttemptId, false)}
            onReGradeWithLLM={() => handleGradeOneWithLLM(openAttemptId, true)}
            onClose={() => { setOpenAttemptId(null); setAttemptDetail(null); }}
            onAnswerUpdated={() => loadDetail(openAttemptId)}
          />
        )}
      </main>
    </div>
  );
}

function AttemptDetailPanel({
  detail,
  loading,
  gradingAttempt,
  onGradeWithLLM,
  onReGradeWithLLM,
  onClose,
  onAnswerUpdated,
}: {
  detail: AttemptResponse | null;
  loading: boolean;
  gradingAttempt: boolean;
  onGradeWithLLM: () => void;
  onReGradeWithLLM: () => void;
  onClose: () => void;
  onAnswerUpdated: () => void;
}) {
  if (loading && !detail) {
    return <div className="bg-white rounded-lg shadow p-6 text-gray-500">Loading...</div>;
  }
  if (!detail) return null;

  const hasUngraded = detail.answers.some(a => (a.graded_by ?? 'none') === 'none');

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-gray-800">Attempt detail</h3>
          <p className="text-sm text-gray-500">
            Score: {detail.score} / {detail.max_score} · Submitted {new Date(detail.submitted_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={hasUngraded ? onGradeWithLLM : onReGradeWithLLM}
            disabled={gradingAttempt}
            className={`px-3 py-1.5 text-sm rounded-lg ${
              gradingAttempt ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-indigo-500 text-white hover:bg-indigo-600'
            }`}
          >
            {gradingAttempt ? 'Grading...' : hasUngraded ? 'Grade with LLM' : 'Re-grade with LLM'}
          </button>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-sm">Close</button>
        </div>
      </div>

      <div className="divide-y">
        {detail.answers.map((a, idx) => (
          <AnswerReviewRow key={a.question_id} index={idx + 1} answer={a} onUpdated={onAnswerUpdated} />
        ))}
      </div>
    </div>
  );
}

function AnswerReviewRow({
  index,
  answer,
  onUpdated,
}: {
  index: number;
  answer: AnswerResult;
  onUpdated: () => void;
}) {
  const [points, setPoints] = useState<number>(answer.points_awarded);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const gradedBy = answer.graded_by ?? 'none';

  useEffect(() => {
    setPoints(answer.points_awarded);
  }, [answer.points_awarded]);

  const handleConfirm = async () => {
    if (!answer.id) {
      setSaveError('Missing answer ID.');
      return;
    }
    try {
      setSaving(true);
      setSaveError(null);
      const clamped = Math.max(0, Math.min(points, answer.points_possible));
      const isCorrect = clamped >= answer.points_possible - 1e-6;
      await api.gradeAnswer(answer.id, { is_correct: isCorrect, points_awarded: clamped });
      onUpdated();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const badge =
    gradedBy === 'llm' ? { bg: 'bg-blue-100', fg: 'text-blue-700', label: 'LLM graded' } :
    gradedBy === 'instructor' ? { bg: 'bg-green-100', fg: 'text-green-700', label: 'Instructor graded' } :
    { bg: 'bg-gray-100', fg: 'text-gray-600', label: 'Not graded' };

  return (
    <div className="px-6 py-5">
      <div className="flex items-start justify-between gap-4 mb-2">
        <div className="flex-1">
          <div className="text-xs text-gray-500 mb-1">Q{index} · {answer.points_awarded} / {answer.points_possible} pts</div>
          <div className="font-medium text-gray-800 mb-2">{answer.question_text}</div>
        </div>
        <span className={`inline-flex px-2 py-1 rounded-full text-xs ${badge.bg} ${badge.fg}`}>{badge.label}</span>
      </div>

      <div className="mb-3">
        <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">Student answer</div>
        <div className="bg-gray-50 border border-gray-200 rounded p-3 text-sm text-gray-800 whitespace-pre-wrap">
          {answer.student_answer || <em className="text-gray-400">No answer submitted.</em>}
        </div>
      </div>

      {answer.grader_reasoning && (
        <div className="mb-3">
          <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">Grader reasoning</div>
          <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-800 whitespace-pre-wrap">
            {answer.grader_reasoning}
          </div>
        </div>
      )}

      {answer.correct_answer && (
        <details className="mb-3">
          <summary className="text-xs uppercase tracking-wide text-gray-500 cursor-pointer">Model answer</summary>
          <div className="bg-gray-50 border border-gray-200 rounded p-3 text-sm text-gray-700 whitespace-pre-wrap mt-1">
            {answer.correct_answer}
          </div>
        </details>
      )}

      <div className="flex items-center gap-3 pt-2 border-t">
        <label className="text-xs uppercase tracking-wide text-gray-500">Points</label>
        <input
          type="number"
          step="0.5"
          min={0}
          max={answer.points_possible}
          value={points}
          onChange={e => setPoints(parseFloat(e.target.value) || 0)}
          className="w-20 border rounded px-2 py-1 text-sm"
        />
        <span className="text-xs text-gray-500">/ {answer.points_possible}</span>
        <button
          onClick={handleConfirm}
          disabled={saving}
          className={`px-3 py-1 text-sm rounded ${saving ? 'bg-gray-200 text-gray-500' : 'bg-green-500 text-white hover:bg-green-600'}`}
        >
          {saving ? 'Saving...' : gradedBy === 'none' ? 'Save grade' : 'Confirm / override'}
        </button>
        {saveError && <span className="text-xs text-red-600">{saveError}</span>}
      </div>
    </div>
  );
}
