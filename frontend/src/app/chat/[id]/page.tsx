'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api, Conversation, Message } from '@/lib/api';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';

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

  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversation');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!conversation || sending) return;

    try {
      setSending(true);
      setError(null);

      const response = await api.sendMessage(conversationId, content);

      // Update conversation with new messages
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
      const response = await api.endConversation(conversationId);

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

  const isActive = conversation.status === 'in_progress';

  return (
    <div className="h-screen flex flex-col bg-gray-100">
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
            <span className="text-sm text-gray-500">
              Turn {conversation.turn_count}
            </span>
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
      ) : (
        <div className="bg-gray-200 p-4 text-center">
          <p className="text-gray-600 mb-3">Conversation completed</p>
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
      )}
    </div>
  );
}
