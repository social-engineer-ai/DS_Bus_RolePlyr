'use client';

import { useRouter } from 'next/navigation';

interface SessionTerminatedProps {
  conversationId: string;
}

export function SessionTerminated({ conversationId }: SessionTerminatedProps) {
  const router = useRouter();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/80">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-8">
        <div className="text-center">
          <div className="text-5xl mb-4 text-red-500">X</div>
          <h2 className="text-2xl font-bold text-red-800 mb-2">Session Terminated</h2>
          <p className="text-gray-600 mb-6">
            Your session was automatically ended because you left this page too many times.
            Your conversation has been submitted as-is for grading.
          </p>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => router.push(`/grade/${conversationId}`)}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-600"
            >
              View Grade
            </button>
            <button
              onClick={() => router.push('/scenarios')}
              className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg font-semibold hover:bg-gray-300"
            >
              Back to Scenarios
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
