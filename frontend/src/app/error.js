"use client";

export default function Error({ reset }) {
  return (
    <main className="container" style={{ textAlign: "center", paddingTop: 64 }}>
      <h1>เกิดข้อผิดพลาด</h1>
      <p style={{ color: "var(--muted)" }}>ไม่สามารถโหลดข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง</p>
      <button
        onClick={reset}
        style={{
          padding: "10px 18px",
          border: "none",
          borderRadius: 999,
          background: "var(--accent)",
          color: "var(--on-accent)",
          font: "inherit",
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        ลองใหม่
      </button>
    </main>
  );
}
