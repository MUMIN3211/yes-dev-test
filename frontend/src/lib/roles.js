export const ROLE_LABELS = {
  super_admin: "Super Admin",
  admin: "Admin",
};

export const PASSWORD_MIN_LENGTH = 8;

// Only allow redirects back into the back office (prevents open redirects via ?next=)
export function safeNextPath(next) {
  return typeof next === "string" && /^\/admin(\/|$)/.test(next) ? next : "/admin";
}
