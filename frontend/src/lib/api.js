// Thin wrapper around the FastAPI backend. Every page talks to the backend
// through here — the frontend never calls Supabase directly.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      // Product data must always be fresh: an edited product should show
      // its new data the next time someone scans its QR.
      cache: "no-store",
      ...options,
    });
  } catch {
    throw new ApiError("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้", 503);
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {}
    throw new ApiError(detail, res.status);
  }
  return res.json();
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
