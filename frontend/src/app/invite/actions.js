"use server";

import { redirect } from "next/navigation";
import { request } from "@/lib/api";
import { PASSWORD_MIN_LENGTH } from "@/lib/roles";

// accessToken comes from the Supabase invitation link (#access_token=...).
// It is sent to the backend in the request body, never in a URL.

export async function getInvitationAction(accessToken) {
  try {
    return { invitation: await request("/api/auth/invitation", { body: { access_token: accessToken } }) };
  } catch (err) {
    return { error: err.message };
  }
}

export async function acceptInvitationAction(_prevState, formData) {
  const accessToken = String(formData.get("access_token") ?? "");
  const password = String(formData.get("password") ?? "");
  const confirm = String(formData.get("confirm") ?? "");

  if (password.length < PASSWORD_MIN_LENGTH) {
    return { error: `รหัสผ่านต้องมีอย่างน้อย ${PASSWORD_MIN_LENGTH} ตัวอักษร` };
  }
  if (password !== confirm) {
    return { error: "รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน" };
  }

  try {
    await request("/api/auth/invitation/accept", { body: { access_token: accessToken, password } });
  } catch (err) {
    return { error: err.message };
  }
  redirect("/login?invited=1");
}
