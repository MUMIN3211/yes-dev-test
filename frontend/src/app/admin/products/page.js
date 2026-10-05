import Link from "next/link";
import { formatPrice } from "@/lib/constants";
import { adminRequest, requireAdmin } from "@/lib/session";
import styles from "@/components/admin/admin.module.css";
import productStyles from "@/components/admin/products.module.css";

export const metadata = { title: "สินค้า | Luma Skin Care" };

export default async function AdminProductsPage() {
  await requireAdmin();
  const { items, total } = await adminRequest("/api/admin/products");
  const activeCount = items.filter((p) => p.status === "active").length;

  return (
    <main className="container">
      <div className={productStyles.header}>
        <div>
          <h1 className={styles.pageTitle}>สินค้า</h1>
          <p className={styles.subtle}>
            ทั้งหมด {total} รายการ · แสดงบนหน้าสาธารณะ {activeCount} รายการ · สินค้าทุกชิ้นมี QR ของตัวเองทันทีหลังนำเข้า
          </p>
        </div>
        <div className={productStyles.headerActions}>
          <Link href="/admin/products/qr-sheet" className={styles.buttonGhost}>
            พิมพ์ QR ทั้งหมด
          </Link>
          <Link href="/admin/products/import" className={styles.button}>
            นำเข้าจาก Excel
          </Link>
        </div>
      </div>

      <section className={styles.section}>
        {items.length === 0 ? (
          <p className={styles.empty}>
            ยังไม่มีสินค้า <Link href="/admin/products/import">นำเข้าจากไฟล์ Excel</Link>
          </p>
        ) : (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>QR</th>
                  <th>SKU</th>
                  <th>ชื่อสินค้า</th>
                  <th>หมวดหมู่</th>
                  <th>ราคา</th>
                  <th>สถานะ</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {items.map((p) => {
                  const qrPath = `/admin/products/${encodeURIComponent(p.sku)}/qr`;
                  return (
                    <tr key={p.sku}>
                      <td>
                        <a href={qrPath} target="_blank" rel="noreferrer" title="เปิด QR ขนาดเต็ม">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={`${qrPath}?scale=3`}
                            alt={`QR ของ ${p.sku}`}
                            className={productStyles.qrThumb}
                            loading="lazy"
                          />
                        </a>
                      </td>
                      <td className={productStyles.mono}>{p.sku}</td>
                      <td>
                        {p.name}
                        {p.size && <span className={styles.hint}> · {p.size}</span>}
                      </td>
                      <td>{p.category}</td>
                      <td className={productStyles.nowrap}>{formatPrice(p.price)}</td>
                      <td>
                        {p.status === "active" ? (
                          <span className={styles.badge}>active</span>
                        ) : (
                          <span className={styles.badgeMuted} title="ไม่แสดงบนหน้าสาธารณะ สแกน QR จะเห็นหน้าไม่พบสินค้า">
                            inactive
                          </span>
                        )}
                      </td>
                      <td>
                        <div className={styles.rowActions}>
                          <a href={`${qrPath}?scale=20&download=1`} className={`${styles.buttonGhost} ${styles.small}`}>
                            ดาวน์โหลด QR
                          </a>
                          {p.status === "active" && (
                            // Not p.qr_url: its ?src=qr would count this click as a scan
                            <a
                              href={`/products/${encodeURIComponent(p.sku)}`}
                              target="_blank"
                              rel="noreferrer"
                              className={`${styles.buttonGhost} ${styles.small}`}
                              title={`QR นี้เปิด ${p.qr_url}`}
                            >
                              เปิดหน้าสินค้า
                            </a>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
