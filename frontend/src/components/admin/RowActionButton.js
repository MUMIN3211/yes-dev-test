"use client";

import { useActionState } from "react";
import styles from "./admin.module.css";

// A one-button form for row actions (deactivate, revoke, ...) that shows the
// backend's error message next to the button if the action fails.
export default function RowActionButton({ action, fields, label, pendingLabel, variant = "ghost", confirm }) {
  const [state, formAction, pending] = useActionState(action, {});

  const onSubmit = (e) => {
    if (confirm && !window.confirm(confirm)) e.preventDefault();
  };

  return (
    <form action={formAction} onSubmit={onSubmit}>
      {Object.entries(fields).map(([name, value]) => (
        <input key={name} type="hidden" name={name} value={String(value)} />
      ))}
      <button
        type="submit"
        disabled={pending}
        className={`${variant === "danger" ? styles.buttonDanger : styles.buttonGhost} ${styles.small}`}
      >
        {pending ? pendingLabel ?? label : label}
      </button>
      {state.error && (
        <span className={styles.hint} role="alert" style={{ color: "var(--danger)", display: "block" }}>
          {state.error}
        </span>
      )}
    </form>
  );
}
