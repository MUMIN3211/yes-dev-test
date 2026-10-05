"use client";

import { useActionState } from "react";
import { acceptInvitationAction } from "@/app/invite/actions";
import { PASSWORD_MIN_LENGTH } from "@/lib/roles";
import styles from "./admin.module.css";

export default function AcceptInviteForm({ accessToken, email }) {
  const [state, formAction, pending] = useActionState(acceptInvitationAction, {});

  return (
    <form action={formAction} className={styles.form}>
      <input type="hidden" name="access_token" value={accessToken} />

      {state.error && (
        <p className={styles.error} role="alert">
          {state.error}
        </p>
      )}

      <label className={styles.field}>
        อีเมลที่ได้รับเชิญ
        {/* Fixed to the invited address; also lets password managers save it */}
        <input
          type="email"
          name="username"
          value={email}
          readOnly
          autoComplete="username"
          className={`${styles.input} ${styles.inputReadOnly}`}
        />
      </label>

      <label className={styles.field}>
        รหัสผ่าน
        <input
          type="password"
          name="password"
          required
          minLength={PASSWORD_MIN_LENGTH}
          autoComplete="new-password"
          className={styles.input}
        />
        <span className={styles.hint}>อย่างน้อย {PASSWORD_MIN_LENGTH} ตัวอักษร</span>
      </label>

      <label className={styles.field}>
        ยืนยันรหัสผ่าน
        <input
          type="password"
          name="confirm"
          required
          minLength={PASSWORD_MIN_LENGTH}
          autoComplete="new-password"
          className={styles.input}
        />
      </label>

      <button type="submit" className={styles.button} disabled={pending}>
        {pending ? "กำลังสมัคร..." : "ยืนยันและสมัคร"}
      </button>
    </form>
  );
}
