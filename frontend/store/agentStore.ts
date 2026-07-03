import { create } from "zustand";

export interface ChatMessage {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: string;
  agentName?: string;
}

interface AgentState {
  chatHistory: ChatMessage[];
  isStreaming: boolean;
  activeAgent: string | null;
  addMessage: (msg: ChatMessage) => void;
  updateLastMessageText: (text: string) => void;
  setStreaming: (val: boolean) => void;
  setActiveAgent: (name: string | null) => void;
  clearHistory: () => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  chatHistory: [
    {
      id: "init",
      sender: "agent",
      text: "Hello! I am the Coordinator Agent. I am here to help monitor and optimize your PVC pipe factory. Ask me anything about OEE, inventory, OEE anomalies, raw materials, or daily scheduling.",
      timestamp: new Date().toLocaleTimeString(),
      agentName: "Coordinator Agent"
    }
  ],
  isStreaming: false,
  activeAgent: "Coordinator Agent",
  addMessage: (msg) => set((state) => ({ chatHistory: [...state.chatHistory, msg] })),
  updateLastMessageText: (text) => set((state) => {
    const history = [...state.chatHistory];
    if (history.length > 0) {
      const lastMsg = history[history.length - 1];
      if (lastMsg.sender === "agent") {
        lastMsg.text += text;
      }
    }
    return { chatHistory: history };
  }),
  setStreaming: (val) => set({ isStreaming: val }),
  setActiveAgent: (name) => set({ activeAgent: name }),
  clearHistory: () => set({ chatHistory: [] }),
}));
