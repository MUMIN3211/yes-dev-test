"use client";

import { useActionState } from "react";
import { inviteAdminAction } from "@/app/admin/actions";
import styles from "./admin.module.css";

export default function InviteForm() {
  const [state, formAction, pending] = useActionState(inviteAdminAction, {});

  return (
    <form action={formAction} className={styles.form} style={{ marginTop: 0 }}>
      {/* key resets the input after a successful invite */}
      <div className={styles.inlineForm} key={state.success}>
        <input
          type="email"
          name="email"
          required
          placeholder="อีเมลของ Admin ใหม่"
          aria-label="อีเมลของ Admin ใหม่"
          defaultValue={state.error ? state.email : ""}
          className={styles.input}
        />
        <button type="submit" className={styles.button} disabled={pending}>
          {pending ? "กำลังส่ง..." : "ส่งคำเชิญ"}
        </button>
      </div>
      {state.error && (
        <p className={styles.error} role="alert">
          {state.error}
        </p>
      )}
      {state.success && (
        <p className={styles.success} role="status">
          {state.success}
        </p>
      )}
    </form>
  );
}
