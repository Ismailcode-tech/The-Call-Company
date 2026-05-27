export const API_BASE_URL = "http://localhost:5000/api";
export const MOCK_MODE = false;

// Shared fetch wrapper for every backend request.
// The generic <T> lets each API module describe the JSON it expects back.
export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  fallback?: () => Promise<T> | T,
): Promise<T> {
  // Mock mode is useful when a caller passes local fallback data for frontend-only testing.
  if (MOCK_MODE && fallback) {
    await new Promise((r) => setTimeout(r, 220));
    return await fallback();
  }

  // Send JSON by default, while still allowing each call to override headers.
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    ...init,
  });

  // Throwing here keeps API failures visible to pages and hooks.
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
  return (await res.json()) as T;
}
