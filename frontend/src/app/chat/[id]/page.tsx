'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, Conversation, Message } from '@/lib/api';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { ViolationToast } from '@/components/ViolationToast';
import { ViolationModal } from '@/components/ViolationModal';
import { SessionTerminated } from '@/components/SessionTerminated';

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const conversationId = params.id as string;

  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shouldEnd, setShouldEnd] = useState(false);
  const [ending, setEnding] = useState(false);

  // Violation state
  const [violationCount, setViolationCount] = useState(0);
  const [showToast, setShowToast] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalViolationNumber, setModalViolationNumber] = useState(0);
  const [terminated, setTerminated] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Timer state
  const [activeSeconds, setActiveSeconds] = useState(0);
  const [timerStarted, setTimerStarted] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Track if page has loaded initially (skip first visibility event)
  const hasLoadedRef = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Start/stop timer
  useEffect(() => {
    if (timerStarted && !isPaused && !terminated) {
      timerRef.current = setInterval(() => {
        setActiveSeconds((prev) => prev + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [timerStarted, isPaused, terminated]);

  // Violation handler
  const handleViolation = useCallback(async () => {
    if (!conversation || conversation.status !== 'in_progress' || terminated) return;

    const newCount = violationCount + 1;
    setViolationCount(newCount);

    // Log violation to backend
    try {
      await api.logViolation(
        conversationId,
        newCount,
        new Date().toISOString(),
        conversation.turn_count,
      );
    } catch {
      // Non-critical — don't block UI
    }

    if (newCount === 1) {
      // 1st: Toast
      setShowToast(true);
    } else if (newCount === 2) {
      // 2nd: Modal, pause timer
      setIsPaused(true);
      setModalViolationNumber(2);
      setShowModal(true);
    } else if (newCount === 3) {
      // 3rd: Hard warning modal, pause timer
      setIsPaused(true);
      setModalViolationNumber(3);
      setShowModal(true);
    } else if (newCount >= 4) {
      // 4th: Auto-submit
      setTerminated(true);
      try {
        await api.endConversation(conversationId, activeSeconds);
      } catch {
        // Best effort
      }
    }
  }, [conversation, conversationId, violationCount, terminated, activeSeconds]);

  // Set up visibility/blur listeners
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!hasLoadedRef.current) {
        hasLoadedRef.current = true;
        return;
      }
      if (document.hidden) {
        handleViolation();
      }
    };

    const handleBlur = () => {
      if (!hasLoadedRef.current) {
        hasLoadedRef.current = true;
        return;
      }
      // Only trigger on blur if document is not hidden (avoids double-fire)
      if (!document.hidden) {
        handleViolation();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);

    // Mark as loaded after a short delay
    const loadTimer = setTimeout(() => {
      hasLoadedRef.current = true;
    }, 1000);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
      clearTimeout(loadTimer);
    };
  }, [handleViolation]);

  useEffect(() => {
    loadConversation();
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversation = async () => {
    try {
      setLoading(true);
      const data = await api.getConversation(conversationId);
      setConversation(data);
      setViolationCount(data.violation_count || 0);
      if (data.total_active_seconds) {
        setActiveSeconds(data.total_active_seconds);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversation');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!conversation || sending) return;

    // Start timer on first message sent
    if (!timerStarted) {
      setTimerStarted(true);
    }

    try {
      setSending(true);
      setError(null);

      const response = await api.sendMessage(conversationId, content);

      setConversation((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          messages: [
            ...prev.messages,
            response.student_message,
            response.stakeholder_message,
          ],
          turn_count: response.turn_count,
          status: response.conversation_status as Conversation['status'],
        };
      });

      if (response.should_end) {
        setShouldEnd(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleEndConversation = async () => {
    if (!conversation || ending) return;

    try {
      setEnding(true);
      const response = await api.endConversation(conversationId, activeSeconds);

      setConversation((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          status: response.status as Conversation['status'],
          completed_at: response.completed_at,
          messages: response.final_message
            ? [...prev.messages, response.final_message]
            : prev.messages,
        };
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end conversation');
    } finally {
      setEnding(false);
    }
  };

  const handleModalAcknowledge = () => {
    setShowModal(false);
    setIsPaused(false);
  };

  const formatTime = (seconds: number): string => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s.toString().padStart(2, '0')}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-gray-600">Loading conversation...</p>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Conversation not found</p>
          <button
            onClick={() => router.push('/scenarios')}
            className="text-blue-500 hover:underline"
          >
            Back to scenarios
          </button>
        </div>
      </div>
    );
  }

  const isActive = conversation.status === 'in_progress' && !terminated;

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Violation overlays */}
      <ViolationToast show={showToast} onDismiss={() => setShowToast(false)} />
      <ViolationModal
        show={showModal}
        violationNumber={modalViolationNumber}
        onAcknowledge={handleModalAcknowledge}
      />
      {terminated && <SessionTerminated conversationId={conversationId} />}

      {/* Header */}
      <header className="bg-white shadow flex-shrink-0">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/scenarios')}
              className="text-gray-600 hover:text-gray-800"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="font-semibold text-gray-800">
                {conversation.persona_name}
              </h1>
              <p className="text-sm text-gray-500">
                {conversation.persona_title}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {timerStarted && (
              <span className={`text-sm font-mono ${isPaused ? 'text-yellow-600' : 'text-gray-500'}`}>
                {formatTime(activeSeconds)}
              </span>
            )}
            <span className="text-sm text-gray-500">
              Turn {conversation.turn_count}
            </span>
            {violationCount > 0 && (
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                violationCount >= 3 ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {violationCount} violation{violationCount !== 1 ? 's' : ''}
              </span>
            )}
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                isActive
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              {conversation.status.replace('_', ' ')}
            </span>
            {isActive && (
              <button
                onClick={handleEndConversation}
                disabled={ending}
                className="text-sm text-red-600 hover:text-red-800 disabled:text-gray-400"
              >
                {ending ? 'Ending...' : 'End Conversation'}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Should end warning */}
      {shouldEnd && isActive && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-center text-sm text-yellow-700">
          Conversation is nearing the end. You may want to wrap up or end the conversation.
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-2 flex items-center justify-between">
          <span className="text-red-700">{error}</span>
          <button
            onClick={() => setError(null)}
            className="text-red-500 hover:text-red-700"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Context */}
      <div className="bg-blue-50 border-b border-blue-200 px-4 py-2 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          <p className="text-xs text-blue-600 font-medium">YOUR PROJECT:</p>
          <p className="text-sm text-blue-800 line-clamp-2">{conversation.context}</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {conversation.messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              personaName={conversation.persona_name}
            />
          ))}
          {sending && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <div className="animate-bounce w-2 h-2 bg-gray-400 rounded-full" />
                  <div className="animate-bounce w-2 h-2 bg-gray-400 rounded-full delay-100" />
                  <div className="animate-bounce w-2 h-2 bg-gray-400 rounded-full delay-200" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input or Completed state */}
      {isActive ? (
        <ChatInput
          onSend={handleSendMessage}
          disabled={sending}
          placeholder="Type your response to the stakeholder..."
        />
      ) : !terminated ? (
        <div className="bg-gray-200 p-4 text-center">
          <p className="text-gray-600 mb-3">
            Conversation completed
            {activeSeconds > 0 && ` | Duration: ${formatTime(activeSeconds)}`}
          </p>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => router.push(`/grade/${conversationId}`)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              View Grade & Feedback
            </button>
          </div>
          <div className="flex justify-center gap-4 mt-3">
            <button
              onClick={() => router.push('/scenarios')}
              className="text-blue-500 hover:underline text-sm"
            >
              Start new practice
            </button>
            <button
              onClick={() => router.push('/history')}
              className="text-blue-500 hover:underline text-sm"
            >
              View history
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
