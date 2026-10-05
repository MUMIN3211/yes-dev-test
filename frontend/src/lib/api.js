// Thin wrapper around the FastAPI backend. Every page talks to the backend
// through here — the frontend never calls Supabase directly.

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// FastAPI returns `detail` as a string for our own errors, or as a list of
// field errors for request validation (422).
function messageFrom(detail, fallback) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length) return "ข้อมูลที่กรอกไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง";
  return fallback;
}

export async function request(path, { token, body, method, ...options } = {}) {
  const headers = { ...options.headers };
  if (token) headers.Authorization = `Bearer ${token}`;
  // FormData (file uploads) sets its own multipart Content-Type with the boundary
  const isForm = body instanceof FormData;
  if (body !== undefined && !isForm) headers["Content-Type"] = "application/json";

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      // Data must always be fresh: an edited product should show its new
      // data the next time someone scans its QR.
      cache: "no-store",
      ...options,
      method: method ?? (body !== undefined ? "POST" : "GET"),
      headers,
      body: body === undefined || isForm ? body : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้", 503);
  }

  if (!res.ok) {
    let detail;
    try {
      detail = (await res.json()).detail;
    } catch {}
    throw new ApiError(messageFrom(detail, res.statusText), res.status);
  }
  return res.status === 204 ? null : res.json();
}

export function getPublicProducts({ category, q } = {}) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (q) params.set("q", q);
  const qs = params.toString();
  return request(`/api/public/products${qs ? `?${qs}` : ""}`);
}

export function getPublicProduct(sku) {
  return request(`/api/public/products/${encodeURIComponent(sku)}`);
}
