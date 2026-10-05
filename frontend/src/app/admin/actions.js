"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { adminRequest, clearSession } from "@/lib/session";

export async function logoutAction() {
  await clearSession();
  redirect("/login");
}

export async function inviteAdminAction(_prevState, formData) {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) return { error: "กรุณากรอกอีเมล" };

  try {
    await adminRequest("/api/admin/invitations", { body: { email } });
  } catch (err) {
    return { error: err.message, email };
  }
  revalidatePath("/admin/users");
  return { success: `Supabase ส่งอีเมลคำเชิญไปที่ ${email.toLowerCase()} แล้ว` };
}

// Sends a fresh invitation email (the old link stops working)
export async function resendInvitationAction(_prevState, formData) {
  const email = String(formData.get("email"));
  try {
    await adminRequest("/api/admin/invitations", { body: { email } });
  } catch (err) {
    return { error: err.message };
  }
  revalidatePath("/admin/users");
  return {};
}

export async function setAdminActiveAction(_prevState, formData) {
  const id = String(formData.get("id"));
  const isActive = formData.get("is_active") === "true";
  try {
    await adminRequest(`/api/admin/users/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: { is_active: isActive },
    });
  } catch (err) {
    return { error: err.message };
  }
  revalidatePath("/admin/users");
  return {};
}

export async function revokeInvitationAction(_prevState, formData) {
  const id = String(formData.get("id"));
  try {
    await adminRequest(`/api/admin/invitations/${encodeURIComponent(id)}`, { method: "DELETE" });
  } catch (err) {
    return { error: err.message };
  }
  revalidatePath("/admin/users");
  return {};
}
