import { create } from "zustand";

export interface UserProfile {
  email: string;
  role: string;
  full_name: string;
  department?: string;
  permissions?: string[];
}

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: UserProfile, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: typeof window !== "undefined" ? JSON.parse(localStorage.getItem("pvcpilot_user") || "null") : null,
  token: typeof window !== "undefined" ? localStorage.getItem("pvcpilot_token") : null,
  isAuthenticated: typeof window !== "undefined" ? !!localStorage.getItem("pvcpilot_token") : false,
  login: (user, token) => {
    localStorage.setItem("pvcpilot_user", JSON.stringify(user));
    localStorage.setItem("pvcpilot_token", token);
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem("pvcpilot_user");
    localStorage.removeItem("pvcpilot_token");
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
