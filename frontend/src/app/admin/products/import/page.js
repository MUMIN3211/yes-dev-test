import Link from "next/link";
import ImportForm from "@/components/admin/ImportForm";
import { requireAdmin } from "@/lib/session";
import styles from "@/components/admin/admin.module.css";

export const metadata = { title: "นำเข้าสินค้า | Luma Skin Care" };

export default async function ImportProductsPage() {
  await requireAdmin();

  return (
    <main className="container">
      <p className={styles.subtle}>
        <Link href="/admin/products">← สินค้า</Link>
      </p>
      <h1 className={styles.pageTitle}>นำเข้าสินค้าจาก Excel</h1>
      <p className={styles.subtle}>
        เลือกไฟล์แล้วกด &quot;ตรวจสอบไฟล์&quot; ระบบจะแสดงตัวอย่างก่อนบันทึก แถวที่ข้อมูลไม่ถูกต้องจะถูกข้ามและแจ้งเหตุผล
        ส่วนแถวที่ถูกต้องจะถูกเพิ่มหรืออัปเดตตาม SKU (QR ที่พิมพ์ไปแล้วยังใช้ได้ และรูปสินค้าเดิมไม่ถูกลบ)
      </p>

      <section className={styles.section}>
        <h2>รูปแบบไฟล์</h2>
        <ul className={styles.subtle}>
          <li>ไฟล์ .xlsx ไม่เกิน 5 MB ใช้ชีตแรก แถวแรกเป็นหัวตาราง</li>
          <li>
            คอลัมน์: <code>sku</code>, <code>name</code>, <code>category</code>, <code>price</code> (จำเป็น) และ{" "}
            <code>size</code>, <code>description</code>, <code>how_to_use</code>, <code>status</code>
          </li>
          <li>SKU รูปแบบ LS-0000 · ราคามากกว่า 0 · หมวดหมู่ Cleanser, Toner, Serum, Moisturizer, Sunscreen หรือ Mask</li>
          <li>status เป็น active หรือ inactive (เว้นว่าง = active) · SKU ซ้ำในไฟล์เดียวกันจะใช้แถวแรก</li>
        </ul>
      </section>

      <section className={styles.section}>
        <ImportForm />
      </section>
    </main>
  );
}
