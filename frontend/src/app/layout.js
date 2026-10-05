import { Noto_Sans_Thai } from "next/font/google";
import InviteHashRedirect from "@/components/InviteHashRedirect";
import SiteHeader from "@/components/SiteHeader";
import "./globals.css";

const notoSansThai = Noto_Sans_Thai({
  variable: "--font-sans",
  subsets: ["thai", "latin"],
  weight: ["400", "600", "700"],
});

export const metadata = {
  title: "Luma Skin",
  description: "ผลิตภัณฑ์ดูแลผิวจาก Luma Skin",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }) {
  return (
    <html lang="th">
      <body className={notoSansThai.variable}>
        <InviteHashRedirect />
        <SiteHeader />
        {children}
      </body>
    </html>
  );
}
