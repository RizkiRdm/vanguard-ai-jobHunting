import { useEffect, useState } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export const Toast = ({ id, message, type, onClose }: { id: number, message: string, type: ToastType, onClose: () => void }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="bg-elevated border border-border rounded-xl px-4 py-3 shadow-lg">
      {message}
    </div>
  );
};
