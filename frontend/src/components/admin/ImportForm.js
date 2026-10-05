"use client";

import Link from "next/link";
import { startTransition, useActionState, useState } from "react";
import { importProductsAction } from "@/app/admin/products/actions";
import ImportSummary from "./ImportSummary";
import styles from "./admin.module.css";

const keyOf = (file) => (file ? `${file.name}:${file.size}:${file.lastModified}` : "");

// The file is kept in state and sent with a manually built FormData, because a
// <form action> would reset the file input after the preview step.
export default function ImportForm() {
  const [state, dispatch, pending] = useActionState(importProductsAction, {});
  const [file, setFile] = useState(null);
  // Changing the key remounts the <input type="file">, which clears it
  const [inputKey, setInputKey] = useState(0);
  const [clearedFor, setClearedFor] = useState(null);

  const result = state.result;
  const committed = result && !result.dry_run;
  // A preview or error only applies to the file it was made from
  const isCurrent = state.fileKey === keyOf(file);
  const preview = result?.dry_run && isCurrent ? result : null;
  const toWrite = preview ? preview.created + preview.updated : 0;

  const submit = (dryRun) => {
    const formData = new FormData();
    if (file) formData.set("file", file);
    formData.set("dry_run", String(dryRun));
    formData.set("file_key", keyOf(file));
    startTransition(() => dispatch(formData));
  };

  const onFileChange = (e) => setFile(e.target.files?.[0] ?? null);

  // After a successful import, clear the picker once so the same file is not imported twice by accident
  if (committed && clearedFor !== state) {
    setClearedFor(state);
    setFile(null);
    setInputKey((k) => k + 1);
  }

  return (
    <div className={styles.form} style={{ marginTop: 0 }}>
      <div className={styles.inlineForm}>
        <input
          key={inputKey}
          type="file"
          accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          aria-label="ไฟล์ Excel"
          className={styles.input}
          onChange={onFileChange}
        />
        <button type="button" className={styles.button} disabled={!file || pending} onClick={() => submit(true)}>
          {pending && !preview ? "กำลังตรวจสอบ..." : "ตรวจสอบไฟล์"}
        </button>
      </div>

      {state.error && isCurrent && (
        <p className={styles.error} role="alert">
          {state.error}
        </p>
      )}

      {preview && (
        <>
          <ImportSummary result={preview} />
          <div className={styles.inlineForm}>
            <button
              type="button"
              className={styles.button}
              disabled={pending || toWrite === 0}
              onClick={() => submit(false)}
            >
              {pending ? "กำลังนำเข้า..." : `ยืนยันนำเข้า ${toWrite} รายการ`}
            </button>
            {toWrite === 0 && <span className={styles.hint}>ไม่มีข้อมูลที่ต้องบันทึก ทุกแถวตรงกับข้อมูลเดิมหรือไม่ถูกต้อง</span>}
          </div>
        </>
      )}

      {committed && !file && (
        <>
          <p className={styles.success} role="status">
            นำเข้า {result.file_name} สำเร็จ: เพิ่มใหม่ {result.created} รายการ อัปเดต {result.updated} รายการ
            {result.failed > 0 && ` · ข้าม ${result.failed} แถวที่ข้อมูลไม่ถูกต้อง`} ·{" "}
            <Link href="/admin/products">ดูสินค้าและ QR →</Link>
          </p>
          <ImportSummary result={result} />
        </>
      )}
    </div>
  );
}
