import { createContext, useContext, useEffect, useRef, ReactNode } from 'react';

const WSContext = createContext<any>(null);

export const WebSocketProvider = ({ children, userId }: { children: ReactNode, userId: string }) => {
  const ws = useRef<WebSocket | null>(null);
  const listeners = useRef<((data: any) => void)[]>([]);

  useEffect(() => {
    ws.current = new WebSocket(`ws://localhost:8000/ws/${userId}`);
    ws.current.onmessage = (e) => {
      const data = JSON.parse(e.data);
      listeners.current.forEach(l => l(data));
    };
    return () => ws.current?.close();
  }, [userId]);

  const subscribe = (l: (data: any) => void) => { listeners.current.push(l); };
  
  return <WSContext.Provider value={{ subscribe }}>{children}</WSContext.Provider>;
};
export const useWebSocket = () => useContext(WSContext);
