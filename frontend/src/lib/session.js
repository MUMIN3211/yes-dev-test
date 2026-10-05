// Server-side session helpers. The FastAPI JWT lives in an httpOnly cookie
// set by Next.js, so browser JavaScript can never read it. Import this only
// from server components, server actions or route handlers.
import { cache } from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, request } from "./api";

export const SESSION_COOKIE = "luma_admin_token";

export async function getSessionToken() {
  return (await cookies()).get(SESSION_COOKIE)?.value ?? null;
}

export async function setSession(token, maxAgeSeconds) {
  (await cookies()).set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: maxAgeSeconds,
  });
}

export async function clearSession() {
  (await cookies()).delete(SESSION_COOKIE);
}

// The logged-in admin, or null when there is no valid session.
// cache() = one /me call per request even if layout and page both ask.
export const getCurrentAdmin = cache(async () => {
  const token = await getSessionToken();
  if (!token) return null;
  try {
    return await request("/api/auth/me", { token });
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) return null;
    throw err;
  }
});

// For admin layouts/pages: the logged-in admin, or redirect to /login.
// Layouts and pages render in parallel, so each page calls this itself
// instead of relying on the layout's check.
export async function requireAdmin() {
  const admin = await getCurrentAdmin();
  if (!admin) redirect("/login");
  return admin;
}

// Authenticated call to the backend using the session cookie.
export async function adminRequest(path, options = {}) {
  return request(path, { ...options, token: await getSessionToken() });
}
