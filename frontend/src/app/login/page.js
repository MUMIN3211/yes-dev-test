import { redirect } from "next/navigation";
import LoginForm from "@/components/admin/LoginForm";
import { safeNextPath } from "@/lib/roles";
import { getCurrentAdmin } from "@/lib/session";
import styles from "@/components/admin/admin.module.css";

export const metadata = { title: "เข้าสู่ระบบผู้ดูแล | Luma Skin Care" };

// Back-office login. There is intentionally no sign-up page: accounts are
// created only by a Super Admin invitation.
export default async function LoginPage({ searchParams }) {
  const params = await searchParams;
  if (await getCurrentAdmin()) redirect(safeNextPath(params.next));

  return (
    <main className="container">
      <div className={styles.authCard}>
        <h1>เข้าสู่ระบบผู้ดูแล</h1>
        <p className={styles.subtle}>สำหรับ Admin และ Super Admin เท่านั้น</p>

        {params.invited && (
          <p className={styles.success} style={{ marginTop: 16 }}>
            ตั้งรหัสผ่านเรียบร้อยแล้ว กรุณาเข้าสู่ระบบ
          </p>
        )}

        <LoginForm next={params.next} />

        <p className={styles.subtle} style={{ marginTop: 16, fontSize: "0.8rem" }}>
          ยังไม่มีบัญชี? ติดต่อ Super Admin เพื่อขอคำเชิญทางอีเมล
        </p>
      </div>
    </main>
  );
}
