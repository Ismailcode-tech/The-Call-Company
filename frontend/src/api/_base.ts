// src/api/_base.ts
export const API_BASE_URL = "/api";

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",          //  sends cookies automatically
    headers: {
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
    ...init,
  });

  // token expired
  if (res.status === 401) {
    // try refresh
    const refreshed = await tryRefresh();
    if (refreshed) {
      // retry original request
      const retry = await fetch(`${API_BASE_URL}${path}`, {
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(init.headers || {}),
        },
        ...init,
      });
      if (!retry.ok) throw new Error(`API ${retry.status}`);
      const text = await retry.text();
      return text ? JSON.parse(text) : (undefined as T);
    }
    window.location.href = "/signin";
    throw new Error("Session expired");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `API ${res.status}`);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : (undefined as T);
}

async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",        //  refresh cookie sent automatically
      headers: { "Content-Type": "application/json" },
    });
    return res.ok;
  } catch {
    return false;
  }
}