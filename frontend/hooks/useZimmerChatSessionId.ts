"use client";

import { useState, useEffect } from "react";

/**
 * Hook to manage a stable session ID for the Zimmer chat widget.
 * 
 * The session ID is stored in localStorage and persists across page reloads.
 * On first use, generates a unique ID and saves it to localStorage.
 * 
 * @returns The session ID string, or null if not yet initialized (client-side only)
 */
export function useZimmerChatSessionId(): string | null {
  const [sessionId, setSessionId] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    let current = window.localStorage.getItem("zimmer_chat_session_id");
    if (!current) {
      // Generate a unique session ID
      current = `zimmer-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      window.localStorage.setItem("zimmer_chat_session_id", current);
    }
    setSessionId(current);
  }, []);

  return sessionId;
}


















