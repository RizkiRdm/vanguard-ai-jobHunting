import { useEffect, useRef, useCallback } from "react";
import { useAgentStore } from "../store/useAgentStore";

interface AgentStreamPayload {
    task_id: string;
    thought?: string;
    action?: string;
    screenshot_url?: string;
    status?: string;
    [key: string]: unknown;
}

export const useAgentSocket = (userId: string | undefined) => {
    const socket = useRef<WebSocket | null>(null);
    const updateTaskStream = useAgentStore((state) => state.updateTaskStream);

    const connect = useCallback(() => {
        if (!userId || userId === "default-user") return;

        const baseUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8000";
        const wsUrl = `${baseUrl}/agent/ws/${userId}`;

        socket.current = new WebSocket(wsUrl);

        socket.current.onopen = () => {
            console.log("[WebSocket] Connected to Agent Stream:", userId);
        };

        socket.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === "AGENT_STREAM") {
                    updateTaskStream(data.payload as AgentStreamPayload);
                }
            } catch (error) {
                console.error("[WebSocket] Failed to parse message:", error);
            }
        };

        socket.current.onerror = (error) => {
            console.error("[WebSocket] Connection error:", error);
        };

        socket.current.onclose = (e) => {
            console.log("[WebSocket] Connection closed. Reconnecting in 3s...", e.reason);
            setTimeout(connect, 3000); // Simple auto-reconnect logic
        };
    }, [userId, updateTaskStream]);

    useEffect(() => {
        connect();

        return () => {
            if (socket.current) {
                socket.current.close();
            }
        };
    }, [connect]);

    return socket.current;
};