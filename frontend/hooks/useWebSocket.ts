import { useEffect, useRef, useState } from "react";
import { useAlertStore, AlertItem } from "../store/alertStore";
import { toast } from "sonner";

export function useWebSocket(topics: string = "machine_status,alerts") {
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const addAlert = useAlertStore((state) => state.addAlert);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
    const userStr = localStorage.getItem("pvcpilot_user");
    let userId = "user_default";
    if (userStr) {
      try {
        const u = JSON.parse(userStr);
        userId = u.email || "user_default";
      } catch (e) {}
    }

    const fullUrl = `${wsUrl}?user_id=${encodeURIComponent(userId)}&topics=${encodeURIComponent(topics)}`;
    
    const connect = () => {
      const socket = new WebSocket(fullUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        setConnected(true);
        console.log("WebSocket connected to topics:", topics);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.event === "new_alert") {
            const newItem: AlertItem = {
              id: Math.random().toString(),
              alert_type: data.alert_type || "machine_fault",
              severity: data.severity || "high",
              title: data.title,
              message: data.message,
              source: data.source || "Sensor Monitor",
              is_acknowledged: false,
              created_at: data.time || new Date().toISOString()
            };
            addAlert(newItem);
            
            // Trigger Sonner toast based on severity
            if (data.severity === "critical") {
              toast.error(`CRITICAL ALERT: ${data.title}\n${data.message}`);
            } else {
              toast.warning(`WARNING: ${data.title}`);
            }
          }
        } catch (err) {
          console.error("Failed to parse websocket event data:", err);
        }
      };

      socket.onclose = () => {
        setConnected(false);
        console.log("WebSocket disconnected. Retrying in 5 seconds...");
        setTimeout(() => connect(), 5000);
      };

      socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        socket.close();
      };
    };

    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [topics, addAlert]);

  return connected;
}
