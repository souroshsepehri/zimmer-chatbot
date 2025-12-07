/**
 * API Module - Functions used across the frontend:
 * 
 * Chat:
 *   - postChat (ChatWidget.tsx, app/admin/faqs/page.tsx)
 * 
 * FAQs:
 *   - getFAQs (app/admin/page.tsx, app/admin/faqs/page.tsx)
 *   - createFAQ (app/admin/faqs/page.tsx)
 *   - updateFAQ (app/admin/faqs/page.tsx)
 *   - deleteFAQ (app/admin/faqs/page.tsx)
 * 
 * Categories:
 *   - getCategories (app/admin/categories/page.tsx, app/admin/faqs/page.tsx, app/admin/page.tsx)
 *   - createCategory (app/admin/categories/page.tsx)
 *   - updateCategory (app/admin/categories/page.tsx)
 *   - deleteCategory (app/admin/categories/page.tsx)
 * 
 * Logs:
 *   - getLogStats (app/admin/page.tsx, app/admin/logs/page.tsx)
 *   - getLogs (app/admin/logs/page.tsx)
 *   - deleteLog (app/admin/logs/page.tsx)
 * 
 * Types:
 *   - FAQ (app/admin/faqs/page.tsx, components/FAQModal.tsx)
 *   - Category (app/admin/faqs/page.tsx, components/FAQModal.tsx)
 *   - ChatLog (app/admin/logs/page.tsx)
 *   - LogFilters (app/admin/logs/page.tsx)
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "";

/**
 * Helper function to make JSON API requests
 */
async function fetchJson<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status} ${res.statusText} for ${url}: ${text}`);
  }

  return res.json() as Promise<T>;
}

// ============================================================================
// Types
// ============================================================================

export interface FAQ {
  id: number;
  question: string;
  answer: string;
  category_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  category?: {
    id: number;
    name: string;
    slug: string;
  };
}

export interface Category {
  id: number;
  name: string;
  slug?: string;
  created_at?: string;
}

export interface ChatRequest {
  message: string;
  debug?: boolean;
}

export interface ChatResponse {
  answer: string;
  debug_info?: Record<string, unknown>;
}

export interface FAQCreate {
  question: string;
  answer: string;
  category_id?: number;
  is_active?: boolean;
}

export interface FAQUpdate {
  question?: string;
  answer?: string;
  category_id?: number;
  is_active?: boolean;
}

export interface ChatLog {
  id: number;
  timestamp: string;
  user_text: string;
  ai_text: string;
  intent?: string;
  source?: string;
  confidence?: number;
  success: boolean;
  matched_faq_id?: number;
  tokens_in?: number;
  tokens_out?: number;
  latency_ms?: number;
  notes?: string;
}

export interface LogFilters {
  success?: boolean;
  intent?: string;
  unanswered_only?: boolean;
  from_date?: string;
  to_date?: string;
  page?: number;
  page_size?: number;
}

export interface LogListResponse {
  items: ChatLog[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LogStats {
  total_chats: number;
  success_rate: number;
  today_chats: number;
  unanswered_logs: number;
}

// ============================================================================
// Chat API
// ============================================================================

export async function postChat(data: ChatRequest): Promise<ChatResponse> {
  return fetchJson<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ============================================================================
// FAQ API
// ============================================================================

export async function getFAQs(page = 1, pageSize = 50): Promise<FAQ[]> {
  const query = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  }).toString();

  const response = await fetchJson<{ items: FAQ[]; total: number }>(
    `/api/faqs?${query}`
  );
  
  // Return items array, or the response itself if it's already an array
  return response.items || (Array.isArray(response) ? response : []);
}

export async function createFAQ(data: FAQCreate): Promise<FAQ> {
  return fetchJson<FAQ>("/api/faqs", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateFAQ(id: number, data: FAQUpdate): Promise<FAQ> {
  return fetchJson<FAQ>(`/api/faqs/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteFAQ(id: number): Promise<void> {
  await fetchJson<void>(`/api/faqs/${id}`, {
    method: "DELETE",
  });
}

// ============================================================================
// Category API
// ============================================================================

export async function getCategories(): Promise<Category[]> {
  return fetchJson<Category[]>("/api/categories");
}

export async function createCategory(data: { name: string; slug: string }): Promise<Category> {
  return fetchJson<Category>("/api/categories", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateCategory(
  id: number,
  data: { name: string; slug: string }
): Promise<Category> {
  return fetchJson<Category>(`/api/categories/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteCategory(id: number): Promise<void> {
  await fetchJson<void>(`/api/categories/${id}`, {
    method: "DELETE",
  });
}

// ============================================================================
// Logs API
// ============================================================================

export async function getLogs(filters?: LogFilters): Promise<LogListResponse> {
  const queryParams = new URLSearchParams();
  
  if (filters) {
    if (filters.success !== undefined) {
      queryParams.append("success", String(filters.success));
    }
    if (filters.intent) {
      queryParams.append("intent", filters.intent);
    }
    if (filters.unanswered_only !== undefined) {
      queryParams.append("unanswered_only", String(filters.unanswered_only));
    }
    if (filters.from_date) {
      queryParams.append("from_date", filters.from_date);
    }
    if (filters.to_date) {
      queryParams.append("to_date", filters.to_date);
    }
    if (filters.page) {
      queryParams.append("page", String(filters.page));
    }
    if (filters.page_size) {
      queryParams.append("page_size", String(filters.page_size));
    }
  }
  
  const query = queryParams.toString();
  const path = query ? `/api/logs?${query}` : "/api/logs";
  
  return fetchJson<LogListResponse>(path);
}

export async function getLogStats(): Promise<LogStats> {
  return fetchJson<LogStats>("/api/logs/stats");
}

export async function deleteLog(id: number): Promise<void> {
  await fetchJson<void>(`/api/logs/${id}`, {
    method: "DELETE",
  });
}
