"use server";

import { redirect } from "next/navigation";
import { request } from "@/lib/api";
import { safeNextPath } from "@/lib/roles";
import { setSession } from "@/lib/session";

export async function loginAction(_prevState, formData) {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  if (!email || !password) {
    return { error: "กรุณากรอกอีเมลและรหัสผ่าน", email };
  }

  let data;
  try {
    data = await request("/api/auth/login", { body: { email, password } });
  } catch (err) {
    return { error: err.message, email };
  }

  await setSession(data.access_token, data.expires_in);
  redirect(safeNextPath(formData.get("next")));
}
