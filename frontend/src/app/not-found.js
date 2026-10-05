import Link from "next/link";

export default function NotFound() {
  return (
    <main className="container" style={{ textAlign: "center", paddingTop: 64 }}>
      <h1>ไม่พบสินค้านี้</h1>
      <p style={{ color: "var(--muted)" }}>
        สินค้าอาจถูกปิดการแสดงผล หรือ QR code ไม่ถูกต้อง
      </p>
      <Link href="/" style={{ color: "var(--accent)", fontWeight: 600 }}>
        ดูสินค้าทั้งหมด
      </Link>
    </main>
  );
}
