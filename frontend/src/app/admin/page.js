import Link from "next/link";
import { ROLE_LABELS } from "@/lib/roles";
import { requireAdmin } from "@/lib/session";
import styles from "@/components/admin/admin.module.css";

export default async function AdminHomePage() {
  const admin = await requireAdmin();
  const isSuperAdmin = admin.role === "super_admin";

  return (
    <main className="container">
      <h1 className={styles.pageTitle}>ยินดีต้อนรับ</h1>
      <p className={styles.subtle}>
        คุณเข้าสู่ระบบในฐานะ <strong>{ROLE_LABELS[admin.role]}</strong>
      </p>

      <div className={styles.cards}>
        <div className={styles.card}>
          <h2>จัดการสินค้า</h2>
          <p>นำเข้าสินค้าจาก Excel แก้ไขข้อมูล อัปโหลดรูป และสร้าง QR (เปิดใช้งานในขั้นถัดไป)</p>
        </div>

        {isSuperAdmin && (
          <Link href="/admin/users" className={styles.card}>
            <h2>จัดการผู้ใช้ →</h2>
            <p>เชิญ Admin ใหม่ทางอีเมล และเปิด/ปิดการใช้งานบัญชี</p>
          </Link>
        )}
      </div>
    </main>
  );
}
