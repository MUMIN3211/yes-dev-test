import { API_URL } from "@/lib/api";
import { getSessionToken } from "@/lib/session";

const SKU_PATTERN = /^LS-\d{4}$/i;
const FORMATS = { png: "image/png", svg: "image/svg+xml" };

// The QR image endpoint needs the admin token, which lives in an httpOnly cookie
// that <img> tags cannot attach as a header. This route adds it server-side.
//   /admin/products/LS-1001/qr?format=png&scale=10&download=1
export async function GET(request, { params }) {
  const { sku } = await params;
  if (!SKU_PATTERN.test(sku)) return new Response("Not found", { status: 404 });

  const token = await getSessionToken();
  if (!token) return new Response("Unauthorized", { status: 401 });

  const search = request.nextUrl.searchParams;
  const format = search.get("format") in FORMATS ? search.get("format") : "png";
  const backendParams = new URLSearchParams({ format, scale: search.get("scale") ?? "10" });

  let res;
  try {
    res = await fetch(`${API_URL}/api/admin/products/${encodeURIComponent(sku)}/qr?${backendParams}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
  } catch {
    return new Response("Backend unavailable", { status: 503 });
  }
  if (!res.ok) return new Response(null, { status: res.status });

  const headers = new Headers({
    "Content-Type": FORMATS[format],
    "Cache-Control": "private, max-age=300",
  });
  if (search.get("download")) {
    headers.set("Content-Disposition", `attachment; filename="${sku.toUpperCase()}-qr.${format}"`);
  }
  return new Response(res.body, { headers });
}
