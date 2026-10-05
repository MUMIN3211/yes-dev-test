"use server";

import { revalidatePath } from "next/cache";
import { adminRequest } from "@/lib/session";

const MAX_FILE_BYTES = 5 * 1024 * 1024; // same limit as the backend

// Called twice per import: dry_run=true to preview what will happen, then
// dry_run=false after the admin confirms. `fileKey` identifies the selected
// file so the form can hide a preview that belongs to a different file.
export async function importProductsAction(_prevState, formData) {
  const file = formData.get("file");
  const dryRun = formData.get("dry_run") !== "false";
  const fileKey = String(formData.get("file_key") ?? "");

  if (!(file instanceof File) || file.size === 0) return { error: "กรุณาเลือกไฟล์ Excel", fileKey };
  if (!file.name.toLowerCase().endsWith(".xlsx")) return { error: "รองรับเฉพาะไฟล์ .xlsx", fileKey };
  if (file.size > MAX_FILE_BYTES) return { error: "ไฟล์ใหญ่เกิน 5 MB", fileKey };

  const body = new FormData();
  body.set("file", file, file.name);
  body.set("dry_run", String(dryRun));

  let result;
  try {
    result = await adminRequest("/api/admin/products/import", { body });
  } catch (err) {
    return { error: err.message, fileKey };
  }

  if (!dryRun) {
    revalidatePath("/admin/products");
    revalidatePath("/");
  }
  return { result, fileKey };
}
