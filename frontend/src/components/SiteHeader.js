import Link from "next/link";
import styles from "./SiteHeader.module.css";

export default function SiteHeader() {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link href="/" className={styles.brand}>
          Luma <span>Skin Care</span>
        </Link>
      </div>
    </header>
  );
}
