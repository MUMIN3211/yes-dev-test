import Link from "next/link";
import ProductImage from "./ProductImage";
import { API_URL } from "@/lib/api";
import { formatPrice } from "@/lib/constants";
import styles from "./ProductCard.module.css";

export default function ProductCard({ product }) {
  return (
    <Link href={`/products/${product.sku}`} className={styles.card}>
      <div className={styles.imageWrap}>
        <ProductImage src={product.image_url} alt={product.name} className={styles.image} />
        {/* Same QR as the printed label: scan it with a phone to open this product */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={`${API_URL}/api/public/products/${encodeURIComponent(product.sku)}/qr`}
          alt={`QR code ของ ${product.name}`}
          title="สแกนเพื่อเปิดหน้าสินค้านี้"
          className={styles.qr}
          loading="lazy"
          width={72}
          height={72}
        />
      </div>
      <div className={styles.body}>
        <span className={styles.category}>{product.category}</span>
        <h2 className={styles.name}>{product.name}</h2>
        <div className={styles.meta}>
          <span className={styles.price}>{formatPrice(product.price)}</span>
          {product.size && <span className={styles.size}>{product.size}</span>}
        </div>
      </div>
    </Link>
  );
}
