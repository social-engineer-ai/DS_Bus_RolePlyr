'use client';

interface ViolationModalProps {
  show: boolean;
  violationNumber: number;
  onAcknowledge: () => void;
}

export function ViolationModal({ show, violationNumber, onAcknowledge }: ViolationModalProps) {
  if (!show) return null;

  const isHardWarning = violationNumber >= 3;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="text-center">
          <div className={`text-4xl mb-4 ${isHardWarning ? 'text-red-500' : 'text-yellow-500'}`}>
            {isHardWarning ? '!!' : '!'}
          </div>
          <h2 className={`text-xl font-bold mb-2 ${isHardWarning ? 'text-red-800' : 'text-yellow-800'}`}>
            {isHardWarning ? 'Final Warning' : 'Focus Required'}
          </h2>
          <p className={`mb-6 ${isHardWarning ? 'text-red-700' : 'text-gray-600'}`}>
            {isHardWarning
              ? 'You have left this page multiple times. One more violation will automatically end your session.'
              : 'You navigated away from this page during an active session. Please remain on this page to continue your conversation.'}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Violation {violationNumber} of 4
          </p>
          <button
            onClick={onAcknowledge}
            className={`px-6 py-2 rounded-lg font-semibold text-white ${
              isHardWarning
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-yellow-500 hover:bg-yellow-600'
            }`}
          >
            I Understand — Continue Session
          </button>
        </div>
      </div>
    </div>
  );
}
