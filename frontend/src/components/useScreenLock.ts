'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface UseScreenLockOptions {
  enabled: boolean;
  onTerminate?: () => void;
}

interface UseScreenLockReturn {
  violationCount: number;
  showToast: boolean;
  setShowToast: (show: boolean) => void;
  showModal: boolean;
  modalViolationNumber: number;
  handleModalAcknowledge: () => void;
  terminated: boolean;
  isPaused: boolean;
}

export function useScreenLock({ enabled, onTerminate }: UseScreenLockOptions): UseScreenLockReturn {
  const [violationCount, setViolationCount] = useState(0);
  const [showToast, setShowToast] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalViolationNumber, setModalViolationNumber] = useState(0);
  const [terminated, setTerminated] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  const hasLoadedRef = useRef(false);
  const violationCountRef = useRef(0);
  const terminatedRef = useRef(false);

  const handleViolation = useCallback(() => {
    if (!enabled || terminatedRef.current) return;

    const newCount = violationCountRef.current + 1;
    violationCountRef.current = newCount;
    setViolationCount(newCount);

    if (newCount === 1) {
      setShowToast(true);
    } else {
      // Every violation from the 2nd onward: pause and show a warning modal.
      // Auto-submit on the 4th violation is intentionally disabled — instructors
      // would rather a student keep working than lose their attempt to a stray
      // tab switch. Violations are still tracked and visible in the header.
      setIsPaused(true);
      setModalViolationNumber(newCount);
      setShowModal(true);
    }
  }, [enabled, onTerminate]);

  useEffect(() => {
    if (!enabled) return;

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
      if (!document.hidden) {
        handleViolation();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);

    const loadTimer = setTimeout(() => {
      hasLoadedRef.current = true;
    }, 1000);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
      clearTimeout(loadTimer);
    };
  }, [enabled, handleViolation]);

  const handleModalAcknowledge = useCallback(() => {
    setShowModal(false);
    setIsPaused(false);
  }, []);

  return {
    violationCount,
    showToast,
    setShowToast,
    showModal,
    modalViolationNumber,
    handleModalAcknowledge,
    terminated,
    isPaused,
  };
}
