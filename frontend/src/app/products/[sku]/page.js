import { cache } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import ProductImage from "@/components/ProductImage";
import { getPublicProduct } from "@/lib/api";
import { formatPrice } from "@/lib/constants";
import styles from "./page.module.css";

// Public product page — this is the URL encoded in each product's QR code
// (/products/{sku}). The SKU never changes, so printed QR codes keep working
// after the product is edited or re-imported.

// cache() makes generateMetadata and the page share ONE backend request per
// visit, so a future scan log is not counted twice.
const loadProduct = cache(async (sku) => {
  try {
    return await getPublicProduct(sku);
  } catch (err) {
    if (err.status === 404) notFound();
    throw err;
  }
});

export async function generateMetadata({ params }) {
  const { sku } = await params;
  const product = await loadProduct(sku);
  return { title: `${product.name} | Luma Skin Care`, description: product.description };
}

export default async function ProductPage({ params }) {
  const { sku } = await params;
  const product = await loadProduct(sku);

  return (
    <main className="container">
      <Link href="/" className={styles.back}>
        ← สินค้าทั้งหมด
      </Link>

      <article className={styles.layout}>
        <div className={styles.imageWrap}>
          <ProductImage
            src={product.image_url}
            alt={product.name}
            className={styles.image}
            priority
          />
        </div>

        <div className={styles.info}>
          <span className={styles.category}>{product.category}</span>
          <h1 className={styles.name}>{product.name}</h1>
          <p className={styles.sku}>รหัสสินค้า {product.sku}</p>

          <div className={styles.priceRow}>
            <span className={styles.price}>{formatPrice(product.price)}</span>
            {product.size && <span className={styles.size}>{product.size}</span>}
          </div>

          {product.description && (
            <section className={styles.section}>
              <h2>รายละเอียดสินค้า</h2>
              <p>{product.description}</p>
            </section>
          )}

          {product.how_to_use && (
            <section className={styles.section}>
              <h2>วิธีใช้</h2>
              <p>{product.how_to_use}</p>
            </section>
          )}
        </div>
      </article>
    </main>
  );
}
