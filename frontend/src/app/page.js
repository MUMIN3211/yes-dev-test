import ProductCard from "@/components/ProductCard";
import ProductFilters from "@/components/ProductFilters";
import { getPublicProducts } from "@/lib/api";
import { CATEGORIES } from "@/lib/constants";
import styles from "./page.module.css";

export default async function HomePage({ searchParams }) {
  const params = await searchParams;
  const category = CATEGORIES.includes(params.category) ? params.category : undefined;
  const q = typeof params.q === "string" ? params.q.trim() : "";

  let data = null;
  let error = null;
  try {
    data = await getPublicProducts({ category, q });
  } catch (err) {
    error = err.message;
  }

  return (
    <main className="container">
      <section className={styles.hero}>
        <h1>ผลิตภัณฑ์ทั้งหมด</h1>
        <p>สแกน QR บนบรรจุภัณฑ์ หรือเลือกดูสินค้าเพื่อดูรายละเอียดและวิธีใช้</p>
      </section>

      <ProductFilters category={category} q={q} />

      {error ? (
        <p className={styles.message} role="alert">
          โหลดรายการสินค้าไม่สำเร็จ: {error}
        </p>
      ) : data.items.length === 0 ? (
        <p className={styles.message}>ไม่พบสินค้าที่ตรงกับเงื่อนไข</p>
      ) : (
        <>
          <p className={styles.count}>{data.total} รายการ</p>
          <ul className={styles.grid}>
            {data.items.map((product) => (
              <li key={product.sku}>
                <ProductCard product={product} />
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  );
}
