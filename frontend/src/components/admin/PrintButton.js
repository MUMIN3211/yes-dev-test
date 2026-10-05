"use client";

import styles from "./admin.module.css";

export default function PrintButton({ label = "พิมพ์" }) {
  return (
    <button type="button" className={styles.button} onClick={() => window.print()}>
      {label}
    </button>
  );
}
