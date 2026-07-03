import { create } from "zustand";

export interface AlertItem {
  id: string;
  alert_type: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  message: string;
  source: string;
  is_acknowledged: boolean;
  created_at: string;
}

interface AlertState {
  alerts: AlertItem[];
  unreadCount: number;
  setAlerts: (alerts: AlertItem[]) => void;
  addAlert: (alert: AlertItem) => void;
  acknowledgeAlert: (id: string) => void;
  markAllRead: () => void;
}

export const useAlertStore = create<AlertState>((set) => ({
  alerts: [],
  unreadCount: 0,
  setAlerts: (alerts) => set({
    alerts,
    unreadCount: alerts.filter(a => !a.is_acknowledged).length
  }),
  addAlert: (alert) => set((state) => {
    const alerts = [alert, ...state.alerts];
    return {
      alerts,
      unreadCount: alerts.filter(a => !a.is_acknowledged).length
    };
  }),
  acknowledgeAlert: (id) => set((state) => {
    const alerts = state.alerts.map(a => a.id === id ? { ...a, is_acknowledged: true } : a);
    return {
      alerts,
      unreadCount: alerts.filter(a => !a.is_acknowledged).length
    };
  }),
  markAllRead: () => set((state) => {
    const alerts = state.alerts.map(a => ({ ...a, is_acknowledged: true }));
    return {
      alerts,
      unreadCount: 0
    };
  }),
}));
