import Link from "next/link";
import ProductImage from "./ProductImage";
import { formatPrice } from "@/lib/constants";
import styles from "./ProductCard.module.css";

export default function ProductCard({ product }) {
  return (
    <Link href={`/products/${product.sku}`} className={styles.card}>
      <div className={styles.imageWrap}>
        <ProductImage src={product.image_url} alt={product.name} className={styles.image} />
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
