"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getInvitationAction } from "@/app/invite/actions";
import AcceptInviteForm from "./AcceptInviteForm";
import styles from "./admin.module.css";

// Errors Supabase puts in the fragment when the link cannot be used
// (e.g. #error=access_denied&error_code=otp_expired)
const SUPABASE_ERRORS = {
  otp_expired: "ลิงก์คำเชิญหมดอายุแล้ว",
  access_denied: "ลิงก์คำเชิญไม่ถูกต้องหรือถูกใช้งานไปแล้ว",
};

export default function InviteSignup() {
  const [state, setState] = useState({ status: "loading" });

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    // Remove the token from the address bar / browser history right away
    if (window.location.hash) {
      window.history.replaceState(null, "", window.location.pathname);
    }

    const accessToken = params.get("access_token");
    if (!accessToken) {
      const code = params.get("error_code") || params.get("error");
      setState({ status: "error", message: SUPABASE_ERRORS[code] ?? "ไม่พบข้อมูลคำเชิญในลิงก์" });
      return;
    }

    getInvitationAction(accessToken).then((res) => {
      if (res.error) setState({ status: "error", message: res.error });
      else setState({ status: "ready", accessToken, invitation: res.invitation });
    });
  }, []);

  if (state.status === "loading") {
    return <p className={styles.subtle}>กำลังตรวจสอบคำเชิญ...</p>;
  }

  if (state.status === "error") {
    return (
      <>
        <h1>ลิงก์ใช้งานไม่ได้</h1>
        <p className={styles.error} role="alert" style={{ margin: "16px 0" }}>
          {state.message}
        </p>
        <p className={styles.subtle} style={{ marginBottom: 16 }}>
          กรุณาติดต่อ Super Admin เพื่อขอคำเชิญใหม่
        </p>
        <Link href="/login" style={{ color: "var(--accent)", fontWeight: 600 }}>
          ไปหน้าเข้าสู่ระบบ
        </Link>
      </>
    );
  }

  const { invitation, accessToken } = state;
  return (
    <>
      <h1>สมัครเป็นผู้ดูแลระบบ</h1>
      <p className={styles.subtle}>
        {invitation.invited_by_email ? (
          <>
            <strong>{invitation.invited_by_email}</strong> (Super Admin) เชิญคุณเข้าร่วมเป็น Admin ของ Luma Skin Care
          </>
        ) : (
          "คุณได้รับคำเชิญเป็น Admin ของ Luma Skin Care"
        )}
      </p>
      <AcceptInviteForm accessToken={accessToken} email={invitation.email} />
    </>
  );
}
