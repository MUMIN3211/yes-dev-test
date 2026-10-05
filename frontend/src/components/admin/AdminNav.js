"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { logoutAction } from "@/app/admin/actions";
import { ROLE_LABELS } from "@/lib/roles";
import styles from "./AdminNav.module.css";

// "/admin" only matches itself; other links also match their sub-pages
function isActive(pathname, href) {
  return href === "/admin" ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);
}

export default function AdminNav({ admin }) {
  const pathname = usePathname();
  const links = [
    { href: "/admin", label: "ภาพรวม" },
    { href: "/admin/products", label: "สินค้า" },
    // Only Super Admin can manage users
    ...(admin.role === "super_admin" ? [{ href: "/admin/users", label: "จัดการผู้ใช้" }] : []),
  ];

  return (
    <div className={styles.bar}>
      <div className={styles.inner}>
        <nav className={styles.links} aria-label="เมนูผู้ดูแล">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={isActive(pathname, link.href) ? styles.linkActive : styles.link}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className={styles.user}>
          <span className={styles.email} title={admin.email}>
            {admin.email}
          </span>
          <span className={styles.role}>{ROLE_LABELS[admin.role]}</span>
          <form action={logoutAction}>
            <button type="submit" className={styles.logout}>
              ออกจากระบบ
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
