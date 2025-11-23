"use client";

import { useState, useRef, useEffect } from "react";
import { useZimmerChatSessionId } from "@/hooks/useZimmerChatSessionId";

type Role = "user" | "assistant";

interface ChatMessage {
  id: string;
  role: Role;
  text: string;
}

export function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionId = useZimmerChatSessionId();

  // Scroll to bottom when new message is added
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading || !sessionId) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      text: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError(null);
    setLoading(true);

    try {
      // Build history array from previous messages (last 10 exchanges)
      const history = messages
        .slice(-10) // Last 10 messages
        .map((msg) => ({
          role: msg.role === "user" ? "user" : "assistant",
          content: msg.text,
        }));

      // Build request payload
      const payload = {
        message: trimmed,
        style: "auto", // Always use "auto" - user cannot choose
        context: {
          session_id: sessionId,
          page_url: typeof window !== "undefined" ? window.location.href : undefined,
          history: history,
        },
      };

      const res = await fetch("/api/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!data.success) {
        throw new Error(data.error || "خطا در پاسخ چت‌بات");
      }

      // Check if response has an error field
      if (data.raw?.error) {
        throw new Error("در حال حاضر دستیار سایت با مشکل فنی روبه‌رو است. لطفاً چند دقیقه دیگر دوباره تلاش کنید.");
      }

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        text: data.response,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error(err);
      // Show polite Persian error message
      setError(err.message || "در حال حاضر دستیار سایت با مشکل فنی روبه‌رو است. لطفاً چند دقیقه دیگر دوباره تلاش کنید.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Floating button */}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-4 right-4 z-40 rounded-full bg-purple-600 px-4 py-2 text-sm font-medium text-white shadow-lg hover:bg-purple-700 transition-colors duration-200 md:bottom-6 md:right-6"
      >
        {open ? "بستن دستیار" : "چت با دستیار زیمر"}
      </button>

      {/* Chat panel */}
      {open && (
        <div
          dir="rtl"
          className="fixed bottom-20 right-4 z-40 flex w-full max-w-sm flex-col overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-neutral-900 md:bottom-24 md:right-6"
          style={{ height: "70vh", maxHeight: "600px" }}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-3 dark:border-neutral-800">
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
                دستیار هوشمند زیمر
              </span>
              <span className="text-xs text-neutral-500 dark:text-neutral-400">
                سوالت رو بپرس، من جواب می‌دم
              </span>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex max-h-[60vh] flex-1 flex-col gap-2 overflow-y-auto bg-neutral-50 px-3 py-3 dark:bg-neutral-950">
            {messages.length === 0 && (
              <p className="text-center text-xs text-neutral-500 dark:text-neutral-400 py-4">
                سلام 😊 اینجا می‌تونی درباره‌ی خدمات زیمر، اتوماسیون و هر سوالی که داری بپرسی.
              </p>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={
                    msg.role === "user"
                      ? "max-w-[80%] rounded-2xl bg-white px-3 py-2 text-xs text-neutral-900 shadow dark:bg-neutral-800 dark:text-neutral-50"
                      : "max-w-[80%] rounded-2xl bg-purple-600 px-3 py-2 text-xs text-white shadow"
                  }
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <p className="text-xs text-neutral-500 dark:text-neutral-400 bg-neutral-100 dark:bg-neutral-800 px-3 py-2 rounded-2xl">
                  در حال فکر کردن…
                </p>
              </div>
            )}

            {error && (
              <div className="flex justify-start">
                <p className="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 px-3 py-2 rounded-2xl">
                  {error}
                </p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <form
            onSubmit={handleSend}
            className="border-t border-neutral-200 bg-white px-3 py-2 dark:border-neutral-800 dark:bg-neutral-900"
          >
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="پیامت رو اینجا بنویس..."
                className="flex-1 rounded-xl border border-neutral-200 bg-white px-3 py-2 text-xs text-neutral-900 focus:outline-none focus:ring-1 focus:ring-purple-500 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-50 dark:placeholder-neutral-400"
                disabled={loading || !sessionId}
              />
              <button
                type="submit"
                disabled={loading || !input.trim() || !sessionId}
                className="rounded-xl bg-purple-600 px-3 py-2 text-xs font-medium text-white shadow-sm hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-60 transition-colors duration-200"
              >
                ارسال
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}

