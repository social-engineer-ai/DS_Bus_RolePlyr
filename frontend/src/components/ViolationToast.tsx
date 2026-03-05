'use client';

import { useEffect, useState } from 'react';

interface ViolationToastProps {
  show: boolean;
  onDismiss: () => void;
}

export function ViolationToast({ show, onDismiss }: ViolationToastProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setVisible(true);
      const timer = setTimeout(() => {
        setVisible(false);
        onDismiss();
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [show, onDismiss]);

  if (!visible) return null;

  return (
    <div className="fixed top-4 right-4 z-50 animate-in slide-in-from-top">
      <div className="bg-yellow-50 border border-yellow-300 rounded-lg shadow-lg p-4 max-w-sm">
        <div className="flex items-start gap-3">
          <span className="text-yellow-500 text-xl flex-shrink-0">!</span>
          <div>
            <p className="font-medium text-yellow-800">Please stay on this page</p>
            <p className="text-sm text-yellow-700 mt-1">
              Switching away during an active session is tracked and may affect your grade.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
