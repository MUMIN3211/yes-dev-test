import Link from "next/link";
import { CATEGORIES } from "@/lib/constants";
import styles from "./ProductFilters.module.css";

// Search + category filter driven by URL query params, so it works without
// client-side JS and filtered views can be shared as links.
export default function ProductFilters({ category, q }) {
  const hrefFor = (cat) => {
    const params = new URLSearchParams();
    if (cat) params.set("category", cat);
    if (q) params.set("q", q);
    const qs = params.toString();
    return qs ? `/?${qs}` : "/";
  };

  return (
    <div className={styles.filters}>
      <form action="/" method="get" className={styles.search} role="search">
        {category && <input type="hidden" name="category" value={category} />}
        <input
          type="search"
          name="q"
          defaultValue={q}
          placeholder="ค้นหาชื่อสินค้าหรือรหัส SKU"
          aria-label="ค้นหาสินค้า"
          className={styles.input}
        />
        <button type="submit" className={styles.button}>
          ค้นหา
        </button>
      </form>

      <nav className={styles.chips} aria-label="หมวดหมู่สินค้า">
        <Link href={hrefFor(null)} className={!category ? styles.chipActive : styles.chip}>
          ทั้งหมด
        </Link>
        {CATEGORIES.map((cat) => (
          <Link
            key={cat}
            href={hrefFor(cat)}
            className={category === cat ? styles.chipActive : styles.chip}
          >
            {cat}
          </Link>
        ))}
      </nav>
    </div>
  );
}
