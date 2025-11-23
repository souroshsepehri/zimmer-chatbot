import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const message = body?.message as string | undefined;
    const style = (body?.style as string | undefined) || "auto";
    const context = body?.context as {
      session_id?: string;
      page_url?: string;
      history?: Array<{ role: string; content: string }>;
    } | undefined;

    if (!message || typeof message !== "string" || !message.trim()) {
      return NextResponse.json(
        { success: false, error: "پیام نامعتبر است." },
        { status: 400 }
      );
    }

    const base = process.env.NEXT_PUBLIC_CHATBOT_API_BASE;
    if (!base) {
      return NextResponse.json(
        { success: false, error: "Chatbot API base is not configured." },
        { status: 500 }
      );
    }

    // Build payload for SmartAIAgent endpoint
    const payload: {
      message: string;
      style: string;
      context?: {
        session_id?: string;
        page_url?: string;
        history?: Array<{ role: string; content: string }>;
      };
    } = {
      message,
      style: "auto", // Always use "auto" - style selection is not exposed to users
    };

    // Add context if provided
    if (context) {
      payload.context = {
        session_id: context.session_id,
        page_url: context.page_url,
        history: context.history || [],
      };
    }

    const res = await fetch(`${base}/api/smart-agent/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json(
        { success: false, error: `Chatbot error: ${res.status} – ${text}` },
        { status: 500 }
      );
    }

    const data = await res.json();

    // Check if response has an error field
    if (data.error) {
      return NextResponse.json(
        {
          success: false,
          error: "در حال حاضر دستیار سایت با مشکل فنی روبه‌رو است. لطفاً چند دقیقه دیگر دوباره تلاش کنید.",
        },
        { status: 500 }
      );
    }

    return NextResponse.json(
      {
        success: true,
        response: data.response,
        style: data.style,
        raw: data,
      },
      { status: 200 }
    );
  } catch (err: any) {
    console.error("Chatbot proxy error:", err);
    return NextResponse.json(
      { success: false, error: "در حال حاضر دستیار سایت با مشکل فنی روبه‌رو است. لطفاً چند دقیقه دیگر دوباره تلاش کنید." },
      { status: 500 }
    );
  }
}

