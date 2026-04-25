import { createContext, useContext, useState, ReactNode } from 'react';

type ToastType = 'success' | 'error' | 'warning' | 'info';
interface Toast { id: number; message: string; type: ToastType; }

const ToastContext = createContext<{ 
  success: (m: string) => void; 
  error: (m: string) => void; 
  warning: (m: string) => void; 
  info: (m: string) => void; 
} | null>(null);

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const add = (message: string, type: ToastType) => {
    const id = Date.now();
    setToasts(prev => [...prev.slice(-2), { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  };
  return (
    <ToastContext.Provider value={{ success: (m) => add(m, 'success'), error: (m) => add(m, 'error'), warning: (m) => add(m, 'warning'), info: (m) => add(m, 'info') }}>
      {children}
      <div className="fixed bottom-6 right-6 flex flex-col gap-2">
        {toasts.map(t => <div key={t.id} className="bg-elevated border border-border rounded-xl px-4 py-3">{t.message}</div>)}
      </div>
    </ToastContext.Provider>
  );
};
export const useToast = () => useContext(ToastContext)!;
