import InviteForm from "@/components/admin/InviteForm";
import RowActionButton from "@/components/admin/RowActionButton";
import { formatDateTime } from "@/lib/constants";
import { ROLE_LABELS } from "@/lib/roles";
import { adminRequest, requireAdmin } from "@/lib/session";
import { resendInvitationAction, revokeInvitationAction, setAdminActiveAction } from "../actions";
import styles from "@/components/admin/admin.module.css";

export const metadata = { title: "จัดการผู้ใช้ | Luma Skin Care" };

export default async function AdminUsersPage() {
  const me = await requireAdmin();

  // The backend enforces this too; here it just avoids showing a broken page
  if (me.role !== "super_admin") {
    return (
      <main className="container">
        <h1 className={styles.pageTitle}>ไม่มีสิทธิ์เข้าถึง</h1>
        <p className={styles.subtle}>หน้านี้สำหรับ Super Admin เท่านั้น</p>
      </main>
    );
  }

  const { admins, invitations } = await adminRequest("/api/admin/users");

  return (
    <main className="container">
      <h1 className={styles.pageTitle}>จัดการผู้ใช้</h1>
      <p className={styles.subtle}>
        เชิญ Admin ใหม่ทางอีเมล (ส่งผ่าน Supabase) ผู้ถูกเชิญกดลิงก์ในอีเมลเพื่อเข้าหน้าสมัครและตั้งรหัสผ่านเอง
      </p>

      <section className={styles.section}>
        <h2>เชิญ Admin ใหม่</h2>
        <InviteForm />
      </section>

      <section className={styles.section}>
        <h2>คำเชิญที่รอการยืนยัน ({invitations.length})</h2>
        {invitations.length === 0 ? (
          <p className={styles.empty}>ไม่มีคำเชิญที่รอการยืนยัน</p>
        ) : (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>อีเมล</th>
                  <th>เชิญโดย</th>
                  <th>เชิญเมื่อ</th>
                  <th>สถานะ</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {invitations.map((inv) => (
                  <tr key={inv.id}>
                    <td>{inv.email}</td>
                    <td>{inv.invited_by_email ?? "—"}</td>
                    <td>{formatDateTime(inv.invited_at)}</td>
                    <td>
                      <span className={styles.badgeMuted}>รอยืนยัน</span>
                    </td>
                    <td className={styles.rowActions}>
                      <RowActionButton
                        action={resendInvitationAction}
                        fields={{ email: inv.email }}
                        label="ส่งอีกครั้ง"
                        pendingLabel="กำลังส่ง..."
                      />
                      <RowActionButton
                        action={revokeInvitationAction}
                        fields={{ id: inv.id }}
                        label="ยกเลิกคำเชิญ"
                        pendingLabel="กำลังยกเลิก..."
                        variant="danger"
                        confirm={`ยกเลิกคำเชิญของ ${inv.email}?`}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className={styles.section}>
        <h2>ผู้ดูแลทั้งหมด ({admins.length})</h2>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>อีเมล</th>
                <th>Role</th>
                <th>สถานะ</th>
                <th>เข้าสู่ระบบล่าสุด</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {admins.map((admin) => {
                const canToggle = admin.id !== me.id && admin.role !== "super_admin";
                return (
                  <tr key={admin.id}>
                    <td>
                      {admin.email}
                      {admin.id === me.id && <span className={styles.hint}> (คุณ)</span>}
                    </td>
                    <td>
                      <span className={admin.role === "super_admin" ? styles.badgeAccent : styles.badgeMuted}>
                        {ROLE_LABELS[admin.role]}
                      </span>
                    </td>
                    <td>
                      {admin.is_active ? (
                        <span className={styles.badge}>ใช้งาน</span>
                      ) : (
                        <span className={styles.badgeDanger}>ปิดใช้งาน</span>
                      )}
                    </td>
                    <td>{formatDateTime(admin.last_login_at)}</td>
                    <td>
                      {canToggle && (
                        <RowActionButton
                          action={setAdminActiveAction}
                          fields={{ id: admin.id, is_active: !admin.is_active }}
                          label={admin.is_active ? "ปิดใช้งาน" : "เปิดใช้งาน"}
                          pendingLabel="กำลังบันทึก..."
                          variant={admin.is_active ? "danger" : "ghost"}
                          confirm={admin.is_active ? `ปิดการใช้งานบัญชี ${admin.email}?` : undefined}
                        />
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
