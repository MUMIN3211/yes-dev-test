"use client";

import { useActionState } from "react";
import { loginAction } from "@/app/login/actions";
import styles from "./admin.module.css";

export default function LoginForm({ next }) {
  const [state, formAction, pending] = useActionState(loginAction, {});

  return (
    <form action={formAction} className={styles.form}>
      <input type="hidden" name="next" value={next ?? ""} />

      {state.error && (
        <p className={styles.error} role="alert">
          {state.error}
        </p>
      )}

      <label className={styles.field}>
        อีเมล
        <input
          type="email"
          name="email"
          required
          autoComplete="email"
          defaultValue={state.email}
          className={styles.input}
        />
      </label>

      <label className={styles.field}>
        รหัสผ่าน
        <input
          type="password"
          name="password"
          required
          autoComplete="current-password"
          className={styles.input}
        />
      </label>

      <button type="submit" className={styles.button} disabled={pending}>
        {pending ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบ"}
      </button>
    </form>
  );
}
