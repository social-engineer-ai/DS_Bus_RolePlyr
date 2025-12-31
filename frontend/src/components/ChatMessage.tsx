'use client';

import { Message } from '@/lib/api';

interface ChatMessageProps {
  message: Message;
  personaName?: string;
}

export function ChatMessage({ message, personaName }: ChatMessageProps) {
  const isStudent = message.role === 'student';

  return (
    <div
      className={`flex ${isStudent ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isStudent
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-800'
        }`}
      >
        <div className="text-xs font-semibold mb-1 opacity-75">
          {isStudent ? 'You' : personaName || 'Stakeholder'}
        </div>
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div className="text-xs mt-2 opacity-50">
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
