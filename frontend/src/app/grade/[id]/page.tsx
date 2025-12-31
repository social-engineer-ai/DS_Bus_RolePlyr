'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, Grade, Conversation } from '@/lib/api';
import { GradeDisplay } from '@/components/GradeDisplay';

export default function GradePage() {
  const params = useParams();
  const router = useRouter();
  const conversationId = params.id as string;

  const [grade, setGrade] = useState<Grade | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [grading, setGrading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [conversationId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load conversation
      const conv = await api.getConversation(conversationId);
      setConversation(conv);

      // Try to load grade
      try {
        const gradeData = await api.getGrade(conversationId);
        setGrade(gradeData);
      } catch (e) {
        // Grade might not exist yet
        setGrade(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerGrading = async () => {
    try {
      setGrading(true);
      setError(null);
      const gradeData = await api.triggerGrading(conversationId);
      setGrade(gradeData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to grade conversation');
    } finally {
      setGrading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading grade...</p>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Conversation not found</p>
          <button
            onClick={() => router.push('/history')}
            className="text-blue-500 hover:underline"
          >
            Back to history
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.back()}
              className="text-gray-600 hover:text-gray-800"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="font-semibold text-gray-800">Grade & Feedback</h1>
              <p className="text-sm text-gray-500">
                {conversation.persona_name} - {new Date(conversation.started_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => router.push(`/chat/${conversationId}`)}
              className="text-sm text-blue-500 hover:text-blue-700"
            >
              View Conversation
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
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

        {conversation.status !== 'completed' ? (
          <div className="bg-yellow-50 rounded-lg p-6 text-center">
            <p className="text-yellow-800 mb-4">
              This conversation is not yet complete. Finish the conversation to receive a grade.
            </p>
            <button
              onClick={() => router.push(`/chat/${conversationId}`)}
              className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600"
            >
              Continue Conversation
            </button>
          </div>
        ) : !grade ? (
          <div className="bg-white rounded-lg p-6 shadow-md text-center">
            <p className="text-gray-600 mb-4">
              This conversation hasn't been graded yet.
            </p>
            <button
              onClick={handleTriggerGrading}
              disabled={grading}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-300"
            >
              {grading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Grading...
                </span>
              ) : (
                'Get Grade'
              )}
            </button>
            <p className="text-sm text-gray-500 mt-2">
              This may take a few moments
            </p>
          </div>
        ) : (
          <GradeDisplay grade={grade} />
        )}

        {/* Quick actions */}
        <div className="mt-8 flex justify-center gap-4">
          <button
            onClick={() => router.push('/scenarios')}
            className="text-blue-500 hover:underline"
          >
            Practice Again
          </button>
          <button
            onClick={() => router.push('/history')}
            className="text-blue-500 hover:underline"
          >
            View History
          </button>
        </div>
      </main>
    </div>
  );
}
