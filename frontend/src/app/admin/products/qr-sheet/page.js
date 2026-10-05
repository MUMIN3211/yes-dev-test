import Link from "next/link";
import PrintButton from "@/components/admin/PrintButton";
import { adminRequest, requireAdmin } from "@/lib/session";
import styles from "@/components/admin/admin.module.css";
import productStyles from "@/components/admin/products.module.css";

export const metadata = { title: "พิมพ์ QR | Luma Skin Care" };

// One label per product, laid out for printing on A4 (4 per row).
// ?all=1 includes inactive products too.
export default async function QrSheetPage({ searchParams }) {
  await requireAdmin();
  const includeInactive = (await searchParams).all === "1";
  const { items } = await adminRequest("/api/admin/products");
  const products = includeInactive ? items : items.filter((p) => p.status === "active");

  return (
    <main className="container">
      <div className={productStyles.noPrint}>
        <p className={styles.subtle}>
          <Link href="/admin/products">← สินค้า</Link>
        </p>
        <h1 className={styles.pageTitle}>พิมพ์ QR สินค้า</h1>
        <p className={styles.subtle}>
          QR แต่ละอันเปิดหน้าสินค้าของ SKU นั้น ข้อมูลที่แก้ไขหรือนำเข้าภายหลังจะแสดงผ่าน QR เดิมได้ทันที ไม่ต้องพิมพ์ใหม่
        </p>
        <div className={productStyles.sheetToolbar}>
          <PrintButton label={`พิมพ์ ${products.length} รายการ`} />
          <Link href={includeInactive ? "/admin/products/qr-sheet" : "/admin/products/qr-sheet?all=1"} className={styles.buttonGhost}>
            {includeInactive ? "เฉพาะสินค้า active" : "รวมสินค้า inactive"}
          </Link>
        </div>
      </div>

      {products.length === 0 ? (
        <p className={styles.empty}>ยังไม่มีสินค้า</p>
      ) : (
        <div className={productStyles.sheet}>
          {products.map((p) => (
            <div key={p.sku} className={productStyles.label}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`/admin/products/${encodeURIComponent(p.sku)}/qr?format=svg&scale=4`} alt={`QR ของ ${p.sku}`} />
              <span className={productStyles.labelSku}>{p.sku}</span>
              <span className={productStyles.labelName}>{p.name}</span>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
