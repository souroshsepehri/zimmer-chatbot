import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const message = body?.message as string | undefined;
    const style = (body?.style as string | undefined) || "auto";

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

    const res = await fetch(`${base}/api/smart-agent/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message, style }),
    });

    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json(
        { success: false, error: `Chatbot error: ${res.status} – ${text}` },
        { status: 500 }
      );
    }

    const data = await res.json();

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
      { success: false, error: "خطا در ارتباط با چت‌بات." },
      { status: 500 }
    );
  }
}

