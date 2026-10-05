import { NextResponse } from "next/server";

const SESSION_COOKIE = "luma_admin_token";

// Fast gate for the back office: no session cookie -> go to the login page.
// The token itself is verified by the backend (/api/auth/me) in the admin layout.
export function middleware(request) {
  if (!request.cookies.has(SESSION_COOKIE)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};
