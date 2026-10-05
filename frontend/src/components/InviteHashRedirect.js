"use client";

import { useEffect } from "react";

// If /invite is not in Supabase's allowed Redirect URLs, Supabase falls back
// to the Site URL (usually "/") but still appends #access_token=...&type=invite.
// Forward that to the sign-up page so the invitation still works.
export default function InviteHashRedirect() {
  useEffect(() => {
    const { hash, pathname } = window.location;
    if (pathname !== "/invite" && /(^#|&)type=invite(&|$)/.test(hash)) {
      window.location.replace(`/invite${hash}`);
    }
  }, []);
  return null;
}
