// Typed client for /api/auth/*. The session token rides in an HttpOnly
// cookie that the browser auto-attaches; the responses here never carry
// it directly, so there's nothing to persist client-side beyond the
// public user object.

export type AuthUser = {
  id:         string;
  email:      string;
  created_at: string;
};

async function authJSON<T>(path: string, init: RequestInit = {}): Promise<T> {
  const resp = await fetch(path, {
    credentials: "include",
    ...init,
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
  });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as T;
}

export async function signup(email: string, password: string): Promise<{ user: AuthUser }> {
  return authJSON("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email: string, password: string): Promise<{ user: AuthUser }> {
  return authJSON("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<{ ok: boolean }> {
  return authJSON("/api/auth/logout", { method: "POST", body: JSON.stringify({}) });
}

export async function fetchMe(): Promise<AuthUser | null> {
  try {
    const resp = await fetch("/api/auth/me", { credentials: "include" });
    if (resp.status === 401) return null;
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const { user } = (await resp.json()) as { user: AuthUser };
    return user;
  } catch {
    return null;
  }
}
