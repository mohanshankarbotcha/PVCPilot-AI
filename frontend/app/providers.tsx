"use client";

import React, { useEffect, useState } from "react";
import { Toaster } from "sonner";
import { useUIStore } from "../store/uiStore";

export function Providers({ children }: { children: React.ReactNode }) {
  const theme = useUIStore((state) => state.theme);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Apply theme class to HTML element
    const root = window.document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme]);

  if (!mounted) {
    return <div className="min-h-screen bg-neutral-900 text-white flex items-center justify-center">Loading PVCPilot AI Framework...</div>;
  }

  return (
    <>
      <Toaster position="top-right" richColors theme={theme} />
      {children}
    </>
  );
}
