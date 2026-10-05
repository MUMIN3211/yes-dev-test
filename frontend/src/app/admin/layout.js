import AdminNav from "@/components/admin/AdminNav";
import { requireAdmin } from "@/lib/session";

export const metadata = { title: "หลังบ้าน | Luma Skin Care" };

// Every /admin page goes through here. middleware.js already sent visitors
// without a cookie to /login; this verifies the token with the backend
// (expired, tampered or deactivated accounts get null).
export default async function AdminLayout({ children }) {
  const admin = await requireAdmin();

  return (
    <>
      <AdminNav admin={admin} />
      {children}
    </>
  );
}
