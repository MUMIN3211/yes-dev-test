import InviteSignup from "@/components/admin/InviteSignup";
import styles from "@/components/admin/admin.module.css";

export const metadata = { title: "สมัครเป็นผู้ดูแลระบบ | Luma Skin Care" };

// Sign-up page reached only from the Supabase invitation email. Supabase
// verifies the link and redirects here with the session in the URL fragment
// (#access_token=...), which only the browser can read, so the work happens
// in the client component.
export default function InvitePage() {
  return (
    <main className="container">
      <div className={styles.authCard}>
        <InviteSignup />
      </div>
    </main>
  );
}
